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

__version__ = '0.0.1'

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

        # Workspace
        p1 = arcpy.Parameter(
            name="workspace",
            displayName="Workspace",
            direction="Input",
            datatype="DEWorkspace",
            parameterType="Required",
            enabled=True,
            category="Workspace" )
        p1.value = arcpy.env.workspace

        # input segmented stream network
        network = arcpy.GetParameterAsText(1)
        p2 = arcpy.Parameter(
            name="network",
            displayName="Segmented Network",
            direction="Input",
            datatype="GPFeatureLayer",
            parameterType="Required",
            enabled=True)

        # input flow accumulation in units of km2
        p3 = arcpy.Parameter(
            name="flow_acc",
            displayName="Flow Accumulation Raster",
            direction="Input",
            datatype="GPRasterLayer",
            parameterType="Required",
            enabled=True)

        # input average annual precip vector layer downloadable from USDA geospatial data gateway
        p4 = arcpy.Parameter(
            name="precip",
            displayName="Precipitation Raster (cm)",
            direction="Input",
            datatype="GPRasterLayer",
            parameterType="Required",
            enabled=True)

        # input valley bottom polygon
        p5 = arcpy.Parameter(
            name="valleybottom",
            displayName="Valley Bottom Polygon",
            direction="Input",
            datatype="GPFeatureLayer",
            parameterType="Required",
            enabled=True)

        # specify output
        p6 = arcpy.Parameter(
            name="output",
            displayName="Output Bankfull Channel",
            direction="Output",
            datatype="DEFeatureClass",
            parameterType="Required",
            enabled=True)

        # Minimum Width
        p7 = arcpy.Parameter(
            name="min_width",
            displayName="Minimum Width  (map units)",
            direction="Input",
            datatype="GPDouble",
            parameterType="Required",
            enabled=True)
        p7.value = 5.0

        # Percent Buffer
        p8 = arcpy.Parameter(
            name="percent_buffer",
            displayName="Percent Buffer",
            direction="Input",
            datatype="GPDouble",
            parameterType="Required",
            enabled=True)
        p8.value = 100

        p9 = arcpy.Parameter(
            name="keep_temp",
            displayName="Delete Temporary Files?",
            direction="Input",
            datatype="GPBoolean",
            parameterType="Required",
            category="Workspace",
            enabled=True)
        p9.value = True

        params = [p1, p2, p3, p4, p5, p6, p7, p8, p9]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        # Code added by DDH on 20/6/18
        if arcpy.ProductInfo() in ["ArcView","ArcEditor","ArcInfo"]:
            if arcpy.ProductInfo() in ["ArcView","ArcEditor"]:
                if arcpy.CheckExtension("Spatial") == "Available":
                    # Spatial Analyst extension available so check it out as an
                    # Arcview/Spatial combination is valid to allow the Polygon
                    # to raster tool to execute.
                    arcpy.CheckOutExtenstion("Spatial")
                else:
                    # Extension not available so tool will not work
                    return False
            else:
                # Advance licensed machine
                return True
        else:
            # No valid desktop license
            return False

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

        arcpy.env.workspace = p[0].valueAsText

        # if precip is vector, convert to cm

        main(p[1].valueAsText,
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
        if arcpy.ProductInfo() != "ArcView":
            return False
        else:
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


def main(network, drarea, precip, valleybottom, output, MinBankfullWidth, dblPercentBuffer, deleteTemp="True"):

    arcpy.env.overwriteOutput = True
    datasets = {}

    #todo use densification points for thiessen?

    #create thiessen polygons from segmented stream network
    datasets['midpoints'] = "midpoints.shp"
    arcpy.FeatureVerticesToPoints_management(network, datasets['midpoints'], "MID")

    arcpy.AddMessage("creating thiessen polygons")
    datasets['thiessen'] = "thiessen.shp"
    arcpy.CreateThiessenPolygons_analysis(datasets['midpoints'], datasets['thiessen'])
    datasets['thiessen_clip'] = "thiessen_clip.shp"
    datasets['valley_buffer'] = "valley_buffer.shp"
    arcpy.Buffer_analysis(valleybottom,  datasets['valley_buffer'], "15 Meters", "FULL", "ROUND", "ALL")
    arcpy.Clip_analysis(datasets['thiessen'],  datasets['valley_buffer'], datasets['thiessen_clip'])

    # Zonal statistics of drainage area and precip using thiessen polygons
    arcpy.AddMessage("calculating zonal statistics for precip and drainage area")
    datasets["tbl_drarea_zs"] = "zonal_table_drarea"
    datasets["tbl_precip_zs"] = "zonal_table_precip"
    ZonalStatisticsAsTable(datasets['thiessen_clip'], "FID", drarea, datasets["tbl_drarea_zs"], "DATA", "MAXIMUM")
    ZonalStatisticsAsTable(datasets['thiessen_clip'], "FID", precip, datasets["tbl_precip_zs"], "DATA", "MAXIMUM")

    # # convert rasters to integers
    # int_dr_area = Int(dr_area_zs)
    # int_precip = Int(precip_zs)
    #
    # # convert integer rasters to polygons
    #datasets['max_dr_area_poly'] = "max_dr_area_poly.shp"
    #datasets['max_precip_poly'] = "max_precip_poly.shp"
    # arcpy.RasterToPolygon_conversion(dr_area_zs, datasets['max_dr_area_poly'])
    # arcpy.RasterToPolygon_conversion(precip_zs, datasets['max_precip_poly'])

    arcpy.JoinField_management(datasets['thiessen_clip'], "FID", datasets["tbl_drarea_zs"], "FID", "MAX")
    arcpy.AddField_management(datasets['thiessen_clip'], "DRAREA", "FLOAT")
    with arcpy.da.UpdateCursor(datasets['thiessen_clip'], ["MAX", "DRAREA"]) as cursor:
        for row in cursor:
            row[1] = row[0]
            cursor.updateRow(row)
    arcpy.DeleteField_management(datasets['thiessen_clip'], "MAX")

    arcpy.JoinField_management(datasets['thiessen_clip'], "FID", datasets["tbl_precip_zs"], "FID", "MAX")
    arcpy.AddField_management(datasets['thiessen_clip'], "PRECIP", "FLOAT")
    with arcpy.da.UpdateCursor(datasets['thiessen_clip'], ["MAX", "PRECIP"]) as cursor:
        for row in cursor:
            row[1] = row[0]
            cursor.updateRow(row)
    arcpy.DeleteField_management(datasets['thiessen_clip'], "MAX")

    # dissolve network and intersect with both rasters
    arcpy.AddMessage("applying precip and drainage area data to line network")
    datasets['dissolved_network'] = "dissolved_network.shp"
    arcpy.Dissolve_management(network, datasets['dissolved_network'])

    datasets['intersect'] = "intersect.shp"
    arcpy.Intersect_analysis([datasets['dissolved_network'], datasets['thiessen_clip']], datasets['intersect'], "", "", "LINE")
    # datasets['intersect2'] = "intersect2.shp"
    # arcpy.Intersect_analysis([datasets['intersect1'], datasets['max_precip_poly']], datasets['intersect2'], "", "", "LINE")

    arcpy.AddField_management(datasets['intersect'], "BFWIDTH", "FLOAT")
    with arcpy.da.UpdateCursor(datasets['intersect'], ["DRAREA", "PRECIP", "BFWIDTH"])as cursor:
        for row in cursor:
            row[2] = 0.177*(pow(row[0],0.397))*(pow(row[1],0.453))
            cursor.updateRow(row)

    arcpy.AddField_management(datasets['intersect'], "BUFWIDTH", "DOUBLE")
    with arcpy.da.UpdateCursor(datasets['intersect'], ["BFWIDTH", "BUFWIDTH"]) as cursor:
        for row in cursor:
            row[1] = row[0]/2 + ((row[0]/2) * (float(dblPercentBuffer)/100))
            cursor.updateRow(row)

    # buffer network by bufwidth field to create bankfull polygon
    arcpy.AddMessage("buffering network")
    datasets['bankfull'] = "bankfull.shp"
    arcpy.Buffer_analysis(datasets['intersect'], datasets['bankfull'], "BUFWIDTH", "FULL", "ROUND", "ALL")

    datasets['bankfull_min_buffer'] = "min_buffer.shp"
    datasets['bankfull_merge'] = "bankfull_merge.shp"
    datasets['bankfull_dissolve'] = "bankfull_dissolve.shp"
    arcpy.Buffer_analysis(network, datasets['bankfull_min_buffer'], str(MinBankfullWidth), "FULL", "ROUND", "ALL")
    arcpy.Merge_management([datasets['bankfull'], datasets['bankfull_min_buffer']], datasets['bankfull_merge'])
    arcpy.Dissolve_management(datasets['bankfull_merge'], datasets['bankfull_dissolve'])

    #smooth for final bunkfull polygon
    arcpy.AddMessage("smoothing final bankfull polygon")
    arcpy.SmoothPolygon_cartography(datasets['bankfull_dissolve'], output, "PAEK", "10 METERS") # TODO: Expose parameter?

    # Todo: add params as fields to shp.

    if deleteTemp == "True":
        arcpy.AddMessage("deleting temporary files")
        for dataset in datasets.itervalues():
            if arcpy.Exists(dataset):
                arcpy.Delete_management(dataset)

    #del dr_area_zs, precip_zs, int_dr_area, int_precip


if __name__ == "__main__":
    import argparse


    #main()
