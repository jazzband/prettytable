import pkg_resources

from .prettytable import (
    ALL,
    DEFAULT,
    FRAME,
    HEADER,
    MARKDOWN,
    MSWORD_FRIENDLY,
    NONE,
    ORGMODE,
    PLAIN_COLUMNS,
    RANDOM,
    PrettyTable,
    TableHandler,
    from_csv,
    from_db_cursor,
    from_html,
    from_html_one,
    from_json,
)

__all__ = [
    "ALL",
    "DEFAULT",
    "FRAME",
    "HEADER",
    "MARKDOWN",
    "MSWORD_FRIENDLY",
    "NONE",
    "ORGMODE",
    "PLAIN_COLUMNS",
    "RANDOM",
    "PrettyTable",
    "TableHandler",
    "from_csv",
    "from_db_cursor",
    "from_html",
    "from_html_one",
    "from_json",
]

__version__ = pkg_resources.get_distribution(__name__).version
