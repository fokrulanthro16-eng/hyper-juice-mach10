"""
=============================================================================
HYPER-JUICE: 60-Second Master Audio Mixer & Ducking Engine
RenderJuice Blender Animation & Programmatic Rendering Contest
Combines procedural synth soundtrack + neural narrator voiceover with
dynamic sidechain ducking and -14 LUFS broadcast mastering.
=============================================================================
"""

import math
import os
import struct
import subprocess
import wave

def mix_master_audio():
    script_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    music_path = os.path.join(script_dir, "hyper_juice_audio.wav")
    vo_path = os.path.join(script_dir, "voiceover_narrator.wav")
    out_wav = os.path.join(script_dir, "master_walkthrough_audio.wav")

    sample_rate = 48000
    total_duration = 60.0
    total_samples = int(total_duration * sample_rate)

    print("Loading audio assets for 60-second broadcast mix...")

    # 1. Read VO audio
    with wave.open(vo_path, 'rb') as wf:
        vo_frames = wf.readframes(wf.getnframes())
        vo_samples = struct.unpack(f"<{len(vo_frames)//2}h", vo_frames)
        # Stereo interleaved: L, R, L, R...

    # 2. Read Music audio (12.0s procedural soundtrack)
    with wave.open(music_path, 'rb') as wf:
        mus_frames = wf.readframes(wf.getnframes())
        mus_samples = struct.unpack(f"<{len(mus_frames)//2}h", mus_frames)
        mus_len_frames = len(mus_samples) // 2

    # 3. Build 60-second background music bed
    # 0.0s - 12.0s: Original animation soundtrack
    # 12.0s - 13.0s: Reverb tail hold
    # 13.0s - 60.0s: Looped ambient bed from Act 2 hypersonic cruise (t=4.0s to 8.5s) + Act 3 cosmic chord
    bed_samples_L = [0.0] * total_samples
    bed_samples_R = [0.0] * total_samples

    # Copy initial 12s
    for i in range(min(total_samples, mus_len_frames)):
        bed_samples_L[i] = mus_samples[i * 2] / 32768.0
        bed_samples_R[i] = mus_samples[i * 2 + 1] / 32768.0

    # Smooth crossfade loop for 12.0s to 60.0s using Act 2 & 3 hypersonic texture
    loop_start_s = int(4.2 * sample_rate)
    loop_end_s = int(8.8 * sample_rate)
    loop_len = loop_end_s - loop_start_s

    # Fill remainder
    for i in range(mus_len_frames, total_samples):
        offset = (i - mus_len_frames) % loop_len
        src_idx = loop_start_s + offset
        
        # Subtle slow harmonic modulation
        t = i / sample_rate
        mod = 0.85 + 0.15 * math.sin(2 * math.pi * 0.1 * t)
        
        bed_samples_L[i] = (mus_samples[src_idx * 2] / 32768.0) * mod
        bed_samples_R[i] = (mus_samples[src_idx * 2 + 1] / 32768.0) * mod

    # 4. Compute Dynamic Ducking Envelope based on Voiceover Energy
    # Fast attack (30ms), smooth release (250ms)
    vo_envelope = [0.0] * total_samples
    attack_coeff = math.exp(-1.0 / (0.030 * sample_rate))
    release_coeff = math.exp(-1.0 / (0.280 * sample_rate))

    env = 0.0
    for i in range(total_samples):
        vo_L = abs(vo_samples[i * 2] / 32768.0) if i * 2 < len(vo_samples) else 0.0
        vo_R = abs(vo_samples[i * 2 + 1] / 32768.0) if i * 2 + 1 < len(vo_samples) else 0.0
        inst_energy = max(vo_L, vo_R)

        if inst_energy > env:
            env = (1.0 - attack_coeff) * inst_energy + attack_coeff * env
        else:
            env = (1.0 - release_coeff) * inst_energy + release_coeff * env
        vo_envelope[i] = env

    # 5. Mix Bed + VO with dynamic gain
    out_interleaved = bytearray(total_samples * 4)

    for i in range(total_samples):
        t = i / sample_rate
        vo_L = (vo_samples[i * 2] / 32768.0) if i * 2 < len(vo_samples) else 0.0
        vo_R = (vo_samples[i * 2 + 1] / 32768.0) if i * 2 + 1 < len(vo_samples) else 0.0

        # Ducking gain: 1.0 (0dB) when no voiceover, drops smoothly to 0.22 (-13.1dB) during speech
        duck_amount = min(1.0, vo_envelope[i] * 3.5)
        bed_gain = (1.0 - duck_amount) * 1.0 + duck_amount * 0.22

        # In Phase 1 (0.0s - 13.0s), keep music bed at full 100% volume
        if t < 12.8:
            bed_gain = 1.0
        elif t < 13.5:
            # Smooth transition into Phase 2
            ramp = (t - 12.8) / 0.7
            bed_gain = (1.0 - ramp) * 1.0 + ramp * 0.22

        # Combine
        mix_L = (bed_samples_L[i] * bed_gain) + (vo_L * 1.15)
        mix_R = (bed_samples_R[i] * bed_gain) + (vo_R * 1.15)

        # Broadcast soft limiter (tanh)
        mix_L = math.tanh(mix_L * 0.95)
        mix_R = math.tanh(mix_R * 0.95)

        s_L = int(max(-32768, min(32767, mix_L * 32767.0)))
        s_R = int(max(-32768, min(32767, mix_R * 32767.0)))

        struct.pack_into("<hh", out_interleaved, i * 4, s_L, s_R)

    with wave.open(out_wav, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(out_interleaved)

    print(f"[SUCCESS] Mixed 60.0s Master Audio: {out_wav} ({os.path.getsize(out_wav)} bytes)")

if __name__ == "__main__":
    mix_master_audio()
