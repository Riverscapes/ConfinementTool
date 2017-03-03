# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Name:        Moving Window Analysis for Line Network                        #
# Purpose:     Run a generic moving window analysis for a variable along a    #
#              line network.                                                  #
#                                                                             #
# Author:      Kelly Whitehead (kelly@southforkresearch.org)                  #
#              South Fork Research, Inc                                       #
#              Seattle, Washington                                            #
#                                                                             #
# Created:     2015-May-05                                                    # 
# Version:     1.2                                                            #
# Modified:    2015-May-05                                                    #
#                                                                             #
# Copyright:   (c) Kelly Whitehead 2015                                       #
#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#!/usr/bin/env python

# # Import Modules # #
import os
import sys
import arcpy
import gis_tools

# # Main Function # # 
def main(
    fcLineNetwork,
    fieldStreamRouteID,
    fieldConfinement,
    fieldConstriction,
    strSeedDistance,
    inputliststrWindowSize,
    outputWorkspace,
    tempWorkspace=arcpy.env.scratchWorkspace):
    """Perform a Moving Window Analysis on a Line Network."""

    liststrWindowSize = inputliststrWindowSize.split(";")

    fcLineNetworkDissolved = gis_tools.newGISDataset(tempWorkspace,"GNAT_MWA_LineNetworkDissolved")
    arcpy.Dissolve_management(fcLineNetwork,fcLineNetworkDissolved,fieldStreamRouteID,multi_part=False,unsplit_lines=True)

    listLineGeometries = arcpy.CopyFeatures_management(fcLineNetworkDissolved,arcpy.Geometry())
    
    listWindows = []
    listSeeds = []
    listWindowEvents = []
    listgWindows = []
    intSeedID = 0
    
    iRoutes = int(arcpy.GetCount_management(fcLineNetworkDissolved).getOutput(0))
    arcpy.SetProgressor("step","Processing Each Route",0,iRoutes,1)
    iRoute = 0
    with arcpy.da.SearchCursor(fcLineNetworkDissolved,["SHAPE@",fieldStreamRouteID,"SHAPE@LENGTH"]) as scLines:
        for fLine in scLines: #Loop Through Routes
            arcpy.SetProgressorLabel("Route: " + str(iRoute) + " Seed Point: " + str(intSeedID))
            arcpy.SetProgressorPosition(iRoute)
            gLine = fLine[0]
            dblSeedPointPosition = float(max(liststrWindowSize))/2 #Start Seeds at position of largest window
            while dblSeedPointPosition + float(max(liststrWindowSize))/2 < fLine[2]:
                arcpy.SetProgressorLabel("Route: " + str(iRoute) + " Seed Point: " + str(intSeedID))
                gSeedPointPosition = gLine.positionAlongLine(dblSeedPointPosition)
                listSeeds.append([scLines[1],intSeedID,gSeedPointPosition])#gSeedPointPosition.X,gSeedPointPosition.Y])
                for strWindowSize in liststrWindowSize:
                    dblWindowSize = float(strWindowSize)
                    dblLengthStart = dblSeedPointPosition - dblWindowSize/2
                    dblLengthEnd = dblSeedPointPosition + dblWindowSize/2
                    
                    gPointStartLocation = gLine.positionAlongLine(dblLengthStart)
                    gPointEndLocation = gLine.positionAlongLine(dblLengthEnd)
                    gTemp = arcpy.Geometry()
                    listgWindowTemp = arcpy.SplitLineAtPoint_management(gLine,[gPointStartLocation,gPointEndLocation],gTemp,"1 METER")
                    #TODO: Need a better method to select the line here!!
                    for gWindowTemp in listgWindowTemp:
                        if abs(gWindowTemp.length - dblWindowSize) < 10 :
                            listgWindows.append([scLines[1],intSeedID,dblWindowSize,gWindowTemp])
                    # End TODO
                    listWindows.append([scLines[1],intSeedID,dblWindowSize,gPointStartLocation])
                    listWindows.append([scLines[1],intSeedID,dblWindowSize,gPointEndLocation])
                    listWindowEvents.append([scLines[1],intSeedID,dblWindowSize,dblLengthStart,dblLengthEnd])
                dblSeedPointPosition = dblSeedPointPosition + float(strSeedDistance)
                intSeedID = intSeedID + 1
            iRoute = iRoute + 1

    fcSeedPoints = gis_tools.newGISDataset(tempWorkspace,"GNAT_MWA_SeedPoints")
    fcWindowEndPoints = gis_tools.newGISDataset(tempWorkspace,"GNAT_MWA_WindowEndPoints")
    fcWindowLines = gis_tools.newGISDataset(tempWorkspace,"GNAT_MWA_WindowLines")
      
    arcpy.CreateFeatureclass_management(tempWorkspace,"GNAT_MWA_SeedPoints","POINT",spatial_reference=fcLineNetwork)
    arcpy.CreateFeatureclass_management(tempWorkspace,"GNAT_MWA_WindowEndPoints","POINT",spatial_reference=fcLineNetwork)
    arcpy.CreateFeatureclass_management(tempWorkspace,"GNAT_MWA_WindowLines","POLYLINE",spatial_reference=fcLineNetwork)

    gis_tools.resetField(fcSeedPoints,"RouteID","LONG")
    gis_tools.resetField(fcSeedPoints,"SeedID","LONG")
    
    gis_tools.resetField(fcWindowEndPoints,"RouteID","LONG")
    gis_tools.resetField(fcWindowEndPoints,"SeedID","LONG")
    gis_tools.resetField(fcWindowEndPoints,"Seg","DOUBLE")

    gis_tools.resetField(fcWindowLines,"RouteID","LONG")
    gis_tools.resetField(fcWindowLines,"SeedID","LONG")
    gis_tools.resetField(fcWindowLines,"Seg","DOUBLE")

    with arcpy.da.InsertCursor(fcSeedPoints,["RouteID","SeedID","SHAPE@XY"]) as icSeedPoints:
        for row in listSeeds:
            icSeedPoints.insertRow(row)

    with arcpy.da.InsertCursor(fcWindowEndPoints,["RouteID","SeedID","Seg","SHAPE@XY"]) as icWindowEndPoints:
        for row in listWindows:
            icWindowEndPoints.insertRow(row)

    with arcpy.da.InsertCursor(fcWindowLines,["RouteID","SeedID","Seg","SHAPE@"]) as icWindowLines:
        for row in listgWindows:
            icWindowLines.insertRow(row)

    fcIntersected = gis_tools.newGISDataset(tempWorkspace,"GNAT_MWA_IntersectWindowAttributes")
    arcpy.Intersect_analysis([fcWindowLines,fcLineNetwork],fcIntersected,"ALL",output_type="LINE")

    # Confinement
    tblSummaryStatisticsConfinement = gis_tools.newGISDataset(tempWorkspace,"GNAT_MWA_SummaryStatsTableConfinement")
    arcpy.Statistics_analysis(fcIntersected, tblSummaryStatisticsConfinement,"Shape_Length SUM", fieldStreamRouteID + ";SeedID;Seg;" + fieldConfinement)

    tblSummaryStatisticsPivot = gis_tools.newGISDataset(tempWorkspace,"GNAT_MWA_SummaryStatisticsPivotTable")
    arcpy.PivotTable_management(tblSummaryStatisticsConfinement,"Route;SeedID;Seg", fieldConfinement, "SUM_Shape_Length", tblSummaryStatisticsPivot)

    fieldConfinementValue = gis_tools.resetField(tblSummaryStatisticsPivot,"CONF_Value","DOUBLE")

    if len(arcpy.ListFields(tblSummaryStatisticsPivot,fieldConfinement + "1")) == 0 :
        arcpy.AddField_management(tblSummaryStatisticsPivot,fieldConfinement + "1","DOUBLE")
    if len(arcpy.ListFields(tblSummaryStatisticsPivot,fieldConfinement + "0")) == 0 :
        arcpy.AddField_management(tblSummaryStatisticsPivot,fieldConfinement + "0","DOUBLE")

    arcpy.CalculateField_management(tblSummaryStatisticsPivot,fieldConfinementValue,"!" + fieldConfinement + "1!/(!" + fieldConfinement + "0! + !" + fieldConfinement + "1!)", "PYTHON")

    #Pivot Confinement on Segment Size
    tblSummaryStatisticsWindowPivot = gis_tools.newGISDataset(tempWorkspace,"GNAT_MWA_SummaryStatisticsWindowPivotTable")
    arcpy.PivotTable_management(tblSummaryStatisticsPivot,fieldStreamRouteID + ";SeedID","Seg",fieldConfinementValue,tblSummaryStatisticsWindowPivot)

    # Constriction

    tblSummaryStatisticsConstriction = gis_tools.newGISDataset(tempWorkspace, "GNAT_MWA_SummaryStatsTableConstriction")
    arcpy.Statistics_analysis(fcIntersected, tblSummaryStatisticsConstriction, "Shape_Length SUM",
                              fieldStreamRouteID + ";SeedID;Seg;" + fieldConstriction)

    tblSummaryStatisticsPivotConstriction = gis_tools.newGISDataset(tempWorkspace, "GNAT_MWA_SummaryStatisticsPivotTableConsriction")
    arcpy.PivotTable_management(tblSummaryStatisticsConstriction, "Route;SeedID;Seg", fieldConstriction,
                                "SUM_Shape_Length", tblSummaryStatisticsPivotConstriction)

    fieldConstrictionValue = gis_tools.resetField(tblSummaryStatisticsPivotConstriction, "CNST_Value", "DOUBLE")
    if len(arcpy.ListFields(tblSummaryStatisticsConstriction,fieldConstriction + "1")) == 0 :
        arcpy.AddField_management(tblSummaryStatisticsConstriction,fieldConstriction + "1","DOUBLE")
    if len(arcpy.ListFields(tblSummaryStatisticsConstriction,fieldConstriction + "0")) == 0 :
        arcpy.AddField_management(tblSummaryStatisticsConstriction,fieldConstriction + "0","DOUBLE")

    arcpy.CalculateField_management(tblSummaryStatisticsPivotConstriction, fieldConstrictionValue,
                                    "!" + fieldConstriction + "1!/(!" + fieldConstriction + "0! + !" + fieldConstriction + "1!)",
                                    "PYTHON")
    tblSummaryStatisticsWindowPivotConstriction = gis_tools.newGISDataset(tempWorkspace,"GNAT_MWA_SummaryStatisticsWindowPivotTableConstriction")
    arcpy.PivotTable_management(tblSummaryStatisticsPivotConstriction,fieldStreamRouteID + ";SeedID","Seg",fieldConstrictionValue,tblSummaryStatisticsWindowPivotConstriction)

    strWindowSizeFields = ""
    for WindowSize in liststrWindowSize:
        strWindowSizeFields = strWindowSizeFields + ";Seg" + WindowSize
    strWindowSizeFields = strWindowSizeFields.lstrip(";")

    #Join Above table to seed points
    arcpy.JoinField_management(fcSeedPoints,"SeedID",tblSummaryStatisticsWindowPivot,"SeedID",strWindowSizeFields)
    arcpy.JoinField_management(fcSeedPoints,"SeedID",tblSummaryStatisticsWindowPivotConstriction,"SeedID",strWindowSizeFields)

    # Manage Outputs
    fcOutputSeedPoints = gis_tools.newGISDataset(outputWorkspace,"MovingWindowSeedPoints")
    arcpy.CopyFeatures_management(fcSeedPoints,fcOutputSeedPoints)

    fcOutputWindows = gis_tools.newGISDataset(outputWorkspace,"MovingWindowSegments")
    arcpy.CopyFeatures_management(fcWindowLines,fcOutputWindows)

    return

if __name__ == "__main__":

    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4],
        sys.argv[5],
        sys.argv[6],
        sys.argv[7],
        sys.argv[8])