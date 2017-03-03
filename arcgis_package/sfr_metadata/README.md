# SFR Metadata Module

**Version** 0.3

**Date** 2016 Sept 8

**Author** Kelly@southforkresearch.org 

## Introduction

The SFR Metadata module is a python module used to generate xml metadata files for geoprocessing models using a standard format. 

A standard format allows for more streamlined workflows, in both producing summary xml files as well as not having to develop new code to consume these files for each and every geoprocessing task that is developed.

### Package Contents
- **Metadata.py**: Primary module
- **MetadataExample.py**: Script to generate a sample output. Also serves as a coding example.
- **Samples**: Contains samples of the output xml metadata.
- **Validation**: XML Schema files that can be used to validate the output XML metadata file.

## How to Use

1. Import the Metadata module in your geoprocessing script.
2. Within the main body of your script (somewhere near the start, before the bulk of the processing begins), create an instance of MetadataWriter. Specify:
   a. the Name of the Script
   b. the Version of the Script
   c. (optional) the name of the user or operator.

```
    mWriter = Metadata.MetadataWriter("Test Tool Name","0.0")
```

2. Create a new "run"
   a. This will create a timestamp of the processing start time.

```
    mWriter.createRun()
```

3. Specify the parameters for the run
   a. Each parameter needs a name and a value.

```
    mWriter.currentRun.addParameter("Parameter Name","Parameter Value")
```

4. Specify the outputs. This could happen at anytime during the processing.
	a. Each output needs a name and a value.
    b. 

```
    mWriter.currentRun.addOutput("Output Name 1","Output Value 1")
```

5. Add Processing messages to the metadataWriter object. This can also happen at any point during the script processing.
   a. You can also specify an optional "level" (i.e. "error", "info" etc.). These are XML attributes, so should not contain spaces.
 
```
    mWriter.currentRun.addMessage("Info","Info Message Text")
    mWriter.currentRun.addMessage("Warning","Warning Message Text")
    mWriter.currentRun.addMessage("Error","Error Message Text")
```

6. Add any results (These are custom for each model and are not validated by the xsd)
	
```
    mWriter.currentRun.addResult("ResultNode1","ResultValue1")
    mWriter.currentRun.addResult("ResultNode2","ResultValue2")
```

> The difference between an "output" and a "result" is that the result name becomes an XML tag (within the Results element).

5. Finalize the run
   b. This will stop the timestamp.

```
    strToolStatus = "Success" # Optional status for the run
    mWriter.finalizeRun(strToolStatus)
```

6. Repeat steps 2-5 if running a batch (these should be within the batch loop).
9. Write the XML file.

```
    mWriter.writeMetadataFile(metadatafile)
```


