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
# Utility function to get the XYZ name
#
def get_XYZ_name(self):
    """
    Only works during pre_asset_export/pre_animation_export I think
    Determine the name and Content path for an asset
    Returns a tuple path, asset_name
    
    XYZ format is 
        Art/LXY/FullAssetName/FullAssetName                                For assets that follow the AB_Name_Tag format
        Art/LXY/FullAssetName/EnclosingFolder/FullAssetName/FullAssetName  For assets that follow the AB_Name_Tag format and are within a subdirectory
        Art/Misc/FullAssetName                                             For assets which have a prefix but no tag suffix
        Art/Misc/EnclosingFolder/FullAssetName                             For assets which have a prefix but no tag suffix        
        Art/Test/FullAssetName                                             For assets that don't follow the XYZ format
        Art/Test/EnclosingFolder/FullAssetName                             For assets that don't follow the XYZ format in an enclosing subfolder

        For this to work the "use collections and folders" must be enabled, and only one level of subdirectory is supported

    :param PropertyGroup self: The scene property group that contains all the addon properties.
    """
    # pprint(self)
    pp = pprint.PrettyPrinter(indent=3)
    
    asset_data = self.asset_data[self.asset_id]
    path, ext = asset_data['file_path'].split('.')
    asset_path = asset_data['asset_path']
    
    if self.extensions.XYZ.Logging == True:
        print("Before get_XYZ_name")
        
    ## TBD new release
    ## splits = self.asset_data[self.asset_id]['asset_name'].split('_')
    asset_name = os.path.split(asset_path)[1]   
    asset_subfolder = asset_path.split('/')[-2]
    
    if self.extensions.XYZ.Logging == True:
        print("   Asset subfolder: " + asset_subfolder )
        print("   Asset Name: " + asset_name )     
    
    splits = asset_name.split('_')
    
    if self.extensions.XYZ.Logging == True:
        print("   Splits: ", end='')
        pp.pprint(splits)
        
    if self.extensions.XYZ.Type == 'DONE':
        if len(splits) > 1: # Follows the XYZ naming 
            level = splits[-1][0:3]
            if level[0:1] == 'L' or level[0:1] == 'M':
                if len(splits) == 4: # Special case of a "SM_Foo-Bar_LXXXXXX" type name
                    if self.extensions.XYZ.Logging == True:
                        print("      Found XYZ dash formatted name: " + asset_name)
                    path = '/Game/Art/' + level + "/" + splits[0] + "_" + splits[1] + "_" + splits[3]
                else:                # Regular case of "SM_Foo_LXXXXX"
                    if self.extensions.XYZ.Logging == True:
                        print("      Found XYZ formatted name: " + asset_name)
                    path = '/Game/Art/' + level + "/" + asset_name 
            else:
                if self.extensions.XYZ.Logging == True:
                    print("      Found unleveled Misc asset: " + asset_name)
                path = '/Game/Art/Misc'    
        else:
            if self.extensions.XYZ.Logging == True:
                print("      Attempted formatted but found unformatted Misc asset: " + asset_name)
            path = '/Game/Art/Misc'
            
    elif self.extensions.XYZ.Type == 'MISC':
        if self.extensions.XYZ.Logging == True:
            print("      Found Misc asset: " + asset_name)
        path = '/Game/Art/Misc'
        
    elif self.extensions.XYZ.Type == 'TEST':
        if self.extensions.XYZ.Logging == True:
            print("      Found Test asset: " + asset_name)
        path = '/Game/Art/Test'
    
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
    
    Enable: bpy.props.BoolProperty(name = 'Enable', description='Enable XYZ Extension', default = True)
    Logging: bpy.props.BoolProperty(name = 'Logging', description='Enable console logging', default = False)
    
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
        row.prop(self.extensions.XYZ, 'Type')
        row = layout.row()
        row.label(text = 'Debugging: ')
        row.prop(self.extensions.XYZ, 'Enable')
        row.prop(self.extensions.XYZ, 'Logging')


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
            
        if self.extensions.XYZ.Logging == True:
            print()
            print("****XYZ Extension***")
            print('Before pre_operation')
            
        # Set these properly - the addon won't work with them anything else. It appears
        # The rest of the addon does some magic additions 
        self.unreal_mesh_folder_path = '/'
        self.unreal_animation_folder_path = '/'
        
        if self.extensions.XYZ.Logging == True:
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
            
        # Setting this to False will terminate execution in the validation phase
        #if self.extensions.XYZ.hello_property != 'Hello world':
        #    self.validations_passed = False
        
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
        path, asset_name = get_XYZ_name(self)
        
        if self.extensions.XYZ.Logging == True:
            print("Before pre_animation_export")
            print("   Initial asset_data: ")
            pp.pprint(asset_data)        
  
        #path = path + "/" + "Animation" 
        
        #skeleton_asset_path = asset_data.get('skeleton_asset_path').replace('_Skeleton', '')
        #self.asset_data[self.asset_id]['skeleton_asset_path'] = f'{skeleton_asset_path}_added_this_Skeleton'
        
        asset_data['asset_folder'] = path  
        asset_data['skeleton_asset_path'] = path + "/" + asset_name 
        
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