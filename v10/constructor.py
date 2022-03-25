from datastructure import *

# ---------------- Constructor Functions ------------------------- #
def ConstructAssemblyFromXML(root):
    assembly = Assembly()

    assembly.wingSkeletons = [ConstructWingSkeleton(item) for item in root.findall('WingSkeleton')]
    assembly.hingePoints, assembly.controlPatterns = ConstructControlSystem(root.find('ControlSystem'))

    return assembly

def ConstructWingSkeleton(wingSkeleton):
    wing = WingSkeleton()

    wing.flags = wingSkeleton.attrib['flags']
    wing.name = wingSkeleton.attrib['name']
    wing.origin = [float(x) for x in wingSkeleton.attrib['origin'].strip().split()]
    wing.rotate = [float(x) for x in wingSkeleton.attrib['rotation'].strip().split()]
    wing.wingSecs = [ConstructWingSection(item) for item in wingSkeleton.findall('WingSection')]

    return wing


def ConstructWingSection(wingSection):
    section = WingSection()

    section.airfoil = wingSection.attrib['airfoil']
    section.name = wingSection.attrib['name']
    section.chord = float(wingSection.attrib['chord'])
    section.dihedral = float(wingSection.attrib['dihedral'])
    section.twist = float(wingSection.attrib['twist'])
    section.yaw = float(wingSection.attrib['yaw'])
    section.center = [float(x) for x in wingSection.attrib['center'].strip().split()]
    section.points = [float(x) for x in wingSection.text.strip().split()]

    return section

def ConstructControlSystem(controlSys):

    hingePoints = ConstructHingePoints(controlSys.findall('ControlSrf'))
    ctrlPatterns = [ConstructControlPattern(item) for item in controlSys.findall('Control')]

    for ctrlPattern in ctrlPatterns:
        for idname,idnum in zip(ctrlPattern.idname,ctrlPattern.idnum):
            id_hp = [id for id,hp in enumerate(hingePoints) if hp.name == idname]
            ctrlPattern.hinge1.append(id_hp[idnum])
            ctrlPattern.hinge2.append(id_hp[idnum+1])

    return hingePoints, ctrlPatterns


def ConstructControlPattern(control):
    ctrlPattern = ControlPattern()

    ctrlPattern.name = control.attrib['name']

    for item in control.findall('Participation'):
        factor = float(item.attrib['factor'])
        id = item.attrib['id'].split('Segment')

        ctrlPattern.factor.append(factor)
        ctrlPattern.idname.append(id[0])

        if len(id) > 1:
            ctrlPattern.idnum.append(int(id[1]))
        else:
            ctrlPattern.idnum.append(int(0))

    return ctrlPattern


def ConstructHingePoints(controlSurf):
    hingePoints = list()

    for surf in controlSurf:
        for hinge in surf.findall('Hingepoint'):
            hp = HingePoint()
            hp.name = surf.attrib['name']
            hp.wing = surf.attrib['wing']
            hp.type = surf.attrib['type']
            hp.chordpos = float(hinge.attrib['chordpos'])
            hp.spanpos = float(hinge.attrib['spanpos'])

            hingePoints.append(hp)

    return hingePoints
