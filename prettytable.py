# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright (c) 2009, Luke Maurits <luke@maurits.id.au>
# All rights reserved.
# With contributions from:
#  * Chris Clark
#  * Klein Stephane
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

import copy
import csv
import random
import sys
import textwrap
import itertools
import unicodedata

py3k = sys.version_info[0] >= 3
if py3k:
    unicode = str
    basestring = str
    itermap = map
    iterzip = zip
else: 
    itermap = itertools.imap
    iterzip = itertools.izip

if py3k and sys.version_info[1] >= 2:
    from html import escape
else:
    from cgi import escape

# hrule styles
FRAME = 0
ALL   = 1
NONE  = 2

# Table styles
DEFAULT = 10
MSWORD_FRIENDLY = 11
PLAIN_COLUMNS = 12
RANDOM = 20

def _get_size(text):
    lines = text.split("\n")
    height = len(lines)
    width = max([textual_width(line) for line in lines])
    return (width, height)
        
class PrettyTable(object):

    def __init__(self, field_names=None, **kwargs):

        """Return a new PrettyTable instance

        Arguments:

        encoding - Unicode encoding scheme used to decode any encoded input
        field_names - list or tuple of field names
        fields - list or tuple of field names to include in displays
        start - index of first data row to include in output
        end - index of last data row to include in output PLUS ONE (list slice style)
        fields - names of fields (columns) to include
        header - print a header showing field names (True or False)
        header_style - stylisation to apply to field names in header ("cap", "title", "upper", "lower" or None)
        border - print a border around the table (True or False)
        hrules - controls printing of horizontal rules after rows.  Allowed values: FRAME, ALL, NONE
	int_format - controls formatting of integer data
	float_format - controls formatting of floating point data
        padding_width - number of spaces on either side of column data (only used if left and right paddings are None)
        left_padding_width - number of spaces on left hand side of column data
        right_padding_width - number of spaces on right hand side of column data
        vertical_char - single character string used to draw vertical lines
        horizontal_char - single character string used to draw horizontal lines
        junction_char - single character string used to draw line junctions
        sortby - name of field to sort rows by
        sort_key - sorting key function, applied to data points before sorting
        reversesort - True or False to sort in descending or ascending order"""

        if "encoding" in kwargs:
            self.encoding = kwargs["encoding"]
        else:
            self.encoding = "UTF-8"

        # Data
        self._field_names = []
        self._align = {}
        self._max_width = {}
        self._rows = []
        if field_names:
            self.field_names = field_names
        else:
            self._widths = []
        self._rows = []

        # Options
        self._options = "start end fields header border sortby reversesort sort_key attributes format hrules".split()
        self._options.extend("int_format float_format padding_width left_padding_width right_padding_width".split())
        self._options.extend("vertical_char horizontal_char junction_char header_style".split())
        for option in self._options:
            if option in kwargs:
                self._validate_option(option, kwargs[option])
            else:
                kwargs[option] = None


        self._start = kwargs["start"] or 0
        self._end = kwargs["end"] or None
        self._fields = kwargs["fields"] or None

        self._header = kwargs["header"] or True
        self._header_style = kwargs["header_style"] or None
        self._border = kwargs["border"] or True
        self._hrules = kwargs["hrules"] or FRAME

        self._sortby = kwargs["sortby"] or None
        self._reversesort = kwargs["reversesort"] or False
        self._sort_key = kwargs["sort_key"] or (lambda x: x)

        self._int_format = kwargs["float_format"] or {}
        self._float_format = kwargs["float_format"] or {}
        self._padding_width = kwargs["padding_width"] or 1
        self._left_padding_width = kwargs["left_padding_width"] or None
        self._right_padding_width = kwargs["right_padding_width"] or None

        self._vertical_char = kwargs["vertical_char"] or self._unicode("|")
        self._horizontal_char = kwargs["horizontal_char"] or self._unicode("-")
        self._junction_char = kwargs["junction_char"] or self._unicode("+")
        
        self._format = kwargs["format"] or False
        self._attributes = kwargs["attributes"] or {}
   
    def _unicode(self, value):
        if not isinstance(value, basestring):
            value = str(value)
        if not isinstance(value, unicode):
            value = unicode(value, self.encoding, "strict")
        return value

    def _justify(self, text, width, align):
        excess = width - textual_width(text)
        if align == "l":
            return text + excess * " "
        elif align == "r":
            return excess * " " + text
        else:
            if excess % 2:
                # Uneven padding
                # Put more space on right if text is of odd length...
                if textual_width(text) % 2:
                    return (excess//2)*" " + text + (excess//2 + 1)*" "
                # and more space on left if text is of even length
                else:
                    return (excess//2 + 1)*" " + text + (excess//2)*" "
                # Why distribute extra space this way?  To match the behaviour of
                # the inbuilt str.center() method.
            else:
                # Equal padding on either side
                return (excess//2)*" " + text + (excess//2)*" "

    def __getattr__(self, name):

        if name == "rowcount":
            return len(self._rows)
        elif name == "colcount":
            if self._field_names:
                return len(self._field_names)
            elif self._rows:
                return len(self._rows[0])
            else:
                return 0
        else:
            raise AttributeError(name)
 
    def __getitem__(self, index):

        newtable = copy.deepcopy(self)
        if isinstance(index, slice):
            newtable._rows = self._rows[index]
        elif isinstance(index, int):
            newtable._rows = [self._rows[index],]
        else:
            raise Exception("Index %s is invalid, must be an integer or slice" % str(index))
        return newtable

    def __str__(self):
        return self.__unicode__().encode(self.encoding)

    def __unicode__(self):
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
        if option in ("field_names"):
            self._validate_field_names(val)
        elif option in ("start", "end", "max_width", "padding_width", "left_padding_width", "right_padding_width", "format"):
            self._validate_nonnegative_int(option, val)
        elif option in ("sortby"):
            self._validate_field_name(option, val)
        elif option in ("sort_key"):
            self._validate_function(option, val)
        elif option in ("hrules"):
            self._validate_hrules(option, val)
        elif option in ("fields"):
            self._validate_all_field_names(option, val)
        elif option in ("header", "border", "reversesort"):
            self._validate_true_or_false(option, val)
        elif option in ("header_style"):
            self._validate_header_style(val)
#        elif option in ("int_format"):
#            self._validate_int_format(option, val)
#        elif option in ("float_format"):
#            self._validate_float_format(option, val)
        elif option in ("vertical_char", "horizontal_char", "junction_char"):
            self._validate_single_char(option, val)
        elif option in ("attributes"):
            self._validate_attributes(option, val)
        else:
            raise Exception("Unrecognised option: %s!" % option)

    def _validate_field_names(self, val):
        # Check for appropriate length
        if self._field_names:
            try:
               assert len(val) == len(self._field_names)
            except AssertionError:
               raise Exception("Field name list has incorrect number of values, (actual) %d!=%d (expected)" % (len(val), len(self._field_names)))
        if self._rows:
            try:
               assert len(val) == len(self._rows[0])
            except AssertionError:
               raise Exception("Field name list has incorrect number of values, (actual) %d!=%d (expected)" % (len(val), len(self._rows[0])))
        # Check for uniqueness
        try:
            assert len(val) == len(set(val))
        except AssertionError:
            raise Exception("Field names must be unique!")

    def _validate_header_style(self, val):
        try:
            assert val in ("cap", "title", "upper", "lower", None)
        except AssertionError:
            raise Exception("Invalid header style, use cap, title, upper, lower or None!")

    def _validate_align(self, val):
        try:
            assert val in ["l","c","r"]
        except AssertionError:
            raise Exception("Alignment %s is invalid, use l, c or r!" % val)

    def _validate_nonnegative_int(self, name, val):
        try:
            assert int(val) >= 0
        except AssertionError:
            raise Exception("Invalid value for %s: %s!" % (name, self._unicode(val)))

    def _validate_true_or_false(self, name, val):
        try:
            assert val in (True, False)
        except AssertionError:
            raise Exception("Invalid value for %s!  Must be True or False." % name)

    def _validate_int_format(self, name, val):
        if val == "":
            return
        try:
            assert type(val) in (str, unicode)
            assert val.isdigit()
        except AssertionError:
            raise Exception("Invalid value for %s!  Must be an integer format string." % name)

    def _validate_float_format(self, name, val):
        if val == "":
            return
        try:
            assert type(val) in (str, unicode)
            assert "." in val
            bits = val.split(".")
            assert len(bits) <= 2
            assert bits[0] == "" or bits[0].isdigit()
            assert bits[1] == "" or bits[1].isdigit()
        except AssertionError:
            raise Exception("Invalid value for %s!  Must be a float format string." % name)

    def _validate_function(self, name, val):
        try:
            assert hasattr(val, "__call__")
        except AssertionError:
            raise Exception("Invalid value for %s!  Must be a function." % name)

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
            assert textual_width(val) == 1
        except AssertionError:
            raise Exception("Invalid value for %s!  Must be a string of length 1." % name)

    def _validate_attributes(self, name, val):
        try:
            assert isinstance(val, dict)
        except AssertionError:
            raise Exception("attributes must be a dictionary of name/value pairs!")

    ##############################
    # ATTRIBUTE MANAGEMENT       #
    ##############################

    def _get_field_names(self):
        return self._field_names
        """The names of the fields

        Arguments:

        fields - list or tuple of field names"""
    def _set_field_names(self, val):
        val = [self._unicode(x) for x in val]
        self._validate_option("field_names", val)
        if self._field_names:
            old_names = self._field_names[:]
        self._field_names = val
        if self._align and old_names:
            for old_name, new_name in zip(old_names, val):
                self._align[new_name] = self._align[old_name]
            for old_name in old_names:
                self._align.pop(old_name)
        else:
            for field in self._field_names:
                self._align[field] = "c"
    field_names = property(_get_field_names, _set_field_names)

    def _get_align(self):
        return self._align
    def _set_align(self, val):
        self._validate_align(val)
        for field in self._field_names:
            self._align[field] = val
    align = property(_get_align, _set_align)

    def _get_max_width(self):
        return self._max_width
    def _set_max_width(self, val):
        self._validate_option("max_width", val)
        for field in self._field_names:
            self._max_width[field] = val
    max_width = property(_get_max_width, _set_max_width)
    
    def _get_start(self):
        """Start index of the range of rows to print

        Arguments:

        start - index of first data row to include in output"""
        return self._start

    def _set_start(self, val):
        self._validate_option("start", val)
        self._start = val
    start = property(_get_start, _set_start)

    def _get_end(self):
        """End index of the range of rows to print

        Arguments:

        end - index of last data row to include in output PLUS ONE (list slice style)"""
        return self._end
    def _set_end(self, val):
        self._validate_option("end", val)
        self._end = val
    end = property(_get_end, _set_end)

    def _get_sortby(self):
        """Name of field by which to sort rows

        Arguments:

        sortby - field name to sort by"""
        return self._sortby
    def _set_sortby(self, val):
        self._validate_option("sortby", val)
        self._sortby = val
    sortby = property(_get_sortby, _set_sortby)

    def _get_reversesort(self):
        """Controls direction of sorting (ascending vs descending)

        Arguments:

        reveresort - set to True to sort by descending order, or False to sort by ascending order"""
        return self._reversesort
    def _set_reversesort(self, val):
        self._validate_option("reversesort", val)
        self._reversesort = val
    reversesort = property(_get_reversesort, _set_reversesort)

    def _get_sort_key(self):
        """Sorting key function, applied to data points before sorting

        Arguments:

        sort_key - a function which takes one argument and returns something to be sorted"""
        return self._sort_key
    def _set_sort_key(self, val):
        self._validate_option("sort_key", val)
        self._sort_key = val
    sort_key = property(_get_sort_key, _set_sort_key)
 
    def _get_header(self):
        """Controls printing of table header with field names

        Arguments:

        header - print a header showing field names (True or False)"""
        return self._header
    def _set_header(self, val):
        self._validate_option("header", val)
        self._header = val
    header = property(_get_header, _set_header)

    def _get_header_style(self):
        """Controls stylisation applied to field names in header

        Arguments:

        header_style - stylisation to apply to field names in header ("cap", "title", "upper", "lower" or None)"""
        return self._header_style
    def _set_header_style(self, val):
        self._validate_header_style(val)
        self._header_style = val
    header_style = property(_get_header_style, _set_header_style)

    def _get_border(self):
        """Controls printing of border around table

        Arguments:

        border - print a border around the table (True or False)"""
        return self._border
    def _set_border(self, val):
        self._validate_option("border", val)
        self._border = val
    border = property(_get_border, _set_border)

    def _get_hrules(self):
        """Controls printing of horizontal rules after rows

        Arguments:

        hrules - horizontal rules style.  Allowed values: FRAME, ALL, NONE"""
        return self._hrules
    def _set_hrules(self, val):
        self._validate_option("hrules", val)
        self._hrules = val
    hrules = property(_get_hrules, _set_hrules)

    def _get_int_format(self):
        """Controls formatting of integer data
        Arguments:

        int_format - integer format string"""
        return self._int_format
    def _set_int_format(self, val):
#        self._validate_option("int_format", val)
        for field in self._field_names:
            self._int_format[field] = val
    int_format = property(_get_int_format, _set_int_format)

    def _get_float_format(self):
        """Controls formatting of floating point data
        Arguments:

        float_format - floating point format string"""
        return self._float_format
    def _set_float_format(self, val):
#        self._validate_option("float_format", val)
        for field in self._field_names:
            self._float_format[field] = val
    float_format = property(_get_float_format, _set_float_format)

    def _get_padding_width(self):
        """The number of empty spaces between a column's edge and its content

        Arguments:

        padding_width - number of spaces, must be a positive integer"""
        return self._padding_width
    def _set_padding_width(self, val):
        self._validate_option("padding_width", val)
        self._padding_width = val
    padding_width = property(_get_padding_width, _set_padding_width)

    def _get_left_padding_width(self):
        """The number of empty spaces between a column's left edge and its content

        Arguments:

        left_padding - number of spaces, must be a positive integer"""
        return self._left_padding_width
    def _set_left_padding_width(self, val):
        self._validate_option("left_padding_width", val)
        self._left_padding_width = val
    left_padding_width = property(_get_left_padding_width, _set_left_padding_width)

    def _get_right_padding_width(self):
        """The number of empty spaces between a column's right edge and its content

        Arguments:

        right_padding - number of spaces, must be a positive integer"""
        return self._right_padding_width
    def _set_right_padding_width(self, val):
        self._validate_option("right_padding_width", val)
        self._right_padding_width = val
    right_padding_width = property(_get_right_padding_width, _set_right_padding_width)

    def _get_vertical_char(self):
        """The charcter used when printing table borders to draw vertical lines

        Arguments:

        vertical_char - single character string used to draw vertical lines"""
        return self._vertical_char
    def _set_vertical_char(self, val):
        val = self._unicode(val)
        self._validate_option("vertical_char", val)
        self._vertical_char = val
    vertical_char = property(_get_vertical_char, _set_vertical_char)

    def _get_horizontal_char(self):
        """The charcter used when printing table borders to draw horizontal lines

        Arguments:

        horizontal_char - single character string used to draw horizontal lines"""
        return self._horizontal_char
    def _set_horizontal_char(self, val):
        val = self._unicode(val)
        self._validate_option("horizontal_char", val)
        self._horizontal_char = val
    horizontal_char = property(_get_horizontal_char, _set_horizontal_char)

    def _get_junction_char(self):
        """The charcter used when printing table borders to draw line junctions

        Arguments:

        junction_char - single character string used to draw line junctions"""
        return self._junction_char
    def _set_junction_char(self, val):
        val = self._unicode(val)
        self._validate_option("vertical_char", val)
        self._junction_char = val
    junction_char = property(_get_junction_char, _set_junction_char)

    def _get_format(self):
        """Controls whether or not HTML tables are formatted to match styling options

        Arguments:

        format - True or False"""
        return self._format
    def _set_format(self, val):
        self._validate_option("format", val)
        self._format = val
    format = property(_get_format, _set_format)

    def _get_attributes(self):
        """A dictionary of HTML attribute name/value pairs to be included in the <table> tag when printing HTML

        Arguments:

        attributes - dictionary of attributes"""
        return self._attributes
    def _set_attributes(self, val):
        self._validate_option("attributes", val)
        self._attributes = val
    attributes = property(_get_attributes, _set_attributes)

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
        self._hrules = FRAME
        self.padding_width = 1
        self.left_padding_width = 1
        self.right_padding_width = 1
        self.vertical_char = "|"
        self.horizontal_char = "-"
        self.junction_char = "+"

    def _set_msword_style(self):

        self.header = True
        self.border = True
        self._hrules = NONE
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
        self._hrules = random.choice((ALL, FRAME, NONE))
        self.left_padding_width = random.randint(0,5)
        self.right_padding_width = random.randint(0,5)
        self.vertical_char = random.choice("~!@#$%^&*()_+|-=\{}[];':\",./;<>?")
        self.horizontal_char = random.choice("~!@#$%^&*()_+|-=\{}[];':\",./;<>?")
        self.junction_char = random.choice("~!@#$%^&*()_+|-=\{}[];':\",./;<>?")

    ##############################
    # DATA INPUT METHODS         #
    ##############################

    def add_row(self, row):

        """Add a row to the table

        Arguments:

        row - row of data, should be a list with as many elements as the table
        has fields"""

        if self._field_names and len(row) != len(self._field_names):
            raise Exception("Row has incorrect number of values, (actual) %d!=%d (expected)" %(len(row),len(self._field_names)))
        if not self._field_names:
            self.field_names = [("Field %d" % (n+1)) for n in range(0,len(row))]
        self._rows.append(list(row))

    def del_row(self, row_index):

        """Delete a row to the table

        Arguments:

        row_index - The index of the row you want to delete.  Indexing starts at 0."""

        if row_index > len(self._rows)-1:
            raise Exception("Cant delete row at index %d, table only has %d rows!" % (row_index, len(self._rows)))
        del self._rows[row_index]

    def add_column(self, fieldname, column, align="c"):

        """Add a column to the table.

        Arguments:

        fieldname - name of the field to contain the new column of data
        column - column of data, should be a list with as many elements as the
        table has rows
        align - desired alignment for this column - "l" for left, "c" for centre and "r" for right"""

        if len(self._rows) in (0, len(column)):
            self._validate_align(align)
            self._field_names.append(fieldname)
            self._align[fieldname] = align
            for i in range(0, len(column)):
                if len(self._rows) < i+1:
                    self._rows.append([])
                self._rows[i].append(column[i])
        else:
            raise Exception("Column length %d does not match number of rows %d!" % (len(column), len(self._rows)))

    def clear_rows(self):

        """Delete all rows from the table but keep the current field names"""

        self._rows = []

    def clear(self):

        """Delete all rows and field names from the table, maintaining nothing but styling options"""

        self._rows = []
        self._field_names = []
        self._widths = []

    ##############################
    # MISC PUBLIC METHODS        #
    ##############################

    def copy(self):
        return copy.deepcopy(self)

    ##############################
    # MISC PRIVATE METHODS       #
    ##############################

    def _format_value(self, field, value):
        if isinstance(value, int) and field in self._int_format:
            value = self._unicode(("{0:" + self._int_format[field] + "}").format(value))
        elif isinstance(value, float) and field in self._float_format:
            value = self._unicode(("{0:" + self._float_format[field] + "}").format(value))
        return self._unicode(value)

    def _compute_widths(self, rows, options):
        if options["header"]:
            widths = [_get_size(field)[0] for field in self._field_names]
        else:
            widths = len(self.field_names) * [0]
        for row in rows:
            for index, value in enumerate(row):
                fieldname = self.field_names[index]
                if fieldname in self.max_width:
                    widths[index] = max(widths[index], min(_get_size(value)[0], self.max_width[fieldname]))
                else:
                    widths[index] = max(widths[index], _get_size(value)[0])
        self._widths = widths

    def _get_padding_widths(self, options):

        if options["left_padding_width"] is not None:
            lpad = options["left_padding_width"]
        else:
            lpad = options["padding_width"]
        if options["right_padding_width"] is not None:
            rpad = options["right_padding_width"]
        else:
            rpad = options["padding_width"]
        return lpad, rpad

    def _get_rows(self, options):
        """Return only those data rows that should be printed, based on slicing and sorting.

        Arguments:

        options - dictionary of option settings."""
       
	# Make a copy of only those rows in the slice range 
        rows = copy.deepcopy(self._rows[options["start"]:options["end"]])
        # Sort if necessary
        if options["sortby"]:
            sortindex = self._field_names.index(options["sortby"])
            # Decorate
            rows = [[row[sortindex]]+row for row in rows]
            # Sort
            rows.sort(reverse=options["reversesort"], key=options["sort_key"])
            # Undecorate
            rows = [row[1:] for row in rows]
        return rows
        
    def _format_row(self, row, options):
        return [self._format_value(field, value) for (field, value) in zip(self._field_names, row)]

    def _format_rows(self, rows, options):
        return [self._format_row(row, options) for row in rows]
 
    ##############################
    # PLAIN TEXT STRING METHODS  #
    ##############################

    def get_string(self, **kwargs):

        """Return string representation of table in current state.

        Arguments:

        start - index of first data row to include in output
        end - index of last data row to include in output PLUS ONE (list slice style)
        fields - names of fields (columns) to include
        header - print a header showing field names (True or False)
        border - print a border around the table (True or False)
        hrules - controls printing of horizontal rules after rows.  Allowed values: FRAME, ALL, NONE
	int_format - controls formatting of integer data
	float_format - controls formatting of floating point data
        padding_width - number of spaces on either side of column data (only used if left and right paddings are None)
        left_padding_width - number of spaces on left hand side of column data
        right_padding_width - number of spaces on right hand side of column data
        vertical_char - single character string used to draw vertical lines
        horizontal_char - single character string used to draw horizontal lines
        junction_char - single character string used to draw line junctions
        sortby - name of field to sort rows by
        sort_key - sorting key function, applied to data points before sorting
        reversesort - True or False to sort in descending or ascending order"""

        options = self._get_options(kwargs)

        lines = []

        # Don't think too hard about an empty table
        # Is this the desired behaviour?  Maybe we should still print the header?
        if self.rowcount == 0:
            return ""

	# Get the rows we need to print, taking into account slicing, sorting, etc.
        rows = self._get_rows(options)

	# Turn all data in all rows into Unicode, formatted as desired
        formatted_rows = self._format_rows(rows, options)

	# Compute column widths
        self._compute_widths(formatted_rows, options)

        # Add header or top of border
        self._hrule = self._stringify_hrule(options)
        if options["header"]:
            lines.append(self._stringify_header(options))
        elif options["border"] and options["hrules"] != NONE:
            lines.append(self._hrule)

        # Add rows
        for row in formatted_rows:
            lines.append(self._stringify_row(row, options))

        # Add bottom of border
        if options["border"] and not options["hrules"]:
            lines.append(self._hrule)
        
        return self._unicode("\n").join(lines)

    def _stringify_hrule(self, options):

        if not options["border"]:
            return ""
        lpad, rpad = self._get_padding_widths(options)
        bits = [options["junction_char"]]
        for field, width in zip(self._field_names, self._widths):
            if options["fields"] and field not in options["fields"]:
                continue
            bits.append((width+lpad+rpad)*options["horizontal_char"])
            bits.append(options["junction_char"])
        return "".join(bits)

    def _stringify_header(self, options):

        bits = []
        lpad, rpad = self._get_padding_widths(options)
        if options["border"]:
            if options["hrules"] != NONE:
                bits.append(self._hrule)
                bits.append("\n")
            bits.append(options["vertical_char"])
        for field, width, in zip(self._field_names, self._widths):
            if options["fields"] and field not in options["fields"]:
                continue
            if self._header_style == "cap":
                fieldname = field.capitalize()
            elif self._header_style == "title":
                fieldname = field.title()
            elif self._header_style == "upper":
                fieldname = field.upper()
            elif self._header_style == "lower":
                fieldname = field.lower()
            else:
                fieldname = field
            if self._align[field] == "l":
                bits.append(" " * lpad + fieldname.ljust(width) + " " * rpad)
            elif self._align[field] == "r":
                bits.append(" " * lpad + fieldname.rjust(width) + " " * rpad)
            else:
                bits.append(" " * lpad + fieldname.center(width) + " " * rpad)
            if options["border"]:
                bits.append(options["vertical_char"])
        if options["border"] and options["hrules"] != NONE:
            bits.append("\n")
            bits.append(self._hrule)
        return "".join(bits)

    def _stringify_row(self, row, options):
       
        for index, field, value, width, in zip(range(0,len(row)), self._field_names, row, self._widths):
            # Enforce max widths
            lines = value.split("\n")
            new_lines = []
            for line in lines: 
                if textual_width(line) > width:
                    line = textwrap.fill(line, width)
                new_lines.append(line)
            lines = new_lines
            value = "\n".join(lines)
            row[index] = value

        row_height = 0
        for c in row:
            h = _get_size(c)[1]
            if h > row_height:
                row_height = h

        bits = []
        lpad, rpad = self._get_padding_widths(options)
        for y in range(0, row_height):
            bits.append([])
            if options["border"]:
                bits[y].append(self.vertical_char)

        for field, value, width, in zip(self._field_names, row, self._widths):

            lines = value.split("\n")
            if len(lines) < row_height:
                lines = lines + ([""] * (row_height-len(lines)))

            y = 0
            for l in lines:
                if options["fields"] and field not in options["fields"]:
                    continue

                bits[y].append(" " * lpad + self._justify(l, width, self._align[field]) + " " * rpad)
                if options["border"]:
                    bits[y].append(self.vertical_char)

                y += 1

        
        if options["border"] and options["hrules"]== ALL:
            bits[row_height-1].append("\n")
            bits[row_height-1].append(self._hrule)

        for y in range(0, row_height):
            bits[y] = "".join(bits[y])

        return "\n".join(bits)

    ##############################
    # HTML STRING METHODS        #
    ##############################

    def get_html_string(self, **kwargs):

        """Return string representation of HTML formatted version of table in current state.

        Arguments:

        start - index of first data row to include in output
        end - index of last data row to include in output PLUS ONE (list slice style)
        fields - names of fields (columns) to include
        header - print a header showing field names (True or False)
        border - print a border around the table (True or False)
        hrules - controls printing of horizontal rules after rows.  Allowed values: FRAME, ALL, NONE
	int_format - controls formatting of integer data
	float_format - controls formatting of floating point data
        padding_width - number of spaces on either side of column data (only used if left and right paddings are None)
        left_padding_width - number of spaces on left hand side of column data
        right_padding_width - number of spaces on right hand side of column data
        sortby - name of field to sort rows by
        sort_key - sorting key function, applied to data points before sorting
        attributes - dictionary of name/value pairs to include as HTML attributes in the <table> tag"""

        options = self._get_options(kwargs)

        if options["format"]:
            string = self._get_formatted_html_string(options)
        else:
            string = self._get_simple_html_string(options)

        return string

    def _get_simple_html_string(self, options):

        lines = []

        open_tag = []
        open_tag.append("<table")
        if options["border"]:
            open_tag.append(" border=\"1\"")
        if options["attributes"]:
            for attr_name in options["attributes"]:
                open_tag.append(" %s=\"%s\"" % (attr_name, options["attributes"][attr_name]))
        open_tag.append(">")
        lines.append("".join(open_tag))

        # Headers
        if options["header"]:
            lines.append("    <tr>")
            for field in self._field_names:
                if options["fields"] and field not in options["fields"]:
                    continue
                lines.append("        <th>%s</th>" % escape(field).replace("\n", "<br />"))
            lines.append("    </tr>")

        # Data
        rows = self._get_rows(options)
        formatted_rows = self._format_rows(rows, options)
        for row in formatted_rows:
            lines.append("    <tr>")
            for field, datum in zip(self._field_names, row):
                if options["fields"] and field not in options["fields"]:
                    continue
                lines.append("        <td>%s</td>" % escape(datum).replace("\n", "<br />"))
            lines.append("    </tr>")

        lines.append("</table>")

        return self._unicode("\n").join(lines)

    def _get_formatted_html_string(self, options):

        lines = []
        lpad, rpad = self._get_padding_widths(options)

        open_tag = []
        open_tag.append("<table")
        if options["border"]:
            open_tag.append(" border=\"1\"")
        if options["hrules"] == NONE:
            open_tag.append(" frame=\"vsides\" rules=\"cols\"")
        if options["attributes"]:
            for attr_name in options["attributes"]:
                open_tag.append(" %s=\"%s\"" % (attr_name, options["attributes"][attr_name]))
        open_tag.append(">")
        lines.append("".join(open_tag))

        # Headers
        if options["header"]:
            lines.append("    <tr>")
            for field in self._field_names:
                if options["fields"] and field not in options["fields"]:
                    continue
                lines.append("        <th style=\"padding-left: %dem; padding-right: %dem; text-align: center\">%s</th>" % (lpad, rpad, escape(field).replace("\n", "<br />")))
            lines.append("    </tr>")

        # Data
        rows = self._get_rows(options)
        formatted_rows = self._format_rows(rows, options)
        aligns = []
        for field in self._field_names:
                aligns.append({ "l" : "left", "r" : "right", "c" : "center" }[self._align[field]])
        for row in formatted_rows:
            lines.append("    <tr>")
            for field, datum, align in zip(self._field_names, row, aligns):
                if options["fields"] and field not in options["fields"]:
                    continue
                lines.append("        <td style=\"padding-left: %dem; padding-right: %dem; text-align: %s\">%s</td>" % (lpad, rpad, align, escape(datum).replace("\n", "<br />")))
            lines.append("    </tr>")
        lines.append("</table>")

        return self._unicode("\n").join(lines)

##############################
# TABLE FACTORIES            #
##############################

def from_csv(fp, field_names = None):

    dialect = csv.Sniffer().sniff(fp.read(1024))
    fp.seek(0)
    reader = csv.reader(fp, dialect)

    table = PrettyTable()
    if field_names:
        table.field_names = field_names
    else:
        table.field_names = reader.next()

    for row in reader:
        table.add_row(row)

    return table

def from_db_cursor(cursor):

    table = PrettyTable()
    table.field_names = [col[0] for col in cursor.description]
    for row in cursor.fetchall():
        table.add_row(row)
    return table

##############################
# MAIN (TEST FUNCTION)       #
##############################

def main():

    x = PrettyTable(["City name", "Area", "Population", "Annual Rainfall"])
    x.sortby = "Population"
    x.reversesort = True
    x.int_format["Area"] = "04d"
    x.float_format = "6.1f"
    x.align["City name"] = "l" # Left align city names
    x.add_row(["Adelaide", 1295, 1158259, 600.5])
    x.add_row(["Brisbane", 5905, 1857594, 1146.4])
    x.add_row(["Darwin", 112, 120900, 1714.7])
    x.add_row(["Hobart", 1357, 205556, 619.5])
    x.add_row(["Sydney", 2058, 4336374, 1214.8])
    x.add_row(["Melbourne", 1566, 3806092, 646.9])
    x.add_row(["Perth", 5386, 1554769, 869.4])
    print(x)
    
if __name__ == "__main__":
    main()

#
# Copyright (c) 2010 Red Hat, Inc.
# Copyright (c) 2010 Ville Skyttä
# Copyright (c) 2009 Tim Lauridsen
# Copyright (c) 2007 Marcus Kuhn
#
# kitchen is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# kitchen is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
# more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with kitchen; if not, see <http://www.gnu.org/licenses/>
#
# Authors:
#   James Antill <james@fedoraproject.org>
#   Marcus Kuhn
#   Toshio Kuratomi <toshio@fedoraproject.org>
#   Tim Lauridsen
#   Ville Skyttä
#
# Portions of this are from yum/i18n.py


def _interval_bisearch(value, table):
    minimum = 0
    maximum = len(table) - 1
    if value < table[minimum][0] or value > table[maximum][1]:
        return False

    while maximum >= minimum:
        mid = (minimum + maximum) / 2
        if value > table[mid][1]:
            minimum = mid + 1
        elif value < table[mid][0]:
            maximum = mid - 1
        else:
            return True

    return False

_COMBINING = (
        (0x300, 0x36f), (0x483, 0x489), (0x591, 0x5bd),
        (0x5bf, 0x5bf), (0x5c1, 0x5c2), (0x5c4, 0x5c5),
        (0x5c7, 0x5c7), (0x600, 0x603), (0x610, 0x61a),
        (0x64b, 0x65e), (0x670, 0x670), (0x6d6, 0x6e4),
        (0x6e7, 0x6e8), (0x6ea, 0x6ed), (0x70f, 0x70f),
        (0x711, 0x711), (0x730, 0x74a), (0x7a6, 0x7b0),
        (0x7eb, 0x7f3), (0x816, 0x819), (0x81b, 0x823),
        (0x825, 0x827), (0x829, 0x82d), (0x901, 0x902),
        (0x93c, 0x93c), (0x941, 0x948), (0x94d, 0x94d),
        (0x951, 0x954), (0x962, 0x963), (0x981, 0x981),
        (0x9bc, 0x9bc), (0x9c1, 0x9c4), (0x9cd, 0x9cd),
        (0x9e2, 0x9e3), (0xa01, 0xa02), (0xa3c, 0xa3c),
        (0xa41, 0xa42), (0xa47, 0xa48), (0xa4b, 0xa4d),
        (0xa70, 0xa71), (0xa81, 0xa82), (0xabc, 0xabc),
        (0xac1, 0xac5), (0xac7, 0xac8), (0xacd, 0xacd),
        (0xae2, 0xae3), (0xb01, 0xb01), (0xb3c, 0xb3c),
        (0xb3f, 0xb3f), (0xb41, 0xb43), (0xb4d, 0xb4d),
        (0xb56, 0xb56), (0xb82, 0xb82), (0xbc0, 0xbc0),
        (0xbcd, 0xbcd), (0xc3e, 0xc40), (0xc46, 0xc48),
        (0xc4a, 0xc4d), (0xc55, 0xc56), (0xcbc, 0xcbc),
        (0xcbf, 0xcbf), (0xcc6, 0xcc6), (0xccc, 0xccd),
        (0xce2, 0xce3), (0xd41, 0xd43), (0xd4d, 0xd4d),
        (0xdca, 0xdca), (0xdd2, 0xdd4), (0xdd6, 0xdd6),
        (0xe31, 0xe31), (0xe34, 0xe3a), (0xe47, 0xe4e),
        (0xeb1, 0xeb1), (0xeb4, 0xeb9), (0xebb, 0xebc),
        (0xec8, 0xecd), (0xf18, 0xf19), (0xf35, 0xf35),
        (0xf37, 0xf37), (0xf39, 0xf39), (0xf71, 0xf7e),
        (0xf80, 0xf84), (0xf86, 0xf87), (0xf90, 0xf97),
        (0xf99, 0xfbc), (0xfc6, 0xfc6), (0x102d, 0x1030),
        (0x1032, 0x1032), (0x1036, 0x1037), (0x1039, 0x103a),
        (0x1058, 0x1059), (0x108d, 0x108d), (0x1160, 0x11ff),
        (0x135f, 0x135f), (0x1712, 0x1714), (0x1732, 0x1734),
        (0x1752, 0x1753), (0x1772, 0x1773), (0x17b4, 0x17b5),
        (0x17b7, 0x17bd), (0x17c6, 0x17c6), (0x17c9, 0x17d3),
        (0x17dd, 0x17dd), (0x180b, 0x180d), (0x18a9, 0x18a9),
        (0x1920, 0x1922), (0x1927, 0x1928), (0x1932, 0x1932),
        (0x1939, 0x193b), (0x1a17, 0x1a18), (0x1a60, 0x1a60),
        (0x1a75, 0x1a7c), (0x1a7f, 0x1a7f), (0x1b00, 0x1b03),
        (0x1b34, 0x1b34), (0x1b36, 0x1b3a), (0x1b3c, 0x1b3c),
        (0x1b42, 0x1b42), (0x1b44, 0x1b44), (0x1b6b, 0x1b73),
        (0x1baa, 0x1baa), (0x1c37, 0x1c37), (0x1cd0, 0x1cd2),
        (0x1cd4, 0x1ce0), (0x1ce2, 0x1ce8), (0x1ced, 0x1ced),
        (0x1dc0, 0x1de6), (0x1dfd, 0x1dff), (0x200b, 0x200f),
        (0x202a, 0x202e), (0x2060, 0x2063), (0x206a, 0x206f),
        (0x20d0, 0x20f0), (0x2cef, 0x2cf1), (0x2de0, 0x2dff),
        (0x302a, 0x302f), (0x3099, 0x309a), (0xa66f, 0xa66f),
        (0xa67c, 0xa67d), (0xa6f0, 0xa6f1), (0xa806, 0xa806),
        (0xa80b, 0xa80b), (0xa825, 0xa826), (0xa8c4, 0xa8c4),
        (0xa8e0, 0xa8f1), (0xa92b, 0xa92d), (0xa953, 0xa953),
        (0xa9b3, 0xa9b3), (0xa9c0, 0xa9c0), (0xaab0, 0xaab0),
        (0xaab2, 0xaab4), (0xaab7, 0xaab8), (0xaabe, 0xaabf),
        (0xaac1, 0xaac1), (0xabed, 0xabed), (0xfb1e, 0xfb1e),
        (0xfe00, 0xfe0f), (0xfe20, 0xfe26), (0xfeff, 0xfeff),
        (0xfff9, 0xfffb), (0x101fd, 0x101fd), (0x10a01, 0x10a03),
        (0x10a05, 0x10a06), (0x10a0c, 0x10a0f), (0x10a38, 0x10a3a),
        (0x10a3f, 0x10a3f), (0x110b9, 0x110ba), (0x1d165, 0x1d169),
        (0x1d16d, 0x1d182), (0x1d185, 0x1d18b), (0x1d1aa, 0x1d1ad),
        (0x1d242, 0x1d244), (0xe0001, 0xe0001), (0xe0020, 0xe007f),
        (0xe0100, 0xe01ef), )

def _ucp_width(ucs, control_chars='guess'):
    # test for 8-bit control characters

    # Don't understand why but this is needed for Python 3
    ucs = ucs[0]

    if (ucs < 32) or ((ucs < 0xa0) and (ucs >= 0x7f)):
        # Control character detected
        if control_chars == 'strict':
            raise ControlCharError(b_('_ucp_width does not understand how to'
                ' assign a width value to control characters.'))
        if ucs in (0x08, 0x07F, 0x94):
            # Backspace, delete, and clear delete remove a single character
            return -1
        if ucs == 0x1b:
            # Excape is tricky.  It removes some number of characters that
            # come after it but the amount is dependent on what is
            # interpreting the code.
            # So this is going to often be wrong but other values will be
            # wrong as well.
            return -1
        # All other control characters get 0 width
        return 0

    if _interval_bisearch(ucs, _COMBINING):
        # Combining characters return 0 width as they will be combined with
        # the width from other characters
        return 0

    # if we arrive here, ucs is not a combining or C0/C1 control character

    return (1 +
      (ucs >= 0x1100 and
       (ucs <= 0x115f or                     # Hangul Jamo init. consonants
        ucs == 0x2329 or ucs == 0x232a or
        (ucs >= 0x2e80 and ucs <= 0xa4cf and
         ucs != 0x303f) or                   # CJK ... Yi
        (ucs >= 0xac00 and ucs <= 0xd7a3) or # Hangul Syllables
        (ucs >= 0xf900 and ucs <= 0xfaff) or # CJK Compatibility Ideographs
        (ucs >= 0xfe10 and ucs <= 0xfe19) or # Vertical forms
        (ucs >= 0xfe30 and ucs <= 0xfe6f) or # CJK Compatibility Forms
        (ucs >= 0xff00 and ucs <= 0xff60) or # Fullwidth Forms
        (ucs >= 0xffe0 and ucs <= 0xffe6) or
        (ucs >= 0x20000 and ucs <= 0x2fffd) or
        (ucs >= 0x30000 and ucs <= 0x3fffd))))

def textual_width(msg, control_chars='guess', encoding='utf-8',
        errors='replace'):

    return sum(
            # calculate width of each char
            itermap(_ucp_width,
                # Setup the arguments to _ucp_width
                iterzip(
                    # int value of each char
                    itermap(ord, msg),
                    # control_chars arg in a form that izip will deal with
                    itertools.repeat(control_chars))))
