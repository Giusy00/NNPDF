"""
    Module containing the classes related to the stopping alogirthm

    In this module there are four Classes:
    - FitState: this class contains the information of the fit
            for a given point in history
    - FitHistory: this class contains the information necessary
            in order to reset the state of the fit to the point
            in which the history was saved.
            i.e., a list of FitStates
    - Stopping: this class monitors the chi2 of the validation
            and training sets and decides when to stop
    - Positivity: Decides whether a given point fullfills the positivity conditions
"""

# TODO for TF 2.0
#   - Save a proper reference to the part of the NN we want to store instead of the whole model
#   - Make the return state from .fit and .evaluate consistent instead of relaying on keras

import logging
import numpy as np

log = logging.getLogger(__name__)

# Put a very big number here so that we for sure discard this run
# AND we have a clear marker that something went wrong, not just a bad fit
TERRIBLE_CHI2 = 1e10
INITIAL_CHI2 = 1e9

# Pass/veto keys
POS_OK = "POS_PASS"
POS_BAD = "POS_VETO"


def parse_ndata(all_data):
    """
    Parses the list of dictionaries received from ModelTrainer
    into a dictionary containing only the name of the experiments
    together with the number of points.

    # Return:
        - `tr_ndata`: dictionary of {'exp' : ndata}
        - `vl_ndata`: dictionary of {'exp' : ndata}
        - `pos_set`: list of the names of the positivity sets

    Note: if there is no validation (total number of val points == 0)
    then vl_ndata will point to tr_ndata
    """
    tr_ndata_dict = {}
    vl_ndata_dict = {}
    pos_set = []
    for dictionary in all_data:
        exp_name = dictionary["name"]
        if dictionary.get("count_chi2"):
            tr_ndata = dictionary["ndata"]
            vl_ndata = dictionary["ndata_vl"]
            if tr_ndata:
                tr_ndata_dict[exp_name] = tr_ndata
            if vl_ndata:
                vl_ndata_dict[exp_name] = vl_ndata
        if dictionary.get("positivity"):
            pos_set.append(exp_name)
    if not vl_ndata_dict:
        vl_ndata_dict = tr_ndata_dict
    return tr_ndata_dict, vl_ndata_dict, pos_set


class FitState:
    """
        Holds the state of the chi2 of the fit.

        It holds the necessary information to reload the fit
        to a specific point in time if we are interested on reloading
        (otherwise the relevant variables stay empty to save memory)

        # Arguments:
            - `all_tr_chi2`: all chi2 from training sets
            - `all_vl_chi2`: all chi2 from validation sets
            - `training_info`: return state from NN training
                        can include positivity sets, penalties, etc
    """

    def __init__(self, all_tr_chi2, all_vl_chi2, training_info):
        self.all_tr_chi2 = all_tr_chi2
        self.all_vl_chi2 = all_vl_chi2
        self.training_info = training_info
        # These two variables are only filled for specific points
        # in order to save precious memory, and only when we are
        # saving the fit history each X number of epoch
        self.weights = None
        self.best_epoch = 0

    def save_history(self, weights, best_epoch):
        """ Save the current best weights and best_epoch of the fit """
        self.weights = weights
        self.best_epoch = best_epoch

    @property
    def vl_chi2(self):
        """ Returns the total validation chi2 """
        return self.all_vl_chi2["total"]

    @property
    def tr_chi2(self):
        """ Returns the total training chi2 """
        return self.all_tr_chi2["total"]

    def __str__(self):
        return f"chi2: tr={self.tr_chi2} vl={self.vl_chi2}"


class FitHistory:
    """
        Keeps a list of FitState items holding the full history of the fit.

        It also keeps track of the best epoch and the associated weights.

        Can be iterated when there are snapshots of the fit being saved.
        When iterated it will rewind the fit to each of the point in history
        that have been saved.

        # Arguments:
            - `validation_model`: a reference to a Validaton object
                    this is necessary at the moment in order to save the weights
            - `save_each`: if given it will save a snapshot of the fit every  `save_each` epochs
    """

    def __init__(self, validation_model, save_each=None):
        self.validation_model = validation_model
        self.save_each = save_each
        # Initialize variables for the history
        self.weights = None
        self._best_epoch = -1
        self.final_epoch = 0
        self.history = []
        self.terrible = False
        # Initialize variables fort he snapshots
        self.reloadable_history = []

    @property
    def best_epoch(self):
        """ Epoch of the best fit """
        return self._best_epoch

    @best_epoch.setter
    def best_epoch(self, epoch):
        """ Saves the current weight """
        self.weights = self.validation_model.weights
        self._best_epoch = epoch

    def best_state(self):
        """ Return the FitState object corresponding to the best fit """
        if self.best_epoch < 0:
            return None
        else:
            index = self.best_epoch
            best_state = self.history[index]
            return best_state

    def best_vl(self):
        """ Returns the chi2 of the best fit
        if there was no best fit returns `INITIAL_CHI2`
        if there was a problem, returns `TERRIBLE_CHI2` """
        if self.terrible:
            return TERRIBLE_CHI2
        best_state = self.best_state()
        if best_state:
            return best_state.vl_chi2
        else:
            return INITIAL_CHI2

    def best_tr(self):
        """ Returns the training chi2 of the best fit
        if there are no best fit, returns the last one """
        best_state = self.best_state()
        if best_state:
            return best_state.tr_chi2
        else:
            return self.history[-1].tr_chi2

    def save(self, fitstate, epoch):
        """ Save a new fitstate and updates the current final epoch
        Every `save_each` (if set) saves a snapshot of the current best fit into
        the fitstate

        # Arguments:
            - `fitstate`: a fitstate object to save
            - `epoch`: the current epoch of the fit
        """
        self.final_epoch = epoch
        self.history.append(fitstate)
        if self.save_each:
            save_here = (epoch + 1) % self.save_each
            if save_here == 0:
                fitstate.save_history(self.weights, self.best_epoch)
                self.reloadable_history.append(fitstate)

    def reload(self):
        """ Reloads the best fit weights into the model """
        if self.weights:
            self.validation_model.weights = self.weights
        else:
            # If there was no model at this point, this was
            # a terrible run, mark it as such
            self.terrible = True

    def __iter__(self):
        """ Iterate over the fitstate members which have weights
        saved on them.
        Rewind the FitHistory object to that point in the fit """
        for i, fitstate in enumerate(self.reloadable_history):
            log.info("Reloading step %d", i)
            self.weights = fitstate.weights
            self.best_epoch = fitstate.best_epoch
            self.final_epoch = (i + 1) * self.save_each
            self.reload()
            yield i


class Stopping:
    """
        Driver of the stopping algorithm

        Note, if the total number of points in the validation dictionary is None, it is assumed
        the validation_model actually corresponds to the training model.

        # Arguments:
            - `validation_model`: the model with the validation mask applied
                                  (and compiled with the validation data and covmat)
            - `all_data_dict`: list containg all dictionaries containing all information about
                              the experiments/validation/regularizers/etc to be parsed by Stopping
            - `threshold_positivity`: maximum value allowed for the sum of all positivity losses
            - `total_epochs`: total number of epochs
            - `stopping_patience`: how many epochs to wait for the validation loss to improve
            - `dont_stop`: dont care about early stopping
            - `save_each`: every how many epochs to save a snapshot of the fit
    """

    def __init__(
        self,
        validation_model,
        all_data_dicts,
        threshold_positivity=1e-6,
        total_epochs=0,
        stopping_patience=7000,
        dont_stop=False,
        save_each=None,
    ):
        # Parse the training, validation and positivity sets from all the input dictionaries
        self.tr_ndata, vl_ndata, pos_sets = parse_ndata(all_data_dicts)

        # Create the Validation, Positivity and History objects
        self.validation = Validation(validation_model, vl_ndata)
        self.positivity = Positivity(threshold_positivity, pos_sets)
        self.history = FitHistory(self.validation, save_each=save_each)

        # Initialize internal variables for the stopping
        self.dont_stop = dont_stop
        self.stop_now = False
        self.stopping_patience = stopping_patience
        self.stopping_degree = 0
        self.count = 0
        self.total_epochs = total_epochs

    @property
    def vl_loss(self):
        """ Validation loss """
        return self.history.best_vl()

    @property
    def tr_loss(self):
        """ Training loss """
        return self.history.best_tr()

    @property
    def e_best_chi2(self):
        """ Epoch of the best chi2 """
        return self.history.best_epoch

    @property
    def epoch_of_the_stop(self):
        """ Epoch in which the fit is stopped """
        return self.history.final_epoch + 1

    def monitor_chi2(self, training_info, epoch, print_stats=False):
        """
        Function to be called at the end of every epoch.
        Stores the total chi2 of the training set as well as the
        total chi2 of the validation set.
        If the training chi2 is below a certain threshold,
        stores the state of the model which gave the minimum chi2
        as well as the epoch in which occurred
        If the epoch is a multiple of save_all_each then we also save the per-exp chi2

        Returns True if the run seems ok and False if a NaN is found

        # Arguments:
            - `training_info`: the output of a .fit() run
            - `epoch`: the index of the epoch

        # Returns:
            - `pass_ok`: true/false according to the status of the run
        """
        # Step 1. Preprocess the event, count it towards the stopping degree
        #         parse the training information and check whether it is a good point
        tr_chi2, all_tr = self._parse_training(training_info)

        if np.isnan(tr_chi2):
            log.warning(" > NaN found, stopping activated")
            self.stop_now = True
            # If we had a good model at any point, reload
            self.history.reload()
            return False

        self.stopping_degree += self.count

        # Step 2. Check the validation loss at this point
        vl_chi2, all_vl = self.validation.loss()

        # Step 3. Store information about the run and print stats if asked
        fitstate = FitState(all_tr, all_vl, training_info)
        self.history.save(fitstate, epoch)
        if print_stats:
            self.print_current_stats(epoch, fitstate)

        # Step 4. Check whether this is a better fit
        #         this means improving vl_chi2 and passing positivity
        if self.positivity(fitstate):
            if vl_chi2 < self.history.best_vl():
                # Set the new best
                self.history.best_epoch = epoch
                # Save stopping info
                self.stopping_degree = 0
                # Initialize the counter
                self.count = 1

        # If your patience has ended, prepare for stop
        if self.stopping_degree > self.stopping_patience:
            self.stop_now = True
            self.history.reload()
        return True

    def print_current_stats(self, epoch, fitstate):
        """
            Prints the last validation and training loss saved
        """
        epoch_index = epoch + 1
        tr_loss = fitstate.tr_chi2
        vl_loss = fitstate.vl_chi2
        total_str = (
            f"At epoch {epoch_index}/{self.total_epochs}, total loss: {tr_loss}\n"
        )

        partials = []
        for experiment in self.tr_ndata:
            chi2 = fitstate.all_tr_chi2[experiment]
            partials.append(f"{experiment}: {chi2:.3f}")
        total_str += ", ".join(partials)

        total_str += f"\nValidation loss at this point: {vl_loss}"
        log.info(total_str)

    def _parse_training(self, training_info):
        """
        Receives an object containg the training chi2.
        Usually a history object, but it can come in the form of a dictionary.

        It loops over the dictionary and uses the npoints_data dictionary to
        normalize the chi2 and return backs a tuple (`total`, `tr_chi2`)

        # Arguments:
            - `training_info`: history object

        # Returns:
            - `total` : total value for the training loss
            - `tr_chi2`: dictionary of {'expname' : loss }
        """
        try:
            hobj = training_info.history
        except AttributeError:  # So it works whether we pass the out our the out.history
            hobj = training_info

        # In the general case epochs = 1.
        # In case that we are doing more than 1 epoch, take the average to smooth out
        # fluctuations.
        # This value is only used for printing output purposes so should not have any significance
        tr_chi2 = {}
        total_points = 0
        total_loss = 0
        for exp_name, npoints in self.tr_ndata.items():
            loss = np.mean(hobj[exp_name + "_loss"])
            tr_chi2[exp_name] = loss / npoints
            total_points += npoints
            total_loss += loss

        # By taking the loss from the history object we would be saving the total loss
        # including positivity sets and (if added/enabled) regularizsers
        # instead we want to restrict ourselves to the loss coming from experiments
        # total_loss = np.mean(hobj["loss"]) / total_points
        total_loss /= total_points
        tr_chi2["total"] = total_loss
        return total_loss, tr_chi2

    def stop_here(self):
        """ Returns the stopping status
        If `dont_stop` is set returns always False (i.e., never stop)
        """
        if self.dont_stop:
            return False
        else:
            return self.stop_now

    def positivity_pass(self):
        """ Checks whether the positivity loss is below the requested threshold """
        if self.positivity(self.history.best_state()):
            return POS_OK
        else:
            return POS_BAD

    def chi2exps_str(self, log_each=100):
        """
        Returns a list of log-string with the status of the fit
        every `log_each` epochs

        # Arguments:
            - `log_each`: every how many epochs to print the log

        # Returns:
            - `file_list`: a list of string to be printed as `chi2exps.log`
        """
        final_epoch = self.history.final_epoch
        file_list = []
        for i in range(log_each - 1, final_epoch + 1, log_each):
            fitstate = self.history.history[i]
            all_tr = fitstate.all_tr_chi2
            all_vl = fitstate.all_vl_chi2
            # Here it is assumed the validation exp set is always a subset of the training exp set
            data_list = []
            for exp in self.tr_ndata:
                tr_loss = all_tr[exp]
                vl_loss = all_vl.get(exp, 0.0)
                data_str = f"{exp}: {tr_loss} {vl_loss}"
                data_list.append(data_str)
            data = "\n".join(data_list)
            epoch_index = i + 1
            total_tr_loss = fitstate.tr_chi2
            total_vl_loss = fitstate.vl_chi2
            strout = f"""
Epoch: {epoch_index}
{data}
Total: training = {total_tr_loss} validation = {total_vl_loss}
"""
            file_list.append(strout)
        return file_list


class Validation:
    """
        Controls the NNPDF cross-validation algorithm

        The cross-validation refers to the validation loss of the points of the dataset
        not used in the fitting.
        In general for any points considered here there will accompanying points from the
        same dataset being included in the fitting.

        # Arguments:
            - `model`: the model with the validation mask applied
                       (and compiled with the validation data and covmat)
    """

    def __init__(self, model, ndata_dict, verbose=False):
        self.model = model
        self.verbose = verbose
        self.ndata_dict = ndata_dict
        # If there are extra losses they will appear at the end of the list, so we want to restrict
        # ourselves to the chi2, which means we want to go up to the number of exp. with validation
        self.n_val_exp = len(ndata_dict)

    def _compute_validation_loss(self):
        # TODO: most of the functionality of this function is equal to that of _parse_training
        #       and has no need for self.stuff BUT it is necessary to deal with the TODO at the
        #       beginning of the file first
        """
        Evaluates the validation model and returns a tuple (`total_loss`, `vl_dict`)
        with the information for the validation loss by experimenet normalized to the
        number of points of each experiment

        # Returns:
            - `total_loss`: total vale for the validation loss
            - `vl_dict`: dictionary containing a map of experiment names and loss
        """
        # The variable vl_list is a list of all losses of the model, where the first element
        # is sum of all other elements
        loss_list = self.model.evaluate(verbose=self.verbose)

        # This loop relies on the information that comes through the input dict to be accurate
        # because since (at the moment) the list that evaluate returns has no names, we need to
        # assume they come in the correct order (same order as the traiing losses)
        vl_dict = {}
        total_points = 0
        total_loss = 0
        for loss, (exp_name, npoints) in zip(
            loss_list[1 : 1 + self.n_val_exp], self.ndata_dict.items()
        ):
            vl_dict[exp_name] = loss / npoints
            total_loss += loss
            total_points += npoints

        total_loss /= total_points
        vl_dict["total"] = total_loss

        return total_loss, vl_dict

    @property
    def weights(self):
        """ Returns the weights of the validation model """
        return self.model.get_weights()

    @weights.setter
    def weights(self, weights):
        """  Sets the weights on the validation model """
        self.model.set_weights(weights)

    def loss(self):
        """
        Returns a tuple with the validation loss and a
        dictionary for the validation loss per experiment
        """
        return self._compute_validation_loss()


class Positivity:
    """
        Controls the positivity requirements.

        In order to check the positivity passes will check the history of the fitting
        as the fitting included positivity sets.
        If the sum of all positivity sets losses is above a certain value the model is
        not accepted and the training continues.

        # Arguments:
            - `threshold_positivity`: maximum value allowed for the sum of all positivity losses
    """

    def __init__(self, threshold, positivity_sets):
        self.threshold = threshold
        self.positivity_sets = positivity_sets

    def check_positivity(self, history_object):
        """
            This function receives a history object and look for entries
            with the keyname: pos_key_something


            # Arguments:
                - `history_object`: a dictionary of entries in the form
                    {'name': loss}, output of a MetaModel .fit()
                - `pos_key`: `key that searchs for the positivity`
        """
        positivity_loss = 0.0
        for key in self.positivity_sets:
            key_loss = f"{key}_loss"
            positivity_loss = history_object[key_loss][-1]
        if positivity_loss > self.threshold:
            return False
        else:
            return True

    def __call__(self, fitstate):
        """
            Checks whether a given FitState object
            passes the positivity requirement
        """
        return self.check_positivity(fitstate.training_info)
