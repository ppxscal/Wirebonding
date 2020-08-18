from tkinter import *
import readLef as lef
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image, ImageGrab
#import resizeimage
import svgwrite
import math
import sys
sys.path.insert(1, 'C:/Users/pasca/Desktop/Projects/Wirebonding/canvas2svg-master')
import canvasvg

# generate frequency_divid

# tags
# add extra - double bond to same package pad
# snap to center
# pick up either end of wire

# size for fre_divid is 664x664 microns know chip dimensions
# given which wires are connected to pads and pins, write pins numbered top left
# as soon as wire is attached, pin name must be known - pin 1 - 12, list names
# generate pin packaging pinout
# mapping of names to pin numbers


# Rules
# max length 3mm
# wire tp bond pad center 120um
# wire to package pad 120um
# min wire angle to die edge 40degrees

projectNames = []
resizeStates = [15]


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Given three colinear points p, q, r, the function checks if


# point q lies on line segment 'pr'
def onSegment(p, q, r):
    if ((q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
            (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
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
    if (val > 0):

        # Clockwise orientation
        return 1
    elif (val < 0):

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
    if ((o1 != o2) and (o3 != o4)):
        return True

    # Special Cases

    # p1 , q1 and p2 are colinear and p2 lies on segment p1q1
    if ((o1 == 0) and onSegment(p1, p2, q1)):
        return True

    # p1 , q1 and q2 are colinear and q2 lies on segment p1q1
    if ((o2 == 0) and onSegment(p1, q2, q1)):
        return True

    # p2 , q2 and p1 are colinear and p1 lies on segment p2q2
    if ((o3 == 0) and onSegment(p2, p1, q2)):
        return True

    # p2 , q2 and q1 are colinear and q1 lies on segment p2q2
    if ((o4 == 0) and onSegment(p2, q1, q2)):
        return True

    # If none of the cases
    return False


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


def clearInfo():
    globalWires.clear()
    globalPins.clear()


def clickEntry():
    entered_text = entry.get()
    jomama = "User: " + entered_text + "\n"
    text.insert(END, jomama)
    jomama = ""
    entry.delete(0, END)
    CMI(entered_text)


def moveLine(e):
    outputItem = output.find_withtag('current')
    try:
        x0, y0, x1, y1 = output.coords(outputItem)
    except:
        pass

    try:

        if outputItem[0] in wires:
            if (abs(output.canvas(e.x) - x0) + abs(output.canvas(e.y - y0)) >= (abs(output.canvas(e.x) - x1) + abs(output.canvas(e.y - y1)))):
                    output.coords(outputItem,output.canvasx(e.x), output.canvasy(e.y), x1, y1)
                    output.itemconfig(outputItem, fill='blue')
                    print("inside")
                    
            else:
                output.coords(outputItem, x0, y0, output.canvasx(e.x), output.canvasy(e.y))
                output.itemconfig(outputItem, fill='blue')

                print("outside")
                
            
    except:
        pass


#output.create_rectangle(center[0] - pinRange / 2,
#                            center[1] - pinRange / 2,
#                            center[0] + pinRange / 2,
#                            center[1] + pinRange / 2, fill='silver')




def release(e):

    try:
        outputItem = output.find_withtag('current')
        x0, y0, x1, y1 = output.coords(outputItem)
        try:
            if outputItem[0] in wires:
                output.itemconfig(outputItem, fill='red')
                whichPin = None
                for i in pins:
                    box = output.bbox(i)
                    tuple = output.find_overlapping(box[0], box[1], box[2], box[3])
                    myList = list(tuple)
                    if outputItem[0] in myList:
                            output.coords(outputItem, x0, y0, (box[0] + box[2]) /2, (box[1] + box[3]) /2)

        except:
            pass
    except:
        pass

def Enter(e):
    clickEntry()


def CMI(string):
    if "generate" in string:
        projectNames.append(string[9: len(string)])
        drawQFN(string[9: len(string)] + ".lef", 0, 15)
    elif "shift" in string:
        output.delete("all")
        wires.clear()
        pins.clear()
        drawQFN(projectNames[-1] + ".lef", int(string.split()[-1]), resizeStates[-1])


    elif "delete" in string:
        output.delete(int(string.split()[-1]) * 2 + 32)

    elif "save as" in string:
        writeImage(string)
        text.insert(END, "Image saved successfully")

    elif "resize" in string:
        output.delete('all')
        wires.clear()
        pins.clear()
        resizeStates.append(int(string.split()[-1]))
        drawQFN(projectNames[-1] + ".lef", 0, int(string.split()[-1]))
    elif "write svg as" in string:
        canvasvg.saveall(string.split()[-1], output, items=None, margin=10, tounicode=None)
    else:
        text.insert(END, "Error: " + string + " is not a valid command" + "\n")


def writeImage(string):
    x = window.winfo_rootx() + output.winfo_rootx()
    y = window.winfo_rooty() + output.winfo_rooty()
    x1 = x + output.winfo_width()
    y1 = y + output.winfo_height()
    ImageGrab.grab().crop((x, y, x1, y1)).save(string.split()[-1])


def getCenterRect(i):
    bounds = output.bbox(i)
    return [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2]


def distance(i, j):
    i = getCenterRect(i)
    j = getCenterRect(j)

    x = i[0] - j[0]
    y = i[1] - j[1]

    return math.hypot(x, y)


window = Tk()

img = None

window.title("Wirebonding")
window.geometry('770x1080')
window.configure(background="white")

frame = Frame(window)
frame.pack()

w = Label(frame, text="Output")
w.pack()
output = Canvas(frame, width=1500, bg="white", height=400)
output.pack()

yscrollbar = ttk.Scrollbar(frame, orient='vertical')
yscrollbar.pack(side=RIGHT, fill=Y)
yscrollbar.config(command=output.yview)

xscrollbar = ttk.Scrollbar(frame, orient='horizontal')
xscrollbar.pack(side=BOTTOM, fill=X)
xscrollbar.config(command=output.xview)

def drawQFN(string, shift, resizeFactor):
    global img
    global wires
    global pins
    global takenPins
    global center
    global pinRange
    pads = []
    wires = []
    pins = []
    takenPins = []
    #contains the indices of the taken pins
    distanceToPins = []

    output.delete('all')
    qfn = lef.vQFN(string, resizeFactor)
    coordinates = qfn.getCoordinates()
    centers = qfn.getCenters()
    central = qfn.centralPad()
    center = [(central[0] + central[2]) / 2, (central[1] + central[3]) / 2]
    numberSide = int(round(len(centers) / 4))
    pinRange = ((2 * numberSide) + 1) * 500 / resizeFactor / 2 - 500 / resizeFactor

    # Image resized from 1000x1000 - 215x215

    img = Image.open(string[:-4] + '.png')
    imgDimx = qfn.getDim()[0] / resizeFactor
    imgDimy = qfn.getDim()[1] / resizeFactor
    img = img.resize((int(round(imgDimx)), int(round(imgDimy))), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    count = 0
    # Inner Rect
    output.create_rectangle(central[0], central[1], central[2], central[3])
    # Mid Rect
    output.create_rectangle(center[0] - imgDimx / 2, center[1] - imgDimy / 2, center[0] + imgDimx / 2,
                            center[1] + imgDimy / 2)
    # Outer Rect(Package)
    output.create_rectangle(center[0] - pinRange / 2 - 1000 / resizeFactor,
                            center[1] - pinRange / 2 - 1000 / resizeFactor,
                            center[0] + pinRange / 2 + 1000 / resizeFactor,
                            center[1] + pinRange / 2 + 1000 / resizeFactor, fill='black')
    # paddle
    output.create_rectangle(center[0] - pinRange / 2,
                            center[1] - pinRange / 2,
                            center[0] + pinRange / 2,
                            center[1] + pinRange / 2, fill='silver')

    output.create_image(center[0], center[1], image=img)

    # pads
    for i in coordinates:
        pads.append(output.create_rectangle(i[0], i[1], i[2], i[3], fill = 'white'))

    # creating paddles
    # pin dimensions, .25mm wide, .25mm spacing, .5mm length, .5mm from paddle
    # order is left, bottom, right, top

    # left Pins
    for i in range(numberSide):
        pins.append(output.create_rectangle(center[0] - pinRange / 2 - 1000 / resizeFactor,
                                            center[1] - pinRange / 2 + 500 * i / resizeFactor,
                                            center[0] - pinRange / 2 - 500 / resizeFactor,
                                            center[1] - pinRange / 2 + 250 / resizeFactor + 500 * i / resizeFactor,
                                            fill='silver'))

        # wires.append(
        # output.create_line(getCenterRect(pins[i])[0], getCenterRect(pins[i])[1], centers[(i + shift)%12][0], centers[(i + shift)%12][1],
        # fill='red'))

    # bottom

    for i in range(numberSide):
        pins.append(output.create_rectangle(center[0] - pinRange / 2 + 500 * i / resizeFactor,
                                            center[1] + pinRange / 2 + 1000 / resizeFactor,
                                            center[0] - pinRange / 2 + 250 / resizeFactor + 500 * i / resizeFactor,
                                            center[1] + pinRange / 2 + 500 / resizeFactor, fill='silver'))
        # wires.append(output.create_line(
        # getCenterRect((pins[i + numberSide]))[0], getCenterRect(pins[i + numberSide])[1], centers[(i + numberSide + shift)%12][0],
        # centers[(i + numberSide + shift)%12][1], fill='red'))

    # right
    for i in range(numberSide):
        pins.append(output.create_rectangle(center[0] + pinRange / 2 + 1000 / resizeFactor,
                                            center[1] + pinRange / 2 - 500 * i / resizeFactor,
                                            center[0] + pinRange / 2 + 500 / resizeFactor,
                                            center[1] + pinRange / 2 - 250 / resizeFactor - 500 * i / resizeFactor,
                                            fill='silver'))
        # wires.append(output.create_line(
        # getCenterRect((pins[i + 2 * numberSide]))[0], getCenterRect(pins[i + 2 * numberSide])[1],
        # centers[(i + 2 * numberSide + shift)%12][0],
        # centers[(i + 2 * numberSide + shift)%12][1], fill='red'))

    # top

    for i in range(numberSide):
        pins.append(output.create_rectangle(center[0] + pinRange / 2 - 500 * i / resizeFactor,
                                            center[1] - pinRange / 2 - 1000 / resizeFactor,
                                            center[0] + pinRange / 2 - 250 / resizeFactor - 500 * i / resizeFactor,
                                            center[1] - pinRange / 2 - 500 / resizeFactor, fill='silver'))

    left = []
    bottom = []
    right = []
    top = []

    xArray = []
    yArray = []

    for i in pads:
        xArray.append(getCenterRect(i)[0])
        yArray.append(getCenterRect(i)[1])

    for i in pads:
        if getCenterRect(i)[0] == min(xArray):
            left.append(i)
        if getCenterRect(i)[0] == max(xArray):
            right.append(i)
        if getCenterRect(i)[1] == max(yArray):
            top.append(i)
        if getCenterRect(i)[1] == min(yArray):
            bottom.append(i)

    left = centerIterator(left)
    bottom = centerIterator(bottom)
    right = centerIterator(right)
    top = centerIterator(top)

    def drawWires(pads):
        for i in pads:
            for j in pins:
                distanceToPins.append(distance(i, j))
                # print(distanceToPins)
            for element in range(len(distanceToPins)):
                if element in takenPins:
                    distanceToPins[element] = sys.maxsize
            closest = distanceToPins.index(min(distanceToPins))
            #print(str(closest) + " distance: " + str(distanceToPins[closest]))
            locI = getCenterRect(i)
            locJ = getCenterRect(pins[closest])
            wires.append(output.create_line(locI[0], locI[1], locJ[0], locJ[1], fill='red'))
            takenPins.append(pins.index(pins[closest]))
            distanceToPins.clear()
        

    drawWires(left)
    drawWires(right)
    drawWires(bottom)
    drawWires(top)

    print(len(pads))
    print(len(wires))

    def checkCrossover(i):
        x0, y0, x1, y1 = output.coords(i)
        a1 = Point(x0, y0)
        a2 = Point(x1, y1)

        temp = list(wires)
        temp.remove(i)

        for j in temp:
            x01, y01, x11, y11 = output.coords(j)
            b1 = Point(x01, y01)
            b2 = Point(x11, y11)

            if not doIntersect(a1,a2,b1,b2):
                continue
            else:
                output.coords(i, x0, y0, x11, y11)
                output.coords(j, x01, y01, x1, y1)



    for i in wires:
        checkCrossover(i)
    for i in wires:
        checkCrossover(i)

    #doesnt quite work 

    for i in reversed(pins):
        centerCoorPin = getCenterRect(i)
        box = output.bbox(i)
        tuple = output.find_overlapping(box[0], box[1], box[2], box[3])
        myList = list(tuple)
        isThereWire = False
        for j in myList:
            if j in wires:
                isThereWire = True
        if not isThereWire or pins.index(i) == 0:
            box1 = output.bbox(pins[pins.index(i) - 1])
            tuple1 = output.find_overlapping(box[0], box[1], box[2], box[3])
            myList1 = list(tuple)
            for k in myList1:
                if k in wires:
                    output.coords(k, output.coords(k)[0], output.coords(k)[1], centerCoorPin[0] + 1, centerCoorPin[1] + 1)

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
output.bind('<B1-Motion>', moveLine)
output.bind('<ButtonRelease-1>', release)
entry.bind('<Return>', Enter)

window.mainloop()
