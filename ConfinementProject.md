
# Confinement Project

While the confinement tool can be used on any GIS data, a preferred workflow is to use a Confinement Project. A confinement project is simply a managed folder structure with an accompanying XML file. The confinement tools are structured to use this XML file to find data and keep a record of all outputs and analysis for a particular set of confinement data. 

A confinement project is also structured to work with the Riverscapes Analyst Toolbar and Data Warehouse. If data is to be included in this system, then it must be processed as a Confinement Project.

Confinement Projects must be set up at the start of processing. There is currently no tools to convert previous results into a confinement project.


# How to Set up a Confinement Project
1. Create an empty folder on your system that will store the confinement project. Input datasets will be copied to this location through the project workflow.
2. In arc

# How to Use a Confinement Project

Using a Confinement Project is easy! Most tools within the Confinement Toolbox ask for an optional Confinement Project XML. Simply specify this input, and the rest of the parameters will be 

# Components of a Confinement Project

- Project
	- Project MetaData
		- Operator
		- Region
		- Watershed
		- DateCreated
	- Inputs
		- **Definition** List of all Inputs used throughought the history of the Project, including
			- Stream Networks
			- Channel Polygons
			- Valley Bottoms
	- Realizations
		- **Definition** A realization is the first step in the Confinement Process, and consists of generating the Raw Confining State and Confining Margins for a set of inputs. 
		- Outputs
			- Raw Confining State
			- ConfiningMargins
		- Analyses
			- **Definition** An Analysis is the processing of the results of a realization. An anaysis is tied to the realization, and there can be any number of analyses of any type for any one realization.
			- Types:
				- Moving Window
				- Fixed Segments
				- Custom Segments