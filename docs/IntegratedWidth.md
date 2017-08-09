# Integrated Width Metrics

The Confinement tool includes a set of two 'integrated width' attributes as well as a ratio value of these two values.

## Method

1. The input polygon is segmented using the segmentation of line network

   > Both the channel and Valley bottoms use the segmented Stream network for segmenting purposes. 

2. Area is calculated for each polygon segment.

3. Spatial Join to copy the area of each polygon segment to the corresponding line segment.

4. Calculate integrated width as:
   $$
   w_i = A_{polygon} / l_{segment}
   $$




## Output Metrics

**Integrated Channel Width** *(IW_Channel)*

Integrated Width of the Active Channel Polygon along the length of the Stream Segment 

**Integrated Valley Bottom Width** *(IW_Valley)*

Integrated Width of the Valley Bottom Polygon along the length of the Stream Segment 

**Integrated Channel to Valley Width Ratio** *(IW_Ratio)*
$$
r_{w_i} = w_{{i}_{channel}} / w_{{i}_{valley}}
$$
