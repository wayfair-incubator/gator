from typing import List

from pydantic import BaseModel

from gator.exceptions import ConfigurationError
from gator.resources import Changeset

CONFIGURATION = None


class Configuration(BaseModel):
    class Config:
        extra = "forbid"

    dry_run: bool
    repositories: List[str]
    changeset: Changeset
    github_domain: str
    clone_directory: str = "cloned_repos"
    github_token: str
    github_username: str


def get_configuration() -> Configuration:
    """Get the configuration for the current run."""
    if CONFIGURATION is None:
        raise ConfigurationError("Configuration has not been loaded.")
    return CONFIGURATION


def set_configuration(configuration: Configuration) -> None:
    """Set the runtime configuration."""
    global CONFIGURATION

    CONFIGURATION = configuration
