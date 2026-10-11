from abc import ABC, abstractmethod

import pandas as pd


class Transformer(ABC):
    """Transformer class"""
    name = "transformer"
    

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

