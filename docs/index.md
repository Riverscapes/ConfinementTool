The Confinement Toolbox contains geoprocessing scripts for calculating confinement along a stream network. This tool is written in Python (2.7) for use in ArcGIS version 10.1.

## News

***2017-APR-28*** 

Version 2.2 Released! This version produces Riverscapes projects via [Riverscapes Project Python module](https://github.com/SouthForkResearch/PythonRiverscapesProject), adds outputs to the map (with a basic symbology applied), improved speed by removing old processes, plus other bugs fixed.  

Version 2.3 is already in the planning stages (see issues marked with Milestone 2.3), and will include features such as Riverscapes project linking, Generic Confinement analysis types,  and more!

## Download

**[Version 2.2.03](Downloads/ConfinementTool_2.2.03.zip)** 2017 AUG 01

``` * Fixed Bug with path naming for Realizations and Analyses```

[Previous Versions and Release Notes](Releases)

### Installation

The Confinement Toolbox is provided as a zip file containing a .pyt file and supporting script files. 

1. Unzip the contents to your computer (keep all files together).
2. Open ArcGIS.
3. Add the .pyt file to Arc toolbox as you would any other Geoprocesssing Toolbox.

## Using the Confinement Tools

![](Images/ArcToolbox.png)

### Project Mode
The Confinement Tool has a **[Project Mode](About-Confinement-Projects)** to support confinement analysis organization and the RiverScapes Program.

**[Start Here](Create-a-Project)** to calculate confinement as a Project

### Stand-Alone Tools
The primary Confinement Tools can also be used in a "stand-alone" analysis workflow. 

- **[Confining Margins Tool](Generate-Confining-Margins)** Generate confining margins and calculate Confinement values for a stream network.
- **[Confinement By Segments](Calculating-Confinement)** Calculate confinement along *pre-existing* segments in the stream network.
- **[Moving Window Tool](MovingWindowTool)** Tool for calculating confinement from a set of moving window segments.

# Acknowledgements
The Confinement Toolbox was written by Kelly Whitehead (South Fork Research, Seattle WA) with support, contributions and testing by

- Carol Volk (SFR)
- Joe Wheaton (Utah State University, Logan UT)
- Wally MacFarlane (USU)
- Jordan Gilbert (USU)
- Gary O'Brien (USU)
- Steve Fortney (TerrAqua, Inc.)
- Jean Olson (SFR)

