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

sys.path.insert(1, "C:/Users/pasca/Desktop/Projects/WirebondingV2/canvas2svg-master")
import canvasvg
import test

# sys.setrecursionlimit(1500)

# tags
# given which wires are connected to pads and pins, write pins numbered top left
# as soon as wire is attached, pin name must be knowshift - pin 1 - 12, list names
# generate pin packaging pinout
# mapping of names to pin numbers

# Rules
# max length 3mm
# wire to bond pad center 120 um
# wire to package pad um
# min wire angle to die edge 40degrees

#


packageMemory = []
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
    # to find the orientation of an ordered triplet (p,q,r)
    # function returns the following values:
    # 0 : Colinear points
    # 1 : Clockwise points
    # 2 : Counterclockwise

    # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/
    # for details of below formula.

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


class vQFN:
    def __init__(self, string, resizeFactor, canvas):
        self.string = string
        self.lefReader = test.lefReader(string, resizeFactor)
        self.pads = []
        self.array = self.lefReader.getCoordinates()
        for i in self.array:
            self.pads.append(Rectangle(i[0], i[1], i[2], i[3]))
        self.dim = self.lefReader.getDim()
        self.wires = []
        self.img = None
        self.imgDimx = None
        self.imgDimy = None
        self.pins = []
        self.takenPins = []
        self.center = None
        self.centers = None
        self.pinRange = None
        self.padItems = []
        self.distanceToPins = []
        self.central = None
        self.resizeFactor = resizeFactor
        self.canvas = canvas
        self.Initialize()
        self.switch = True
        self.left = None
        self.bottom = None
        self.right = None
        self.top = None

    def getName(self):
        return self.string[:-4]

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

    def Initialize(self):

        self.centers = self.getCenters()
        self.central = self.centralPad()
        self.center = [
            (self.central[0] + self.central[2]) / 2,
            (self.central[1] + self.central[3]) / 2,
        ]
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
        # Pads by Pins

    def drawImage(self):
        self.canvas.create_image(self.center[0], self.center[1], image=self.img)

    def drawInnerRect(self):
        self.canvas.create_rectangle(
            self.central[0], self.central[1], self.central[2], self.central[3]
        )

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

    def changePinRange(self, number):
        self.numberSide += number

        self.pinRange = (
            (2 * self.numberSide) + 1
        ) * 500 / self.resizeFactor / 2 - 500 / self.resizeFactor
        self.canvas.delete("all")

    def getCenterRect(self, i):
        bounds = self.canvas.bbox(i)
        print
        return [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2]

    def distance(self, i, j):
        i = self.getCenterRect(i)
        j = self.getCenterRect(j)
        x = i[0] - j[0]
        y = i[1] - j[1]

        return math.hypot(x, y)

    def checkLength(self):
        for i in self.wires:
            x0, y0, x1, y1 = self.canvas.coords(i)

            x = x0 - x1
            y = y0 - y1

            if not (
                1000 / self.resizeFactor <= math.hypot(x, y) <= 3000 / self.resizeFactor
            ):
                self.canvas.itemconfig(i, fill="red")

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
            if (
                max(xArray) - 50 / self.resizeFactor
                <= self.getCenterRect(i)[0]
                <= max(xArray) + 50 / self.resizeFactor
            ):
                right.append(i)
            if (
                max(yArray) - 50 / self.resizeFactor
                <= self.getCenterRect(i)[1]
                <= max(yArray) + 50 / self.resizeFactor
            ):
                top.append(i)
            if (
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

        for i in left + bottom + right + top:
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

                    # self.fixCrossover()
                    # statement improves wirebonding at the expense of memory issues

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
                                    else:
                                        self.canvas.itemconfig(l, fill="#0000FF")

                                else:
                                    if math.atan(y / (x + 1)) < math.radians(40):
                                        self.canvas.itemconfig(l, fill="red")
                                    else:
                                        self.canvas.itemconfig(l, fill="#0000FF")

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

        self.checkAngles()


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

    qfn.fixCrossover()

    qfn.checkAngles()

    qfn.checkLength()

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

    qfn.checkAngles()

    qfn.checkLength()

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
                qfn.checkLength()
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
    if "generate" in string:
        output.delete("all")
        packageMemory.append(drawQFN(string.split()[-1], 15, output))

    elif "save as" in string:

        if "svg" not in string:
            writeImage(string)
            text.insert(END, "Image saved successfully" + "\n")
        else:
            canvasvg.saveall(
                string.split()[-1], output, items=None, margin=10, tounicode=None
            )
            text.insert(END, "SVG file saved successfully" + "\n")

    elif "resize" in string:
        packageMemory.append(
            drawQFN(packageMemory[-1].getName(), int(string.split()[-1]), output)
        )
    elif "delete" in string:
        packageMemory[-1].getCanvas().delete(
            packageMemory[-1].getWires()[int(string.split()[-1])]
        )
    elif "shift" in string:

        packageMemory[-1].shiftWires(int(string.split()[-1]))
        packageMemory[-1].checkAngles()

    elif "check" in string:
        packageMemory[-1].checkAngles()

    elif "a" in string:
        packageMemory[-1].flipSwitch()
        text.insert(END, "Switched wire acnhor" + "\n")

    elif "+" in string or "-" in string:
        packageMemory.append(
            drawBiggerQFN(
                packageMemory[-1].getName(),
                packageMemory[-1].getResizeFactor(),
                output,
                int(string.split()[-1]),
            )
        )

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
output.bind("<ButtonRelease-1>", release)
entry.bind("<Return>", Enter)

window.mainloop()
