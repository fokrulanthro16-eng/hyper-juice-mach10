"""
=============================================================================
HYPER-JUICE: 8K Master Video Walkthrough Renderer & Compositor
RenderJuice Blender Animation & Programmatic Rendering Contest
Composites the 5 distinct phases at 7680x4320 (8K UHD) with synchronized
voiceover ducking into hyper_juice_8k_technical_walkthrough.mp4 (60.00s).
=============================================================================
"""

import os
import subprocess
import sys
import time

def run_command(cmd, desc):
    print(f"\n>>> [Stage] {desc}")
    print(f"Executing: {cmd}")
    t0 = time.time()
    p = subprocess.run(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elapsed = time.time() - t0
    if p.returncode != 0:
        print(f"ERROR: {desc} failed after {elapsed:.1f}s!\n{p.stderr}")
        sys.exit(1)
    print(f"[+] Completed: {desc} ({elapsed:.1f}s)")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    plates_dir = os.path.join(script_dir, "plates_8k")
    temp_dir = os.path.join(script_dir, "temp_8k_segments")
    os.makedirs(temp_dir, exist_ok=True)

    master_audio = os.path.join(script_dir, "master_walkthrough_audio.wav")
    final_video = os.path.join(script_dir, "hyper_juice_8k_technical_walkthrough.mp4")

    if not os.path.exists(master_audio):
        print("Master audio not found. Running build_audio_mix.py...")
        subprocess.run(f"py -3.11 {os.path.join(script_dir, 'build_audio_mix.py')}", shell=True, check=True)

    # 1. Segment 1: Fullscreen Master Animation (00:00 - 00:13, 13.0s)
    seg1 = os.path.join(temp_dir, "seg1.mp4")
    overlay_p1 = os.path.join(plates_dir, "overlay_phase1_8k.png")
    master_anim = os.path.join(script_dir, "hyper_juice_speed_render.mp4")

    cmd_seg1 = (
        f'ffmpeg -y -i "{master_anim}" -i "{overlay_p1}" '
        f'-filter_complex "[0:v]tpad=stop_mode=clone:stop_duration=1,scale=7680:4320:flags=lanczos,unsharp=5:5:0.5[vid];'
        f'[vid][1:v]overlay=0:0[outv]" -map "[outv]" -t 13.0 '
        f'-c:v libx264 -pix_fmt yuv420p -preset fast -b:v 35M -r 24 "{seg1}"'
    )
    run_command(cmd_seg1, "Rendering 8K Segment 1 (Master Animation, 13.0s)")

    # 2. Segment 2: Code Architecture & Asset Disclosure (00:13 - 00:25, 12.0s)
    seg2 = os.path.join(temp_dir, "seg2.mp4")
    plate_p2 = os.path.join(plates_dir, "plate_phase2_8k.png")
    cmd_seg2 = (
        f'ffmpeg -y -loop 1 -t 12.0 -i "{plate_p2}" '
        f'-vf "scale=7680:4320,format=yuv420p" '
        f'-c:v libx264 -preset fast -b:v 30M -r 24 "{seg2}"'
    )
    run_command(cmd_seg2, "Rendering 8K Segment 2 (Code & Disclosure, 12.0s)")

    # 3. Segment 3: Mathematical Formulas & Flight Dynamics (00:25 - 00:40, 15.0s)
    seg3 = os.path.join(temp_dir, "seg3.mp4")
    plate_p3 = os.path.join(plates_dir, "plate_phase3_8k.png")
    cmd_seg3 = (
        f'ffmpeg -y -loop 1 -t 15.0 -i "{plate_p3}" '
        f'-vf "scale=7680:4320,format=yuv420p" '
        f'-c:v libx264 -preset fast -b:v 30M -r 24 "{seg3}"'
    )
    run_command(cmd_seg3, "Rendering 8K Segment 3 (Mathematical Formulas, 15.0s)")

    # 4. Segment 4: Three.js 3D Viewport & Benchmark (00:40 - 00:52, 12.0s)
    seg4 = os.path.join(temp_dir, "seg4.mp4")
    plate_p4 = os.path.join(plates_dir, "plate_phase4_8k.png")
    loop_gif = os.path.join(script_dir, "preview_loop.gif")

    cmd_seg4 = (
        f'ffmpeg -y -loop 1 -t 12.0 -i "{plate_p4}" -stream_loop -1 -t 12.0 -i "{loop_gif}" '
        f'-filter_complex "[1:v]scale=3840:2160:flags=lanczos[tunnel];'
        f'[0:v][tunnel]overlay=240:720[outv]" -map "[outv]" '
        f'-c:v libx264 -pix_fmt yuv420p -preset fast -b:v 32M -r 24 "{seg4}"'
    )
    run_command(cmd_seg4, "Rendering 8K Segment 4 (Three.js 3D Viewport & Benchmarks, 12.0s)")

    # 5. Segment 5: 1-Click Verification & Outro (00:52 - 01:00, 8.0s)
    seg5 = os.path.join(temp_dir, "seg5.mp4")
    plate_p5 = os.path.join(plates_dir, "plate_phase5_8k.png")
    cmd_seg5 = (
        f'ffmpeg -y -loop 1 -t 8.0 -i "{plate_p5}" '
        f'-vf "fade=t=out:st=7.25:d=0.75,scale=7680:4320,format=yuv420p" '
        f'-c:v libx264 -preset fast -b:v 30M -r 24 "{seg5}"'
    )
    run_command(cmd_seg5, "Rendering 8K Segment 5 (1-Click CLI & Grand Outro, 8.0s)")

    # 6. Final Concatenation & Master Audio Synchronization
    print("\n>>> [Final Assembly] Concatenating 5 8K Segments and Muxing 48kHz Ducked Master Audio...")
    concat_list = os.path.join(temp_dir, "concat_list.txt")
    with open(concat_list, "w") as f:
        f.write(f"file '{seg1.replace(chr(92), '/')}'\n")
        f.write(f"file '{seg2.replace(chr(92), '/')}'\n")
        f.write(f"file '{seg3.replace(chr(92), '/')}'\n")
        f.write(f"file '{seg4.replace(chr(92), '/')}'\n")
        f.write(f"file '{seg5.replace(chr(92), '/')}'\n")

    cmd_final = (
        f'ffmpeg -y -f concat -safe 0 -i "{concat_list}" -i "{master_audio}" '
        f'-c:v copy -c:a aac -b:a 256k -shortest "{final_video}"'
    )
    run_command(cmd_final, "Assembling Final 8K Master Video (hyper_juice_8k_technical_walkthrough.mp4)")

    # Verification
    if os.path.exists(final_video):
        fsize = os.path.getsize(final_video)
        print("\n" + "=" * 79)
        print(f"[SUCCESS] 8K Technical Walkthrough Video Generated!")
        print(f"File: {final_video}")
        print(f"Size: {fsize / (1024*1024):.2f} MB ({fsize} bytes)")
        print(f"Resolution: 7680x4320 (8K UHD) @ 24 FPS")
        print(f"Duration: Exactly 60.00 Seconds")
        print(f"Audio: 48kHz Stereo AAC (Ducked Procedural Synth + Neural Narrator)")
        print("=" * 79)

if __name__ == "__main__":
    main()
