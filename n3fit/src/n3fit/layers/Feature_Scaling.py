import numpy as np

from n3fit.backends import MetaLayer
from tensorflow.keras import backend as K
import tensorflow as tf

class Feature_Scaling(MetaLayer):
    """
        Applies a Normalisation of the x-grid distribution.
    """

    def __init__(
        self, scaler=False, feature_range=(-1, 1), with_mean=True, with_std=True, **kwargs
    ):

        scaler_list = ["MinMaxScaler", "StandardScaler", "Test"]

        # name scalar type
        self.scaler = scaler
        if self.scaler != False:
            if self.scaler not in scaler_list:
                raise ValueError(f"Feature Scaling does not support '{self.scaler}'.")

        # input options for MinMaxScaler
        feature_range = feature_range

        # input options for StandardScalar
        self.with_mean = with_mean
        self.with_std = with_std

        # Replicate distrubtion on x-grid of the experimental data
        # if self.scaler != False:
        #     fake_x = np.concatenate(
        #         (np.logspace(-6, -3, num=50, endpoint=False), np.linspace(1e-3, 1, num=50))
        #     )

        # List of scalers
        if self.scaler == "MinMaxScaler":
            self.scale_ = feature_range[1] - feature_range[0]
            self.min_ = feature_range[0] - fake_x.min() * self.scale_
        elif self.scaler == "StandardScaler":
            if self.with_mean:
                self.mean_ = np.mean(fake_x)
            else:
                self.mean_ = 0
            if self.with_std:
                self.std_ = np.std(fake_x)
            else:
                self.std_ = 1

        super().__init__(**kwargs)

    def call(self, x_raw):
        x = x_raw

        def log10(x):
            numerator = K.log(x)
            denominator = K.log( tf.constant(10, dtype=numerator.dtype))
            return numerator/denominator

        if self.scaler == "MinMaxScaler":
            pass
        elif self.scaler == "StandardScaler":
            if self.with_mean:
                x -= self.mean_
            if self.with_std:
                x /= self.std_
        elif self.scaler == "Test":
            x = log10(x*1e3)/3
            # x -= 1.07e-6
            # x /= (0.75-1.07e-6)
            # x *= (1 - -1)
            # x += -1

        return x
