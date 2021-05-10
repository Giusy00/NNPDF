"""
    Fit action controller
"""

# Backend-independent imports
from collections import namedtuple
import logging
import numpy as np
import n3fit.checks
from n3fit.vpinterface import N3PDF

log = logging.getLogger(__name__)


# Action to be called by validphys
# All information defining the NN should come here in the "parameters" dict
@n3fit.checks.can_run_multiple_replicas
@n3fit.checks.check_consistent_basis
@n3fit.checks.wrapper_check_NN
@n3fit.checks.wrapper_hyperopt
@n3fit.checks.check_deprecated_options
def performfit(
    *,
    replicas, # used for checks
    genrep, # used for checks
    data, # used for checks
    replicas_nnseed_fitting_data_dict,
    posdatasets_fitting_pos_dict,
    integdatasets_fitting_integ_dict,
    theoryid,
    basis,
    fitbasis,
    sum_rules=True,
    parameters,
    replica_path,
    output_path,
    save=None,
    load=None,
    hyperscan=None,
    hyperopt=None,
    kfold_parameters,
    tensorboard=None,
    debug=False,
    maxcores=None,
    parallel_models=1
):
    """
        This action will (upon having read a validcard) process a full PDF fit
        for a set of replicas.

        The input to this function is provided by validphys
        and/or defined in the runcards or commandline arguments.

        This controller is provided with:
        1. Seeds generated using the replica number and the seeds defined in the runcard.
        2. Loaded datasets with replicas generated.
            2.1 Loaded positivity/integrability sets.

        The workflow of this controller is as follows:
        1. Generate a ModelTrainer object holding information to create the NN and perform a fit
            (at this point no NN object has been generated)
            1.1 (if hyperopt) generates the hyperopt scanning dictionary
                    taking as a base the fitting dictionary  and the runcard's hyperscan dictionary
        2. Pass the dictionary of parameters to ModelTrainer
                                        for the NN to be generated and the fit performed
            2.1 (if hyperopt) Loop over point 4 for `hyperopt` number of times
        3. Once the fit is finished, output the PDF grid and accompanying files

        Parameters
        ----------
            genrep: bool
                Whether or not to generate MC replicas. (Only used for checks)
            data: validphys.core.DataGroupSpec
                containing the datasets to be included in the fit. (Only used
                for checks)
            replicas_nnseed_fitting_data_dict: list[tuple]
                list with element for each replica (typically just one) to be
                fitted. Each element
                is a tuple containing the replica number, nnseed and
                ``fitted_data_dict`` containing all of the data, metadata
                for each group of datasets which is to be fitted.
            posdatasets_fitting_pos_dict: list[dict]
                list of dictionaries containing all data and metadata for each
                positivity dataset
            integdatasets_fitting_integ_dict: list[dict]
                list of dictionaries containing all data and metadata for each
                integrability dataset
            theoryid: validphys.core.TheoryIDSpec
                Theory which is used to generate theory predictions from model
                during fit. Object also contains some metadata on the theory
                settings.
            basis: list[dict]
                preprocessing information for each flavour to be fitted.
            fitbasis: str
                Valid basis which the fit is to be ran in. Available bases can
                be found in :py:mod:`validphys.pdfbases`.
            sum_rules: bool
                Whether to impose sum rules in fit. By default set to True
            parameters: dict
                Mapping containing parameters which define the network
                architecture/fitting methodology.
            replica_path: pathlib.Path
                path to the output of this run
            output_path: str
                name of the fit
            save: None, str
                model file where weights will be saved, used in conjunction with
                ``load``.
            load: None, str
                model file from which to load weights from.
            hyperscan: dict
                dictionary containing the details of the hyperscan
            hyperopt: int
                if given, number of hyperopt iterations to run
            kfold_parameters: None, dict
                dictionary with kfold settings used in hyperopt.
            tensorboard: None, dict
                mapping containing tensorboard settings if it is to be used. By
                default it is None and tensorboard is not enabled.
            debug: bool
                activate some debug options
            maxcores: int
                maximum number of (logical) cores that the backend should be aware of
            parallel_models: int
                number of models to be run in parallel
    """
    from n3fit.backends import set_initial_state

    # If debug is active, the initial state will be fixed so that the run is reproducible
    set_initial_state(debug=debug, max_cores=maxcores)

    from n3fit.stopwatch import StopWatch

    stopwatch = StopWatch()

    # All potentially backend dependent imports should come inside the fit function
    # so they can eventually be set from the runcard
    from n3fit.model_trainer import ModelTrainer
    from n3fit.io.writer import WriterWrapper

    # Note: In the basic scenario we are only running for one replica and thus this loop is only
    # run once as replicas_nnseed_fitting_data_dict is a list of just one element
    for replica_number, exp_info, nnseed in replicas_nnseed_fitting_data_dict:
        replica_path_set = replica_path / f"replica_{replica_number}"
        if parallel_models == 1:
            log.info("Starting replica fit %s", replica_number)
        else:
            log.info(
                "Starting replica fits %s to %s",
                replica_number,
                replica_number + parallel_models - 1,
            )

        # Generate a ModelTrainer object
        # this object holds all necessary information to train a PDF (up to the NN definition)
        the_model_trainer = ModelTrainer(
            exp_info,
            posdatasets_fitting_pos_dict,
            integdatasets_fitting_integ_dict,
            basis,
            fitbasis,
            nnseed,
            debug=debug,
            kfold_parameters=kfold_parameters,
            max_cores=maxcores,
            model_file=load,
            sum_rules=sum_rules,
            parallel_models=parallel_models
        )

        # This is just to give a descriptive name to the fit function
        pdf_gen_and_train_function = the_model_trainer.hyperparametrizable

        # Read up the parameters of the NN from the runcard
        stopwatch.register_times("replica_set")

        ########################################################################
        # ### Hyperopt                                                         #
        # If hyperopt is active the parameters of NN will be substituted by the#
        # hyoperoptimizable variables.                                         #
        # Hyperopt will run for --hyperopt number of iterations before leaving #
        # this block                                                           #
        ########################################################################
        if hyperopt:
            from n3fit.hyper_optimization.hyper_scan import hyper_scan_wrapper

            true_best = hyper_scan_wrapper(
                replica_path_set, the_model_trainer, parameters, hyperscan, max_evals=hyperopt,
            )
            print("##################")
            print("Best model found: ")
            for k, i in true_best.items():
                print(f" {k} : {i} ")

            # In general after we do the hyperoptimization we do not care about the fit
            # so just let this die here
            break
        ####################################################################### end of hyperopt

        # Ensure hyperopt is off
        the_model_trainer.set_hyperopt(False)

        # Enable the tensorboard callback
        if tensorboard is not None:
            profiling = tensorboard.get("profiling", False)
            weight_freq = tensorboard.get("weight_freq", 0)
            log_path = replica_path_set / "tboard"
            the_model_trainer.enable_tensorboard(log_path, weight_freq, profiling)

        #############################################################################
        # ### Fit                                                                   #
        # This function performs the actual fit, it reads all the parameters in the #
        # "parameters" dictionary, uses them to generate the NN and trains the net  #
        #############################################################################
        result = pdf_gen_and_train_function(parameters)
        stopwatch.register_ref("replica_fitted", "replica_set")

        stopping_object = result["stopping_object"]
        log.info("Stopped at epoch=%d", stopping_object.stop_epoch)

        final_time = stopwatch.stop()
        all_training_chi2, all_val_chi2, all_exp_chi2 = the_model_trainer.evaluate(stopping_object)

        pdf_models = result["pdf_models"]
        for i, pdf_model in enumerate(pdf_models):
            # Each model goes into its own replica folder
            replica_path_set = replica_path / f"replica_{replica_number + i}"

            # Create a pdf instance
            pdf_instance = N3PDF(pdf_model, fit_basis=basis)

            # Generate the writer wrapper
            writer_wrapper = WriterWrapper(
                replica_number,
                pdf_instance,
                stopping_object,
                theoryid.get_description().get("Q0") ** 2,
                final_time,
            )

            # Get the right chi2s
            training_chi2 = np.take(all_training_chi2, i)
            val_chi2 = np.take(all_val_chi2, i)
            exp_chi2 = np.take(all_exp_chi2, i)

            # And write the data down
            writer_wrapper.write_data(
                replica_path_set, output_path.name, training_chi2, val_chi2, exp_chi2
            )
            log.info(
                    "Best fit for replica #%d, chi2=%.3f (tr=%.3f, vl=%.3f)",
                    replica_number+i,
                    exp_chi2,
                    training_chi2,
                    val_chi2
                    )


            # Save the weights to some file for the given replica
            if save:
                model_file_path = replica_path_set / save
                log.info(" > Saving the weights for future in %s", model_file_path)
                # Need to use "str" here because TF 2.2 has a bug for paths objects (fixed in 2.3)
                pdf_model.save_weights(str(model_file_path), save_format="h5")

        if tensorboard is not None:
            log.info("Tensorboard logging information is stored at %s", log_path)
