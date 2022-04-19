import bpy

def fabrik_ik():
    print("Nice")

bpy.app.handlers.frame_change_pre.append(fabrik_ik)