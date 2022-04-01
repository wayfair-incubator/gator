import logging
import re
from pathlib import Path
from typing import List, Pattern

from gator.constants import VERSION_V1_ALPHA
from gator.resources.models import BaseModelForbidExtra, CodeChangeResource
from gator.resources.util import get_recursive_path_contents

_logger = logging.getLogger(__name__)


class RegexReplacementDetails(BaseModelForbidExtra):
    regex: Pattern
    paths: List[str]
    replace_term: str


class RegexReplaceCodeChangeV1AlphaSpec(BaseModelForbidExtra):
    replacement_details: List[RegexReplacementDetails]


class RegexReplaceCodeChangeV1Alpha(CodeChangeResource):
    kind = "RegexReplaceCodeChange"
    version = VERSION_V1_ALPHA
    spec: RegexReplaceCodeChangeV1AlphaSpec

    def make_code_changes(self, repo_path: Path) -> None:
        """
        Code change logic for `RegexReplaceCodeChangeV1Alpha` resource.

        :param repo_path: The filepath where the repository content is located
        """
        for replacement_detail in self.spec.replacement_details:
            for specpath in replacement_detail.paths:
                subpath_root = repo_path / specpath
                try:
                    for subpath, content in get_recursive_path_contents(subpath_root):
                        replaced = re.sub(
                            replacement_detail.regex,
                            replacement_detail.replace_term,
                            content,
                        )
                        if replaced != content:
                            subpath.write_text(replaced)
                except FileNotFoundError:
                    _logger.warning(
                        f"Provided spec path does not exist in repo: {subpath_root}"
                    )
