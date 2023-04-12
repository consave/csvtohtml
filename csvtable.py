"""This module will convert a .csv file into an html table. It can be imported or run like a command in bash"""

import sys
import csv
import os
import copy


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
    def __init__(self, filename=None, getheaders=False, rowarray=None, headerlist=None):
        """
        create a WorkingTable with csv data. A WorkingTable contains an html style table.
        :param filename: If defined, reads the specified csv file as input
        :param getheaders: If true, the first row of the csv file will be used as a header.
        :param rowarray: an array of strings representing a csv. Extends the read file data, if any.
        :param headerlist: sets the headers attribute. Overwrites the read file data, if any.

        You can specify a file to read, pass the data directly as an array, or both. If no row
        data is passed, all attributes will be set to None.

        This method does not handle file exceptions and should be placed in a Try/Except block.
        """

        self.headers: list[str]     # csv headers
        self.rows: list[list[str]]  # csv rows
        self.table: list[str]       # html table for output

        if type(filename) == str:
            with open(filename, newline='') as file:
                csvreader = csv.reader(file)
                if getheaders is True:
                    self.headers = csvreader.__next__()
                else:
                    self.headers = None
                for row in csvreader:
                    self.rows.append(row)
            file.close()
        else:
            self.rows = [[]]  # gives this a .len and .extend() property

        if type(rowarray) == list[list[str]]:
            self.rows.extend(copy.deepcopy(rowarray))

        if type(headerlist) == list[str]:
            self.headers = copy(headerlist)

        if self.rows.len > 0:
            self.__parse__()
        else:
            self.headers = None
            self.rows = None
            self.table = None

    def save(self, filename, overwrite=False):
        """
        save the current table to a file. This method doesn't handle file exceptions
        and should be placed in a Try/Except block.
        :param filename: The name of the file to be written
        :param overwrite: If false, raise a FileExistsError exception rather than overwrite.
        :return: none

        if table is None (because no data was loaded) it will try to write an empty file
        """
        if overwrite is False and os.path.exists(filename):
            raise FileExistsError

        with open(filename, 'w') as file:
            if self.table is None:
                file.close()
                return
            file.writelines(self.table)

    def __parse__(self):
        self.table = None  # initialize in case self.rows is empty

        # check that the data isn't empty
        if self.rows is None:
            return
        if self.rows.len < 1:
            return
        columns = self.rows[0].len  # use number of columns to make the headers match up
        if columns < 1:
            return

        # align the headers with columns
        if type(self.headers) == list[str]:
            aligned_headers = []
            for i in range(columns):  # if too many headers, ignore the extras
                if i < self.headers.len:
                    aligned_headers.append(self.headers[i])
                else:
                    aligned_headers.append(" ")  # if too few headers, put an empty header for each column
            self.headers = aligned_headers
        else:
            self.headers = None

        # begin writing the table
        self.table = ["<table>"]

        if self.headers is not None:
            self.table.append("\t<tr>")
            for header in self.headers:
                self.table.append("\t\t<th>" + header + "</th>")
            self.table.append("\t</tr>")

        for row in self.rows:
            self.table.append("\t<tr>")
            for cell in row:
                self.table.append("\t\t<td>" + cell + "</td>")
            self.table.append("\t</tr>")

        self.table.append("</table>")

    def add_html(self):
        """
        add the <!DOCTYPE html> tag and <html>/<body> wrappers to the table
        If table is None it won't add anything
        :return: none
        """
        if self.table is None:
            return

        self.table.insert("<body>", 0)
        self.table.insert("<html>", 0)
        self.table.insert("<!DOCTYPE html>", 0)
        self.table.append("</body>")
        self.table.append("</html>")


def quick_convert(filename: str) -> list[str]:  # TODO: implement this
    """quickly convert the passed file into html table form"""
    pass


def main():
    """
    NAME
        csvtable.py - converts a .csv file or stream into an .html format

    SYNOPSIS
        csvtable.py [-h] [-w=<filename>] [file ...]

    DESCRIPTION
        This will convert a .csv file into an .html <table> format. By default, it will input
        and output from and to the standard streams.

        The following options are available:

        -h
            This will wrap the output in <html> and <body> tags to make the output viewable in a browser.

        -w=<filename>
            Write the output to the specified filename instead of printing it.

    EXAMPLES
        The command:
            csvtable.py -h -w=file1.html file1.csv

        will convert the contents of file1.csv and write them to file1.html with the <html> and <body> tags.

        The command:
            tail file1.csv | csvtable.py >> file1.html

        will take the output of "tail file1.csv" and append it to file1.html as just a <table>
            """
    addhtml = False
    writefile = None
    readfile = None
    for argument in sys.argv:
        if argument == "-h":
            addhtml = True
        elif argument[0:2] == "-w=":
            writefile = argument[3:]
        else:
            if readfile is not None:
                sys.stderr.write("csvtable.py ERROR: unexpected argument: " + argument)
                return
            readfile = argument

    if readfile is not None:
        if os.path.isfile(readfile) is False:
            sys.stderr.write("csvtable.py ERROR: \'" + readfile + "\' could not be found")
            return
        rowdata = None
    elif sys.stdin.isatty() is False:
        sys.stderr.write("csvtable.py ERROR: no input given")
        return
    else:
        rowdata = sys.stdin

    my_table = WorkingTable(readfile, False, rowdata, None)

    if writefile is not None:  # TODO: exception handling
        my_table.save(writefile, True)
    else:
        sys.stdout.writelines(my_table.table)


if __name__ == "__main__":
    main()
