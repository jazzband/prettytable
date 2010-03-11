import unittest
import sys
sys.path.append("../src/")
from prettytable import *

class BuildEquivelanceTest(unittest.TestCase):

    """Make sure that building a table row-by-row and column-by-column yield the same results"""

    def setUp(self):

        # Row by row...
        self.row = PrettyTable()
        self.row.field_names = ["City name", "Area", "Population", "Annual Rainfall"]
        self.row.add_row(["Adelaide",1295, 1158259, 600.5])
        self.row.add_row(["Brisbane",5905, 1857594, 1146.4])
        self.row.add_row(["Darwin", 112, 120900, 1714.7])
        self.row.add_row(["Hobart", 1357, 205556, 619.5])
        self.row.add_row(["Sydney", 2058, 4336374, 1214.8])
        self.row.add_row(["Melbourne", 1566, 3806092, 646.9])
        self.row.add_row(["Perth", 5386, 1554769, 869.4])

        # Column by column...
        self.col = PrettyTable()
        self.col.add_column("City name",["Adelaide","Brisbane","Darwin","Hobart","Sydney","Melbourne","Perth"])
        self.col.add_column("Area", [1295, 5905, 112, 1357, 2058, 1566, 5386])
        self.col.add_column("Population", [1158259, 1857594, 120900, 205556, 4336374, 3806092, 1554769])
        self.col.add_column("Annual Rainfall",[600.5, 1146.4, 1714.7, 619.5, 1214.8, 646.9, 869.4])

        # A mix of both!
        self.mix = PrettyTable()
        self.mix.field_names = ["City name", "Area"]
        self.mix.add_row(["Adelaide",1295])
        self.mix.add_row(["Brisbane",5905])
        self.mix.add_row(["Darwin", 112])
        self.mix.add_row(["Hobart", 1357])
        self.mix.add_row(["Sydney", 2058])
        self.mix.add_row(["Melbourne", 1566])
        self.mix.add_row(["Perth", 5386])
        self.mix.add_column("Population", [1158259, 1857594, 120900, 205556, 4336374, 3806092, 1554769])
        self.mix.add_column("Annual Rainfall",[600.5, 1146.4, 1714.7, 619.5, 1214.8, 646.9, 869.4])

    def testRowColEquivalenceASCII(self):

        self.assertEqual(self.row.get_string(), self.col.get_string())

    def testRowMixEquivalenceASCII(self):

        self.assertEqual(self.row.get_string(), self.mix.get_string())

    def testRowColEquivalenceHTML(self):

        self.assertEqual(self.row.get_html_string(), self.col.get_html_string())

    def testRowMixEquivalenceHTML(self):

        self.assertEqual(self.row.get_html_string(), self.mix.get_html_string())

class CityDataTest(unittest.TestCase):

    """Just build the Australian capital city data example table."""

    def setUp(self):

        self.x = PrettyTable(["City name", "Area", "Population", "Annual Rainfall"])
        self.x.add_row(["Adelaide",1295, 1158259, 600.5])
        self.x.add_row(["Brisbane",5905, 1857594, 1146.4])
        self.x.add_row(["Darwin", 112, 120900, 1714.7])
        self.x.add_row(["Hobart", 1357, 205556, 619.5])
        self.x.add_row(["Sydney", 2058, 4336374, 1214.8])
        self.x.add_row(["Melbourne", 1566, 3806092, 646.9])
        self.x.add_row(["Perth", 5386, 1554769, 869.4])

class OptionOverrideTests(CityDataTest):

    """Make sure all options are properly overwritten by printt."""

    def testBorder(self):
        default = self.x.get_string()
        override = self.x.get_string(border=False)
        self.assert_(default != override)

    def testHeader(self):
        default = self.x.get_string()
        override = self.x.get_string(header=False)
        self.assert_(default != override)

    def testHrulesAll(self):
        default = self.x.get_string()
        override = self.x.get_string(hrules=ALL)
        self.assert_(default != override)

    def testHrulesNone(self):

        default = self.x.get_string()
        override = self.x.get_string(hrules=NONE)
        self.assert_(default != override)

class BasicTests(CityDataTest):

    """Some very basic tests."""

    def testNoBlankLines(self):

        """No table should ever have blank lines in it."""

        string = self.x.get_string()
        lines = string.split("\n")
        self.assert_("" not in lines)

    def testAllLengthsEqual(self):

        """All lines in a table should be of the same length."""

        string = self.x.get_string()
        lines = string.split("\n")
        lengths = [len(line) for line in lines]
        lengths = set(lengths)
        self.assertEqual(len(lengths),1)

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

class PresetBasicTests(BasicTests):

    """Run the basic tests after using set_style"""

    def setUp(self):
        BasicTests.setUp(self)
        self.x.set_style(MSWORD_FRIENDLY)

class BreakLineTests(unittest.TestCase):
    def testAsciiBreakLine(self):
        t = PrettyTable(['Field 1', 'Field 2'])
        t.add_row(['value 1', 'value2\nsecond line'])
        t.add_row(['value 3', 'value4'])
        result = t.get_string(hrules=True)
        assert result.strip() == """
+---------+-------------+
| Field 1 |   Field 2   |
+---------+-------------+
| value 1 |    value2   |
|         | second line |
+---------+-------------+
| value 3 |    value4   |
+---------+-------------+
""".strip()

        t = PrettyTable(['Field 1', 'Field 2'])
        t.add_row(['value 1', 'value2\nsecond line'])
        t.add_row(['value 3\n\nother line', 'value4\n\n\nvalue5'])
        result = t.get_string(hrules=True)
        assert result.strip() == """
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

        t = PrettyTable(['Field 1', 'Field 2'])
        t.add_row(['value 1', 'value2\nsecond line'])
        t.add_row(['value 3\n\nother line', 'value4\n\n\nvalue5'])
        result = t.get_string()
        assert result.strip() == """
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

    def testHtmlBreakLine(self):
        t = PrettyTable(['Field 1', 'Field 2'])
        t.add_row(['value 1', 'value2\nsecond line'])
        t.add_row(['value 3', 'value4'])
        result = t.get_html_string(hrules=True)
        assert result.strip() == """
<table border="1">
    <tr>
        <th>Field 1</th>
        <th>Field 2</th>
    </tr>
    <tr>
        <td>value 1</td>
        <td>value2<br />second line</td>
    <tr>
        <td>value 3</td>
        <td>value4</td>
    </tr>
</table>
""".strip()

if __name__ == "__main__":
    unittest.main()
