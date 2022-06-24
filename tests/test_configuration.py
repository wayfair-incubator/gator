import pytest

import tests.sample_data as sd
from gator.configuration import Configuration, get_configuration, set_configuration
from gator.exceptions import ConfigurationError


def test_get_configuration__configuration_not_set__raises_not_set_error():
    set_configuration(None)
    with pytest.raises(ConfigurationError):
        get_configuration()


def test_get_and_set_configuration__no_errors__configuration_saved_and_returned():
    some_configuration = Configuration(**sd.SOME_CONFIGURATION_VALUES)
    set_configuration(some_configuration)
    assert get_configuration() == some_configuration
