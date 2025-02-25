from .user._user import User
import click
import logging


@click.command
@click.option(
    "--delete",
    "-d",
    required=False,
    is_flag=True,
    help="Deletes the configuration file.",
)
@click.option(
    "--modify",
    "-m",
    required=False,
    is_flag=True,
    help="Modifies the configuration file.",
)
def user(delete, modify):
    usr = User()
    match (delete, modify):
        case (False, False):
            logging.info(
                "Your user configuration exists already. Please use respective flags."
            )

        case (True, True):
            logging.error("Can't use both flags.")
            return

        case (False, True):
            usr.modify_prompt()

        case (True, False):
            usr.mark_for_delete = True
            del usr
