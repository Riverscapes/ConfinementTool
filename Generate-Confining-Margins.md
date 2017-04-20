The Confining Margins tool generates both the Confining Margins (intersection of the edges of the valley bottom polygon and the active channel polygon) and transfers this information to the Stream Line Network using a near-function method. This information can then be used to calculate confinement values based on  segment lengths or moving windows along the line network. This tool can be used in either a Confinement Project or as a stand-alone tool. 

[TOC]

# Tool Usage

## Project Mode

With the inputs loaded into the project, the next step is to generate the Raw Confining State and Confining Margins from the inputs. Collectively this step is called a "Confinement Realization" within the project. You may have more than one Realization stored in a Confinement Project.

1. Make sure you have loaded at least one of each of the three inputs from step 2.

2. In ArcMap navigate to Confinement Toolbox / Confinement Tools /  Confining Margins Tool in ArcToolbox.

3. Specify the **project.rs.xml** file. The Confining Margins Tool window will enter "Project Mode".

4. Specify the **name of the new Realization**. Since projects must contain uniquely named realizations, the tool will check if there is already a realization with the specified name already stored in the project.

5. Specify the three input datasets.

    - Stream Network
    - Active Channel Polygon (i.e. "Bankfull Buffer")
    - Valley Bottom Polygon

    Note: You will need to navigate within the project folder to find these inputs. **Do not use input files from outside of the project!**

6. The outputs will be automatically created for you within the project.

7. *Optional* Specify a temporary workspace.

8. Click OK to run the tool.

![Realization Window](Images/ConfiementRealizationToolWindow.PNG)

Proceed to [Calculate Confinement by Segments](Calculating-Confinement) or [Moving Window Analysis](MovingWindowTool)

------

## Stand Alone (non-project) Mode

This tool allows you to generate Raw Confining State and Confining Margins from a set of valley bottom, channel polygon, and stream network. 

For more information on what this tool is doing, refer to the documentation on the [Confining Margins Tool](ConfinementTool).

1. Make sure you have prepared each of the three inputs.

2. In ArcMap navigate to Confinement Toolbox / Confinement Tools /  Confining Margins Tool in ArcToolbox.

3. Leave the project file parameter empty. 

4. Specify the three input datasets:
   - Stream Network
   - Active Channel Polygon (i.e. "Bankfull Buffer")
   - Valley Bottom Polygon

5. Specify the Name and Location of the output datasets:

   * Raw Confining Network
   * Confining Margins

6. *Optional* Specify a temporary workspace.

7. Click OK to run the tool.

   Proceed to [Calculate Confinement by Segments](Calculating-Confinement) or [Moving Window Analysis](MovingWindowTool)

------

# About 

## Methods 



## Outputs

### Raw Confining State
### Confining Margins