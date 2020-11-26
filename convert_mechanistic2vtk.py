# -*- coding: utf-8 -*-
"""Convert position result from mechanistic model to VTK."""
import sys

import meshio
import numpy as np

if __name__ == "__main__":
    in_filename = sys.argv[-1]
    out_filename = in_filename.replace(".txt", ".vtk")

    print("Converting %s" % in_filename)

    with open(in_filename) as infile:
        total = infile.readline()
        nodes = []
        lines = []
        nodeid = 0

        while True:
            line = infile.readline()

            if not line:
                break

            N = int(line)
            for i in range(N):
                v, x, y, z = infile.readline().split()
                if N > 2:
                    nodes.append([float(x), float(y), float(z)])
                    if i < (N - 1):
                        lines.append([nodeid, nodeid + 1])
                    nodeid += 1

    points = np.array(nodes)
    cells = [("line", np.array(lines))]

    meshio.write_points_cells(
        out_filename,
        points,
        cells,
    )
