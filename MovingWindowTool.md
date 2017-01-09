---
title: "Moving Window Tool"
---


# Moving Window Tool #

The moving window analysis tool calculates length based attributes over a series of user specified window lengths. The results are reported at the center point of each window series (Seed Point).

## Inputs ##

### Line Netowrk

The Line network on which the Moving Window analysis will be generated. **This should be the `Raw Confining State` feature class output from the confinement tool.**

Requirements: 

* Contains the network attributes for which the moving window summary will be calculated (i.e. Confinement). 
* The Line Network must have tributary topology information as an attribute to dissolve the network (i.e. GNIS names, Stream Order, etc)

### Stream Route ID

The field that contains a unique ID for each Stream/Route. The tool will dissolve based on this ID, so as to create the longest continuous river segments for generating the Seed Points.

### Attribute Field

The Field that contains the Attribute information for the moving window calculation. <Needs clarification: Currently only BINARY fields for Confinement (i.e. `IsConfined`).>

### Seed Point Distance

Distance between seed points. Seed Points represent the center of each window, and multiple windows are aligned on each seed point. The first seed point is located at half the distance of the largest window size from the ends of each stream route. This is to ensure that each seed point has every window size associated with it.

### Window Sizes

Window size (in meters) to be generated at each seed point.  Multiple window sizes can be specified.

### Output Workspace

Output File Geodatabase to store the results and intermediate data. The default is the Scratch Workspace listed in the File Geodatabase Environments.  

## Outputs ##

In the output workspace you will find:

### GNAT_MWA_SeedPoints

Points feature class that contain the calculated attribute for each window size, centered on each seed point feature. 

Attributes:

* RouteID: The same attribute as the StreamBranchID specified in the inputs.
* SeedID: Unique ID for each seed point. Can be used to join back to Window line features in GNAT_MWA_WindowLines.
* Each window size will have its own field (i.e. `WindowSize100` for a window of 100m, etc)

### GNAT_MWA_WindowLines

The line features that represent the moving windows. These features will overlap both in window spacing (seed distance) and window sizes. 

Attributes:

* SeedID: Unique id for each seed point. This can be used to join back to the individual seed points.
* Window size: Size of the window (due to geometric rounding, the actual shape length may be slightly larger or smaller than the window size).