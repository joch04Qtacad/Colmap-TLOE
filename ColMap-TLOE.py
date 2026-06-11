"""
ColMap-TLOE
Addon Blender pour normaliser un import COLMAP (timeline, orientation, échelle)

Copyright (C) 2026 joch04Qtacad

This file is part of Colmap-TLOE and is licensed under the GNU General Public License v3.
See the LICENSE file at the project root for details: https://www.gnu.org/licenses/gpl-3.0
"""

# B5 - mise à l'échelle, orientation et timeline
# pour Blender Photogrammetry Importer

bl_info = {
    "name": "ColmapTLOE",
    "author": "Joch04",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "Vue 3D > N > ColmapTLOE",
    "description": "Outils de timeline, orientation et mise à l'échelle",
    "category": "3D View",
}

import math

import bpy
from mathutils import Matrix


# =============================================
# TIMELINE : Gestion des caméras
# =============================================


class TIMELINE_OT_link_cameras(bpy.types.Operator):
    bl_idname = "timeline_tools.link_cameras"
    bl_label = "Lier caméras à la timeline"
    bl_description = "Crée des markers pour naviguer entre les caméras avec les flèches"

    def execute(self, context):
        cameras = [obj for obj in context.scene.objects if obj.type == "CAMERA"]
        if not cameras:
            self.report({"ERROR"}, "Aucune caméra trouvée")
            return {"CANCELLED"}

        cameras.sort(key=lambda x: x.name)
        scene = context.scene
        scene.frame_start = 1
        scene.frame_end = len(cameras)

        # Supprimer les markers existants
        for marker in list(scene.timeline_markers):
            scene.timeline_markers.remove(marker)

        # Créer un marker par caméra
        for i, cam in enumerate(cameras, start=1):
            marker = scene.timeline_markers.new(name=cam.name, frame=i)
            marker.camera = cam

        # Activer le verrouillage caméra pour les vues 3D
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        space.lock_camera = True

        self.report({"INFO"}, f"{len(cameras)} caméra(s) liée(s) aux frames 1-{len(cameras)}")
        return {"FINISHED"}


class TIMELINE_OT_set_focal(bpy.types.Operator):
    bl_idname = "timeline_tools.set_focal"
    bl_label = "Appliquer focale à toutes les caméras"
    bl_description = "Applique la même focale à toutes les caméras de la scène"

    focal_length: bpy.props.FloatProperty(
        name="Focale (mm)",
        description="Focale en millimètres",
        default=15.3,
        min=1.0,
        max=300.0,
        step=0.1,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "focal_length")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        cameras = [obj for obj in context.scene.objects if obj.type == "CAMERA"]
        if not cameras:
            self.report({"ERROR"}, "Aucune caméra trouvée")
            return {"CANCELLED"}

        for cam in cameras:
            cam.data.lens = self.focal_length

        self.report({"INFO"}, f"Focale {self.focal_length}mm appliquée à {len(cameras)} caméra(s)")
        return {"FINISHED"}


# =============================================
# ÉCHELLE : Opérateurs
# =============================================


class SCALE_OT_create_markers(bpy.types.Operator):
    bl_idname = "scale_tools.create_markers"
    bl_label = "Créer les repères d'échelle"

    def execute(self, context):
        for name in ("ScaleRef_A", "ScaleRef_B"):
            obj = bpy.data.objects.get(name)
            if obj:
                bpy.data.objects.remove(obj, do_unlink=True)

        bpy.ops.object.empty_add(type="SPHERE", location=(0, 0.5, 0))
        empty_a = context.active_object
        empty_a.name = "ScaleRef_A"
        empty_a.empty_display_size = 0.5
        empty_a.show_name = True

        bpy.ops.object.empty_add(type="SPHERE", location=(0, 1.0, 0))
        empty_b = context.active_object
        empty_b.name = "ScaleRef_B"
        empty_b.empty_display_size = 0.5
        empty_b.show_name = True

        self.report({"INFO"}, "Repères créés. Déplacez-les puis lancez 'Appliquer l'échelle'.")
        return {"FINISHED"}


class SCALE_OT_apply_scale(bpy.types.Operator):
    bl_idname = "scale_tools.apply_scale"
    bl_label = "Appliquer l'échelle"

    real_distance: bpy.props.FloatProperty(
        name="Distance réelle",
        description="Distance réelle entre les deux repères",
        default=1.0,
        min=0.0001,
    )

    def invoke(self, context, event):
        a = bpy.data.objects.get("ScaleRef_A")
        b = bpy.data.objects.get("ScaleRef_B")
        if not a or not b:
            self.report({"ERROR"}, "Repères introuvables. Créez-les d'abord.")
            return {"CANCELLED"}
        self.measured_distance = (a.location - b.location).length
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text=f"Distance mesurée : {self.measured_distance:.6f}")
        layout.prop(self, "real_distance")

    def execute(self, context):
        if getattr(self, "measured_distance", 0) <= 0:
            self.report({"ERROR"}, "Distance mesurée invalide.")
            return {"CANCELLED"}

        scale_factor = self.real_distance / self.measured_distance
        bpy.ops.object.select_all(action="DESELECT")

        for obj in bpy.data.objects:
            if obj.name not in {"ScaleRef_A", "ScaleRef_B", "OriginRef", "XRef", "YRef"}:
                obj.select_set(True)

        selected = context.selected_objects
        if selected:
            context.view_layer.objects.active = selected[0]
        context.scene.tool_settings.transform_pivot_point = "CURSOR"
        bpy.ops.transform.resize(value=(scale_factor, scale_factor, scale_factor))

        self.report({"INFO"}, f"Échelle appliquée : x{scale_factor:.6f}")
        return {"FINISHED"}


# =============================================
# ORIENTATION : Opérateurs
# =============================================


class ORIENT_OT_create_origin_refs(bpy.types.Operator):
    bl_idname = "orient_tools.create_origin_refs"
    bl_label = "Créer repères d'origine (00, X, Y)"

    def execute(self, context):
        for name in ("OriginRef", "XRef", "YRef"):
            obj = bpy.data.objects.get(name)
            if obj:
                bpy.data.objects.remove(obj, do_unlink=True)

        bpy.ops.object.empty_add(type="SPHERE", location=(0, 0, 0))
        origin = context.active_object
        origin.name = "OriginRef"
        origin.empty_display_size = 0.5
        origin.show_name = True

        bpy.ops.object.empty_add(type="SPHERE", location=(1, 0, 0))
        x_ref = context.active_object
        x_ref.name = "XRef"
        x_ref.empty_display_size = 0.5
        x_ref.show_name = True

        bpy.ops.object.empty_add(type="SPHERE", location=(0, 1, 0))
        y_ref = context.active_object
        y_ref.name = "YRef"
        y_ref.empty_display_size = 0.5
        y_ref.show_name = True

        self.report({"INFO"}, "Repères créés. Déplacez OriginRef, XRef et YRef sur la scène.")
        return {"FINISHED"}


class ORIENT_OT_apply_orientation(bpy.types.Operator):
    bl_idname = "orient_tools.apply_orientation"
    bl_label = "Appliquer orientation (Z=0)"

    def execute(self, context):
        origin = bpy.data.objects.get("OriginRef")
        x_ref = bpy.data.objects.get("XRef")
        y_ref = bpy.data.objects.get("YRef")

        if not origin or not x_ref or not y_ref:
            self.report({"ERROR"}, "Repères introuvables. Créez-les d'abord.")
            return {"CANCELLED"}

        x_vec = (x_ref.location - origin.location).normalized()
        y_vec = (y_ref.location - origin.location).normalized()
        z_vec = x_vec.cross(y_vec).normalized()

        rot_mat = Matrix([
            [x_vec.x, y_vec.x, z_vec.x, 0],
            [x_vec.y, y_vec.y, z_vec.y, 0],
            [x_vec.z, y_vec.z, z_vec.z, 0],
            [0, 0, 0, 1],
        ]).transposed()

        trans_mat = Matrix.Translation(-origin.location)
        final_mat = rot_mat @ trans_mat

        excluded = {"ScaleRef_A", "ScaleRef_B", "OriginRef", "XRef", "YRef"}
        for obj in bpy.data.objects:
            if obj.name not in excluded:
                obj.matrix_world = final_mat @ obj.matrix_world

        self.report({"INFO"}, "Orientation appliquée : sol sur Z=0, origine sur OriginRef")
        return {"FINISHED"}


class ORIENT_OT_rotate_180_x(bpy.types.Operator):
    bl_idname = "orient_tools.rotate_180_x"
    bl_label = "Rotation 180° autour de X"

    def execute(self, context):
        rot_mat = Matrix.Rotation(math.pi, 4, "X")
        excluded = {"ScaleRef_A", "ScaleRef_B", "OriginRef", "XRef", "YRef"}
        for obj in bpy.data.objects:
            if obj.name not in excluded:
                obj.matrix_world = rot_mat @ obj.matrix_world
        self.report({"INFO"}, "Rotation de 180° autour de X appliquée")
        return {"FINISHED"}


# =============================================
# NETTOYAGE
# =============================================


class VIEW3D_OT_toggle_vertex_snap(bpy.types.Operator):
    bl_idname = "view3d.toggle_vertex_snap"
    bl_label = "Accrochage Vertex"

    def execute(self, context):
        ts = context.scene.tool_settings

        if ts.use_snap:
            ts.use_snap = False
            self.report({"INFO"}, "Accrochage désactivé")
        else:
            ts.use_snap = True
            ts.snap_elements = {"VERTEX"}
            self.report({"INFO"}, "Accrochage Vertex activé")

        return {"FINISHED"}


class ORIENT_OT_purge_markers(bpy.types.Operator):
    bl_idname = "orient_tools.purge_markers"
    bl_label = "Purger tous les repères"

    def execute(self, context):
        all_markers = ["ScaleRef_A", "ScaleRef_B", "OriginRef", "XRef", "YRef"]
        removed_count = 0
        for name in all_markers:
            obj = bpy.data.objects.get(name)
            if obj:
                bpy.data.objects.remove(obj, do_unlink=True)
                removed_count += 1
        self.report({"INFO"}, f"{removed_count} repère(s) supprimé(s)")
        return {"FINISHED"}


# =============================================
# PANELS
# =============================================


class TIMELINE_PT_panel(bpy.types.Panel):
    bl_label = "Timeline"
    bl_idname = "TIMELINE_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ColmapTLOE"

    def draw(self, context):
        layout = self.layout
        layout.operator("timeline_tools.link_cameras", icon="CAMERA_DATA")
        layout.operator("timeline_tools.set_focal", icon="SETTINGS")


class ORIENT_PT_panel(bpy.types.Panel):
    bl_label = "Orientation"
    bl_idname = "ORIENT_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ColmapTLOE"

    def draw(self, context):
        layout = self.layout
        layout.operator("orient_tools.create_origin_refs", icon="EMPTY_AXIS")
        layout.operator("orient_tools.apply_orientation", icon="ORIENTATION_GLOBAL")
        layout.operator("orient_tools.rotate_180_x", icon="DRIVER_ROTATIONAL_DIFFERENCE")


class SCALE_PT_panel(bpy.types.Panel):
    bl_label = "Échelle"
    bl_idname = "SCALE_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ColmapTLOE"

    def draw(self, context):
        layout = self.layout
        layout.operator("scale_tools.create_markers", icon="EMPTY_AXIS")
        layout.operator("scale_tools.apply_scale", icon="FULLSCREEN_ENTER")


class CLEANUP_PT_panel(bpy.types.Panel):
    bl_label = "Nettoyage"
    bl_idname = "CLEANUP_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ColmapTLOE"

    def draw(self, context):
        layout = self.layout

        layout.operator("orient_tools.purge_markers", icon="TRASH")

        ts = context.scene.tool_settings

        if ts.use_snap and "VERTEX" in ts.snap_elements:
            txt = "Accrochage Vertex : OUI"
            icn = "CHECKMARK"
        else:
            txt = "Accrochage Vertex : NON"
            icn = "X"

        layout.operator(
            "view3d.toggle_vertex_snap",
            text=txt,
            icon=icn,
        )


# =============================================
# REGISTER
# =============================================


classes = (
    TIMELINE_OT_link_cameras,
    TIMELINE_OT_set_focal,
    SCALE_OT_create_markers,
    SCALE_OT_apply_scale,
    ORIENT_OT_create_origin_refs,
    ORIENT_OT_apply_orientation,
    ORIENT_OT_rotate_180_x,
    ORIENT_OT_purge_markers,
    TIMELINE_PT_panel,
    ORIENT_PT_panel,
    SCALE_PT_panel,
    CLEANUP_PT_panel,
    VIEW3D_OT_toggle_vertex_snap,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
