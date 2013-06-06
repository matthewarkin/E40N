import math
import common_txrx as common
import numpy
import hamming_db

class Transmitter:
    def __init__(self, carrier_freq, samplerate, one, spb, silence, cc_len):
        self.fc = carrier_freq  # in cycles per sec, i.e., Hz
        self.samplerate = samplerate
        self.one = one
        self.spb = spb
        self.silence = silence
        self.cc_len=cc_len
        print 'Transmitter: '

    def encode(self,databits):
        #ToDo Call Hamming_Encode on the Databits (this is the payload does not include the preamble)
        header = "Create Header HERE!" #Header includes length and cc_length

        index, encodedData = self.hamming_encoding(databits, False)
        closest_encode = min(hamming_db.parameters, key=lambda x:abs(x[0]-self.cc_len))

        encoding_index = numpy.binary_repr(hamming_db.parameters.index(closest_encode), width=2)
        length = numpy.binary_repr(len(encodedData), width=30)
        header_str = length + encoding_index
        header = []
        for bit in header_str:
            header.append(int(bit,2))
        index, coded_header = self.hamming_encoding(header, True)
        ##### TEST #####
        print "CODED DATA: " + str(encodedData)
        ##### END TEST #####
        return numpy.append(coded_header, encodedData)


        #return self.hamming_encoding(header,True)+self.hamming_encoding(databits,False)

    def hamming_encoding(self, databits, is_header):
        cc_len=self.cc_len
        if is_header:
            cc_len=3 #always use 3 for header

        n, k, index, G = hamming_db.gen_lookup(cc_len)

        encodedBits= []
        #Pad with zeros
        while len(databits)%k != 0:
            databits=numpy.append(databits,0)

        for x in xrange(0, len(databits), k):
            block = databits[x:x+k]
            encodedBits = numpy.append(encodedBits, numpy.dot(block, G))
        return index, encodedBits


    def add_preamble(self, databits):
        '''
        Prepend the array of source bits with silence bits and preamble bits
        The recommended preamble bits is 
        [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
        The output should be the concatenation of arrays of
            [silence bits], [preamble bits], and [databits]
        '''
        # fill in your implementation
        silence_bits = []
        for x in range(0, self.silence):
            silence_bits.append(0)
        databits_with_preamble = [1,1,1,1,1,0,1,1,1,1,0,0,1,1,1,0,1,0,1,1,0,0,0,0,1,0,1,1,1,0,0,0,
                                  1,1,0,1,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0,0,1,0,1,0,1,0,0,0,0,0,0]
        databits_with_preamble = silence_bits + databits_with_preamble
        databits_with_preamble = numpy.append(databits_with_preamble, databits)
        return databits_with_preamble


    def bits_to_samples(self, databits_with_preamble):
        '''
        Convert each bits into [spb] samples. 
        Sample values for bit '1', '0' should be [one], 0 respectively.
        Output should be an array of samples.
        '''
        # fill in your implemenation
        sample_per_bit = self.spb
        samples = []
        for x in range(0, len(databits_with_preamble)):
            samp = 0
            if databits_with_preamble[x] == 1:
                samp = self.one
            for x in range(0,sample_per_bit):
                samples.append(samp)

        return numpy.array(samples)
        

    def modulate(self, samples):
        '''
        Calls modulation function. No need to touch it.
        '''
        return common.modulate(self.fc, self.samplerate, samples)
