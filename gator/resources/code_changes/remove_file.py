import logging
import os
from pathlib import Path
from typing import List

from gator.constants import VERSION_V1_ALPHA
from gator.resources.models import BaseModelForbidExtra, CodeChangeResource

_logger = logging.getLogger(__name__)


class RemoveFileCodeChangeV1AlphaSpec(BaseModelForbidExtra):
    files: List[str]


class RemoveFileCodeChangeV1Alpha(CodeChangeResource):

    kind = "RemoveFileCodeChange"
    version = VERSION_V1_ALPHA
    spec: RemoveFileCodeChangeV1AlphaSpec

    def make_code_changes(self, repo_path: Path) -> None:
        """
        Code change logic for the RemoveFileCodeChangeV1Alpha resource.

        :param repo_path: The filepath where the repository content is located.
        """
        for file in self.spec.files:
            file_path = repo_path / Path(file)
            try:
                file_path.unlink()
            except FileNotFoundError:
                _logger.info(f"Skipping {file_path} because file does not exist")
                continue
            self._remove_parent_directory_if_empty(file_path)

    @staticmethod
    def _remove_parent_directory_if_empty(file_path: Path) -> None:
        head, _ = os.path.split(file_path)
        head_path = Path(head)
        if not list(head_path.iterdir()):
            head_path.rmdir()
