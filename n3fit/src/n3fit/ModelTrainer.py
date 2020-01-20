"""
    The ModelTrainer class is the true driver around the n3fit code

    This class is initialized with all information about the NN, inputs and outputs.
    The construction of the NN and the fitting is performed at the same time when the
    hyperparametizable method of the function is called.

    This allows to use hyperscanning libraries, that need to change the parameters of the network
    between iterations while at the same time keeping the amount of redundant calls to a minimum
"""
import logging
import n3fit.model_gen as model_gen
import n3fit.msr as msr_constraints
from n3fit.backends import MetaModel, clear_backend_state
from n3fit.stopping import Stopping

log = logging.getLogger(__name__)

# If an experiment matches this name, it will not be included int he training
TESTNAME = "TEST"
# Weights for the hyperopt cost function
TEST_MULTIPLIER = 0.5
VALIDATION_MULTIPLIER = 0.5


class ModelTrainer:
    """
        ModelTrainer Class:

        Wrapper around the fitting code and the generation of the Neural Network

        When the "hyperparametizable"* function is called with a dictionary of parameters,
        it generates a NN and subsequentially performs a fit.

        The motivation behind this class is minimising the amount
        of redundant calls of each hyperopt run, in particular this allows to completely reset
        the NN at the beginning of each iteration reusing some of the previous work.

        *called in this way because it accept a dictionary of hyper-parameters
        which defines the Neural Network
    """

    def __init__(
        self,
        exp_info,
        pos_info,
        flavinfo,
        nnseed,
        pass_status="ok",
        failed_status="fail",
        debug=False,
        save_weights_each=False,
    ):
        """
        # Arguments:
            - `exp_info`: list of dictionaries containing experiments
            - `pos_info`: list of dictionaries containing positivity sets
            - `flavinfo`: the object returned by fitting['basis']
            - `nnseed`: the seed used to initialise the Neural Network, will be passed to model_gen
            - `pass_status`: flag to signal a good run
            - `failed_status`: flag to signal a bad run
            - `pass_status`: flag to signal a good run
            - `failed_status`: flag to signal a bad run
            - `debug`: flag to activate some debug options
            - `save_weights_each`: if set, save the state of the fit
                                    every `save_weights_each` epochs
        """

        # Save all input information
        self.exp_info = exp_info
        self.pos_info = pos_info
        self.all_info = exp_info + pos_info
        self.flavinfo = flavinfo
        self.NNseed = nnseed
        self.pass_status = pass_status
        self.failed_status = failed_status
        self.debug = debug
        self.save_weights_each = save_weights_each

        # Initialise internal variables which define behaviour
        self.print_summary = True
        self.mode_hyperopt = False
        self.model_file = None
        self.impose_sumrule = True

        # Initialize the pdf layer
        self.layer_pdf = None

        # Initialize the dictionaries which contain all fitting information
        self.input_list = []
        self.training = {
            "output": [],
            "expdata": [],
            "losses": [],
            "ndata": 0,
            "model": None,
            "posdatasets": [],
        }
        self.validation = {
            "output": [],
            "expdata": [],
            "losses": [],
            "ndata": 0,
            "model": None,
        }
        self.experimental = {
            "output": [],
            "expdata": [],
            "losses": [],
            "ndata": 0,
            "model": None,
        }
        self.list_of_models_dicts = [self.training, self.experimental]

        self.test_dict = None
        self._fill_the_dictionaries()

        if self.validation["ndata"] == 0:
            # If there is no validation, the validation chi2 = training chi2
            self.no_validation = True
            self.validation["expdata"] = self.training["expdata"]
        else:
            # Consider the validation only if there is validation (of course)
            self.no_validation = False
            self.list_of_models_dicts.append(self.validation)

    @property
    def model_file(self):
        """ If a model_file is set the training model will try to get the weights form here """
        return self._model_file

    @model_file.setter
    def model_file(self, model_file):
        self._model_file = model_file

    def set_hyperopt(self, hyperopt_on, keys=None):
        """ Set hyperopt options on and off (mostly suppresses some printing) """
        if keys is None:
            keys = []
        self.hyperkeys = keys
        if hyperopt_on:
            self.print_summary = False
            self.mode_hyperopt = True
        else:
            self.print_summary = True
            self.mode_hyperopt = False

    ###########################################################################
    # # Internal functions                                                    #
    # Never to be called from the dark and cold outside world                 #
    ###########################################################################
    def _fill_the_dictionaries(self):
        """
        This function fills the following dictionaries
            -`training`: data for the fit
            -`validation`: data which for the stopping
            -`experimental`: 'true' data, only used for reporting purposes
        with fixed information.

        Fixed information: information which will not change between different runs of the code.
        This information does not depend on the parameters of the fit at any stage
        and so it will remain unchanged between different runs of the hyperoptimizer.

        The aforementioned information corresponds to:
            - `expdata`: experimental data
            - `name`: names of the experiment
            - `ndata`: number of experimental points
        """
        for exp_dict in self.exp_info:
            if exp_dict["name"] == TESTNAME:
                self.test_dict = {
                    "output": [],
                    "expdata": exp_dict["expdata_true"],
                    "losses": [],
                    "ndata": exp_dict["ndata"] + exp_dict["ndata_vl"],
                    "model": None,
                }
                self.list_of_models_dicts.append(self.test_dict)
                continue
            self.training["expdata"].append(exp_dict["expdata"])
            self.validation["expdata"].append(exp_dict["expdata_vl"])
            self.experimental["expdata"].append(exp_dict["expdata_true"])

            nd_tr = exp_dict["ndata"]
            nd_vl = exp_dict["ndata_vl"]

            self.training["ndata"] += nd_tr
            self.validation["ndata"] += nd_vl
            self.experimental["ndata"] += nd_tr + nd_vl

        for pos_dict in self.pos_info:
            self.training["expdata"].append(pos_dict["expdata"])
            self.training["posdatasets"].append(pos_dict["name"])

    def _model_generation(self):
        """
        Fills the three dictionaries (`training`, `validation`, `experimental`)
        with the `model` entry

        *Note*: before entering this function the dictionaries contain a list of inputs
            and a list of outputs, but they are not connected.
            This function connects inputs with outputs by injecting the PDF

        Compiles the validation and experimental models with fakes optimizers and learning rate
        as they are never trained, but this is needed by some backends
        in order to run evaluate on them
        """
        log.info("Generating the Model")

        input_list = self.input_list

        # Loop over all the dictionary models and create the trainig,
        #                 validation, true (data w/o replica) models:
        # note: if test_dict exists, it will also create a model for it

        for model_dict in self.list_of_models_dicts:
            model_dict["model"] = MetaModel(
                input_list, self._pdf_injection(model_dict["output"])
            )

        if self.model_file:
            # If a model file is given, load the weights from there
            # note: even though the load corresponds to the training model only,
            #       the layer_pdf is shared  and so it should affect all models
            self.training["model"].load_weights(self.model_file)

        if self.print_summary:
            self.training["model"].summary()

    def _reset_observables(self):
        """
        Resets the 'output' and 'losses' entries of all 3 dictionaries:
                            (`training`, `validation`, `experimental`)
        as well as the input_list
        this is necessary as these can either depend on the parametrization of the NN
        or be obliterated when/if the backend state is reset
        """
        self.input_list = []
        for key in ["output", "losses"]:
            self.training[key] = []
            self.validation[key] = []
            self.experimental[key] = []
            if self.test_dict:
                self.test_dict[key] = []

    def _pdf_injection(self, olist):
        """
        Takes as input a list of output layers and returns a corresponding list
        where all output layers call the pdf layer at self.pdf_layer
        """
        return [o(self.layer_pdf) for o in olist]

    ############################################################################
    # # Parametizable functions                                                #
    #                                                                          #
    # The functions defined in this block accept a 'params' dictionary which   #
    # defines the fit and the behaviours of the Neural Networks                #
    #                                                                          #
    # These are all called by the function hyperparamizable below              #
    # i.e., the most important function is hyperparametizable, which is a      #
    # wrapper around all of these                                              #
    ############################################################################
    def _generate_observables(self, pos_multiplier, pos_initial):
        """
        This functions fills the 3 dictionaries (training, validation, experimental)
        with the output layers and the loss functions
        It also fill the list of input tensors (input_list)

        Parameters accepted:
            - `pos_multiplier`: the multiplier to be applied to the positivity each 100 epochs
            - `pos_initial`: the initial value for the positivity
        """

        # First reset the dictionaries
        self._reset_observables()
        log.info("Generating layers")

        # Now we need to loop over all dictionaries (First exp_info, then pos_info)
        for exp_dict in self.exp_info:
            if not self.mode_hyperopt:
                log.info("Generating layers for experiment %s", exp_dict["name"])

            exp_layer = model_gen.observable_generator(exp_dict)

            # Save the input(s) corresponding to this experiment
            self.input_list += exp_layer["inputs"]

            if exp_dict["name"] == TESTNAME and self.test_dict:
                # If this is the test set, fill the dictionary and stop here
                self.test_dict["output"].append(exp_layer["output"])
                self.test_dict["losses"].append(exp_layer["loss"])
                continue

            # Now save the observable layer, the losses and the experimental data
            self.training["output"].append(exp_layer["output_tr"])
            self.validation["output"].append(exp_layer["output_vl"])
            self.experimental["output"].append(exp_layer["output"])

            self.training["losses"].append(exp_layer["loss_tr"])
            self.validation["losses"].append(exp_layer["loss_vl"])
            self.experimental["losses"].append(exp_layer["loss"])

        # Finally generate the positivity penalty
        for pos_dict in self.pos_info:
            if not self.mode_hyperopt:
                log.info("Generating positivity penalty for %s", pos_dict["name"])
            pos_layer = model_gen.observable_generator(
                pos_dict,
                positivity_initial=pos_initial,
                positivity_multiplier=pos_multiplier,
            )
            # The input list is still common
            self.input_list += pos_layer["inputs"]

            # The positivity all falls to the training
            self.training["output"].append(pos_layer["output_tr"])
            self.training["losses"].append(pos_layer["loss_tr"])
        # Save the positivity multiplier into the training dictionary
        # as it will be used during training
        self.training["pos_multiplier"] = pos_multiplier

    def _generate_pdf(
        self, nodes_per_layer, activation_per_layer, initializer, layer_type, dropout
    ):
        """
        Defines the internal variable layer_pdf
        this layer takes any input (x) and returns the pdf value for that x

        if the sumrule is being imposed, it also updates input_list with the
        integrator_input tensor used to calculate the sumrule

        # Returns: (layers, integrator_input)
            `layers`: a list of layers
            `integrator_input`: input used to compute the  sumrule
        both are being used at the moment for reporting purposes at the end of the fit

        Parameters accepted:
            - `nodes_per_layer`
            - `activation_per_layer`
            - `initializer`
            - `layer_type`
            - `dropout`
        see model_gen.pdfNN_layer_generator for more information
        """
        log.info("Generating PDF layer")

        # Set the parameters of the NN

        # Generate the NN layers
        layer_pdf, layers = model_gen.pdfNN_layer_generator(
            nodes=nodes_per_layer,
            activations=activation_per_layer,
            layer_type=layer_type,
            flav_info=self.flavinfo,
            seed=self.NNseed,
            initializer_name=initializer,
            dropout=dropout,
        )

        integrator_input = None
        if self.impose_sumrule:
            # Impose the sumrule
            # Inyect here momentum sum rule, effecively modifying layer_pdf
            layer_pdf, integrator_input = msr_constraints.msr_impose(
                layers["fitbasis"], layer_pdf
            )
            self.input_list.append(integrator_input)

        self.layer_pdf = layer_pdf

        return layers, integrator_input

    def _model_compilation(self, learning_rate, optimizer):
        """
        Compiles the model with the data given in params

        Parameters accepted:
            - `learning_rate`
            - `optimizer`
        Optimizers accepted are backend-dependent
        """

        # Compile all different models
        for model_dict in self.list_of_models_dicts:
            model = model_dict["model"]
            losses = model_dict["losses"]
            data = model_dict["expdata"]
            model.compile(
                optimizer_name=optimizer,
                learning_rate=learning_rate,
                loss=losses,
                target_output=data,
            )

    def _train_and_fit(self, stopping_object, epochs):
        """
        Trains the NN for the number of epochs given using
        stopping_object as the stopping criteria

        Every 100 epochs the positivitiy will be updated with
        self.training['pos_multiplier']
        """
        training_model = self.training["model"]
        pos_multiplier = self.training["pos_multiplier"]
        # Train the model for the number of epochs given
        for epoch in range(epochs):
            out = training_model.fit(verbose=False)
            print_stats = False

            if (epoch + 1) % 100 == 0:
                print_stats = True
                training_model.multiply_weights('pos', self.training["posdatasets"], pos_multiplier)

            passes = stopping_object.monitor_chi2(out, epoch, print_stats=print_stats)

            if stopping_object.stop_here():
                break

        # Report a "good" training only if there was no NaNs
        # and if there was at least a point which passed positivity
        if passes and stopping_object.positivity:
            return self.pass_status
        else:
            return self.failed_status

    def _hyperopt_override(self, params):
        """ Unrolls complicated hyperopt structures into very simple dictionaries"""
        # I love the smell of napalm in the morning
        for hyperkey in self.hyperkeys:
            item = params[hyperkey]
            if isinstance(item, dict):
                for key, value in item.items():
                    params[key] = value

    def evaluate(self, stopping_object):
        """ Returns the training, validation and experimental chi2

        Parameters
        ----------
            `stopping_object`
                A Stopping intance which will have associated a validation model and the
                list of output layers that should contribute to the training chi2

        Returns
        -------
            `train_chi2`: chi2 of the trainining set
            `val_chi2` : chi2 of the validation set
            `exp_chi2`: chi2 of the experimental data (without replica or tr/vl split)
        """
        # Needs to receive a `stopping_object` in order to select the part of the
        # training and the validation which are actually `chi2` and not part of the penalty
        train_chi2 = stopping_object.evaluate_training(self.training["model"])
        val_chi2, _ = stopping_object.validation.loss()
        exp_chi2 = self.experimental["model"].fit_evaluate()["loss"] / self.experimental["ndata"]
        return train_chi2, val_chi2, exp_chi2

    def hyperparametizable(self, params):
        """
        Wrapper around all the functions defining the fit.

        After the ModelTrainer class has been instantiated,
        a call to this function (with a `params` dictionary) is necessary
        in order to generate the whole PDF model and perform a fit.

        This is a necessary step for hyperopt to work

        Parameters used only here:
            - `epochs`: maximum number of iterations for the fit to run
            - `stopping_patience`: patience of the stopper after finding a new minimum
        All other parameters are passed to the corresponding functions
        """

        # Reset the internal state of the backend
        print("")
        if not self.debug:
            clear_backend_state()

        # When doing hyperopt some entries in the params dictionary
        # can bring with them overriding arguments
        if self.mode_hyperopt:
            log.info("Performing hyperparameter scan")
            for key in self.hyperkeys:
                log.info(" > > Testing %s = %s", key, params[key])
            self._hyperopt_override(params)

        # Fill the 3 dictionaries (training, validation, experimental) with the layers and losses
        self._generate_observables(params["pos_multiplier"], params["pos_initial"])

        # Generate the pdf layer
        layers, integrator_input = self._generate_pdf(
            params["nodes_per_layer"],
            params["activation_per_layer"],
            params["initializer"],
            params["layer_type"],
            params["dropout"],
        )

        # Model generation
        self._model_generation()

        # Generate the stopping_object
        # this object holds statistical information about the fit
        # it can be used to perform stopping
        epochs = int(params["epochs"])
        stopping_patience = params["stopping_patience"]
        stopping_epochs = epochs * stopping_patience

        if self.no_validation:
            validation_model = self.training["model"]
        else:
            validation_model = self.validation["model"]

        stopping_object = Stopping(
            validation_model,
            self.all_info,
            total_epochs=epochs,
            stopping_patience=stopping_epochs,
            save_weights_each=self.save_weights_each,
        )

        # Compile the training['model'] with the given parameters
        self._model_compilation(params["learning_rate"], params["optimizer"])

        ### Training loop
        passed = self._train_and_fit(stopping_object, epochs)

        # Compute validation loss
        validation_loss = stopping_object.vl_loss

        # Compute experimental loss
        experimental_loss = self.experimental["model"].fit_evaluate()["loss"] / self.experimental["ndata"]

        # Compute the testing loss if it was given
        if self.test_dict:
            # Generate the 'true' chi2 with the experimental model
            # but only for models that were stopped
            target_model = self.test_dict["model"]
            testing_loss = target_model.fit_evaluate(verbose=False)["loss"] / self.test_dict["ndata"]
        else:
            testing_loss = 0.0

        if self.mode_hyperopt:
            final_loss = VALIDATION_MULTIPLIER * validation_loss
            final_loss += TEST_MULTIPLIER * testing_loss
            final_loss /= TEST_MULTIPLIER + VALIDATION_MULTIPLIER
            arc_lengths = msr_constraints.compute_arclength(layers["fitbasis"])
        else:
            final_loss = experimental_loss
            arc_lengths = None

        dict_out = {
            "loss": final_loss,
            "status": passed,
            "arc_lengths": arc_lengths,
            "training_loss": stopping_object.tr_loss,
            "validation_loss": validation_loss,
            "experimental_loss": experimental_loss,
            "testing_loss": testing_loss,
        }

        if self.mode_hyperopt:
            # If we are using hyperopt we don't need to output any other information
            return dict_out

        # Add to the output dictionary things that are needed by fit.py
        # to generate the output pdf, check the arc-length, gather stats, etc
        # some of them are already attributes of the class so they are redundant here
        # but I think it's good to present them explicitly
        dict_out["layer_pdf"] = self.layer_pdf
        dict_out["layers"] = layers
        dict_out["integrator_input"] = integrator_input
        dict_out["stopping_object"] = stopping_object
        dict_out["experimental"] = self.experimental
        dict_out["training"] = self.training

        return dict_out
