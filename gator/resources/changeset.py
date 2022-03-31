"""
Define Gator Changeset structure.

Changeset specifications contain everything Gator needs to know in order to make
code changes to a given repository, and create update or close existing github
PRs or Issues.

Broadly:

* Filters, if present, will be run before CodeChanges
* If all Filters pass, and there are no CodeChanges, an Issue will be created
* If there are CodeChanges, and the CodeChanges modify file content, a PR will
  be created
* If repository content is not modified, but the repository passes Filters, no
  PR or Issue will be created
"""

from typing import List, Optional

from gator.resources.models import (
    CodeChangeResource,
    FilterResource,
    GatorResource,
    GatorResourceMetaclass,
    GatorResourceSpec,
)


class ChangesetSpecV1AlphaSpec(GatorResourceSpec):
    issue_title: Optional[str]
    issue_body: Optional[str]
    pull_request_branch: Optional[str]
    filters: Optional[List[FilterResource]]
    code_changes: Optional[List[CodeChangeResource]]


class Changeset(GatorResource, metaclass=GatorResourceMetaclass):
    kind = "Changeset"
    version = "v1alpha"
    spec: ChangesetSpecV1AlphaSpec


def build_changeset(spec: str) -> Changeset:
    """
    Given a string containing raw yaml, build a Changeset object.

    :param spec: A raw yaml string containing the changeset definition
    :raises InvalidSpecificationError: If anything went wrong.
    :return Changeset: The fully constructed pydantic model representing a
    changeset
    """
    pass
