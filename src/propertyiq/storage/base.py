from abc import ABC, abstractmethod

import pandas as pd


class Repository(ABC):
    """Repository used to save and load DataFrames """

    @abstractmethod
    def save(self, name: str, df: pd.DataFrame) -> None:
        """" saves files"""
        raise NotImplementedError

    @abstractmethod
    def load(self, name: str) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def list_datasets(self) -> list[str]:
        raise NotImplementedError