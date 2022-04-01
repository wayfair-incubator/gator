from abc import abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel

from gator.constants import RESOURCE_KIND_GENERIC, RESOURCE_VERSION_UNUSABLE


class GatorResourceType(Enum):
    FILTER = "filter"
    CODE_CHANGE = "code_change"
    CHANGESET = "changeset"


class BaseModelForbidExtra(BaseModel):
    """
    All subclasses will forbid members not explicitly defined.
    """

    class Config:
        extra = "forbid"


class GatorResourceSpec(BaseModelForbidExtra):
    """
    GatorResourceSpec's will define the actual configurable fields of a resource.
    """


class GatorResource(BaseModelForbidExtra):
    """
    GatorResources define a specific `kind`, `version`, and associated spec fields.
    """

    spec: GatorResourceSpec


class FilterResource(GatorResource):

    kind = RESOURCE_KIND_GENERIC
    version = RESOURCE_VERSION_UNUSABLE

    @abstractmethod
    def matches(self, repo_path: Path) -> bool:
        """
        Concrete FilterResources must implement the `matches` function.

        :param repo_path: The path to the directory where repository content exists
        """
        ...


class CodeChangeResource(GatorResource):

    kind = RESOURCE_KIND_GENERIC
    version = RESOURCE_VERSION_UNUSABLE

    @abstractmethod
    def make_code_changes(self, repo_path: Path) -> None:
        """
        Concrete CodeChangeResources must implement the `apply` function.

        `make_code_changes` will apply a code change given the repository
        :repo_path: The path to the directory where repository content exists
        """
        ...


class GatorResourceData(BaseModelForbidExtra):
    """
    Represents shape of data provided to `build_gator_resource()`.
    """

    kind: str
    version: str
    spec: Dict[str, Any]
