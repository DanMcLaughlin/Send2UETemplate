# -----------------------------------------------------------------------------
# This small extension is provided free of use to the community under a CC0 
# license as inspiration or template for your own extension. 

import bpy
from pprint import pprint
from send2ue.core.extension import ExtensionBase
from send2ue.dependencies.unreal import remote_unreal_decorator
import os
import pprint

@remote_unreal_decorator
def rename_unreal_asset(source_asset_path, destination_asset_path):
    if unreal.EditorAssetLibrary.does_asset_exist(destination_asset_path):
        unreal.EditorAssetLibrary.delete_asset(destination_asset_path)
    return unreal.EditorAssetLibrary.rename_asset(source_asset_path, destination_asset_path)

# -----------------------------------------------------------------------------
# Utility function to check the validity of an XYZ name
#

def valid_XYZ_name(self):
    """
    Check whether is a valid XYZ formatted name
    Returns multiple values
         IsValid, asset name, subfolder, name split by "_", level, whether there is a "-" in the descriptive name
    """
    if self.extensions.XYZ.Logging == True:
        print("   Before valid_XYZ_name")
        
    asset_data = self.asset_data[self.asset_id]
    path, ext = asset_data['file_path'].split('.')
    asset_path = asset_data['asset_path']
    
    ## TBD new plugin release which gives us the object name (James)
    ## Sans that figure it out from the file path
    ## splits = self.asset_data[self.asset_id]['asset_name'].split('_')
    asset_name = os.path.split(asset_path)[1]   
    asset_subfolder = asset_path.split('/')[-2]
    splits = asset_name.split('_')
   
    
    if len(splits) > 1: # Follows the XYZ naming 
        level = splits[-1][0:3]
        if level[0:1] == 'L' or level[0:1] == 'M':
            if len(splits) == 4: # Special case of a "SM_Foo-Bar_LXXXXXX" type name
                if self.extensions.XYZ.Logging == True:
                    print("      Found XYZ dash formatted name: " + asset_name)
                    print("   After valid_XYZ_name")
                return True, asset_name, asset_subfolder, splits, level, True
            else:
                if self.extensions.XYZ.Logging == True:
                    print("      Found XYZ formatted name: " + asset_name)
                    print("   After valid_XYZ_name")
                    return True, asset_name, asset_subfolder, splits, level, False
        else:
            if self.extensions.XYZ.Logging == True:
                print("      A split up name but doesn't have the tag formatting: " + asset_name)
                print("   After valid_XYZ_name")
            return False, asset_name, asset_subfolder, splits, level, False
    else:
        if self.extensions.XYZ.Logging == True:
            print("      Name has no _ seperators: " + asset_name)
            print("   After valid_XYZ_name")
            return False, asset_name, "", "", "", False    

        
    if self.extensions.XYZ.Logging == True:
        print("   After valid_XYZ_name")
        
    return False, asset_name, asset_subfolder, splits, level, False
           

# -----------------------------------------------------------------------------
# Utility function to get the XYZ name
#
def get_XYZ_name(self):
    """
    Only works during pre_asset_export/pre_animation_export I think
    Determine the name and Content path for an asset
    Returns a tuple path, asset_name
    A properly formatted name is of the form, e.g. 
        
        SM_Boss_L0123456789
            or
        SM_Boss-Manny_L0123456789
        
        Prefix_DescriptiveName-DescriptiveVariation_LABCDEFGHIJ
        
        The last split is the 'tag', which is a unique ID for the asset, prefixed by 'L' (Level) or 'M' (Map), the rest of the tag
        indicates other information by two digit groups
        L01 23 45 67 89 means
           Level     01   # The level the asset first appears in
           Scene     23   # The scene/location the asset first appears in
           Lot       45   # The Lot, e.g. buildings = 01, characters = 02, etc, 
           Asset     67   # Something specific to the asset
           Variation 89   # An individual asset may have variations such as skins
        
    XYZ subdirectory format is
        Art/LXY/FullAssetName/FullAssetName                                For assets that follow the AB_Name_Tag format
        Art/LXY/FullAssetName/EnclosingFolder/FullAssetName/FullAssetName  For assets that follow the AB_Name_Tag format and are within a subdirectory
        Art/Misc/FullAssetName                                             For assets which have a prefix but no tag suffix
        Art/Misc/EnclosingFolder/FullAssetName                             For assets which have a prefix but no tag suffix        
        Art/Test/FullAssetName                                             For assets that don't follow the XYZ format
        Art/Test/EnclosingFolder/FullAssetName                             For assets that don't follow the XYZ format in an enclosing subfolder

        For this to work the "use collections and folders" must be enabled, and only one level of subdirectory is supported

    :param PropertyGroup self: The scene property group that contains all the addon properties.
    """
    pp = pprint.PrettyPrinter(indent=3)
    
    asset_data = self.asset_data[self.asset_id]

    if self.extensions.XYZ.Logging == True:
        print("Before get_XYZ_name")
        
    valid, asset_name, asset_subfolder, splits, level, variation = valid_XYZ_name(self)    
    
    if self.extensions.XYZ.Logging == True:
        if asset_subfolder == None:
            print("   No asset subfolder found")
        else:
            print("   Asset subfolder: " + asset_subfolder )
        if asset_name == None:
            print("   No asset_name found")
        else: 
            print("   Asset Name: " + asset_name )     
    
    if self.extensions.XYZ.Logging == True:
        if splits == None:
            print("   Name has no underscores (_)")
        else:
            print("   Splits: ", end='')
            pp.pprint(splits)
        
    if self.extensions.XYZ.Type == 'DONE':
        if valid == True:
            if variation == True: # Variation type, put it in the same as the base 
                if self.extensions.XYZ.Logging == True:
                    print("      Found XYZ dash formatted Finished asset: " + asset_name)
                path = '/Game/Art/' + level + "/" + splits[0] + "_" + splits[1] + "_" + splits[3]
            else:                # Normal case of "SM_Foo_LXXXXX"
                if self.extensions.XYZ.Logging == True:
                    print("      Found XYZ formatted Finished asset: " + asset_name)
                path = '/Game/Art/' + level + "/" + asset_name 
        else:
            # The name wasn't formatted correctly, but is supposed to be "Finished" - put it in Miscellanous
            print("      Found improperly formatted asset name: " + asset_name)
            print("      Asset goes into Misc")
            path = '/Game/' + self.extensions.XYZ.ArtFolder + '/Misc'
    
    elif self.extensions.XYZ.Type == 'MISC':
        if self.extensions.XYZ.Logging == True:
            print("      Found Misc asset: " + asset_name)
        path = '/Game/' + self.extensions.XYZ.ArtFolder + '/Misc' 
    
    elif self.extensions.XYZ.Type == 'TEST':
        if self.extensions.XYZ.Logging == True:
            print("      Found Test asset: " + asset_name)
        path = '/Game/' + self.extensions.XYZ.ArtFolder + '/Test'
    
    else:
        print("Error - this should not occur")
    
    if asset_subfolder != "Export" and asset_subfolder != "":
        path = path + "/" + asset_subfolder   
        if self.extensions.XYZ.Logging == True:
            print("   Using an Asset subfolder: " + asset_subfolder + " Full path: " + path)

    if self.extensions.XYZ.Logging == True:
        print("   path: " + path)
        print("   asset_name: " + asset_name)
        print("After get_XYZ_name")
        print()
        
    return path, asset_name    

# -----------------------------------------------------------------------------
# Main class
#

class XYZExtension(ExtensionBase):
    name = 'XYZ'
    
    asset_type = [
        ("DONE", "Finished", "Finished asset, XYZ format \"SM_Foo-Bar_LABCDEFGHIJ\"", 0), 
        ("MISC", "Misc", "Miscellaneous file, not in XYZ format", 1),
        ("TEST", "Test", "Test file, not for inclusion in the game", 2),
    ]
    Type: bpy.props.EnumProperty(items = asset_type)
    
    Enable: bpy.props.BoolProperty(name = 'Enable extension', description='Enable XYZ Extension', default = True)
    Logging: bpy.props.BoolProperty(name = 'Logging', description='Enable console logging', default = False)
    ArtFolder: bpy.props.StringProperty(default = 'Art')
    AnimationFolder: bpy.props.StringProperty(default = 'Animation')
    NestedAnimation: bpy.props.BoolProperty(name = 'Animation subfolder', description='Place the animation folder as a subfolder of the asset folder, e.g. \"Art/Asset/Animation\"', default = True)
    
    # -----------------------------------------------------------------------------
    # Properties
    #
    def draw_validations(self, dialog, layout):
        """
        Can be overridden to draw an interface for the extension under the validations tab.

        :param Send2UeSceneProperties self: The scene property group that contains all the addon properties.
        :param Send2UnrealDialog dialog: The dialog class.
        :param bpy.types.UILayout layout: The extension layout area.
        """
        row = layout.row()
        row.prop(self.extensions.XYZ, 'Type', text = "Asset status")   
        row = layout.row()
        row.prop(self.extensions.XYZ, 'ArtFolder', text = "Art folder")
        row = layout.row()
        row.prop(self.extensions.XYZ, 'AnimationFolder', text = "Animation folder")
        row = layout.row()        
        row.prop(self.extensions.XYZ, 'NestedAnimation', text = "Nested animation folder")
        row = layout.row()
        row.label(text = 'Debugging: ')
        row.prop(self.extensions.XYZ, 'Enable', text = "Enable extension")
        row.prop(self.extensions.XYZ, 'Logging', text = "Enable logging")


    # -----------------------------------------------------------------------------
    # General pre ops
    #
    def pre_operation(self):
        """
        Defines the pre operation logic that will be run before the operation.

        :param Send2UeSceneProperties self: The scene property group that contains all the addon properties.
        """
        if self.extensions.XYZ.Enable == False:
            return;
            
        pp = pprint.PrettyPrinter(indent=3)
        
        if self.extensions.XYZ.Logging == True:
            print()
            print("****XYZ Extension***")
            print('Before pre_operation')
            pp.pprint(self)
            
        # Set these initially - no this causes issues
        #self.unreal_mesh_folder_path = '/Game/' + self.extensions.XYZ.ArtFolder
        
        #if self.extensions.XYZ.NestedAnimation == True:
        #    self.unreal_animation_folder_path = self.unreal_mesh_folder_path + self.extensions.XYZ.AnimationFolder
        #else:
        #    self.unreal_animation_folder_path = self.unreal_mesh_folder_path
        
        
        if self.extensions.XYZ.Logging == True:
            print("   Mesh folder path: " + self.unreal_mesh_folder_path)
            print("   Animation folder path: " + self.unreal_animation_folder_path);
            print('After pre_operation')
            print()
            
            
    # -----------------------------------------------------------------------------
    # General pre validations
    #
    def pre_validations(self):
        """
        Defines the pre validation logic that will be an injected operation.

        :param Send2UeSceneProperties self: The scene property group that contains all the addon properties.
        """
        if self.extensions.XYZ.Enable == False:
            return;   
            
        if self.extensions.XYZ.Logging == True:
            print('Before pre_validations')
            
        pass_accumulator = True
        
        pp = pprint.PrettyPrinter(indent=3)
        if self.extensions.XYZ.Logging == True:
            print("   Asset Data:")
            pp.pprint(self.asset_data)
        
        # No asset validations can occur here, this is only for global validations
        # asset_data = self.asset_data[self.asset_id]
        # valid, asset_name, asset_subfolder, splits, level, variation = valid_XYZ_name(self)        
        # if self.extensions.XYZ.Type == 'DONE':
            # if valid == True:
                # if self.extensions.XYZ.Logging == True:
                    # print("   Pass: Finished asset has proper name structure")
            # else:
                # print("   Fail: Finished asset doesn't have valid XYZ name structure")
                # pp.pprint(asset_data)
                # pass_accumulator = False

        self.validations_passed = pass_accumulator
        
        if self.extensions.XYZ.Logging == True:
            print('After pre_validations')
            print()
            


    # -----------------------------------------------------------------------------
    # Pre export of mesh types
    #
    def pre_mesh_export(self):
        """
        :param PropertyGroup self: The scene property group that contains all the addon properties.
        """
        if self.extensions.XYZ.Enable == False:
            return;      
            
        pp = pprint.PrettyPrinter(indent=6)
        asset_data = self.asset_data[self.asset_id]
        path, asset_name = get_XYZ_name(self)
        
        if self.extensions.XYZ.Logging == True:
            print("Before pre_mesh_export")
            print("   Initial asset_data: ")            
            pp.pprint(asset_data)

             
        asset_data['asset_folder'] = path         
        asset_data['asset_path'] = path + "/" + asset_name 
        
        # Hack or feature? Store the determined mesh location in these
        # places so that pre_animation_export gets some useful information
        # In other words set these up for the animation 
        
        self.unreal_mesh_folder_path = path
        
        if self.extensions.XYZ.NestedAnimation == True:
            self.unreal_animation_folder_path = path + "/" + self.extensions.XYZ.AnimationFolder
        else:
            # Note this needs to be fully qualified, e.g. "Game/"
            self.unreal_animation_folder_path = path
        
        if self.extensions.XYZ.Logging == True:
            print("   Modified asset_data: ")         
            pp.pprint(asset_data)
            print("After pre_mesh_export")
            print()
            
            

    # -----------------------------------------------------------------------------
    # Pre export of animation types
    #
    def pre_animation_export(self):
        """
        Defines the pre animation export logic that will be an injected operation.

        :param PropertyGroup self: The scene property group that contains all the addon properties.
        """
        #print('Before Animation Export')
        if self.extensions.XYZ.Enable == False:
            return;        

        pp = pprint.PrettyPrinter(indent=6)
        asset_data = self.asset_data[self.asset_id]
        #path, asset_name = get_XYZ_name(self)
        
        # Already set up previously by the pre_mesh_export
        # Note however this doesn't presently support an animation export only 
        path = self.unreal_animation_folder_path
        
        if self.extensions.XYZ.Logging == True:
            print("Before pre_animation_export")
            #print("   path: " + path + ", asset_name: " + asset_name)
            print("   Initial asset_data: ")
            pp.pprint(asset_data)        
  
        # The name has already been set up properly by the mesh export, by using self.unreal_animation_folder_path
        
        if self.extensions.XYZ.Logging == True:
            print("   Modified asset_data:")        
            pp.pprint(asset_data)        
            print("After pre_animation_export")
            print()


    # -----------------------------------------------------------------------------
    #
    #
    def post_import(self):
        """
        Defines the post import logic that will be an injected operation.

        :param Send2UeSceneProperties self: The scene property group that contains all the addon properties.
        """
        if self.extensions.XYZ.Enable == False:
            return;
            
        if self.extensions.XYZ.Logging == True:
            print('Before post_import')
            
        #asset_path = self.asset_data[self.asset_id]['asset_path']
        #rename_unreal_asset(asset_path, f'{asset_path}_renamed_again')
        
        if self.extensions.XYZ.Logging == True:
            print('After post_import')
            print()
            


    # -----------------------------------------------------------------------------
    #
    #
    def post_operation(self):
        """
        Defines the post operation logic that will be run after the operation.
        """
        if self.extensions.XYZ.Enable == False:
            return;      
            
        if self.extensions.XYZ.Logging == True:
            print('Before post_operation')
            
        if self.extensions.XYZ.Logging == True:
            print('After post_operation')
            print("****XYZ Extension***")
       


# End of file XYZ.py
# -----------------------------------------------------------------------------