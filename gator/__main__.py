import logging

import click

from gator.configuration import Configuration, set_configuration
from gator.resources.build import build_changeset_from_file

_logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--github-username", envvar="GATOR_GITHUB_USERNAME")
@click.option("--github-token", envvar="GATOR_GITHUB_TOKEN")
@click.option("--github-domain", envvar="GATOR_GITHUB_DOMAIN")
@click.option("--dry-run", envvar="IS_DRY_RUN", flag=True)
@click.option("--changeset-file", "changeset")
@click.option(
    "--repository-names",
    help="Comma separated list of full names, eg some-org/some-repo,some-org/some-other-repo",
)
def run(
    github_username: str,
    github_token: str,
    github_domain: str,
    repository_names: str,
    dry_run: bool,
    changeset_file: str,
):
    """The main entrypoint for running Gator."""

    _logger.info("Parsing changeset specification...")
    changeset = build_changeset_from_file(changeset_file)

    _logger.info("Initializing configuration...")

    set_configuration(
        Configuration(
            dry_run=dry_run,
            repositories=repository_names.split(","),
            changeset=changeset,
            github_domain=github_domain,
            github_token=github_token,
            github_username=github_username,
        )
    )

    click.echo("Running Gator...")

    click.echo("Done.")


if __name__ == "__main__":  # pragma: no cover
    cli()
