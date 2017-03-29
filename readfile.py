# -*- coding: utf-8 -*-
from __future__ import print_function

from itertools import count
from numpy import array, char, ndarray
from os.path import isfile

# Python 2/3 compatibility issues
try: # Python 2.x
    from itertools import izip as zip
    range = xrange
except ImportError: # Python 3.x
    basestring = str


def dict(filename, cols=None, dtype=float, include=None, exclude='#',
         delimiter='', removechar='#', hmode='1', linenum=1,
         hsep='', lower=False):
    """
    Creates a dictionary in which each chosen column in the file is an
    element of the dictionary, where keys correspond to column names.

    Uses the functions header and table to create a dictionary with the
    columns of the file (see each function's help).

    The file must have a header in which all column names are given.

    """
    if isinstance(cols, basestring) or isinstance(cols, int):
        cols = (cols,)
    full_output = False
    if cols is not None:
        if isinstance(cols[0], basestring):
            full_output = True
    head = header(filename, cols=cols, removechar=removechar,
                    hmode=hmode, linenum=linenum, hsep=hsep, lower=lower,
                    full_output=full_output)
    if full_output:
        head, cols = head
    data = table(filename, cols=cols, dtype=dtype, include=include,
                 exclude=exclude, delimiter=delimiter)
    if type(data) == ndarray:
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
                  Original format string, which may be in either Python
                  2 or 3 format, and may be a single format string, or
                  multiple space-separated format strings, or a list of
                  format strings.
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
                  The final format string, separated by `delimiter`,
                  which can be directly applied to the corresponding
                  list of elements

    Examples
    --------
        # multiple formats
        >>>

    """
    if isinstance(fmt, basestring):
        fmt = fmt.split()
    # is it Python 2 or 3 style?
    style = '2' if '%' in fmt[0] else '3'
    # if it comes in Python2 style
    if style == '2' and len(fmt) == 1:
        fmt = fmt[0].replace('%', '')
        fmt = ['{{{0}:{1}}}'.format(i, fmt) for i in range(ncols)]
    elif style == '2':
        fmt = ['{{{0}:{1}}}'.format(i[0], i[1].replace('%', ''))
               for i in enumerate(fmt)]
    # if it comes in Python3 style
    #else:
    return delimiter.join(fmt)


def header(filename, cols=None, removechar='#', hmode='1', linenum=0,
           hsep='', lower=False, remove_spaces=True, full_output=False):
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
        the header. If `hmode='1'` and `linenum=0` then the header will
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
    linenum : int
        The line number in which the header is located (count starts at
        1). If `linenum=0` and `hmode='1'`, the header is assumed to be
        the first line starting with `removechar`. If `hmode=='2'`,
        then this is used as the column number containing the names of
        the data columns.
    hsep : char
        Separator between column names. Typically <space> (default) or
        <comma>. Used only in `hmode=1`.
    lower: boole
        whether to return all column names in lower case.
    remove_spaces : bool
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
        Single-line header given in line number `linenum`. The header
        line may start with any comment character which is specified in
        `removechar`. Column names are separated by `hsep`. If
        starting with `removechar`. `linenum=0`, the header will be
        assumed to be the first line.
            `hmode=2`
        Column names are given in separate lines with explanations, each of
        which starts with a `'#'`, similar to the display of a FITS file header.
        Used, for instance, by SExtractor.
            `hmode=3`
        ApJ table format. File header contains a "byte-by-byte" description
        of the columns. No hashtags need to be present, but readfile can
        handle them if they are. NOT YET IMPLEMENTED

        Examples
        --------
        hmode=1
        Examples for different formats:
            removechar='#' :
            # ID  RA  Dec  redshift  mag_r
            removechar = '|' , sep = '|' :
            | ID | RA | Dec | redshift | mag_r |

        hmode=2, linenum=
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
    if isinstance(cols, int) or isinstance(cols, basestring):
        cols = [cols]

    if cols is not None:
        tp = type(cols[0])
        cols_items_are_str = isinstance(cols[0], basestring)
        cols_items_are_int = isinstance(cols[0], int)
        if not (cols_items_are_int or cols_items_are_str):
            raise TypeError('wrong type in cols, must be either str or int')
        for c in cols:
            if type(c) != tp:
                msg = 'All elements of cols must be of the same type'
                raise ValueError(msg)
        if cols_items_are_str:
            colnums = []
    if removechar not in (False, None):
        if not isinstance(removechar, basestring):
            raise TypeError('wrong type for removechar, should be a string')

    head = []
    # horizontal header
    if hmode == '1':
        file = open(filename)
        if linenum > 0:
            for i in range(linenum-1):
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
                colnums = array([i for i, h in enumerate(head) \
                                       if h in cols])
                head = [h for h in head if h in cols]
            else:
                head = [h for i, h in enumerate(head) if i in cols]

    # vertical header
    elif hmode == '2':
        if not removechar:
            msg = "ERROR: when setting hmode='2' must include removechar"
            print(msg)
            exit()
        data = table(filename, cols=linenum, dtype=str, include=removechar)
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
                colnums = array([name.index(i)
                                       for i in cols if i in name])
            else:
                head = [name_i for name_i, num_i in zip(name, num)
                        if num_i-1 in cols]
            head = array(head, dtype=str)

    if lower:
        head = array([h.lower() for h in head])

    # remove leading and trailing spaces from each column name
    if remove_spaces:
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
        #print >>out, header
        print(header, file=out)
    for i in zip(*data):
        #print >>out, fmt %i
        print(fmt.format(i), file=out)
    out.close()
    if verbose:
        print('Saved file {0}'.format(output))
    return


def table(filename, cols=None, dtype=float, exclude='#', include=None,
          skip=0, delimiter=None, whole=False, force_array=False,
          remove_spaces=True):
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
    skip : int
        Number of lines to skip before starting to read data. Note that
        excluded lines are not counted. Ignored if `include` is
        defined.
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
    if isinstance(cols, int) or isinstance(cols, basestring):
        cols = [cols]

    if cols is None:
        data = []
    else:
        data = [[] for i in cols]

    file = open(filename)
    if include:
        if isinstance(include, basestring):
            include = [include]
        for line in file:
            if len(line.split()) == 0:
                continue
            if whole:
                first = line.split(delimiter)[0]
            for i in include:
                if not whole:
                    first = line.replace(' ', '')[:len(i)]
                if first != i:
                    continue
                data = _append_single_line(
                    data, line, delimiter, dtype, cols)
    elif exclude:
        if isinstance(include, basestring):
            exclude = [exclude]
        for i, line in enumerate(file):
            if len(line.split()) == 0:
                continue
            add = True
            if whole:
                first = line.split(delimiter)[0]
            for e in exclude:
                if not whole:
                    first = line.replace(' ', '')[:len(e)]
                if first == e:
                    add = False
                    break
            if add and i >= skip:
                data = _append_single_line(
                    data, line, delimiter, dtype, cols)
    else:
        for i, line in enumerate(file):
            if len(line.split()) > 0 and i >= skip:
                data = _append_single_line(data, line, delimiter, dtype, cols)

    # remove leading and trailing spaces
    if remove_spaces:
        for i in range(len(data)):
            if isinstance(data[i][0], basestring):
                data[i] = char.strip(data[i], ' ')
                data[i] = char.rstrip(data[i], ' ')

    # if only one line is printed, don't want many arrays of length one
    # but one single array (if force_array is set to False)
    if not force_array:
        if len(data) > 1:
            if hasattr(data[0], '__iter__'):
                if len(data[0]) == 1:
                    table = []
                    if dtype is None:
                        for i in data:
                            try:
                                table.append(int(i[0]))
                            except ValueError:
                                try:
                                    table.append(float(i[0]))
                                except ValueError:
                                    table.append(i[0])
                    elif type(dtype) is type:
                        for i in data:
                            try:
                                table.append(dtype(i[0]))
                            except ValueError:
                                table.append(i[0])
                    else:
                        for i, tp in zip(data, dtype):
                            try:
                                table.append(tp(i[0]))
                            except ValueError:
                                table.append(i[0])
                    return table
        # the same if only one column is selected
        else:
            data = data[0]
            try:
                if len(data[0]) == 1:
                    try:
                        return dtype(data[0])
                    except ValueError:
                        return data[0][0]
            except TypeError:
                pass
            except IndexError:
                pass
            try:
                return array(data, dtype=dtype)
            except ValueError:
                return array(data, dtype=str)
    # many columns, many rows
    table = []
    if hasattr(dtype, '__iter__'):
        for tp, row in zip(dtype, data):
            try:
                try:
                    table.append(array(row, dtype=tp))
                except ValueError:
                    table.append(array(row, dtype=str))
            except IndexError:
                print('WARNING: No data selected from file {0}'.format(
                          filename))
                return []
    elif dtype is None:
        for row in data:
            try:
                try:
                    table.append(array(row, dtype=int))
                except ValueError:
                    try:
                        table.append(array(row, dtype=float))
                    except ValueError:
                        table.append(array(row, dtype=str))
            except IndexError:
                print('WARNING: No data selected from file'.format(filename))
                return []
    else:
        for row in data:
            try:
                try:
                    table.append(array(row, dtype=dtype))
                except ValueError:
                    table.append(array(row, dtype=str))
            except IndexError:
                print('WARNING: No data selected from file'.format(filename))
                return []
    if cols is not None:
        if len(cols) == 1:
            return table[0]
    return table


def _append_single_line(table, line, delimiter='', dtype=float, cols=None):
    """
    Auxiliary function, not meant to be used directly.

    Appends a single line to a table. Devised to iteratively make a table from
    a file. Can give a specified type to each field in the line (specified by
    `dtype`).

    """
    N = len(table)

    if delimiter in [' ', '', '\t']:
        line = line.split()
    else:
        line = line.replace('\n', '').split(delimiter)
    if hasattr(dtype, '__iter__'):
        if cols is None:
            if len(dtype) == len(line):
                for i, dt, col in zip(count(), dtype, line):
                    try:
                        table[i].append(dt(col))
                    except IndexError:
                        table.append([])
                        table[i].append(dt(col))
            else:
                msg = 'array dtype has a different length than the line'
                msg += ' (dtype:{0}; line:{1})'.format(len(dtype), len(line))
                raise IndexError(msg)
        elif len(dtype) == len(cols):
            for i, dt, col in zip(count(), dtype, cols):
                table[i].append(dt(line[col]))
            return table
        else:
            msg = 'arrays cols and dtype have different lengths in line'
            msg += ' (cols:{0}; dtype:{1}; line:{2})'.format(len(cols),
                                                             len(dtype),
                                                             len(line))
            raise IndexError(msg)

    elif type(dtype) == type:
        if cols is None:
            for i, col in enumerate(line):
                try:
                    try:
                        table[i].append(dtype(col))
                    except ValueError:
                        table[i].append(col)
                except IndexError:
                    table.append([])
                    try:
                        table[i].append(dtype(col))
                    except ValueError:
                        table[i].append(col)
        else:
            for i, col in enumerate(cols):
                try:
                    table[i].append(dtype(line[col]))
                except ValueError:
                    table[i].append(line[col])
        return table
    else:
        if cols is None:
            for l in line:
                try:
                    table[i].append(l)
                except IndexError:
                    table.append([])
                    table[i].append(l)
        else:
            table = [line[col] for col in cols]
    return table
