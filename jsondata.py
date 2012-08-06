"""
    jsondata helps you read and write data files.
    It saves lists line-by-line with each item in the list as json

    It saves dictionary values recursively as separate files by key of dict.
    It saves numpy arrays using savetxt a readable format offered by numpy lib.
    It saves lists of numpy arrays efficiently in an archive also offered by numpy lib: npz.

    It does this all through one simple interface: save and read.

    Copyright (C) 2011 Joseph Perla

    GNU Affero General Public License. See <http://www.gnu.org/licenses/>.
"""
import cjson

try:
    # works with Pypy
    import numpypy as numpy
except:
    import numpy

def save(filename, data):
    """Accepts filenamestring and a list of objects, probably dictionaries.
        Writes these to a file with each object pickled using json on each line.
    """
    if isinstance(data, dict):
        # save dict values recursively in separate files
        filename,ext = (filename.rsplit('.',1) if '.' in filename else (filename,''))

        for k,v in data.iteritems():
            save('{0}-{1}.{2}'.format(filename, k, ext), v)
    else:
        if isinstance(data, numpy.ndarray):
            # save numpy using its own thing for speed; .gz auto compresses
            numpy.savetxt(filename + '.npy.gz', data)
        elif isinstance(data, list) and isinstance(data[0], numpy.ndarray):
            # is a big list of arrays, so save in one big file
            numpy.savez(filename + '.npy.list', *data)
        else:
            with open(filename, 'w') as f:
                if hasattr(data, '__iter__'):
                    for i,d in enumerate(data):
                        if i != 0:
                            f.write('\n')
                        f.write(cjson.encode(d))
                else:
                    f.write(cjson.encode(data))


def read(filename):
    """Accepts filename string.
        Reads filename line by line and unpickles from json each line.
        Returns generator of objects.
    """
    if '.npy.list.npz' in filename:
        a = numpy.load(filename)
        return [a['arr_%s' % i] for i in xrange(len(a.keys()))]
    elif '.npy' in filename:
        # use numpy to read in; may be .gz compressed
        return numpy.loadtxt(filename)
    else:
        with open(filename, 'r') as f:
            return [cjson.decode(r) for r in f.xreadlines()]

read_list = lambda f: list(read(f))

#TODO: jperla: cjson api is different from simplejson api
#TODO: jperla: read_dict ?
