from xml.etree import ElementTree as ET
from constructor import ConstructAssemblyFromXML
from rotation import rotate, reduce

def str3(value):
    return "%.3f" % value

def str8(value):
    return "%.8f" % value

SMX_FILE = 'test2.smx'
AVL_FILE = 'test2.avl'


tree = ET.parse(SMX_FILE)
root = tree.getroot()

assembly = ConstructAssemblyFromXML(root)
assembly.addControlSys()
assembly.check()
# assembly.plot()

Mach = 0.3
Nchord = 12
Cspace = 1.0
Nspanwise = 26
Sspace = -1.1
COMPOENT = 1
YDUPLICATE = 0

lines = list()
lines.append("SUMO TO AVL GEOMETRY")

lines.append("#Mach")
lines.append(str(Mach)+'\n')

lines.append("\t".join(['#IYsym', 'IZsym', 'Zsym']))
lines.append("0\t0\t0\n")

lines.append('\t'.join(['#Sref', 'Cref', 'Bref']))
lines.append("1260\t11\t113\n")

lines.append('\t'.join(['#Xref', 'Yref', 'Zref']))
lines.append("60\t0\t0\n")

for wing in assembly.wingSkeletons:

    lines.append("#================================================")

    lines.append("SURFACE")
    lines.append(wing.name)

    lines.append('\t'.join(['#Nchord', 'Cspace', 'Nspan', 'Sspace']))
    lines.append(f"{Nchord}\t{Cspace}\t{Nspanwise}\t{Sspace}\n")

    # lines.append(f"COMPONENT\n{COMPOENT}")

    if 'autosym' in wing.flags:
        lines.append(f"YDUPLICATE\n{YDUPLICATE}\n")
    else:
        pass

    lines.append("ANGLE")
    lines.append(str(wing.rotate[1]) + '\n')

    lines.append("SCALE")
    lines.append("1.0 1.0 1.0\n")

    lines.append("TRANSLATE")
    lines.append('\t'.join([str(num) for num in wing.origin]) + '\n')

    for section in wing.wingSecs[::-1]:

        lines.append("#--------------------------------")

        lines.append("SECTION")
        lines.append('#' + section.name + '\n')

        lines.append('\t'.join(['#Xle', 'Yle', 'Zle', 'chord', 'angle', 'Nspan', 'Sspace']))
        pos = rotate(wing.rotate, section.center)
        pos.append(section.chord)
        pos.append(section.twist)
        lines.append('\t'.join([str3(x) for x in pos]) + '\n')

        lines.append("AIRFOIL")
        pts = [str8(pt) + '\n' if i%2==1 else str8(pt) + ' ' for i,pt in enumerate(reduce(section.points))]
        lines.append(''.join(pts))
        # lines.append("AFIL")
        # lines.append("ag35.dat" + "\n")

        key = wing.name + '###' + section.name
        if key in assembly.ctrlInfo:
            lines.append("CONTROL")
            lines.append('\t'.join(['#name', 'gain', 'Xhinge', 'XYZhvec', 'SgnDup']))
            for info in assembly.ctrlInfo[key]:
                lines.append('\t'.join([info.name, "1.0", str3(info.Xhinge), "0 0 0", str(info.SgnDup)]))

with open(AVL_FILE, 'w') as file:
    file.write("\n".join(lines).expandtabs(8))


