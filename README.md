# Send2UETemplate
Example Send2UE Template 

Here's an extension I've been developing that I thought would be useful as a starting place for others. 
Notable features:
- Three different modes for asset renaming using an Enum ("Final", "Misc" and "Test) available in extension settings
- Helper function to rename according to our internal standard, which puts all the assets in their own subdirectory under Game/Art/Level, e.g. "/Game/Art/L01/SM_MyAsset_AssetTag
- Debugging tools, to enable easy to read console prints and/or turn off the extension entirely and use default Send2UE functionality, all settable 

This is a WIP internally, but is at a state such that it can provide inspiration or as a template to get started, it should probably not be used as-is.

The most likely starting place is to modify the 'XYZ' to your initials or name, and to modify "get_XYZ_name" to suit your folder structure. 

If anybody knows how to make the get_XYZ_name function a part of the XYZExtension extension class let me know, despite a bunch of experimentation I wasn't able to get that to work so had to stick it up outside. Not a big deal either way but I like things to be tidy, and class helper functions would be better. 

Example debugging output. Developing an extension can be difficult but having good output like this is really helpful. 

```
****XYZ Extension***
Before pre_operation
After pre_operation

Before pre_validations
After pre_validations

Before get_XYZ_name
   Asset subfolder:
   Asset Name: TheBossMesh
   Splits: ['TheBossMesh']
      Attempted formatted but found unformatted misc asset: TheBossMesh
   path: /Game/Art/Misc
   asset_name: TheBossMesh
After get_XYZ_name

Before pre_mesh_export
   Initial asset_data:
{     'asset_folder': '/',
      'asset_path': '/TheBossMesh',
      'asset_type': 'MESH',
      'file_path': 'C:\\SomeDirectory\\TheBossMesh.fbx',
      'import_mesh': True,
      'lods': None,
      'skeletal_mesh': False,
      'skeleton_asset_path': '',
      'sockets': {}}
   Modified asset_data:
{     'asset_folder': '/Game/Art/Misc',
      'asset_path': '/Game/Art/Misc/TheBossMesh',
      'asset_type': 'MESH',
      'file_path': 'C:\\SomeDirectory\\TheBossMesh.fbx',
      'import_mesh': True,
      'lods': None,
      'skeletal_mesh': False,
      'skeleton_asset_path': '',
      'sockets': {}}
After pre_mesh_export
```
