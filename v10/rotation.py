import numpy as np
from scipy.spatial.transform import Rotation as R


def rotate(rot_vec, center):
    rot_vec = np.array(rot_vec)
    center = np.array(center)

    if np.linalg.norm(rot_vec) < 1e-3:
        return center.tolist()
    else:
        rx = R.from_rotvec(rot_vec[0] * np.array([1, 0, 0]))
        ry = R.from_rotvec(rot_vec[1] * np.array([0, 1, 0]))
        rz = R.from_rotvec(rot_vec[2] * np.array([0, 0, 1]))
        rxyz = rz * ry * rx

        center = rxyz.apply(center)
        return center.round(3).tolist()


def translate(trans_vec, center):
    return [x + dx for x, dx in zip(center, trans_vec)]


def reduce(pts, lim=600):
    if len(pts) < lim:
        return pts

    x = pts[0::2]
    y = pts[1::2]

    x = x[0::2]
    y = y[0::2]

    return [pt for item in zip(x, y) for pt in item]
