import re
import test as test


# Class for Rectangle
class Rectangle:

    def __init__(self, xl, yl, xr, yr):
        self.xl = xl
        self.yl = yl
        self.xr = xr
        self.yr = yr

    # Returns Coornidates for the center of the rec
    def getCenter(self):
        a = (float(self.xl) + float(self.xr)) / 2
        b = (float(self.yl) + float(self.yr)) / 2
        return [a, b]

    def getCoordinates(self):
        return [self.xl, self.yl, self.xr, self.yr]


# (lower-left-x) (lower-left-y) (upper-right-x) (upper-right-y)

class vQFN:

    def __init__(self, string, resizeFactor):
        self.lefReader = test.lefReader(string, resizeFactor)

        self.pads = []
        self.array = self.lefReader.getCoordinates()
        for i in self.array:
            self.pads.append(Rectangle(i[0], i[1], i[2], i[3]))
        self.dim = self.lefReader.getDim()

    def centralPad(self):
        xArray = []
        yArray = []
        array = self.array

        for i in array:
            xArray.append(i[0])
            xArray.append(i[2])
            yArray.append(i[1])
            yArray.append(i[3])

        xArray.sort()
        yArray.sort()

        xArray = list(dict.fromkeys(xArray))
        yArray = list(dict.fromkeys(yArray))

        return [xArray[2], yArray[2], xArray[len(xArray) - 3], yArray[len(yArray) - 3]]

    def getCenters(self):
        array = []
        for i in self.pads:
            array.append(i.getCenter())
        return array

    def getCoordinates(self):
        return self.array

    def getDim(self):
        return self.dim



