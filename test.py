#!/usr/bin/env python3
#
# Convert VNB and VPB layers in a LEF file from "li1" or "met1" to
# "substrate" and "well" masterslice layers, as they should be. 
#
# the algorithm cannot be expected to wok in all possible cases

#command to increase the size of the package by n pins





import os
import sys
import re


class lefReader():

    def __init__(self, string, resize):

        self.lefFile = open(string, 'r')
        self.resizeFactor = resize
        self.lines = self.lefFile.readlines()


    def getDim(self):
        lefLines = self.lines
        x = None
        y = None
        for i in lefLines:
            if i.__contains__("SIZE"):
                # print(i)
                x = float(i[i.index("SIZE") + 4: i.index(" BY")])
                y = float(i[i.index("Y ") + 1: i.index(" ;")])

        return [x, y]


    def getCoordinates(self):
        # if len(sys.argv) < 2:
        #    print("Usage: test.py <lef_file_in>")
        #    sys.exit(1)

        # lef_file_in = sys.argv[1]

        # print("Input:  " + <lef_file_in>)

        array = []

        # with open('frequency_divid.lef', 'r') as ifile:
        #    leflines = ifile.readlines()

        leflines = self.lines

        endrex = re.compile('[ \t]*END[ \t]+([^ \t\n]+)[ \t]*')
        pinrex = re.compile('[ \t]*PIN[ \t]+([^ \t\n]+)[ \t]*')
        layrex = re.compile('[ \t]*LAYER[ \t]+([^ \t]+)[ \t]+;')
        rectrex = re.compile('[ \t]*RECT[ \t]+([^ \t]+)[ \t]+([^ \t]+)[ \t]+([^ \t]+)[ \t]+([^ \t]+)[ \t]+;')

        inpin = False
        for line in leflines:
            rmatch = rectrex.match(line)
            lmatch = layrex.match(line)
            pmatch = pinrex.match(line)
            ematch = endrex.match(line)

            if pmatch:
                inpin = True
                pinname = pmatch.group(1)
                # print('PIN ' + pinname)
            elif ematch:
                if inpin == True and ematch.group(1) == pinname:
                    inpin = False
                    pinname = ''
            elif lmatch:
                if inpin:
                    layer = lmatch.group(1)
                    # print('   PIN ' + pinname + ' layer: ' + layer)
            elif rmatch:
                if inpin:
                    llx = rmatch.group(1)
                    lly = rmatch.group(2)
                    urx = rmatch.group(3)
                    ury = rmatch.group(4)
                    # print('   PIN ' + pinname + ' rect: ' + llx + ' ' + lly + ' ' + urx + ' ' + ury)

                    array.append([float(llx)/self.resizeFactor, float(lly)/self.resizeFactor, float(urx)/self.resizeFactor, float(ury)/self.resizeFactor])
            # print(array)

        return array
#print(lefReader("hydra.lef", 1).getDim())