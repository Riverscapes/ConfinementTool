'''
Name:        Stream and Valley Confinement Toolbox
Purpose:     Tools for and calculating confinement on a stream
             network or using a moving window along the stream network

Authors:     Kelly Whitehead (kelly@southforkresearch.org)
             South Fork Research, Inc
             Seattle, Washington

Created:     2015-Jan-08
Version:     2.2.03
Released:    2017 AUG 01
Updated:     23/8/2018 - DDH - Removed redundant imports to Riverscapes module
                         DDH - Set parameter type to GPFeatureLayer so the function testLayerSelection() would actually do it's job.
                         DDH - Updated version number to .04
License:     Free to use.
'''
# !/usr/bin/env python

# # Import Modules # #
from os import path, makedirs
import arcpy
from arcgis_package import ConfiningMargins, MovingWindow, ConfinementSegments
from Riverscapes import Riverscapes

# Version numbers
ConfinementToolReleaseVersion = "2.2.04"
ConfinementProjectVersion = "2.3"

path_lyr = path.join(path.dirname(path.realpath(__file__)),"lyr")

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Confinement Toolbox"
        self.alias = 'ConfinementTB'
        #self.description = "Tools for generating Valley Confinement."

        # List of tool classes associated with this toolbox
        # Not all tool classes are exposed
        self.tools = [MovingWindowConfinementTool,SegmentedNetworkConfinementTool,ConfiningMarginTool,ConfinementProjectTool,LoadInputsTool]

#
# Tools
#
class ConfinementProjectTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create a New Confinement Project"
        self.description = "Start a new Confinment Project. Tool Documentation: https://bitbucket.org/KellyWhitehead/geomorphic-network-and-analysis-toolbox/wiki/Tool_Documentation/MovingWindow"
        self.canRunInBackground = False
        self.category = "Confinement Project Management"

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Project Name",
            name="projectName",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Project Folder",
            name="projectFolder",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ["File System"]

        paramBoolNewFolder = arcpy.Parameter(
            displayName="Create New Project Folder?",
            name="boolNewFolder",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="User Name (Operator)",
            name="metaOperator",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Region",
            name="metaRegion",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        param3.filter.list = ["CRB"]

        param4 = arcpy.Parameter(
            displayName="Watershed (HUC 8 Name)",
            name="metaWatershed",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        #TODO  add param4.filter.list = [], load and read from program.xml

        params = [param0, param1, paramBoolNewFolder, param2, param3, param4]
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
        """
            Description:
                The source code of the tool.
            Updates:
                15/8/18 - DDH - Useful messages added to inform user and help with debugging.
                23/8/18 - DDH - Added error trapping.
        """

        try:
            projectFolder = p[1].valueAsText

            if p[2].valueAsText == "true":
                projectFolder = path.join(p[1].valueAsText,p[0].valueAsText)
                makedirs(projectFolder)
                arcpy.AddMessage("Project folder created.")

            # Create Project file
            newConfinementProject = Riverscapes.Project()
            newConfinementProject.create(p[0].valueAsText, "Confinement", projectPath=projectFolder)
            newConfinementProject.addProjectMetadata("Operator",p[3].valueAsText)
            newConfinementProject.addProjectMetadata("Region",p[4].valueAsText)
            newConfinementProject.addProjectMetadata("Watershed",p[5].valueAsText)
            newConfinementProject.addProjectMetadata("ConfinementProjectVersion", ConfinementProjectVersion)
            newConfinementProject.addProjectMetadata("ConfinementToolRelease", ConfinementToolReleaseVersion)
            newConfinementProject.writeProjectXML()
            arcpy.AddMessage("Project file " + newConfinementProject.xmlname + " created.")
            return
        except Exception as e:
            arcpy.AddError("Error in Execute function: " + str(e))

class LoadInputsTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Load Input Datasets"
        self.description = "Load Input Datasets to a Confinement Project. "
        self.canRunInBackground = False
        self.category = "Confinement Project Management"

    def getParameterInfo(self):
        ''' Description:
                Define parameter definitions

            Modified:
                28/8/18 - DDH - Added 4th parameter and removed code making p1-p3 optional.

        '''

        p1 = paramStreamNetwork
        p2 = paramChannelPolygon
        p3 = paramValleyBottom

        # Create an option buffer Parameter, the default will be zero metres, if the user changes
        # this then the channel polygon will be buffered during the export to shapefile
        p4 = arcpy.Parameter(name="paramBufferDistance",displayName="Buffer Channel Polygon (m)",direction="Input",datatype="GPLong",parameterType="Optional",enabled=True,multiValue=False)
        p4.value = 0

        params = [paramProjectXML,p1,p2,p3,p4]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, p):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        '''
            Description:
                Modify the messages created by internal validation for each tool
                parameter.  This method is called after internal validation.

            Modified:
                28/8/18 - DDH - Check on sensible 4th parameter value, must be zero or greater.
        '''

        p = parameters[4]
        if p.value < 0:
            p.setErrorMessage("Negatives buffer distances are invalid, must be zero or greater!")
        else:
            p.clearMessage()
        return

    def execute(self, p, messages):
        """
            Description:
                The source code of the tool.

            Updates:
                23/8/18 - DDH - Error trapping and useful messages added to inform user and help with debugging.
                23/8/18 - DDH - Removed redundant import from module os
                28/8/18 - DDH - Added new code that will buffer the channel polygon as it stores it in the project
                                sub-folder, but only if buffer distance is greater than zero.
        """

        try:

            # Get a handle on project file (project.rs.xml)
            newConfinementProject = Riverscapes.Project(p[0].valueAsText)
            pathProject = arcpy.Describe(p[0].valueAsText).path

            # Create Project Paths if they do not exist
            pathInputs = pathProject + "\\Inputs"
            if not arcpy.Exists(pathInputs):
                makedirs(pathInputs)
                arcpy.AddMessage("Inputs Subfolder created.")


            # KMW - The following is a lot of repeated code for each input. It contains file and folder creation and copying, rather than using the project module to do this. This could be streamlined in the future, but
            # is working at the moment.
            if p[1].valueAsText: # Stream Network Input
                pathStreamNetworks = pathInputs + "\\StreamNetworks"
                nameStreamNetwork = arcpy.Describe(p[1].valueAsText).basename
                if not arcpy.Exists(pathStreamNetworks):
                    makedirs(pathStreamNetworks)
                    arcpy.AddMessage("StreamNetworks Subfolder created.")

                # Create stream network input sub folder
                id_streamnetwork = Riverscapes.get_input_id(pathStreamNetworks, "StreamNetwork")
                pathStreamNetworkID = path.join(pathStreamNetworks, id_streamnetwork)
                makedirs(pathStreamNetworkID)
                arcpy.AddMessage("Subfolder " + id_streamnetwork + " created.")

                # Copy dataset to shapefile in input subfolder
                arcpy.AddMessage("Copying stream network into its input folder...")
                arcpy.FeatureClassToFeatureClass_conversion(p[1].valueAsText, pathStreamNetworkID, nameStreamNetwork)
                newConfinementProject.addInputDataset(nameStreamNetwork,id_streamnetwork,path.join(path.relpath(pathStreamNetworkID, pathProject),nameStreamNetwork) + ".shp",p[1].valueAsText)

            if p[2].valueAsText: # Channel Polygon
                buffDist = p[4].value # This will be a long of 0 or greater

                pathChannelPolygons = pathInputs + "\\ChannelPolygons"
                nameChannelPolygon = arcpy.Describe(p[2].valueAsText).basename
                if not arcpy.Exists(pathChannelPolygons):
                    makedirs(pathChannelPolygons)
                    arcpy.AddMessage("ChannelPolygons Subfolder created.")

                # Create channel polygon input sub folder
                id_channelpolygon = Riverscapes.get_input_id(pathChannelPolygons, "ChannelPolygon")
                pathChannelPolygonID = path.join(pathChannelPolygons,id_channelpolygon)
                makedirs(pathChannelPolygonID)
                arcpy.AddMessage("Subfolder " + id_channelpolygon + " created.")

                if buffDist == 0:
                    # Copy dataset to shapefile in input subfolder
                    arcpy.AddMessage("Copying channel polygon into its input folder...")
                    arcpy.FeatureClassToFeatureClass_conversion(p[2].valueAsText, pathChannelPolygonID, nameChannelPolygon)
                else:
                    # Create a buffered version of channel dataset
                    arcpy.AddMessage("Buffering channel polygon into its input folder...")
                    outFC = path.join(pathChannelPolygonID, nameChannelPolygon)+ ".shp"
                    dist = str(buffDist) + " METERS"
                    arcpy.Buffer_analysis(p[2].valueAsText,outFC,dist,"FULL","ROUND","NONE","#","PLANAR")

                newConfinementProject.addInputDataset(nameChannelPolygon,id_channelpolygon,path.join(path.relpath(pathChannelPolygonID, pathProject),nameChannelPolygon) + ".shp",p[2].valueAsText)

            if p[3].valueAsText: # Valley  Bottom
                pathValleyBottoms = pathInputs + "\\ValleyBottoms"
                nameValleyBottom = arcpy.Describe(p[3].valueAsText).basename
                if not arcpy.Exists(pathValleyBottoms):
                    makedirs(pathValleyBottoms)
                    arcpy.AddMessage("ValleyBottoms Subfolder created.")

                # Create valley bottom input sub folder
                id_valleybottom = Riverscapes.get_input_id(pathValleyBottoms,"ValleyBottom")
                pathValleyBottomID = path.join(pathValleyBottoms,id_valleybottom)
                makedirs(pathValleyBottomID)
                arcpy.AddMessage("Subfolder " + id_valleybottom + " created.")

                # Copy dataset to shapefile in input subfolder
                arcpy.AddMessage("Copying valley bottoms into its input folder...")
                arcpy.FeatureClassToFeatureClass_conversion(p[3].valueAsText,pathValleyBottomID,nameValleyBottom)
                newConfinementProject.addInputDataset(nameValleyBottom,id_valleybottom,path.join(path.relpath(pathValleyBottomID,pathProject),nameValleyBottom) + ".shp",p[3].valueAsText)

            # Write new XML
            newConfinementProject.writeProjectXML(p[0].valueAsText)
            return
        except Exception as e:
            arcpy.AddError("Error in Execute function: " + str(e))

class LoadInputsFromProjectTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Load Input Datasets From Other Projects"
        self.description = "Load Input Datasets to a Confinement Project. "
        self.canRunInBackground = False
        self.category = "Confinement Project Management"

    def getParameterInfo(self):
        """Define parameter definitions"""

        p1_project = get_projectxml_param("Source GNAT Project for Stream Networks")
        p1 = arcpy.Parameter("StreamNetwork", "Stream Networks", "Input", "GPString", "Optional", multiValue=True)
        p1.filter.list = []

        p2 = paramChannelPolygon
        p2.enabled = False
        p3_project = get_projectxml_param("Source VBET Project for Valley Bottom Polygon")
        p3 = paramValleyBottom

        p3.enabled = False
        p3_project.enabled = False

        params = [paramProjectXML,p1_project,p1,p2,p3_project,p3]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, p):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        # Todo better check for type of project (GNAT only) and if exists, and if empty datasets
        if p[1].value:
            if arcpy.Exists(p[1].valueAsText):
                project_streamnetwork = Riverscapes.Project(p[1].valueAsText)
                p[2].filter.list = []
                filter_list = []
                for realizationName, realization in project_streamnetwork.Realizations.iteritems():
                    filter_list.append(realizationName + " " +
                                       realization.GNAT_StreamNetwork.name +
                                       " (" + realization.GNAT_StreamNetwork.absolutePath(project_streamnetwork.projectPath) + ") [" +
                                       realization.GNAT_StreamNetwork.guid + "]")
                p[2].filter.list = filter_list

        if p[4].value:
            if arcpy.Exists(p[4].valuAsText):

                project_vbet = Riverscapes.Project()
                project_vbet.loadProjectXML(p[1].valueAsText)
                filter_list = []
                for realizationName, realization in project_vbet.Realizations.iteritems():
                    filter_list.append(realizationName + " " + realization.GNAT_StreamNetwork.name + " (" + realization.GNAT_StreamNetwork.absolutePath(project_vbet.projectPath) + ")")
                p[4].filter.list = filter_list
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        return

    def execute(self, p, messages):
        """The source code of the tool."""

        ConfinementProject = Riverscapes.Project(p[0].valueAsText)

        # Create Project Paths if they do not exist
        pathInputs = ConfinementProject.projectPath + "\\Inputs"
        if not arcpy.Exists(pathInputs):
            makedirs(pathInputs)

        # Stream Network Input
        for value in p[2].valueAsText.split(";"):
            stream_network = value[value.find("(") + 1:value.find(")") ]
            pathStreamNetworks = pathInputs + "\\StreamNetworks"
            nameStreamNetwork = arcpy.Describe(stream_network).basename
            if not arcpy.Exists(pathStreamNetworks):
                makedirs(pathStreamNetworks)
            id_streamnetwork = Riverscapes.get_input_id(pathStreamNetworks, "StreamNetwork")
            pathStreamNetworkID = path.join(pathStreamNetworks, id_streamnetwork)
            makedirs(pathStreamNetworkID)
            arcpy.FeatureClassToFeatureClass_conversion(stream_network, pathStreamNetworkID, nameStreamNetwork)
            #ConfinementProject.addInputDataset(nameStreamNetwork,
                                                  # id_streamnetwork,
                                                  # path.join(path.relpath(pathStreamNetworkID,
                                                  #                        ConfinementProject.projectPath),
                                                  #           nameStreamNetwork) + ".shp",
                                                  # p[1].valueAsText)
            dataset = Riverscapes.Dataset()
            dataset.create(nameStreamNetwork,
                           path.join(path.relpath(pathStreamNetworkID,ConfinementProject.projectPath)),
                           "StreamNetwork",
                           stream_network)
            dataset.guid = value[value.find("[") + 1:value.find("]") - 1]
            ConfinementProject.InputDatasets[id_streamnetwork] = dataset

        # if p[2].valueAsText:  # Channel Polygon
        #     pathChannelPolygons = pathInputs + "\\ChannelPolygons"
        #     nameChannelPolygon = arcpy.Describe(p[2].valueAsText).basename
        #     if not arcpy.Exists(pathChannelPolygons):
        #         makedirs(pathChannelPolygons)
        #     id_channelpolygon = Riverscapes.get_input_id(pathChannelPolygons, "ChannelPolygon")
        #     pathChannelPolygonID = path.join(pathChannelPolygons, id_channelpolygon)
        #     makedirs(pathChannelPolygonID)
        #     arcpy.FeatureClassToFeatureClass_conversion(p[2].valueAsText, pathChannelPolygonID, nameChannelPolygon)
        #     newConfinementProject.addInputDataset(nameChannelPolygon,
        #                                           id_channelpolygon,
        #                                           path.join(path.relpath(pathChannelPolygonID, pathProject),
        #                                                     nameChannelPolygon) + ".shp",
        #                                           p[2].valueAsText)

        if p[3].valueAsText:  # Valley  Bottom
            pathValleyBottoms = pathInputs + "\\ValleyBottoms"
            nameValleyBottom = arcpy.Describe(p[3].valueAsText).basename
            if not arcpy.Exists(pathValleyBottoms):
                makedirs(pathValleyBottoms)
            id_valleybottom = Riverscapes.get_input_id(pathValleyBottoms, "ValleyBottom")
            pathValleyBottomID = path.join(pathValleyBottoms, id_valleybottom)
            makedirs(pathValleyBottomID)
            arcpy.FeatureClassToFeatureClass_conversion(p[3].valueAsText, pathValleyBottomID, nameValleyBottom)
            ConfinementProject.addInputDataset(nameValleyBottom,
                                               id_valleybottom,
                                               path.join(path.relpath(pathValleyBottomID, ConfinementProject.projectPath),
                                                            nameValleyBottom) + ".shp",
                                               p[3].valueAsText)

        # Write new XML
        ConfinementProject.writeProjectXML(p[0].valueAsText)

        return


###### Realizations ######

class ConfiningMarginTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Confining Margins Tool"
        self.description = "Determine the Confining Margins using the Stream Network, Channel Buffer Polygon, and Valley Bottom Polygon."
        self.canRunInBackground = "False"
        self.Category = 'Confinement Tools'

    def getParameterInfo(self):
        '''
            Description:
                Define parameter definitions

            Updates: 5/9/18 - DDH - Added Filter by Length Parameter
        '''

        # 0
        # paramProjectXML
        #paramProjectXML.filter.list = ["xml"]

        # 1 - Required as it sets the output names to their default names. If this parameter was not set then the output controls disable and don't allow you
        # to enter a shapefile dataset name!
        paramRealizationName = arcpy.Parameter(displayName="Confinement Realization Name", name="realizationName", datatype="GPString", parameterType="Required", direction="Input")

        # 2
        paramStreamNetwork = arcpy.Parameter(displayName="Input Stream Network", name="InputFCStreamNetwork", datatype="GPFeatureLayer", parameterType="Required", direction="Input")
        paramStreamNetwork.filter.list = ["Polyline"]

        paramValleyBottom = arcpy.Parameter(displayName="Input Valley Bottom Polygon", name="InputValleyBottomPolygon", datatype="GPFeatureLayer", parameterType="Required", direction="Input")
        paramValleyBottom.filter.list = ["Polygon"]

        paramChannelPolygon = arcpy.Parameter(displayName="Input Active Channel Polygon (Buffered Bankfull)", name="InputBankfullChannelPoly", datatype="GPFeatureLayer", parameterType="Required", direction="Input")
        paramChannelPolygon.filter.list = ["Polygon"]

        paramOutputRawConfiningState = arcpy.Parameter(displayName="Output Raw Confining State", name="outputRawConfiningState", datatype="DEFeatureClass", parameterType="Optional", direction="Output",)
        paramOutputRawConfiningState.symbology = path.join(path_lyr,"") + "Raw_Confining_State.lyr"

        paramOutputConfiningMargins = arcpy.Parameter(displayName="Output Confining Margins", name="fcOutputConfiningMargins", datatype="DEFeatureClass", parameterType="Optional", direction="Output")
        paramOutputConfiningMargins.symbology = path.join(path_lyr,"") + "Confining_Margins.lyr"

        paramFilterByLength = arcpy.Parameter(name="FilterByLength",displayName="Filter by Length (m)",direction="Input",datatype="GPDouble",parameterType="Required")
        paramFilterByLength.value = 5 # Default value of 5m

        # Note: Parameters common to all tools are defined from lines at end of code.
        return [paramProjectXML,paramRealizationName,paramStreamNetwork,paramValleyBottom,paramChannelPolygon,paramFilterByLength,paramOutputRawConfiningState,paramOutputConfiningMargins,paramTempWorkspace]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, p):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        if p[0].altered:
            if p[0].value and arcpy.Exists(p[0].valueAsText):
                # Set Project Mode

                p[6].enabled = "False"
                p[7].enabled = "False"
                p[6].parameterType = "Optional"
                p[7].parameterType = "Optional"

                currentProject = Riverscapes.Project(p[0].valueAsText)

                # This section of code fails so has been commented out. It is trying to load a list of string values which are featureclass paths into
                # a control that is expecting a FEATURECLASS with the filter set to a specific geometry type.
                # We could make the control a GPString then this logic would work but then it messes up the LoadsInputTool. This problem stems
                # from the odd behaviour of creating generic parameters at the end of the code.
                #
                # DDH - 15/8/18

##                listInputDatasets = []
##                for name,inputDataset in currentProject.InputDatasets.iteritems():
##                    listInputDatasets.append(inputDataset.absolutePath(currentProject.projectPath))
##                p[2].filter.list = listInputDatasets
##                p[3].filter.list = listInputDatasets
##                p[4].filter.list = listInputDatasets

                if p[1].altered:
                    if p[1].valueAsText:
                        realization_id = currentProject.get_next_realization_id()
                        p[6].value = path.join(currentProject.projectPath, "Outputs", realization_id) + "\\RawConfiningState.shp"
                        p[7].value = path.join(currentProject.projectPath, "Outputs", realization_id) + "\\ConfiningMargins.shp"

            else:
                p[6].enabled = "True"
                p[7].enabled = "True"
                p[6].parameterType = "Required"
                p[7].parameterType = "Optional"



        return

    def updateMessages(self, parameters):
        '''
            Description:
                Modify the messages created by internal validation for each tool
                parameter.  This method is called after internal validation.

            Updates: 5/9/18 - DDH - Added error check for filter by length parameter and updated parameter indices
        '''

        if parameters[0].valueAsText:
            newConfinementProject = Riverscapes.Project(parameters[0].valueAsText)

            for realization in newConfinementProject.Realizations:
                if realization == parameters[1].valueAsText:
                    parameters[1].setErrorMessage("Realization " + parameters[1].valueAsText + " already exists.")
                    return

        # Check if filter value is negative
        if parameters[5].value < 0:
            parameters[5].setErrorMessage("Negative filter lengths are invalid, must be zero or greater")
        else:
            parameters[5].clearMessage()

        # Run a bunch a quality control tests on inputs and set any appropriate warnings
        testProjected(parameters[2])
        testProjected(parameters[3])
        testProjected(parameters[4])
        testMValues(parameters[2])
        testMValues(parameters[3])
        testMValues(parameters[4])
        testLayerSelection(parameters[2])
        testLayerSelection(parameters[3])
        testLayerSelection(parameters[4])
        testWorkspacePath(parameters[8])
        return

    def execute(self, p, messages):
        '''
            Description:
                The source code of the tool.

            Updates: 5/9/18 - DDH - Indices changed due to new filter by length parameter
        '''
        reload(ConfiningMargins)


        # if in project mode, create workspaces as needed.
        if p[0].valueAsText:
            newConfinementProject = Riverscapes.Project(p[0].valueAsText)
            if p[1].valueAsText:
                realization_id = newConfinementProject.get_next_realization_id()
                makedirs(path.join(newConfinementProject.projectPath, "Outputs", realization_id))

        bOK = ConfiningMargins.main(p[2].valueAsText,p[3].valueAsText,p[4].valueAsText,p[5].value,p[6].valueAsText,p[7].valueAsText,getTempWorkspace(p[8].valueAsText),False) # If Not specified, in memory is used

        if bOK:
            # on success, rewrite xml file if in project mode
            if p[0].valueAsText:
                arcpy.AddMessage("... Updating project file")
                newConfinementProject = Riverscapes.Project() # ConfinementProject.ConfinementProject()
                newConfinementProject.loadProjectXML(p[0].valueAsText)

                idStreamNetwork = newConfinementProject.get_dataset_id(p[2].valueAsText)
                idValleyBottom = newConfinementProject.get_dataset_id(p[3].valueAsText)
                idChannelPolygon = newConfinementProject.get_dataset_id(p[4].valueAsText)
                # DDH - This line was causing tool to fail, after trying to follow logic I think this code was attempting retrieve a realization ID before it ever existed
                # So I Commented it out and replaced it with the below line, this seems to be work, original code was newConfinementProject.Realizations[p[1].valueAsText].id
                idRealization = realization_id

                outputRawConfiningState = Riverscapes.Dataset()
                outputRawConfiningState.create(arcpy.Describe(p[6].valueAsText).basename,
                                               path.join("Outputs", idRealization, "RawConfiningState" ) + ".shp")

                outputConfiningMargins = Riverscapes.Dataset()
                outputConfiningMargins.create(arcpy.Describe(p[7].valueAsText).basename,
                                              path.join("Outputs", idRealization, "ConfiningMargins") + ".shp")

                newRealization = Riverscapes.ConfinementRealization()
                newRealization.createConfinementRealization(p[1].valueAsText,
                                      idStreamNetwork,
                                      idValleyBottom,
                                      idChannelPolygon,
                                      outputConfiningMargins,
                                      outputRawConfiningState)

                newRealization.productVersion = ConfinementToolReleaseVersion

                newConfinementProject.addRealization(newRealization)
                newConfinementProject.writeProjectXML()
        else:
            arcpy.AddError("Main processing algorithm failed, project file not updated!")

        return

class ConfiningMarginTool2(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Confining Margins Tool (Linked Projects)"
        self.description = "Determine the Confining Margins using the Stream Network, Channel Buffer Polygon, and Valley Bottom Polygon."
        self.canRunInBackground = "False"
        self.Category = 'Confinement Tools'

    def getParameterInfo(self):
        """Define parameter definitions"""

        paramConfinementProjectXML = get_projectxml_param("Confinement Project rs.xml file")

        paramRealizationName = arcpy.Parameter(
            displayName="Confinement Realization Name",
            name="realizationName",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        paramOutputRawConfiningState = arcpy.Parameter(
            displayName="Output Raw Confining State",
            name="outputRawConfiningState",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Output")

        paramOutputConfiningMargins = arcpy.Parameter(
            displayName="Output Confining Margins",
            name="fcOutputConfiningMargins",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Output")

        paramGNATProjectXML = get_projectxml_param("Source Project of Stream Network Layers (GNAT)","Link Inputs from Projects")

        paramGNATLayerFinder = arcpy.Parameter(
            displayName="Available Stream Networks",
            name="strStreamNetwork",
            datatype="GPString",
            parameterType="Optional",
            direction="Input",
        category="Link Inputs from Projects")

        paramActiveChannelProject = get_projectxml_param("Source Project of Active Channel Polygons", "Link Inputs from Projects")

        paramACPLayerFinder = arcpy.Parameter(
            displayName="Available Active Channel Polygons",
            name="strChannelPolygon",
            datatype="GPString",
            parameterType="Optional",
            direction="Input",
            category="Link Inputs from Projects")

        paramVBETProjectXML = get_projectxml_param("Source Project of Valley Bottom Polygons (VBET)","Link Inputs from Projects")

        paramVBETLayerFinder = arcpy.Parameter(
            displayName="Available VBET Polygons",
            name="strVBET",
            datatype="GPString",
            parameterType="Optional",
            direction="Input",
            category="Link Inputs from Projects")

        paramActiveChannelProject.enabled = "False"
        paramACPLayerFinder.enabled = "False"

        return [paramProjectXML,                #0
                paramRealizationName,           #1
                paramStreamNetwork,             #2
                paramChannelPolygon,            #3
                paramValleyBottom,              #4
                paramOutputRawConfiningState,   #5
                paramOutputConfiningMargins,    #6
                paramTempWorkspace,             #7
                paramGNATProjectXML,            #8
                paramGNATLayerFinder,           #9
                paramActiveChannelProject,      #10
                paramACPLayerFinder,            #11
                paramVBETProjectXML,            #12
                paramVBETLayerFinder]           #13

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, p):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        if p[0].altered:
            if p[0].value and arcpy.Exists(p[0].valueAsText):
                # Set Project Mode
                p[5].enabled = "False"
                p[6].enabled = "False"
                p[5].parameterType = "Optional"
                p[6].parameterType = "Optional"
                currentProject = Riverscapes.Project(p[0].valueAsText)
                # listInputDatasets = []
                # for name, inputDataset in currentProject.InputDatasets.iteritems():
                #     listInputDatasets.append(inputDataset.absolutePath(currentProject.projectPath))
                # p[2].filter.list = listInputDatasets
                # p[3].filter.list = listInputDatasets
                # p[4].filter.list = listInputDatasets
                if p[1].altered:
                    if p[1].value:
                        p[5].value = path.join(currentProject.projectPath, "Outputs",
                                               p[1].valueAsText) + "\\RawConfiningState.shp"
                        p[6].value = path.join(currentProject.projectPath, "Outputs",
                                               p[1].valueAsText) + "\\ConfiningMargins.shp"
                        # TODO manage output folder if project mode
            else:
                p[5].enabled = "True"
                p[6].enabled = "True"
                p[5].parameterType = "Required"
                p[6].parameterType = "Optional"

        if p[8].altered:
            if p[8].value:
                if arcpy.Exists(p[8].valueAsText):
                    p[9].enabled = "True"
                    p[9].filter.list = []
                    GNATproject = Riverscapes.Project(p[8].valueAsText)
                    listGNATpaths = []
                    for realizationName, realization in GNATproject.Realizations.iteritems():
                        listGNATpaths.append(realizationName + " " + realization.GNAT_StreamNetwork.name +
                                           " (" + realization.GNAT_StreamNetwork.absolutePath(GNATproject.projectPath) +
                                           ") [" + realization.GNAT_StreamNetwork.guid + "]")
                        for analysisName, analysis in realization.analyses.iteritems():
                            for dataset in analysis.outputDatasets.values():
                                listGNATpaths.append(realizationName + " " + analysisName + " (" +
                                                     dataset.absolutePath(GNATproject.projectPath) + ") [" +
                                                     dataset.guid + "]")
                    p[9].filter.list = listGNATpaths
                else:
                    p[9].enabled = "False"
            else:
                p[9].enabled = "False"

        if p[9].altered:
            if p[9].value:
                p[2].value = p[9].value[p[9].value.find("(") + 1:p[9].value.find(")") ]
                p[9].enabled = "False"

        if p[12].altered:
            if p[12].value:
                if arcpy.Exists(p[12].valueAsText):
                    p[13].enabled = "True"
                    p[13].filter.list = []
                    VBETproject = Riverscapes.Project(p[12].valueAsText)
                    listVBETpaths = []
                    for realizationName, realization in VBETproject.Realizations.iteritems():
                        # listVBETpaths.append(realizationName + " " + realization.GNAT_StreamNetwork.name +
                        #                      " (" + realization.  .absolutePath(
                        #     VBETproject.projectPath) +
                        #                      ") [" + realization..guid + "]")
                        for analysisName, analysis in realization.analyses.iteritems():
                            for dataset in analysis.outputDatasets.values():
                                strGUID = ""
                                if dataset.guid:
                                    strGUID = " [" + dataset.guid + "]"
                                listVBETpaths.append(realizationName + " " + analysisName + " (" +
                                                     dataset.absolutePath(VBETproject.projectPath) + ")" + strGUID)
                    p[13].filter.list = listVBETpaths
                else:
                    p[13].enabled = "False"
            else:
                p[13].enabled = "False"

        if p[13].altered:
            if p[13].value:
                p[4].value = p[13].value[p[13].value.find("(") + 1:p[13].value.find(")")]
                p[13].enabled = "False"

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        if parameters[0].valueAsText:
            newConfinementProject = Riverscapes.Project(parameters[0].valueAsText)

            for realization in newConfinementProject.Realizations:
                if realization == parameters[1].valueAsText:
                    parameters[1].setErrorMessage("Realization " + parameters[1].valueAsText + " already exists.")
                    return

        testProjected(parameters[2])
        testProjected(parameters[3])
        testProjected(parameters[4])
        testMValues(parameters[2])
        testMValues(parameters[3])
        testMValues(parameters[4])
        testLayerSelection(parameters[2])
        testLayerSelection(parameters[3])
        testLayerSelection(parameters[4])
        testWorkspacePath(parameters[7])
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(ConfiningMargins)

        # if in project mode, create workspaces as needed.
        if p[0].valueAsText:
            newConfinementProject = Riverscapes.Project(p[0].valueAsText)  # ConfinementProject.ConfinementProject()
            if p[1].valueAsText:
                makedirs(path.join(newConfinementProject.projectPath, "Outputs", p[1].valueAsText))

            # Create Project Paths if they do not exist
            pathInputs = newConfinementProject.projectPath + "\\Inputs"
            if not arcpy.Exists(pathInputs):
                makedirs(pathInputs)

            if p[2].valueAsText and not p[9].valueAsText:  # Stream Network Input
                pathStreamNetworks = pathInputs + "\\StreamNetworks"
                nameStreamNetwork = arcpy.Describe(p[2].valueAsText).basename
                if not arcpy.Exists(pathStreamNetworks):
                    makedirs(pathStreamNetworks)
                id_streamnetwork = Riverscapes.get_input_id(pathStreamNetworks, "StreamNetwork")
                pathStreamNetworkID = path.join(pathStreamNetworks, id_streamnetwork)
                makedirs(pathStreamNetworkID)
                arcpy.FeatureClassToFeatureClass_conversion(p[1].valueAsText, pathStreamNetworkID, nameStreamNetwork)
                newConfinementProject.addInputDataset(nameStreamNetwork,
                                                      id_streamnetwork,
                                                      path.join(path.relpath(pathStreamNetworkID,
                                                                             newConfinementProject.projectPath),
                                                                nameStreamNetwork) + ".shp",
                                                      p[2].valueAsText)

            if p[2].valueAsText and not p[11].valueAsText:  # Channel Polygon
                pathChannelPolygons = pathInputs + "\\ChannelPolygons"
                nameChannelPolygon = arcpy.Describe(p[2].valueAsText).basename
                if not arcpy.Exists(pathChannelPolygons):
                    makedirs(pathChannelPolygons)
                id_channelpolygon = Riverscapes.get_input_id(pathChannelPolygons, "ChannelPolygon")
                pathChannelPolygonID = path.join(pathChannelPolygons,id_channelpolygon)
                makedirs(pathChannelPolygonID)
                arcpy.FeatureClassToFeatureClass_conversion(p[2].valueAsText, pathChannelPolygonID, nameChannelPolygon)
                newConfinementProject.addInputDataset(nameChannelPolygon,
                                                      id_channelpolygon,
                                                      path.join(path.relpath(pathChannelPolygonID, newConfinementProject.projectPath),
                                                                nameChannelPolygon) + ".shp",
                                                      p[2].valueAsText)

            if p[3].valueAsText and not p[13].valueAsText:  # Valley  Bottom
                pathValleyBottoms = pathInputs + "\\ValleyBottoms"
                nameValleyBottom = arcpy.Describe(p[3].valueAsText).basename
                if not arcpy.Exists(pathValleyBottoms):
                    makedirs(pathValleyBottoms)
                id_valleybottom = Riverscapes.get_input_id(pathValleyBottoms,"ValleyBottom")
                pathValleyBottomID = path.join(pathValleyBottoms,id_valleybottom)
                makedirs(pathValleyBottomID)
                arcpy.FeatureClassToFeatureClass_conversion(p[3].valueAsText,pathValleyBottomID,nameValleyBottom)
                newConfinementProject.addInputDataset(nameValleyBottom,
                                                      id_valleybottom,
                                                      path.join(path.relpath(pathValleyBottomID,
                                                                             newConfinementProject.projectPath),
                                                                nameValleyBottom) + ".shp",
                                                      p[3].valueAsText)



        ConfiningMargins.main(p[2].valueAsText,
                              p[3].valueAsText,
                              p[4].valueAsText,
                              p[5].valueAsText,
                              p[6].valueAsText,
                              getTempWorkspace(p[7].valueAsText),
                              False)  # If Not specified, in memory is used

        # on success, rewrite xml file if in project mode
        if p[0].valueAsText:
            newConfinementProject = Riverscapes.Project()  # ConfinementProject.ConfinementProject()
            newConfinementProject.loadProjectXML(p[0].valueAsText)




            idStreamNetwork = newConfinementProject.get_dataset_id(p[2].valueAsText)
            idValleyBottom = newConfinementProject.get_dataset_id(p[3].valueAsText)
            idChannelPolygon = newConfinementProject.get_dataset_id(p[4].valueAsText)

            outputRawConfiningState = Riverscapes.Dataset()
            outputRawConfiningState.create(arcpy.Describe(p[5].valueAsText).basename,
                                           p[5].valueAsText)  # TODO make this relative path

            outputConfiningMargins = Riverscapes.Dataset()
            outputConfiningMargins.create(arcpy.Describe(p[6].valueAsText).basename, p[6].valueAsText)

            newRealization = Riverscapes.ConfinementRealization()
            newRealization.createConfinementRealization(p[1].valueAsText,
                                                        idStreamNetwork,
                                                        idValleyBottom,
                                                        idChannelPolygon,
                                                        outputConfiningMargins,
                                                        outputRawConfiningState)

            newConfinementProject.addRealization(newRealization)
            newConfinementProject.writeProjectXML(p[0].valueAsText)

        return

###### Analysis Tools ######

class MovingWindowConfinementTool(object):
        def __init__(self):
            """Define the tool (tool name is the name of the class)."""
            self.label = "Moving Window Confinement"
            self.description = "Calculate the Valley Confinement using moving windows."
            self.category = 'Confinement Tools\\Analysis'
            self.canRunInBackground = False

        def getParameterInfo(self):
            """Define parameter definitions"""

            # 0
            # paramProjectXML

            # 1
            paramRealization = arcpy.Parameter(
                displayName="Confinement Realization Name",
                name="realizationName",
                datatype="GPString",
                parameterType="Optional",
                direction="Input")
            paramRealization.enabled = "False"

            # 2
            #paramAnalysisName

            # 3
            #paramStreamNetwork

            # 4
            paramFieldDissolve = arcpy.Parameter(
                displayName="Dissolve Field (Stream Branch ID)",
                name="fieldStreamID",
                datatype="GPString",
                parameterType="Required",
                direction="Input")
            paramFieldDissolve.filter.list = []

            # 5
            paramFieldConfiningState = arcpy.Parameter(
                displayName="Confining State Field",
                name="fieldConfinement",
                datatype="GPString",
                parameterType="Required",
                direction="Input")
            paramFieldConfiningState.filter.list = []

            # 6
            paramFieldConstriction = arcpy.Parameter(
                displayName="Constriction State Field",
                name="fieldConstriction",
                datatype="GPString",
                parameterType="Required",
                direction="Input")
            paramFieldConstriction.filter.list = []

            # 7
            paramSeedPointDistance = arcpy.Parameter(
                displayName="Seed Point Distance",
                name="dblSeedPointDistance",
                datatype="GPDouble",
                parameterType="Required",
                direction="Input")
            # paramSeedPointDistance.value = 50

            # 8
            paramWindowSizes = arcpy.Parameter(
                displayName="Window Sizes",
                name="inputWindowSizes",
                datatype="GPDouble",
                parameterType="Required",
                direction="Input",
                multiValue=True)
            # paramWindowSizes.value = [50,100]

            # 9
            # Output Workspace
            paramOutputWorkspaceMW = arcpy.Parameter(
                displayName="Output Workspace",
                name="strOutputWorkspace",
                datatype="DEWorkspace",
                parameterType="Optional",
                direction="Output",
                category="Outputs")

            # 10
            # TempWorkspace

            params = [paramProjectXML,
                      paramRealization,
                      paramAnalysisName,
                      paramStreamNetwork,
                      paramFieldDissolve,
                      paramFieldConfiningState,
                      paramFieldConstriction,
                      paramSeedPointDistance,
                      paramWindowSizes,
                      paramOutputWorkspaceMW,
                      paramTempWorkspace]
            return params

        def isLicensed(self):
            """Set whether tool is licensed to execute."""
            return True

        def updateParameters(self, p):
            """Modify the values and properties of parameters before internal
            validation is performed.  This method is called whenever a parameter
            has been changed."""
##            from Riverscapes import Riverscapes

            if p[0].value:
                if arcpy.Exists(p[0].value):
                    confinementProject = Riverscapes.Project(p[0].valueAsText)
                    p[1].enabled = "True"
                    p[9].enabled = "False"
                    p[1].filter.list = confinementProject.Realizations.keys()
                    if p[1].value:
                        currentRealization = confinementProject.Realizations.get(p[1].valueAsText)
                        p[3].value = currentRealization.OutputRawConfiningState.absolutePath(confinementProject.projectPath)
                        p[3].enabled = "False"
                        if p[2].value:
                            analysis_id = "ConfiningSegments_" + str(len(currentRealization.analyses) + 1).zfill(3)
                            p[9].value = path.join(confinementProject.projectPath, "Outputs", currentRealization.id, "Analyses", analysis_id)
                else:
                    p[1].filter.list = []
                    p[1].value = ''
                    p[1].enabled = "False"
                    p[3].value = ""
                    p[3].enabled = "True"
                    p[9].value = ""
                    p[9].enabled = "True"

            #Find Fields
            populateFields(p[3], p[4], "BranchID")
            populateFields(p[3], p[5], "IsConfined")
            populateFields(p[3], p[6], "IsConstric")

            return

        def updateMessages(self, parameters):
            """Modify the messages created by internal validation for each tool
            parameter.  This method is called after internal validation."""
##            from Riverscapes import Riverscapes

            if parameters[0].value:
                if arcpy.Exists(parameters[0].value):
                    confinementProject = Riverscapes.Project(parameters[0].valueAsText)
                    if parameters[1].value:
                        currentRealization = confinementProject.Realizations.get(parameters[1].valueAsText)
                        if parameters[2].value:
                            if parameters[2].value in currentRealization.analyses.keys():
                                parameters[2].setErrorMessage(parameters[2].name + " " + parameters[2].value + " already exists for Realization " + currentRealization.name + ".")

            testProjected(parameters[4])
            testWorkspacePath(parameters[9])
            testWorkspacePath(parameters[10])
            return

        def execute(self, p, messages):
            """The source code of the tool."""
            reload(MovingWindow)
##            from Riverscapes import Riverscapes
            setEnvironmentSettings()

            # if in project mode, create workspaces as needed.
            if p[0].valueAsText:
                newConfinementProject = Riverscapes.Project(p[0].valueAsText)
                if p[1].valueAsText:
                    currentRealization = newConfinementProject.Realizations[p[1].valueAsText]
                    analysis_id = "ConfiningSegments_" + str(len(currentRealization.analyses) + 1).zfill(3)
                    makedirs(path.join(newConfinementProject.projectPath, "Outputs", newConfinementProject.Realizations[p[0].valueAsText].id, "Analyses", analysis_id))

            MovingWindow.main(p[3].valueAsText,
                              p[4].valueAsText,
                              p[5].valueAsText,
                              p[6].valueAsText,
                              p[7].valueAsText,
                              p[8].valueAsText,
                              p[9].valueAsText,
                              p[10].valueAsText)

            if p[0].valueAsText:
                outConfinementProject = Riverscapes.Project(p[0].valueAsText)
                currentRealization = outConfinementProject.Realizations.get(p[1].valueAsText)
                realization_id = currentRealization.id
                analysis_id = "ConfiningSegments_" + str(len(currentRealization.analyses) + 1).zfill(3)
                outputSeedPoints = Riverscapes.Dataset()
                outputSeedPoints.create("MovingWindowSeedPoints",path.join( "Outputs" , realization_id, "Analyses", analysis_id, "MovingWindowSeedPoints") + ".shp")

                outputWindows = Riverscapes.Dataset() #ConfinementProject.dataset()
                outputWindows.create("MovingWindowSegments", path.join("Outputs", realization_id, "Analyses", analysis_id, "MovingWindowSegments") + ".shp")

                currentRealization.newAnalysisMovingWindow(p[2].valueAsText, p[7].valueAsText, p[8].valueAsText, outputSeedPoints, outputWindows, analysis_id)
                outConfinementProject.Realizations[p[1].valueAsText] = currentRealization
                outConfinementProject.writeProjectXML()

            return

class FixedSegmentConfinementTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Fixed Segment Confinement"
        self.description = "Calculate the Valley Confinement. Tool Documentation: https://bitbucket.org/KellyWhitehead/geomorphic-network-and-analysis-toolbox/wiki/Tool_Documentation/MovingWindow"
        self.category = 'Confinement Tools\\Analysis'
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input Stream Network with Confining State",
            name="lineNetwork",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        param0.filter.list = ["Polyline"]

        param1 = arcpy.Parameter(
            displayName="Dissolve Field (Stream Branch ID)",
            name="fieldStreamID",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="Confining State Field",
            name="fieldAttribute",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Seed Point Distance",
            name="dblSeedPointDistance",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        # param3.value = 50

        param4 = arcpy.Parameter(
            displayName="Window Sizes",
            name="inputWindowSizes",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        # param4.value = [50,100]

        param5 = arcpy.Parameter(
            displayName="Output Workspace",
            name="strOutputWorkspace",
            datatype="DEWorkspace",
            parameterType="Optional",
            direction="Input",
            category="Outputs")

        param6 = arcpy.Parameter(
            displayName="Temp Workspace",
            name="strTempWorkspace",
            datatype="DEWorkspace",
            parameterType="Optional",
            direction="Input",
            category="Outputs")
        param6.value = arcpy.env.scratchWorkspace

        param5.value = str(arcpy.env.scratchWorkspace)
        params = [param0, param1, param2, param3, param4, param5, param6]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[0].value:
            if arcpy.Exists(parameters[0].value):
                # Get Fields
                fields = arcpy.Describe(parameters[0].value).fields
                listFields = []
                for f in fields:
                    listFields.append(f.name)
                parameters[1].filter.list = listFields
                if "BranchID" in listFields:
                    parameters[1].value = "BranchID"
                parameters[2].filter.list = listFields
            else:
                parameters[1].filter.list = []
                parameters[2].filter.list = []
                parameters[0].setErrorMessage(" Dataset does not exist.")
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        testProjected(parameters[0])
        testWorkspacePath(parameters[5])
        testWorkspacePath(parameters[6])
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        #reload(MovingWindow)
        setEnvironmentSettings()

        #MovingWindow.main(p[0].valueAsText,
                          # p[1].valueAsText,
                          # p[2].valueAsText,
                          # p[3].valueAsText,
                          # p[4].valueAsText,
                          # p[5].valueAsText,
                          # p[6].valueAsText)
        return

class SegmentedNetworkConfinementTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Confinement on Segmented Network"
        self.description = "Calculate the Valley Confinement Using a Pre-Segmented Network. "
        self.category = 'Confinement Tools\\Analysis'
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        paramRealization = arcpy.Parameter(
            displayName="Realization Name",
            name="realization",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        param0 = arcpy.Parameter(
            displayName="Input Stream Network with Confining State",
            name="lineNetwork",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param0.filter.list = ["Polyline"]

        paramFieldSegmentID = arcpy.Parameter(
            displayName="Segment ID Field",
            name="fieldSegmentID",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        paramFieldConfinement = arcpy.Parameter(
            displayName="IsConfined Field",
            name="fieldConfined",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        paramFieldConstriction = arcpy.Parameter(
            displayName="IsConstrict Field",
            name="fieldConstriction",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        params = [paramProjectXML,        #0
                  paramRealization, #1
                  paramAnalysisName, #2
                  paramStreamNetwork, #3
                  paramFieldSegmentID, #4
                  paramFieldConfinement, #5
                  paramFieldConstriction, #6
                  paramOutputWorkspaceMW, #7
                  paramTempWorkspace] #8
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, p):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        if p[0].value:
            if arcpy.Exists(p[0].value):
                confinementProject = Riverscapes.Project(p[0].valueAsText)
                p[1].enabled = "True"
                p[7].enabled = "False"
                p[1].filter.list = confinementProject.Realizations.keys()
                if p[1].value:
                    currentRealization = confinementProject.Realizations.get(p[1].valueAsText)
                    realization_id = currentRealization.id
                    p[3].value = currentRealization.OutputRawConfiningState.absolutePath(confinementProject.projectPath)
                    p[3].enabled = "False"
                    if p[2].value:
                        analysis_id = "ConfiningSegments_" + str(len(currentRealization.analyses) + 1).zfill(3)
                        p[7].value = path.join(confinementProject.projectPath, "Outputs", realization_id, "Analyses", analysis_id)
            else:
                p[1].filter.list = []
                p[1].value = ''
                p[1].enabled = "False"
                p[3].value = ""
                p[3].enabled = "True"
                p[7].value = ""
                p[7].enabled = "True"

        # Find Fields
        populateFields(p[3], p[4], "SegmentID")
        populateFields(p[3], p[5], "IsConfined")
        populateFields(p[3], p[6], "IsConstric")

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        if parameters[0].value:
            if arcpy.Exists(parameters[0].value):
                confinementProject = Riverscapes.Project(parameters[0].valueAsText)
                if parameters[1].value:
                    currentRealization = confinementProject.Realizations.get(parameters[1].valueAsText)
                    if parameters[2].value:
                        if parameters[2].value in currentRealization.analyses.keys():
                            parameters[2].setErrorMessage(parameters[2].name + " " + parameters[2].value +
                                                          " already exists for Realization " + currentRealization.name +
                                                          ".")

        testProjected(parameters[3])
        testWorkspacePath(parameters[7])
        testWorkspacePath(parameters[8])
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(ConfinementSegments)
        setEnvironmentSettings()

        if p[0].valueAsText:
            newConfinementProject = Riverscapes.Project(p[0].valueAsText)
            if p[1].valueAsText:
                currentRealization = newConfinementProject.Realizations.get(p[1].valueAsText)
                realization_id = currentRealization.id
                analysis_id = "ConfiningSegments_" + str(len(currentRealization.analyses) + 1).zfill(3)
                makedirs(path.join(newConfinementProject.projectPath, "Outputs", realization_id, "Analyses", analysis_id))

        ConfinementSegments.custom_segments(p[3].valueAsText,
                                            p[4].valueAsText,
                                            p[5].valueAsText,
                                            p[6].valueAsText,
                                            p[7].valueAsText,
                                            getTempWorkspace(p[8].valueAsText))

        if p[0].valueAsText:
            outConfinementProject = Riverscapes.Project(p[0].valueAsText)
            currentRealization = outConfinementProject.Realizations.get(p[1].valueAsText)
            realization_id = currentRealization.id
            analysis_id = outConfinementProject.projectType + "_" + str(len(currentRealization.analyses) + 1).zfill(3)

            outputConfinementSegments = Riverscapes.Dataset()
            outputConfinementSegments.create("ConfinementSegments",
                                        path.join("Outputs", realization_id, "Analyses", analysis_id, "ConfinementSegments") + ".shp")

            currentRealization.newAnalysisSegmentedNetwork(p[2].valueAsText,
                                                           p[4].valueAsText,
                                                           p[5].valueAsText,
                                                           p[6].valueAsText,
                                                           outputConfinementSegments,
                                                           analysis_id)

            outConfinementProject.Realizations[p[1].valueAsText] = currentRealization
            outConfinementProject.writeProjectXML()

        return

#
# Common Parameters #######################################################################################################
#
paramProjectXML = arcpy.Parameter(displayName="Confinement Project XML", name="projectXML", datatype="DEFile", parameterType="Optional", direction="Input")
paramProjectXML.filter.list = ["xml"]

paramStreamNetwork = arcpy.Parameter(displayName="Input Stream Network", name="InputFCStreamNetwork", datatype="GPFeatureLayer", parameterType="Required", direction="Input")
paramStreamNetwork.filter.list = ["Polyline"]

paramValleyBottom = arcpy.Parameter(displayName="Input Valley Bottom Polygon", name="InputValleyBottomPolygon", datatype="GPFeatureLayer", parameterType="Required", direction="Input")
paramValleyBottom.filter.list = ["Polygon"]

paramChannelPolygon = arcpy.Parameter(displayName="Input Active Channel Polygon (Buffered Bankfull)", name="InputBankfullChannelPoly", datatype="GPFeatureLayer", parameterType="Required", direction="Input")
paramChannelPolygon.filter.list = ["Polygon"]

paramAnalysisName = arcpy.Parameter(displayName="Name of Analysis", name="nameAnalysis", datatype="GPString", parameterType="Required", direction="Input")

# Workspace Params
paramOutputWorkspace = arcpy.Parameter(displayName="Output Workspace", name="strOutputWorkspace", datatype="DEWorkspace", parameterType="Optional", direction="Input", category="Outputs")

paramOutputWorkspaceMW = arcpy.Parameter(displayName="Output Workspace", name="strOutputWorkspace", datatype="DEWorkspace", parameterType="Optional", direction="Output", category="Outputs")

paramTempWorkspace = arcpy.Parameter(displayName="Temp Workspace", name="strTempWorkspace", datatype="DEWorkspace", parameterType="Optional", direction="Input", category="Outputs")
paramTempWorkspace.value = arcpy.env.scratchWorkspace


#
# Other Functions
#
def get_projectxml_param(display_name, str_category=""):
    param = arcpy.Parameter(displayName=display_name, name=display_name.replace(" ",""), datatype="DEFile", parameterType="Optional", direction="Input", category=str_category)
    paramProjectXML.filter.list = ["xml"]
    return param

def setEnvironmentSettings():
    arcpy.env.OutputMFlag = "Disabled"
    arcpy.env.OutputZFlag = "Disabled"
    return

def getTempWorkspace(strWorkspaceParameter):
    if strWorkspaceParameter == None or strWorkspaceParameter == "":
        return "in_memory"
    else:
       return strWorkspaceParameter

def testProjected(parameter):
    '''
        Description:
            Test if dataset referenced by parameter is in a projected coordinate system.
    '''
    if parameter.value:
        if arcpy.Exists(parameter.value):
            if arcpy.Describe(parameter.value).spatialReference.type <> u"Projected":
                parameter.setErrorMessage("Input " + parameter.name + " must be in a Projected Coordinate System.")
                return False
            else:
                return True

def testMValues(parameter):
    '''
        Description:
            Checks the dataset referenced by the parameter to see if it is M aware. If dataset is found to have M values then
            warn user to set environment settings before running tool.
    '''
    if parameter.value:
        if arcpy.Exists(parameter.value):
            if arcpy.Describe(parameter.value).hasM is True:
                parameter.setWarningMessage("Input " + parameter.name + " shoud not be M-enabled. Make sure to Disable M-values in the Environment Settings for this tool.")
                return False
            else:
                return True

def populateFields(parameterSource,parameterField,strDefaultFieldName):
    if parameterSource.value:
        if arcpy.Exists(parameterSource.value):
            # Get Fields
            fields = arcpy.Describe(parameterSource.value).fields
            listFields = []
            for f in fields:
                # DDH - Add fields to list but exclude specific types.
                if f.type in ["Double","GlobalID","Guid","Integer","Single","SmallInteger","String"]:
                    listFields.append(f.name)
            parameterField.filter.list=listFields
            if strDefaultFieldName in listFields:
                parameterField.value=strDefaultFieldName
            #else:
            #    parameterField.value=""
        else:
            parameterField.value=""
            parameterField.filter.list=[]
            parameterSource.setErrorMessage("Dataset does not exist.")
    return

def testLayerSelection(parameter):
    '''
        Description:
            Checks if the FeatureLayer referenced by parameter has a selection. If layer has then warn user to clear selection
    '''
    if parameter.value:
        if arcpy.Exists(parameter.value):
            desc=arcpy.Describe(parameter.value)
            if desc.dataType == "FeatureLayer":
                if desc.FIDSet:
                    parameter.setWarningMessage("Input layer " + parameter.name + " contains a selection. Clear the selection in order to run this tool on all features in the layer.")
    return

def testWorkspacePath(parameterWorkspace):
    if parameterWorkspace.value:
        if arcpy.Exists(parameterWorkspace.value):
            desc = arcpy.Describe(parameterWorkspace.value)
            if desc.dataType == "Workspace" or desc.dataType == "Folder":
                if desc.workspaceType == "LocalDatabase":
                    strPath = desc.path
                elif desc.workspaceType == "FileSystem":
                    strPath = str(parameterWorkspace.value)
                else:
                    parameterWorkspace.setWarningMessage("Cannot identify workspace type for " + parameterWorkspace.name + ".")
                    return
                if " " in strPath:
                    parameterWorkspace.setWarningMessage(parameterWorkspace.name + " contains a space in the file path name and could cause Geoprocessing issues. Please use a different workspace that does not contain a space in the path name.")
    return