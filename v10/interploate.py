# -------------- interpolate related funcitons -------------#

def interpSection(rightSec, leftSec, pos, newSec):

    rpos = rightSec.center[1]
    lpos = leftSec.center[1]

    if rpos == lpos:
        return None

    lalpha = (rpos - pos) / (rpos - lpos)
    ralpha = (pos - lpos) / (rpos - lpos)

    newSec.name = f"interpolated-{pos:.3f}"
    newSec.center = [rc*ralpha+lc*lalpha for rc,lc in zip(rightSec.center,leftSec.center)]
    newSec.chord = ralpha*rightSec.chord + lalpha*leftSec.chord
    newSec.yaw = ralpha * rightSec.yaw + lalpha * leftSec.yaw
    newSec.twist = ralpha*rightSec.twist + lalpha*leftSec.twist
    newSec.dihedral = ralpha*rightSec.dihedral + lalpha*leftSec.dihedral

    newSec.points = interpAirfoilPoints(rightSec.points, leftSec.points, ralpha, lalpha)

    return newSec

def interpAirfoilPoints(rpts, lpts, ralpha, lalpha):
    from scipy.interpolate import interp1d

    rightSec_x, rightSec_y = normalize(rpts)
    leftSec_x, leftSec_y = normalize(lpts)

    rid = rightSec_x.index(min(rightSec_x))
    lid = leftSec_x.index(min(leftSec_x))

    rSec_x_upper = rightSec_x[0:rid+1]
    rSec_x_lower = rightSec_x[rid::]

    lSec_x_upper = leftSec_x[0:lid+1]
    lSec_x_lower = leftSec_x[lid::]

    rSec_y_upper = rightSec_y[0:rid+1]
    rSec_y_lower = rightSec_y[rid::]

    lSec_y_upper = leftSec_y[0:lid+1]
    lSec_y_lower = leftSec_y[lid::]

    if ralpha > lalpha:
        x_upper = rSec_x_upper
        x_lower = rSec_x_lower

        lSec_y_upper_interp = interp1d(lSec_x_upper, lSec_y_upper)
        lSec_y_lower_interp = interp1d(lSec_x_lower, lSec_y_lower)

        lSec_y_upper = lSec_y_upper_interp(x_upper)
        lSec_y_lower = lSec_y_lower_interp(x_lower)

    else:
        x_upper = lSec_x_upper
        x_lower = lSec_x_lower

        rSec_y_upper_interp = interp1d(rSec_x_upper, rSec_y_upper)
        rSec_y_lower_interp = interp1d(rSec_x_lower, rSec_y_lower)

        rSec_y_upper = rSec_y_upper_interp(x_upper)
        rSec_y_lower = rSec_y_lower_interp(x_lower)

    y_upper = [lalpha * ly + ralpha * ry for (ly, ry) in zip(lSec_y_upper, rSec_y_upper)]
    y_lower = [lalpha * ly + ralpha * ry for (ly, ry) in zip(lSec_y_lower, rSec_y_lower)]


    newSec_x = x_upper + x_lower[1::]
    newSec_y = y_upper + y_lower[1::]


    return [item for sublist in zip(newSec_x,newSec_y) for item in sublist]


def normalize(pts):
    xpts = pts[0::2]
    ypts = pts[1::2]
    xmin = min(xpts)
    xmax = max(xpts)
    return [(x - xmin) / (xmax - xmin) for x in xpts], [y / (xmax - xmin) for y in ypts]