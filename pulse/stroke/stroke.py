import click
from .stroke_dump import dump


@click.command
@click.argument("code", type=int)
@click.argument("meta", type=str, required=False)
def stroke(code: int, meta: str = None) -> None:
    """
    Dumps the stroke.

    Args:
        code (int): Integer representation of exitcode.
        meta (str): Optional metadata.
    """
    dump(code, meta, __as_command=True)
