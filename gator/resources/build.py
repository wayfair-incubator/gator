from typing import Dict, Type

import yaml
from pydantic import ValidationError, parse_obj_as

from gator.exceptions import InvalidSpecificationError
from gator.resources.changeset import Changeset
from gator.resources.code_changes import (
    NewFileCodeChangeV1Alpha,
    RegexReplaceCodeChangeV1Alpha,
    RemoveFileCodeChangeV1Alpha,
)
from gator.resources.filters.regex_filter import RegexFilterV1Alpha
from gator.resources.models import GatorResource

ACTIVE_RESOURCES: Dict[str, Type[GatorResource]] = {
    "NewFileCodeChange": NewFileCodeChangeV1Alpha,
    "RemoveFileCodeChange": RemoveFileCodeChangeV1Alpha,
    "RegexReplaceCodeChange": RegexReplaceCodeChangeV1Alpha,
    "RegexFilter": RegexFilterV1Alpha,
}


def build_gator_resource(resource_dict: Dict) -> GatorResource:
    if "kind" not in resource_dict:
        raise InvalidSpecificationError(
            "Resources must have a 'kind' field at the top level"
        )

    _class = ACTIVE_RESOURCES.get(resource_dict["kind"])

    if not _class:
        raise InvalidSpecificationError(
            f"Resource kind: {resource_dict['kind']} is not active"
        )

    try:
        return _class.parse_obj(resource_dict)
    except ValidationError as e:
        raise InvalidSpecificationError from e


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
        return parse_obj_as(Changeset, changeset_dict)
    except ValidationError as e:
        raise InvalidSpecificationError from e
