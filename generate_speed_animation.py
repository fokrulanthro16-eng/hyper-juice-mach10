"""
=============================================================================
HYPER-JUICE: Mach-10 Render Pipeline
RenderJuice Blender Animation & Programmatic Rendering Contest
Theme: Speed | Category: Best Procedural & Programmatic Animation / Best Promo

Author: Autonomous AGY Production Agent
License: MIT / Contest Submission
Target: Blender 4.x (fully compatible with 4.0, 4.1, 4.2+ EEVEE-Next & EEVEE)
Asset Disclosure: 100% Procedurally generated using Blender Python API (bpy).
                  Zero third-party meshes, textures, or external AI assets.
=============================================================================
"""

import bpy
import math
import random
import os
import sys

# ---------------------------------------------------------------------------
# GLOBAL CONSTANTS & CONFIGURATION
# ---------------------------------------------------------------------------
FPS = 24
TOTAL_FRAMES = 288       # 12.0 seconds exact
RES_X = 1920
RES_Y = 1080

# Act Boundaries
ACT1_END = 60            # Frames 1-60:  Act 1 - Local GPU Bottleneck
ACT2_END = 216           # Frames 61-216: Act 2 - Mach-10 RenderJuice Hyperspace
ACT3_END = 288           # Frames 217-288: Act 3 - Open Space & Title Reveal

# Tunnel Dimensions
TUNNEL_START_Y = 25.0
TUNNEL_END_Y = 2200.0
TUNNEL_LENGTH = TUNNEL_END_Y - TUNNEL_START_Y
NUM_RINGS = 150
NUM_STREAKS = 260
TUNNEL_RADIUS = 5.2

# Signature Color Palette (RGBA)
COLOR_ORANGE = (1.0, 0.32, 0.01, 1.0)       # RenderJuice Signature Electric Orange
COLOR_CYAN = (0.0, 0.92, 1.0, 1.0)          # RenderJuice Signature Quantum Cyan
COLOR_WARNING_RED = (1.0, 0.02, 0.03, 1.0)   # Local GPU Thermal Throttle Red
COLOR_METAL_DARK = (0.05, 0.055, 0.07, 1.0)  # Heavy Industrial Gunmetal Alloy
COLOR_COPPER = (0.85, 0.42, 0.18, 1.0)       # Cooling Heatpipes
COLOR_WHITE_STAR = (0.9, 0.95, 1.0, 1.0)     # Celestial Starlight Particles


# ---------------------------------------------------------------------------
# UTILITY HELPERS
# ---------------------------------------------------------------------------
def clear_scene():
    """Purge all existing objects, meshes, materials, lights, and collections."""
    # Ensure object mode
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Remove all objects
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # Purge orphan data blocks
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    for curve in list(bpy.data.curves):
        bpy.data.curves.remove(curve)
    for light in list(bpy.data.lights):
        bpy.data.lights.remove(light)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam)
    for col in list(bpy.data.collections):
        if col != bpy.context.scene.collection:
            bpy.data.collections.remove(col)


def get_or_create_collection(name, parent_collection=None):
    """Retrieve or construct a named collection and link it to the tree."""
    if name in bpy.data.collections:
        col = bpy.data.collections[name]
    else:
        col = bpy.data.collections.new(name)
        if parent_collection is None:
            parent_collection = bpy.context.scene.collection
        parent_collection.children.link(col)
    return col


def set_principled_bsdf(node, base_color=None, metallic=None, roughness=None,
                        emission_color=None, emission_strength=None):
    """Set Principled BSDF attributes across Blender 3.x, 4.0, 4.1, and 4.2+."""
    if base_color is not None and "Base Color" in node.inputs:
        node.inputs["Base Color"].default_value = base_color
    if metallic is not None and "Metallic" in node.inputs:
        node.inputs["Metallic"].default_value = metallic
    if roughness is not None and "Roughness" in node.inputs:
        node.inputs["Roughness"].default_value = roughness
    if emission_color is not None:
        if "Emission Color" in node.inputs:
            node.inputs["Emission Color"].default_value = emission_color
        elif "Emission" in node.inputs:
            node.inputs["Emission"].default_value = emission_color
    if emission_strength is not None and "Emission Strength" in node.inputs:
        node.inputs["Emission Strength"].default_value = emission_strength


# ---------------------------------------------------------------------------
# PROCEDURAL MATERIALS FACTORY
# ---------------------------------------------------------------------------
def create_shader_materials():
    """Create all procedural shaders with Blender 4.x Principled & Emission nodes."""
    materials = {}

    # 1. Dark Industrial Gunmetal (Bottleneck core chassis & tunnel alloy)
    mat_metal = bpy.data.materials.new(name="Mat_Bottleneck_Gunmetal")
    mat_metal.use_nodes = True
    tree_m = mat_metal.node_tree
    bsdf = tree_m.nodes.get("Principled BSDF")
    if bsdf:
        set_principled_bsdf(bsdf, base_color=COLOR_METAL_DARK, metallic=0.96, roughness=0.32)
        # Add micro-surface noise and bump for cybernetic grit
        tex_noise = tree_m.nodes.new(type="ShaderNodeTexNoise")
        tex_noise.inputs["Scale"].default_value = 45.0
        tex_noise.inputs["Detail"].default_value = 4.0
        bump = tree_m.nodes.new(type="ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.12
        bump.inputs["Distance"].default_value = 0.08
        tree_m.links.new(tex_noise.outputs["Fac"], bump.inputs["Height"])
        tree_m.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    materials["metal_gunmetal"] = mat_metal

    # 2. Brushed Copper Heat Pipes
    mat_copper = bpy.data.materials.new(name="Mat_Cooling_Copper")
    mat_copper.use_nodes = True
    tree_c = mat_copper.node_tree
    bsdf = tree_c.nodes.get("Principled BSDF")
    if bsdf:
        set_principled_bsdf(bsdf, base_color=COLOR_COPPER, metallic=0.92, roughness=0.22)
        tex_noise_c = tree_c.nodes.new(type="ShaderNodeTexNoise")
        tex_noise_c.inputs["Scale"].default_value = 65.0
        bump_c = tree_c.nodes.new(type="ShaderNodeBump")
        bump_c.inputs["Strength"].default_value = 0.08
        tree_c.links.new(tex_noise_c.outputs["Fac"], bump_c.inputs["Height"])
        tree_c.links.new(bump_c.outputs["Normal"], bsdf.inputs["Normal"])
    materials["copper"] = mat_copper

    # 3. Throttle Red Warning Emission (Act 1 Bottleneck warning strobe)
    mat_red = bpy.data.materials.new(name="Mat_Warning_Red")
    mat_red.use_nodes = True
    tree = mat_red.node_tree
    tree.nodes.clear()
    out_node = tree.nodes.new(type="ShaderNodeOutputMaterial")
    em_node = tree.nodes.new(type="ShaderNodeEmission")
    em_node.inputs["Color"].default_value = COLOR_WARNING_RED
    em_node.inputs["Strength"].default_value = 8.0
    tree.links.new(em_node.outputs["Emission"], out_node.inputs["Surface"])
    materials["warning_red"] = mat_red
    materials["warning_red_emission_node"] = em_node

    # 4. RenderJuice Signature Electric Orange Neon (Act 2 & 3)
    mat_orange = bpy.data.materials.new(name="Mat_RenderJuice_Orange")
    mat_orange.use_nodes = True
    tree = mat_orange.node_tree
    tree.nodes.clear()
    out_node = tree.nodes.new(type="ShaderNodeOutputMaterial")
    em_node_orange = tree.nodes.new(type="ShaderNodeEmission")
    em_node_orange.inputs["Strength"].default_value = 35.0
    
    # Procedural Noise & ColorRamp for living plasma core
    noise_o = tree.nodes.new(type="ShaderNodeTexNoise")
    noise_o.inputs["Scale"].default_value = 16.0
    ramp_o = tree.nodes.new(type="ShaderNodeValToRGB")
    ramp_o.color_ramp.elements[0].color = COLOR_ORANGE
    ramp_o.color_ramp.elements[1].color = (1.0, 0.68, 0.18, 1.0) # Hot plasma core
    tree.links.new(noise_o.outputs["Fac"], ramp_o.inputs["Fac"])
    tree.links.new(ramp_o.outputs["Color"], em_node_orange.inputs["Color"])
    tree.links.new(em_node_orange.outputs["Emission"], out_node.inputs["Surface"])
    materials["neon_orange"] = mat_orange
    materials["neon_orange_node"] = em_node_orange

    # 5. RenderJuice Signature Quantum Cyan Neon (Act 2 & 3)
    mat_cyan = bpy.data.materials.new(name="Mat_RenderJuice_Cyan")
    mat_cyan.use_nodes = True
    tree = mat_cyan.node_tree
    tree.nodes.clear()
    out_node = tree.nodes.new(type="ShaderNodeOutputMaterial")
    em_node_cyan = tree.nodes.new(type="ShaderNodeEmission")
    em_node_cyan.inputs["Strength"].default_value = 35.0

    # Procedural Noise & ColorRamp for quantum cyan plasma core
    noise_c = tree.nodes.new(type="ShaderNodeTexNoise")
    noise_c.inputs["Scale"].default_value = 16.0
    ramp_c = tree.nodes.new(type="ShaderNodeValToRGB")
    ramp_c.color_ramp.elements[0].color = COLOR_CYAN
    ramp_c.color_ramp.elements[1].color = (0.55, 0.98, 1.0, 1.0) # Intense quantum core
    tree.links.new(noise_c.outputs["Fac"], ramp_c.inputs["Fac"])
    tree.links.new(ramp_c.outputs["Color"], em_node_cyan.inputs["Color"])
    tree.links.new(em_node_cyan.outputs["Emission"], out_node.inputs["Surface"])
    materials["neon_cyan"] = mat_cyan
    materials["neon_cyan_node"] = em_node_cyan

    # 6. Tunnel Structural Framing Dark Metal with Voronoi Plating
    mat_tunnel = bpy.data.materials.new(name="Mat_Tunnel_Truss")
    mat_tunnel.use_nodes = True
    tree_t = mat_tunnel.node_tree
    bsdf = tree_t.nodes.get("Principled BSDF")
    if bsdf:
        set_principled_bsdf(bsdf, base_color=(0.025, 0.028, 0.035, 1.0), metallic=0.98, roughness=0.22)
        tex_vor = tree_t.nodes.new(type="ShaderNodeTexVoronoi")
        tex_vor.inputs["Scale"].default_value = 9.0
        bump_t = tree_t.nodes.new(type="ShaderNodeBump")
        bump_t.inputs["Strength"].default_value = 0.15
        bump_t.inputs["Distance"].default_value = 0.06
        tree_t.links.new(tex_vor.outputs["Distance"], bump_t.inputs["Height"])
        tree_t.links.new(bump_t.outputs["Normal"], bsdf.inputs["Normal"])
    materials["tunnel_metal"] = mat_tunnel

    # 7. Shockwave Energy Pulse (Act 3 exit blast)
    mat_shock = bpy.data.materials.new(name="Mat_Shockwave_Blast")
    mat_shock.use_nodes = True
    tree = mat_shock.node_tree
    tree.nodes.clear()
    out_node = tree.nodes.new(type="ShaderNodeOutputMaterial")
    em_node = tree.nodes.new(type="ShaderNodeEmission")
    em_node.inputs["Color"].default_value = COLOR_CYAN
    em_node.inputs["Strength"].default_value = 40.0
    tree.links.new(em_node.outputs["Emission"], out_node.inputs["Surface"])
    materials["shockwave"] = mat_shock
    materials["shockwave_emission_node"] = em_node

    # 8. Celestial Starlight Particle Material
    mat_star = bpy.data.materials.new(name="Mat_Celestial_Dust")
    mat_star.use_nodes = True
    tree = mat_star.node_tree
    tree.nodes.clear()
    out_node = tree.nodes.new(type="ShaderNodeOutputMaterial")
    em_node = tree.nodes.new(type="ShaderNodeEmission")
    em_node.inputs["Color"].default_value = COLOR_WHITE_STAR
    em_node.inputs["Strength"].default_value = 25.0
    tree.links.new(em_node.outputs["Emission"], out_node.inputs["Surface"])
    materials["star_dust"] = mat_star

    # 9. Master Title Face Chrome Material
    mat_title_chrome = bpy.data.materials.new(name="Mat_Title_Chrome")
    mat_title_chrome.use_nodes = True
    bsdf = mat_title_chrome.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        set_principled_bsdf(bsdf, base_color=(0.04, 0.045, 0.05, 1.0), metallic=1.0, roughness=0.08)
    materials["title_chrome"] = mat_title_chrome

    return materials


# ---------------------------------------------------------------------------
# PROCEDURAL GEOMETRY BUILDERS
# ---------------------------------------------------------------------------
def create_extruded_polygon_mesh(name, radius_in, radius_out, length_y, segments, twist_rad=0.0):
    """
    Construct a clean, manifold 3D polygonal ring mesh with quad faces.
    Segments determine shape: 6=Hexagon, 8=Octagon, 24=Circular Torus, 4=Diamond.
    """
    verts = []
    half_y = length_y / 2.0
    N = segments

    # Layer 0: Front face (y = -half_y)
    for r in [radius_in, radius_out]:
        for i in range(N):
            angle = (2.0 * math.pi * i / N) + twist_rad
            verts.append((r * math.cos(angle), -half_y, r * math.sin(angle)))

    # Layer 1: Back face (y = +half_y)
    for r in [radius_in, radius_out]:
        for i in range(N):
            angle = (2.0 * math.pi * i / N) + twist_rad
            verts.append((r * math.cos(angle), half_y, r * math.sin(angle)))

    faces = []
    # Front ring faces (quads between inner and outer loop)
    for i in range(N):
        nxt = (i + 1) % N
        faces.append([i, nxt, N + nxt, N + i])

    # Back ring faces
    for i in range(N):
        nxt = (i + 1) % N
        faces.append([2 * N + i, 3 * N + i, 3 * N + nxt, 2 * N + nxt])

    # Outer cylindrical rim
    for i in range(N):
        nxt = (i + 1) % N
        faces.append([N + i, N + nxt, 3 * N + nxt, 3 * N + i])

    # Inner cylindrical tunnel wall
    for i in range(N):
        nxt = (i + 1) % N
        faces.append([i, 2 * N + i, 2 * N + nxt, nxt])

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


def create_solid_box_mesh(name, size_x, size_y, size_z):
    """Generate a clean 3D cuboid mesh."""
    hx, hy, hz = size_x / 2.0, size_y / 2.0, size_z / 2.0
    verts = [
        (-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
        (-hx, -hy, hz),  (hx, -hy, hz),  (hx, hy, hz),  (-hx, hy, hz)
    ]
    faces = [
        [0, 1, 2, 3],  # Bottom
        [4, 7, 6, 5],  # Top
        [0, 4, 5, 1],  # Front
        [2, 6, 7, 3],  # Back
        [0, 3, 7, 4],  # Left
        [1, 5, 6, 2]   # Right
    ]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


# ---------------------------------------------------------------------------
# ACT 1: LOCAL GPU BOTTLENECK CORE (Frames 1 - 60)
# ---------------------------------------------------------------------------
def build_act1_bottleneck_scene(materials, collection):
    """
    Build the sluggish local GPU bottleneck assembly:
    - Heavy beveled metallic core chassis
    - Procedural heat sink cooling fin array
    - Copper heatpipes
    - Pulsing thermal throttle red warning LED lightbars
    - Overheat warning beacon light
    - Keyframed labored/stuttering rotation and thermal surge detonation at frame 60
    """
    # 1. Main Core Chassis Cube
    core_mesh = create_solid_box_mesh("Mesh_BottleneckCore", 2.2, 2.2, 2.2)
    core_obj = bpy.data.objects.new("Bottleneck_Core", core_mesh)
    core_obj.data.materials.append(materials["metal_gunmetal"])
    collection.objects.link(core_obj)
    core_obj.location = (0.0, 0.0, 0.0)

    # 2. Procedural Heatsink Fins (10 horizontal plates)
    for k in range(10):
        z_pos = -0.95 + k * (1.9 / 9.0)
        fin_mesh = create_solid_box_mesh(f"Mesh_HeatsinkFin_{k}", 2.55, 2.55, 0.04)
        fin_obj = bpy.data.objects.new(f"Heatsink_Fin_{k}", fin_mesh)
        fin_obj.data.materials.append(materials["metal_gunmetal"])
        collection.objects.link(fin_obj)
        fin_obj.parent = core_obj
        fin_obj.location = (0.0, 0.0, z_pos)

    # 3. Copper Cooling Pipes (4 vertical heat dissipation conduits)
    pipe_offsets = [
        (-1.18, -1.18),
        (1.18, -1.18),
        (1.18, 1.18),
        (-1.18, 1.18)
    ]
    for idx, (px, py) in enumerate(pipe_offsets):
        pipe_mesh = create_extruded_polygon_mesh(f"Mesh_CopperPipe_{idx}", 0.07, 0.11, 2.6, 12)
        pipe_obj = bpy.data.objects.new(f"Copper_Pipe_{idx}", pipe_mesh)
        pipe_obj.data.materials.append(materials["copper"])
        collection.objects.link(pipe_obj)
        pipe_obj.parent = core_obj
        pipe_obj.location = (px, 0.0, py)
        pipe_obj.rotation_euler = (math.pi / 2.0, 0.0, 0.0)

    # 4. Red Warning Lightbars on 4 Faces
    lightbar_configs = [
        ((0.0, -1.12, 0.0), (2.1, 0.05, 0.16)),   # Front face
        ((0.0, 1.12, 0.0),  (2.1, 0.05, 0.16)),   # Back face
        ((-1.12, 0.0, 0.0), (0.05, 2.1, 0.16)),   # Left face
        ((1.12, 0.0, 0.0),  (0.05, 2.1, 0.16))    # Right face
    ]
    for idx, (lpos, lsize) in enumerate(lightbar_configs):
        bar_mesh = create_solid_box_mesh(f"Mesh_WarningBar_{idx}", lsize[0], lsize[1], lsize[2])
        bar_obj = bpy.data.objects.new(f"Warning_Lightbar_{idx}", bar_mesh)
        bar_obj.data.materials.append(materials["warning_red"])
        collection.objects.link(bar_obj)
        bar_obj.parent = core_obj
        bar_obj.location = lpos

    # 5. Internal Thermal Warning Point Light
    light_data = bpy.data.lights.new(name="Light_ThrottleWarning", type='POINT')
    light_data.color = (1.0, 0.05, 0.05)
    light_data.energy = 250.0
    light_data.shadow_soft_size = 0.5
    light_obj = bpy.data.objects.new("Warning_Beacon_Light", light_data)
    collection.objects.link(light_obj)
    light_obj.parent = core_obj
    light_obj.location = (0.0, 0.0, 0.0)

    # 6. Procedural Holographic Warning HUD Circle
    hud_mesh = create_extruded_polygon_mesh("Mesh_WarningHUD", 2.0, 2.08, 0.02, 32)
    hud_obj = bpy.data.objects.new("Warning_HUD_Ring", hud_mesh)
    hud_obj.data.materials.append(materials["warning_red"])
    collection.objects.link(hud_obj)
    hud_obj.parent = core_obj
    hud_obj.location = (0.0, 0.0, 0.0)

    # -----------------------------------------------------------------------
    # ANIMATION & KEYFRAMING FOR ACT 1
    # -----------------------------------------------------------------------
    # Keyframe labored rotation & thermal stuttering on the core
    core_obj.animation_data_create()
    light_obj.animation_data_create()

    # Stutter simulation: simulate GPU thermal throttling dropping frames
    stutter_timeline = [
        (1,   0.0,    0.0,    200.0),
        (15,  0.15,   0.04,   450.0),
        (22,  0.16,   0.045,  150.0),   # Stutter freeze 1
        (35,  0.42,   0.12,   600.0),
        (42,  0.44,   0.125,  200.0),   # Stutter freeze 2 (thermal throttle)
        (52,  0.85,   0.24,   1400.0),  # Critical alarm
        (58,  1.20,   0.38,   4000.0),  # Pre-detonation spike
        (60,  1.45,   0.45,   6000.0),  # Rupture instant
        (65,  2.20,   0.70,   0.0)      # Vanished / Surge explosion
    ]

    for frame, rz, rx, pwr in stutter_timeline:
        # Core labored rotation
        core_obj.rotation_euler.z = rz
        core_obj.rotation_euler.x = rx
        core_obj.keyframe_insert(data_path="rotation_euler", index=2, frame=frame)
        core_obj.keyframe_insert(data_path="rotation_euler", index=0, frame=frame)

        # Scale: Disintegrates outward / collapses as RenderJuice surge hits at frame 60
        if frame < 58:
            core_obj.scale = (1.0, 1.0, 1.0)
        elif frame == 60:
            core_obj.scale = (1.25, 1.25, 1.25)
        else:
            core_obj.scale = (0.001, 0.001, 0.001)
        core_obj.keyframe_insert(data_path="scale", frame=frame)

        # Light power pulse
        light_obj.data.energy = pwr
        light_obj.data.keyframe_insert(data_path="energy", frame=frame)

    # Keyframe emission node strength for the warning red shader
    em_node = materials["warning_red_emission_node"]
    for f in range(1, 65):
        if f <= 50:
            # Rhythmic warning pulse: 6Hz heartbeat
            val = 6.0 + 18.0 * (0.5 + 0.5 * math.sin(f * 0.45))
        elif f <= 60:
            # Exponential thermal overload surge
            val = 25.0 + 95.0 * ((f - 50) / 10.0) ** 2.0
        else:
            val = 0.0  # Obliterated by RenderJuice
        em_node.inputs["Strength"].default_value = val
        em_node.inputs["Strength"].keyframe_insert(data_path="default_value", frame=f)

    return core_obj


# ---------------------------------------------------------------------------
# ACT 2: MACH-10 RENDERJUICE HYPERSPACE TUNNEL (Frames 61 - 216)
# ---------------------------------------------------------------------------
def build_act2_tunnel_scene(materials, collection):
    """
    Construct the hypersonic cyberpunk tunnel:
    - Exactly 150 procedural neon speed rings (Hexagons, Octagons, Toruses, Diamonds)
    - Progressive vortex twist rotation
    - Alternating RenderJuice Electric Orange and Quantum Cyan emission shaders
    - 8 continuous longitudinal high-voltage guide rails spanning 2200 meters
    - 260+ high-velocity light streaks / ion particles generating motion blur
    """
    rings = []

    # 1. Procedural 150 Neon Speed Rings
    for i in range(NUM_RINGS):
        frac = i / float(NUM_RINGS - 1)
        # Spaced along the full length from 30m to 2180m
        y_pos = TUNNEL_START_Y + (TUNNEL_END_Y - TUNNEL_START_Y - 20.0) * frac

        # Cycle 4 futuristic archetypes
        archetype = i % 4
        if archetype == 0:
            # Hexagonal Accelerator Gate
            segments = 6
            r_in = TUNNEL_RADIUS * 0.88
            r_out = TUNNEL_RADIUS * 1.05
            depth = 0.55
        elif archetype == 1:
            # Octagonal Compression Ring
            segments = 8
            r_in = TUNNEL_RADIUS * 0.84
            r_out = TUNNEL_RADIUS * 0.98
            depth = 0.40
        elif archetype == 2:
            # Circular Quantum Torus
            segments = 24
            r_in = TUNNEL_RADIUS * 0.82
            r_out = TUNNEL_RADIUS * 0.94
            depth = 0.48
        else:
            # Diamond Velocity Gate
            segments = 4
            r_in = TUNNEL_RADIUS * 0.92
            r_out = TUNNEL_RADIUS * 1.15
            depth = 0.65

        # Progressive Vortex Twist
        twist = i * 0.092  # Radians

        ring_mesh = create_extruded_polygon_mesh(
            f"Mesh_SpeedRing_{i:03d}",
            r_in, r_out, depth, segments, twist_rad=twist
        )
        ring_obj = bpy.data.objects.new(f"SpeedRing_{i:03d}", ring_mesh)

        # Dynamic Color Distribution: Waves of Electric Orange & Quantum Cyan
        color_wave = math.sin(i * 0.35)
        if color_wave > -0.15:
            ring_obj.data.materials.append(materials["neon_orange"])
        else:
            ring_obj.data.materials.append(materials["neon_cyan"])

        collection.objects.link(ring_obj)
        ring_obj.location = (0.0, y_pos, 0.0)
        rings.append(ring_obj)

    # 2. 8 Continuous Longitudinal Cyber Guide Rails (0 to 2200m)
    rail_count = 8
    rail_radius = TUNNEL_RADIUS * 1.08
    for r in range(rail_count):
        theta = 2.0 * math.pi * r / rail_count
        rx = rail_radius * math.cos(theta)
        rz = rail_radius * math.sin(theta)

        # Continuous rail length
        rail_mesh = create_solid_box_mesh(f"Mesh_GuideRail_{r}", 0.08, TUNNEL_LENGTH + 50.0, 0.08)
        rail_obj = bpy.data.objects.new(f"GuideRail_{r}", rail_mesh)

        # Alternating rail colors (Cyan & Orange)
        if r % 2 == 0:
            rail_obj.data.materials.append(materials["neon_cyan"])
        else:
            rail_obj.data.materials.append(materials["neon_orange"])

        collection.objects.link(rail_obj)
        rail_obj.location = (rx, (TUNNEL_START_Y + TUNNEL_END_Y) / 2.0, rz)

    # 3. 260 High-Velocity Light Streaks (Ion Particles)
    # Stretched along Y to create instantaneous laser velocity blur
    random.seed(42)  # Deterministic seed for reproducible elegance
    for s in range(NUM_STREAKS):
        sy = random.uniform(TUNNEL_START_Y + 10.0, TUNNEL_END_Y - 30.0)
        s_angle = random.uniform(0.0, 2.0 * math.pi)
        s_dist = random.uniform(TUNNEL_RADIUS * 0.45, TUNNEL_RADIUS * 0.95)
        sx = s_dist * math.cos(s_angle)
        sz = s_dist * math.sin(s_angle)

        streak_length = random.uniform(18.0, 55.0)
        streak_thickness = random.uniform(0.025, 0.065)

        streak_mesh = create_solid_box_mesh(f"Mesh_Streak_{s:03d}", streak_thickness, streak_length, streak_thickness)
        streak_obj = bpy.data.objects.new(f"LightStreak_{s:03d}", streak_mesh)

        if random.random() > 0.45:
            streak_obj.data.materials.append(materials["neon_orange"])
        else:
            streak_obj.data.materials.append(materials["neon_cyan"])

    # 4. Animate Tunnel Ignition Surge at Frame 60 (Dormant during Act 1, explodes at Act 2)
    em_orange = materials["neon_orange_node"]
    em_cyan = materials["neon_cyan_node"]

    # Keyframe ignition surge
    ignition_keyframes = [
        (1, 0.0),      # Dark during Act 1 bottleneck
        (59, 0.0),     # Dark right before surge
        (60, 25.0),    # Surge detonation strikes!
        (63, 65.0),    # Blinding hypersonic ignition
        (75, 38.0),    # Steady Mach-10 cruise emission
        (TOTAL_FRAMES, 38.0)
    ]
    for frame, strength in ignition_keyframes:
        em_orange.inputs["Strength"].default_value = strength
        em_orange.inputs["Strength"].keyframe_insert(data_path="default_value", frame=frame)
        em_cyan.inputs["Strength"].default_value = strength
        em_cyan.inputs["Strength"].keyframe_insert(data_path="default_value", frame=frame)

    # 5. Surge Detonation Flash Light at Y = 20.0
    surge_light_data = bpy.data.lights.new(name="Light_SurgeDetonation", type='POINT')
    surge_light_data.color = (0.2, 0.9, 1.0)
    surge_light_data.energy = 0.0
    surge_light_data.shadow_soft_size = 3.0
    surge_light = bpy.data.objects.new("Surge_Detonation_Light", surge_light_data)
    collection.objects.link(surge_light)
    surge_light.location = (0.0, 15.0, 0.0)

    surge_light.animation_data_create()
    surge_light.data.energy = 0.0
    surge_light.data.keyframe_insert(data_path="energy", frame=1)
    surge_light.data.keyframe_insert(data_path="energy", frame=59)
    surge_light.data.energy = 95000.0  # Epic blast
    surge_light.data.keyframe_insert(data_path="energy", frame=61)
    surge_light.data.energy = 10000.0
    surge_light.data.keyframe_insert(data_path="energy", frame=68)
    surge_light.data.energy = 0.0
    surge_light.data.keyframe_insert(data_path="energy", frame=75)

    return rings


# ---------------------------------------------------------------------------
# ACT 3: OPEN SPACE, SHOCKWAVES & 3D TITLE (Frames 217 - 288)
# ---------------------------------------------------------------------------
def build_act3_reveal_scene(materials, collection):
    """
    Construct the grand finale:
    - 4 Expanding supersonic shockwave rings bursting at the tunnel exit portal
    - Celestial starlight dust particles scattered across open space
    - Master 3D extruded title: "RENDERJUICE: SPEED UNLEASHED"
    - Underline aerodynamic chevron bracket
    - Studio key and rim lighting
    """
    # 1. Expanding Supersonic Shockwave Rings (Centered at Y = 2215m)
    shockwaves = []
    for w in range(4):
        w_y = 2210.0 + w * 4.0
        ring_mesh = create_extruded_polygon_mesh(f"Mesh_Shockwave_{w}", 1.8, 2.15, 0.35, 36)
        shock_obj = bpy.data.objects.new(f"Shockwave_Ring_{w}", ring_mesh)

        if w % 2 == 0:
            shock_obj.data.materials.append(materials["neon_cyan"])
        else:
            shock_obj.data.materials.append(materials["neon_orange"])

        collection.objects.link(shock_obj)
        shock_obj.location = (0.0, w_y, 0.0)
        shockwaves.append(shock_obj)

        # Animate Shockwave Expansion from Frame 216 to 260
        shock_obj.animation_data_create()
        delay = w * 3
        t_start = ACT2_END + delay
        t_peak = t_start + 18
        t_end = t_start + 38

        # Keyframe initial dormant state
        shock_obj.scale = (0.01, 0.01, 0.01)
        shock_obj.keyframe_insert(data_path="scale", frame=1)
        shock_obj.keyframe_insert(data_path="scale", frame=t_start)

        # Peak explosive burst
        shock_obj.scale = (14.0, 1.0, 14.0)
        shock_obj.keyframe_insert(data_path="scale", frame=t_peak)

        # Final dissipation into open space
        shock_obj.scale = (38.0, 0.1, 38.0)
        shock_obj.keyframe_insert(data_path="scale", frame=t_end)

    # 2. Celestial Starlight Dust Field & Title Streamers (Open deep space)
    random.seed(1337)
    # 450 ambient floating starlight particles
    for p in range(450):
        py = random.uniform(2220.0, 2490.0)
        p_angle = random.uniform(0.0, 2.0 * math.pi)
        p_dist = random.uniform(6.0, 68.0)
        px = p_dist * math.cos(p_angle)
        pz = p_dist * math.sin(p_angle)
        p_size = random.uniform(0.07, 0.24)

        star_mesh = create_solid_box_mesh(f"Mesh_StarDust_{p:03d}", p_size, p_size, p_size)
        star_obj = bpy.data.objects.new(f"StarDust_{p:03d}", star_mesh)
        star_obj.data.materials.append(materials["star_dust"])
        collection.objects.link(star_obj)
        star_obj.location = (px, py, pz)

    # 36 High-Velocity Light Streamers passing the title text
    for s_idx in range(36):
        sy = random.uniform(2320.0, 2440.0)
        s_rad = random.uniform(5.5, 28.0)
        s_ang = random.uniform(0.0, 2.0 * math.pi)
        sx = s_rad * math.cos(s_ang)
        sz = s_rad * math.sin(s_ang)
        s_len = random.uniform(12.0, 32.0)
        s_thick = random.uniform(0.02, 0.05)

        streamer_mesh = create_solid_box_mesh(f"Mesh_TitleStreamer_{s_idx:02d}", s_thick, s_len, s_thick)
        streamer_obj = bpy.data.objects.new(f"TitleStreamer_{s_idx:02d}", streamer_mesh)
        streamer_obj.data.materials.append(materials["neon_orange"] if s_idx % 2 == 0 else materials["neon_cyan"])
        collection.objects.link(streamer_obj)
        streamer_obj.location = (sx, sy, sz)

    # 3. Master 3D Extruded Title Text: "RENDERJUICE: SPEED UNLEASHED"
    # Line 1: "RENDERJUICE" (Hero font size, bevel, chrome face with orange rim)
    title_curve1 = bpy.data.curves.new(name="Curve_Title1", type='FONT')
    title_curve1.body = "RENDERJUICE"
    title_curve1.size = 6.4
    title_curve1.extrude = 0.65
    title_curve1.bevel_depth = 0.06
    title_curve1.bevel_resolution = 3
    title_curve1.align_x = 'CENTER'
    title_curve1.align_y = 'CENTER'

    title_obj1 = bpy.data.objects.new("Title_RENDERJUICE", title_curve1)
    title_obj1.data.materials.append(materials["title_chrome"])
    collection.objects.link(title_obj1)
    # Position in open space facing oncoming camera
    title_obj1.location = (0.0, 2370.0, 1.2)
    title_obj1.rotation_euler = (math.pi / 2.0, 0.0, 0.0)

    # Glowing Orange Backplate for "RENDERJUICE"
    back_curve1 = bpy.data.curves.new(name="Curve_Backplate1", type='FONT')
    back_curve1.body = "RENDERJUICE"
    back_curve1.size = 6.45
    back_curve1.extrude = 0.70
    back_curve1.bevel_depth = 0.09
    back_curve1.align_x = 'CENTER'
    back_curve1.align_y = 'CENTER'

    back_obj1 = bpy.data.objects.new("Title_RENDERJUICE_Glow", back_curve1)
    back_obj1.data.materials.append(materials["neon_orange"])
    collection.objects.link(back_obj1)
    back_obj1.location = (0.0, 2370.8, 1.2)
    back_obj1.rotation_euler = (math.pi / 2.0, 0.0, 0.0)

    # Line 2: "SPEED UNLEASHED" (Glowing Quantum Cyan Subtitle)
    title_curve2 = bpy.data.curves.new(name="Curve_Title2", type='FONT')
    title_curve2.body = "SPEED UNLEASHED"
    title_curve2.size = 3.3
    title_curve2.extrude = 0.45
    title_curve2.bevel_depth = 0.04
    title_curve2.bevel_resolution = 2
    title_curve2.align_x = 'CENTER'
    title_curve2.align_y = 'CENTER'

    title_obj2 = bpy.data.objects.new("Title_SPEED_UNLEASHED", title_curve2)
    title_obj2.data.materials.append(materials["neon_cyan"])
    collection.objects.link(title_obj2)
    title_obj2.location = (0.0, 2369.0, -3.8)
    title_obj2.rotation_euler = (math.pi / 2.0, 0.0, 0.0)

    # 4. Underline Aerodynamic Speed Chevron Bracket
    bar_mesh = create_solid_box_mesh("Mesh_UnderlineChevron", 22.0, 0.4, 0.18)
    bar_obj = bpy.data.objects.new("Underline_Chevron_Bar", bar_mesh)
    bar_obj.data.materials.append(materials["neon_orange"])
    collection.objects.link(bar_obj)
    bar_obj.location = (0.0, 2368.5, -6.0)

    wing_left_mesh = create_solid_box_mesh("Mesh_ChevronWing_L", 4.0, 0.4, 0.22)
    wing_left = bpy.data.objects.new("ChevronWing_L", wing_left_mesh)
    wing_left.data.materials.append(materials["neon_cyan"])
    collection.objects.link(wing_left)
    wing_left.location = (-12.5, 2368.5, -5.2)
    wing_left.rotation_euler = (0.0, math.radians(25.0), 0.0)

    wing_right_mesh = create_solid_box_mesh("Mesh_ChevronWing_R", 4.0, 0.4, 0.22)
    wing_right = bpy.data.objects.new("ChevronWing_R", wing_right_mesh)
    wing_right.data.materials.append(materials["neon_cyan"])
    collection.objects.link(wing_right)
    wing_right.location = (12.5, 2368.5, -5.2)
    wing_right.rotation_euler = (0.0, -math.radians(25.0), 0.0)

    # 5. Hero Cinematic Studio Lights
    # Key Cyan Rim Light
    key_light_data = bpy.data.lights.new(name="Light_HeroCyan", type='POINT')
    key_light_data.color = (0.1, 0.9, 1.0)
    key_light_data.energy = 18000.0
    key_light_data.shadow_soft_size = 2.0
    key_light = bpy.data.objects.new("Hero_Cyan_KeyLight", key_light_data)
    collection.objects.link(key_light)
    key_light.location = (18.0, 2345.0, 8.0)

    # Warm Orange Fill Light
    fill_light_data = bpy.data.lights.new(name="Light_HeroOrange", type='POINT')
    fill_light_data.color = (1.0, 0.4, 0.05)
    fill_light_data.energy = 14000.0
    fill_light_data.shadow_soft_size = 2.0
    fill_light = bpy.data.objects.new("Hero_Orange_FillLight", fill_light_data)
    collection.objects.link(fill_light)
    fill_light.location = (-18.0, 2345.0, -6.0)

    # Ambient Tunnel Exit Flash Light
    exit_light_data = bpy.data.lights.new(name="Light_ExitShockwave", type='POINT')
    exit_light_data.color = (0.5, 0.9, 1.0)
    exit_light_data.energy = 45000.0
    exit_light_data.shadow_soft_size = 5.0
    exit_light = bpy.data.objects.new("Tunnel_Exit_BurstLight", exit_light_data)
    collection.objects.link(exit_light)
    exit_light.location = (0.0, 2215.0, 0.0)

    # Animate Exit Flash Light Burst at Frame 216-245
    exit_light.animation_data_create()
    exit_light.data.energy = 0.0
    exit_light.data.keyframe_insert(data_path="energy", frame=1)
    exit_light.data.keyframe_insert(data_path="energy", frame=ACT2_END)
    exit_light.data.energy = 75000.0
    exit_light.data.keyframe_insert(data_path="energy", frame=ACT2_END + 5)
    exit_light.data.energy = 5000.0
    exit_light.data.keyframe_insert(data_path="energy", frame=ACT2_END + 25)
    exit_light.data.energy = 0.0
    exit_light.data.keyframe_insert(data_path="energy", frame=ACT2_END + 45)


# ---------------------------------------------------------------------------
# CINEMATIC CAMERA SYSTEM & PERLIN-NOISE SHAKE
# ---------------------------------------------------------------------------
def compute_camera_shake(frame):
    """
    Mathematical harmonic noise function for organic camera turbulence.
    Simulates multi-octave Perlin noise without external dependencies.
    """
    if frame < ACT1_END:
        # Act 1: Subtle claustrophobic breathing drift
        amp = 0.03
    elif frame < 85:
        # Act 2 Surge trigger ramp
        amp = 0.03 + 0.97 * ((frame - ACT1_END) / 25.0)
    elif frame < 185:
        # Sustained Mach-10 Hypersonic Flight
        amp = 1.00
    elif frame < ACT2_END:
        # Approaching Tunnel Exit
        amp = 1.00 - 0.70 * ((frame - 185) / float(ACT2_END - 185))
    elif frame < 240:
        # Post-shockwave cosmic glide
        amp = 0.30 * (1.0 - (frame - ACT2_END) / 24.0)
    else:
        # Hero Shot floating drift
        amp = 0.015

    t = frame * 0.48

    # Lateral & Vertical turbulence (X, Z)
    shake_x = amp * 0.22 * (
        math.sin(t * 1.73 + 0.5) +
        0.5 * math.sin(t * 3.41 + 1.2) +
        0.25 * math.sin(t * 7.19 + 2.4)
    )
    shake_z = amp * 0.18 * (
        math.cos(t * 1.91 + 0.8) +
        0.5 * math.cos(t * 4.13 + 0.3) +
        0.25 * math.cos(t * 8.07 + 1.9)
    )

    # Angular turbulence (Pitch X, Roll Y, Yaw Z)
    rot_pitch = amp * 0.030 * (math.sin(t * 2.11) + 0.4 * math.sin(t * 5.23 + 0.9))
    rot_roll  = amp * 0.055 * (math.sin(t * 1.47 + 1.1) + 0.5 * math.cos(t * 3.83))
    rot_yaw   = amp * 0.022 * (math.cos(t * 1.83 + 0.4) + 0.4 * math.sin(t * 4.67))

    return shake_x, shake_z, rot_pitch, rot_roll, rot_yaw


def build_camera_rig(collection):
    """
    Construct the cinematic camera rig with:
    - Act 1 slow push-in (50mm)
    - Act 2 dynamic focal length warp (50mm -> 18mm) and Mach-10 exponential acceleration
    - Multi-octave Perlin noise camera shake
    - Act 3 smooth ease-out deceleration into open space framing the 3D title text (32mm)
    """
    cam_data = bpy.data.cameras.new(name="Camera_Mach10")
    cam_data.sensor_width = 36.0
    cam_data.clip_start = 0.1
    cam_data.clip_end = 4000.0  # Deep sightline for 2.2km tunnel and open space

    cam_obj = bpy.data.objects.new("Camera_Mach10_Main", cam_data)
    collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    cam_obj.animation_data_create()

    # Pre-calculate trajectory for all 288 frames
    for f in range(1, TOTAL_FRAMES + 1):
        shake_x, shake_z, rot_pitch, rot_roll, rot_yaw = compute_camera_shake(f)

        # 1. Base Forward Trajectory Y
        if f <= ACT1_END:
            # Act 1: Slow claustrophobic creep toward the struggling GPU core
            t_frac = f / float(ACT1_END)
            y_base = -6.8 + 1.6 * t_frac  # Moves from -6.8 to -5.2
            z_base = 0.4 - 0.1 * t_frac
            x_base = 0.0
            focal_len = 50.0  # Tight cinematic focal length

        elif f <= ACT2_END:
            # Act 2: Mach-10 Hypersonic Exponential Acceleration
            u = (f - ACT1_END) / float(ACT2_END - ACT1_END)  # 0.0 to 1.0
            # Exponential surge curve (u^2.35): explosive rocket-like acceleration
            y_base = -5.2 + (TUNNEL_END_Y + 5.0 - (-5.2)) * (u ** 2.35)
            x_base = 0.0
            z_base = 0.0

            # Focal Length Dynamic Warp: 50mm -> 18mm warp
            if f <= 85:
                # Fast explosive FOV warp
                warp_frac = (f - ACT1_END) / 25.0
                focal_len = 50.0 - (50.0 - 18.0) * (warp_frac ** 1.5)
            elif f <= 195:
                # Hypersonic speed-breathing effect
                focal_len = 18.0 + 0.6 * math.sin(f * 0.28)
            else:
                # Pre-exit FOV normalization
                exit_warp = (f - 195) / float(ACT2_END - 195)
                focal_len = 18.0 + (28.0 - 18.0) * exit_warp

        else:
            # Act 3: Bursting into open space & smooth ease-out deceleration
            v = (f - ACT2_END) / float(TOTAL_FRAMES - ACT2_END)  # 0.0 to 1.0
            # Cubic ease-out: carries high-speed momentum and gracefully halts
            ease_v = 1.0 - ((1.0 - v) ** 3.0)
            # Decelerates from tunnel exit (2205m) to hero presentation point (2310m)
            y_base = (TUNNEL_END_Y + 5.0) + 105.0 * ease_v
            x_base = 0.0
            z_base = -0.5 * ease_v

            # Hero shot focal length
            if f <= 235:
                focal_len = 28.0 + (32.0 - 28.0) * ((f - ACT2_END) / 18.0)
            else:
                focal_len = 32.0

        # Apply procedural shake offsets to camera coordinates
        cam_obj.location.x = x_base + shake_x
        cam_obj.location.y = y_base
        cam_obj.location.z = z_base + shake_z

        # Orientation: Pointing along +Y axis (math.pi/2 on X) + shake angles
        cam_obj.rotation_euler.x = (math.pi / 2.0) + rot_pitch
        cam_obj.rotation_euler.y = rot_roll
        cam_obj.rotation_euler.z = rot_yaw

        cam_data.lens = focal_len

        # Insert keyframes
        cam_obj.keyframe_insert(data_path="location", frame=f)
        cam_obj.keyframe_insert(data_path="rotation_euler", frame=f)
        cam_data.keyframe_insert(data_path="lens", frame=f)

    return cam_obj


# ---------------------------------------------------------------------------
# POST-PROCESSING, COMPOSITOR & FAST EEVEE PIPELINE
# ---------------------------------------------------------------------------
def configure_render_and_compositor():
    """
    Configure fast EEVEE render engine, motion blur, compositor bloom/glare,
    chromatic dispersion, and H.264 MP4 export settings.
    """
    scene = bpy.context.scene

    # 1. Timeline & Resolution Configuration
    scene.frame_start = 1
    scene.frame_end = TOTAL_FRAMES
    scene.render.fps = FPS
    scene.render.fps_base = 1.0
    scene.render.resolution_x = RES_X
    scene.render.resolution_y = RES_Y
    scene.render.resolution_percentage = 100

    # 2. Render Engine Configuration (EEVEE-Next & Legacy EEVEE fallback)
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        try:
            scene.render.engine = 'BLENDER_EEVEE'
        except Exception:
            scene.render.engine = 'CYCLES'

    # 3. Motion Blur Configuration (Essential for Mach-10 light streaks)
    scene.render.use_motion_blur = True
    if hasattr(scene.render, "motion_blur_shutter"):
        scene.render.motion_blur_shutter = 0.55
    if hasattr(scene.eevee, "motion_blur_shutter"):
        scene.eevee.motion_blur_shutter = 0.55

    # 4. Viewport / EEVEE Bloom Attributes (Blender 4.0/4.1/4.2)
    if hasattr(scene.eevee, "use_bloom"):
        scene.eevee.use_bloom = True
        scene.eevee.bloom_threshold = 0.75
        scene.eevee.bloom_intensity = 0.12
        scene.eevee.bloom_radius = 6.5

    # 5. Fast Render Sampling (Blender 4.x)
    if hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = 32  # Ultra fast, noise-free with motion blur
    if hasattr(scene.eevee, "ray_tracing_method"):
        scene.eevee.ray_tracing_method = 'SCREEN'

    # 6. Color Management (AgX High Contrast for vibrant cyberpunk neon)
    scene.display_settings.display_device = 'sRGB'
    if hasattr(scene.view_settings, "view"):
        try:
            scene.view_settings.view = 'AgX'
        except Exception:
            scene.view_settings.view = 'Filmic'
    try:
        scene.view_settings.look = 'High Contrast'
    except Exception:
        pass

    # 7. Video Export Settings (H.264 / MP4 Container)
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
    script_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    scene.render.filepath = os.path.join(script_dir, "hyper_juice_speed_render.mp4")

    # 8. Compositor Node Tree (Glare Bloom & Hyperspace Lens Dispersion)
    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()

    # Create compositor nodes
    node_rl = tree.nodes.new(type="CompositorNodeRLayers")
    node_rl.location = (-300, 200)

    # Glare / Bloom Node
    node_glare = tree.nodes.new(type="CompositorNodeGlare")
    node_glare.location = (0, 200)
    # Check supported glare types in current Blender build
    glare_types = [item.identifier for item in node_glare.bl_rna.properties['glare_type'].enum_items]
    if 'FOG_GLOW' in glare_types:
        node_glare.glare_type = 'FOG_GLOW'
        node_glare.quality = 'HIGH'
        node_glare.threshold = 0.70
        node_glare.size = 8
    elif 'BLOOM' in glare_types:
        node_glare.glare_type = 'BLOOM'

    # Lens Distortion (Subtle chromatic aberration for hypersonic speed sensation)
    node_lens = tree.nodes.new(type="CompositorNodeLensdist")
    node_lens.location = (250, 200)
    if "Distortion" in node_lens.inputs:
        node_lens.inputs["Distortion"].default_value = 0.0
    elif "Distort" in node_lens.inputs:
        node_lens.inputs["Distort"].default_value = 0.0
    if "Dispersion" in node_lens.inputs:
        node_lens.inputs["Dispersion"].default_value = 0.012

    # Composite Output
    node_comp = tree.nodes.new(type="CompositorNodeComposite")
    node_comp.location = (500, 200)

    # Link nodes
    tree.links.new(node_rl.outputs["Image"], node_glare.inputs["Image"])
    tree.links.new(node_glare.outputs["Image"], node_lens.inputs["Image"])
    tree.links.new(node_lens.outputs["Image"], node_comp.inputs["Image"])

    # 9. Deep Space Void World Shader
    world = bpy.data.worlds.get("World")
    if not world:
        world = bpy.data.worlds.new("World")
        scene.world = world
    world.use_nodes = True
    w_tree = world.node_tree
    bg_node = w_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.003, 0.005, 0.008, 1.0)
        bg_node.inputs["Strength"].default_value = 0.35


# ---------------------------------------------------------------------------
# MAIN PROGRAMMATIC ENTRY POINT
# ---------------------------------------------------------------------------
def main():
    print("=" * 72)
    print("HYPER-JUICE: Mach-10 Render Pipeline - Programmatic Generator")
    print("RenderJuice Blender Animation & Programmatic Rendering Contest")
    print("=" * 72)

    # 1. Reset scene to pristine state
    print("[1/6] Purging scene & initializing environment...")
    clear_scene()

    # 2. Create hierarchical collections
    col_act1 = get_or_create_collection("Act_1_Bottleneck_Core")
    col_act2 = get_or_create_collection("Act_2_Mach10_Tunnel")
    col_act3 = get_or_create_collection("Act_3_OpenSpace_Reveal")
    col_rig  = get_or_create_collection("Cinematic_Rig")

    # 3. Build materials
    print("[2/6] Compiling procedural shader materials...")
    materials = create_shader_materials()

    # 4. Construct Act 1: Local GPU Bottleneck Core
    print("[3/6] Generating Act 1: Local GPU Bottleneck Core (Frames 1-60)...")
    build_act1_bottleneck_scene(materials, col_act1)

    # 5. Construct Act 2: 150 Speed Rings & Light Streaks
    print("[4/6] Generating Act 2: Mach-10 Hyperspace Tunnel (150 Rings, 260 Streaks)...")
    build_act2_tunnel_scene(materials, col_act2)

    # 6. Construct Act 3: Shockwaves & 3D Title "RENDERJUICE: SPEED UNLEASHED"
    print("[5/6] Generating Act 3: Open Space, Shockwaves & 3D Title (Frames 217-288)...")
    build_act3_reveal_scene(materials, col_act3)

    # 7. Build Camera Rig & Configure Render Pipeline
    print("[6/6] Rigging camera warp, Perlin shake & configuring fast EEVEE...")
    build_camera_rig(col_rig)
    configure_render_and_compositor()

    # 8. Save Master Blender Project File
    script_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    output_blend_path = os.path.join(script_dir, "hyper_juice_wip.blend")
    print(f"\n[SUCCESS] Saving master project file to: {output_blend_path}")
    bpy.ops.wm.save_as_mainfile(filepath=output_blend_path)

    # Print Scene Statistics
    total_objs = len(bpy.data.objects)
    total_meshes = len(bpy.data.meshes)
    total_mats = len(bpy.data.materials)
    print("\n" + "-" * 72)
    print("SCENE METRICS SUMMARY:")
    print(f" - Total Objects Created:     {total_objs}")
    print(f" - Procedural Meshes:         {total_meshes}")
    print(f" - Procedural Shaders:        {total_mats}")
    print(f" - Animation Frame Span:      1 - {TOTAL_FRAMES} (12.0s @ 24 FPS)")
    print(f" - Speed Rings Generated:     {NUM_RINGS} Rings (Hex, Oct, Torus, Diamond)")
    print(f" - Light Streaks:             {NUM_STREAKS} High-Velocity Ion Particles")
    print(f" - Render Engine:             {bpy.context.scene.render.engine}")
    print(f" - Motion Blur:               Enabled (Shutter 0.55)")
    print(f" - Resolution:                {RES_X}x{RES_Y} @ 100%")
    print(f" - Output Container:          MP4 (H.264 FFMPEG)")
    print(f" - Master File Saved:         hyper_juice_wip.blend")
    print("-" * 72)
    print("HYPER-JUICE GENERATION COMPLETE. READY FOR MACH-10 RENDERING!")
    print("=" * 72)


if __name__ == "__main__":
    main()
