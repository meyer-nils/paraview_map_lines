# -*- coding: utf-8 -*-
"""Convert fiber position result from 3DTIMON model to VTK."""
import sys

import meshio
import numpy as np

if __name__ == "__main__":
    in_filename = sys.argv[-1]
    out_filename = in_filename.replace(".unv", ".vtk")

    print("Converting %s" % in_filename)

    with open(in_filename) as infile:
        infile.readline()
        nodes = []
        lines = []
        nodeid = 0

        while True:
            line = infile.readline()

            if not line:
                break

            # This is a quick and dirty implementation and not feasible for
            # general *.unv files
            if line.split()[-1] == "7":
                x, y, z = infile.readline().split()
                nodes.append([float(x), float(y), float(z)])
            elif line.split()[-1] == "2":
                infile.readline()
                n1, n2 = infile.readline().split()
                lines.append([int(n1) - 1, int(n2) - 1])
            else:
                infile.readline()

    points = np.array(nodes)
    cells = [("line", np.array(lines))]

    meshio.write_points_cells(
        out_filename,
        points,
        cells,
    )
