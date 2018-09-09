# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Tween Objects",
    "author": "Duy Kevin Nguyen <cpau3D@gmail.com>",
    "version": (0, 0, 1),
    "blender": (2, 79),
    "location": "Tool bar > Animation tab > Tween",
    "description": "Allows to blend keyframes for in between",
    "warning": "",
    "wiki_url": "",
    "category": "Animation",
}

import bpy
from bpy.types import (
        Operator,
        Panel,
        AddonPreferences,
        )
from bpy.props import (
        IntProperty,
        FloatProperty,
        BoolProperty,
        StringProperty,
        CollectionProperty,
        )

# Utility functions

def refresh_ui_keyframes():
    try:
        bpy.context.scene.frame_set(bpy.context.scene.frame_current)
        for area in bpy.context.screen.areas:
            if area.type in ('TIMELINE', 'GRAPH_EDITOR', 'DOPESHEET_EDITOR', 'VIEW_3D'):
                area.tag_redraw()
        bpy.context.scene.update()
    except:
        pass
    
def tween_key(self, context):
    # TODO: Clean code duplication
    current_frame = bpy.context.scene.frame_current
    for ob in bpy.context.selected_objects:
        if ob.type in ['MESH', 'ARMATURE'] and ob.animation_data:
            if ob.type in ['MESH']:
                for fc in ob.animation_data.action.fcurves:
                    frame_before = 0
                    frame_after = 9999
                    before = 0
                    after = 0
                    update_frame = False             
                    for key in fc.keyframe_points:
                        if key.co[0] < current_frame:
                            if key.co[0] > frame_before:
                                frame_before = key.co[0]
                                before = key.co[1]
                        elif key.co[0] > current_frame:
                            if key.co[0] < frame_after:
                                frame_after = key.co[0]
                                after = key.co[1]
                        if key.co[0] == current_frame or not context.scene.on_keyframes:
                            update_frame = True
                    if update_frame:
                        fc.keyframe_points.insert(current_frame, before * (1 - context.scene.tween) + after * context.scene.tween)
                        
            if ob.type in ['ARMATURE']:
                bone_names = [b.name for b in bpy.context.selected_pose_bones]
                for fc in ob.animation_data.action.fcurves:
                    if fc.data_path.split('"')[1] in bone_names:
                        frame_before = 0
                        frame_after = 9999
                        before = 0
                        after = 0
                        update_frame = False             
                        for key in fc.keyframe_points:
                            if key.co[0] < current_frame:
                                if key.co[0] > frame_before:
                                    frame_before = key.co[0]
                                    before = key.co[1]
                            elif key.co[0] > current_frame:
                                if key.co[0] < frame_after:
                                    frame_after = key.co[0]
                                    after = key.co[1]
                            if key.co[0] == current_frame or not context.scene.on_keyframes:
                                update_frame = True
                        if update_frame:
                            fc.keyframe_points.insert(current_frame, before * (1 - context.scene.tween) + after * context.scene.tween)
                    

    refresh_ui_keyframes()
          
# Operators

class Tween(bpy.types.Operator):
    """Tween an object with the mouse"""
    bl_idname = "tween.tween_key"
    bl_label = "Tween"
    bl_description = "Tween between two keys"
    bl_options = {"REGISTER", "UNDO"}
    
    first_mouse_x = IntProperty()
    init_tween = FloatProperty()
    tween = FloatProperty()
    help_string = StringProperty()
    
    @classmethod
    def poll(cls, context):
        if context.active_object and context.active_object.type in {'MESH', 'ARMATURE'}:
            return context.active_object.type

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            # TODO : improve screen size and shift
            # Precision mode
            if event.shift:
                rapport = 1600
            else:
                rapport = 800
            delta = (self.first_mouse_x - event.mouse_x) / rapport
            self.tween = max(min(self.init_tween - delta, 1.0), 0.0)
            # Snap mode
            if event.ctrl:
                self.tween = int(self.tween * 10)/10
            context.scene.tween = self.tween
            context.area.header_text_set(
                        "Tween: %.4f" % self.tween + self.help_string)
            tween_key(self.tween, context)

        elif event.type == 'LEFTMOUSE':
            context.scene.tween = self.tween
            context.object.saved_tween = str(context.scene.frame_current) + ":" + str(self.tween)
            context.area.header_text_set()
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.area.header_text_set()
            self.tween = self.init_tween
            context.scene.tween = self.init_tween
            context.object.saved_tween = str(context.scene.frame_current) + ":" + str(self.init_tween)
            tween_key(self.init_tween, context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        if context.object:
            self.help_string  = ', Confirm: (Enter/LMB)'
            self.help_string += ', Cancel: (Esc/RMB)'
            self.first_mouse_x = event.mouse_x
            if context.object.get('saved_tween') is None:
                print("None")
                context.object.saved_tween = str(context.scene.frame_current) + ":0.5"
                context.scene.tween = 0.5
            else:
                if int(context.object.saved_tween.split(":")[0]) == context.scene.frame_current:
                    context.scene.tween = float(context.object.saved_tween.split(":")[1])
                else:
                    context.scene.tween = 0.5
            self.init_tween = context.scene.tween
            context.scene.tween_frame = context.scene.frame_current
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}

# GUI (Panel)

class VIEW3D_PT_Tween(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Animation"
    bl_label = 'Tween'

    @classmethod
    def poll(self, context):
        if context.active_object and context.active_object.type in {'MESH', 'ARMATURE'}:
            return context.active_object.type

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, "on_keyframes")
        row = layout.row()
        row.prop(context.scene, "tween", slider=True)

addon_keymaps = []

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.tween = FloatProperty(name="Tween", default=0.0, min=0, max=1.0, update=tween_key)
    bpy.types.Object.saved_tween = StringProperty(name="Saved Tween")
    bpy.types.Scene.on_keyframes = BoolProperty(name="Only on keyframes", default=False)
    bpy.types.Scene.tween_frame = IntProperty(name="Tween frame", default=0)
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    km.keymap_items.new(
        Tween.bl_idname,
        'W', 'PRESS', alt=True, shift=True)
    addon_keymaps.append(km)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.tween
    del bpy.types.Object.saved_tween
    del bpy.types.Scene.on_keyframes 
    del bpy.types.Scene.tween_frame
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
