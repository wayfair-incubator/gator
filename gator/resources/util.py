import logging
from pathlib import Path
from typing import Iterator, List, Tuple

from gator.constants import GIT_INTERNALS_DIRECTORY

_logger = logging.getLogger(__name__)


def get_recursive_path_contents(target_path: Path) -> Iterator[Tuple[Path, str]]:
    """
    Generate file content for all files recursively present in provided target_path.

    Note: ignores contents of the `.git` directory
    :param target_path: Path to recursively scan for content.
    :return: Generate (Path, str) tuples containing path and content at path.
    """

    file_paths: List[Path] = []

    if target_path.is_dir():
        # build list of file paths that recursively reside in the provided `target_dir`
        for matched_path in target_path.glob("**/*"):
            if not matched_path.is_dir():
                file_paths.append(matched_path)
    else:
        file_paths.append(target_path)

    for path in file_paths:
        if GIT_INTERNALS_DIRECTORY in str(path).split("/"):
            continue
        try:
            content = path.read_text()
            yield path, content
        except UnicodeDecodeError as e:
            _logger.warning(f"We could not decode text at path {path}: {e}")
