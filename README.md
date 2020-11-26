[![LICENSE](https://black.readthedocs.io/en/stable/_static/license.svg)](https://raw.github.com/nilsmeyerkit/fiberoripy/master/LICENSE)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Paraview Map Lines
This repository offers a filter to evaluate results from direct simulation techniques [1, 2, 3] on a volume mesh. The result is a volume mesh that contains the cell data attributes 'Orientation tensor' and 'Volume fraction'.

The plugin requires Paraview 5.8 or higher.

Load the plugin to Paraview via 'Tools' -> 'Manage Plugins...' -> 'Load New'.

# Use
Load a .vtk file with line elements and a .vtk file with cells to paraview. Execute 'Filters' -> 'Map Lines' and select source lines and target cells. Click 'Apply' to start the plugin and 'Reload Python Module' to update the filter to changes in the code.

If line positions are given in the form
```
N
1 x1 y1 z1
1 x2 y2 z3
...
1 xN yN zN
M
1 x1 y1 z1
1 x2 y2 z3
...
1 xM yM zM
...
```
you may use the 'convert_mechanistic2vtk.py' tool to create a VTK that can be used for the Paraview filter.

# References
[1] Meyer et al., Direct Bundle Simulation approach for the compression molding process of Sheet Molding Compound, Composites Part A: Applied Science and Manufacturing, Volume 132,
2020,(https://doi.org/10.1016/j.compositesa.2020.105809).

[2] Londoño-Hurtado. Mechanistic Model for Fiber Flow; University of Wisconsin-Madison: Madison, WI, USA, 2009.

[3] Kuhn C et al., 'A simulative overview on fiber predictions models for discontinuous long fiber composites.', Polymer Composites. 2020;41:73–81. (https://doi.org/10.1002/pc.25346)
