import sys
import math
import numpy
import scipy.cluster.vq
import common_txrx as common
from numpy import linalg as LA
import receiver_mil3
import hamming_db


class Receiver:
    def __init__(self, carrier_freq, samplerate, spb):
        '''
        The physical-layer receive function, which processes the
        received samples by detecting the preamble and then
        demodulating the samples from the start of the preamble 
        sequence. Returns the sequence of received bits (after
        demapping)
        '''
        self.fc = carrier_freq
        self.samplerate = samplerate
        self.spb = spb 
        print 'Receiver: '

    def detect_threshold(self, demod_samples):
        '''
        Calls the detect_threshold function in another module.
        No need to touch this.
        ''' 
        return receiver_mil3.detect_threshold(demod_samples)
 
    def detect_preamble(self, demod_samples, thresh, one):
        '''
        Find the sample corresp. to the first reliable bit "1"; this step 
        is crucial to a proper and correct synchronization w/ the xmitter.
        '''

        '''
        First, find the first sample index where you detect energy based on the
        moving average method described in the milestone 2 description.
        '''
        # Fill in your implementation of the high-energy check procedure

        energy_offset = 0
        lower_bound = (one + thresh)/2
        print "one: " + str(one)
        print "thresh: " + str(thresh)
        while True:
            mean = numpy.average(demod_samples[energy_offset + self.spb/4:energy_offset + self.spb*3/4])
            if mean > lower_bound:
                break
            energy_offset = energy_offset + 1

        if energy_offset < 0:
            print '*** ERROR: Could not detect any ones (so no preamble). ***'
            print '\tIncrease volume / turn on mic?'
            print '\tOr is there some other synchronization bug? ***'
            sys.exit(1)

        '''
        Then, starting from the demod_samples[offset], find the sample index where
        the cross-correlation between the signal samples and the preamble 
        samples is the highest. 
        '''
        # Fill in your implementation of the cross-correlation check procedure
        preamble_bits = [1,1,1,1,1,0,1,1,1,1,0,0,1,1,1,0,1,0,1,1,0,0,0,0,1,0,1,1,1,0,0,0,
                         1,1,0,1,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0,0,1,0,1,0,1,0,0,0,0,0,0]
        preamble_samples = []
        for x in range(0, len(preamble_bits)):
            sample = [preamble_bits[x]]*self.spb
            #print "sample: " + str(sample)
            preamble_samples = preamble_samples + sample

        preamble_samples = numpy.array(preamble_samples)
        print "preamble_samples: " + str(preamble_samples)

        maximum = 0
        offset = 0
        for x in range(-10*self.spb,10*self.spb):
            #print "preamble_samples" + str(preamble_samples)
            test_array = demod_samples[energy_offset + x:energy_offset + x + len(preamble_samples)]
            #print "test_array: " + str(test_array)
            result = numpy.multiply(test_array, preamble_samples)
            #print "result: " + str(result)
            temp = numpy.sum(result)
            
            if temp > maximum:
                #print "temp: " + str(temp)
                #print "offset: " + str(x)
                maximum = temp
                offset = x



        preamble_offset = offset
        print "NUMBER of samples: " + str(len(demod_samples)/self.spb)
        print "Energy Offset: " + str(energy_offset)
        print "preamble_offset: " + str(offset)
        
        '''
        [preamble_offset] is the additional amount of offset starting from [offset],
        (not a absolute index reference by [0]). 
        Note that the final return value is [offset + pre_offset]
        '''
        print "total offset: " + str(energy_offset + preamble_offset)
        print "starting bit: " + str((energy_offset + preamble_offset)/self.spb)
        return energy_offset + preamble_offset
        
    def demap_and_check(self, demod_samples, preamble_start):
        '''
        Demap the demod_samples (starting from [preamble_start]) into bits.
        1. Calculate the average values of midpoints of each [spb] samples
           and match it with the known preamble bit values.
        2. Use the average values and bit values of the preamble samples from (1)
           to calculate the new [thresh], [one], [zero]
        3. Demap the average values from (1) with the new three values from (2)
        4. Check whether the first [preamble_length] bits of (3) are equal to
           the preamble. If it is proceed, if not terminate the program. 
        Output is the array of data_bits (bits without preamble)
        '''
        preamble_bits = [1,1,1,1,1,0,1,1,1,1,0,0,1,1,1,0,1,0,1,1,0,0,0,0,1,0,1,1,1,0,0,0,
                         1,1,0,1,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0,0,1,0,1,0,1,0,0,0,0,0,0]
        

        ones = []
        zeroes = []
        for x in range(0, len(preamble_bits)):
            mean = numpy.average(demod_samples[preamble_start + x*self.spb:x*self.spb + self.spb + preamble_start])
            if preamble_bits[x] == 1:
                ones.append(mean)
            else:
                zeroes.append(mean)

        ones_average = numpy.mean(ones)
        zeroes_average = numpy.mean(zeroes)
        print "high: " + str(ones_average)
        print "low: " + str(zeroes_average)

        # Fill in your implementation
        threshold = (ones_average + zeroes_average)/2
        offset = preamble_start + len(preamble_bits)*self.spb

        data_bits = []

        for x in range(0, (len(demod_samples) - offset)/self.spb): #iterating through the bits
            mean = 0
            #print (x - offset/self.spb)
            for y in range(0, self.spb):
                mean  = mean + demod_samples[offset + x*self.spb + y]
            mean = mean / self.spb
            if (mean > threshold):
                data_bits.append(1)
            else:
                data_bits.append(0)
            #x = x + self.spb


        return data_bits # without preamble

    def demodulate(self, samples):
        return common.demodulate(self.fc, self.samplerate, samples)

    def correct(self, chunk, n, k, H):
        cols = numpy.hsplit(H, n)
        syndrome = numpy.dot(H, numpy.transpose(chunk))
        # account for xor
        for x in xrange(len(syndrome)):
            if syndrome[x]%2 == 0: syndrome[x] = 0
            else: syndrome[x] = 1
            # check if correct
        correct = True
        for x in xrange(len(syndrome)):
            if syndrome[x] != 0: correct = False
        if correct: return 0, chunk[:k]
        # correct error
        #print chunk[:k]
        # print "SYND = " + str(syndrome)
        # for vec in cols:
        #     print "HCOL = " + str(numpy.transpose(vec)[0])
        for x in xrange(k):
            if numpy.array_equal(syndrome, numpy.transpose(cols[x])[0]):
                #print "Corrected"
                chunk[x] = 1 if chunk[x] == 0 else 0
            #print chunk[:k]
        return 1, chunk[:k]

    def hamming_decoding(self, coded_bits, index):
        decoded_bits = []
        num_errors = 0
        n, k, H = hamming_db.parity_lookup(index)
        coding_rate = float(k)/n
        while len(coded_bits)%n != 0:
            coded_bits = numpy.append(coded_bits, 0)
        for x in xrange(0, len(coded_bits), n):
            chunk = coded_bits[x:x+n]
            corrected, correct_chunk  = self.correct(chunk, n, k, H)
            num_errors += corrected
            decoded_bits = numpy.append(decoded_bits, correct_chunk)
        decoded_bits = ''.join(numpy.char.mod('%d', decoded_bits))
        return decoded_bits, coding_rate, num_errors

    def decode(self, rcd_bits):
        encoding_options = [[3,1],[7,4],[15,11],[31,26]]
        header = rcd_bits[0:32*3] #length of encoded header
        decoded_header, temp_cr, temp_ne = self.hamming_decoding(header, 0)
        data_len = int(str(decoded_header[:30]), 2)
        index = int(str(decoded_header[30:]), 2)
        data = rcd_bits[32*3:]#32*3+data_len]
        decoded_data, coding_rate, num_errors = self.hamming_decoding(data, index)
        ##### TEST #####
        #print data
        #print "Len = " + str(data_len)
        #print "Ind = " + str(index)
        print "DECODED HEAD: " + str(list(int(x) for x in decoded_header))
        #print "DECODED DATA: " + str(list(int(x) for x in decoded_data))
        ##### END TEST #####
        print "channel coding rate: " + str(coding_rate)
        print "errors corrected: " + str(num_errors)
        return list(int(x) for x in decoded_data)
