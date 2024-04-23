import click
from .stroke_dump import dump

@click.command
@click.argument('code', type=int)
def stroke(code: int) -> None:
    # check for code
    dump(int(code))