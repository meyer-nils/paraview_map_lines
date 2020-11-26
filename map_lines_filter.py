# -*- coding: utf-8 -*-
"""Custom paraview filter to map line orientation to cells."""
import numpy as np
import vtk
from paraview.util.vtkAlgorithm import smdomain, smproperty, smproxy
from vtk.numpy_interface import algorithms as algs
from vtkmodules.numpy_interface import dataset_adapter as dsa
from vtkmodules.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid


@smproxy.filter(label="Map Lines")
@smproperty.input(name="Source Lines", port_index=0)
@smdomain.datatype(
    dataTypes=["vtkUnstructuredGrid"], composite_data_supported=False
)
@smproperty.input(name="Target Cells", port_index=1)
@smdomain.datatype(
    dataTypes=["vtkUnstructuredGrid"], composite_data_supported=False
)
class MapBundleFilter(VTKPythonAlgorithmBase):
    """MapBundleFilter.

    Attributes
    ----------
    _area : float
        Cross sectional area attributed to each line.
    _minN : int
        Minimum number of lines required to compute a meaningfull orientation
        tensor.

    """

    def __init__(self):
        """Set up the filter."""
        VTKPythonAlgorithmBase.__init__(
            self,
            nInputPorts=2,
            nOutputPorts=1,
            outputType="vtkUnstructuredGrid",
        )
        self._area = 0.0
        self._minN = 5

    def FillInputPortInformation(self, port, info):
        """Require unstructured grids as input types."""
        info.Set(self.INPUT_REQUIRED_DATA_TYPE(), "vtkUnstructuredGrid")
        return 1

    @smproperty.doublevector(
        name="Cross section area", default_values=[1.76872e-07]
    )
    @smdomain.doublerange()
    def SetArea(self, area):
        """Create an input field for the cross sectional area and save it."""
        if self._area != area:
            self._area = area
            self.Modified()

    @smproperty.doublevector(
        name="Minimum number of directions for tensor computation",
        default_values=[5],
    )
    @smdomain.doublerange()
    def SetMinimumNumber(self, N):
        """Create an input field for the min. number of dirs and save it."""
        if self._minN != N:
            self._minN = N
            self.Modified()

    def RequestData(self, request, inInfo, outInfo):
        """Process the request submitted after applying the filter."""
        source_input = vtkUnstructuredGrid.GetData(inInfo[0])
        source = dsa.WrapDataObject(source_input)
        target_input = vtkUnstructuredGrid.GetData(inInfo[1])
        target = dsa.WrapDataObject(target_input)

        output = dsa.WrapDataObject(vtkUnstructuredGrid.GetData(outInfo))
        output.ShallowCopy(target_input)

        # Compute target cell volume
        volumes = np.abs(algs.volume(target))

        # Create a vtkCellLocator for fast computation of neighborhood
        cell_locator = vtk.vtkCellLocator()
        cell_locator.SetDataSet(source_input)
        cell_locator.SetNumberOfCellsPerNode(1)
        cell_locator.BuildLocator()

        # Correct cell position indicators (for some reason they must be
        # all shifted)
        correction = np.arange(0, len(source.CellLocations))
        cell_pos = source.CellLocations + correction

        # Prepare source lines
        node_ids_a = cell_pos + 1
        node_ids_b = cell_pos + 2
        point_ids_a = source.Cells[node_ids_a]
        point_ids_b = source.Cells[node_ids_b]
        points_a = source.Points[point_ids_a]
        points_b = source.Points[point_ids_b]
        directions = points_a - points_b
        norm_directions = directions / np.linalg.norm(directions, axis=1)

        # Fill new cell data
        n_lines = np.zeros_like(volumes)
        vf = np.zeros_like(volumes)
        A = np.nan * np.ones((len(volumes), 3, 3))
        for i, cell_volume in enumerate(volumes):
            # Find a bounding box
            idList = vtk.vtkIdList()
            bounds = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            target.GetCellBounds(i, bounds)
            cell_locator.FindCellsWithinBounds(bounds, idList)

            # Number of potential lines
            N0 = idList.GetNumberOfIds()

            # Compress to number of real intersections
            ids = [idList.GetId(j) for j in range(N0)]
            cell = target.GetCell(i)
            reduced_line_ids = []
            length_in_cell = []
            for id, p1, p2 in zip(ids, points_a[ids], points_b[ids]):
                res = self.compute_length_in_cell(cell, p1, p2)
                if res > 0.0:
                    reduced_line_ids.append(id)
                    length_in_cell.append(res)

            # Compute number of fibers in cell
            N = len(reduced_line_ids)
            n_lines[i] = N

            # Compute approximate fiber volume fraction
            vf[i] = np.sum(length_in_cell) * self._area / cell_volume

            # Compute fiber orientation tensors
            dirs = norm_directions[reduced_line_ids]
            if N > self._minN:
                A[i, :, :] = np.einsum("ki,kj->ij", dirs, dirs) / N

        output.CellData.append(volumes, "Cell Volume")
        output.CellData.append(n_lines, "N Lines")
        output.CellData.append(A, "Orientation Tensor (2nd Order)")
        output.CellData.append(vf, "Volume Fraction")

        return 1

    def compute_length_in_cell(self, cell, p1, p2):
        """Compute lenght of the line inside a cell.

        Parameters
        ----------
        cell : vtkCell
            The cell to be cut by a line.
        p1 : type
            First endpoint describing the line.
        p2 : type
            Second endpoint describing the line.

        Returns
        -------
        float
            Intersected length.

        """
        # set up a bunch of dummy properties for passing to the cell functions.
        t = vtk.reference(0.0)
        dist = vtk.reference(0.0)
        pcords = [0.0, 0.0, 0.0]
        subid = vtk.reference(0)
        weights = [0.0] * cell.GetNumberOfPoints()
        dummy = [0.0, 0.0, 0.0]

        # Determine wether the points are inside the cell
        in1 = cell.EvaluatePosition(p1, dummy, subid, pcords, dist, weights)
        in2 = cell.EvaluatePosition(p2, dummy, subid, pcords, dist, weights)

        # Both points inside
        if in1 == 1 and in2 == 1:
            return np.linalg.norm(np.array(p2) - np.array(p1))

        # Both points outside
        if in1 == 0 and in2 == 0:
            return 0.0

        # Only point 2 inside
        if in1 == 0 and in2 == 1:
            x = [0.0, 0.0, 0.0]
            res = cell.IntersectWithLine(p1, p2, 0.0, t, x, pcords, subid)
            if res > 0:
                return np.linalg.norm(np.array(p2) - np.array(x))
            else:
                return 0.0

        # Only point 1 inside
        if in1 == 1 and in2 == 0:
            x = [0.0, 0.0, 0.0]
            res = cell.IntersectWithLine(p1, p2, 0.0, t, x, pcords, subid)
            if res > 0:
                return np.linalg.norm(np.array(p1) - np.array(x))
            else:
                return 0.0

        return 0.0
