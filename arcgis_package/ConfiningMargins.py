#
# Name:        Valley Confinement Tool
# Purpose:     Calculate Valley Confinement Along a Stream Network
#
# Author:      Kelly Whitehead (kelly@southforkresearch.org)
#              South Fork Research, Inc
#              Seattle, Washington
#
# Created:     2014-Nov-01
# Version:     1.3
# Modified:    2016-Feb-10
# Modified:    23/8/2018 - DDH - Improved messaging/error trapping
#              5/9/2018  - DDH - Updated main to take and process FilterByLength
#              6/9/2018  - DDH - Added prepConfinementOutput function to clean up output
#
# Copyright:   (c) Kelly Whitehead 2016
#
#
#!/usr/bin/env python

# # Import Modules # #
import sys
import arcpy
import gis_tools
import DividePolygonBySegment

## Updates
# Shapefile support
# Remove old calculation methods
# use stat table calculation method
# Added Constriction Field
# Added Final Intersect to rejoin Original Attributes.


# # Main Function # #
def main(fcInputStreamLineNetwork,fcInputValleyBottomPolygon,fcInputChannelPolygon,filterByLength,fcOutputRawConfiningState,fcOutputConfiningMargins,scratchWorkspace,boolIntegratedWidthAttributes=False):
    '''
        Description:
            Main processing function for creating the confinement margins and segmenting the network.

        Updated: 24/8/18 - DDH - Now returns True/False if code succeeds or fails, this can be used by calling module
                  5/9/18 - DDH - Now uses FilterByLength to delete out confinement margins created by the intersection that fall below
                                 the specified length. Default is 5m
                  6/9/18 - DDH - Creates MarginID field and purges out all other fields except Length
    '''
    try:

        ##Prepare processing environments
        arcpy.AddMessage("Starting Confining Margins Tool")

        # Create Confined Channel Polygon
        # This clips the channel polygon by the valley botton polygon
        arcpy.AddMessage("... Clipping channel polygon with Valley bottom")
        fcConfinedChannel = gis_tools.newGISDataset(scratchWorkspace,"ChannelConfined")
        arcpy.Clip_analysis(fcInputChannelPolygon,fcInputValleyBottomPolygon,fcConfinedChannel)

        # Convert Confined Channel polygon to Edges polyline
        arcpy.AddMessage("... Converting clipped channel polygon to a polyline dataset")
        fcChannelMargins = gis_tools.newGISDataset(scratchWorkspace,"ChannelMargins")
        arcpy.PolygonToLine_management(fcConfinedChannel,fcChannelMargins)

        # Create Confinement Edges
        if fcOutputConfiningMargins:
            gis_tools.resetData(fcOutputConfiningMargins)
            fcConfiningMargins = fcOutputConfiningMargins
        else:
            fcConfiningMargins = gis_tools.newGISDataset(scratchWorkspace, "ConfiningMargins")

        arcpy.AddMessage("... Intersecting clipped channel polygon with valley bottom returning intersection lines")
        fcConfiningMarginsMultipart = gis_tools.newGISDataset(scratchWorkspace, "ConfiningMargins_Multipart")
        arcpy.Intersect_analysis([fcConfinedChannel, fcInputValleyBottomPolygon], fcConfiningMarginsMultipart, output_type="LINE")
        arcpy.MultipartToSinglepart_management(fcConfiningMarginsMultipart,fcConfiningMargins)

        # Delete lines that fall below the specified length
        if filterByLength > 0:
            # Make a temporary layer, select lines and delete
            arcpy.AddMessage("... Adding Length field and updating")
            arcpy.MakeFeatureLayer_management(fcConfiningMargins,"tempLayer")
            arcpy.AddField_management("tempLayer","Length","DOUBLE")
            arcpy.CalculateField_management("tempLayer","Length","!SHAPE.length@METERS!","PYTHON_9.3")
            arcpy.AddMessage("... Selecting lines smaller than " + str(filterByLength) + "m and deleting")
            arcpy.SelectLayerByAttribute_management("tempLayer","NEW_SELECTION",'"' + "Length" +'"' + " <= " + str(filterByLength))
            descObj = arcpy.Describe("tempLayer")
            if len(descObj.FIDSet) > 0:
                # A Selection exists so delete
                arcpy.DeleteFeatures_management("tempLayer")

            # Clean up
            del descObj
            arcpy.Delete_management("tempLayer")
        else:
            arcpy.AddMessage("Filter by Length parameter was set to 0m, skipping deleting features")

        # Merge segments in Polyline Centerline to create Route Layer
        arcpy.AddMessage("... Dissolving stream network into routes")
        arcpy.env.outputZFlag = "Disabled" # 'empty' z values can cause problem with dissolve
        fcStreamNetworkDissolved = gis_tools.newGISDataset(scratchWorkspace, "StreamNetworkDissolved") # one feature per 'section between trib or branch junctions'
        arcpy.Dissolve_management(fcInputStreamLineNetwork, fcStreamNetworkDissolved, multi_part="SINGLE_PART", unsplit_lines="UNSPLIT_LINES")

        arcpy.AddMessage("... Extracting stream network END points")
        fcNetworkSegmentPoints = gis_tools.newGISDataset(scratchWorkspace, "StreamNetworkSegmentPoints")
        arcpy.FeatureVerticesToPoints_management(fcInputStreamLineNetwork, fcNetworkSegmentPoints, "END")

        arcpy.AddMessage("... Extracting stream network DANGLE points")
        fcStreamNetworkDangles = gis_tools.newGISDataset(scratchWorkspace, "StreamNetworkDangles")
        arcpy.FeatureVerticesToPoints_management(fcInputStreamLineNetwork, fcStreamNetworkDangles, "DANGLE")

        #SegmentPolgyons
        arcpy.AddMessage("Preparing Segmented Polygons...")

        fcChannelSegmentPolygons = gis_tools.newGISDataset(scratchWorkspace, "SegmentPolygons")
        fcChannelSegmentPolygonLines = gis_tools.newGISDataset(scratchWorkspace,"SegmentPolygonLines")

        arcpy.AddMessage("... Copying clipped channel polygon and converting to polyline dataset")
        #DividePolygonBySegment.main(fcInputStreamLineNetwork, fcConfinedChannel, fcChannelSegmentPolygons, scratchWorkspace)
        arcpy.CopyFeatures_management(fcConfinedChannel,fcChannelSegmentPolygons)
        arcpy.PolygonToLine_management(fcChannelSegmentPolygons, fcChannelSegmentPolygonLines)

        arcpy.AddMessage("... Building proximity information for DANGLES")
        lyrStreamNetworkDangles = gis_tools.newGISDataset("LAYER", "lyrStreamNetworkDangles")
        arcpy.MakeFeatureLayer_management(fcStreamNetworkDangles, lyrStreamNetworkDangles)
        arcpy.SelectLayerByLocation_management(lyrStreamNetworkDangles, "INTERSECT", fcConfinedChannel)
        arcpy.Near_analysis(lyrStreamNetworkDangles, fcChannelSegmentPolygonLines, location="LOCATION")
        arcpy.AddXY_management(lyrStreamNetworkDangles)

        arcpy.AddMessage("... Building bank lines")
        fcChannelBankNearLines = gis_tools.newGISDataset(scratchWorkspace, "Bank_NearLines")
        arcpy.XYToLine_management(lyrStreamNetworkDangles,fcChannelBankNearLines,"POINT_X","POINT_Y","NEAR_X","NEAR_Y")

        fcChannelBankLines = gis_tools.newGISDataset(scratchWorkspace, "Bank_Lines")
        arcpy.Merge_management([fcInputStreamLineNetwork,fcChannelBankNearLines, fcChannelSegmentPolygonLines], fcChannelBankLines)
        fcChannelBankPolygons = gis_tools.newGISDataset(scratchWorkspace, "Bank_Polygons")
        arcpy.FeatureToPolygon_management(fcChannelBankLines, fcChannelBankPolygons)

        # Intersect and Split Channel polygon Channel Edges and Polyline Confinement using cross section lines
        arcpy.AddMessage("Intersect and Split Channel Polygons...")
        fcIntersectPoints_ChannelMargins = gis_tools.newGISDataset(scratchWorkspace, "IntersectPoints_ChannelMargins")
        fcIntersectPoints_ConfinementMargins = gis_tools.newGISDataset(scratchWorkspace, "IntersectPoints_ConfinementMargins")
        arcpy.Intersect_analysis([fcConfiningMargins,fcChannelSegmentPolygonLines], fcIntersectPoints_ConfinementMargins, output_type="POINT")
        arcpy.Intersect_analysis([fcChannelMargins,fcChannelSegmentPolygonLines], fcIntersectPoints_ChannelMargins, output_type="POINT")
        fcConfinementMargin_Segments = gis_tools.newGISDataset(scratchWorkspace, "ConfinementMargin_Segments")
        fcChannelMargin_Segments = gis_tools.newGISDataset(scratchWorkspace, "ChannelMargin_Segements")
        arcpy.SplitLineAtPoint_management(fcConfiningMargins, fcIntersectPoints_ConfinementMargins, fcConfinementMargin_Segments, search_radius="10 Meters")
        arcpy.SplitLineAtPoint_management(fcChannelMargins, fcIntersectPoints_ChannelMargins, fcChannelMargin_Segments, search_radius="10 Meters")

        # Create River Side buffer to select right or left banks
        arcpy.AddMessage("Determining Relative Sides of Bank...")
        determine_banks(fcInputStreamLineNetwork, fcChannelBankPolygons, scratchWorkspace)

        # Prepare Layers for Segment Selection
        lyrSegmentPolygons = gis_tools.newGISDataset("Layer","lyrSegmentPolygons")
        lyrConfinementEdgeSegments = gis_tools.newGISDataset("Layer", "lyrConfinementEdgeSegments")
        lyrChannelEdgeSegments = gis_tools.newGISDataset("Layer", "lyrChannelEdgeSegments")
        arcpy.MakeFeatureLayer_management(fcChannelSegmentPolygons, lyrSegmentPolygons)
        arcpy.MakeFeatureLayer_management(fcConfinementMargin_Segments, lyrConfinementEdgeSegments)
        arcpy.MakeFeatureLayer_management(fcChannelMargin_Segments, lyrChannelEdgeSegments)

        ## Prepare Filtered Margins
        fcFilterSplitPoints = gis_tools.newGISDataset(scratchWorkspace, "FilterSplitPoints")
        arcpy.FeatureVerticesToPoints_management(fcConfinementMargin_Segments, fcFilterSplitPoints, "BOTH_ENDS")

        # Transfer Confining Margins to Stream Network ##
        arcpy.AddMessage("Transferring Confining Margins to Stream Network...")
        fcConfinementMarginSegmentsBankSide = gis_tools.newGISDataset(scratchWorkspace, "ConfinementMarginSegmentsBank")
        lyrConfinementMarginSegmentsBankside = gis_tools.newGISDataset("Layer", "lyrConfinementMarginSegmentsBankside")

        field_map = """BankSide "BankSide" true true false 255 Text 0 0 ,First,#,""" + fcChannelBankPolygons + """,BankSide,-1,-1"""
        arcpy.SpatialJoin_analysis(fcConfinementMargin_Segments,fcChannelBankPolygons,fcConfinementMarginSegmentsBankSide,"JOIN_ONE_TO_ONE","KEEP_ALL",field_map)

        arcpy.MakeFeatureLayer_management(fcConfinementMarginSegmentsBankSide, lyrConfinementMarginSegmentsBankside)
        arcpy.SelectLayerByAttribute_management(lyrConfinementMarginSegmentsBankside, "NEW_SELECTION", """ "BankSide" = 'LEFT'""")

        fcStreamNetworkConfinementLeft = transfer_line(lyrConfinementMarginSegmentsBankside, fcStreamNetworkDissolved, "LEFT")
        arcpy.SelectLayerByAttribute_management(lyrConfinementMarginSegmentsBankside, "NEW_SELECTION", """ "BankSide" = 'RIGHT'""")
        fcStreamNetworkConfinementRight = transfer_line(lyrConfinementMarginSegmentsBankside, fcStreamNetworkDissolved, "RIGHT")

        # This intersection step combines the two outputs from transfer_line() into a single dataset using intersection
        arcpy.AddMessage("... Constructing segmented stream network")
        fcConfinementStreamNetworkIntersected = gis_tools.newGISDataset(scratchWorkspace,"ConfinementStreamNetworkIntersected")
        arcpy.Intersect_analysis([fcStreamNetworkConfinementLeft,fcStreamNetworkConfinementRight],
                                 fcConfinementStreamNetworkIntersected, "NO_FID") # TODO no fid?

        #Re-split centerline by segments
        arcpy.AddMessage("Determining Confinement State on Stream Network...")
        fcRawConfiningNetworkSplit = gis_tools.newGISDataset(scratchWorkspace,"RawConfiningNetworkSplit")
        arcpy.SplitLineAtPoint_management(fcConfinementStreamNetworkIntersected,fcNetworkSegmentPoints,fcRawConfiningNetworkSplit,"0.01 Meters")

        #Table and Attributes
        arcpy.AddMessage("... Adding fields and attributing")
        arcpy.AddField_management(fcRawConfiningNetworkSplit, "Con_Type", "TEXT", field_length="6")
        arcpy.AddField_management(fcRawConfiningNetworkSplit, "IsConfined", "SHORT")
        gis_tools.resetField(fcRawConfiningNetworkSplit, "IsConstric", "SHORT")

        lyrRawConfiningNetwork = gis_tools.newGISDataset("Layer", "lyrStreamNetworkCenterline1")
        arcpy.MakeFeatureLayer_management(fcRawConfiningNetworkSplit,lyrRawConfiningNetwork)

        arcpy.SelectLayerByAttribute_management(lyrRawConfiningNetwork,"NEW_SELECTION", """ "Con_LEFT" = 1""")
        arcpy.CalculateField_management(lyrRawConfiningNetwork,"Con_Type", "'LEFT'", "PYTHON")

        arcpy.SelectLayerByAttribute_management(lyrRawConfiningNetwork, "NEW_SELECTION", """ "Con_RIGHT" = 1""")
        arcpy.CalculateField_management(lyrRawConfiningNetwork,"Con_Type", "'RIGHT'", "PYTHON")

        arcpy.SelectLayerByAttribute_management(lyrRawConfiningNetwork, "NEW_SELECTION", """ "Con_LEFT" = 1 AND "Con_RIGHT" = 1""")
        arcpy.CalculateField_management(lyrRawConfiningNetwork,"Con_Type", "'BOTH'", "PYTHON")
        arcpy.CalculateField_management(lyrRawConfiningNetwork,"IsConstric", "1", "PYTHON")

        arcpy.SelectLayerByAttribute_management(lyrRawConfiningNetwork, "SWITCH_SELECTION")
        arcpy.CalculateField_management(lyrRawConfiningNetwork, "IsConstric", "0", "PYTHON")

        arcpy.SelectLayerByAttribute_management(lyrRawConfiningNetwork, "NEW_SELECTION", """ "Con_LEFT" = 1 OR "Con_RIGHT" = 1""")
        arcpy.CalculateField_management(lyrRawConfiningNetwork, "IsConfined", "1", "PYTHON")

        arcpy.SelectLayerByAttribute_management(lyrRawConfiningNetwork, "SWITCH_SELECTION")
        arcpy.CalculateField_management(lyrRawConfiningNetwork, "IsConfined", "0", "PYTHON")
        arcpy.CalculateField_management(lyrRawConfiningNetwork, "Con_Type", "'NONE'", "PYTHON")

        # Integrated Width
        # This code is never executed as the Boolean is ALWAYS FALSE!
        fcIntersectLineNetwork = fcInputStreamLineNetwork
        if boolIntegratedWidthAttributes:
            fcIntegratedChannelWidth = gis_tools.newGISDataset(scratchWorkspace,"IW_Channel")
            fieldIWChannel = integrated_width(fcInputStreamLineNetwork, fcChannelSegmentPolygons, fcIntegratedChannelWidth, "Channel" , False)

            fcIntegratedWidth = gis_tools.newGISDataset(scratchWorkspace,"IW_ChannelAndValley")
            fieldIWValley = integrated_width(fcIntegratedChannelWidth,fcInputValleyBottomPolygon,fcIntegratedWidth,"Valley",True)

            fieldIWRatio = gis_tools.resetField(fcIntegratedWidth, "IW_Ratio", "DOUBLE")
            exp = "!" + fieldIWValley + r"! / !" + fieldIWChannel + "!"
            arcpy.CalculateField_management(fcIntegratedWidth, fieldIWRatio, exp, "PYTHON_9.3")
            fcIntersectLineNetwork = fcIntegratedWidth

        # Final Output
        arcpy.AddMessage("Preparing Final Output...")
        if arcpy.Exists(fcOutputRawConfiningState):
            arcpy.Delete_management(fcOutputRawConfiningState)
        arcpy.Intersect_analysis([fcRawConfiningNetworkSplit,fcIntersectLineNetwork], fcOutputRawConfiningState, "NO_FID")

        # Call function to clean up fields
        arcpy.AddMessage("Cleaning up confinement margins layer...")
        bOK = prepConfinementOutput(fcConfiningMargins,fcConfinementMarginSegmentsBankSide)
        if not bOK:
            arcpy.AddWarning("An error occurred whilst preparing Confinement Margins layer!")
            arcpy.AddWarning("Make sure it has a valid MarginID and Length field")
        return True
    except arcpy.ExecuteError:
        # Geoprocessor threw an error
        arcpy.AddError(arcpy.GetMessages(2))
        return False
    except Exception as e:
        arcpy.AddError("Error in ConfiningMargins main function: " + str(e))
        return False

def determine_banks(fcInputStreamLineNetwork,fcChannelBankPolygons,scratchWorkspace):
    '''
        Description:
            Takes  the stream network, buffers out to the left by 1 meter, extracts centroid and
            uses that to select left channel bank (a layer with two polygons l/r), and sets bankside to LEFT
            then inverts selection and set that to RIGHT writing this back to fcChannelBankPolygons.

        Update: 24/8/18 - DDH -Added error trapping
    '''
    try:
        fcChannelBankSideBuffer = gis_tools.newGISDataset(scratchWorkspace,"BankSide_Buffer")
        fcChannelBankSidePoints = gis_tools.newGISDataset(scratchWorkspace,"BankSidePoints")
        arcpy.Buffer_analysis(fcInputStreamLineNetwork,fcChannelBankSideBuffer,"1 Meter","LEFT","FLAT","NONE")
        arcpy.FeatureToPoint_management(fcChannelBankSideBuffer,fcChannelBankSidePoints,"INSIDE")
        arcpy.AddField_management(fcChannelBankPolygons,"BankSide","TEXT","10")
        lyrChannelBanks = gis_tools.newGISDataset("Layer","lyrChannelBanks")
        arcpy.MakeFeatureLayer_management(fcChannelBankPolygons,lyrChannelBanks)
        arcpy.SelectLayerByLocation_management(lyrChannelBanks,"INTERSECT",fcChannelBankSidePoints,selection_type="NEW_SELECTION")
        arcpy.CalculateField_management(lyrChannelBanks,"BankSide","'LEFT'","PYTHON")
        arcpy.SelectLayerByAttribute_management(lyrChannelBanks,"SWITCH_SELECTION")
        arcpy.CalculateField_management(lyrChannelBanks,"BankSide","'RIGHT'","PYTHON")
        return
    except Exception as e:
        arcpy.AddError("Error in determine_banks function: " + str(e))

def transfer_line(fcInLine,fcToLine,strStreamSide):
    '''
    Inputs:
        fcInLine - Confinement margin segments with a selection imposed upon it
        fcToLine - The dissolved river network
        strStreamSide - LEFT or RIGHT
    Outputs:
        fcOutput - Featureclass type line, the network split

        Update: 24/8/18 - DDH -Added error trapping
    '''

    try:
        outputWorkspace = arcpy.Describe(fcInLine).path
        fcOutput = gis_tools.newGISDataset(outputWorkspace,"LineNetworkConfinement" + strStreamSide)

        # Split Line Network by Line Ends
        arcpy.AddMessage("... Splitting network")
        fcSplitPoints = gis_tools.newGISDataset(outputWorkspace,"SplitPoints_Confinement" + strStreamSide)
        arcpy.FeatureVerticesToPoints_management(fcInLine,fcSplitPoints,"BOTH_ENDS")
        tblNearPointsConfinement = gis_tools.newGISDataset(outputWorkspace,"NearPointsConfinement" + strStreamSide)
        arcpy.GenerateNearTable_analysis(fcSplitPoints,fcToLine,tblNearPointsConfinement,location="LOCATION",angle="ANGLE")
        lyrNearPointsConfinement = gis_tools.newGISDataset("Layer","lyrNearPointsConfinement"+ strStreamSide)
        arcpy.MakeXYEventLayer_management(tblNearPointsConfinement,"NEAR_X","NEAR_Y",lyrNearPointsConfinement,fcToLine)
        arcpy.SplitLineAtPoint_management(fcToLine,lyrNearPointsConfinement,fcOutput,search_radius="0.01 Meters")

        # Prepare Fields
        strConfinementField = "Con_" + strStreamSide
        arcpy.AddField_management(fcOutput,strConfinementField,"LONG")

        # Transfer Attributes by Centroids
        arcpy.AddMessage("... Updating Con_" + strStreamSide)
        fcCentroidPoints = gis_tools.newGISDataset(outputWorkspace,"CentroidPoints_Confinement" + strStreamSide)
        arcpy.FeatureVerticesToPoints_management(fcInLine,fcCentroidPoints,"MID")
        tblNearPointsCentroid = gis_tools.newGISDataset(outputWorkspace,"NearPointsCentroid" + strStreamSide)
        arcpy.GenerateNearTable_analysis(fcCentroidPoints,fcToLine,tblNearPointsCentroid,location="LOCATION",angle="ANGLE")
        lyrNearPointsCentroid = gis_tools.newGISDataset("Layer","lyrNearPointsCentroid" + strStreamSide)
        arcpy.MakeXYEventLayer_management(tblNearPointsCentroid,"NEAR_X","NEAR_Y",lyrNearPointsCentroid,fcToLine)
        lyrToLineSegments = gis_tools.newGISDataset("Layer","lyrToLineSegments")
        arcpy.MakeFeatureLayer_management(fcOutput,lyrToLineSegments)

        arcpy.SelectLayerByLocation_management(lyrToLineSegments,"INTERSECT",lyrNearPointsCentroid,selection_type="NEW_SELECTION")#"0.01 Meter","NEW_SELECTION")
        arcpy.CalculateField_management(lyrToLineSegments,strConfinementField,1,"PYTHON")

        bOK = postFIXtoConfinement(fcOutput,strStreamSide,lyrNearPointsConfinement,fcSplitPoints)
        if not bOK:
            arcpy.AddWarning("The post fix confinement code returned an error, centreline will be attributed incorrectly")
        return fcOutput
    except Exception as e:
        arcpy.AddError("Error in transfer_line function: " + str(e))

def postFIXtoConfinement(fcOutput,strStreamSide,lyrNearPointsConfinement,fcSplitPoints):
    '''
        Description:
            This code attempts to fix the issue described in https://github.com/Riverscapes/ConfinementTool/issues/30.

            The code steps through each segment, selects it's near points, gets their ID's, use these to select the split points
            and then checks if ORIG_FID are constant. If they are, the segment is correctly attributed with confinement side. If they
            are not then this must be an error and the segment field will be reset.

        Inputs:
            fcOutput                 = This is the segmented network for the RIGHT or LEFT side
            strStreamSide            = LEFT or RIGHT
            lyrNearPointsConfinement = A FeatureLayer, these are the points that were used to split the network, we will hook into the
                                       IN_FID field.
            fcSplitPoints            = These are the end points (nodes) of the confinement margin polyline and were used to create the points in
                                       lyrNearPointsConfinement. This is a featureclass.

        Outputs:
            Returns True if code executed without error else False.

        Limitations:
            Code assumes the temporary workspace is a file geodatabase.

        Author:
            Duncan Hornby (ddh@geodata.soton.ac.uk)

        Created:
            4/9/18
    '''
    # This is used to overcome issues of tolerance in the select by location tool, currently set to 5cm
    # you may need to change this.
    search_distance="5 Centimeters"

    # Create a layer object so selections can be done
    arcpy.MakeFeatureLayer_management(fcSplitPoints,"lyrSplitPoints")

    try:
        arcpy.AddMessage("Applying post fix confinement code to resolve geometry issues...")
        aField = "Con_" + strStreamSide

        # Get a count on number of features to process and initialise progress bar
        resObj = arcpy.GetCount_management(fcOutput)
        n = int(resObj.getOutput(0))
        arcpy.SetProgressor("step","Checking and fixing segments...",0,n,1)

        # Main loop to step through each segment and check
        with arcpy.da.UpdateCursor(fcOutput,["SHAPE@",aField]) as cursor:
            for row in cursor:
                arcpy.SetProgressorPosition()
                geom = row[0]

                # Use polyline to select near points
                arcpy.SelectLayerByLocation_management(lyrNearPointsConfinement,"INTERSECT",geom,search_distance,"NEW_SELECTION","NOT_INVERT")

                # Now read the IN_FID values from the selected rows into a list
                idList = []
                with arcpy.da.SearchCursor(lyrNearPointsConfinement,["IN_FID"]) as cursor2:
                    for row2 in cursor2:
                        idList.append(row2[0])

                # Check u/s and d/s limit selections where only 1 point will be selected
                if len(idList) == 1:
                    arcpy.AddMessage("Skipping an end segment")
                else:

                    # Now build a SQL query that can be used to select rows using the ID's in idList in the split points layer
                    myTup = str(tuple(idList))
                    sql = "OBJECTID IN " + myTup
                    #arcpy.AddMessage(sql)
                    arcpy.SelectLayerByAttribute_management("lyrSplitPoints", "NEW_SELECTION", sql)

                    # Now read the ORIG_FID into a set, if 2 values are found then the line was incorrectly tagged and the aField needs resetting to null
                    s = set()
                    with arcpy.da.SearchCursor("lyrSplitPoints",["ORIG_FID"]) as cursor3:
                        for row3 in cursor3:
                            s.add(row3[0])

                    if len(s) == 2:
                        # Segmented was incorrectly identified the wrong confinement side, reset to null
                        row[1] = None
                    else:
                        row[1] = 1 # Be aware this may incorrectly set a segment that has 3 node intersections at one end.
                    cursor.updateRow(row)

        # Got here code ran without error
        arcpy.ResetProgressor()
        return True
    except Exception as e:
        arcpy.AddError("Error in postFIXtoConfinement function: " + str(e))
        return False
    finally:
        arcpy.Delete_management("lyrSplitPoints")

def integrated_width(fcInLines, fcInPolygons, fcOutLines, strMetricName="", boolSegmentPolygon=False, temp_workspace="in_memory"):
     # This code is never executed as the boolean flag that calls this is always FALSE
    fcMemLines = gis_tools.newGISDataset(temp_workspace,"lineNetwork")
    arcpy.CopyFeatures_management(fcInLines,fcMemLines)
    fieldLength = gis_tools.resetField(fcMemLines,"IW_Length","DOUBLE")
    arcpy.CalculateField_management(fcMemLines,fieldLength,"!Shape!.length","PYTHON")

    fcMemPolygons = gis_tools.newGISDataset(temp_workspace,'Polygons')
    if boolSegmentPolygon:
        DividePolygonBySegment.main(fcMemLines, fcInPolygons, fcMemPolygons, temp_workspace, dblPointDensity=5.0)
    else:
        arcpy.CopyFeatures_management(fcInPolygons,fcMemPolygons)

    fieldPolygonArea = gis_tools.resetField(fcMemPolygons, strMetricName[0:6] + "Area","DOUBLE")
    arcpy.CalculateField_management(fcMemPolygons, fieldPolygonArea, "!Shape!.area", "PYTHON")

    f_mappings = arcpy.FieldMappings()
    f_mappings.addTable(fcMemLines)
    fmap_area = arcpy.FieldMap()
    fmap_area.addInputField(fcMemPolygons, fieldPolygonArea)
    f_mappings.addFieldMap(fmap_area)

    arcpy.SpatialJoin_analysis(fcMemLines, fcMemPolygons, fcOutLines, "JOIN_ONE_TO_ONE", "KEEP_ALL",
                               field_mapping=f_mappings, match_option="WITHIN")
    fieldIntegratedWidth = gis_tools.resetField(fcOutLines, "IW" + strMetricName[0:8], "DOUBLE")
    exp = "!" + fieldPolygonArea + r"! / !" + fieldLength + "!"
    print exp
    arcpy.CalculateField_management(fcOutLines, fieldIntegratedWidth, exp, "PYTHON_9.3")

    return fieldIntegratedWidth

def prepConfinementOutput(fc,fcBankSide):
    '''
        Description:
            This function cleans up the output shapefile by deleting all but the Length field (created by an earlier step)
            and adds a MarginID which is simply an incremental number. This prepares the data for the intersect with geology model
            Tool.

        Inputs:
            fc = The Confinement Margin FeaureClass

        Outputs:
            Returns True if code executed without error else False.

        Limitations:
            Code assumes the FeatureClass to be Shapefile format

        Author:
            Duncan Hornby (ddh@geodata.soton.ac.uk)

        Created:
            6/9/18
        Updated:
            6/11/18 - Add code to pass over bank side to Confining Margin
    '''
    try:
        # Create a list of field names to delete
        arcpy.AddMessage("... Deleting unnecessary fields")
        fieldsList = [f.name for f in arcpy.ListFields(fc)]
        fieldsList.remove("FID")
        fieldsList.remove("Shape")
        fieldsList.remove("Length")
        arcpy.DeleteField_management(fc,fieldsList)

        # Add MarginID and set with incremental number
        arcpy.AddMessage("... Creating MarginID field")
        i = 1
        arcpy.AddField_management(fc,"MarginID","LONG")
        with arcpy.da.UpdateCursor(fc,["MarginID"]) as cursor:
            for row in cursor:
                row[0] = i
                cursor.updateRow(row)
                i = i + 1

        # Create a dictionary where key is an XY tup of centroid and item is the bank side text
        arcpy.AddMessage("... Extracting bankside information")
        aDictBankSide = {}
        with arcpy.da.SearchCursor(fcBankSide,["Shape@XY","BankSide"]) as cursor:
            for row in cursor:
                aDictBankSide[row[0]] = row[1]

        # Add bankside field then update.
        arcpy.AddMessage("... Transferring bankside details to Margins")
        arcpy.AddField_management(fc,"BankSide","TEXT","10")
        arcpy.AddMessage("... Extracting Margin information")
        with arcpy.da.UpdateCursor(fc,["Shape@XY","BankSide"]) as cursor:
            for row in cursor:
                xyTup = row[0]
                side = aDictBankSide[xyTup] # Get the bankside
                row[1] = side
                cursor.updateRow(row)

        # Got here so all OK
        del aDictBankSide
        return True
    except Exception as e:
        arcpy.AddError("Error in prepConfinementOutput() function")
        arcpy.AddError(str(e))
        return False
if __name__ == "__main__":
    main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6])