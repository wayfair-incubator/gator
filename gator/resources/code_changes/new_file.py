import logging
import os
from pathlib import Path
from typing import List

from gator.constants import VERSION_V1_ALPHA
from gator.resources.models import BaseModelForbidExtra, CodeChangeResource

_logger = logging.getLogger(__name__)


class FileDetails(BaseModelForbidExtra):
    file_path: str
    file_content: str


class NewFileCodeChangeV1AlphaSpec(BaseModelForbidExtra):
    files: List[FileDetails]


class NewFileCodeChangeV1Alpha(CodeChangeResource):

    kind = "NewFileCodeChange"
    version = VERSION_V1_ALPHA
    spec: NewFileCodeChangeV1AlphaSpec

    def make_code_changes(self, repo_path: Path) -> None:
        """
        Code change logic for the NewFileCodeChangeV1Alpha resource.

        :param repo_path: The filepath where the repository content is located.
        """
        for file_details in self.spec.files:
            head, tail = os.path.split(file_details.file_path)
            file_location = repo_path / Path(head)
            file_location.mkdir(parents=True, exist_ok=True)
            full_path = file_location / tail
            if full_path.exists():
                _logger.info(f"Skipping {full_path} because file already exists")
            else:
                full_path.write_text(file_details.file_content)
