import click

from gator.pre_process import preprocess_repository


@click.group()
def cli():
    pass


@cli.command()
@click.option("--github-username", envvar="GATOR_GITHUB_USERNAME")
@click.option("--github-token", envvar="GATOR_GITHUB_TOKEN")
@click.option("--github-domain", envvar="GATOR_GITHUB_DOMAIN")
@click.option("--repository")
def run(
    github_username: str,
    github_token: str,
    github_domain: str,
    repository: str,
):
    click.echo(f"Running Gator on {repository}...")

    preprocess_repository(
        github_username,
        github_token,
        repository.split("/")[0],
        repository.split("/")[1],
        github_domain,
    )

    click.echo("Done.")


if __name__ == "__main__":  # pragma: no cover
    cli()
