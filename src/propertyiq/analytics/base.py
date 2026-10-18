from abc import ABC, abstractmethod

import pandas as pd


class Analyzer(ABC):
    """Analytics class"""

    title = "analysis"

    @abstractmethod
    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError