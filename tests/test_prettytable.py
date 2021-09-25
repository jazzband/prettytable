#!/usr/bin/env python

import io
import random
import sqlite3
import unittest
from math import e, pi, sqrt

import pytest

from prettytable import (
    ALL,
    DEFAULT,
    DOUBLE_BORDER,
    MARKDOWN,
    MSWORD_FRIENDLY,
    NONE,
    ORGMODE,
    PLAIN_COLUMNS,
    RANDOM,
    PrettyTable,
    from_csv,
    from_db_cursor,
    from_html,
    from_html_one,
    from_json,
)
from prettytable.prettytable import FRAME


def helper_table(rows=3):
    t = PrettyTable(["Field 1", "Field 2", "Field 3"])
    v = 1
    for row in range(rows):
        # Some have spaces, some not, to help test padding columns of different widths
        t.add_row([f"value {v}", f"value{v+1}", f"value{v+2}"])
        v += 3
    return t


class BuildEquivalenceTest(unittest.TestCase):
    """Make sure that building a table row-by-row and column-by-column yield the same
    results"""

    def setUp(self):

        # Row by row...
        self.row = PrettyTable()
        self.row.field_names = ["City name", "Area", "Population", "Annual Rainfall"]
        self.row.add_row(["Adelaide", 1295, 1158259, 600.5])
        self.row.add_row(["Brisbane", 5905, 1857594, 1146.4])
        self.row.add_row(["Darwin", 112, 120900, 1714.7])
        self.row.add_row(["Hobart", 1357, 205556, 619.5])
        self.row.add_row(["Sydney", 2058, 4336374, 1214.8])
        self.row.add_row(["Melbourne", 1566, 3806092, 646.9])
        self.row.add_row(["Perth", 5386, 1554769, 869.4])

        # Column by column...
        self.col = PrettyTable()
        self.col.add_column(
            "City name",
            [
                "Adelaide",
                "Brisbane",
                "Darwin",
                "Hobart",
                "Sydney",
                "Melbourne",
                "Perth",
            ],
        )
        self.col.add_column("Area", [1295, 5905, 112, 1357, 2058, 1566, 5386])
        self.col.add_column(
            "Population", [1158259, 1857594, 120900, 205556, 4336374, 3806092, 1554769]
        )
        self.col.add_column(
            "Annual Rainfall", [600.5, 1146.4, 1714.7, 619.5, 1214.8, 646.9, 869.4]
        )

        # A mix of both!
        self.mix = PrettyTable()
        self.mix.field_names = ["City name", "Area"]
        self.mix.add_row(["Adelaide", 1295])
        self.mix.add_row(["Brisbane", 5905])
        self.mix.add_row(["Darwin", 112])
        self.mix.add_row(["Hobart", 1357])
        self.mix.add_row(["Sydney", 2058])
        self.mix.add_row(["Melbourne", 1566])
        self.mix.add_row(["Perth", 5386])
        self.mix.add_column(
            "Population", [1158259, 1857594, 120900, 205556, 4336374, 3806092, 1554769]
        )
        self.mix.add_column(
            "Annual Rainfall", [600.5, 1146.4, 1714.7, 619.5, 1214.8, 646.9, 869.4]
        )

    def testRowColEquivalenceASCII(self):

        assert self.row.get_string() == self.col.get_string()

    def testRowMixEquivalenceASCII(self):

        assert self.row.get_string() == self.mix.get_string()

    def testRowColEquivalenceHTML(self):

        assert self.row.get_html_string() == self.col.get_html_string()

    def testRowMixEquivalenceHTML(self):

        assert self.row.get_html_string() == self.mix.get_html_string()


class DeleteColumnTest(unittest.TestCase):
    def testDeleteColumn(self):
        with_del = PrettyTable()
        with_del.add_column("City name", ["Adelaide", "Brisbane", "Darwin"])
        with_del.add_column("Area", [1295, 5905, 112])
        with_del.add_column("Population", [1158259, 1857594, 120900])
        with_del.del_column("Area")

        without_row = PrettyTable()
        without_row.add_column("City name", ["Adelaide", "Brisbane", "Darwin"])
        without_row.add_column("Population", [1158259, 1857594, 120900])

        assert with_del.get_string() == without_row.get_string()

    def testDeleteIllegalColumnRaisesException(self):
        table = PrettyTable()
        table.add_column("City name", ["Adelaide", "Brisbane", "Darwin"])

        with pytest.raises(Exception):
            table.del_column("City not-a-name")


class FieldnamelessTableTest(unittest.TestCase):

    """Make sure that building and stringing a table with no fieldnames works fine"""

    def setUp(self):
        self.x = PrettyTable()
        self.x.add_row(["Adelaide", 1295, 1158259, 600.5])
        self.x.add_row(["Brisbane", 5905, 1857594, 1146.4])
        self.x.add_row(["Darwin", 112, 120900, 1714.7])
        self.x.add_row(["Hobart", 1357, 205556, 619.5])
        self.x.add_row(["Sydney", 2058, 4336374, 1214.8])
        self.x.add_row(["Melbourne", 1566, 3806092, 646.9])
        self.x.add_row(["Perth", 5386, 1554769, 869.4])

    def testCanStringASCII(self):
        output = self.x.get_string()
        assert "|  Field 1  | Field 2 | Field 3 | Field 4 |" in output
        assert "|  Adelaide |   1295  | 1158259 |  600.5  |" in output

    def testCanStringHTML(self):
        output = self.x.get_html_string()
        assert "<th>Field 1</th>" in output
        assert "<td>Adelaide</td>" in output

    def testAddFieldNamesLater(self):
        self.x.field_names = ["City name", "Area", "Population", "Annual Rainfall"]
        assert "City name | Area | Population | Annual Rainfall" in self.x.get_string()


class CityDataTest(unittest.TestCase):

    """Just build the Australian capital city data example table."""

    def setUp(self):

        self.x = PrettyTable(["City name", "Area", "Population", "Annual Rainfall"])
        self.x.add_row(["Adelaide", 1295, 1158259, 600.5])
        self.x.add_row(["Brisbane", 5905, 1857594, 1146.4])
        self.x.add_row(["Darwin", 112, 120900, 1714.7])
        self.x.add_row(["Hobart", 1357, 205556, 619.5])
        self.x.add_row(["Sydney", 2058, 4336374, 1214.8])
        self.x.add_row(["Melbourne", 1566, 3806092, 646.9])
        self.x.add_row(["Perth", 5386, 1554769, 869.4])


class OptionOverrideTests(CityDataTest):

    """Make sure all options are properly overwritten by get_string."""

    def testBorder(self):
        default = self.x.get_string()
        override = self.x.get_string(border=False)
        assert default != override

    def testHeader(self):
        default = self.x.get_string()
        override = self.x.get_string(header=False)
        assert default != override

    def testHrulesAll(self):
        default = self.x.get_string()
        override = self.x.get_string(hrules=ALL)
        assert default != override

    def testHrulesNone(self):

        default = self.x.get_string()
        override = self.x.get_string(hrules=NONE)
        assert default != override


class OptionAttributeTests(CityDataTest):

    """Make sure all options which have an attribute interface work as they should.
    Also make sure option settings are copied correctly when a table is cloned by
    slicing."""

    def testSetForAllColumns(self):
        self.x.field_names = sorted(self.x.field_names)
        self.x.align = "l"
        self.x.max_width = 10
        self.x.start = 2
        self.x.end = 4
        self.x.sortby = "Area"
        self.x.reversesort = True
        self.x.header = True
        self.x.border = False
        self.x.hrules = True
        self.x.int_format = "4"
        self.x.float_format = "2.2"
        self.x.padding_width = 2
        self.x.left_padding_width = 2
        self.x.right_padding_width = 2
        self.x.vertical_char = "!"
        self.x.horizontal_char = "~"
        self.x.junction_char = "*"
        self.x.top_junction_char = "@"
        self.x.bottom_junction_char = "#"
        self.x.right_junction_char = "$"
        self.x.left_junction_char = "%"
        self.x.top_right_junction_char = "^"
        self.x.top_left_junction_char = "&"
        self.x.bottom_right_junction_char = "("
        self.x.bottom_left_junction_char = ")"
        self.x.format = True
        self.x.attributes = {"class": "prettytable"}
        assert self.x.get_string() == self.x[:].get_string()

    def testSetForOneColumn(self):
        self.x.align["Rainfall"] = "l"
        self.x.max_width["Name"] = 10
        self.x.int_format["Population"] = "4"
        self.x.float_format["Area"] = "2.2"
        assert self.x.get_string() == self.x[:].get_string()


class BasicTests(CityDataTest):

    """Some very basic tests."""

    def testNoBlankLines(self):

        """No table should ever have blank lines in it."""

        string = self.x.get_string()
        lines = string.split("\n")
        assert "" not in lines

    def testAllLengthsEqual(self):

        """All lines in a table should be of the same length."""

        string = self.x.get_string()
        lines = string.split("\n")
        lengths = [len(line) for line in lines]
        lengths = set(lengths)
        assert len(lengths) == 1


class TitleBasicTests(BasicTests):

    """Run the basic tests with a title"""

    def setUp(self):
        BasicTests.setUp(self)
        self.x.title = "My table"


class NoBorderBasicTests(BasicTests):

    """Run the basic tests with border = False"""

    def setUp(self):
        BasicTests.setUp(self)
        self.x.border = False


class NoHeaderBasicTests(BasicTests):

    """Run the basic tests with header = False"""

    def setUp(self):
        BasicTests.setUp(self)
        self.x.header = False


class HrulesNoneBasicTests(BasicTests):

    """Run the basic tests with hrules = NONE"""

    def setUp(self):
        BasicTests.setUp(self)
        self.x.hrules = NONE


class HrulesAllBasicTests(BasicTests):

    """Run the basic tests with hrules = ALL"""

    def setUp(self):
        BasicTests.setUp(self)
        self.x.hrules = ALL


class EmptyTableTests(CityDataTest):

    """Make sure the print_empty option works"""

    def setUp(self):
        CityDataTest.setUp(self)
        self.y = PrettyTable()
        self.y.field_names = ["City name", "Area", "Population", "Annual Rainfall"]

    def testPrintEmptyTrue(self):
        assert self.y.get_string(print_empty=True) != ""
        assert self.x.get_string(print_empty=True) != self.y.get_string(
            print_empty=True
        )

    def testPrintEmptyFalse(self):
        assert self.y.get_string(print_empty=False) == ""
        assert self.y.get_string(print_empty=False) != self.x.get_string(
            print_empty=False
        )

    def testInteractionWithBorder(self):
        assert self.y.get_string(border=False, print_empty=True) == ""


class PresetBasicTests(BasicTests):

    """Run the basic tests after using set_style"""

    def setUp(self):
        BasicTests.setUp(self)
        self.x.set_style(MSWORD_FRIENDLY)


class SlicingTests(CityDataTest):
    def setUp(self):
        CityDataTest.setUp(self)

    def testSliceAll(self):
        y = self.x[:]
        assert self.x.get_string() == y.get_string()

    def testSliceFirstTwoRows(self):
        y = self.x[0:2]
        string = y.get_string()
        assert len(string.split("\n")) == 6
        assert "Adelaide" in string
        assert "Brisbane" in string
        assert "Melbourne" not in string
        assert "Perth" not in string

    def testSliceLastTwoRows(self):
        y = self.x[-2:]
        string = y.get_string()
        assert len(string.split("\n")) == 6
        assert "Adelaide" not in string
        assert "Brisbane" not in string
        assert "Melbourne" in string
        assert "Perth" in string


class SortingTests(CityDataTest):
    def setUp(self):
        CityDataTest.setUp(self)

    def testSortBy(self):
        self.x.sortby = self.x.field_names[0]
        old = self.x.get_string()
        for field in self.x.field_names[1:]:
            self.x.sortby = field
            new = self.x.get_string()
            assert new != old

    def testReverseSort(self):
        for field in self.x.field_names:
            self.x.sortby = field
            self.x.reversesort = False
            forward = self.x.get_string()
            self.x.reversesort = True
            backward = self.x.get_string()
            forward_lines = forward.split("\n")[2:]  # Discard header lines
            backward_lines = backward.split("\n")[2:]
            backward_lines.reverse()
            assert forward_lines == backward_lines

    def testSortKey(self):
        # Test sorting by length of city name
        def key(vals):
            vals[0] = len(vals[0])
            return vals

        self.x.sortby = "City name"
        self.x.sort_key = key
        assert (
            self.x.get_string().strip()
            == """
+-----------+------+------------+-----------------+
| City name | Area | Population | Annual Rainfall |
+-----------+------+------------+-----------------+
|   Perth   | 5386 |  1554769   |      869.4      |
|   Darwin  | 112  |   120900   |      1714.7     |
|   Hobart  | 1357 |   205556   |      619.5      |
|   Sydney  | 2058 |  4336374   |      1214.8     |
|  Adelaide | 1295 |  1158259   |      600.5      |
|  Brisbane | 5905 |  1857594   |      1146.4     |
| Melbourne | 1566 |  3806092   |      646.9      |
+-----------+------+------------+-----------------+
""".strip()
        )

    def testSortSlice(self):
        """Make sure sorting and slicing interact in the expected way"""
        x = PrettyTable(["Foo"])
        for i in range(20, 0, -1):
            x.add_row([i])
        newstyle = x.get_string(sortby="Foo", end=10)
        assert "10" in newstyle
        assert "20" not in newstyle
        oldstyle = x.get_string(sortby="Foo", end=10, oldsortslice=True)
        assert "10" not in oldstyle
        assert "20" in oldstyle


class IntegerFormatBasicTests(BasicTests):

    """Run the basic tests after setting an integer format string"""

    def setUp(self):
        BasicTests.setUp(self)
        self.x.int_format = "04"


class FloatFormatBasicTests(BasicTests):

    """Run the basic tests after setting a float format string"""

    def setUp(self):
        BasicTests.setUp(self)
        self.x.float_format = "6.2f"


class FloatFormatTests(unittest.TestCase):
    def setUp(self):
        self.x = PrettyTable(["Constant", "Value"])
        self.x.add_row(["Pi", pi])
        self.x.add_row(["e", e])
        self.x.add_row(["sqrt(2)", sqrt(2)])

    def testNoDecimals(self):
        self.x.float_format = ".0f"
        self.x.caching = False
        assert "." not in self.x.get_string()

    def testRoundTo5DP(self):
        self.x.float_format = ".5f"
        string = self.x.get_string()
        assert "3.14159" in string
        assert "3.141592" not in string
        assert "2.71828" in string
        assert "2.718281" not in string
        assert "2.718282" not in string
        assert "1.41421" in string
        assert "1.414213" not in string

    def testPadWith2Zeroes(self):
        self.x.float_format = "06.2f"
        string = self.x.get_string()
        assert "003.14" in string
        assert "002.72" in string
        assert "001.41" in string


class BreakLineTests(unittest.TestCase):
    def testAsciiBreakLine(self):
        t = PrettyTable(["Field 1", "Field 2"])
        t.add_row(["value 1", "value2\nsecond line"])
        t.add_row(["value 3", "value4"])
        result = t.get_string(hrules=ALL)
        assert (
            result.strip()
            == """
+---------+-------------+
| Field 1 |   Field 2   |
+---------+-------------+
| value 1 |    value2   |
|         | second line |
+---------+-------------+
| value 3 |    value4   |
+---------+-------------+
""".strip()
        )

        t = PrettyTable(["Field 1", "Field 2"])
        t.add_row(["value 1", "value2\nsecond line"])
        t.add_row(["value 3\n\nother line", "value4\n\n\nvalue5"])
        result = t.get_string(hrules=ALL)
        assert (
            result.strip()
            == """
+------------+-------------+
|  Field 1   |   Field 2   |
+------------+-------------+
|  value 1   |    value2   |
|            | second line |
+------------+-------------+
|  value 3   |    value4   |
|            |             |
| other line |             |
|            |    value5   |
+------------+-------------+
""".strip()
        )

        t = PrettyTable(["Field 1", "Field 2"])
        t.add_row(["value 1", "value2\nsecond line"])
        t.add_row(["value 3\n\nother line", "value4\n\n\nvalue5"])
        result = t.get_string()
        assert (
            result.strip()
            == """
+------------+-------------+
|  Field 1   |   Field 2   |
+------------+-------------+
|  value 1   |    value2   |
|            | second line |
|  value 3   |    value4   |
|            |             |
| other line |             |
|            |    value5   |
+------------+-------------+
""".strip()
        )

    def testHtmlBreakLine(self):
        t = PrettyTable(["Field 1", "Field 2"])
        t.add_row(["value 1", "value2\nsecond line"])
        t.add_row(["value 3", "value4"])
        result = t.get_html_string(hrules=ALL)
        assert (
            result.strip()
            == """
<table>
    <thead>
        <tr>
            <th>Field 1</th>
            <th>Field 2</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>value 1</td>
            <td>value2<br>second line</td>
        </tr>
        <tr>
            <td>value 3</td>
            <td>value4</td>
        </tr>
    </tbody>
</table>
""".strip()
        )


class AnsiWidthTest(unittest.TestCase):
    colored = "\033[31mC\033[32mO\033[31mL\033[32mO\033[31mR\033[32mE\033[31mD\033[0m"

    def testColor(self):
        t = PrettyTable(["Field 1", "Field 2"])
        t.add_row([self.colored, self.colored])
        t.add_row(["nothing", "neither"])
        result = t.get_string()
        assert (
            result.strip()
            == f"""
+---------+---------+
| Field 1 | Field 2 |
+---------+---------+
| {self.colored} | {self.colored} |
| nothing | neither |
+---------+---------+
""".strip()
        )

    def testReset(self):
        t = PrettyTable(["Field 1", "Field 2"])
        t.add_row(["abc def\033(B", "\033[31mabc def\033[m"])
        t.add_row(["nothing", "neither"])
        result = t.get_string()
        assert (
            result.strip()
            == """
+---------+---------+
| Field 1 | Field 2 |
+---------+---------+
| abc def\033(B | \033[31mabc def\033[m |
| nothing | neither |
+---------+---------+
""".strip()
        )


class JSONOutputTests(unittest.TestCase):
    def testJSONOutput(self):
        t = helper_table()
        result = t.get_json_string()
        assert (
            result.strip()
            == """
[
    [
        "Field 1",
        "Field 2",
        "Field 3"
    ],
    {
        "Field 1": "value 1",
        "Field 2": "value2",
        "Field 3": "value3"
    },
    {
        "Field 1": "value 4",
        "Field 2": "value5",
        "Field 3": "value6"
    },
    {
        "Field 1": "value 7",
        "Field 2": "value8",
        "Field 3": "value9"
    }
]""".strip()
        )

    def testJSONOutputOptions(self):
        t = helper_table()
        result = t.get_json_string(header=False, indent=None, separators=(",", ":"))
        assert (
            result
            == """[{"Field 1":"value 1","Field 2":"value2","Field 3":"value3"},"""
            """{"Field 1":"value 4","Field 2":"value5","Field 3":"value6"},"""
            """{"Field 1":"value 7","Field 2":"value8","Field 3":"value9"}]"""
        )


class HtmlOutputTests(unittest.TestCase):
    def testHtmlOutput(self):
        t = helper_table()
        result = t.get_html_string()
        assert (
            result.strip()
            == """
<table>
    <thead>
        <tr>
            <th>Field 1</th>
            <th>Field 2</th>
            <th>Field 3</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>value 1</td>
            <td>value2</td>
            <td>value3</td>
        </tr>
        <tr>
            <td>value 4</td>
            <td>value5</td>
            <td>value6</td>
        </tr>
        <tr>
            <td>value 7</td>
            <td>value8</td>
            <td>value9</td>
        </tr>
    </tbody>
</table>
""".strip()
        )

    def testHtmlOutputFormatted(self):
        t = helper_table()
        result = t.get_html_string(format=True)
        assert (
            result.strip()
            == """
<table frame="box" rules="cols">
    <thead>
        <tr>
            <th style="padding-left: 1em; padding-right: 1em; text-align: center">Field 1</th>
            <th style="padding-left: 1em; padding-right: 1em; text-align: center">Field 2</th>
            <th style="padding-left: 1em; padding-right: 1em; text-align: center">Field 3</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top">value 1</td>
            <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top">value2</td>
            <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top">value3</td>
        </tr>
        <tr>
            <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top">value 4</td>
            <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top">value5</td>
            <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top">value6</td>
        </tr>
        <tr>
            <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top">value 7</td>
            <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top">value8</td>
            <td style="padding-left: 1em; padding-right: 1em; text-align: center; vertical-align: top">value9</td>
        </tr>
    </tbody>
</table>
""".strip()  # noqa: E501
        )


class PositionalJunctionsTests(CityDataTest):

    """Verify different cases for positional-junction characters"""

    def setUp(self):
        CityDataTest.setUp(self)
        self.x.set_style(DOUBLE_BORDER)

    def testDefault(self):
        assert (
            self.x.get_string().strip()
            == """
╔═══════════╦══════╦════════════╦═════════════════╗
║ City name ║ Area ║ Population ║ Annual Rainfall ║
╠═══════════╬══════╬════════════╬═════════════════╣
║  Adelaide ║ 1295 ║  1158259   ║      600.5      ║
║  Brisbane ║ 5905 ║  1857594   ║      1146.4     ║
║   Darwin  ║ 112  ║   120900   ║      1714.7     ║
║   Hobart  ║ 1357 ║   205556   ║      619.5      ║
║   Sydney  ║ 2058 ║  4336374   ║      1214.8     ║
║ Melbourne ║ 1566 ║  3806092   ║      646.9      ║
║   Perth   ║ 5386 ║  1554769   ║      869.4      ║
╚═══════════╩══════╩════════════╩═════════════════╝""".strip()
        )

    def testNoHeader(self):
        self.x.header = False
        assert (
            self.x.get_string().strip()
            == """
╔═══════════╦══════╦═════════╦════════╗
║  Adelaide ║ 1295 ║ 1158259 ║ 600.5  ║
║  Brisbane ║ 5905 ║ 1857594 ║ 1146.4 ║
║   Darwin  ║ 112  ║  120900 ║ 1714.7 ║
║   Hobart  ║ 1357 ║  205556 ║ 619.5  ║
║   Sydney  ║ 2058 ║ 4336374 ║ 1214.8 ║
║ Melbourne ║ 1566 ║ 3806092 ║ 646.9  ║
║   Perth   ║ 5386 ║ 1554769 ║ 869.4  ║
╚═══════════╩══════╩═════════╩════════╝""".strip()
        )

    def testWithTitle(self):
        self.x.title = "Title"
        assert (
            self.x.get_string().strip()
            == """
╔═════════════════════════════════════════════════╗
║                      Title                      ║
╠═══════════╦══════╦════════════╦═════════════════╣
║ City name ║ Area ║ Population ║ Annual Rainfall ║
╠═══════════╬══════╬════════════╬═════════════════╣
║  Adelaide ║ 1295 ║  1158259   ║      600.5      ║
║  Brisbane ║ 5905 ║  1857594   ║      1146.4     ║
║   Darwin  ║ 112  ║   120900   ║      1714.7     ║
║   Hobart  ║ 1357 ║   205556   ║      619.5      ║
║   Sydney  ║ 2058 ║  4336374   ║      1214.8     ║
║ Melbourne ║ 1566 ║  3806092   ║      646.9      ║
║   Perth   ║ 5386 ║  1554769   ║      869.4      ║
╚═══════════╩══════╩════════════╩═════════════════╝""".strip()
        )

    def testWithTitleNoHeader(self):
        self.x.title = "Title"
        self.x.header = False
        assert (
            self.x.get_string().strip()
            == """
╔═════════════════════════════════════╗
║                Title                ║
╠═══════════╦══════╦═════════╦════════╣
║  Adelaide ║ 1295 ║ 1158259 ║ 600.5  ║
║  Brisbane ║ 5905 ║ 1857594 ║ 1146.4 ║
║   Darwin  ║ 112  ║  120900 ║ 1714.7 ║
║   Hobart  ║ 1357 ║  205556 ║ 619.5  ║
║   Sydney  ║ 2058 ║ 4336374 ║ 1214.8 ║
║ Melbourne ║ 1566 ║ 3806092 ║ 646.9  ║
║   Perth   ║ 5386 ║ 1554769 ║ 869.4  ║
╚═══════════╩══════╩═════════╩════════╝""".strip()
        )

    def testHruleAll(self):
        self.x.title = "Title"
        self.x.hrules = ALL
        assert (
            self.x.get_string().strip()
            == """
╔═════════════════════════════════════════════════╗
║                      Title                      ║
╠═══════════╦══════╦════════════╦═════════════════╣
║ City name ║ Area ║ Population ║ Annual Rainfall ║
╠═══════════╬══════╬════════════╬═════════════════╣
║  Adelaide ║ 1295 ║  1158259   ║      600.5      ║
╠═══════════╬══════╬════════════╬═════════════════╣
║  Brisbane ║ 5905 ║  1857594   ║      1146.4     ║
╠═══════════╬══════╬════════════╬═════════════════╣
║   Darwin  ║ 112  ║   120900   ║      1714.7     ║
╠═══════════╬══════╬════════════╬═════════════════╣
║   Hobart  ║ 1357 ║   205556   ║      619.5      ║
╠═══════════╬══════╬════════════╬═════════════════╣
║   Sydney  ║ 2058 ║  4336374   ║      1214.8     ║
╠═══════════╬══════╬════════════╬═════════════════╣
║ Melbourne ║ 1566 ║  3806092   ║      646.9      ║
╠═══════════╬══════╬════════════╬═════════════════╣
║   Perth   ║ 5386 ║  1554769   ║      869.4      ║
╚═══════════╩══════╩════════════╩═════════════════╝""".strip()
        )

    def testVrulesNone(self):
        self.x.vrules = NONE
        assert (
            self.x.get_string().strip()
            == "═══════════════════════════════════════════════════\n"
            "  City name   Area   Population   Annual Rainfall  \n"
            "═══════════════════════════════════════════════════\n"
            "   Adelaide   1295    1158259          600.5       \n"
            "   Brisbane   5905    1857594          1146.4      \n"
            "    Darwin    112      120900          1714.7      \n"
            "    Hobart    1357     205556          619.5       \n"
            "    Sydney    2058    4336374          1214.8      \n"
            "  Melbourne   1566    3806092          646.9       \n"
            "    Perth     5386    1554769          869.4       \n"
            "═══════════════════════════════════════════════════".strip()
        )

    def testVrulesFrameWithTitle(self):
        self.x.vrules = FRAME
        self.x.title = "Title"
        assert (
            self.x.get_string().strip()
            == """
╔═════════════════════════════════════════════════╗
║                      Title                      ║
╠═════════════════════════════════════════════════╣
║ City name   Area   Population   Annual Rainfall ║
╠═════════════════════════════════════════════════╣
║  Adelaide   1295    1158259          600.5      ║
║  Brisbane   5905    1857594          1146.4     ║
║   Darwin    112      120900          1714.7     ║
║   Hobart    1357     205556          619.5      ║
║   Sydney    2058    4336374          1214.8     ║
║ Melbourne   1566    3806092          646.9      ║
║   Perth     5386    1554769          869.4      ║
╚═════════════════════════════════════════════════╝""".strip()
        )


@pytest.mark.parametrize(
    "style, expected",
    [
        pytest.param(
            DEFAULT,
            """
+---------+---------+---------+
| Field 1 | Field 2 | Field 3 |
+---------+---------+---------+
| value 1 |  value2 |  value3 |
| value 4 |  value5 |  value6 |
| value 7 |  value8 |  value9 |
+---------+---------+---------+
""",
            id="DEFAULT",
        ),
        pytest.param(
            MARKDOWN,
            """
| Field 1 | Field 2 | Field 3 |
|---------|---------|---------|
| value 1 |  value2 |  value3 |
| value 4 |  value5 |  value6 |
| value 7 |  value8 |  value9 |
""",
            id="MARKDOWN",
        ),
        pytest.param(
            MSWORD_FRIENDLY,
            """
| Field 1 | Field 2 | Field 3 |
| value 1 |  value2 |  value3 |
| value 4 |  value5 |  value6 |
| value 7 |  value8 |  value9 |
""",
            id="MSWORD_FRIENDLY",
        ),
        pytest.param(
            ORGMODE,
            """
|---------+---------+---------|
| Field 1 | Field 2 | Field 3 |
|---------+---------+---------|
| value 1 |  value2 |  value3 |
| value 4 |  value5 |  value6 |
| value 7 |  value8 |  value9 |
|---------+---------+---------|
""",
            id="ORGMODE",
        ),
        pytest.param(
            PLAIN_COLUMNS,
            """
Field 1        Field 2        Field 3        
value 1         value2         value3        
value 4         value5         value6        
value 7         value8         value9
""",  # noqa: W291
            id="PLAIN_COLUMNS",
        ),
        pytest.param(
            RANDOM,
            """
'^^^^^^^^^^^'^^^^^^^^^^'^^^^^^^^^^'
%    value 1%    value2%    value3%
'^^^^^^^^^^^'^^^^^^^^^^'^^^^^^^^^^'
%    value 4%    value5%    value6%
'^^^^^^^^^^^'^^^^^^^^^^'^^^^^^^^^^'
%    value 7%    value8%    value9%
'^^^^^^^^^^^'^^^^^^^^^^'^^^^^^^^^^'
""",
            id="RANDOM",
        ),
        pytest.param(
            DOUBLE_BORDER,
            """
╔═════════╦═════════╦═════════╗
║ Field 1 ║ Field 2 ║ Field 3 ║
╠═════════╬═════════╬═════════╣
║ value 1 ║  value2 ║  value3 ║
║ value 4 ║  value5 ║  value6 ║
║ value 7 ║  value8 ║  value9 ║
╚═════════╩═════════╩═════════╝
""",
        ),
    ],
)
def test_style(style, expected):
    # Arrange
    t = helper_table()
    random.seed(1234)

    # Act
    t.set_style(style)

    # Assert
    result = t.get_string()
    assert result.strip() == expected.strip()


def test_style_invalid():
    # Arrange
    t = helper_table()

    # Act / Assert
    # This is an hrule style, not a table style
    with pytest.raises(Exception):
        t.set_style(ALL)


class CsvConstructorTest(BasicTests):
    def setUp(self):

        csv_string = """City name, Area , Population , Annual Rainfall
        Sydney, 2058 ,  4336374   ,      1214.8
        Melbourne, 1566 ,  3806092   ,       646.9
        Brisbane, 5905 ,  1857594   ,      1146.4
        Perth, 5386 ,  1554769   ,       869.4
        Adelaide, 1295 ,  1158259   ,       600.5
        Hobart, 1357 ,   205556   ,       619.5
        Darwin, 0112 ,   120900   ,      1714.7"""
        csv_fp = io.StringIO(csv_string)
        self.x = from_csv(csv_fp)


class CsvOutputTests(unittest.TestCase):
    def testCsvOutput(self):
        t = helper_table()
        assert t.get_csv_string(delimiter="\t", header=False) == (
            "value 1\tvalue2\tvalue3\r\n"
            "value 4\tvalue5\tvalue6\r\n"
            "value 7\tvalue8\tvalue9\r\n"
        )
        assert t.get_csv_string() == (
            "Field 1,Field 2,Field 3\r\n"
            "value 1,value2,value3\r\n"
            "value 4,value5,value6\r\n"
            "value 7,value8,value9\r\n"
        )


class DatabaseConstructorTest(BasicTests):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.cur = self.conn.cursor()
        self.cur.execute(
            "CREATE TABLE cities "
            "(name TEXT, area INTEGER, population INTEGER, rainfall REAL)"
        )
        self.cur.execute('INSERT INTO cities VALUES ("Adelaide", 1295, 1158259, 600.5)')
        self.cur.execute(
            'INSERT INTO cities VALUES ("Brisbane", 5905, 1857594, 1146.4)'
        )
        self.cur.execute('INSERT INTO cities VALUES ("Darwin", 112, 120900, 1714.7)')
        self.cur.execute('INSERT INTO cities VALUES ("Hobart", 1357, 205556, 619.5)')
        self.cur.execute('INSERT INTO cities VALUES ("Sydney", 2058, 4336374, 1214.8)')
        self.cur.execute(
            'INSERT INTO cities VALUES ("Melbourne", 1566, 3806092, 646.9)'
        )
        self.cur.execute('INSERT INTO cities VALUES ("Perth", 5386, 1554769, 869.4)')
        self.cur.execute("SELECT * FROM cities")
        self.x = from_db_cursor(self.cur)

    def testNonSelectCursor(self):
        self.cur.execute('INSERT INTO cities VALUES ("Adelaide", 1295, 1158259, 600.5)')
        assert from_db_cursor(self.cur) is None


class JSONConstructorTest(CityDataTest):
    def testJSONAndBack(self):
        json_string = self.x.get_json_string()
        new_table = from_json(json_string)
        assert new_table.get_string() == self.x.get_string()


class HtmlConstructorTest(CityDataTest):
    def testHtmlAndBack(self):
        html_string = self.x.get_html_string()
        new_table = from_html(html_string)[0]
        assert new_table.get_string() == self.x.get_string()

    def testHtmlOneAndBack(self):
        html_string = self.x.get_html_string()
        new_table = from_html_one(html_string)
        assert new_table.get_string() == self.x.get_string()

    def testHtmlOneFailOnMany(self):
        html_string = self.x.get_html_string()
        html_string += self.x.get_html_string()
        with pytest.raises(Exception):
            from_html_one(html_string)


class PrintEnglishTest(CityDataTest):
    def testPrint(self):
        print()
        print(self.x)


class PrintJapaneseTest(unittest.TestCase):
    def setUp(self):

        self.x = PrettyTable(["Kanji", "Hiragana", "English"])
        self.x.add_row(["神戸", "こうべ", "Kobe"])
        self.x.add_row(["京都", "きょうと", "Kyoto"])
        self.x.add_row(["長崎", "ながさき", "Nagasaki"])
        self.x.add_row(["名古屋", "なごや", "Nagoya"])
        self.x.add_row(["大阪", "おおさか", "Osaka"])
        self.x.add_row(["札幌", "さっぽろ", "Sapporo"])
        self.x.add_row(["東京", "とうきょう", "Tokyo"])
        self.x.add_row(["横浜", "よこはま", "Yokohama"])

    def testPrint(self):
        print()
        print(self.x)


class PrintEmojiTest(unittest.TestCase):
    def setUp(self):
        thunder1 = [
            '\033[38;5;226m _`/""\033[38;5;250m.-.    \033[0m',
            "\033[38;5;226m  ,\\_\033[38;5;250m(   ).  \033[0m",
            "\033[38;5;226m   /\033[38;5;250m(___(__) \033[0m",
            "\033[38;5;228;5m    ⚡\033[38;5;111;25mʻ ʻ\033[38;5;228;5m"
            "⚡\033[38;5;111;25mʻ ʻ \033[0m",
            "\033[38;5;111m    ʻ ʻ ʻ ʻ  \033[0m",
        ]
        thunder2 = [
            "\033[38;5;240;1m     .-.     \033[0m",
            "\033[38;5;240;1m    (   ).   \033[0m",
            "\033[38;5;240;1m   (___(__)  \033[0m",
            "\033[38;5;21;1m  ‚ʻ\033[38;5;228;5m⚡\033[38;5;21;25mʻ‚\033[38;5;228;5m"
            "⚡\033[38;5;21;25m‚ʻ   \033[0m",
            "\033[38;5;21;1m  ‚ʻ‚ʻ\033[38;5;228;5m⚡\033[38;5;21;25mʻ‚ʻ   \033[0m",
        ]
        self.x = PrettyTable(["Thunderbolt", "Lightning"])
        for i in range(len(thunder1)):
            self.x.add_row([thunder1[i], thunder2[i]])

    def testPrint(self):
        print()
        print(self.x)


def test_paginate():
    # Arrange
    t = helper_table(rows=7)
    expected_page_1 = """
+----------+---------+---------+
| Field 1  | Field 2 | Field 3 |
+----------+---------+---------+
| value 1  |  value2 |  value3 |
| value 4  |  value5 |  value6 |
| value 7  |  value8 |  value9 |
| value 10 | value11 | value12 |
+----------+---------+---------+
    """.strip()
    expected_page_2 = """
+----------+---------+---------+
| Field 1  | Field 2 | Field 3 |
+----------+---------+---------+
| value 13 | value14 | value15 |
| value 16 | value17 | value18 |
| value 19 | value20 | value21 |
+----------+---------+---------+
""".strip()

    # Act
    paginated = t.paginate(page_length=4)

    # Assert
    paginated = paginated.strip()
    assert paginated.startswith(expected_page_1)
    assert "\f" in paginated
    assert paginated.endswith(expected_page_2)


def test_add_rows():
    """A table created with multiple add_row calls
    is the same as one created with a single add_rows
    """
    # Arrange
    t1 = PrettyTable(["A", "B", "C"])
    t2 = PrettyTable(["A", "B", "C"])
    t1.add_row([1, 2, 3])
    t1.add_row([4, 5, 6])
    rows = [
        [1, 2, 3],
        [4, 5, 6],
    ]

    # Act
    t2.add_rows(rows)

    # Assert
    assert str(t1) == str(t2)


def test_autoindex():

    """Testing that a table with a custom index row is
    equal to the one produced by the function
    .add_autoindex()
    """
    table1 = PrettyTable()
    table1.field_names = ["City name", "Area", "Population", "Annual Rainfall"]
    table1.add_row(["Adelaide", 1295, 1158259, 600.5])
    table1.add_row(["Brisbane", 5905, 1857594, 1146.4])
    table1.add_row(["Darwin", 112, 120900, 1714.7])
    table1.add_row(["Hobart", 1357, 205556, 619.5])
    table1.add_row(["Sydney", 2058, 4336374, 1214.8])
    table1.add_row(["Melbourne", 1566, 3806092, 646.9])
    table1.add_row(["Perth", 5386, 1554769, 869.4])
    table1.add_autoindex(fieldname="Test")

    table2 = PrettyTable()
    table2.field_names = ["Test", "City name", "Area", "Population", "Annual Rainfall"]
    table2.add_row([1, "Adelaide", 1295, 1158259, 600.5])
    table2.add_row([2, "Brisbane", 5905, 1857594, 1146.4])
    table2.add_row([3, "Darwin", 112, 120900, 1714.7])
    table2.add_row([4, "Hobart", 1357, 205556, 619.5])
    table2.add_row([5, "Sydney", 2058, 4336374, 1214.8])
    table2.add_row([6, "Melbourne", 1566, 3806092, 646.9])
    table2.add_row([7, "Perth", 5386, 1554769, 869.4])

    assert str(table1) == str(table2)


class UnpaddedTableTest(unittest.TestCase):
    def setUp(self):
        self.x = PrettyTable(header=False, padding_width=0)
        self.x.add_row("abc")
        self.x.add_row("def")
        self.x.add_row("g..")

    def testUnbordered(self):
        self.x.border = False
        result = self.x.get_string()
        expected = """
abc
def
g..
"""
        assert result.strip() == expected.strip()

    def testBordered(self):
        self.x.border = True
        result = self.x.get_string()
        expected = """
+-+-+-+
|a|b|c|
|d|e|f|
|g|.|.|
+-+-+-+
"""
        assert result.strip() == expected.strip()
