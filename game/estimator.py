from dataclasses import dataclass, field
from typing import List, Tuple
from pathlib import Path

import numpy as np
import tensorflow as tf


@dataclass
class Estimator:
    """
    ニューラルネットによる推定
    """

    name: str
    n_class: int
    hidden_layers: List[int]

    def __init__(self,
                 name: str,
                 n_class: int,
                 hidden_layers: List[int] = [16, 8]):
        self.name = name
        self.n_class = n_class
        self.hidden_layers = hidden_layers
        self.model = None
        self.model_prob = None

    def get_dir(self) -> Path:
        return Path.home() / ".rpg-ai-battle" / "models" / self.get_tag()

    def get_tag(self) -> str:
        model_name = "DNN"
        for hl in self.hidden_layers:
            model_name += '-%d' % hl
        return model_name

    def get_path(self) -> Path:
        return self.get_dir() / (self.name + ".h5")

    def build_model(self, inputs=None):
        if inputs is None:
            inputs = [
                tf.keras.Input(shape=(1,), name="input_v"),
                tf.keras.Input(shape=(self.n_class,), name="input_c"),
            ]

        _v, _c = inputs

        # not so good
        # _ = tf.keras.layers.Concatenate()([_v, _c])
        # _ = tf.keras.layers.Dense(self.hidden_layers[0])(_)

        # more better
        _c = tf.keras.layers.Dense(self.hidden_layers[0])(_c)
        _ = tf.keras.layers.Concatenate()([_v, _c])

        _ = tf.keras.layers.Dense(self.hidden_layers[1])(_)
        _ = tf.keras.layers.Dense(1, name="output")(_)

        self.model = tf.keras.Model(inputs, _)
        self.model.compile(loss='mean_squared_error', optimizer="adam")

    def load_model(self):
        self.model = tf.keras.models.load_model(str(self.get_path()))

    def save_model(self):
        # import shutil
        # shutil.rmtree(self.get_dir(), ignore_errors=True)
        model_dir = self.get_dir()
        model_dir.mkdir(parents=True, exist_ok=True)
        tf.keras.models.save_model(self.model, str(self.get_path()))
