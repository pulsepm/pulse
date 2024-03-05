import click


def prompt_choices(welcome: bool = False) -> int:
    """
    Prompt the user to choose an option for modifying the Pulse configuration.

    Args:
        welcome (bool): If True,\
        display a welcome message indicating that the configuration exists.
            If False, only display the menu.

    Returns:
        int: The user's choice as an integer.

    Menu Options:
        1. Modify GitHub username
        2. Modify GitHub Token
        3. Exit with saving
        4. Exit without saving

    Raises:
        click.exceptions.Abort: If the user enters an invalid choice\
        or aborts the prompt.
    """
    if welcome:
        click.echo('Configuration exists. Let\'s modify it')
        click.echo('Select which option you would like to modify.')

    click.echo('1. GitHub username')
    click.echo('2. GitHub Token')
    click.echo('3. Exit with saving')
    click.echo('4. Exit without saving')

    choice = click.prompt('Enter your choice.', type=click.IntRange(1, 4))
    return choice
