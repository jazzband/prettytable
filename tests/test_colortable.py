import pytest

from prettytable import PrettyTable
from prettytable.colortable import RESET_CODE, ColorTable, Theme


@pytest.fixture
def row_prettytable():
    # Row by row...
    row = PrettyTable()
    row.field_names = ["City name", "Area", "Population", "Annual Rainfall"]
    row.add_row(["Adelaide", 1295, 1158259, 600.5])
    row.add_row(["Brisbane", 5905, 1857594, 1146.4])
    row.add_row(["Darwin", 112, 120900, 1714.7])
    row.add_row(["Hobart", 1357, 205556, 619.5])
    row.add_row(["Sydney", 2058, 4336374, 1214.8])
    row.add_row(["Melbourne", 1566, 3806092, 646.9])
    row.add_row(["Perth", 5386, 1554769, 869.4])
    return row


@pytest.fixture
def row_colortable():
    row = ColorTable()
    row.field_names = ["City name", "Area", "Population", "Annual Rainfall"]
    row.add_row(["Adelaide", 1295, 1158259, 600.5])
    row.add_row(["Brisbane", 5905, 1857594, 1146.4])
    row.add_row(["Darwin", 112, 120900, 1714.7])
    row.add_row(["Hobart", 1357, 205556, 619.5])
    row.add_row(["Sydney", 2058, 4336374, 1214.8])
    row.add_row(["Melbourne", 1566, 3806092, 646.9])
    row.add_row(["Perth", 5386, 1554769, 869.4])
    return row


@pytest.fixture
def color_theme():
    return Theme(
        default_color="31",
        vertical_color="32",
        horizontal_color="33",
        junction_color="34",
    )


class TestColorTable:
    def test_themeless(self, row_prettytable, row_colortable):
        # Not worth the logic customizing the reset code
        # For now we'll just get rid of it
        assert (
            row_colortable.get_string().replace(RESET_CODE, "")
            == row_prettytable.get_string()
        )

    def test_theme_setter(self, color_theme):
        table1 = ColorTable(theme=color_theme)

        table2 = ColorTable()
        table2.theme = color_theme

        assert table1.theme == table2.theme

        dict1 = table1.__dict__
        dict2 = table2.__dict__

        # So we don't compare functions
        del dict1["_sort_key"]
        del dict2["_sort_key"]

        assert dict1 == dict2


class TestFormatCode:
    def test_basic(self):
        assert Theme.format_code("31") == "\x1b[31m"

    def test_prefix(self):
        assert Theme.format_code("\x1b[35m") == "\x1b[35m"

    def test_escapes(self):
        assert Theme.format_code("\033[41m") == "\x1b[41m"
        assert Theme.format_code("\u001b[41m") == "\x1b[41m"

    def test_empty(self):
        assert Theme.format_code("") == ""

    def test_stripped(self):
        assert Theme.format_code("\t\t     \t") == ""

    def test_multiple(self):
        assert Theme.format_code("30;42") == "\x1b[30;42m"
        assert Theme.format_code("\x1b[30;42m") == "\x1b[30;42m"
