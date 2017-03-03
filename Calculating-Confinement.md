A confinement analysis must be associated with one and only one "Realization." If a new realization is created within a project, new analyses must be generated for the new realization. ** A Project will store all realizations and analyses. At this point, there is no support for deleting a realization or analysis from a project.**

An Analysis tool will calculate Confinement  using one of the three tools in the Analysis toolset. Each are described below.

### Custom Segments



### Moving Window
This section describes how to generate a Moving Window Analysis within a Project. For more information on what a Moving Window Analysis is, see [Moving Window Tool](MovingWindowTool).

1. Make sure you have generated at least one Confinement Realization.
2. In ArcMap navigate to Confinement Toolbox / Confinement Tools / Analysis / Moving Window Confinement Tool in ArcToolbox.
	1. Specify the **Project.XML** file. The Tool window will enter "Project Mode".
	2. From the Dropdown, select the Realization you want to base your analysis on.
		1. The Tool will automatically use the correct Stream Network Input from the specified Realization.
	2. Specify a **Dissolve** Field that is used to make continuous streaches of the stream. For Example, GNAT uses a "Stream Branch ID" system. 
		> *** There is currently a bug in the workflow that does not retain existing fields in the original input stream network. This will be fixed for the next release of the confinement tool.***
	4. The tool will attempt to find the correct confinement and Constriction fields.
	5.  Specify a seed Distance, and specify the window size(s) you want to use.
	6.  In "Project Mode", the output workspace is managed for you, but you make specify a Temporary workspace.
	7.  Click OK to run the tool.

![](Images/MovingWindowToolWindow.PNG)



