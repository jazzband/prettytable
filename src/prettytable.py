#!/usr/bin/env python
#
# Copyright (c) 2009, Luke Maurits <luke@maurits.id.au>
# All rights reserved.
# With contributions from:
#  * Chris Clark
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * The name of the author may not be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

__version__ = "TRUNK"

import cgi
import copy
import cPickle
import random
import sys

# hrule styles
FRAME = 0
ALL   = 1
NONE  = 2

# Table styles
DEFAULT = 10
MSWORD_FRIENDLY = 11
PLAIN_COLUMNS = 12
RANDOM = 20

def cache_clearing(method):
    def wrapper(self, *args, **kwargs):
        method(self, *args, **kwargs)
        self.cache = {}
        self.html_cache = {}
    return wrapper

class PrettyTable:

    def __init__(self, fields=None, caching=True, padding_width=1, left_padding_width=1, right_padding_width=1):

        """Return a new PrettyTable instance

        Arguments:

        fields - list or tuple of field names
        caching - boolean value to turn string caching on/off
        padding width - number of spaces between column lines and content"""

        # Data
        self._field_names = []
        if fields:
            self.set_field_names(fields)
        else:
            self.widths = []
            self.aligns = []
        self.set_padding_width(padding_width)
        self.rows = []
        self.cache = {}
        self.html_cache = {}

        # Options
        self._start = 0
        self._end = None
        self._fields = None
        self._header = True
        self._border = True
        self._sortby = None
        self._reversesort = False
        self._attributes = {}
        self._hrules = FRAME
        self._caching = caching
        self._padding_width = padding_width
        self._left_padding_width = left_padding_width
        self._right_padding_width = right_padding_width
        self._vertical_char = "|"
        self._horizontal_char = "-"
        self._junction_char = "+"
        self._options = "start end fields header border sortby reversesort attributes hrules caching padding_width left_padding_width right_padding_width vertical_char horizontal_char junction_char".split()
    
    def __getslice__(self, i, j):

        """Return a new PrettyTable whose data rows are a slice of this one's

        Arguments:

        i - beginning slice index
        j - ending slice index"""

        newtable = copy.deepcopy(self)
        newtable.rows = self.rows[i:j]
        return newtable

    def __str__(self):

        return self.get_string()

    ##############################
    # ATTRIBUTE VALIDATORS       #
    ##############################

    # The method _validate_option is all that should be used elsewhere in the code base to validate options.
    # It will call the appropriate validation method for that option.  The individual validation methods should
    # never need to be called directly (although nothing bad will happen if they *are*).
    # Validation happens in TWO places.
    # Firstly, in the property setters defined in the ATTRIBUTE MANAGMENT section.
    # Secondly, in the _get_options method, where keyword arguments are mixed with persistent settings

    def _validate_option(self, option, val):
        if option in ("start", "end", "padding_width", "left_padding_width", "right_padding_width"):
            self._validate_nonnegative_int(option, val)
        elif option in ("sortby"):
            self._validate_field_name(option, val)
        elif option in ("hrules"):
            self._validate_hrules(option, val)
        elif option in ("fields"):
            self._validate_all_field_names(option, val)
        elif option in ("header", "border", "caching", "reversesort"):
            self._validate_true_or_false(option, val)
        elif option in ("vertical_char", "horizontal_char", "junction_char"):
            self._validate_single_char(option, val)
        else:
            raise Exception("Unrecognised option: %s!" % option)

    def _validate_nonnegative_int(self, name, val):
    	try:
            assert int(val) >= 0
        except AssertionError:
            raise Exception("Invalid value for %s: %s!" % (name, unicode(val)))

    def _validate_true_or_false(self, name, val):
    	try:
            assert val in (True, False)
        except AssertionError:
            raise Exception("Invalid value for %s!  Must be True or False." % name)

    def _validate_hrules(self, name, val):
    	try:
            assert val in (ALL, FRAME, NONE)
        except AssertionError:
            raise Exception("Invalid value for %s!  Must be ALL, FRAME or NONE." % name)

    def _validate_field_name(self, name, val):
    	try:
            assert val in self._field_names
        except AssertionError:
            raise Exception("Invalid field name: %s!" % val)

    def _validate_all_field_names(self, name, val):
    	try:
            for x in val:
                self._validate_field_name(name, x)
        except AssertionError:
            raise Exception("fields must be a sequence of field names!")

    def _validate_single_char(self, name, val):
    	try:
            assert len(unicode(val)) == 1
        except AssertionError:
            raise Exception("Invalid value for %s!  Must be a string of length 1." % name)

    ##############################
    # ATTRIBUTE MANAGEMENT       #
    ##############################

    # Start property
    def _get_start(self):
        return self._start
    def _set_start(self, val):
        self._validate_option("start", val)
        self._start = val
    start = property(_get_start, _set_start)

    # End property
    def _get_end(self):
        return self._end
    def _set_end(self, val):
        self._validate_option("end", val)
        self._end = val
    end = property(_get_end, _set_end)

    # Header property
    def _get_header(self):
        return self._header
    def _set_header(self, val):
    	self._validate_option("header", val)
        self._header = val
    header = property(_get_header, _set_header)

    # Border property
    def _get_border(self):
        return self._border
    def _set_border(self, val):
    	self._validate_option("border", val)
        self._border = val
    border = property(_get_border, _set_border)

    # Hrules property
    def _get_hrules(self):
        return self._hrules
    def _set_hrules(self, val):
    	self._validate_option("hrules", val)
        self._hrules = val
    hrules = property(_get_hrules, _set_hrules)

    # Padding width property
    def _get_padding_width(self):
        return self._padding_width
    def _set_padding_width(self, val):
        self._validate_option("padding_width", val)
        self._padding_width = val
    padding_width = property(_get_padding_width, _set_padding_width)

    # Left padding width property
    def _get_left_padding_width(self):
        return self._left_padding_width
    def _set_left_padding_width(self, val):
        self._validate_option("left_padding_width", val)
        self._left_padding_width = val
    left_padding_width = property(_get_left_padding_width, _set_left_padding_width)

    # Right padding width property
    def _get_right_padding_width(self):
        return self._right_padding_width
    def _set_right_padding_width(self, val):
        self._validate_option("right_padding_width", val)
        self._right_padding_width = val
    right_padding_width = property(_get_right_padding_width, _set_right_padding_width)

    # Vertical char property
    def _get_vertical_char(self):
        return self._vertical_char
    def _set_vertical_char(self, val):
        self._validate_option("vertical_char", val)
        self._vertical_char = val
    vertical_char = property(_get_vertical_char, _set_vertical_char)

    # Horizontal char property
    def _get_horizontal_char(self):
        return self._horizontal_char
    def _set_horizontal_char(self, val):
        self._validate_option("horizontal_char", val)
        self._horizontal_char = val
    horizontal_char = property(_get_horizontal_char, _set_horizontal_char)

    # Junction char property
    def _get_junction_char(self):
        return self._junction_char
    def _set_junction_char(self, val):
        self._validate_option("vertical_char", val)
        self._junction_char = val
    junction_char = property(_get_junction_char, _set_junction_char)

    ##############################
    # OPTION MIXER               #
    ##############################

    def _get_options(self, kwargs):
        options = {}
        for option in self._options:
            if option in kwargs:
                self._validate_option(option, kwargs[option])
                options[option] = kwargs[option]
            else:
                options[option] = getattr(self, "_"+option)
        return options

    ##############################
    # ATTRIBUTE SETTERS          #
    ##############################

    @cache_clearing
    def set_field_names(self, fields):

        """Set the names of the fields

        Arguments:

        fields - list or tuple of field names"""

        # We *may* need to change the widths if this isn't the first time
        # setting the field names.  This could certainly be done more
        # efficiently.
        if self._field_names:
            self.widths = [len(field) for field in fields]
            for row in self.rows:
                for i in range(0,len(row)):
                    if len(unicode(row[i])) > self.widths[i]:
                        self.widths[i] = len(unicode(row[i]))
        else:
            self.widths = [len(field) for field in fields]
        self._field_names = fields
        self.aligns = len(fields)*["c"]

    @cache_clearing
    def set_field_align(self, fieldname, align):

        """Set the alignment of a field by its fieldname

        Arguments:

        fieldname - name of the field whose alignment is to be changed
        align - desired alignment - "l" for left, "c" for centre and "r" for right"""

        if fieldname not in self._field_names:
            raise Exception("No field %s exists!" % fieldname)
        if align not in ["l","c","r"]:
            raise Exception("Alignment %s is invalid, use l, c or r!" % align)
        self.aligns[self._field_names.index(fieldname)] = align

    @cache_clearing
    def set_padding_width(self, padding_width):

        """Set the number of empty spaces between a column's edge and its content

        Arguments:

        padding_width - number of spaces, must be a positive integer"""

        try:
            assert int(padding_width) >= 0
        except AssertionError:
            raise Exception("Invalid value for padding_width: %s!" % unicode(padding_width))

        self.padding_width = padding_width

    @cache_clearing
    def set_left_padding(self, left_padding):

        """Set the number of empty spaces between a column's left edge and its content

        Arguments:

        left_padding - number of spaces, must be a positive integer"""

        try:
            assert left_padding == None or int(left_padding) >= 0
        except AssertionError:
            raise Exception("Invalid value for left_padding: %s!" % unicode(left_padding))

        self.left_padding = left_padding

    @cache_clearing
    def set_right_padding(self, right_padding):

        """Set the number of empty spaces between a column's right edge and its content

        Arguments:

        right_padding - number of spaces, must be a positive integer"""

        try:
            assert right_padding == None or int(right_padding) >= 0
        except AssertionError:
            raise Exception("Invalid value for right_padding: %s!" % unicode(right_padding))

        self.right_padding = right_padding

    @cache_clearing
    def set_border_chars(self, vertical="|", horizontal="-", junction="+"):

        """Set the characters to use when drawing the table border

        Arguments:

        vertical - character used to draw a vertical line segment.  Default is |
        horizontal - character used to draw a horizontal line segment.  Default is -
        junction - character used to draw a line junction.  Default is +"""

        if len(vertical) > 1 or len(horizontal) > 1 or len(junction) > 1:
            raise Exception("All border characters must be strings of length ONE!")
        self.vertical_char = vertical
        self.horizontal_char = horizontal
        self.junction_char = junction

    ##############################
    # PRESET STYLE LOGIC         #
    ##############################

    def set_style(self, style):
        if style == DEFAULT:
            self._set_default_style()
        elif style == MSWORD_FRIENDLY:
            self._set_msword_style()
        elif style == PLAIN_COLUMNS:
            self._set_columns_style()
        elif style == RANDOM:
            self._set_random_style()
        else:
            raise Exception("Invalid pre-set style!")

    def _set_default_style(self):

        self.header = True
        self.border = True
        self.hrules = FRAME
        self.padding_width = 1
        self.left_padding_width = 1
        self.right_padding_width = 1
        self.vertical_char = "|"
        self.horizontal_char = "-"
        self.junction_char = "+"

    def _set_msword_style(self):

        self.header = True
        self.border = True
        self.hrules = NONE
        self.padding_width = 1
        self.left_padding_width = 1
        self.right_padding_width = 1
        self.vertical_char = "|"

    def _set_columns_style(self):

        self.header = True
        self.border = False
        self.padding_width = 1
        self.left_padding_width = 0
        self.right_padding_width = 8

    def _set_random_style(self):

        # Just for fun!
        self.header = random.choice((True, False))
        self.border = random.choice((True, False))
        self.hrules = random.choice((ALL, FRAME, NONE))
        self.left_padding_width = random.randint(0,5)
        self.right_padding_width = random.randint(0,5)
        self.vertical_char = random.choice("~!@#$%^&*()_+|-=\{}[];':\",./;<>?")
        self.horizontal_char = random.choice("~!@#$%^&*()_+|-=\{}[];':\",./;<>?")
        self.junction_char = random.choice("~!@#$%^&*()_+|-=\{}[];':\",./;<>?")

    ##############################
    # DATA INPUT METHODS         #
    ##############################

    @cache_clearing
    def add_row(self, row):

        """Add a row to the table

        Arguments:

        row - row of data, should be a list with as many elements as the table
        has fields"""

        if len(row) != len(self._field_names):
            raise Exception("Row has incorrect number of values, (actual) %d!=%d (expected)" %(len(row),len(self._field_names)))
        self.rows.append(row)
        for i in range(0,len(row)):
            if len(unicode(row[i])) > self.widths[i]:
                self.widths[i] = len(unicode(row[i]))

    @cache_clearing
    def add_column(self, fieldname, column, align="c"):

        """Add a column to the table.

        Arguments:

        fieldname - name of the field to contain the new column of data
        column - column of data, should be a list with as many elements as the
        table has rows
        align - desired alignment for this column - "l" for left, "c" for centre and "r" for right"""

        if len(self.rows) in (0, len(column)):
            if align not in ["l","c","r"]:
                raise Exception("Alignment %s is invalid, use l, c or r!" % align)
            self._field_names.append(fieldname)
            self.widths.append(len(fieldname))
            self.aligns.append(align)
            for i in range(0, len(column)):
                if len(self.rows) < i+1:
                    self.rows.append([])
                self.rows[i].append(column[i])
                if len(unicode(column[i])) > self.widths[-1]:
                    self.widths[-1] = len(unicode(column[i]))
        else:
            raise Exception("Column length %d does not match number of rows %d!" % (len(column), len(self.rows)))

    ##############################
    # MISC PRIVATE METHODS       #
    ##############################

    def _get_sorted_rows(self, options):
        # Sort rows using the "Decorate, Sort, Undecorate" (DSU) paradigm
        rows = copy.deepcopy(self.rows[options["start"]:options["end"]])
        sortindex = self._field_names.index(options["sortby"])
        # Decorate
        rows = [[row[sortindex]]+row for row in rows]
        # Sort
        rows.sort(reverse=options["reversesort"])
        # Undecorate
        rows = [row[1:] for row in rows]
        return rows

    ##############################
    # ASCII PRINT/STRING METHODS #
    ##############################

    def printt(self, **kwargs):

        """Print table in current state to stdout.

        Arguments:

        start - index of first data row to include in output
        end - index of last data row to include in output PLUS ONE (list slice style)
        fields - names of fields (columns) to include
        sortby - name of field to sort rows by
        reversesort - True or False to sort in descending or ascending order
        border - should be True or False to print or not print borders
        hrules - controls printing of horizontal rules after each row.  Allowed values: FRAME, ALL, NONE"""

        print self.get_string(**kwargs)

    def get_string(self, **kwargs):

        """Return string representation of table in current state.

        Arguments:

        start - index of first data row to include in output
        end - index of last data row to include in output PLUS ONE (list slice style)
        fields - names of fields (columns) to include
        sortby - name of field to sort rows by
        reversesort - True or False to sort in descending or ascending order
        border - should be True or False to print or not print borders
        hrules - controls printing of horizontal rules after each row.  Allowed values: FRAME, ALL, NONE"""

        options = self._get_options(kwargs)

        if self._caching:
            key = cPickle.dumps(options)
            if key in self.cache:
                return self.cache[key]

        bits = []
        if not self._field_names:
            return ""
        if not options["header"]:
            # Recalculate widths - avoids tables with long field names but narrow data looking odd
            old_widths = self.widths[:]
            self.widths = [0]*len(self._field_names)
            for row in self.rows:
                for i in range(0,len(row)):
                    if len(unicode(row[i])) > self.widths[i]:
                        self.widths[i] = len(unicode(row[i]))
        if options["header"]:
            bits.append(self._stringify_header(options))
        elif options["border"] and options["hrules"] != NONE:
            bits.append(self._stringify_hrule(options))
        if options["sortby"]:
            rows = self._get_sorted_rows(options)
        else:
            rows = self.rows[options["start"]:options["end"]]
        for row in rows:
            bits.append(self._stringify_row(row, options))
        if options["border"] and not options["hrules"]:
            bits.append(self._stringify_hrule(options))
        string = "\n".join(bits)

        if self._caching:
            self.cache[key] = string

        if not options["header"]:
            # Restore previous widths
            self.widths = old_widths
            for row in self.rows:
                for i in range(0,len(row)):
                    if len(unicode(row[i])) > self.widths[i]:
                        self.widths[i] = len(unicode(row[i]))

        return string

    def _stringify_hrule(self, options):

        if not options["border"]:
            return ""
        padding_width = options["left_padding_width"]+options["right_padding_width"]
        bits = [options["junction_char"]]
        for field, width in zip(self._field_names, self.widths):
            if options["fields"] and field not in options["fields"]:
                continue
            bits.append((width+padding_width)*options["horizontal_char"])
            bits.append(options["junction_char"])
        return "".join(bits)

    def _stringify_header(self, options):

        bits = []
        if options["border"]:
            if options["hrules"] != NONE:
                bits.append(self._stringify_hrule(options))
                bits.append("\n")
            bits.append(options["vertical_char"])
        for field, width, align in zip(self._field_names, self.widths, self.aligns):
            if options["fields"] and field not in options["fields"]:
                continue
            if align == "l":
                bits.append(" " * options["left_padding_width"] + unicode(field).ljust(width) + " " * options["right_padding_width"])
            elif align == "r":
                bits.append(" " * options["left_padding_width"] + unicode(field).rjust(width) + " " * options["right_padding_width"])
            else:
                bits.append(" " * options["left_padding_width"] + unicode(field).center(width) + " " * options["right_padding_width"])
            if options["border"]:
                bits.append(options["vertical_char"])
        if options["border"] and options["hrules"] != NONE:
            bits.append("\n")
            bits.append(self._stringify_hrule(options))
        return "".join(bits)

    def _stringify_row(self, row, options):

        bits = []
        if options["border"]:
            bits.append(self.vertical_char)
        for field, value, width, align in zip(self._field_names, row, self.widths, self.aligns):
            if options["fields"] and field not in options["fields"]:
                continue
            if align == "l":
                bits.append(" " * options["left_padding_width"] + unicode(value).ljust(width) + " " * options["right_padding_width"])
            elif align == "r":
                bits.append(" " * options["left_padding_width"] + unicode(value).rjust(width) + " " * options["right_padding_width"])
            else:
                bits.append(" " * options["left_padding_width"] + unicode(value).center(width) + " " * options["right_padding_width"])
            if options["border"]:
                bits.append(self.vertical_char)
        if options["border"] and options["hrules"]== ALL:
            bits.append("\n")
            bits.append(self._stringify_hrule(options))
        return "".join(bits)

    ##############################
    # HTML PRINT/STRING METHODS  #
    ##############################

    def print_html(self, **kwargs):

        """Print HTML formatted version of table in current state to stdout.

        Arguments:

        start - index of first data row to include in output
        end - index of last data row to include in output PLUS ONE (list slice style)
        fields - names of fields (columns) to include
        sortby - name of field to sort rows by
        format - should be True or False to attempt to format alignmet, padding, etc. or not
        header - should be True or False to print a header showing field names or not
        border - should be True or False to print or not print borders
        hrules - include horizontal rule after each row
        attributes - dictionary of name/value pairs to include as HTML attributes in the <table> tag"""

        print self.get_html_string(**kwargs)

    def get_html_string(self, **kwargs):

        """Return string representation of HTML formatted version of table in current state.

        Arguments:

        start - index of first data row to include in output
        end - index of last data row to include in output PLUS ONE (list slice style)
        fields - names of fields (columns) to include
        sortby - name of 
        border - should be True or False to print or not print borders
        format - should be True or False to attempt to format alignmet, padding, etc. or not
        header - should be True or False to print a header showing field names or not
        border - should be True or False to print or not print borders
        hrules - include horizontal rule after each row
        attributes - dictionary of name/value pairs to include as HTML attributes in the <table> tag"""

        options = self._get_options(kwargs)

        if self._caching:
            key = cPickle.dumps(options)
            if key in self.html_cache:
                return self.html_cache[key]

        if format:
            string = self._get_formatted_html_string(options)
        else:
            string = self._get_simple_html_string(options)

        if self._caching:
            self.html_cache[key] = string

        return string

    def _get_simple_html_string(self, options):

        bits = []
        # Slow but works
        table_tag = '<table'
        if options["border"]:
            table_tag += ' border="1"'
        if options["attributes"]:
            for attr_name in options["attributes"]:
                table_tag += ' %s="%s"' % (attr_name, options["attributes"][attr_name])
        table_tag += '>'
        bits.append(table_tag)
        # Headers
        bits.append("    <tr>")
        for field in self._field_names:
            if options["fields"] and field not in options["fields"]:
                continue
            bits.append("        <th>%s</th>" % cgi.escape(unicode(field)))
        bits.append("    </tr>")
        # Data
        if options["sortby"]:
            rows = self._get_sorted_rows(options)
        else:
            rows = self.rows
        for row in self.rows:
            bits.append("    <tr>")
            for field, datum in zip(self._field_names, row):
                if options["fields"] and field not in options["fields"]:
                    continue
                bits.append("        <td>%s</td>" % cgi.escape(unicode(datum)))
        bits.append("    </tr>")
        bits.append("</table>")
        string = "\n".join(bits)

        return string

    def _get_formatted_html_string(self, options):

        bits = []
        # Slow but works
        table_tag = '<table'
        if options["border"]:
            table_tag += ' border="1"'
        if options["hrules"] == NONE:
            table_tag += ' frame="vsides" rules="cols"'
        if options["attributes"]:
            for attr_name in options["attributes"]:
                table_tag += ' %s="%s"' % (attr_name, options["attributes"][attr_name])
        table_tag += '>'
        bits.append(table_tag)
        # Headers
        if options["header"]:
            bits.append("    <tr>")
            for field in self._field_names:
                if options["fields"] and field not in options["fields"]:
                    continue
                bits.append("        <th style=\"padding-left: %dem; padding-right: %dem; text-align: center\">%s</th>" % (options["left_padding_width"], options["right_padding_width"], cgi.escape(unicode(field))))
            bits.append("    </tr>")
        # Data
        if options["sortby"]:
            rows = self._get_sorted_rows(options)
        else:
            rows = self.rows
        for row in self.rows:
            bits.append("    <tr>")
            for field, align, datum in zip(self._field_names, self.aligns, row):
                if options["fields"] and field not in options["fields"]:
                    continue
                if align == "l":
                    bits.append("        <td style=\"padding-left: %dem; padding-right: %dem; text-align: left\">%s</td>" % (options["left_padding_width"], options["right_padding_width"], cgi.escape(unicode(datum))))
                elif align == "r":
                    bits.append("        <td style=\"padding-left: %dem; padding-right: %dem; text-align: right\">%s</td>" % (options["left_padding_width"], options["right_padding_width"], cgi.escape(unicode(datum))))
                else:
                    bits.append("        <td style=\"padding-left: %dem; padding-right: %dem; text-align: center\">%s</td>" % (options["left_padding_width"], options["right_padding_width"], cgi.escape(unicode(datum))))
        bits.append("    </tr>")
        bits.append("</table>")
        string = "\n".join(bits)

        return string

def main():

    x = PrettyTable(["City name", "Area", "Population", "Annual Rainfall"])
    x.set_field_align("City name", "l") # Left align city names
    x.add_row(["Adelaide",1295, 1158259, 600.5])
    x.add_row(["Brisbane",5905, 1857594, 1146.4])
    x.add_row(["Darwin", 112, 120900, 1714.7])
    x.add_row(["Hobart", 1357, 205556, 619.5])
    x.add_row(["Sydney", 2058, 4336374, 1214.8])
    x.add_row(["Melbourne", 1566, 3806092, 646.9])
    x.add_row(["Perth", 5386, 1554769, 869.4])
    print x

if __name__ == "__main__":
    main()
