from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class RuleResult:
    rule: str
    passed: bool
    failed_rows: int


class Rule(ABC):
    @abstractmethod
    def check(self, df: pd.DataFrame) -> RuleResult:
        raise NotImplementedError


class NotNullRule(Rule):

    def __init__(self, columns: list[str]) -> None:
        self.columns = columns

    def check(self, df: pd.DataFrame) -> RuleResult:
        missing = int((df[self.columns]).isna().any(axis=1).sum())
        return RuleResult(f"not_null{self.columns}", missing == 0, missing)