#!/usr/bin/env python3
"""This module will convert a .csv file into an html table. It can be imported or run like a command in bash"""
import _io
import sys
import csv
import copy
import argparse


class WorkingTable:
    """represents a chunk of csv data as an html table

        Attributes
        headers: list of strings
            the csv headers. Will be written with the <th> tags. Superfluous
            headers will be ignored. Empty headers will be written as a single space.

        rows: array of strings
            the array of cells representing the csv file data.

        table: list of strings
            the html output of the loaded csv file.

        Methods
        save(filename: str, overwrite=False):
            save the current table attribute to the specified filepath. Expects a
            relative filepath in string form. Does not handle exceptions.

            If the overwrite value is True, it will overwrite an existing file.
            Otherwise, it will return an exception.

        add_html():
            update the table attribute to be wrapped in <!DOCTYPE html>, <html> and <body> tags.
    """
    def __init__(self, csvdata: _io.TextIOWrapper, getheaders=False, headerlist=None):
        """
        create a WorkingTable with csv data. A WorkingTable contains an html style table.
        :param csvdata: can be a file stream or stdin input. Expects .readlines() to work
        :param getheaders: If true, the first row of the input will be read as a header
        :param headerlist: sets the headers attribute. Overwrites the stream header, if any.

        You must pass an open file or other stdin like object. This class does not handle any
        exceptions.
        """

        self.headers: list[str]      # csv headers
        self.rows = list[list[str]]  # csv rows
        self.table: list[str]        # html table for output

        if csvdata.readable():
            csvreader = csv.reader(csvdata, skipinitialspace=True)
            self.rows = []
            if getheaders is True:
                self.headers = next(csvreader)
            else:
                self.headers = None
            self.rows.extend(csvreader)
        else:
            self.rows = None

        if headerlist is not None:
            self.headers = copy.copy(headerlist)

        if len(self.rows) > 0:
            self.__parse__()
        else:
            self.headers = None
            self.rows = None
            self.table = None

    def __parse__(self):
        self.table = None  # initialize in case self.rows is empty

        # check that the data isn't empty
        if self.rows is None:
            return
        if len(self.rows) < 1:
            return
        columns = len(self.rows[0])  # use number of columns to make the headers match up
        if columns < 1:
            return

        # align the headers with columns
        if self.headers is not None:
            aligned_headers = []
            for i in range(columns):  # if too many headers, ignore the extras
                if i < len(self.headers):
                    aligned_headers.append(self.headers[i])
                else:
                    aligned_headers.append(" ")  # if too few headers, put an empty header for each column
            self.headers = aligned_headers
        else:
            self.headers = None

        # begin writing the table
        self.table = ["<table>\n"]

        if self.headers is not None:
            self.table.append("\t<tr>\n")
            for header in self.headers:
                self.table.append("\t\t<th>" + header + "</th>\n")
            self.table.append("\t</tr>\n")

        for row in self.rows:
            self.table.append("\t<tr>\n")
            for cell in row:
                self.table.append("\t\t<td>" + cell + "</td>\n")
            self.table.append("\t</tr>\n")

        self.table.append("</table>\n")

    def add_html(self):
        """
        add the <!DOCTYPE html> tag and <html>/<body> wrappers to the table
        If table is None it won't add anything
        :return: none
        """
        if self.table is None:
            return

        self.table.insert(0, "<body>\n")
        self.table.insert(0, "<html>\n")
        self.table.insert(0, "<!DOCTYPE html>\n")
        self.table.append("</body>\n")
        self.table.append("</html>\n")


def main():
    """
    The command-line utility for csvtable. Reads arguments from sys.argv
    :return: will exit with sys.exit()
    """
    parser = argparse.ArgumentParser(description="convert a .csv file into an .html table")
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin, help="Input file. Uses stdin otherwise")
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout, help="Output file. Uses stdout otherwise")
    parser.add_argument("-b", "--browser", help="wrap the output in browser-friendly tags",
                        action="store_true")
    parser.add_argument("-r", "--read", help="Read the first row as file headers",
                        action="store_true")
    args = parser.parse_args()

    my_table = WorkingTable(args.infile, args.read, None)
    if args.browser:
        my_table.add_html()

    if my_table.table is not None:
        args.outfile.writelines(my_table.table)


if __name__ == "__main__":
    main()
