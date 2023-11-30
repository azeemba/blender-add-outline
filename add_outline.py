
bl_info = {
    "name": "Outline",
    "description": "Add NPR/cartoon outline to an object that works in eevee and cycles",
    "author": "Azeem Bande-Ali",
    "version": (0, 1),
    "blender": (3, 6),
    "category": "Material"
}

import bpy
from bpy.props import StringProperty
from bpy.types import Operator, AddonPreferences

def get_path_to_blendfile(context):
    preferences = context.preferences
    addon_prefs = preferences.addons[__name__].preferences
    return addon_prefs.source


def main(context):
    """Handles the user action to actually add outline to object"""
    material_name = "ToonOutline"
    filepath = get_path_to_blendfile(context)
    for obj in context.selected_objects:
        add_modifier(obj)
        add_outline_material(obj, filepath, material_name)


def add_modifier(obj):
    """Add the solidify modifier to object"""
    obj.modifiers.new("Outline", "SOLIDIFY")
    modifier = obj.modifiers["Outline"]
    modifier.thickness = 0.01
    modifier.use_rim = False
    modifier.offset = 1
    modifier.use_flip_normals = True
    modifier.use_quality_normals = True

    # We want the material offset to be the "next one"
    # but if there is no material at all, we assign a default one first
    if len(obj.data.materials) == 0:
        default_material = bpy.data.materials.new(name="DefaultMaterial")
        obj.data.materials.append(default_material)

    modifier.material_offset = len(obj.data.materials)


def add_outline_material(obj, filepath, material_name):
    """Loads material from filepath and appends to object"""
    outline_material = bpy.data.materials.get(material_name)
    
    if not outline_material:
        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            source_index = data_from.materials.index(material_name)
            data_to.materials.append(data_from.materials[source_index])

        outline_material = bpy.data.materials.get(material_name)

    obj.data.materials.append(outline_material)
        

class AddOutlineOperator(Operator):
    """
    Add NPR/cartoon outline to an object that works in eevee and cycles
    """
    bl_idname = "object.add_outline"
    bl_label = "Add Outline"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):
        main(context)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(AddOutlineOperator.bl_idname)

class OutlinePreferences(AddonPreferences):

    bl_idname = __name__
    source: StringProperty(
        name="Blend file",
        subtype="FILE_PATH")
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Select blend file containing ToonOutline material")
        layout.prop(self, "source")


classes = (AddOutlineOperator, OutlinePreferences)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.VIEW3D_MT_object.append(menu_func)
        
def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
 

if __name__ == "__main__":
    register()
