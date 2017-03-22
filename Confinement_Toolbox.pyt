# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Name:        Stream and Valley Confinement Toolbox                          #
# Purpose:     Tools for and calculating confinement on a stream              # 
#              network or using a moving window along the stream network      #
#                                                                             #
# Authors:     Kelly Whitehead (kelly@southforkresearch.org)                  #
#              South Fork Research, Inc                                       #
#              Seattle, Washington                                            #
#                                                                             #
# Created:     2015-Jan-08                                                    #
# Version:     2.1                                                            #
# Released:                                                                   #
#                                                                             #
# License:     Free to use.                                                   #
#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# !/usr/bin/env python

# # Import Modules # #
from os import path, makedirs
import arcpy
from arcgis_package import ConfiningMargins, MovingWindow, ConfinementSegments
# import ConfinementProject
import Riverscapes

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Confinement Toolbox"
        self.alias = ''
        #self.description = "Tools for generating Valley Confinement."

        # List of tool classes associated with this toolbox
        self.tools = [MovingWindowConfinementTool,
                      SegmentedNetworkConfinementTool,
                      #FixedSegmentConfinementTool,
                      ConfiningMarginTool,
                      ConfinementProjectTool,
                      LoadInputsTool]

###### Project Management ######
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

        params = [param0,param1,param2,param3,param4]
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
        reload(Riverscapes)
        from os import path
        newConfinementProject = Riverscapes.Project()# ConfinementProject.ConfinementProject()
        newConfinementProject.create(p[0].valueAsText,"Confinement")
        newConfinementProject.addProjectMetadata("Operator",p[2].valueAsText)
        newConfinementProject.addProjectMetadata("Region",p[3].valueAsText)
        newConfinementProject.addProjectMetadata("Watershed",p[4].valueAsText)
        newConfinementProject.addProjectMetadata("ConfinementProjectVersion","2.1.02")
        newConfinementProject.writeProjectXML(path.join(p[1].valueAsText,"project.rs.xml"))

        return

class LoadInputsTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Load Input Datsets"
        self.description = "Load Input Datsets to a Confinment Project. Tool Documentation: https://bitbucket.org/KellyWhitehead/geomorphic-network-and-analysis-toolbox/wiki/Tool_Documentation/MovingWindow"
        self.canRunInBackground = False
        self.category = "Confinement Project Management"

    def getParameterInfo(self):
        """Define parameter definitions"""

        p1 = paramStreamNetwork
        p2 = paramChannelPolygon
        p3 = paramValleyBottom

        p1.parameterType = "Optional"
        p2.parameterType = "Optional"
        p3.parameterType = "Optional"

        params = [paramProjectXML,
                  p1,
                  p2,
                  p3]

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
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(Riverscapes)
        from os import path,makedirs
        newConfinementProject = Riverscapes.Project() #ConfinementProject.ConfinementProject()
        newConfinementProject.loadProjectXML(p[0].valueAsText)

        pathProject = arcpy.Describe(p[0].valueAsText).path

        # Create Project Paths if they do not exist
        pathInputs = pathProject + "\\Inputs"
        if not arcpy.Exists(pathInputs):
            makedirs(pathInputs)


        # KMW - The following is a lot of repeated code for each input. It contains file and folder creation and copying, rather than useing the project module to do this. This could be streamlined in the future, but
        # is working at the moment.
        if p[1].valueAsText: # Stream Network Input
            pathStreamNetworks = pathInputs + "\\StreamNetworks"
            nameStreamNetwork = arcpy.Describe(p[1].valueAsText).basename
            if not arcpy.Exists(pathStreamNetworks):
                makedirs(pathStreamNetworks)
            id_streamnetwork = Riverscapes.get_input_id(pathStreamNetworks, "StreamNetwork")
            pathStreamNetworkID = path.join(pathStreamNetworks, id_streamnetwork)
            makedirs(pathStreamNetworkID)
            arcpy.FeatureClassToFeatureClass_conversion(p[1].valueAsText, pathStreamNetworkID, nameStreamNetwork)
            newConfinementProject.addInputDataset(nameStreamNetwork,
                                                  id_streamnetwork,
                                                  path.join(path.relpath(pathStreamNetworkID, pathProject),
                                                            nameStreamNetwork) + ".shp",
                                                  p[1].valueAsText)

        if p[2].valueAsText: # Channel Polygon
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
                                                  path.join(path.relpath(pathChannelPolygonID, pathProject),
                                                            nameChannelPolygon) + ".shp",
                                                  p[2].valueAsText)

        if p[3].valueAsText: # Valley  Bottom
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
                                                  path.join(path.relpath(pathValleyBottomID,pathProject),nameValleyBottom) + ".shp",
                                                  p[3].valueAsText)

        # Write new XML
        newConfinementProject.writeProjectXML(p[0].valueAsText)

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
        """Define parameter definitions"""

        # 0
        # paramProjectXML
        #paramProjectXML.filter.list = ["xml"]

        # 1
        paramRealizationName = arcpy.Parameter(
            displayName="Confinement Realization Name",
            name="realizationName",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        # 2
        #paramStreamNetwork

        # 3
        #paramChannelPolygon

        # 4
        #paramValleyBottom

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

        return [paramProjectXML,
                paramRealizationName,
                paramStreamNetwork,
                paramValleyBottom,
                paramChannelPolygon,
                paramOutputRawConfiningState,
                paramOutputConfiningMargins,
                paramTempWorkspace]

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
                # p[2].datatype = "GPString"
                # p[3].datatype = "GPString"
                # p[4].datatype = "GPString"
                p[5].enabled = "False"
                p[6].enabled = "False"
                p[5].parameterType = "Optional"
                p[6].parameterType = "Optional"

                currentProject = Riverscapes.Project()# ConfinementProject.ConfinementProject()
                currentProject.loadProjectXML(p[0].valueAsText)

                # listInputDatasets = []
                # for name,inputDataset in currentProject.InputDatasets.iteritems():
                #     listInputDatasets.append(inputDataset.absolutePath(projectPath))
                # p[2].filter.list = listInputDatasets
                # p[3].filter.list = listInputDatasets
                # p[4].filter.list = listInputDatasets

                if p[1].altered:
                    if p[1].value:
                        from os import path
                        p[5].value = path.join(currentProject.projectPath, "Outputs", p[1].valueAsText) + "\\RawConfiningState.shp"
                        p[6].value = path.join(currentProject.projectPath, "Outputs", p[1].valueAsText) + "\\ConfiningMargins.shp"

                # TODO manage output folder if project mode


            else:
                p[5].enabled = "True"
                p[6].enabled = "True"
                p[5].parameterType = "Required"
                p[6].parameterType = "Optional"

        return


    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        if parameters[0].valueAsText:
            newConfinementProject = Riverscapes.Project() # ConfinementProject.ConfinementProject()
            newConfinementProject.loadProjectXML(parameters[0].valueAsText)

            for realization in newConfinementProject.Realizations:
                if realization == parameters[1].valueAsText:
                    parameters[1].setErrorMessage("Realization " + parameters[1].valueAsText + " already exists.")
                    break

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
            newConfinementProject = Riverscapes.Project()# ConfinementProject.ConfinementProject()
            newConfinementProject.loadProjectXML(p[0].valueAsText)
            if p[1].valueAsText:
                from os import path,makedirs
                makedirs(path.join(newConfinementProject.projectPath, "Outputs",p[1].valueAsText))

        ConfiningMargins.main(p[2].valueAsText,
                              p[3].valueAsText,
                              p[4].valueAsText,
                              p[5].valueAsText,
                              p[6].valueAsText,
                              getTempWorkspace(p[7].valueAsText)) # If Not specified, in memory is used

        # on success, rewrite xml file if in project mode
        if p[0].valueAsText:
            newConfinementProject = Riverscapes.Project() # ConfinementProject.ConfinementProject()
            newConfinementProject.loadProjectXML(p[0].valueAsText)

            # Retain if we want to reuse this - do we create inputs here??
            # inputValleyBottom = ConfinementProject.dataset()
            # inputValleyBottom.create(arcpy.Describe(p[3].valueAsText).basename,p[3].valueAsText)
            #
            # inputChannelPolygon = ConfinementProject.dataset()
            # inputChannelPolygon.create(arcpy.Describe(p[4].valueAsText).basename,p[4].valueAsText)
            #
            # inputStreamNetwork = ConfinementProject.dataset()
            # inputStreamNetwork.create(arcpy.Describe(p[2].valueAsText).basename,p[2].valueAsText)

            idStreamNetwork = newConfinementProject.get_dataset_id(p[2].valueAsText)
            idValleyBottom = newConfinementProject.get_dataset_id(p[3].valueAsText)
            idChannelPolygon = newConfinementProject.get_dataset_id(p[4].valueAsText)

            outputRawConfiningState = Riverscapes.dataset()
            outputRawConfiningState.create(arcpy.Describe(p[5].valueAsText).basename,p[5].valueAsText) # TODO make this relative path

            outputConfiningMargins = Riverscapes.dataset()
            outputConfiningMargins.create(arcpy.Describe(p[6].valueAsText).basename,p[6].valueAsText)

            newRealization = Riverscapes.ConfinementRealization()
            newRealization.create(p[1].valueAsText,
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
            self.description = "Calculate the Valley Confinement. Tool Documentation: https://bitbucket.org/KellyWhitehead/geomorphic-network-and-analysis-toolbox/wiki/Tool_Documentation/MovingWindow"
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
            reload(Riverscapes)

            if p[0].value:
                if arcpy.Exists(p[0].value):
                    confinementProject = Riverscapes.Project() #ConfinementProject.ConfinementProject()
                    confinementProject.loadProjectXML(p[0].valueAsText)
                    p[1].enabled = "True"
                    p[9].enabled = "False"
                    p[1].filter.list = confinementProject.Realizations.keys()
                    if p[1].value:
                        currentRealization = confinementProject.Realizations.get(p[1].valueAsText)
                        p[3].value = currentRealization.OutputRawConfiningState.absolutePath(confinementProject.projectPath)
                        p[3].enabled = "False"
                        if p[2].value:
                            from os import path
                            p[9].value = path.join(confinementProject.projectPath, "Outputs", p[1].valueAsText, "Analyses", p[2].valueAsText)
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
            confinementProject = Riverscapes.Project() #ConfinementProject.ConfinementProject()
            if parameters[0].value:
                if arcpy.Exists(parameters[0].value):
                    confinementProject.loadProjectXML(parameters[0].valueAsText)
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
            reload(Riverscapes)
            setEnvironmentSettings()

            # if in project mode, create workspaces as needed.
            if p[0].valueAsText:
                newConfinementProject = Riverscapes.Project() #ConfinementProject.ConfinementProject()
                newConfinementProject.loadProjectXML(p[0].valueAsText)
                if p[1].valueAsText:
                    makedirs(path.join(newConfinementProject.projectPath, "Outputs" , p[1].valueAsText, "Analyses",p[2].valueAsText))

            MovingWindow.main(p[3].valueAsText,
                              p[4].valueAsText,
                              p[5].valueAsText,
                              p[6].valueAsText,
                              p[7].valueAsText,
                              p[8].valueAsText,
                              p[9].valueAsText,
                              p[10].valueAsText)

            if p[0].valueAsText:

                outputSeedPoints = Riverscapes.dataset() #ConfinementProject.dataset()
                outputSeedPoints.create("MovingWindowSeedPoints",path.join( "Outputs" , p[1].valueAsText, "Analyses",p[2].valueAsText, "MovingWindowSeedPoints") + ".shp")

                outputWindows = Riverscapes.dataset() #ConfinementProject.dataset()
                outputWindows.create("MovingWindowSegments",path.join( "Outputs" , p[1].valueAsText, "Analyses",p[2].valueAsText, "MovingWindowSegments") + ".shp")

                outConfinementProject = Riverscapes.Project() # .ConfinementProject()
                outConfinementProject.loadProjectXML(p[0].valueAsText)
                currentRealization = outConfinementProject.Realizations.get(p[1].valueAsText)
                currentRealization.newAnalysisMovingWindow(p[2].valueAsText,p[7].valueAsText,p[8].valueAsText,outputSeedPoints,outputWindows)

                outConfinementProject.Realizations[p[1].valueAsText] = currentRealization

                outConfinementProject.writeProjectXML(p[0].valueAsText)

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
            datatype="GPFeatureLayer",
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

        reload(Riverscapes)

        if p[0].value:
            if arcpy.Exists(p[0].value):
                confinementProject = Riverscapes.Project() # ConfinementProject.ConfinementProject()
                confinementProject.loadProjectXML(p[0].valueAsText)
                p[1].enabled = "True"
                p[7].enabled = "False"
                p[1].filter.list = confinementProject.Realizations.keys()
                if p[1].value:
                    currentRealization = confinementProject.Realizations.get(p[1].valueAsText)
                    p[3].value = currentRealization.OutputRawConfiningState.absolutePath(confinementProject.projectPath)
                    p[3].enabled = "False"
                    if p[2].value:
                        from os import path
                        p[7].value = path.join(confinementProject.projectPath, "Outputs", p[1].valueAsText, "Analyses", p[2].valueAsText)
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
        confinementProject = Riverscapes.Project()
        if parameters[0].value:
            if arcpy.Exists(parameters[0].value):
                confinementProject.loadProjectXML(parameters[0].valueAsText)
            if parameters[1].value:
                currentRealization = confinementProject.Realizations.get(parameters[1].valueAsText)
                if parameters[2].value:
                    if parameters[2].value in currentRealization.analyses.keys():
                        parameters[2].setErrorMessage(parameters[2].name + " " + parameters[
                            2].value + " already exists for Realization " + currentRealization.name + ".")

        testProjected(parameters[3])
        testWorkspacePath(parameters[7])
        testWorkspacePath(parameters[8])
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(ConfinementSegments)
        reload(Riverscapes)
        setEnvironmentSettings()

        if p[0].valueAsText:
            newConfinementProject = Riverscapes.Project() #.ConfinementProject()
            newConfinementProject.loadProjectXML(p[0].valueAsText)
            if p[1].valueAsText:
                makedirs(path.join(newConfinementProject.projectPath, "Outputs", p[1].valueAsText, "Analyses",
                                   p[2].valueAsText))

        ConfinementSegments.custom_segments(p[3].valueAsText,
                                            p[4].valueAsText,
                                            p[5].valueAsText,
                                            p[6].valueAsText,
                                            p[7].valueAsText,
                                            p[8].valueAsText)

        if p[0].valueAsText:
            outputConfinementSegments = Riverscapes.dataset() #ConfinementProject.dataset()
            outputConfinementSegments.create("ConfinementSegments",
                                        path.join("Outputs", p[1].valueAsText, "Analyses", p[2].valueAsText, "ConfinementSegments") + ".shp")

            outConfinementProject = Riverscapes.Project() #ConfinementProject.ConfinementProject()
            outConfinementProject.loadProjectXML(p[0].valueAsText)
            currentRealization = outConfinementProject.Realizations.get(p[1].valueAsText)
            currentRealization.newAnalysisSegmentedNetwork(p[2].valueAsText,
                                                           p[4].valueAsText,
                                                           p[5].valueAsText,
                                                           p[6].valueAsText,
                                                           outputConfinementSegments)

            outConfinementProject.Realizations[p[1].valueAsText] = currentRealization
            outConfinementProject.writeProjectXML(p[0].valueAsText)

        return

# Common Params #######################################################################################################
paramProjectXML = arcpy.Parameter(
    displayName="Confinement Project XML",
    name="projectXML",
    datatype="DEFile",
    parameterType="Optional",
    direction="Input")
paramProjectXML.filter.list = ["rs.xml"]

paramStreamNetwork = arcpy.Parameter(
    displayName="Input Stream Network",
    name="InputFCStreamNetwork",
    datatype="DEFeatureClass",
    parameterType="Required",
    direction="Input")
paramStreamNetwork.filter.list = ["Polyline"]

paramValleyBottom = arcpy.Parameter(
    displayName="Input Valley Bottom Polygon",
    name="InputValleyBottomPolygon",
    datatype="DEFeatureClass", #Integer
    parameterType="Required",
    direction="Input")
paramValleyBottom.filter.list = ["Polygon"]

paramChannelPolygon = arcpy.Parameter(
    displayName="Input Buffered Bankfull Channel Polygon",
    name="InputBankfullChannelPoly",
    datatype="DEFeatureClass",
    parameterType="Required",
    direction="Input")
paramChannelPolygon.filter.list = ["Polygon"]

paramAnalysisName = arcpy.Parameter(
    displayName="Name of Analysis",
    name="nameAnalysis",
    datatype="GPString",
    parameterType="Required",
    direction="Input")

# Workspace Params
paramOutputWorkspace = arcpy.Parameter(
    displayName="Output Workspace",
    name="strOutputWorkspace",
    datatype="DEWorkspace",
    parameterType="Optional",
    direction="Input",
    category="Outputs")

paramOutputWorkspaceMW = arcpy.Parameter(
    displayName="Output Workspace",
    name="strOutputWorkspace",
    datatype="DEWorkspace",
    parameterType="Optional",
    direction="Output",
    category="Outputs")

paramTempWorkspace = arcpy.Parameter(
    displayName="Temp Workspace",
    name="strTempWorkspace",
    datatype="DEWorkspace",
    parameterType="Optional",
    direction="Input",
    category="Outputs")
paramTempWorkspace.value = arcpy.env.scratchWorkspace


# Other Functions # 
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
    # Test Projection
    if parameter.value:
        if arcpy.Exists(parameter.value):
            if arcpy.Describe(parameter.value).spatialReference.type <> u"Projected":
                parameter.setErrorMessage("Input " + parameter.name + " must be in a Projected Coordinate System.")
                return False
            else:
                return True


def testMValues(parameter):
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
                listFields.append(f.name)
            parameterField.filter.list=listFields
            if strDefaultFieldName in listFields:
                parameterField.value=strDefaultFieldName
            #else:
            #    parameterField.value=""
        else:
            parameterField.value=""
            parameterField.filter.list=[]
            parameterSource.setErrorMessage(" Dataset does not exist.")
    return


def testLayerSelection(parameter):
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