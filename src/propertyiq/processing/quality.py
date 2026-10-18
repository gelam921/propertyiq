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


class RangeRule(Rule):
    def __init__(
        self,
        column: str,
        min_value: float | None = None,
        max_value: float | None = None,
    ) -> None:
        self.column = column
        self.min_value = min_value
        self.max_value = max_value

    def check(self, df: pd.DataFrame) -> RuleResult:
        s = df[self.column].dropna()
        out_of_range = pd.Series(False, index=s.index)
        if self.max_value is not None:
            out_of_range |= s > self.max_value
        if self.min_value is not None:
            out_of_range |= s < self.min_value
        failed = int(out_of_range.sum())
        return RuleResult(
            f"out_of_range({self.column}, {self.min_value}, {self.max_value})",
            failed == 0,
            failed,
        )


class UniqueRule(Rule):
    def __init__(self, columns: list[str]) -> None:
        self.columns = columns

    def check(self, df: pd.DataFrame) -> RuleResult:
        s = df.duplicated(subset=self.columns)
        failed = int(s.sum())
        return RuleResult(f"unique({self.columns})", failed == 0, failed)


@dataclass(frozen=True)
class QualityReport:
    dataset: str
    rows: int
    results: list[RuleResult]

    @property
    def score(self) -> float:
        if len(self.results) == 0:
            return 100.0
        count_passed = sum(r.passed for r in self.results)
        total_results = len(self.results)
        passed_percentage = round(count_passed / total_results * 100, 1)
        return passed_percentage

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def failures(self) -> list[RuleResult]:
        return [r for r in self.results if not r.passed]


class Validator:
    def __init__(self, rules: list[Rule]) -> None:
        self.rules = rules

    def run(self, dataset: str, df: pd.DataFrame) -> QualityReport:
        out = df
        findings = [r.check(out) for r in self.rules]
        return QualityReport(dataset, rows=len(out), results=findings)
