# Generate Confining Margins (Project Mode)

With the inputs loaded into the project, the next step is to generate the Raw Confining State and Confining Margins from the inputs. Collectively this step is called a "Confinement Realization" within the project. You may have more than one Realization stored in a Confinement Project.

For more information on what this tool is doing, refer to the documentation on the [Confining Margins Tool](ConfinementTool).

1. Make sure you have loaded at least one of each of the three inputs from step 2.
2. In ArcMap navigate to Confinement Toolbox / Confinement Tools /  Confining Margins Tool in ArcToolbox.
	1. Specify the **Project.XML** file. The Tool window will enter "Project Mode".
	2. Specify the ** Name of the new Realization**. The tool will check if there is already a realization with the specified name already stored in the project.
	3. Specify the three input datasets.
	You will need to navigate within the project folder to find these inputs. ** Do not use input files from outside of the project!**
	2. The outputs will be automatically created for you within the project.
	3. *Optional* Specify a temporary workspace.
	4. Click OK to run the tool.

![Realization Window](Images/ConfiementRealizationToolWindow.PNG)

