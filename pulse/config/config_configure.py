import click
import pulse.config.config as config


@click.command
def configure() -> None:
    """
    Configure Pulse.

    Prompts the user to configure Pulse\
    by modifying GitHub credentials.
    If a configuration file exists,\
    it offers options to modify the existing configuration.
    If no configuration file exists, it prompts the user to create a new one.

    Welcome message is displayed at the beginning.

    Returns:
        None
    """
    click.echo(
        "\tWelcome to Pulse configuration manager!"
        "This is only used for github credentials e.g to publish a repository."
    )
    if config.exists():
        config.modify(load_data=True)

    else:
        config.create()
