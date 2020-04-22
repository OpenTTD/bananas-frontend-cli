import sys

from click import ClickException

from . import commands  # noqa
from .cli import (
    cli,
    cli_exit,
)
from .exceptions import Exit


if __name__ == "__main__":
    try:
        cli(auto_envvar_prefix="BANANAS_CLI", standalone_mode=False)
    except Exit:
        sys.exit(1)
    except ClickException as e:
        e.show()
        sys.exit(2)
    finally:
        cli_exit()
