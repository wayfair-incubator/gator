import filecmp
import shutil
from pathlib import Path

import pytest
import yaml

from gator.resources.build import build_gator_resource

CODE_CHANGE_TEST_DATA_DIR = Path("tests/resources/code_changes/code_change_test_data")
scenario_dirs = [
    scenario_dir
    for scenario_dir in CODE_CHANGE_TEST_DATA_DIR.iterdir()
    if scenario_dir.is_dir()
]


@pytest.mark.parametrize("scenario_dir", scenario_dirs)
def test_code_change_resources__modify_initial_dir__expected_changes_produced(
    tmp_path, scenario_dir
):
    """
    Dynamic testing setup for code changes.

    Please see tests/resources/test_code_change/README.md for more information regarding this setup.
    """

    INITIAL_DIRECTORY_NAME = "initial"
    EXPECTED_DIRECTORY_NAME = "expected"
    CODE_CHANGE_FILENAME = "code_change.yaml"

    initial_path_workdir = tmp_path / INITIAL_DIRECTORY_NAME

    # copy `initial` dir into `tmp_path` so that we can safely modify it
    shutil.copytree(scenario_dir / INITIAL_DIRECTORY_NAME, initial_path_workdir)

    raw_code_changes = yaml.safe_load((scenario_dir / CODE_CHANGE_FILENAME).read_text())

    # contents of `CODE_CHANGE_FILENAME` must be in a list form
    assert isinstance(raw_code_changes, list)
    code_changes = [
        build_gator_resource(raw_code_change) for raw_code_change in raw_code_changes
    ]

    # apply code changes
    for code_change in code_changes:
        code_change.make_code_changes(initial_path_workdir)

    try:
        _assert_dirs_identical(
            Path(initial_path_workdir), scenario_dir / EXPECTED_DIRECTORY_NAME
        )
    except AssertionError as e:
        raise AssertionError(
            f"The code_change defined in {scenario_dir / CODE_CHANGE_FILENAME} did not produce the expected results for scenario {scenario_dir}: {e}"
        )


def _assert_dirs_identical(dir1: Path, dir2: Path):
    """
    Given two directories, recursively assert that they are identical.

    The two directories must have the same files and directories, and the file content must be identical.
    """

    file_compare = filecmp.dircmp(dir1, dir2)
    if file_compare.left_list != file_compare.right_list:
        raise AssertionError(
            f"The set of files and directories in the left list {file_compare.left_list} is not identical to the set of files in the right list {file_compare.right_list}"
        )

    diff = file_compare.diff_files
    if diff:
        raise AssertionError(
            f"There are files whose content differ between the two directories: {diff}"
        )

    for common_dir in file_compare.common_dirs:
        _assert_dirs_identical(dir1 / common_dir, dir2 / common_dir)
