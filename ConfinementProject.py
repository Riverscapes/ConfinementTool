"""Confinement Project"""

from os import path
import xml.etree.ElementTree as ET


class ConfinementProject(object):
    """Confinement Project Class
    Represent the inputs, realizations and outputs for a confinement project and read,
    write and update xml project file."""

    def __init__(self):

        self.name = ''
        self.projectType = "Confinement"
        self.projectPath = ''

        self.ProjectMetadata = {}
        self.Realizations = {}
        self.InputDatasets = {}

    def create(self,projectName):

        self.name = projectName

    def addProjectMetadata(self,Name,Value):
        self.ProjectMetadata[Name] = Value

    def addInputDataset(self, name, relativePath,sourcePath):

        newInputDataset = InputDataset()
        newInputDataset.create(name,relativePath,origPath=sourcePath)
        self.InputDatasets[newInputDataset.name] = newInputDataset

    def loadProjectXML(self,XMLpath):

        # Open and Verify XML.
        tree = ET.parse(XMLpath)
        root = tree.getroot()
        # TODO Validate XML, If fail, throw validation error
        # TODO Project Type self.projectType == "Confinement"

        # Load Project Level Info
        self.name = root.find("Name").text
        for meta in root.findall("./MetaData/Meta"):
            self.ProjectMetadata[meta.get("name")] = meta.text

        # Load Input Datasets
        for inputDatasetXML in root.findall("./Inputs/Vector"):
            inputDataset = InputDataset()
            inputDataset.createFromXMLElement(inputDatasetXML)
            self.InputDatasets[inputDataset.id] = inputDataset

        # Load Realizations
        for realizationXML in root.findall("./Realizations/Confinement"):
            realization = ConfinementRealization()
            realization.createFromXMLElement(realizationXML, self.InputDatasets)
            self.Realizations[realization.name] = realization

        # TODO Link Realizations with inputs?

        self.projectPath = path.dirname(XMLpath)

        return

    def addRealization(self, realization):

        self.Realizations[realization.name] = realization
        return

    def writeProjectXML(self,XMLpath):

        rootProject = ET.Element("Project")
        rootProject.set("xmlns:xsi","http://www.w3.org/2001/XMLSchema-instance")
        rootProject.set("xsi:noNamespaceSchemaLocation","https://raw.githubusercontent.com/Riverscapes/Program/master/Project/XSD/V1/Project.xsd")

        nodeName = ET.SubElement(rootProject,"Name")
        nodeName.text = self.name

        nodeType = ET.SubElement(rootProject,"ProjectType")
        nodeType.text = self.projectType

        nodeMetadata = ET.SubElement(rootProject,"MetaData")
        for metaName,metaValue in self.ProjectMetadata.iteritems():
            nodeMeta = ET.SubElement(nodeMetadata,"Meta",{"name":metaName})
            nodeMeta.text = metaValue

        if len(self.InputDatasets) > 0:
            nodeInputDatasets = ET.SubElement(rootProject,"Inputs")
            for inputDatasetName,inputDataset in self.InputDatasets.iteritems():
                nodeInputDataset = inputDataset.getXMLNode(nodeInputDatasets)

        if len(self.Realizations) > 0:
            nodeRealizations = ET.SubElement(rootProject,"Realizations")
            for realizationName, realizationInstance in self.Realizations.iteritems():
                nodeRealization = realizationInstance.getXMLNode(nodeRealizations)

        indent(rootProject)
        tree = ET.ElementTree(rootProject)
        tree.write(XMLpath,'utf-8',True)

        # TODO Add warning if xml does not validate??

        return


class ConfinementRealization(object):

    def __init__(self):

        self.promoted = ''
        self.dateCreated = ''
        self.productVersion = ''
        self.guid = ''
        self.name = ''

        self.StreamNetwork = ''
        self.ValleyBottom = ''
        self.ChannelPolygon = ''
        self.listSegmentedNetworks = []

        self.OutputConfiningMargins = OutputDataset()
        self.OutputRawConfiningState = OutputDataset()

        self.analyses = {}

    def create(self, name,StreamNetwork,ValleyBottom,ChannelPolygon,OutputConfiningMargins,OutputRawConfiningState):
        self.promoted = ''
        self.dateCreated = ''
        self.productVersion = ''
        self.guid = ''
        self.name = name

        StreamNetwork.type = "StreamNetwork"
        ValleyBottom.type = "ValleyBottom"
        ChannelPolygon.type = "ChannelPolygon"

        OutputConfiningMargins.type = "ConfiningMargins"
        OutputConfiningMargins.xmlSourceType = "ConfiningMargins"
        OutputRawConfiningState.type = "RawConfiningState"
        OutputRawConfiningState.xmlSourceType = "RawConfiningState"

        self.StreamNetwork = StreamNetwork
        self.ValleyBottom = ValleyBottom
        self.ChannelPolygon = ChannelPolygon

        self.OutputConfiningMargins = OutputConfiningMargins
        self.OutputRawConfiningState = OutputRawConfiningState

    def createFromXMLElement(self, xmlElement,dictInputDatasets):

        # Pull Realization Data
        self.promoted =  xmlElement.get("promoted")
        self.dateCreated = xmlElement.get("dateCreated")
        self.productVersion = xmlElement.get('productVersion')
        self.guid = xmlElement.get('guid')
        self.name = xmlElement.find('Name').text

        # Pull Inputs
        self.ValleyBottom = dictInputDatasets[xmlElement.find('./Inputs/ValleyBottom').get('ref')]
        self.ChannelPolygon = dictInputDatasets[xmlElement.find('./Inputs/ChannelPolygon').get('ref')]
        self.StreamNetwork = dictInputDatasets[xmlElement.find('./Inputs/StreamNetwork').get('ref')]
        #TODO pull segmented networks if they exist

        # Pull Outputs
        self.OutputConfiningMargins.createFromXMLElement(xmlElement.find("./Outputs/ConfiningMargins"))
        self.OutputRawConfiningState.createFromXMLElement(xmlElement.find("./Outputs/RawConfiningState"))

        # Pull Analyses
        for analysisXML in xmlElement.findall("./Analyses/*"):
            analysis = ConfinementAnalysis()
            analysis.createFromXMLElement(analysisXML)
            self.analyses[analysis.name] = analysis
        return

    def getXMLNode(self,xmlNode):

        # Prepare Attributes
        attributes = {}
        attributes['promoted'] = self.promoted
        attributes['dateCreated'] = self.dateCreated
        if self.productVersion:
            attributes['productVersion'] = self.productVersion
        if self.guid:
            attributes['Guid'] = self.guid

        # Create Node
        nodeRealization = ET.SubElement(xmlNode,"Confinement",attributes)
        nodeConfiementName = ET.SubElement(nodeRealization,"Name")
        nodeConfiementName.text = self.name

        # Realization Inputs
        nodeRealizationInputs = ET.SubElement(nodeRealization,"Inputs")
        nodeValleyBottom = ET.SubElement(nodeRealizationInputs,"ValleyBottom")
        nodeValleyBottom.set("ref",self.ValleyBottom.name)
        nodeChannelPolygon = ET.SubElement(nodeRealizationInputs,"ChannelPolygon")
        nodeChannelPolygon.set("ref",self.ChannelPolygon.name)
        nodeStreamNetwork = ET.SubElement(nodeRealizationInputs,"StreamNetwork")
        nodeStreamNetwork.set('ref',self.StreamNetwork.name)
        # TODO Add Custom Segmented Networks if exists

        nodeOutputs = ET.SubElement(nodeRealization,"Outputs")
        self.OutputRawConfiningState.getXMLNode(nodeOutputs)
        self.OutputConfiningMargins.getXMLNode(nodeOutputs)

        #Realization Analyses
        nodeAnalyses = ET.SubElement(nodeRealization,"Analyses")
        for analysisName,analysis in self.analyses.iteritems():
            analysis.getXMLNode(nodeAnalyses)

        return nodeRealization

    def newAnalysisMovingWindow(self,analysisName,paramSeedPointDist,paramWindowSizes,outputSeedPoints,outputWindows):

        analysis = ConfinementAnalysis()
        analysis.create(analysisName,"MovingWindow")

        analysis.parameters["SeedPointDistance"] = paramSeedPointDist
        analysis.parameters["WindowSizes"] = paramWindowSizes
        analysis.outputDatasets["SeedPointFile"] = outputSeedPoints
        analysis.outputDatasets["MovingWindowFile"] = outputWindows

        self.analyses[analysisName] = analysis

    def newAnalysisFixedSegments(self,analysisName,paramSegmentSize,outputSegments):
        analysis = ConfinementAnalysis()
        analysis.create(analysisName,"FixedSegments")

        analysis.parameters["SegmentSize"] = paramSegmentSize
        analysis.outputDatasets["FixedSegmentFile"] = outputSegments

        self.analyses[analysisName] = analysis
        return


    def newAnalysisCustomSegments(self,analysisName):

        analysis = ConfinementAnalysis()
        analysis.create(analysisName, "CustomSegments")

        # ToDO Custom Segment
        # Special case, need to add segment as input to realization, and input datasets??!!

        self.analyses[analysisName] = analysis

        return


class ConfinementAnalysis(object):

    def __init__(self):
        self.name = ''
        self.type = ''
        self.parameters = {}
        self.outputDatasets = {}

    def create(self,analysisName,analysisType):
        self.name = analysisName
        self.type = analysisType
        return

    def createFromXMLElement(self,xmlElement):

        self.type = xmlElement.tag
        self.name = xmlElement.find("Name").text

        for param in xmlElement.findall("./Parameters/Param"):
            self.parameters[param.get('name')] = param.text

        for output in xmlElement.findall("./Outputs/*"):
            outputDS = OutputDataset()
            outputDS.createFromXMLElement(output)
            self.outputDatasets[outputDS.name] = outputDS

        return

    def addParameter(self,parameterName,parameterValue):
        self.parameters[parameterName] = parameterValue
        return

    def getXMLNode(self,xmlNode):

        nodeAnalysis = ET.SubElement(xmlNode,self.type)

        nodeAnalysisName = ET.SubElement(nodeAnalysis,'Name')
        nodeAnalysisName.text = self.name

        nodeParameters = ET.SubElement(nodeAnalysis,"Parameters")
        for paramName,paramValue in self.parameters.iteritems():
            nodeParam = ET.SubElement(nodeParameters,"Param",{"name":paramName})
            nodeParam.text = paramValue

        nodeOutputs = ET.SubElement(nodeAnalysis,"Outputs")
        for outputName,outputDataset in self.outputDatasets.iteritems():
            outputDataset.getXMLNode(nodeOutputs)

        #TODO Writing Analysis Node

        return xmlNode


class InputDataset(object):

    def __init__(self):
        self.id = '' # also ref
        self.name = ''
        self.guid = ''
        self.type = ''
        self.relpath = ''
        self.meta = ""
        self.origPath = ""

    def create(self, name, relpath, inputtype="Vector",guid='',origPath=""):

        self.name = name # also ref
        self.guid = guid
        self.type = inputtype
        self.relpath = relpath
        self.origPath = origPath

        self.id = name # TODO make this unique!!!!

    def createFromXMLElement(self, xmlElement):

        self.id = xmlElement.get("id")
        self.guid = xmlElement.get('Guid')
        self.name = xmlElement.find('Name').text
        self.relpath = xmlElement.find("Path").text

        for nodeMetaOrigin in xmlElement.findall("MetaData/Meta"):
            if nodeMetaOrigin.get('name') == "original_path":
                self.origPath = nodeMetaOrigin.text

    def getXMLNode(self,xmlNode):

        #Prepare Attributes
        attributes = {}
        attributes["id"] = self.id
        if self.guid:
            attributes['Guid'] = self.guid

        # Generate Node
        nodeInputDataset = ET.SubElement(xmlNode,"Vector",attributes)

        nodeInputDatasetName = ET.SubElement(nodeInputDataset, "Name")
        nodeInputDatasetName.text = self.name
        nodeInputDatasetPath = ET.SubElement(nodeInputDataset,"Path")
        nodeInputDatasetPath.text = self.relpath

        if self.origPath:
            nodeInputDatasetMeta = ET.SubElement(nodeInputDataset,"MetaData")
            nodeInputDatasetOrigPath = ET.SubElement(nodeInputDatasetMeta,"Meta",{"name":"original_path"})
            nodeInputDatasetOrigPath.text = self.origPath

        return xmlNode

    def absolutePath(self,projectPath):

        return path.join(projectPath,self.relpath,self.name) + '.shp'


class OutputDataset(object):

    def __init__(self):
        self.name = ''
        self.type = ''
        self.relpath = ''
        self.xmlSourceType = "Vector"

    def create(self, name, relpath, outputtype="Vector"):
        self.name = name # also ref
        self.type = outputtype
        self.relpath = relpath

    def createFromXMLElement(self, xmlElement):
        self.name = xmlElement.find('Name')
        self.relpath = xmlElement.find("Path").text

        if xmlElement.tag == "Vector":
            self.type = xmlElement.find("./MetaData/Meta[@name='Type']").text
        else:
            self.type = xmlElement.tag
            self.xmlSourceType = xmlElement.tag
        return

    def absolutePath(self,projectPath):
        return path.join(projectPath,self.relpath)

    def getXMLNode(self,xmlNode):

        nodeOutput = ET.SubElement(xmlNode,self.xmlSourceType)
        nodeOutputName = ET.SubElement(nodeOutput,"Name")
        nodeOutputName.text = self.name
        nodeOutputPath = ET.SubElement(nodeOutput,"Path")
        nodeOutputPath.text = self.relpath

        if self.xmlSourceType == "Vector":
            nodeTypeMetaData = ET.SubElement(nodeOutput,"MetaData")
            nodeTypeMeta = ET.SubElement(nodeTypeMetaData,"Meta",{"name":"Type"})
            nodeTypeMeta.text = self.type

        def absolutePath(self, projectPath):
            return path.join(projectPath, self.relpath, self.name) + '.shp'

# Other Functions ##
def indent(elem, level=0, more_sibs=False):
    """ Pretty Print XML Element
    Source: http://stackoverflow.com/questions/749796/pretty-printing-xml-in-python
    """

    i = "\n"
    if level:
        i += (level-1) * '  '
    num_kids = len(elem)
    if num_kids:
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
            if level:
                elem.text += '  '
        count = 0
        for kid in elem:
            indent(kid, level+1, count < num_kids - 1)
            count += 1
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
            if more_sibs:
                elem.tail += '  '
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
            if more_sibs:
                elem.tail += '  '