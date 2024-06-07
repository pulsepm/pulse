import click
from .stroke_dump import dump

@click.command
@click.argument('code', type=int)
@click.argument('meta', type=str, required=False)
def stroke(code: int, meta: str = None) -> None:
    # check for code
    dump(code, meta, __as_command=True)