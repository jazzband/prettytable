from prettytable.colortable import Theme

# Import table fixture from test_prettytable


# Test colortable


# Test default and ocean theme


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
