# -*- coding: utf-8 -*-
"""Convert Moldex3D results to VTK."""
import sys

import meshio
import numpy as np

if __name__ == "__main__":
    in_filename = sys.argv[-3]
    ori_filename = sys.argv[-2]
    c_filename = sys.argv[-1]
    out_filename = in_filename.replace(".inp", ".vtk")

    print(
        "Converting '%s' with \n"
        "orientation file '%s' \n"
        "and concentration file '%s'" % (in_filename, ori_filename, c_filename)
    )

    mesh = meshio.read(in_filename)

    with open(ori_filename) as infile:
        # skip first 18 lines
        for i in range(18):
            infile.readline()

        ori_list = []

        while True:
            line = infile.readline()

            if not line:
                break

            splitline = line.split()
            id = int(splitline[0])
            Axx, Ayy, Axy, Axz, Ayz = list(map(float, splitline[2:9]))
            values = [Axx, Ayy, 1.0 - Axx - Ayy, Axy, Axz, Ayz]
            ori_list.append(values)

    with open(ori_filename) as infile:
        # skip first 18 lines
        for i in range(18):
            infile.readline()

        ori_list = []

        while True:
            line = infile.readline()

            if not line:
                break

            splitline = line.split()
            id = int(splitline[0])
            Axx, Ayy, Axy, Axz, Ayz = list(map(float, splitline[2:9]))
            values = [Axx, Ayy, 1.0 - Axx - Ayy, Axy, Axz, Ayz]
            ori_list.append(values)

    with open(c_filename) as infile:
        concentration_list = []
        while True:
            line = infile.readline()

            if not line:
                break

            if "$" not in line:
                splitline = line.split()
                id = int(splitline[0])
                c = float(splitline[1])
                concentration_list.append(c)

    mesh.cell_data["Orientation"] = [np.array(ori_list)]
    mesh.point_data["Concentration"] = np.array(concentration_list)
    meshio.write(out_filename, mesh)
