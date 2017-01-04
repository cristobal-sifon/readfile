readfile
========

Flexible python module to read ascii files as either tables or dictionaries. The user can provide either the index or the names (if given in the file) of specific columns to return, each column's data type, and lines starting with what character(s) to include or exclude. A full description can be found in the python help pages of the modules.

This module contains four functions:

    header(filename, **kwargs)
returns the header of a file as a list of strings.

    table(filename, **kwargs)
returns the data in the file, where each column is a numpy array.

    dict(filename, **kwargs)
a wrapper of the previous two, where the data is a dictionary with the keys being column names and the corresponding data.

    save(filename, data, **kwargs)
store data to a file. Similar to `numpy.savetxt()` but supports lists with elements of multiple types.