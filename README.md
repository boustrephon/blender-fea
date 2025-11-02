# BlenderFEA

## Overview

BlenderFEA is a Blender add-on designed to create, view, and manage structural models for finite element analysis (FEA). It provides a user-friendly interface within Blender to streamline the process of setting up and exporting models for FEA simulations.

**WARNING:** This is little more than a proof of concept at present. Breaking changes WILL be made over the next few versions. It is very slow at importing large models from JSON - the "undo" functionality needs to be switched off while it is creating beams etc from a JSON file.

## TO DO

* Switch off UNDO while importing large models from JSON.
* Modify JSON "Point" format to allow definition of support constraints
* Add more information into the JSON format
* Modify the creating of beam solids - at present it creates boxes. I want it to be able to handle I-sections etc.

## Features

*   **Model Creation:** Tools for creating and editing structural models directly within Blender.
*   **Material Properties:** Define and assign material properties to different parts of the model.
*   **Boundary Conditions:** Apply various boundary conditions, such as fixed supports and applied loads.
*   **Meshing:** Generate meshes suitable for FEA simulations.
*   **Exporting:** Export models to popular FEA solver formats (e.g., Abaqus, ANSYS).
*   **Visualization:** Visualize analysis results directly within Blender.
*   **Units Conversion:** Includes robust units conversion using a comprehensive dictionary.

## Installation

1.  Download the latest version of the add-on from the [Releases](link to releases page) page.
2.  Open Blender.
3.  Go to `Edit > Preferences > Add-ons`.
4.  Click `Install...` and select the downloaded `.zip` file.
5.  Enable the add-on by checking the box next to "BlenderFEA" in the list.

## Usage

1.  Once enabled, the BlenderFEA panel will appear in the 3D Viewport sidebar.
2.  Use the tools in the panel to create, modify, and set up your structural model.
3.  Define material properties, boundary conditions, and mesh settings.
4.  Import the model from a JSON format file. (Possible future development) Import the model from an FEA solver format.
5.  Export the model to a JSON format file. (Possible future development) Export the model to an FEA solver format. 
6.  (Possible future development) Import and visualize analysis results within Blender.

## Project Structure

```
blenderfea/           # Add-on's root directory
├── __init__.py       # Main add-on file
├── src/
│   ├── __init__.py   # src package initialization
│   ├── operators.py  # Operator definitions
│   ├── panels.py     # UI panel definitions
│   ├── properties.py # Custom property definitions
│   └── utils.py      # Utility functions
```

## Contributing

Contributions are welcome! If you'd like to contribute to BlenderFEA, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Implement your changes.
4.  Test your changes thoroughly.
5.  Submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contact

Andrew Mole - use GitHub issue

## Acknowledgements

This project is developed as an add-on for [Blender](https://www.blender.org/), a free and open-source 3D creation suite licensed under the GNU General Public License (GPL).
