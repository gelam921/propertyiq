from abc import ABC, abstractmethod

import pandas as pd


class Transformer(ABC):
    """Transformer class"""
    name = "transformer"
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

