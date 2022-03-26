import matplotlib.pyplot as plt

# ----------------- Class Definitions ----------------------------------#
# --------- WingSkeletion -------------------#
class Assembly:
    def __init__(self):
        self.wingSkeletons = list()     # list of WingSkeleton ('WingSkeletion')
        self.controlPatterns = list()   # list of ControlPattern ('Control')
        self.hingePoints = list()       # list of HingePoints ('ControlSrf')
        self.ctrlInfo = dict()         # mapping the control system to sections

    def plot(self):
        __plot__(self)

        plt.show()

    def check(self):
        print("Checking WingSkeletons ...")
        for wing in self.wingSkeletons:
            wing.check()
        print("Checking Control Patterns ...")
        for pattern in self.controlPatterns:
            pattern.check()
        print("Checking Hinge Points ...")
        for id, hinge in enumerate(self.hingePoints):
            print(f"\t{id}", end='')
            hinge.check()
        print("Checking Control Info ...")
        for key in self.ctrlInfo:
            print("\t" + key + f"\t{[info.name for info in self.ctrlInfo[key]]}")
        print("Checking Finished ...........\n")

    def addControlSys(self):
        __addControlSys__(self)

# --------- WingSkeletion -------------------#
class WingSkeleton:
    def __init__(self):
        self.flags = ""
        self.name = ""
        self.origin = None
        self.rotate = None
        self.wingSecs = None

    # .............................
    def check(self):
        print(f"\t{self.name:<16s}", end='')
        if self.rotate[2] != 0.0:
            print("*** non-zero yaw ***", end='')
        if self.rotate[0] != 0.0 and self.rotate[1] != 0.0:
            print("*** non-zero roll and pitch ***", end='')
        print("")
        for section in self.wingSecs:
            section.check()

    def plot(self):
        __WingSkeleton_plot__(self)

    # ...............................
    def addCtrlSections(self, ctrlSpanPos):
        __addCtrlSections__(self, ctrlSpanPos)

    def GetWingSecName(self, spanpos):
        id = self.GetWingSecId(spanpos)
        return self.wingSecs[id].name if id is not None else ""

    def GetWingSecId(self, spanpos):
        LE_y = [sec.center[1] for sec in self.wingSecs]

        maxPos = max(LE_y)
        minPos = min(LE_y)
        SPAN = maxPos - minPos

        fac = 2 if "autosym" in self.flags else 1
        pos = maxPos - fac * spanpos * SPAN

        id = __findIndex__(LE_y, pos)[0]

        return id


# --------- WingSection -------------------#
class WingSection:
    def __init__(self):
        self.airfoil = ""
        self.name = ""
        self.chord = None
        self.dihedral = None
        self.twist = None
        self.yaw = None
        self.center = None
        self.points = None

    # .................................
    def check(self):
        print(f"\t\t{self.name:<24s}", end='')
        if self.yaw != 0.0:
            print("*** non-zero z-rotation ***", end='')
        if len(self.points) % 2 != 0 or len(self.points) >= 600:
            print("*** incorrect number of airfoil points ****", end='')
        print("")

    def plot(self):
        style = '--' if 'interp' in self.name else '-'
        plt.plot(self.points[0::2], self.points[1::2], style, label=self.name)


#-------------------- ControlPattern Class ---------------------------#
class ControlPattern:
    def __init__(self):
        self.name = ""
        self.factor = list()
        self.idname = list()
        self.idnum = list()
        self.hinge1 = list()        # list of left hinge id in Assembly::hingePoints list
        self.hinge2 = list()        # list of right hinge id in Assembly::hingePoints list


    def check(self):
        print(f"\t{self.name}")
        for factor, idname, idnum, h1, h2 in zip(self.factor,self.idname,self.idnum, self.hinge1, self.hinge2):
            print(f"\t\t{idname}-{idnum}, Factor = {factor}, Hinge-1 id = {h1}, Hinge-2 id = {h2}")


# ---------------------- HingePoints Class ----------------------------#
class HingePoint:
    def __init__(self):
        self.name = ""
        self.type = ""
        self.wing = ""
        self.spanpos = None
        self.chordpos = None
        self.section = None

    def check(self):
        print(f"\t{self.name} type = {self.type} wing = {self.wing} sec = {self.section} span = {self.spanpos}, chord = {self.chordpos}")


class Info:
    def __init__(self):
        self.name = ""
        self.Xhinge = None
        self.SgnDup = None


# ------------------------- Functions ---------------------------------- #
def __addControlSys__(self):

    for wing in self.wingSkeletons:
        ctrlSpanPos = [hp.spanpos for hp in self.hingePoints if hp.wing == wing.name]
        if ctrlSpanPos:
            wing.addCtrlSections(ctrlSpanPos)

    for part in self.controlPatterns:
        for idnum, idname, hinge1, hinge2 in zip(part.idnum, part.idname, part.hinge1, part.hinge2):
            for hinge in [hinge1, hinge2]:
                spanpos = self.hingePoints[hinge].spanpos
                chordpos = self.hingePoints[hinge].chordpos
                wingname = self.hingePoints[hinge].wing
                hingetype = self.hingePoints[hinge].type
                wing = [wing for wing in self.wingSkeletons if wing.name == wingname][0]

                info = Info()
                info.name = part.name
                info.Xhinge = chordpos if hingetype == 'TEF' else (0 - chordpos)
                info.SgnDup = 1 if max(part.factor) * min(part.factor) > 0 else -1

                secname = wing.GetWingSecName(spanpos)
                self.hingePoints[hinge].section = secname

                if secname:                     # secname is not empty
                    key = wing.name + '###' + secname
                    if key in self.ctrlInfo:
                        self.ctrlInfo[key].append(info)
                    else:
                        self.ctrlInfo[key] = [info]
                else:                           # secname is empty because hingePoint is on the left wing
                    continue


def __addCtrlSections__(self, ctrlSpanPos):

    if not ctrlSpanPos or ctrlSpanPos is None:
        return

    LE_y = [sec.center[1] for sec in self.wingSecs]

    maxSpanPos = max(LE_y)
    minSpanPos = min(LE_y)
    SPAN = maxSpanPos - minSpanPos

    if "autosym" in self.flags:
        ctrlPos = [maxSpanPos - 2 * pos * SPAN for pos in ctrlSpanPos if pos <= 0.5]
    else:
        ctrlPos = [maxSpanPos - pos * SPAN for pos in ctrlSpanPos if pos <= 1.0]


    ids = [__findIndex__(LE_y, pos) for pos in ctrlPos]

    ctrlSecs = [__interpSection__(self.wingSecs[id2], self.wingSecs[id1], pos) \
                   for pos, (id1,id2) in zip(ctrlPos, ids)]

    for pos, newsec in zip(ctrlPos, ctrlSecs):
        id1, id2 = __findIndex__(LE_y, pos)

        if id1 != id2:
            LE_y.insert(id1, pos)
            self.wingSecs.insert(id1, newsec)
        else:   # do nothing because ctrlSec coincides with exising sections
            pass


def __interpSection__(rightSec, leftSec, pos):
    from interploate import interpSection
    return interpSection(rightSec, leftSec, pos, WingSection())


def __findIndex__(posList, newpos):
    id1 = None
    id2 = None

    if newpos > max(posList) or newpos < min(posList):
        return id1, id2

    for id, pos in enumerate(posList):
        if pos > newpos:
            continue
        elif abs(pos - newpos) < 0.001:     # # wingroot - id1 = pos/newpos = id2 - wingtip
            id1 = id
            id2 = id
            break
        else:                               # wingroot - id1 < pos < id2 - wingtip
            id1 = id
            id2 = id1 - 1 if id1 >= 1 else id1
            break

    return id1, id2


def __plot__(self):
        for wing in self.wingSkeletons:
            wing.plot()

        for part in self.controlPatterns:
            for idnum, idname, hinge1, hinge2 in zip(part.idnum, part.idname, part.hinge1, part.hinge2):
                hps = list()
                for hinge in [hinge1, hinge2]:
                    secname = self.hingePoints[hinge].section
                    wingname = self.hingePoints[hinge].wing
                    chordpos = self.hingePoints[hinge].chordpos

                    if not secname:             # empty secname because hinge on the left wing
                        break

                    wing = [wing for wing in self.wingSkeletons if wing.name == wingname][0]
                    sec = [sec for sec in wing.wingSecs if sec.name == secname][0]

                    rotve = wing.rotate
                    trans = wing.origin

                    chord = sec.chord
                    center = sec.center

                    from rotation import translate, rotate
                    hp = translate([chordpos * chord, 0, 0], center)
                    hp = rotate(rotve, hp)
                    hp = translate(trans, hp)

                    hps.append(hp)

                if not hps:
                    break

                import numpy as np  # covert to 2D array
                hps = np.array(hps)

                plt.figure(1000)
                plt.plot(hps[:,0], hps[:,1], '--og')

                plt.figure(2000)
                plt.plot(hps[:,0], hps[:,2], '--og')


def __WingSkeleton_plot__(self):
    trans = self.origin
    rotve = self.rotate

    # plot leading edges (le) and trailing edges (te)
    from rotation import translate, rotate
    le = [sec.center for sec in self.wingSecs]
    te = [translate([sec.chord, 0, 0], pos) for sec, pos in zip(self.wingSecs, le)]

    # rotate first
    le = [rotate(rotve, pos) for pos in le]
    te = [rotate(rotve, pos) for pos in te]

    # translate second
    le = [translate(trans, pos) for pos in le]
    te = [translate(trans, pos) for pos in te]

    import numpy as np          # covert to 2D array
    le = np.array(le)
    te = np.array(te)

    # figure-1: X-Y plot
    plt.figure(1000)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.plot(le[:, 0], le[:, 1], '-or')
    plt.plot(te[:, 0], te[:, 1], '-ob')

    for l, t in zip(le, te):
        plt.plot([l[0], t[0]], [l[1], t[1]], '-y')

    # figure-2: X-Z plot
    plt.figure(2000)
    plt.xlabel("X")
    plt.ylabel("Z")
    plt.plot(le[:, 0], le[:, 2], '-or')
    plt.plot(te[:, 0], te[:, 2], '-ob')

    for l, t in zip(le, te):
        plt.plot([l[0], t[0]], [l[2], t[2]], '-y')

    # figure-3: Y-Z plot
    plt.figure(3000)
    plt.xlabel("Y")
    plt.ylabel("Z")
    plt.plot(le[:, 1], le[:, 2], '-or')
    plt.plot(te[:, 1], te[:, 2], '-ob')

    for l, t in zip(le, te):
        plt.plot([l[1], t[1]], [l[2], t[2]], '-y')

    # figure-4: airfoil plot
    plt.figure(4000)
    plt.xlabel("CHORD")
    for sec in self.wingSecs:
        sec.plot()

    plt.legend()

