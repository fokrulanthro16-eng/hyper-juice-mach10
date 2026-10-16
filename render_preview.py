"""
=============================================================================
HYPER-JUICE: Preview & Still Renderer Utility
RenderJuice Blender Animation & Programmatic Rendering Contest
=============================================================================
Quickly render key hero frames or preview animation clips from hyper_juice_wip.blend.
"""

import bpy
import os
import sys

def render_act_stills():
    script_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    blend_path = os.path.join(script_dir, "hyper_juice_wip.blend")
    if not os.path.exists(blend_path):
        print(f"Error: {blend_path} not found. Please run generate_speed_animation.py first.")
        sys.exit(1)

    print(f"Opening {blend_path}...")
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene

    # Set still render format
    scene.render.image_settings.file_format = 'PNG'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100

    hero_frames = [
        (35,  "hero_act1_bottleneck.png",   "Act 1: Local GPU Bottleneck Core"),
        (61,  "hero_act2_surge_blast.png",   "Act 2: RenderJuice Surge Detonation"),
        (130, "hero_act2_mach10_tunnel.png", "Act 2: Mach-10 Hyperspace Speed Rings"),
        (265, "hero_act3_title_reveal.png",  "Act 3: RENDERJUICE: SPEED UNLEASHED")
    ]

    for frame, filename, desc in hero_frames:
        out_path = os.path.join(script_dir, filename)
        scene.frame_set(frame)
        scene.render.filepath = out_path
        print(f"\n[Rendering Frame {frame}] {desc} -> {filename}...")
        bpy.ops.render.render(write_still=True)
        print(f"Saved: {out_path} ({os.path.getsize(out_path)} bytes)")

    print("\nAll hero still frames successfully rendered!")

if __name__ == "__main__":
    render_act_stills()
