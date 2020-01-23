---
title: Bankfull Channel Polygon Tool
category: Other Tools
---

The Bankfull Channel Tool generates an approximate bankfull channel, with an optional buffer. This tool is modified from the Bankfull Channel tool developed by USU and is included as a basic tool for generating an active channel polygon used in confinement. 

![]()

# Workflow

## Prepare Inputs

### DEM/Hydrology

A DEM covering the entire Watershed of interest is required. It is highly recommended to use a projection system with equal cell size (i.e. UTM).

1. Fill holes in the DEM (Spatial Analyst/Hydrology/Fill)
2. Generate Flow Direction Raster (Spatial Analyst/Hydrology/Flow Direction)
3. Generate Flow Accumulation Raster (Spatial Analyst/Hydrology/Flow Accumulation)
4. Convert Flow accumulation raster to SQKM 
   1. Use Spatial Analyst/Math/Times
   2. Multiply raster by: (cellX size * conversion value to km) * (cellY size * conversion value to km) 
   3. The largest raster value should be in the range of the estimated km area of the watershed.
   
> Note: The [BRAT table tool](http://brat.riverscapes.xyz/Documentation/Tutorials/4-BRATTableTool.html) calculates drainage area in square kilometers. If you have already run BRAT on your watershed, the raster can be found under 'Inputs/03_Topography/DEM_01/Flow/DrainArea_sqkm.tif' within the BRAT project folder.

### Precipitation Raster

Download [PRISM annual precipitation data](http://www.prism.oregonstate.edu/normals/) for the whole study area. 

If you clip PRISM data to the watershed area, first buffer the watershed polygon by 1000 meters. Otherwise, the clipped raster will not cover the full network due to the low resolution of PRISM data.

> Shortcut: Download Precip of entire State once and clip out Watershed area outline. 
  

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
* Specify an output folder to save the bankfull channel polygon and stream network with bankfull width values.
* Specify a temporary workspace, and uncheck the "Delete temporary files?" box if you want to save or review any temporary files used in the processing.

## Output

The following outputs can be found under the output folder specified in the tool inputs:

### Bankfull Channel Polygon

Bankfull channel polygons for each continuous section of  stream network, named "final_bankfull_channel.shp".

### Bankfull Width Channel Fields

Segmented stream network with calculated bankfull width calculations saved in the attribute table for 
"network_buffer_values.shp" under the fields:
* `BFWIDTH` = Raw bankfull channel width based on the regression equation below. (in map units)
* `BUFWIDTH` = Adjusted bankfull channel width based on the percent buffer specified (`BFDWITH * (percent buffer/100)`). (in map units)

------

# About 

The Bankfull Channel Tool is a separate Arc Python Toolbox from the confinement tool, and exists as a self-contained .pyt file. 

Dependencies:

* Arcgis 10.1 or higher
* Spatial Analyst extension


* There are no additional external libraries required

## Summary of Method 

1. Generate thiessen polygons from midpoints of segmented network, Clipped to Valley Bottom Extent
2. For large thiessen polygons overlapping multiple drainage area or precipitation pixels, use Zonal Statistics to find the Max values of Precip and Drainage Area for each Thiessen Polygon. For small thiessen polygons that only overlap one pixel, extract pixel values based on the centroid of the polygon.
3. Intersect thiessen polygons with input stream network to add drainage area and precipitation values to the network.
4. Calculate Bankfull Width for each segment based on the following regression:
   bf_width(m) = 0.177(DrainageArea^0.397)(Precip^0.453))
5. Perform Buffer on each segment:
   bf_buffer(m) = bf_width + bf_width/(percent buffer/100)
6. Generate a minimum width buffer
7. Merge and Dissolve the Bankfull Polygon with the Minimum width buffer.
8. Apply 10m "PAEK" smoothing.
