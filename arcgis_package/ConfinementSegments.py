


import arcpy
import gis_tools
#import

def custom_segments(fcInputNetwork,
                    fieldSegmentID,
                    fieldConfinement,
                    fieldConstriction,
                    outputWorkspace,
                    tempWorkspace=arcpy.env.scratchWorkspace):
    """

    :param fcInputNetwork:
    :param fieldSegmentID:
    :param fieldConfinement:
    :param fieldConstriction:
    :param outputWorkspace:
    :param tempWorkspace:
    :return: Output Network: str
    """

    # Copy Network to Temp Workspace
    fcNetwork = gis_tools.newGISDataset(tempWorkspace,"StreamNetwork")
    arcpy.CopyFeatures_management(fcInputNetwork,fcNetwork)

    # Calculate Segment Lengths
    fieldSegLength = gis_tools.resetField(fcNetwork,"SegLen","DOUBLE")
    arcpy.CalculateField_management(fcNetwork,fieldSegLength,"!shape.length!","PYTHON")

    #Sum Segment Lengths
    tblStatsConfinementLength = gis_tools.newGISDataset(tempWorkspace,"TableStatisticsConfinementLength")
    tblStatsConstrictionLength = gis_tools.newGISDataset(tempWorkspace,"TableStatisticsConstrictionLength")
    arcpy.Statistics_analysis(fcNetwork, tblStatsConfinementLength, [[fieldSegLength,"SUM"]], [fieldSegmentID,fieldConfinement])
    arcpy.Statistics_analysis(fcNetwork, tblStatsConstrictionLength, [[fieldSegLength,"SUM"]], [fieldSegmentID,fieldConstriction])

    # Pivot on Confinement/Constriction
    tblPivotConfinement = gis_tools.newGISDataset(tempWorkspace,"PivotTableConfinement")
    tblPivotConstriction = gis_tools.newGISDataset(tempWorkspace,"PivotTableConstriction")
    arcpy.PivotTable_management(tblStatsConfinementLength,fieldSegmentID,fieldConfinement,"SUM_" + fieldSegLength,tblPivotConfinement)
    arcpy.PivotTable_management(tblStatsConstrictionLength,fieldSegmentID,fieldConstriction,"SUM_" + fieldSegLength,tblPivotConstriction)

    # Make Sure required fields exist for calculations:
    if len(arcpy.ListFields(tblPivotConstriction,fieldConstriction + "1")) == 0 :
        arcpy.AddField_management(tblPivotConstriction,fieldConstriction + "1","DOUBLE")
    if len(arcpy.ListFields(tblPivotConstriction,fieldConstriction + "0")) == 0 :
        arcpy.AddField_management(tblPivotConstriction,fieldConstriction + "0","DOUBLE")

    if len(arcpy.ListFields(tblPivotConfinement,fieldConfinement + "1")) == 0 :
        arcpy.AddField_management(tblPivotConfinement,fieldConfinement + "1","DOUBLE")
    if len(arcpy.ListFields(tblPivotConfinement,fieldConfinement + "0")) == 0 :
        arcpy.AddField_management(tblPivotConfinement,fieldConfinement + "0","DOUBLE")

    # Calculate Confinement/Constriction
    fieldConfinementValue = gis_tools.resetField(tblPivotConfinement,"CONF_Value","DOUBLE")
    arcpy.CalculateField_management(tblPivotConfinement,
                                    fieldConfinementValue,
                                    "!" + fieldConfinement + "1!/(!" + fieldConfinement + "0! + !" + fieldConfinement + "1!)",
                                    "PYTHON")

    fieldConstrictionValue = gis_tools.resetField(tblPivotConstriction,"CNST_Value","DOUBLE")
    arcpy.CalculateField_management(tblPivotConstriction,
                                    fieldConstrictionValue,
                                    "!" + fieldConstriction + "1!/(!" + fieldConstriction + "0! + !" + fieldConstriction + "1!)",
                                    "PYTHON")

    # Join Results to Network
    arcpy.JoinField_management(fcNetwork,fieldSegmentID,tblPivotConfinement,fieldSegmentID,fieldConfinementValue)
    arcpy.JoinField_management(fcNetwork,fieldSegmentID,tblPivotConstriction,fieldSegmentID,fieldConstrictionValue)

    # Copy Final Output
    outNetwork = gis_tools.newGISDataset(outputWorkspace,"ConfinementSegments.shp")
    arcpy.CopyFeatures_management(fcNetwork,outNetwork)

    return outNetwork


def fixed_segments():
    """

    :return:
    """


    return




if __name__ == "__main__":

    # TODO Set up ArgParse Here

    custom_segments()