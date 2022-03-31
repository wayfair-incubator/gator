from abc import abstractmethod
from pathlib import Path

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from gator.constants import RESOURCE_KIND_GENERIC, RESOURCE_VERSION_UNUSABLE


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


# Hierarchy of metaclasses: `ValidateGatorResource` extends `pydantic.main.ModelMetaclass` extends `abc.ABCMeta`
# Classes using `metaclass=GatorResourceMetaclass` must assume inclusion of the base metaclasses
class GatorResourceMetaclass(ModelMetaclass):
    def __new__(meta, name, bases, class_dict):
        """
        Validate class definitions upon initial module load.
        """

        if not class_dict.get("kind", "") or not class_dict.get("version", ""):
            raise ValueError(
                "GatorResources must define `kind` and `version` class properties"
            )

        return type.__new__(meta, name, bases, class_dict)


class GatorResource(BaseModelForbidExtra):
    """
    GatorResources define a specific `kind`, `version`, and associated spec fields.
    """

    kind: str = ""
    version: str = ""
    spec: GatorResourceSpec


class FilterResource(GatorResource, metaclass=GatorResourceMetaclass):

    kind = RESOURCE_KIND_GENERIC
    version = RESOURCE_VERSION_UNUSABLE

    @abstractmethod
    def matches(self, repo_path: Path) -> bool:
        """
        Concrete FilterResources must implement the `matches` function.

        :param repo_path: The path to the directory where repository content exists
        """
        ...


class CodeChangeResource(GatorResource, metaclass=GatorResourceMetaclass):

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
