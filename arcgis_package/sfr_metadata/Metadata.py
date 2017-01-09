""" Module for writing Metadata XML files for SFR GIS tools. 
    
    Author: kelly@southforkresearch.org
    Version: 0.3
    Date: 2016-Sept-8
"""

import xml.etree.ElementTree as ET
import datetime
from getpass import getuser
from socket import gethostname

class MetadataWriter():
    """Object to store tool run metadata and write output xml file"""

    Runs = []

    metadataVersion = "0.3"
    scriptVersion = "0.3"
    metadataType = "SFR Processing"

    def __init__(self,ToolName,ToolVersion,Operator="",GISVersion=""):
        """Create a new instance of a Metadata File Object.
        
        Arguments
        MetadataFileName: Path and Name of output xml file
        ToolName: Name of the tool or script
        ToolVersion: Version of the Tool or Script
        Keyword Arguments:
        Operator (Optional): Name of the user. If not specified, the os username is used.
        """

        self.toolName = ToolName
        self.toolVersion = ToolVersion
        #self.gisVersion = GISVersion
        self.computerID = gethostname()

        if Operator:
            self.operator = Operator
        else:
            try:
                self.operator = getuser()
            except:
                self.operator = "USERNAME not found"

    def createRun(self):
        """Create a new instance of a run"""
        self.currentRun = run()

    def finalizeRun(self,status=""):
        """Finish processing run and save to Metadata Runs"""

        self.currentRun.finalize(status)
        self.Runs.append(self.currentRun)

    def writeMetadataFile(self,metadataFile):
        """ save the final metadata xml file"""
        rootElement = ET.Element("Metadata",{"type":self.metadataType,"metadata_version":self.metadataVersion,"script_version":self.scriptVersion})

        nodeTool = ET.SubElement(rootElement,"Tool")
        ET.SubElement(nodeTool,"Name").text = self.toolName
        ET.SubElement(nodeTool,"Version").text = self.toolVersion

        nodeProcessing = ET.SubElement(rootElement,"Processing")
        ET.SubElement(nodeProcessing,"ComputerID").text = self.computerID
        ET.SubElement(nodeProcessing,"Operator").text = self.operator
        #ET.SubElement(nodeProcessing,"GISVersion").text = self.gisVersion

        nodeRuns = ET.SubElement(nodeProcessing,"Runs")
        for run in self.Runs:
            nodeRun = ET.SubElement(nodeRuns,"Run",{"status":run.status})

            ET.SubElement(nodeRun,"TimeStart").text = run.timestampStart.strftime('%Y-%m-%dT%H:%M:%S')
            ET.SubElement(nodeRun,"TimeStop").text = run.timestampStop.strftime('%Y-%m-%dT%H:%M:%S')
            ET.SubElement(nodeRun,"TotalProcessingTime").text = str(run.timeProcessing.total_seconds()) # Need to provide attribute for unit of time

            nodeParameters = ET.SubElement(nodeRun,"Parameters")
            for parameter in run.Parameters:
                nodeParameter = ET.SubElement(nodeParameters,"Parameter")
                ET.SubElement(nodeParameter,"Name").text = parameter.Name
                ET.SubElement(nodeParameter,"Value").text = parameter.Value

            nodeOutputs = ET.SubElement(nodeRun,"Outputs")
            for output in run.Outputs:
                nodeOutput = ET.SubElement(nodeOutputs,"Output")
                ET.SubElement(nodeOutput,"Name").text = output.Name
                ET.SubElement(nodeOutput,"Value").text = output.Value

            nodeMessages = ET.SubElement(nodeRun,"Messages")
            for message in run.Messages:
                ET.SubElement(nodeMessages,"Message",{"Level":message.Level}).text = message.Message

            nodeResults = ET.SubElement(nodeRun,"Results")
            for result in run.Results:
                ET.SubElement(nodeResults,result.Name).text = result.Value

        #nodeSummary = ET.SubElement(nodeProcessing,"Summary")

        indent(rootElement)
        tree = ET.ElementTree(rootElement)
        tree.write(metadataFile,'utf-8',True)
        
class run():
    """ Class that represents a tool run. """
    
    Parameters = []
    Outputs = []
    Messages = []
    Results = []

    def __init__(self):
        """Get the start timestamp"""
        self.timestampStart = datetime.datetime.now()

    def addParameter(self,parameterName,parameterValue):
        """Add a parameter to the processing run"""
        newParameter = parameter(parameterName,parameterValue)
        self.Parameters.append(newParameter)

    def addOutput(self,outputName,outputValue):
        """Add an output to the processing run"""
        newOutput = output(outputName,outputValue)
        self.Outputs.append(newOutput)

    def addMessage(self,severityLevel,messageText):
        """Add a message to the processing run"""
        newMessage = message(severityLevel,messageText)
        self.Messages.append(newMessage)

    def addResult(self,Name,Value):
        """Add a custom Node to Information Node"""
        newResult = result(Name,Value)
        self.Results.append(newResult)

    def finalize(self,status=""):
        """Sets the stop timestamp and total processing time"""
        self.timestampStop = datetime.datetime.now()
        self.timeProcessing = self.timestampStop - self.timestampStart

        self.status = status

class parameter():

    def __init__(self,Name,Value):
        self.Name = Name
        self.Value = Value

class output():

    def __init__(self,name,value):
        self.Name = name
        self.Value = value

class message():

    def __init__(self,level,message):
        self.Level = level
        self.Message = message

class result():
    
    def __init__(self,Name,Value):
        self.Name = Name
        self.Value = Value

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
