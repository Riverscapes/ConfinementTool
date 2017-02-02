## Load Input Datasets to Project

1. In order to generate confinement within a project, you must first load the three input files to the project.
2. In ArcMap navigate to Confinement Toolbox / Confinement Project Management /  Load Input Datasets in ArcToolbox.
	1. Specify the Project.xml file created in step 1.
	2. Specify the following three inputs to the project:
		* Stream Network
		* Channel/Bankfull Buffer Polygon
		* Valley Bottom Polygon
	> These inputs may be of any GIS vector format (as recognized by ArcGIS), however when they are imported into the project, they will stored as Shapefiles (.shp). This should not have any affect on the data other than limiting the field names to 10 characters. 	
	2. Click OK to import the inputs into the project.
	
![Add Inputs Tool](Images/AddInputsToProjectToolWindow.PNG)

3. The Project.xml file will be updated to include these inputs, and they will be stored appropriately in the Project folder structure.

** At this point in the project, do not move any files within the project folder. Doing so could cause the project to become corrupt. **	

