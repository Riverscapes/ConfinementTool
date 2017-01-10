---
title: "Confinement Tool"
---
# Confinement Tool #
**Version 0.2.x**

Tips:

* Set Geoprocesssing Environments to disable M and Z values.
* All input data should be in the same Projected Coordinate System. UTM is highly recommended.

## Input Parameters ##

***Confinement Results Type***

> This parameter is new for 0.2

+ Full - All outputs will be generated. 
+ 

> Note: Shapefile output is not possible with **Full** Results type.

***Stream Network***

This is the line network for which confinement will be calculated. If there are segments, confinement calculations will be determined for each segment (line feature).

Requirements

* Projected Coordinate System (same as other inputs)
* No Z or M values

**Valley Bottom Polygon***

This polygon represents the boundary of the valley bottom (or other margin that the user is trying to model). 

***Channel Polygon (Bankfull Buffer)***

The Stream Channel Polygon represents the area of the active channel of the stream. It is important that this polygon does not under-represent the margins of the channel, and in fact should be buffered sufficiently to account for any error or uncertainty in the data products. The stream Network should be entirely within this polygon.

Requirements

* Stream Network should be fully contained within the Stream Channel Polygon
* Polygon sufficiently buffered to represent possible edges of active channel and any uncertainty in the GIS data


***Scratch Workspace***


## Outputs ##

***Raw Confining State***

This is the name of a Polyline Feature Class that will be created in the FGDB to store the raw confining state of the Stream Network.

> Note: This is does not contain the "Calculated Value" for confinement, even though this is the only required output for this tool. In order to calculate confinement, you must Segment the network and specify a value for the Output Confinement Calculated by Segments parameter.

* The feature class will be overwritten if it already exists.
* None of the Original Segments or their attributes are retained in this feature class.

Attribute Fields:
> Note: Short field names are for Shapefile output types

* `Confinement_Left`/`CON_LEFT` and `Confinement_Right`/`CON_RIGHT`: (Boolean) 
	* True = section is confined on that side of the stream.
	* False = section is not confined on that side of the stream. 
* `Confinement_Type`/`CON_TYPE`: (String) 
	* None = Not confined on either side of the stream.
	* Right = Confined on right side of stream.
	* Left = Confined on left side of the stream. 
	* Both = Confined on both sides of the stream.
* `IsConfined`: (Boolean) 
	* True = section is considered confined (i.e. Confinement_Type = Right, left, or Both).
	* False = section is considered unconfined.



***Confinement by Segments***

The actual confinement calculation is run on this line by using the segments in the input stream network.  

For Results type **Full**:

Confinement Calculation by using the Raw Confining State (Converged Margins):

* `Confinement_LineNetwork_All`: 
Confinement as calculated by transferring the attributes from the `Raw Confining State` to the segmented network. 

	* Confinement = Sum of length of Confined margins divided by the Sum of the total length of segment, Expressed as a ratio:
		* 0  = unconfined 
		* 1.0 = completely confined
	* This method does not double count the lengths of the confining margins if the stream is confined on both sides of the channel at that location. 

* `Confinement_LineNetwork_Both`: Confinement is calculated where both sides of the stream are considered “Confined”.
* `Confinement_LineNetwork_Left`: Confinement is calculated where the left side of the stream is considered “Confined”.
* `Confinement_LineNetwork_Right`: Confinement is calculated where the right side of the stream is considered “Confined”.

Confinement Calculation by Segmenting Channel Polygon:

* `Confinement_Margin_Summed`
Simplified method for calculating confinement using channel margin lengths. Length of confined margins on both sides of channel divided by total length of channel margins on both sides of channel. Values is a ratio 0 (unconfined) to 1.0 (confined on all margins). *This method does not exclude double counting of confinement if confined on both sides of the channel at that location*.
* `Length_ConfinedMargin_Left` and `Length_ConfinedMargin_Right`
Length of confined margin for Left and Right sides of the channel for that segment.
* `Length_ChannelMargin_Left` and 
`Length_ChannelMargin_Right`
Length of channel margin for Left and Right sides of the channel for that segment.
* `Confinement_Margin_Left` and 
`Confinement_Margin_Right` 
Confinement expressed on each side of the bank separately.

***Confining Margins***

This polyline feature class represents the confining margins as the intersection of the input stream channel and valley bottom polygons. 