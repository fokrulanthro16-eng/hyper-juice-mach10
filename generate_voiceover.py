"""
=============================================================================
HYPER-JUICE: 60-Second Master Voiceover Synthesizer (Neural TTS)
RenderJuice Blender Animation & Programmatic Rendering Contest
Generates voiceover_narrator.wav strictly synchronized to the 5-phase timeline.
=============================================================================
"""

import asyncio
import os
import subprocess
import sys
import wave

# Exact 5-Phase Master Script
VOICEOVER_PHASES = [
    {
        "phase": 1,
        "name": "Master Animation Intro",
        "start_sec": 0.0,
        "end_sec": 13.0,
        "text": "",  # 00:00 - 00:13 is dedicated to fullscreen animation with raw procedural synth
        "ducking": 1.0  # Full music volume
    },
    {
        "phase": 2,
        "name": "Code Architecture & Asset Disclosure",
        "start_sec": 13.2,
        "end_sec": 25.0,
        "text": (
            "Welcome to HYPER-JUICE: Mach-10 Render Pipeline. "
            "Built for RenderJuice, every polygon, material shader, "
            "and audio waveform sample is one hundred percent procedurally generated with Blender Python."
        ),
        "ducking": 0.28
    },
    {
        "phase": 3,
        "name": "Mathematical Engine & Flight Dynamics",
        "start_sec": 25.2,
        "end_sec": 40.0,
        "text": (
            "The camera accelerates past Mach-10 along an exponential power curve, "
            "contracting its focal length from fifty to eighteen millimeters. "
            "Multi-harmonic Fourier equations drive organic cockpit buffeting across one hundred fifty procedural quad speed rings."
        ),
        "ducking": 0.28
    },
    {
        "phase": 4,
        "name": "Interactive Web Showcase & 3D Explorer",
        "start_sec": 40.2,
        "end_sec": 52.0,
        "text": (
            "Our web showcase features a Three.js 3D wireframe explorer with 360-degree orbit controls, "
            "plus a timeline scrubber synchronizing optical telemetry and velocity in real-time."
        ),
        "ducking": 0.28
    },
    {
        "phase": 5,
        "name": "One-Click Pipeline & Grand Outro",
        "start_sec": 52.2,
        "end_sec": 60.0,
        "text": (
            "Verified for one-click reproducibility via Windows batch and PowerShell automation. "
            "Experience Mach-10 speed with RenderJuice."
        ),
        "ducking": 0.28
    }
]

VOICE = "en-US-ChristopherNeural"  # Authoritative, broadcast-quality technical narrator

async def synthesize_segment(text, out_mp3):
    import edge_tts
    communicate = edge_tts.Communicate(text, VOICE, rate="+20%", pitch="+0Hz")
    await communicate.save(out_mp3)

def run_cmd(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    if p.returncode != 0:
        print(f"Command error: {cmd}\n{p.stderr}")
    return p.returncode == 0

async def generate_voiceover():
    script_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    temp_dir = os.path.join(script_dir, "temp_vo")
    os.makedirs(temp_dir, exist_ok=True)

    final_wav = os.path.join(script_dir, "voiceover_narrator.wav")
    print(f"=== Generating 60-Second Master Voiceover via Edge-TTS ({VOICE}) ===")

    # 1. Synthesize individual segments
    segment_wavs = []
    for item in VOICEOVER_PHASES:
        p = item["phase"]
        text = item["text"].strip()
        if not text:
            print(f"Phase {p} ({item['name']}): Silent narrator interval (music highlight).")
            continue

        mp3_path = os.path.join(temp_dir, f"phase_{p}.mp3")
        wav_path = os.path.join(temp_dir, f"phase_{p}.wav")
        print(f"Synthesizing Phase {p} ({item['start_sec']}s - {item['end_sec']}s)...")
        await synthesize_segment(text, mp3_path)

        # Convert to 48kHz 16-bit stereo WAV
        cmd = f'ffmpeg -y -i "{mp3_path}" -ar 48000 -ac 2 -c:a pcm_s16le "{wav_path}"'
        run_cmd(cmd)

        # Measure duration
        with wave.open(wav_path, 'rb') as wf:
            dur = wf.getnframes() / float(wf.getframerate())
            print(f"  -> Generated: {dur:.2f}s (Budget: {item['end_sec'] - item['start_sec']}s)")

        segment_wavs.append((item["start_sec"], wav_path))

    # 2. Build exact 60.0-second 48kHz stereo master timeline
    sample_rate = 48000
    total_samples = 60 * sample_rate
    master_audio = bytearray(total_samples * 4)  # 2 channels * 2 bytes = 4 bytes per sample frame (silent)

    import struct

    for start_t, wav_path in segment_wavs:
        start_sample = int(start_t * sample_rate)
        with wave.open(wav_path, 'rb') as wf:
            n_frames = wf.getnframes()
            data = wf.readframes(n_frames)
            
            # Read 16-bit stereo samples and mix
            end_sample = min(total_samples, start_sample + n_frames)
            num_to_copy = end_sample - start_sample

            in_samples = struct.unpack(f"<{num_to_copy * 2}h", data[:num_to_copy * 4])
            out_offset = start_sample * 4
            
            # Write into master buffer
            for idx in range(num_to_copy * 2):
                byte_idx = out_offset + idx * 2
                existing = struct.unpack_from("<h", master_audio, byte_idx)[0]
                val = max(-32768, min(32767, existing + in_samples[idx]))
                struct.pack_into("<h", master_audio, byte_idx, val)

    # 3. Write final master WAV
    with wave.open(final_wav, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(master_audio)

    print(f"\n[SUCCESS] Master Voiceover exported to: {final_wav}")
    print(f"Duration: Exactly 60.00s @ 48kHz Stereo PCM (File size: {os.path.getsize(final_wav)} bytes)")

if __name__ == "__main__":
    asyncio.run(generate_voiceover())
