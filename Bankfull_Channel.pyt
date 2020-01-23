#-------------------------------------------------------------------------------
# Name:        Bankfull Channel
# Purpose:     Creates a polygon representing the bankfull channel for the input
#              network.  The regression used to derive this bankfull estimate
#              was developed by T. Beechie and H. Imaki for the interior Columbia
#              River Basin
#
# Author:      Jordan
#
# Created:     05/2015
# Copyright:   (c) Jordan 2015
# Modified     12/2017 Kelly Whitehead @ South Fork Research
# License:     <your license>
#-------------------------------------------------------------------------------

import arcpy
from arcpy.sa import *
import os
import shutil

#__version__ = 0.0.1

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Bankfull Channel"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [BankfullChannelTool]


class BankfullChannelTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Bankfull Channel"
        self.description = "Generate a Bankfull Channel with or without a percent buffer."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        # input segmented stream network
        network = arcpy.GetParameterAsText(1)
        p1 = arcpy.Parameter(
            name="network",
            displayName="Segmented Network",
            direction="Input",
            datatype="GPFeatureLayer",
            parameterType="Required",
            enabled=True)

        # input flow accumulation in units of km2
        p2 = arcpy.Parameter(
            name="flow_acc",
            displayName="Flow Accumulation Raster",
            direction="Input",
            datatype="GPRasterLayer",
            parameterType="Required",
            enabled=True)

        # input average annual precip vector layer downloadable from PRISM #USDA geospatial data gateway
        p3 = arcpy.Parameter(
            name="precip",
            displayName="PRISM Precipitation Raster (mm)",
            direction="Input",
            datatype="GPRasterLayer",
            parameterType="Required",
            enabled=True)

        # input valley bottom polygon
        p4 = arcpy.Parameter(
            name="valleybottom",
            displayName="Valley Bottom Polygon",
            direction="Input",
            datatype="GPFeatureLayer",
            parameterType="Required",
            enabled=True)

        # specify output
        p5 = arcpy.Parameter(
            name="out_dir",
            displayName="Output Folder (for storing outputs)",
            direction="Output",
            datatype="DEFolder",
            parameterType="Required",
            enabled=True)

        # Minimum Width
        p6 = arcpy.Parameter(
            name="min_width",
            displayName="Minimum Width  (map units)",
            direction="Input",
            datatype="GPDouble",
            parameterType="Required",
            enabled=True)
        p6.value = 5.0

        # Percent Buffer
        p7 = arcpy.Parameter(
            name="percent_buffer",
            displayName="Percent Buffer",
            direction="Input",
            datatype="GPDouble",
            parameterType="Required",
            enabled=True)
        p7.value = 100

        # Workspace
        p8 = arcpy.Parameter(
            displayName="Temporary Folder (for storing intermediates)",
            name="temp_dir",
            direction="Input",
            datatype="DEFolder",
            parameterType="Required",
            enabled=True)
            #category="Workspace" )

        p9 = arcpy.Parameter(
            name="keep_temp",
            displayName="Delete Temporary Files?",
            direction="Input",
            datatype="GPBoolean",
            parameterType="Required",
            #category="Workspace",
            enabled=True)
        p9.value = True

        params = [p1, p2, p3, p4, p5, p6, p7, p8, p9]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        """The source code of the tool."""

        arcpy.env.workspace = p[8].valueAsText

        # if precip is vector, convert to cm

        main(p[0].valueAsText,
             p[1].valueAsText,
             p[2].valueAsText,
             p[3].valueAsText,
             p[4].valueAsText,
             p[5].valueAsText,
             p[6].valueAsText,
             p[7].valueAsText,
             p[8].valueAsText)
        
        return


class PrecipitationToRasterTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Vector Precip to Raster"
        self.description = "Generate a precipitation raster from usda precip shapefile."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        # Workspace
        p1 = arcpy.Parameter(
            name="Workspace",
            displayName="Workspace",
            direction="Input",
            datatype="DEWorkspace",
            parameterType="Required",
            enabled=True)

        # input vector
        network = arcpy.GetParameterAsText(1)
        p2 = arcpy.Parameter(
            name="percent_buffer",
            displayName="Percent Buffer",
            direction="Input",
            datatype="GPDouble",
            parameterType="Required",
            enabled=True)

        # Output raster
        p3 = arcpy.Parameter(
             name="output_raster",
             displayName="Output Precipitation Raster",
             direction="Input",
             datatype="DEraster",
             parameterType="Required",
             enabled=True)

        params = [p1,p2,p3]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        """The source code of the tool."""

        arcpy.env.workspace = p[0].valueAsText()

        # if precip is vector, convert to cm
        precip = p[1].valueAsText()
        precip_out = p[2].valueAsText()

        # convert precip units to cm and conver vector to raster
        arcpy.AddMessage("converting precip to cm")
        arcpy.AddField_management(precip, "CM", "DOUBLE")
        with arcpy.da.UpdateCursor(precip, ["Inches", "CM"]) as cursor:
            for row in cursor:
                row[1] = row[0] * 2.54
                cursor.updateRow(row)
        arcpy.PolygonToRaster_conversion(precip, "CM", precip_out, "", "", 30)

        return


def main(network, drarea, precip, valleybottom, out_dir, MinBankfullWidth, dblPercentBuffer, temp_dir, deleteTemp):

    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension('Spatial')
	
    #workspace = arcpy.env.workspace
    #datasets = {}

    # clean and make new temp_dir
    #if os.path.exists(temp_dir):
    #    shutil.rmtree(temp_dir)
    #os.mkdir(temp_dir)
    workspace = temp_dir

    # make output directory
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    #create thiessen polygons from segmented stream network
    midpoints = os.path.join(workspace, "midpoints.shp")
    #network_lyr = "network.lyr"
    #arcpy.MakeFeatureLayer_management(network, network_lyr)
    arcpy.FeatureVerticesToPoints_management(network, midpoints, "MID")

    arcpy.AddMessage("creating thiessen polygons")
    print '.....creating thiessen polygons'
    thiessen = os.path.join(workspace, "thiessen.shp")
    arcpy.CreateThiessenPolygons_analysis(midpoints, thiessen)
    thiessen_clip = os.path.join(workspace, "thiessen_clip.shp")
    valley_buffer = os.path.join(workspace, "valley_buffer.shp")
    arcpy.Buffer_analysis(valleybottom,  valley_buffer, "15 Meters", "FULL", "ROUND", "ALL")
    arcpy.Clip_analysis(thiessen,  valley_buffer, thiessen_clip)

    # Zonal statistics of drainage area and precip using thiessen polygons
    print ".....calculating precip and drainage area for each thiessen polygon"
    arcpy.AddMessage("calculating zonal statistics for precip and drainage area")
    #tbl_drarea_zs = os.path.join(workspace, "zonal_table_drarea")
    #tbl_precip_zs = os.path.join(workspace, "zonal_table_precip")
    tbl_drarea_zs = os.path.join(workspace, "zonal_table_drarea.dbf")
    tbl_drarea_zs = ZonalStatisticsAsTable(thiessen_clip, "FID", drarea, tbl_drarea_zs, "DATA", "MAXIMUM")
    tbl_precip_zs = os.path.join(workspace, "zonal_table_precip.dbf")
    tbl_precip_zs = ZonalStatisticsAsTable(thiessen_clip, "FID", precip, tbl_precip_zs, "DATA", "MAXIMUM")

    # # convert rasters to integers
    # int_dr_area = Int(dr_area_zs)
    # int_precip = Int(precip_zs)
    #
    # # convert integer rasters to polygons
    #max_dr_area_poly = os.path.join(workspace, "max_dr_area_poly")
    #max_precip_poly = os.path.join(workspace, "max_precip_poly")
    # arcpy.RasterToPolygon_conversion(dr_area_zs, max_dr_area_poly)
    # arcpy.RasterToPolygon_conversion(precip_zs, max_precip_poly)

    # join thiessen clip to tbl_drarea_zs and calculate drarea for each thiessen polygon    
    arcpy.JoinField_management(thiessen_clip, "FID", tbl_drarea_zs, "FID_", "MAX")
    arcpy.AddField_management(thiessen_clip, "DRAREA", "FLOAT")
    with arcpy.da.UpdateCursor(thiessen_clip, ["MAX", "DRAREA"]) as cursor:
        for row in cursor:
            row[1] = row[0]
            cursor.updateRow(row)
    arcpy.DeleteField_management(thiessen_clip, "MAX")
  
    # join thiessen clip to tbl_precip_zs and calculate precip for each thiessen polygon
    arcpy.JoinField_management(thiessen_clip, "FID", tbl_precip_zs, "FID_", "MAX")
    arcpy.AddField_management(thiessen_clip, "PRECIP", "FLOAT")
    with arcpy.da.UpdateCursor(thiessen_clip, ["MAX", "PRECIP"]) as cursor:
        for row in cursor:
            row[1] = row[0]
            cursor.updateRow(row)
    arcpy.DeleteField_management(thiessen_clip, "MAX")

    ## We're going to extract raster values to the center of each thiessen polygon that did not
    ## receive a value using zonal statistics. Most polygons are being "missed" for precip and some
    ## for drainage area since the raster resolution is larger than many of these tiny thiessen polygons -
    ## especially with the 800 meters-squared PRISM data.

    # get list of original fields before anything else
    thiessen_fields = [f.name for f in arcpy.ListFields(thiessen_clip)]
    # select thiessen polygons with no drainage area data
    no_drarea_data = arcpy.Select_analysis(thiessen_clip, None, """ "DRAREA" = 0 """)
    # convert selected polygons to centroid points
    drarea_pts = os.path.join(temp_dir, "missing_drarea_pts.shp")
    arcpy.FeatureToPoint_management(no_drarea_data, drarea_pts, "INSIDE")
    # extract values from raster to points
    missing_drarea_data = os.path.join(temp_dir, "missing_drarea_data.shp")
    arcpy.sa.ExtractValuesToPoints(drarea_pts, drarea, missing_drarea_data)
    # join points to selected polygons
    filled_missing_drarea = os.path.join(temp_dir, "filled_missing_drarea.shp")
    needed_fields = thiessen_fields.append("RASTERVALU")
    arcpy.SpatialJoin_analysis(no_drarea_data, missing_drarea_data, filled_missing_drarea,
                               join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_ALL",
                               field_mapping=needed_fields, match_option="CONTAINS")
    # join selected polygons to original thiessen polygons
    arcpy.JoinField_management(thiessen_clip, "Input_FID", filled_missing_drarea, "Input_FID")
    # fill in missing DRAREA values based on raster values extracted to points
    with arcpy.da.UpdateCursor(thiessen_clip, ["DRAREA", "RASTERVALU"]) as cursor:
        for row in cursor:
            if row[0] == 0:
                row[0] = row[1]
            cursor.updateRow(row)
    # delete all extra fields joined to original thiessen polygons
    arcpy.DeleteField_management(thiessen_clip, "RASTERVALU")
    all_fields = [f.name for f in arcpy.ListFields(thiessen_clip)]
    for f in all_fields:
        if f not in thiessen_fields:
            try:
                arcpy.DeleteField_management(thiessen_clip, f)
            except Exception as err:
                print "Could not delete unnecessary field " + f + " from thiessen_clip.shp"
                print "Error thrown was"
                print err

    # same thing for PRECIP field....
    # set output names
    no_precip_data = arcpy.Select_analysis(thiessen_clip, None, """ "PRECIP" = 0 """)
    precip_pts = os.path.join(temp_dir, "missing_precip_pts.shp")
    missing_precip_data = os.path.join(temp_dir, "missing_precip_data.shp")
    filled_missing_precip = os.path.join(temp_dir, "filled_missing_precip.shp")
    # convert polygons to centroid points - "inside" set so that points end up in
    # original polygon, otherwise spatial join misses some points
    arcpy.FeatureToPoint_management(no_precip_data, precip_pts, "INSIDE")
    # remove RASTERVALU to prevent error...
    precip_pts_fields = [f.name for f in arcpy.ListFields(precip_pts)]
    if "RASTERVALU" in precip_pts_fields:
        arcpy.DeleteField_management(precip_pts, "RASTERVALU")
    if os.path.exists(missing_precip_data):
        missing_precip_fields = [f.name for f in arcpy.ListFields(missing_precip_data)]
        if "RASTERVALU" in missing_precip_fields:
            arcpy.DeleteField_management(missing_precip_data, "RASTERVALU")
    arcpy.sa.ExtractValuesToPoints(precip_pts, precip, missing_precip_data)
    needed_fields = thiessen_fields.append("RASTERVALU")
    arcpy.SpatialJoin_analysis(no_precip_data, missing_precip_data, filled_missing_precip,
                               join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_ALL",
                               field_mapping=needed_fields, match_option="CONTAINS")
    arcpy.JoinField_management(thiessen_clip, "Input_FID", filled_missing_precip, "Input_FID")
    with arcpy.da.UpdateCursor(thiessen_clip, ["PRECIP", "RASTERVALU"]) as cursor:
        for row in cursor:
            if row[0] == 0:
                row[0] = row[1]
            cursor.updateRow(row)
    arcpy.DeleteField_management(thiessen_clip, "RASTERVALU")
    all_fields = [f.name for f in arcpy.ListFields(thiessen_clip)]
    for f in all_fields:
        if f not in thiessen_fields:
            try:
                arcpy.DeleteField_management(thiessen_clip, f)
            except Exception as err:
                print "Could not delete unnecessary field " + f + " from thiessen_clip.shp"
                print "Error thrown was"
                print err
    
    # dissolve network and intersect with both rasters
    arcpy.AddMessage("applying precip and drainage area data to line network")
    print ".....adding precip and drainage area data to the line network"
    dissolved_network = os.path.join(workspace, "dissolved_network.shp")
    arcpy.Dissolve_management(network, dissolved_network)

    intersect = os.path.join(out_dir, "network_buffer_values.shp")
    arcpy.Intersect_analysis([dissolved_network, thiessen_clip], intersect, "", "", "LINE")
    # intersect2 = os.path.join(workspace, "intersect2")
    # arcpy.Intersect_analysis([intersect, dmax_precip_poly], intersect2, "", "", "LINE")

    arcpy.AddField_management(intersect, "BFWIDTH", "FLOAT")
    with arcpy.da.UpdateCursor(intersect, ["DRAREA", "PRECIP", "BFWIDTH"])as cursor:
        for row in cursor:
            # if row[0] == ' ' or row[1] == ' ':
                precip_cm = row[1]/10
                drarea = row[0]
                row[2] = 0.177*(pow(drarea,0.397))*(pow(precip_cm,0.453))
                if row[2] < float(MinBankfullWidth):
                    row[2] = float(MinBankfullWidth)
            #else:
                #   row[2] = ' '
                cursor.updateRow(row)

    arcpy.AddField_management(intersect, "BUFWIDTH", "DOUBLE")
    with arcpy.da.UpdateCursor(intersect, ["BFWIDTH", "BUFWIDTH"]) as cursor:
        for row in cursor:
            row[1] = row[0]/2 + ((row[0]/2) * (float(dblPercentBuffer)/100))
            cursor.updateRow(row)

    # buffer network by bufwidth field to create bankfull polygon
    arcpy.AddMessage("buffering network")
    print ".....buffering network"
    bankfull = os.path.join(workspace, "bankfull.shp")
    arcpy.Buffer_analysis(intersect, bankfull, "BUFWIDTH", "FULL", "ROUND", "ALL")

    bankfull_min_buffer = os.path.join(workspace, "min_buffer.shp")
    bankfull_merge = os.path.join(workspace, "bankfull_merge.shp")
    bankfull_dissolve = os.path.join(workspace, "bankfull_dissolve.shp")
    arcpy.Buffer_analysis(network, bankfull_min_buffer, str(MinBankfullWidth), "FULL", "ROUND", "ALL")
    arcpy.Merge_management([bankfull, bankfull_min_buffer], bankfull_merge)
    arcpy.Dissolve_management(bankfull_merge, bankfull_dissolve)

    #smooth for final bunkfull polygon
    arcpy.AddMessage("smoothing final bankfull polygon")
    print ".....smoothing final bankfull polygon"
    output = os.path.join(out_dir, "final_bankfull_channel.shp")
    arcpy.SmoothPolygon_cartography(bankfull_dissolve, output, "PAEK", "10 METERS") # TODO: Expose parameter?
    
    # Todo: add params as fields to shp.

    if deleteTemp == "True":
        print ".....deleting temporary directory"
        try:
            shutil.rmtree(temp_dir)
        except Exception as err:
            print "Could not delete temp_dir, but final outputs are saved"
        #datasets = [midpoints, thiessen, valley_buffer, thiessen_clip, dissolved_network, intersect, bankfull, bankfull_min_buffer,
        #            bankfull_merge, bankfull_dissolve]
        #arcpy.AddMessage("deleting temporary files")
        #for dataset in datasets:
        #    if arcpy.Exists(dataset):
        #        arcpy.Delete_management(dataset)

    #del dr_area_zs, precip_zs, int_dr_area, int_precip


if __name__ == "__main__":
    import argparse


    #main()
