import numpy
import math
import operator
import common_txrx_mil3
import binascii
import sys

generating_matrices = [numpy.array([1, 1, 1]),
                       numpy.array([1,    1,    0,    1,    0,    0,    0,
                                    0,    1,    1,    0,    1,    0,    0,
                                    1,    1,    1,    0,    0,    1,    0,
                                    1,    0,    1,    0,    0,    0,    1]),
                       numpy.array([1,     1,     0,     0,     1,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
                                    0,     1,     1,     0,     0,     1,     0,     0,     0,     0,     0,     0,     0,     0,     0,
                                    0,     0,     1,     1,     0,     0,     1,     0,     0,     0,     0,     0,     0,     0,     0,
                                    1,     1,     0,     1,     0,     0,     0,     1,     0,     0,     0,     0,     0,     0,     0,
                                    1,     0,     1,     0,     0,     0,     0,     0,     1,     0,     0,     0,     0,     0,     0,
                                    0,     1,     0,     1,     0,     0,     0,     0,     0,     1,     0,     0,     0,     0,     0,
                                    1,     1,     1,     0,     0,     0,     0,     0,     0,     0,     1,     0,     0,     0,     0,
                                    0,     1,     1,     1,     0,     0,     0,     0,     0,     0,     0,     1,     0,     0,     0,
                                    1,     1,     1,     1,     0,     0,     0,     0,     0,     0,     0,     0,     1,     0,     0,
                                    1,     0,     1,     1,     0,     0,     0,     0,     0,     0,     0,     0,     0,     1,     0,
                                    1,     0,     0,     1,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     1]),
                       numpy.array([ 1,    0,     1,     0,     0,     1,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
                                     0,    1,    0,    1,     0,     0,     1,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
                                     0,    0,    1,    0,     1,     0,     0,     1,     0,     0,     0,     0,     0,     0,     0,     0,     0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    0,    1,    1,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     0,    1,    0,    1,    1,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    0,    0,    0,    1,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     0,    1,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     0,    0,    1,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    0,    1,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    1,    1,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    1,    0,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    1,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     0,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     0,    0,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     0,    0,    0,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    0,    1,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    1,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,
                                     0,    1,    1,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,
                                     1,    0,    0,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,
                                     1,    1,    1,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,
                                     1,    1,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,
                                     0,    1,    1,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,
                                     1,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,
                                     0,    1,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1])]

parameters = [[3,1],[7,4],[15,11],[31,26]]


def gen_lookup(cc_len):
    ''' 
    returns
    (1) n (=cc_len, codeword length)
    (2) k (length of data bit in each codeword)
    (3) index (index of the corresponding code in the above lookup table)
    (4) generater matrix
    for Hamming code with n = cc_len
    '''

    matrix = min(parameters, key=lambda x:abs(x[0]-cc_len))


    index=parameters.index(matrix)
    '''
    if cc_len == 3:
        index = 0
    elif cc_len == 7:
        index = 1
    elif cc_len == 15:
        index = 2
    elif cc_len == 31:
        index = 3
    else:
        print '\tNo Hamming code with n =', cc_len
        sys.exit(1)
    '''
    n=matrix[0]
    k=matrix[1]
    '''
    n = parameters[index][0]
    k = parameters[index][1]
    '''
    # Reshape G:
    G = numpy.eye(k)
    temp = numpy.reshape(generating_matrices[index], (k, n))
    cols = numpy.hsplit(temp, n)
    for x in xrange(n-k):
        G = numpy.concatenate((G, cols[x]), axis=1)
    return n, k, index, G

def parity_lookup(index):
    '''
    returns the
    (1) n (=cc_len, codeword length)
    (2) k (length of data bit in each codeword)
    (3) index (index of the corresponding code in the above lookup table)
    (4) parity check matrix
    matched by the lookup table above given the index
    The reason why this takes the index as the input while gen_lookup takes cc_len
    is, because containing index is efficient than containing n in the header.
    The decoder reads the header to pick the right parity check matrix.
    '''

    G = generating_matrices[index]
    n = parameters[index][0]
    k = parameters[index][1]

    matrix = numpy.reshape(generating_matrices[index], (k, n))
    cols = numpy.hsplit(matrix, n)

    col0=cols[0]
    for x in xrange(1, n-k):
        col0 = numpy.concatenate((col0, cols[x]), axis=1)
    col0=col0.transpose()
    H=numpy.eye(n-k)
    H=numpy.concatenate((col0, H), axis=1)


    # Reshape G, extract A and compute H:

    return n, k, H



