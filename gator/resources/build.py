from typing import Dict, List, Optional, Type

import yaml
from pydantic import ValidationError

from gator.exceptions import InvalidResourceError, InvalidSpecificationError
from gator.resources.code_changes import (
    NewFileCodeChangeV1Alpha,
    RegexReplaceCodeChangeV1Alpha,
    RemoveFileCodeChangeV1Alpha,
)
from gator.resources.filters.regex_filter import RegexFilterV1Alpha
from gator.resources.models import (
    BaseModelForbidExtra,
    CodeChangeResource,
    FilterResource,
    GatorResource,
)

ACTIVE_RESOURCES = {
    "NewFileCodeChange": NewFileCodeChangeV1Alpha,
    "RemoveFileCodeChange": RemoveFileCodeChangeV1Alpha,
    "RegexReplaceCodeChange": RegexReplaceCodeChangeV1Alpha,
    "RegexFilter": RegexFilterV1Alpha,
}


class _ResourceWithValidation(GatorResource):
    """
    Define a subclass of Gator Resource for Pydantic deserialization purposes.

    This subclass uses Pydantic validators to look up the classes associated
    with given resource names in a registry, allowing deserialization of
    resources not present in the registry at import time (Custom Resources).
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.return_kind

    @classmethod
    def return_kind(cls, values):
        try:
            kind = values["kind"]
        except KeyError:
            raise ValueError(f"Missing required 'kind' field for kind: {values}")
        try:
            return ACTIVE_RESOURCES[kind].parse_obj(values)
        except KeyError:
            raise ValueError(f"Incorrect kind: {kind}")


class ChangesetSpecV1AlphaSpec(BaseModelForbidExtra):
    """Changeset Specification."""
    name: str
    issue_title: Optional[str]
    issue_body: Optional[str]
    filters: Optional[List[_ResourceWithValidation]]
    code_changes: Optional[List[_ResourceWithValidation]]


class Changeset(BaseModelForbidExtra):
    """Define Changeset."""
    kind = "Changeset"
    version = "v1alpha"
    spec: ChangesetSpecV1AlphaSpec


def build_changeset(spec: str) -> Changeset:
    """
    Given a string containing raw yaml, build a Changeset object.

    :param spec: A raw yaml string containing the changeset definition
    :raises InvalidSpecificationError: If anything went wrong.
    :return Changeset: The fully constructed pydantic model representing a
    """
    try:
        changeset_dict = yaml.safe_load(spec)
    except yaml.YAMLError as e:
        raise InvalidSpecificationError from e

    try:
        return Changeset.parse_obj(changeset_dict)
    except ValidationError as e:
        raise InvalidSpecificationError from e


def build_gator_resource(resource_dict: Dict) -> GatorResource:
    """
    Build a Gator Resource Pydantic model from a dictionary representation.

    :param resource_dict: dictionary representation of the resource to build a model for.
    :raises InvalidSpecificationError: If the resource dict could not be built into a model.
    :return: Fully-constructed and validated GatorResource.
    """
    kind = resource_dict.get("kind")
    if not kind:
        raise InvalidSpecificationError(
            "Resource is not valid, must contain top-level field 'kind'"
        )

    resource_class = ACTIVE_RESOURCES.get(kind)
    if not resource_class:
        raise InvalidSpecificationError(f"No active resources found of kind: {kind}")

    try:
        return resource_class.parse_obj(resource_dict)
    except ValidationError as e:
        raise InvalidSpecificationError(
            "Could not parse resource spec into the corresponding model"
        ) from e


def register_custom_resource(resource_class: Type) -> None:
    """
    Register a custom Gator resource.

    Use this function to register a custom resource with Gator.
    :param resource_class: Pydantic class, extending CodeChangeResource or FilterResource,
        that contains the business logic for executing the resource
    """
    global ACTIVE_RESOURCES

    if not issubclass(resource_class, CodeChangeResource) or issubclass(
        resource_class, FilterResource
    ):
        raise InvalidResourceError(
            "Resource must subclass either CodeChangeResource or FilterResource"
        )

    try:
        ACTIVE_RESOURCES[
            resource_class.schema()["properties"]["kind"]["const"]
        ] = resource_class
    except KeyError:
        raise InvalidResourceError(
            "Custom resource must define a class variable 'kind'"
        )
