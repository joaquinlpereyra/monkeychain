import click

from . import __version__

@click.command()
@click.version_option(version=__version__)
def main():
    """Start up a new monkeychain node."""
    click.echo("Starting up...")
