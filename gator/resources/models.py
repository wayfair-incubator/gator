from abc import abstractmethod
from pathlib import Path

from pydantic import BaseModel


class BaseModelForbidExtra(BaseModel):
    """
    All subclasses will forbid members not explicitly defined.
    """

    class Config:
        extra = "forbid"


class GatorResource(BaseModel):
    """
    Base class for all Gator Resources.
    """

    class Config:
        fields = {"kind": dict(const=True)}
        extra = "forbid"


class FilterResource(GatorResource):
    @abstractmethod
    def matches(self, repo_path: Path) -> bool:
        ...


class CodeChangeResource(GatorResource):
    @abstractmethod
    def make_code_changes(self, repo_path: Path) -> None:
        ...
