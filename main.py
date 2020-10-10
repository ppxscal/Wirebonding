from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import math
import sys
from PIL import ImageTk, Image

try:
    from PIL import ImageGrab
except:
    import pyscreenshot as ImageGrab

# imports canvas2svg package manually

sys.path.insert(1, "C:/Users/pasca/Desktop/Projects/WirebondingV2/canvas2svg-master")
import canvasvg
import test
import time


# tags
# given which wires are connected to pads and pins, write pins numbered top left
# as soon as wire is attached, pin name must be knowshift - pin 1 - 12, list names
# generate pin packaging pinout diagrams
# mapping of names to pin numbers
# KiCad Symbols


# Rules
# max length 3mm

# wire to bond pad center 120 um (Depends on Wire Material)
# wire to package pad um (Depends on Wire Material)


# min wire angle to die edge 40degrees

# Allows access to previous diagrams
packageMemory = []

# img object to evade tkinter garbage collector
img = None


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Given three colinear points p, q, r, the function checks if


# point q lies on line segment 'pr'
def onSegment(p, q, r):
    if (
        (q.x <= max(p.x, r.x))
        and (q.x >= min(p.x, r.x))
        and (q.y <= max(p.y, r.y))
        and (q.y >= min(p.y, r.y))
    ):
        return True
    return False


def orientation(p, q, r):

    val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
    if val > 0:

        # Clockwise orientation
        return 1
    elif val < 0:

        # Counterclockwise orientation
        return 2
    else:

        # Colinear orientation
        return 0


# The main function that returns true if
# the line segment 'p1q1' and 'p2q2' intersect.
def doIntersect(p1, q1, p2, q2):
    # Find the 4 orientations required for
    # the general and special cases
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if (o1 != o2) and (o3 != o4):
        return True

    # Special Cases

    # p1 , q1 and p2 are colinear and p2 lies on segment p1q1
    if (o1 == 0) and onSegment(p1, p2, q1):
        return True

    # p1 , q1 and q2 are colinear and q2 lies on segment p1q1
    if (o2 == 0) and onSegment(p1, q2, q1):
        return True

    # p2 , q2 and p1 are colinear and p1 lies on segment p2q2
    if (o3 == 0) and onSegment(p2, p1, q2):
        return True

    # p2 , q2 and q1 are colinear and q1 lies on segment p2q2
    if (o4 == 0) and onSegment(p2, q1, q2):
        return True

    # If none of the cases
    return False


# Rectangle Object for dealing with lef coordinates


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


# Object Representation of the QFN Package


class vQFN:
    def __init__(self, string, resizeFactor, canvas):
        self.string = string
        self.lefReader = test.lefReader(string, resizeFactor)
        self.pads = []
        self.array = self.lefReader.getCoordinates()
        for i in self.array:
            self.pads.append(Rectangle(i[0], i[1], i[2], i[3]))

        # returns dimensions of the chip
        self.dim = self.lefReader.getDim()

        self.wires = []

        # image object
        self.img = None

        # Directional dimensions of chip
        self.imgDimx = None
        self.imgDimy = None

        # Tkinter pin objects
        self.pins = []
        # Taken Pins that have been already wire bonded to

        self.takenPins = []

        # Center coordinate of the chip
        self.center = None

        # Centers coordinates of each pad
        self.centers = None

        # The length of the span of pins over one side

        self.pinRange = None

        # Tkinter pad Objects
        self.padItems = []

        # Dynamic array that details the distance from one pin to every other - is not constant
        self.distanceToPins = []

        # coordinates for the rectangle that outlines the chip - can be used if no image is availiable
        self.central = None

        # Resizing factor for drawing the diagram to fit the tkinter window

        self.resizeFactor = resizeFactor

        self.canvas = canvas

        # Sets up many self variables

        self.Initialize()

        # Switches anchor for dragging wire

        self.switch = True

        # Contains pads that belong either to left bottom right or top side of the QFN

        self.left = None

        self.bottom = None

        self.right = None

        self.top = None

        self.badWires = 0

        self.maxLength = 3000 / self.resizeFactor

        self.minLength = 1000 / self.resizeFactor

    def getName(self):
        return self.string[:-4]

    # Returns coordinates for the rectangle that outlines the chip - can be used if no image is availiable

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

    def getImgDimx(self):
        return self.imgDimx

    def getImgDimy(self):
        return self.imgDimy

    def getCentral(self):
        return self.central

    def getCenter(self):
        return self.center

    def getPinRange(self):
        return self.pinRange

    def getResizeFactor(self):
        return self.resizeFactor

    def getImg(self):
        return self.img

    def getWires(self):
        return self.wires

    def getCanvas(self):
        return self.canvas

    def getPins(self):
        return self.pins

    def getPads(self):
        return self.padItems

    def getSwitch(self):
        return self.switch

    def flipSwitch(self):
        self.switch = not (self.switch)

    def getBadWires(self):
        return self.badWires

    def getPinNames(self):
        return self.lefReader.getPinNames()

    def getLengths(self):
        return [self.minLength, self.maxLength]

    def setLengths(self, a, b):
        self.minLength = int(a) / self.resizeFactor
        self.maxLength = int(b) / self.resizeFactor

    def Initialize(self):

        self.centers = self.getCenters()
        self.central = self.centralPad()

        self.numberSide = int(round(len(self.centers) / 4))
        self.pinRange = (
            (2 * self.numberSide) + 1
        ) * 500 / self.resizeFactor / 2 - 500 / self.resizeFactor
        self.img = Image.open(self.string[:-4] + ".png")
        self.imgDimx = self.getDim()[0] / self.resizeFactor
        self.imgDimy = self.getDim()[1] / self.resizeFactor
        self.img = self.img.resize(
            (int(round(self.imgDimx)), int(round(self.imgDimy))), Image.ANTIALIAS
        )
        self.img = ImageTk.PhotoImage(self.img)
        self.canvas.img = self.img
        self.center = [self.imgDimx / 2, self.imgDimy / 2]
        # Pads by Pins

    def drawImage(self):
        self.canvas.create_image(self.center[0], self.center[1], image=self.img)

        # draws rectangle inside the chip - for reference purposes

    def drawInnerRect(self):
        self.canvas.create_rectangle(
            self.central[0], self.central[1], self.central[2], self.central[3]
        )

        # draws the outline of the entire package

    def drawOuterRect(self):
        self.canvas.create_rectangle(
            self.center[0] - self.pinRange / 2 - 1000 / self.resizeFactor,
            self.center[1] - self.pinRange / 2 - 1000 / self.resizeFactor,
            self.center[0] + self.pinRange / 2 + 1000 / self.resizeFactor,
            self.center[1] + self.pinRange / 2 + 1000 / self.resizeFactor,
            fill="black",
        )

    def drawPaddle(self):
        self.canvas.create_rectangle(
            self.center[0] - self.pinRange / 2,
            self.center[1] - self.pinRange / 2,
            self.center[0] + self.pinRange / 2,
            self.center[1] + self.pinRange / 2,
            fill="silver",
        )

        # draws chip ouline

    def drawMidRect(self):
        self.canvas.create_rectangle(
            self.center[0] - self.imgDimx / 2,
            self.center[1] - self.imgDimy / 2,
            self.center[0] + self.imgDimx / 2,
            self.center[1] + self.imgDimy / 2,
        )

    def drawPads(self):
        for pad in self.array:
            self.padItems.append(
                self.canvas.create_rectangle(
                    pad[0], pad[1], pad[2], pad[3], fill="white"
                )
            )

    # creating paddles
    # pin dimensions, .25mm wide, .25mm spacing, .5mm length, .5mm from paddle
    # order is left, bottom, right, top

    def drawPinsLeft(self):
        for i in range(self.numberSide):
            self.pins.append(
                self.canvas.create_rectangle(
                    self.center[0] - self.pinRange / 2 - 1000 / self.resizeFactor,
                    self.center[1] - self.pinRange / 2 + 500 * i / self.resizeFactor,
                    self.center[0] - self.pinRange / 2 - 500 / self.resizeFactor,
                    self.center[1]
                    - self.pinRange / 2
                    + 250 / self.resizeFactor
                    + 500 * i / self.resizeFactor,
                    fill="silver",
                )
            )

    def drawPinsBottom(self):
        for i in range(self.numberSide):
            self.pins.append(
                self.canvas.create_rectangle(
                    self.center[0] - self.pinRange / 2 + 500 * i / self.resizeFactor,
                    self.center[1] + self.pinRange / 2 + 1000 / self.resizeFactor,
                    self.center[0]
                    - self.pinRange / 2
                    + 250 / self.resizeFactor
                    + 500 * i / self.resizeFactor,
                    self.center[1] + self.pinRange / 2 + 500 / self.resizeFactor,
                    fill="silver",
                )
            )

    def drawPinsRight(self):
        for i in range(self.numberSide):
            self.pins.append(
                self.canvas.create_rectangle(
                    self.center[0] + self.pinRange / 2 + 1000 / self.resizeFactor,
                    self.center[1] + self.pinRange / 2 - 500 * i / self.resizeFactor,
                    self.center[0] + self.pinRange / 2 + 500 / self.resizeFactor,
                    self.center[1]
                    + self.pinRange / 2
                    - 250 / self.resizeFactor
                    - 500 * i / self.resizeFactor,
                    fill="silver",
                )
            )

    def drawPinsTop(self):
        for i in range(self.numberSide):
            self.pins.append(
                output.create_rectangle(
                    self.center[0] + self.pinRange / 2 - 500 * i / self.resizeFactor,
                    self.center[1] - self.pinRange / 2 - 1000 / self.resizeFactor,
                    self.center[0]
                    + self.pinRange / 2
                    - 250 / self.resizeFactor
                    - 500 * i / self.resizeFactor,
                    self.center[1] - self.pinRange / 2 - 500 / self.resizeFactor,
                    fill="silver",
                )
            )

        # increase size of packeg

    def changePinRange(self, number):
        self.numberSide += number

        self.pinRange = (
            (2 * self.numberSide) + 1
        ) * 500 / self.resizeFactor / 2 - 500 / self.resizeFactor
        self.canvas.delete("all")

    def getCenterRect(self, i):
        bounds = self.canvas.bbox(i)

        return [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2]

    def distance(self, i, j):
        i = self.getCenterRect(i)
        j = self.getCenterRect(j)
        x = i[0] - j[0]
        y = i[1] - j[1]

        return math.hypot(x, y)

        # checks length requirement for chips - depends on type of wire used

    def checkLength(self):

        for i in self.wires:
            x0, y0, x1, y1 = self.canvas.coords(i)

            x = x0 - x1
            y = y0 - y1

            if not (self.minLength <= math.hypot(x, y) <= self.maxLength):
                self.canvas.itemconfig(i, fill="red")
                self.badWires += 1

    def drawWires(self):
        xArray = []
        yArray = []

        left = []
        bottom = []
        right = []
        top = []

        for i in self.padItems:

            xArray.append(self.getCenterRect(i)[0])
            yArray.append(self.getCenterRect(i)[1])

        for i in self.padItems:
            if (
                min(xArray) - 50 / self.resizeFactor
                <= self.getCenterRect(i)[0]
                <= min(xArray) + 50 / self.resizeFactor
            ):
                left.append(i)
            elif (
                max(xArray) - 50 / self.resizeFactor
                <= self.getCenterRect(i)[0]
                <= max(xArray) + 50 / self.resizeFactor
            ):
                right.append(i)
            elif (
                max(yArray) - 50 / self.resizeFactor
                <= self.getCenterRect(i)[1]
                <= max(yArray) + 50 / self.resizeFactor
            ):
                top.append(i)
            elif (
                min(yArray) - 50 / self.resizeFactor
                <= self.getCenterRect(i)[1]
                <= min(yArray) + 50 / self.resizeFactor
            ):
                bottom.append(i)

        left = centerIterator(left)

        bottom = centerIterator(bottom)

        right = centerIterator(right)

        top = centerIterator(top)

        self.left = left
        self.bottom = bottom
        self.right = right
        self.top = top

        sideList = self.left + self.bottom + self.right + self.top

        # need to check that all pads are wired because the algorithm leaves some unwired for some reason

        for i in self.padItems:
            if i not in sideList:
                if (
                    min(xArray) - 50 / self.resizeFactor
                    <= self.getCenterRect(i)[0]
                    <= min(xArray) + 50 / self.resizeFactor
                ):
                    self.left.append(i)
                elif (
                    max(xArray) - 50 / self.resizeFactor
                    <= self.getCenterRect(i)[0]
                    <= max(xArray) + 50 / self.resizeFactor
                ):
                    self.right.append(i)
                elif (
                    max(yArray) - 50 / self.resizeFactor
                    <= self.getCenterRect(i)[1]
                    <= max(yArray) + 50 / self.resizeFactor
                ):
                    self.top.append(i)
                elif (
                    min(yArray) - 50 / self.resizeFactor
                    <= self.getCenterRect(i)[1]
                    <= min(yArray) + 50 / self.resizeFactor
                ):
                    self.bottom.append(i)

        sideList = self.left + self.bottom + self.right + self.top

        for i in sideList:
            for j in self.pins:
                self.distanceToPins.append(self.distance(i, j))
            for element in range(len(self.distanceToPins)):
                if element in self.takenPins:
                    self.distanceToPins[element] = sys.maxsize
            closest = self.distanceToPins.index(min(self.distanceToPins))
            locI = self.getCenterRect(i)
            locJ = self.getCenterRect(self.pins[closest])
            self.wires.append(
                self.canvas.create_line(locI[0], locI[1], locJ[0], locJ[1], fill="blue")
            )
            self.takenPins.append(self.pins.index(self.pins[closest]))
            self.distanceToPins.clear()

        # uscrambles wires
        # If unsolvable - python runs out of memory. Simply increase package size eg "* strive"

    def fixCrossover(self):
        for i in self.wires:
            x0, y0, x1, y1 = self.canvas.coords(i)
            a1 = Point(x0, y0)
            a2 = Point(x1, y1)
            temp = list(self.wires)
            temp.remove(i)
            for j in temp:
                x01, y01, x11, y11 = output.coords(j)
                b1 = Point(x01, y01)
                b2 = Point(x11, y11)

                if not doIntersect(a1, a2, b1, b2):
                    continue
                else:
                    self.canvas.coords(i, x0, y0, x11, y11)
                    self.canvas.coords(j, x01, y01, x1, y1)
                    # time.sleep(0.1)
                    self.fixCrossover()

                    return

    def checkCrossOver(self):
        for i in self.wires:
            x0, y0, x1, y1 = self.canvas.coords(i)
            a1 = Point(x0, y0)
            a2 = Point(x1, y1)
            temp = list(self.wires)
            temp.remove(i)
            for j in temp:
                x01, y01, x11, y11 = output.coords(j)
                b1 = Point(x01, y01)
                b2 = Point(x11, y11)

                if not doIntersect(a1, a2, b1, b2):
                    continue
                else:
                    self.canvas.itemconfig(i, fill="#0000FF")
                    self.canvas.itemconfig(j, fill="#0000FF")

        # checks angle requirements

    def checkAngles(self):
        for i in self.pins:
            pinDim = self.canvas.bbox(i)
            wiresWithinPin = list(
                self.canvas.find_overlapping(pinDim[0], pinDim[1], pinDim[2], pinDim[3])
            )
            for j in wiresWithinPin:
                if j in self.wires:
                    x01, y01, x11, y11 = self.canvas.coords(j)
                    for k in self.padItems:
                        padDim = self.canvas.bbox(k)
                        wiresWithinPad = list(
                            self.canvas.find_overlapping(
                                padDim[0], padDim[1], padDim[2], padDim[3]
                            )
                        )
                        for l in wiresWithinPad:
                            if l == j:
                                x = abs(x01 - x11)
                                y = abs(y01 - y11)

                                if k in self.left or k in self.right:
                                    if math.atan(x / (y + 1)) < math.radians(40):
                                        self.canvas.itemconfig(l, fill="red")
                                        self.badWires += 1
                                    else:
                                        self.canvas.itemconfig(l, fill="#0000FF")

                                else:
                                    if math.atan(y / (x + 1)) < math.radians(40):
                                        self.canvas.itemconfig(l, fill="red")
                                        self.badWires += 1
                                    else:
                                        self.canvas.itemconfig(l, fill="#0000FF")

        # shift wires any direction mod len(pads)

    def shiftWires(self, number):

        alreadyShifted = []

        for i in self.pins:
            # pinDim = self.canvas.bbox(i)

            pinCenter = self.getCenterRect(i)
            newPin = self.getCenterRect(
                self.pins[(self.pins.index(i) + int(number)) % len(self.pins)]
            )

            wiresWithinPin = list(
                self.canvas.find_overlapping(
                    pinCenter[0], pinCenter[1], pinCenter[0], pinCenter[1]
                )
            )

            for item in wiresWithinPin:
                if item not in self.wires or item in alreadyShifted:
                    wiresWithinPin.remove(item)

            for j in wiresWithinPin:
                if j in self.wires:
                    x01, y01, x11, y11 = self.canvas.coords(j)
                    self.canvas.coords(j, x01, y01, newPin[0], newPin[1])
                    alreadyShifted.append(j)

        self.badWires = 0
        self.checkAngles()
        # self.checkLength()

        # fins optimized solution for shift

    def adjustShift(self):
        array = []
        self.shiftWires(-2)
        array.append(self.badWires)
        self.shiftWires(1)
        array.append(self.badWires)
        self.shiftWires(1)
        array.append(self.badWires)
        self.shiftWires(1)
        array.append(self.badWires)
        self.shiftWires(1)
        array.append(self.badWires)
        bestCase = array.index(min(array))
        self.shiftWires(-2)
        self.shiftWires(bestCase - 2)


def drawQFN(string, resizeFactor, canvas):
    output.delete("all")
    qfn = vQFN(string + ".lef", resizeFactor, canvas)

    # Outer Rect(Package)
    qfn.drawOuterRect()

    # paddle
    qfn.drawPaddle()

    # Inner Rect
    qfn.drawInnerRect()

    # Mid Rect
    qfn.drawMidRect()

    # Image
    qfn.drawImage()
    # pads
    qfn.drawPads()

    # pins
    qfn.drawPinsLeft()
    qfn.drawPinsBottom()
    qfn.drawPinsRight()
    qfn.drawPinsTop()

    # wires
    qfn.drawWires()

    # Crossover correction

    qfn.fixCrossover()

    qfn.adjustShift()

    # qfn.checkLength()

    return qfn


def drawBiggerQFN(string, resizeFactor, canvas, pinRange):
    output.delete("all")
    qfn = vQFN(string + ".lef", resizeFactor, canvas)

    qfn.changePinRange(pinRange)

    # Outer Rect(Package)
    qfn.drawOuterRect()

    # paddle
    qfn.drawPaddle()

    # Inner Rect
    qfn.drawInnerRect()

    # Mid Rect
    qfn.drawMidRect()

    # Image
    qfn.drawImage()
    # pads
    qfn.drawPads()

    # pins
    qfn.drawPinsLeft()
    qfn.drawPinsBottom()
    qfn.drawPinsRight()
    qfn.drawPinsTop()

    # wires
    qfn.drawWires()

    # Crossover correction

    qfn.fixCrossover()

    qfn.adjustShift()

    # qfn.checkLength()

    return qfn


def centerIterator(list):
    result = []
    countRight = 1
    countLeft = 1
    center = round((len(list) - 1) / 2)

    result.append(list[center])

    while True:
        if center - countLeft < 0:
            break
        try:
            result.append(list[center + countRight])
            countRight += 1
        except:
            pass
        result.append(list[center - countLeft])
        countLeft += 1

    return result


def Enter(e):
    clickEntry()


def clickEntry():
    entered_text = entry.get()
    jomama = "User: " + entered_text + "\n"
    text.insert(END, jomama)
    jomama = ""
    entry.delete(0, END)
    CMI(entered_text)


def hoverPad(e):

    try:
        qfn = packageMemory[-1]
        pinNames = qfn.getPinNames()
        x = output.canvasx(e.x)
        y = output.canvasy(e.y)
        try:
            for i in qfn.getPads():
                box = qfn.getCanvas().bbox(i)
                if box[0] <= x <= box[2] and box[1] <= y <= box[3]:

                    name = (
                        pinNames[qfn.getPads().index(i)]
                        + "          position: "
                        + str(output.canvasx(e.x))
                        + ", "
                        + str(output.canvasy(e.y))
                    )
                    statusLabel.config(text="Pin: " + name)

        except:
            pass
    except:
        pass


def moveLine(e):
    qfn = packageMemory[-1]
    outputItem = qfn.getCanvas().find_withtag("current")
    try:
        x0, y0, x1, y1 = qfn.getCanvas().coords(outputItem)
    except:
        pass

    try:
        if outputItem[0] in qfn.getWires():
            if qfn.getSwitch():
                qfn.getCanvas().coords(
                    outputItem,
                    x0,
                    y0,
                    qfn.getCanvas().canvasx(e.x),
                    qfn.getCanvas().canvasy(e.y),
                )
                qfn.getCanvas().itemconfig(outputItem, fill="#39FF14")
            else:
                qfn.getCanvas().coords(
                    outputItem,
                    qfn.getCanvas().canvasx(e.x),
                    qfn.getCanvas().canvasy(e.y),
                    x1,
                    y1,
                )
                qfn.getCanvas().itemconfig(outputItem, fill="#39FF14")
    except:
        pass
    pass


def release(e):
    qfn = packageMemory[-1]
    try:
        outputItem = qfn.getCanvas().find_withtag("current")
        x0, y0, x1, y1 = qfn.getCanvas().coords(outputItem)
        try:
            if outputItem[0] in qfn.getWires():
                qfn.getCanvas().itemconfig(outputItem, fill="#0000FF")
                if qfn.getSwitch():
                    for i in qfn.getPins():
                        box = qfn.getCanvas().bbox(i)
                        tuple = qfn.getCanvas().find_overlapping(
                            box[0], box[1], box[2], box[3]
                        )
                        myList = list(tuple)
                        if outputItem[0] in myList:
                            qfn.getCanvas().coords(
                                outputItem,
                                x0,
                                y0,
                                (box[0] + box[2]) / 2,
                                (box[1] + box[3]) / 2,
                            )
                else:
                    for i in qfn.getPads():
                        box = qfn.getCanvas().bbox(i)
                        tuple = qfn.getCanvas().find_overlapping(
                            box[0], box[1], box[2], box[3]
                        )
                        myList = list(tuple)
                        if outputItem[0] in myList:
                            qfn.getCanvas().coords(
                                outputItem,
                                (box[0] + box[2]) / 2,
                                (box[1] + box[3]) / 2,
                                x1,
                                y1,
                            )
                qfn.checkAngles()
                # qfn.checkLength()
        except:
            pass
    except:
        pass


def writeImage(string):
    x = window.winfo_rootx() + output.winfo_rootx()
    y = window.winfo_rooty() + output.winfo_rooty()
    x1 = x + output.winfo_width()
    y1 = y + output.winfo_height()
    ImageGrab.grab().crop((x, y, x1, y1)).save(string.split()[-1])


def CMI(string):

    split = string.split()

    if "help" in split:
        text.insert(END, "'generate <chip name>' to generate diagram" + "\n")
        text.insert(
            END,
            "'* <chip name>' to automatically generate 1 extra pin for each side"
            + "\n",
        )
        text.insert(
            END,
            "'save as <file name.filetype> to save the canvas image (svg supported)"
            + "\n",
        )
        text.insert(END, "resize <scale factor (default 15)> to zoom in or out" + "\n")
        text.insert(END, "delete <wire number>" + "\n")
        text.insert(END, "shift <shift over number>" + "\n")
        text.insert(END, "'check' to verify wire angles" + "\n")
        text.insert(END, "'a' to switch wire anchor for dragging" + "\n")
        text.insert(END, "'+ <int> to add pins to each side of the package'" + "\n")

    elif "*" in split:
        output.delete("all")
        packageMemory.append(drawBiggerQFN(split[-1], 15, output, 1))
    elif "generate" in split:
        output.delete("all")
        packageMemory.append(drawQFN(split[-1], 15, output))

    elif "save as" in string:

        if "svg" not in string:
            writeImage(string)
            text.insert(END, "Image saved successfully" + "\n")
        else:
            canvasvg.saveall(split[-1], output, items=None, margin=10, tounicode=None)
            text.insert(END, "SVG file saved successfully" + "\n")

    elif "resize" in split:
        packageMemory.append(
            drawQFN(packageMemory[-1].getName(), int(split[-1]), output)
        )

    elif "delete" in split:
        packageMemory[-1].getCanvas().delete(
            packageMemory[-1].getWires()[int(split[-1])]
        )
    elif "shift" in split:

        packageMemory[-1].shiftWires(int(split[-1]))
        packageMemory[-1].checkAngles()

    elif "check" in split:
        packageMemory[-1].checkAngles()

    elif "a" in split:
        packageMemory[-1].flipSwitch()
        text.insert(END, "Switched wire acnhor" + "\n")

    elif "+" in split or "-" in split:
        packageMemory.append(
            drawBiggerQFN(
                packageMemory[-1].getName(),
                packageMemory[-1].getResizeFactor(),
                output,
                int(split[-1]),
            )
        )
    elif "wireLength" in split:

        packageMemory[-1].setLengths(split[-2], split[-1])
        packageMemory[-1].checkLength()

    else:
        text.insert(END, "Error: " + string + " is not a valid command" + "\n")


window = Tk()
window.title("Wirebonding")
window.geometry("770x1080")
window.configure(background="white")

frame = Frame(window)
frame.pack(expand=True, fill=BOTH)

w = Label(frame, text="Output")
w.pack()
output = Canvas(frame, width=1500, bg="white", height=400)

xscrollbar = ttk.Scrollbar(frame, orient="horizontal")
xscrollbar.pack(side=BOTTOM, fill=X)
xscrollbar.config(command=output.xview)

yscrollbar = ttk.Scrollbar(frame, orient="vertical")
yscrollbar.pack(side=RIGHT, fill=Y)
yscrollbar.config(command=output.yview)

statusLabel = Label(frame, text="Pin: ", anchor=W)
statusLabel.pack(fill=X, side=BOTTOM)

output.config(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
output.pack(side=LEFT, expand=True, fill=BOTH)

frame1 = Frame(window)
frame1.pack()

entry = Entry(frame1, width=980, bg="white")
entry.pack()

Button(frame1, text="Enter Commands", width=15, command=clickEntry).pack(fill=X)

text = Text(frame1, width=190, height=15, background="white")
text.pack()

# y1scrollbar = ttk.Scrollbar(frame1, orient='vertical')
# y1scrollbar.pack(side = RIGHT, fill = Y)
# y1scrollbar.config(command=output.yview)
output.bind("<B1-Motion>", moveLine)
output.bind("<Motion>", hoverPad)
output.bind("<ButtonRelease-1>", release)
entry.bind("<Return>", Enter)

window.mainloop()
