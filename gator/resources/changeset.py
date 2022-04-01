from typing import List, Optional, Union

from gator.resources.code_changes.new_file import NewFileCodeChangeV1Alpha
from gator.resources.code_changes.regex_replace import RegexReplaceCodeChangeV1Alpha
from gator.resources.code_changes.remove_file import RemoveFileCodeChangeV1Alpha
from gator.resources.filters.regex_filter import RegexFilterV1Alpha
from gator.resources.models import GatorResource, GatorResourceSpec


class ChangesetSpecV1AlphaSpec(GatorResourceSpec):
    issue_title: Optional[str]
    issue_body: Optional[str]
    pull_request_branch: Optional[str]
    filters: Optional[List[RegexFilterV1Alpha]]
    code_changes: Optional[
        List[
            Union[
                RegexReplaceCodeChangeV1Alpha,
                NewFileCodeChangeV1Alpha,
                RemoveFileCodeChangeV1Alpha,
            ]
        ]
    ]


class Changeset(GatorResource):
    kind = "Changeset"
    version = "v1alpha"
    spec: ChangesetSpecV1AlphaSpec
    stuff: str
