---
title: Confinement Tool Home
---

The Confinement Toolbox contains geoprocessing scripts for calculating confinement along a stream network. This tool is written in Python (2.7) for use in ArcGIS version 10.1.

## News

***2017-APR-28*** 

Version 2.2 Released! This version produces Riverscapes projects via [Riverscapes Project Python module](https://github.com/SouthForkResearch/PythonRiverscapesProject), adds outputs to the map (with a basic symbology applied), improved speed by removing old processes, plus other bugs fixed.  

Version 2.3 is already in the planning stages (see issues marked with Milestone 2.3), and will include features such as Riverscapes project linking, Generic Confinement analysis types,  and more!

## Download

**[Latest Version](https://github.com/Riverscapes/ConfinementTool/releases/latest)** 2017 AUG 01

``` * Fixed Bug with path naming for Realizations and Analyses```

[Previous Versions and Release Notes](Releases)

### Installation

The Confinement Toolbox is provided as a zip file containing a .pyt file and supporting script files. 

1. Unzip the contents to your computer (keep all files together).
2. Open ArcGIS.
3. Add the .pyt file to Arc toolbox as you would any other Geoprocesssing Toolbox.

## Using the Confinement Tools

![]({{ site.baseurl }}/assets/images/ArcToolbox.png)

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
- [Joe Wheaton](http://joewheaton.org) (Utah State University, Logan UT)
- [Wally MacFarlane](http://etal.joewheaton.org/people/researchers-technicians/Wally) (USU)
- [Jordan Gilbert](http://etal.joewheaton.org/people/researchers-technicians/jordan-gilbert) (USU)
- [Gary O'Brien](http://etal.joewheaton.org/people/researchers-technicians/gary-o-brien) (USU)
- Steve Fortney (TerrAqua, Inc.)
- Jean Olson (SFR)

# Support
While the confinement tool scripts are free, open-source and reasonably well documented, it is not perfect, and you get what you pay for. Unlike our more mature models (e.g. GCD) that have full GUIs and ArcGIS Add-Ins, the confinement tool is a highly finicky series of ArcPy Toolboxes and scripts, that are very version sensitive (to both version of ArcGIS and Python), and with rather narrow workflows that have been tailored to how we typically run confinement in the ETAL lab. The dirty secret about the confinement tool is that none of the development or support happens without someone paying for it (contrary to popular belief, we get no support from our university for supporting this effort and capable students don’t work for free). Everything is on our personal time and personal dime. We try to help out users where we can, but our development and support team is in high demand on our paying contracts. If you want to ensure you get the help you need when you need it, you can hire an USU ETAL analyst to help you with your confinement analysis. 

