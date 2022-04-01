import logging
import re
from pathlib import Path
from typing import List

from gator.constants import DEFAULT_REGEX_MODES
from gator.resources.models import BaseModelForbidExtra, FilterResource
from gator.resources.util import get_recursive_path_contents

_logger = logging.getLogger(__name__)


class RegexFilterV1AlphaSpec(BaseModelForbidExtra):
    regex: str
    paths: List[str]


class RegexFilterV1Alpha(FilterResource):

    kind = "RegexFilter"
    version = "v1alpha"
    spec: RegexFilterV1AlphaSpec

    def matches(self, path: Path) -> bool:
        """
        Determine if a match is present for this filter.

        Returns True if the specified regex is present in any of the generated content.
        This content is recursively generated from the specified paths.

        :param path: The Github repository to perform the match against.
        :return: Whether or not the match was present
        """

        expression = re.compile(self.spec.regex, flags=DEFAULT_REGEX_MODES)
        for search_path in [path / spec_path for spec_path in self.spec.paths]:
            try:
                for _, content in get_recursive_path_contents(search_path):
                    # short circuit if there is a single match
                    if expression.search(content):
                        return True
            except FileNotFoundError:
                _logger.debug(f"Provided spec path {search_path} does not exist")

        return False
