---
title: Bankfull Channel Polygon Tool
category: Other Tools
---

The Bankfull Channel Tool generates an approximate bankfull channel, with an optional buffer. This tool is modified from the Bankfull Channel tool developed by USU and is included as a basic tool for generating an active channel polygon used in confinement. 

![]()

# Workflow

## Prepare Inputs

###DEM/Hydrology

A DEM covering the entire Watershed of interest is required. It is highly recommended to use a projection system with equal cell size (i.e. UTM).

1. Fill holes in the DEM (Spatial Analyst/Hydrology/Fill)
2. Generate Flow Direction Raster (Spatial Analyst/Hydrology/Flow Direction)
3. Generate Flow Accumulation Raster (Spatial Analyst/Hydrology/Flow Accumulation)
4. Convert Flow accumulation raster to SQKM 
   1. Use Spatial Analyst/Math/Times
   2. Multiply raster by: (cellX size * conversion value to km) * (cellY size * conversion value to km) 
   3. The largest raster value should be in the range of the estimated km area of the watershed.

###Precipitation Raster

Download NRCS Annual Precip shapefile of the area. 

> Shortcut: Download Precip of entire State once and clip out Watershed area outline. 

1. Add a Double precision field to the Precipitation Shapefile named "CM".
2. Add "CM" values by using Calcuate Field = ["IN"] * 
3. [Optional]  Clip this to the watershed extent to speed up processing time.
4. Use Polygon To Raster tool to convert "CM" field to raster. Make sure to use the same cell size, spatial reference and snap raster environment as the DEM.  

### Stream Network

Stream network Polyline layer that defines the location where Bankfull polygons are to be generated. 

>  Note: The tool uses the segmentation of the network. Too fine of segmentation will result in difficulty in finding the max drainage area for a section of stream, where too large of segmentation may result in overestimation of bankfull in many area.

### Valley Bottom

A valley bottom polygon is used to constrain the search area for determining max drainage area for a certain section of stream.

> Shortcut: It may be possible to use a simple buffer polygon of the stream network, however, make sure that the 'stream' in the flow accumulation raster is within this buffer. Manual editing may be necessary at lower elevations with very large and flat valley bottoms.

## Generate Bankfull Polygon

Once the inputs are ready, Open the Bankfull Polygon Tool

* Specify a minimum bankfull value (i.e. 5m) 
* Specify an optional percent buffer size to increase the polygon size by a percent of the bankfull width (this is especially important for confinement). Use 100 for no buffer, or 200 for twice the size of the calculated bankfull width.
* Specify a temporary workspace, and uncheck the box if you want to save or review any temporary files used in the processing.


------

# About 

The Bankfull Channel Tool is a separate Arc Python Toolbox from the confinement tool, and exists as a self-contained .pyt file. 

Dependencies:

* Arcgis 10.1 or higher
* Spatial Analyst extension


* There are no additional external libraries required

## Summary of Method 

1. Generate Thiessen polygons from midpoints of segmented network, Clipped to Valley Bottom Extent
2. Use Zonal Statistics to find the Max values of Precip and Drainage Area for each Thiessen Polygon
3. Intersect Thiessen Polygons with Stream Network.
4. Calculate Bankfull Width for each segment based on the following regression:
   bf_width(m) = 0.177(DrainageArea^0.397)(Precip^0.453))
5. Perform Buffer on each segment:
   bf_buffer(m) = bf_width + bf_width/(percent buffer/100)
6. Generate a minimum width buffer
7. Merge and Dissolve the Bankfull Polygon with the Minimum width buffer.
8. Apply 10m "PAEK" smoothing.

## Output

### Bankfull Channel

Bankfull polygons for each continuous section of  stream network.



