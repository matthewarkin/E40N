# audiocom library: Source and sink functions
from collections import defaultdict
import heapq
import common_srcsink
import Image
from graphs import *
import binascii
import random


class Sink:
    def __init__(self):
        # no initialization required for sink 
        print 'Sink:'

    def process(self, recd_bits):
        # Process the recd_bits to form the original transmitted
        # file. 
        # Here recd_bits is the array of bits that was 
        # passed on from the receiver. You can assume, that this 
        # array starts with the header bits (the preamble has 
        # been detected and removed). However, the length of 
        # this array could be arbitrary. Make sure you truncate 
        # it (based on the payload length as mentioned in 
        # header) before converting into a file.
        
        # If its an image, save it as "rcd-image.png"
        # If its a text, just print out the text
        
        # Return the received payload for comparison purposes
        bytes = self.bitToByte(recd_bits)
        #self.printBytes(bytes)
        header=bytes[0:5]
        huffman=[]
        huffman, bytes = self.seperateHuffmanHeader(bytes[4:])
        codeToSym = self.huffmanFrequencyReader(huffman)
        bytes = list(self.decompress(codeToSym,bytes))
        ext = ""
        if (recd_bits[0] == 0 and recd_bits[1] == 1):
            ext = "txt"
            self.printBytes(bytes)
        elif (recd_bits[0] == 0 and recd_bits[1] == 0):
            print "png file"
            ext = "png"
            f = open("received." + ext, "wb")
            print len(bytes)
            for b in range (0, len(bytes)):
                print bytes[b]
                f.write(bytes[b])

            f.close()
        rcd_payload = recd_bits
        return rcd_payload

    def bytesToBits(self,bytes):
        for b in bytes:
            for i in xrange(8):
                yield (b >> i) & 1

    def decompress(self,codeToSym,bytes):
        bits=self.bytesToBits(bytes)
        bitString=""
        uncompressed=""
        for i in range(0,len(bytes*8)):
            int1 = next(bits)
            #print str(int1)
            bitString+=str(int1)
            if(bitString in codeToSym):
                uncompressed+=codeToSym[bitString]
                bitString=""
                #print bitString +"\n"
        return uncompressed




    def seperateHuffmanHeader(self,bytes):
        for i in range(0,len(bytes)-1,1):
            if (chr(bytes[i]) == '|') and (chr(bytes[i+1]) == '\n'):
                return bytes[0:i], bytes[i+2:]

    def huffmanFrequencyReader(self,huffmanHeader):
        symToCount=defaultdict(int)
        for i in range(0,len(huffmanHeader)-1,2):
            symToCount[chr(huffmanHeader[i])]=huffmanHeader[i+1]
            print str(huffmanHeader[i]) +" " + str(huffmanHeader[i+1])
        heap = [[wt, [sym, ""]] for sym, wt in symToCount.items()]
        heapq.heapify(heap)
        #generate the huffman encoding
        while len(heap) > 1:
            lo = heapq.heappop(heap)
            hi = heapq.heappop(heap)
            for pair in lo[1:]:
                pair[1] = '0' + pair[1]
            for pair in hi[1:]:
                pair[1] = '1' + pair[1]
            heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
        SymToCode = dict(sorted(heapq.heappop(heap)[1:], key=lambda p: (len(p[-1]), p)))
        CodeToSym = defaultdict(str)
        for sym in SymToCode:
            CodeToSym[SymToCode[sym]]=sym
        return CodeToSym


    def printBytes(self, bytes):
        text = ""
        for b in range (0, len(bytes)):
            text+= bytes[b]
        print text

    def bits2text(self, bits):
        # Convert the received payload to text (string)
        return  bits

    def image_from_bits(self, bits,filename):
        # Convert the received payload to an image and save it
        # No return value required .
        pass 

    def read_header(self, header_bits): 
        # Given the header bits, compute the payload length
        # and source type (compatible with get_header on source)
 
        print '\tRecd header: ', header_bits
        print '\tLength from header: ', payload_length
        print '\tSource type: ', srctype
        return srctype, payload_length

    def bitToByte(self, bits):
        bytes = []
        while (len(bytes) < len(bits)/8):
            pos = len(bytes)
            byteString = ""
            byteAsArray = bits[pos*8: pos*8 + 8]
            for b in byteAsArray:
                byteString += str(b)

            byteString = byteString[::-1]
            byte = int(byteString, 2)
            bytes.append(byte)
        return bytes