from pathlib import Path

import pytest
import yaml
from pydantic import BaseModel

from gator.exceptions import InvalidResourceError, InvalidSpecificationError
from gator.resources.build import (
    CodeChangeResource,
    build_changeset,
    build_gator_resource,
    register_custom_resource,
)

SOME_INVALID_YAML = """not: real: \n- : -"""
SOME_INVALID_CHANGESET = """
some-unknown-field: value
"""

SOME_CHANGESET_UNKNOWN_RESOURCE = """
kind: Changeset
version: v1alpha
spec:
  name: time to do a thing
  issue_title: stuff
  issue_body: other stuff
  filters:
      - kind: SomeUnknownFilter
        version: v1alpha
        spec:
          stuff: stuff
"""

SOME_CHANGESET_RESOURCE_WITHOUT_KIND = """
kind: Changeset
version: v1alpha
spec:
  name: time to do a thing
  issue_title: stuff
  issue_body: other stuff
  filters:
      - version: v1alpha
        spec:
          stuff: stuff
"""

SOME_VALID_CHANGESET = """
kind: Changeset
version: v1alpha
spec:
  name: time to do a thing
  issue_title: stuff
  issue_body: other stuff
  filters:
      - kind: RegexFilter
        version: v1alpha
        spec:
          regex: '([ t]+)bo1c2:'
          paths:
            - "asd"
            - k8s.yml
  code_changes:
      - kind: RegexReplaceCodeChange
        version: v1alpha
        spec:
          replacement_details:
            - regex: '(?<=black==)(22.1.0|21.w+)'
              replace_term: "22.3.0"
              paths:
                - "requirements-test.txt"
"""

SOME_VALID_RESOURCE = """
kind: RegexReplaceCodeChange
version: v1alpha
spec:
  replacement_details:
    - regex: '(?<=black==)(22.1.0|21.w+)'
      replace_term: "22.3.0"
      paths:
        - "requirements-test.txt"
"""

DO_NOTHING_CHANGESET = """
kind: Changeset
version: v1alpha
spec:
  name: time to do a thing
  issue_title: stuff
  issue_body: other stuff
  code_changes:
      - kind: DoNothingCodeChange
        version: v1alpha
        spec:
          some_value: "concrete value"
"""


class DoNothingSpec(BaseModel):
    some_value: str


class DoNothingCodeChange(CodeChangeResource):
    kind = "DoNothingCodeChange"
    version = "v1alpha"
    spec: DoNothingSpec

    def make_code_changes(self, path: Path) -> None:
        pass

    class Config:
        extra = "forbid"


@pytest.mark.parametrize(
    "spec",
    [
        SOME_INVALID_YAML,
        SOME_INVALID_CHANGESET,
        SOME_CHANGESET_UNKNOWN_RESOURCE,
        SOME_CHANGESET_RESOURCE_WITHOUT_KIND,
    ],
)
def test_build_changeset__invalid__raises_invalid_specification_error(spec):
    with pytest.raises(InvalidSpecificationError):
        build_changeset(spec)


def test_build_changeset__valid__works():
    build_changeset(SOME_VALID_CHANGESET)


@pytest.mark.parametrize(
    ["spec", "match"],
    [
        (
            {"stuff": "stuff"},
            "Resource is not valid, must contain top-level field 'kind'",
        ),
        ({"kind": "nonexistent"}, "No active resources found of kind.*"),
        (
            {"kind": "RegexFilter"},
            "Could not parse resource spec into the corresponding model",
        ),
    ],
)
def test_build_gator_resource__invalid__raises_invalid_specification_error(spec, match):
    with pytest.raises(InvalidSpecificationError, match=match):
        build_gator_resource(spec)


def test_build_gator_resource__valid__works():
    objects = yaml.safe_load(SOME_VALID_RESOURCE)
    build_gator_resource(objects)


def test_register_custom_resource__valid__works():
    register_custom_resource(DoNothingCodeChange)
    build_changeset(DO_NOTHING_CHANGESET)


def test_register_custom_resource__doesnt_subclass_appropriate_classes__raises_error():
    with pytest.raises(
        InvalidResourceError,
        match="Resource must subclass either CodeChangeResource or FilterResource",
    ):

        class SomeClass:
            pass

        register_custom_resource(SomeClass)


def test_register_custom_resource__no_kind_field__raises_error():
    with pytest.raises(
        InvalidResourceError,
        match="Custom resource must define a class variable.*",
    ):

        class SomeClass(CodeChangeResource):
            def make_code_changes(self, repo_path: Path) -> None:
                pass

        register_custom_resource(SomeClass)
