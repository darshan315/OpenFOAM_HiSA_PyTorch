#!/usr/bin/env python

"""
Convert files from NASA's Plot3D mesh format to Gmsh's MSH.

The MIT License (MIT)

Copyright (c) 2015-2016 J Heyns

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import print_function, division
import sys
import argparse
import os.path
import numpy as np
from ctypes import CDLL, c_int, byref, c_double

# File API.
#
# A FILE_ptr type is used instead of c_void_p because technically a pointer
# to structure can have a different size or alignment to a void pointer.
#
# Note that the file api may change.
#
# Source:
# http://svn.python.org/projects/ctypes/trunk/ctypeslib/ctypeslib/contrib/pythonhdr.py
try:
    import ctypes

    class FILE(ctypes.Structure):

        """stdio FILE representation."""

        pass
    FILE_ptr = ctypes.POINTER(FILE)

    PyFile_FromFile = ctypes.pythonapi.PyFile_FromFile
    PyFile_FromFile.restype = ctypes.py_object
    PyFile_FromFile.argtypes = [FILE_ptr,
                                ctypes.c_char_p,
                                ctypes.c_char_p,
                                ctypes.CFUNCTYPE(ctypes.c_int, FILE_ptr)]

    PyFile_AsFile = ctypes.pythonapi.PyFile_AsFile
    PyFile_AsFile.restype = FILE_ptr
    PyFile_AsFile.argtypes = [ctypes.py_object]
except AttributeError:
    del FILE_ptr



class P2DfmtFile(object):

    """P2Dfmt file representation."""

    def __init__(self, filename=None, **kwargs):
        """Construct from components or load from file."""
        if filename:
            self.load(filename=filename)
        else:
            if kwargs is not None:
                self.__nblocks = kwargs['nblocks'] \
                    if 'nblocks' in kwargs else 0
                self.__coords = kwargs['coords'] \
                    if 'coords' in kwargs else None
            else:
                self.__nblocks = None
                self.__coords = None

    @property
    def nblocks(self):
        """Number of blocks in the file."""
        return self.__nblocks

    def idims(self, nblk=1):
        """Return i-dimensions of the file."""
        return self.__coords[nblk - 1][0].shape[0]

    def jdims(self, nblk=1):
        """Return j-dimensions of the file."""
        return self.__coords[nblk - 1][0].shape[1]

    @property
    def coords(self):
        """Return coordinates stored in the file."""
        return self.__coords

    def load(self, filename):
        """Load mesh blocks from the given file."""
        if sys.platform == 'darwin':
            try:
                libc = CDLL('libc.dylib')
            except OSError:
                try:
                    libc = CDLL('/usr/lib/libc.dylib')
                except OSError:
                    print('Can not load libc.dylib')
                    sys.exit(-1)
        elif sys.platform == 'linux2':
            libc = CDLL('libc.so.6')
        else:
            raise OSError('Unsupported OS.')
        fscanf = libc.fscanf
        tmp = c_int()
        fp = open(filename)

        # Reading number of blocks
        fscanf(PyFile_AsFile(fp), '%d', byref(tmp))
        self.__nblocks = tmp.value

        # Reading dimensions
        idims = np.zeros(self.__nblocks, 'i')
        jdims = np.zeros(self.__nblocks, 'i')

        for i in xrange(self.__nblocks):
            fscanf(PyFile_AsFile(fp), '%d', byref(tmp))
            idims[i] = tmp.value
            fscanf(PyFile_AsFile(fp), '%d', byref(tmp))
            jdims[i] = tmp.value

        # Reading coordinates
        ftmp = c_double()
        self.__coords = []

        for b in xrange(self.__nblocks):
            idim = idims[b]
            jdim = jdims[b]
            x = np.zeros((idim, jdim, 1), 'f8')
            y = np.zeros((idim, jdim, 1), 'f8')
            z = np.zeros((idim, jdim, 1), 'f8')

            coords = [x, y, z]
            for c in coords:
                for k in xrange(1):
                    for j in xrange(jdim):
                        for i in xrange(idim):
                            fscanf(PyFile_AsFile(fp), '%lf', byref(ftmp))
                            c[i, j, k] = ftmp.value

            self.__coords.append((x, y, z))

        fp.close()

    def writeP3D(self, filename=None):
        """Write file, to stdout if no filename is given."""
        if filename:
            fp = open(filename, 'w')
        else:
            fp = sys.stdout
            
        # Number of blocks    
        fp.write('     '+str(self.__nblocks)+'\n')
        for b in xrange(self.__nblocks):
            # Extending from 2D to 3D by setting 
            # iDim = 2
            # jDim = iDim
            # kDim = jDim
            idim = 2
            jdim = self.idims(b)
            kdim = self.jdims(b)
            fp.write('     '+str(idim))
            fp.write('     '+str(jdim))
            fp.write('     '+str(kdim))
            fp.write('\n')
            
            coords = self.__coords
            x, y, z = self.__coords[b]
            
            count = 0
            # jDim
            for c in coords:
                for k in xrange(kdim):
                    for j in xrange(jdim):
                        for i in xrange(idim):
                            fp.write("{0:.14e} \t".format((x[j][k][0]))) 
                            count = count + 1
                            if (count == 3):
                                fp.write('\n')
                                count = 0;
                                
            # iDim
            for c in coords:
                for k in xrange(kdim):
                    for j in xrange(jdim):
                        for i in xrange(idim):
                            if i == 0:
                                #fp.write("{0:.14f} \t".format((z[j][k][0]/10.0)))
                                fp.write("{0:.14e} \t".format(0.0))
                            elif i == 1:
                                #fp.write("-{0:.14f} \t".format((z[j][k][0]/10.0)))
                                fp.write("{0:.14e} \t".format(-1.0))
                            count = count + 1
                            if (count == 3):
                                fp.write('\n')
                                count = 0;
                                
            # kDim
            for c in coords:
                for k in xrange(kdim):
                    for j in xrange(jdim):
                        for i in xrange(idim):
                            fp.write("{0:.14e} \t".format((y[j][k][0]))) 
                            count = count + 1
                            if (count == 3):
                                fp.write('\n')
                                count = 0;
                                
            



def main():
    """Parse command line options, convert files."""
    # CLI options:
    # --output-file / -o: write resulting mesh into
    # --map-file / -m: read boundary description from

    parser = argparse.ArgumentParser(description='''\
        Convert P2Dfmt mesh into P3Dfmt mesh''', add_help=True)
    parser.add_argument('files', nargs='+', help='files to convert')
    parser.add_argument('-o', '--output-file', nargs=1, help='''\
        output file name, if omitted mesh will be written to <filename>.msh''')
    args = parser.parse_args()

    print("Converting p2d to p3d")

    for fn in args.files:
        
        if not os.path.exists(fn):
            print('Can\'t open {0}. Skipping.'.format(fn))
            continue
        (name, _) = os.path.splitext(fn)

        outputfile = None
        if args.output_file is None:
            outputfile = '{0}.p3dfmt'.format(name)
        else:
            outputfile = args.output_file.pop()

        p2d = P2DfmtFile()
        p2d.load(fn)
        p2d.writeP3D(outputfile)
        

if __name__ == '__main__':
    main()
