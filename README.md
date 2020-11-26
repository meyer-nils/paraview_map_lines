[![LICENSE](https://black.readthedocs.io/en/stable/_static/license.svg)](https://raw.github.com/nilsmeyerkit/fiberoripy/master/LICENSE)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Paraview Map Lines

This repository offers a filter to evaluate results from direct simulation techniques on a volume mesh. The result is a volume mesh that contains the cell data attributes 'Orientation tensor' and 'Volume fraction'.

# Requirements
- Paraview 5.8 or higher

# Install plugin
Load the plugin to Paraview via 'Tools' -> 'Manage Plugins...' -> 'Load New'.

# Use
Load a .vtk file with line elements and a .vtk file with cells to paraview. Execute 'Filters' -> 'Map Lines' and select source lines and target cells. Click 'Apply' to start the plugin and 'Reload Python Module' to update the filter to changes in the code.
