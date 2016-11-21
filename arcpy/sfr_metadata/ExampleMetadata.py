""" Write a test metadata.xml file"""

import Metadata
import sys

def main(metadatafile):
    """ Write a test metadata.xml file"""

    # Create a Metadata Writer once with Tool Name and Version
    mWriter = Metadata.MetadataWriter("Test Tool Name","0.0")

    ## You can loop the following for a batch mode, or just once for a single tool run 
    # Create a "run", and start the processing clock
    mWriter.createRun()

    # Add Parameter Name and value for each Input
    mWriter.currentRun.addParameter("Parameter Name 1","Parameter Value 1")
    mWriter.currentRun.addParameter("Parameter Name 2","Parameter Value 2")

    # Add Output Name and Value for each output
    mWriter.currentRun.addOutput("Output Name 1","Output Value 1")
    mWriter.currentRun.addOutput("Output Name 2","Output Value 2")

    # Use addMessage to write messages to the file. 
    mWriter.currentRun.addMessage("Info","Info Message Text")
    mWriter.currentRun.addMessage("Warning","Warning Message Text")
    mWriter.currentRun.addMessage("Error","Error Message Text")

    # Use addCustomNode to write custom node tags to Information Node
    mWriter.currentRun.addResult("CustomNode1","CustomValue1")
    mWriter.currentRun.addResult("CustomNode2","CustomValue2")

    # When Processing is complete, stop the clock
    strToolStatus = "Success" # Optional status for the run
    mWriter.finalizeRun(strToolStatus)
    ## Repeat this block for each run if in batch mode.

    # At the very end, write the file. (Only do this at the very end if batching!)
    mWriter.writeMetadataFile(metadatafile)

if __name__ == "__main__":

    main(sys.argv[1])