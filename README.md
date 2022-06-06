# Send2UETemplate
Example Send2UE Template 

Here's an extension I've been developing that I thought would be useful as a starting place for others. 
Notable features
-Three different modes for asset renaming using an Enum ("Final", "Misc" and "Test)
- Helper function to rename according to our internal standard, which puts all the assets in their own subdirectory under Game/Art/Level, e.g. "/Game/Art/L01/SM_MyAsset_AssetTag
- Debugging bools, to enable easy to read console prints and/or turn off the extension entirely and use default Send2UE functionality

This is a WIP internally, but is at a state such that it can provide inspiration or as a template to get started, it should probably not be used as-is.

The most likely starting place is to modify the 'XYZ' to your initials or name, and to modify "get_XYZ_name" to suit your folder structure
