from __future__ import print_function

import numpy as np
from numpy import char
from os.path import isfile
from six import string_types
import sys

# Python 2/3 compatibility
if sys.version_info[0] == 2:
    from itertools import izip as zip
    range = xrange


def dict(filename, cols=None, dtype=float, include=None, exclude='#',
         delimiter='', removechar='#', hmode='1', header_start=1,
         data_start=0, hsep='', lower=False):
    """
    Creates a dictionary in which each chosen column in the file is an
    element of the dictionary, where keys correspond to column names.

    Uses the functions header and table to create a dictionary with the
    columns of the file (see each function's help).

    The file must have a header in which all column names are given.

    """
    if isinstance(cols, string_types) or isinstance(cols, int):
        cols = (cols,)
    full_output = False
    if cols is not None:
        if isinstance(cols[0], string_types):
            full_output = True
    head = header(filename, cols=cols, removechar=removechar, hmode=hmode,
                  header_start=header_start, hsep=hsep, lower=lower,
                  full_output=full_output)
    if full_output:
        head, cols = head
    data = table(filename, cols=cols, dtype=dtype, include=include,
                 exclude=exclude, data_start=data_start, delimiter=delimiter)
    if isinstance(data, np.ndarray):
        if len(data.shape) == 1:
            dic = {head[0]: data}
        else:
            dic = {head[0]: data[0]}
            for i in range(1, len(head)):
                dic[head[i]] = data[i]
    else:
        dic = {head[0]: data[0]}
        for i in range(1, len(head)):
            dic[head[i]] = data[i]
    return dic


def format_fmt(fmt, delimiter, n=1):
    """
    Give a formatting string the correct Python 3.x-style format, and
    prepare it to be ready to use by save()

    Parameters
    ----------
        fmt     : str or list of str
                  Original format string in Python 2 format, which may
                  be a single format string, or multiple space-
                  separated format strings, or a list of format
                  strings.
        delimiter : str
                  String to use as delimiter in the string to which
                  this format will be applied.

    Optional parameters
    -------------------
        n       : int
                  if `fmt` is a single format string, then `fmt` will
                  be repeated `n` times (changing the index to follow
                  Python 3 syntax).

    Returns
    -------
        fmt3    : str
                  The final format string, in Python 3 style, separated
                  by `delimiter`, which can be directly applied to the
                  corresponding list of elements.

    Examples
    --------
        # multiple formats
        >>> format_fmt('%s %4.1f', ' | ')
        '{0:s} | {1:4.1f}'
        # single format with repetition
        >>> format_fmt('%.3e', ' ', n=3)
        '{0:.3e} {1:.3e} {2:.3e}'

    """
    if isinstance(fmt, string_types):
        fmt = fmt.split()
    # is it Python 2 or 3 style?
    style = '2' if '%' in fmt[0] else '3'
    # if it comes in Python2 style
    if style == '2' and len(fmt) == 1:
        fmt = fmt[0].replace('%', '')
        fmt3 = ['{{{0}:{1}}}'.format(i, fmt) for i in range(n)]
    elif style == '2':
        fmt3 = ['{{{0}:{1}}}'.format(i[0], i[1].replace('%', ''))
                for i in enumerate(fmt)]
    # if it comes in Python3 style
    return delimiter.join(fmt3)


def header(filename, cols=None, removechar='#', hmode='1', header_start=0,
           hsep='', lower=False, strip=True, full_output=False):
    """
    Returns the header of the file, which can be defined in various
    ways.

    Parameters
    ----------
    filename : str
        Name of the file.
    cols : int/str or list of int/str
        Columns wanted in the output, either by number or by name
        (numbered starting at 0). If not specified, all columns will be
        returned.
    removechar : str
        Character(s) to be removed from the first line, not part of
        the header. If `hmode='1'` and `header_start=0` then the header will
        be the first line in the file starting with `removechar`. If
        `hmode='2'` then all lines starting with `removechar` will be
        considered part of the header.
    hmode : {'1', '2'}
        How the header is defined. `hmode='1'` means column names are
        given in the first line, separated by spaces; `hmode='2'` means
        they are given in separate lines at the top of the file with
        column numbers, as in SExtractor outputs. Note that the latter
        headers usually enumerate the columns starting from 1, which is
        corrected here to the python convention. See below for further
        explanation.
    header_start : int
        The line number in which the header is located (count starts at
        0). If `header_start=0` and `hmode='1'`, the header is assumed to be
        the first line starting with `removechar`. If `hmode=='2'`,
        then this is used as the column number containing the names of
        the data columns.
    hsep : char
        Separator between column names. Typically <space> (default) or
        <comma>. Used only in `hmode=1`.
    lower: boole
        whether to return all column names in lower case.
    strip : bool
        If `True`, remove leading and trailing spaces from all string
        elements.
    full_output: bool
        if `True`, return the column numbers as well. Useful when the
        columns are defined from their names.

    Returns
    -------
    header : a list or numpy.ndarray with the desired column names


    THE `hmode` PARAMETER
    --------------------

        Definitions
        -----------
            `hmode=1`
        Single-line header given in line number `header_start`. The header
        line may start with any comment character which is specified in
        `removechar`. Column names are separated by `hsep`. If
        starting with `removechar`. `header_start=0`, the header will be
        assumed to be the first line.
            `hmode=2`
        Column names are given in separate lines with explanations, each of
        which starts with a `'#'`, similar to the display of a FITS file header.
        Used, for instance, by SExtractor.
            `hmode=3`
        ApJ table format. File header contains a "byte-by-byte" description
        of the columns. No hcashtags need to be present, but readfile can
        handle them if they are. NOT YET IMPLEMENTED

        Examples
        --------
        hmode=1
        Examples for different formats:
            removechar='#' :
            # ID  RA  Dec  redshift  mag_r
            removechar = '|' , sep = '|' :
            | ID | RA | Dec | redshift | mag_r |

        hmode=2
        # 1   ID                Unique object identification
        # 2   RA                J2000 Right Ascension (deg)
        # 3   Dec               J2000 Declination (deg)
        # 4   redshift          Object redshift
        # 5   mag_r             Aperture magnitude in the r band (mag)

        hmode=3
        ...


    NOTES
    -----

        All leading and trailing spaces are removed from column names.

    """
    if isinstance(cols, int) or isinstance(cols, string_types):
        cols = [cols]

    if cols is not None:
        tp = type(cols[0])
        cols_items_are_str = isinstance(cols[0], string_types)
        cols_items_are_int = isinstance(cols[0], int)
        if not (cols_items_are_int or cols_items_are_str):
            raise TypeError(
                f'wrong type in cols ({tp}), must be either str or int')
        for c in cols:
            if type(c) != tp:
                msg = 'All elements of cols must be of the same type'
                raise ValueError(msg)
        if cols_items_are_str:
            colnums = []
    if removechar not in (False, None):
        if not isinstance(removechar, string_types):
            raise TypeError('wrong type for removechar, should be a string')

    head = []
    # horizontal header
    if hmode == '1':
        file = open(filename)
        if header_start > 0:
            for i in range(header_start-1):
                head = file.readline()
        head = file.readline().strip()
        if removechar:
            head = head.strip(removechar)
        file.close()
        # remove line breaks and spaces before splitting
        head = head.strip()
        if len(hsep) == 0:
            head = head.split()
        else:
            head = head.split(hsep)
        # select columns
        if cols is not None:
            if cols_items_are_str:
                colnums = np.array(
                    [i for i, h in enumerate(head) if h in cols])
                head = [h for h in head if h in cols]
            else:
                head = [h for i, h in enumerate(head) if i in cols]

    # vertical header
    elif hmode == '2':
        if not removechar:
            msg = "ERROR: when setting hmode='2' must include removechar"
            print(msg)
            exit()
        data = table(filename, cols=2, dtype=str, include=removechar)
        # column numbers
        num  = range(len(data))
        # column names
        name = list(data)
        if cols is None:
            head = name
        else:
            head = []
            if cols_items_are_str:
                head = [i for i in cols if i in name]
                colnums = np.array([name.index(i) for i in cols if i in name])
            else:
                head = [name_i for name_i, num_i in zip(name, num)
                        if num_i-1 in cols]
            head = np.array(head, dtype=str)

    if lower:
        head = np.array([h.lower() for h in head])

    # remove leading and trailing spaces from each column name
    if strip:
        for i, h in enumerate(head):
            if len(h) == 0:
                continue
            head = char.strip(head, ' ')

    if cols is not None:
        if cols_items_are_int:
            colnums = cols
    if full_output:
        return head, colnums
    return head


def save(output, data, delimiter='  ', fmt='%s', header='', overwrite=True,
         append=False, verbose=True):
    """
    Save output file

    Parameters
    ----------
    output : str
        Name of the output file
    data : 2-d array
    fmt : string of space-separated formats (compatible with both
        Python 2.x and 3.x)
    header : str
    overwrite : `bool`
        Whether to overwrite the file if it exists
    append : bool
        If the file exists, whether to append information at the end.
        Overrides `overwrite`.
    verbose : bool

    """
    # does the output exist?
    if isfile(output) and not overwrite:
        msg = 'File {0} already exists. Skipping.'.format(output)
        print(msg)
        return
    ncols = len(data)
    # do all the columns have the same length?
    if hasattr(data[0], '__iter__'):
        nrows = len(data[0])
        for i, column in enumerate(data):
            if len(column) != nrows:
                msg = 'All columns must have the same length.'
                msg += ' Column lengths: {0}'.format([len(c) for c in data])
                raise ValueError(msg)
    # append or overwrite
    if isfile and append:
        out = open(output, 'a')
    else:
        out = open(output, 'w')
    fmt = format_fmt(fmt, delimiter, n=ncols)
    # save file! start with the header
    if len(header) > 0:
        print(header, file=out)
    for i in zip(*data):
        print(fmt.format(*i), file=out)
    out.close()
    if verbose:
        print('Saved file {0}'.format(output))
    return


def table(filename, cols=None, dtype=float, exclude='#', include=None,
          data_start=0, delimiter=None, whole=False, force_array=False,
          strip=True):
    """
    Returns a table with all the data in a file. Each column is
    returned as a numpy array.

    Parameters
    ----------
    filename : str
        Name of the file

    Optional parameters
    -------------------
    cols : int or list of ints
        Columns wanted in the output (numbered starting at 0). If the
        file has columns that do not have data in one or more rows,
        only columns before those can be included.
    dtype : type or list of types
        A generic type for all columns or a type for each of the
        columns in `cols`. If `dtype` is a list of types, then it must
        be of the same length of `cols`, or its length equal to the
        number of columns in the file if `cols=None`. If a character
        cannot be converted to the desired type, the elements in the
        corresponding column will be strings.
    exclude : str or list of strings
        Comment character(s), of any length. Lines starting with (any
        of the elements of) `exclude` are not considered for the table.
    include : str or list of strings
        Lines to be included in the table must start with (any of the
        elements of) `include`, (each of which) can be of any length.
        If given, `include` overrides `exclude`. It cannot have any
        spaces, and leading spaces in the file are ignored.
    data_start : int
        line number at which to start recording data. Note that
        commented lines are counted but excluded lines are not. Ignored
        if `include` is defined.
    delimiter : str
        Separator beween lines. Can be a string of any length.
    whole : bool
        If `True`, the string or strings given in `include` or `exclude`
        are taken into account only if they are a full string, i.e.,
        there is a `delimiter` character right after it.
    force_array : bool
        If `True`, each column is returned as an array even if the
        length of the column or row is one. This is useful if you are
        automatically dealing with arrays; by setting this, you always
        get the same format. By default, when each column or row has
        length 1, `table()` returns a single array with all the
        selected elements of the row/column.

    Returns
    -------
    data : a list containing the selected columns in the file, each
        with the specified type.
    """
    if isinstance(cols, int) or isinstance(cols, string_types):
        cols = [cols]
    elif cols is not None and not hasattr(cols, '__iter__'):
        err = 'cols must be int, str or list of either (received' \
             f' {type(cols)})'
        raise TypeError(err)
    if isinstance(dtype, type):
        dtype = [dtype]

    if isinstance(include, string_types):
        include = [include]
    if isinstance(exclude, string_types):
        exclude = [exclude]

    with open(filename) as file:
        data = (_read_single_line(line, delimiter, cols, include,
                                  exclude, whole=whole, strip=strip)
                for line in file)
        data = [i for i in data if i is not None]
    # transpose. Numpy doesn't preserve object type so must do manually
    data = [[i[j] for i in data]
            for j in range(len(data[0]))]
    #return data
    # now convert to numpy array one by one with the requested type
    if dtype is None:
        for i, col in enumerate(data):
            try:
                data[i] = np.array(col, dtype=float)
            except ValueError:
                try:
                    data[i] = np.array(col, type=int)
                except ValueError:
                    data[i] = np.array(col)
    else:
        if len(dtype) == 1:
            dtype = len(data) * dtype
        else:
            assert len(data) == len(dtype), \
                f'number of dtypes ({len(dtype)}) different from number of' \
                f' columns ({len(data)})'
        for i, (col, tp) in enumerate(zip(data, dtype)):
            try:
                data[i] = np.array(col, dtype=tp)
            except ValueError:
                msg = f'column {i} cannot be converted to type {tp}'
                raise ValueError(msg)
    return data


def _read_single_line(line, delimiter, cols, include=None, exclude=None,
                      whole=False, strip=True):
    if strip:
        line = line.strip()
    words = line.split(delimiter)
    # only register lines listed in ``include``
    if include is not None:
         if whole and words[0] not in include:
            return
         elif not sum([(line[:len(i)] == i) for i in include]):
            return
    # discard lines listed in ``exclude``
    if exclude is not None:
        if whole and words[0] in exclude:
            return
        elif sum([(line[:len(e)] == e) for e in exclude]):
            return
    # make cols a list of length len(line)
    if cols is None:
        cols = range(len(words))
    elif len(cols) == 1:
        cols = len(words) * cols
    line_data = [words[col] for col in cols]
    return line_data
