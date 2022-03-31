from collections import Counter

import pytest

from gator.resources.util import get_recursive_path_contents

SOME_TEXT_1 = "some-text-1"
SOME_TEXT_2 = "some-text-2"
SOME_TEXT_3 = "some-text-3"

SOME_FILENAME_1 = "some-filename-1"
SOME_FILENAME_2 = "some-filename-2"
SOME_FILENAME_3 = "some-filename-3"

SOME_NON_UTF_8_BYTES = "foo".encode("utf-16")


def test_get_recursive_path_contents__empty_directory__no_file_contents_returned(
    tmp_path,
):

    contents = [content for some_path, content in get_recursive_path_contents(tmp_path)]
    assert not contents


def test_get_recursive_path_contents__provided_path_dne__raises_file_not_found_error(
    tmp_path,
):

    some_path_dne = tmp_path / "some-dir-dne"

    with pytest.raises(FileNotFoundError):
        list(get_recursive_path_contents(some_path_dne))


def test_get_recursive_path_contents__one_file_present__single_item_content_returned(
    tmp_path,
):

    some_path = tmp_path / SOME_FILENAME_1
    some_path.write_text(SOME_TEXT_1)

    contents = [
        (content_path, content)
        for content_path, content in get_recursive_path_contents(tmp_path)
    ]
    assert contents == [(some_path, SOME_TEXT_1)]


def test_get_recursive_path_contents__multiple_files_present__multiple_item_content_returned(
    tmp_path,
):

    some_path_1 = tmp_path / SOME_FILENAME_1
    some_path_2 = tmp_path / SOME_FILENAME_2

    some_path_1.write_text(SOME_TEXT_1)
    some_path_2.write_text(SOME_TEXT_2)

    contents = [
        (content_path, content)
        for content_path, content in get_recursive_path_contents(tmp_path)
    ]

    expected_content = [(some_path_1, SOME_TEXT_1), (some_path_2, SOME_TEXT_2)]
    assert all(content in contents for content in expected_content)


def test_get_recursive_path_contents__multiple_files_present_one_decode_error__single_item_content_returned(
    tmp_path,
):

    some_path_1 = tmp_path / SOME_FILENAME_1
    some_path_2 = tmp_path / SOME_FILENAME_2

    some_path_1.write_text(SOME_TEXT_1)
    some_path_2.write_bytes(SOME_NON_UTF_8_BYTES)

    expected_content = [(some_path_1, SOME_TEXT_1)]

    assert [
        (content_path, content)
        for content_path, content in get_recursive_path_contents(tmp_path)
    ] == expected_content


def test_get_recursive_path_contents__content_present_in_nested_directory__content_returned(
    tmp_path,
):

    dir_name = "some-dir"
    (tmp_path / dir_name).mkdir()
    some_path = tmp_path / dir_name / SOME_FILENAME_1
    some_path.write_text(SOME_TEXT_1)

    contents = [
        (content_path, content)
        for content_path, content in get_recursive_path_contents(tmp_path)
    ]
    assert contents == [(some_path, SOME_TEXT_1)]


def test_get_recursive_path_contents__git_directory_present__git_directory_ignored(
    tmp_path,
):

    dir_name = ".git"
    (tmp_path / dir_name).mkdir()
    some_path = tmp_path / dir_name / SOME_FILENAME_1
    some_path.write_text(SOME_TEXT_1)

    assert list(get_recursive_path_contents(tmp_path)) == []


def test_get_recursive_path_contents__content_present_in_root_and_nested_directories__content_returned(
    tmp_path,
):

    dir_name_1 = "some-dir-1"
    dir_name_2 = "some_dir-2"

    (tmp_path / dir_name_1).mkdir()
    some_path_1 = tmp_path / dir_name_1 / SOME_FILENAME_1
    some_path_1.write_text(SOME_TEXT_1)

    (tmp_path / dir_name_2).mkdir()
    some_path_2 = tmp_path / dir_name_2 / SOME_FILENAME_2
    some_path_2.write_text(SOME_TEXT_2)

    some_path_3 = tmp_path / SOME_FILENAME_3
    some_path_3.write_text(SOME_TEXT_3)

    contents = [
        (content_path, content)
        for content_path, content in get_recursive_path_contents(tmp_path)
    ]

    assert Counter(contents) == Counter(
        [
            (some_path_1, SOME_TEXT_1),
            (some_path_2, SOME_TEXT_2),
            (some_path_3, SOME_TEXT_3),
        ]
    )
