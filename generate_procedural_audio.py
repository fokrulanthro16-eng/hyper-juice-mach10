"""
=============================================================================
HYPER-JUICE: 100% Procedural Audio Synthesizer v2.0
RenderJuice Blender Animation & Programmatic Rendering Contest
Theme: Speed | 100% Mathematically Synthesized via Python (wave, math, struct)
Zero external samples, zero third-party audio assets, zero AI audio models.
=============================================================================
Synthesizes a 12.0-second (288 frames @ 24 FPS) broadcast-quality 48kHz stereo WAV:
- Multi-pole analog IIR low-pass filtering to eliminate digital harshness
- Multi-tap stereo acoustic spatial reverb & Doppler echoes
- Rich sub-bass harmonics (28Hz - 80Hz) providing cinematic trailer weight
- Act 1 (0.0s - 2.5s): 38Hz sub-rumble, 55Hz mains hum, GPU coil whine, and panic alert beeps
- Act 2 (2.5s - 9.0s): Massive 95kW detonation, exponential Doppler acceleration roar,
                      and 48 accelerating stereo whoosh pulses
- Act 3 (9.0s - 12.0s): 28Hz supersonic shockwave boom & lush D-maj9 cosmic chord shimmer
=============================================================================
"""

import wave
import struct
import math
import random
import os

SAMPLE_RATE = 48000
DURATION = 12.0
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION)
OUTPUT_WAV = "hyper_juice_audio.wav"

def soft_clip(x):
    """Analog-style hyperbolic tangent limiter to guarantee smooth saturation."""
    return math.tanh(x * 0.92)

def apply_2pole_lowpass(buffer, cutoff_hz=7200.0, sample_rate=48000):
    """2-pole IIR lowpass filter to eliminate digital harshness and add analog warmth."""
    rc = 1.0 / (2.0 * math.pi * cutoff_hz)
    dt = 1.0 / sample_rate
    alpha = dt / (rc + dt)
    
    # Pole 1
    p1 = 0.0
    stage1 = [0.0] * len(buffer)
    for i in range(len(buffer)):
        p1 += alpha * (buffer[i] - p1)
        stage1[i] = p1
        
    # Pole 2
    p2 = 0.0
    stage2 = [0.0] * len(buffer)
    for i in range(len(buffer)):
        p2 += alpha * (stage1[i] - p2)
        stage2[i] = p2
        
    return stage2

def apply_spatial_reverb(left_buf, right_buf, sample_rate=48000, wet_level=0.22):
    """Multi-tap spatial acoustic feedback reverb for cinematic trailer depth."""
    taps_l = [int(0.027 * sample_rate), int(0.049 * sample_rate), int(0.083 * sample_rate)]
    taps_r = [int(0.035 * sample_rate), int(0.057 * sample_rate), int(0.091 * sample_rate)]
    gains = [0.42, 0.28, 0.16]

    out_l = list(left_buf)
    out_r = list(right_buf)

    for tap_len, gain in zip(taps_l, gains):
        for i in range(tap_len, TOTAL_SAMPLES):
            out_l[i] += left_buf[i - tap_len] * gain * wet_level

    for tap_len, gain in zip(taps_r, gains):
        for i in range(tap_len, TOTAL_SAMPLES):
            out_r[i] += right_buf[i - tap_len] * gain * wet_level

    return out_l, out_r

def synthesize_soundtrack():
    print("=" * 72)
    print("HYPER-JUICE: Synthesizing v2.0 Cinema-Grade Stereo Audio (48kHz 16-bit)...")
    print("=" * 72)

    left_buffer = [0.0] * TOTAL_SAMPLES
    right_buffer = [0.0] * TOTAL_SAMPLES

    dt = 1.0 / SAMPLE_RATE

    # -----------------------------------------------------------------------
    # ACT 1: LOCAL GPU BOTTLENECK (0.0s - 2.5s)
    # -----------------------------------------------------------------------
    print("[1/5] Synthesizing Act 1: 38Hz sub-drone, 55Hz hum, coil whine, alert beeps...")
    beep_times = [0.35, 0.85, 1.35, 1.75, 2.05, 2.25, 2.40]

    phase_sub = 0.0
    phase_hum = 0.0
    phase_whine1 = 0.0
    phase_whine2 = 0.0
    phase_riser = 0.0

    for i in range(TOTAL_SAMPLES):
        t = i * dt

        if t < 2.55:
            # 1. 38Hz Deep Sub-Bass Mechanical Drone (Heavy industrial weight)
            sub_drone = 0.28 * math.sin(phase_sub)
            phase_sub += 2.0 * math.pi * 38.0 * dt

            # 2. 55Hz / 110Hz / 220Hz Mains Electrical Struggle with Thermal Tremolo
            tremolo = 0.75 + 0.25 * math.sin(2.0 * math.pi * 3.8 * t)
            hum = (
                0.22 * math.sin(phase_hum) +
                0.11 * math.sin(phase_hum * 2.0) +
                0.04 * math.sin(phase_hum * 4.0)
            ) * tremolo
            phase_hum += 2.0 * math.pi * 55.0 * dt

            # 3. High-Frequency GPU Coil Whine (3,240Hz & 6,480Hz with voltage jitter)
            jitter = 40.0 * math.sin(2.0 * math.pi * 21.0 * t) + 20.0 * math.cos(2.0 * math.pi * 53.0 * t)
            freq_w1 = 3240.0 + jitter
            freq_w2 = 6480.0 + jitter * 1.5
            whine = (0.07 * math.sin(phase_whine1) + 0.035 * math.sin(phase_whine2)) * (0.8 + 0.2 * math.sin(t * 11.0))
            phase_whine1 += 2.0 * math.pi * freq_w1 * dt
            phase_whine2 += 2.0 * math.pi * freq_w2 * dt

            # 4. Rhythmic Warning Strobe Beeps with Warm Harmonic Body
            beep_val = 0.0
            for b_idx, bt in enumerate(beep_times):
                if bt <= t < bt + 0.16:
                    tau = t - bt
                    env = math.exp(-20.0 * tau)
                    freq_beep = 880.0 if b_idx % 2 == 0 else 1174.0 # A5 / D6
                    beep_val += 0.26 * env * (
                        math.sin(2.0 * math.pi * freq_beep * tau) +
                        0.25 * math.sin(2.0 * math.pi * freq_beep * 2.0 * tau)
                    )

            # 5. Thermal Rupture Exponential Pitch Riser (2.05s - 2.5s)
            riser = 0.0
            if 2.05 <= t < 2.5:
                rt = (t - 2.05) / 0.45
                rfreq = 220.0 + 2800.0 * (rt ** 2.3)
                phase_riser += 2.0 * math.pi * rfreq * dt
                riser = 0.38 * (rt ** 1.6) * math.sin(phase_riser)

            # Fade out Act 1 cleanly at detonation
            act1_fade = 1.0 if t < 2.45 else max(0.0, 1.0 - (t - 2.45) / 0.05)
            sig_act1 = (sub_drone + hum + whine + beep_val + riser) * act1_fade

            left_buffer[i] += sig_act1 * 0.96
            right_buffer[i] += sig_act1 * 1.04

    # -----------------------------------------------------------------------
    # ACT 2: MACH-10 SURGE & HYPERSPACE TUNNEL (2.5s - 9.0s)
    # -----------------------------------------------------------------------
    print("[2/5] Synthesizing Act 2: 95kW blast detonation, rich Doppler sweep, 48 whooshes...")

    # A. Massive Detonation Impact (t = 2.5s) with 32Hz Sub-Boom
    phase_sub_boom = 0.0
    random.seed(42)
    for i in range(TOTAL_SAMPLES):
        t = i * dt
        if 2.5 <= t < 4.5:
            tau = t - 2.5
            # Sub bass drop (190Hz down to 32Hz)
            freq_sub = 32.0 + 158.0 * math.exp(-7.0 * tau)
            phase_sub_boom += 2.0 * math.pi * freq_sub * dt
            sub_env = math.exp(-2.2 * tau)
            sub_impact = 0.72 * math.sin(phase_sub_boom) * sub_env

            # Textured lowpass noise burst
            noise_env = math.exp(-6.5 * tau)
            noise_val = 0.40 * (random.random() * 2.0 - 1.0) * noise_env

            left_buffer[i] += (sub_impact + noise_val) * 1.15
            right_buffer[i] += (sub_impact + noise_val) * 1.15

    # B. Rich Doppler Hypersonic Turbine Roar (2.5s - 9.0s)
    phase_roar1 = 0.0
    phase_roar2 = 0.0
    phase_sub_layer = 0.0

    for i in range(TOTAL_SAMPLES):
        t = i * dt
        if 2.5 <= t < 9.1:
            u = (t - 2.5) / 6.5 # 0.0 to 1.0
            freq_engine = 85.0 + 1550.0 * (u ** 2.35)
            freq_octave = freq_engine * 0.5
            freq_sub = 45.0 + 120.0 * (u ** 1.8) # Constant sub-bass pressure

            phase_roar1 += 2.0 * math.pi * freq_engine * dt
            phase_roar2 += 2.0 * math.pi * freq_octave * dt
            phase_sub_layer += 2.0 * math.pi * freq_sub * dt

            amp = math.sin(u * math.pi) ** 0.5 if u < 0.9 else max(0.0, 1.0 - (u - 0.9) / 0.1)

            detune = 1.004
            engine_l = (0.26 * math.sin(phase_roar1) + 0.20 * math.sin(phase_roar2) + 0.22 * math.sin(phase_sub_layer)) * amp
            engine_r = (0.26 * math.sin(phase_roar1 * detune) + 0.20 * math.sin(phase_roar2 * detune) + 0.22 * math.sin(phase_sub_layer)) * amp

            # Aerodynamic pink noise buffeting
            air_noise = (random.random() * 2.0 - 1.0) * 0.14 * (u ** 1.4) * amp

            left_buffer[i] += engine_l + air_noise
            right_buffer[i] += engine_r + air_noise

    # C. Passing Speed Rings Stereo Whooshes (48 accelerating pulses with alternating L-R pans)
    num_whooshes = 48
    whoosh_times = []
    for w in range(num_whooshes):
        frac = (w / float(num_whooshes)) ** 0.65
        w_time = 3.15 + 5.75 * frac
        whoosh_times.append((w_time, -0.88 if w % 2 == 0 else 0.88))

    for w_time, pan in whoosh_times:
        start_idx = int((w_time - 0.09) * SAMPLE_RATE)
        end_idx = int((w_time + 0.14) * SAMPLE_RATE)
        pan_l = 0.5 * (1.0 - pan)
        pan_r = 0.5 * (1.0 + pan)

        for i in range(max(0, start_idx), min(TOTAL_SAMPLES, end_idx)):
            t = i * dt
            tau = (t - w_time) / 0.065
            if abs(tau) < 2.5:
                w_env = math.exp(-tau * tau)
                w_freq = 420.0 + 720.0 * (1.0 - abs(tau) / 2.5)
                w_sig = 0.28 * w_env * math.sin(2.0 * math.pi * w_freq * (t - w_time))
                left_buffer[i] += w_sig * pan_l
                right_buffer[i] += w_sig * pan_r

    # -----------------------------------------------------------------------
    # ACT 3: OPEN SPACE & "SPEED UNLEASHED" REVEAL (9.0s - 12.0s)
    # -----------------------------------------------------------------------
    print("[3/5] Synthesizing Act 3: 28Hz sonic boom impact & lush D-maj9 cosmic chord...")

    # A. 28Hz Supersonic Sonic Boom Shockwave (Colossal cinematic trailer impact)
    phase_boom = 0.0
    for i in range(TOTAL_SAMPLES):
        t = i * dt
        if 9.0 <= t < 11.5:
            tau = t - 9.0
            freq_boom = 28.0 + 75.0 * math.exp(-5.5 * tau)
            phase_boom += 2.0 * math.pi * freq_boom * dt
            boom_env = math.exp(-1.6 * tau)
            boom_sig = 0.82 * math.sin(phase_boom) * boom_env
            # Thunder crack transient
            crack = (random.random() * 2.0 - 1.0) * 0.32 * math.exp(-15.0 * tau)

            left_buffer[i] += (boom_sig + crack) * 1.1
            right_buffer[i] += (boom_sig + crack) * 1.1

    # B. Ethereal D-maj9 Cosmic Victory Chord (D3, A3, F#4, C#5, E5)
    chord_freqs = [
        146.83, # D3 (Root)
        220.00, # A3 (5th)
        369.99, # F#4 (Major 3rd)
        554.37, # C#5 (Major 7th)
        659.25  # E5 (9th)
    ]
    chord_weights = [0.26, 0.22, 0.19, 0.17, 0.15]

    for c_idx, (cfreq, weight) in enumerate(zip(chord_freqs, chord_weights)):
        phase_c1 = 0.0
        phase_c2 = 0.0 # Unison chorusing
        pan_c = -0.5 + c_idx * 0.25
        pan_l = 0.5 * (1.0 - pan_c)
        pan_r = 0.5 * (1.0 + pan_c)

        detune_ratio = 1.0025

        for i in range(TOTAL_SAMPLES):
            t = i * dt
            if t >= 9.05:
                tau = t - 9.05
                if tau < 0.65:
                    c_env = (tau / 0.65) ** 1.4
                else:
                    c_env = math.exp(-0.32 * (tau - 0.65))

                shimmer = 1.0 + 0.12 * math.sin(2.0 * math.pi * 3.0 * t + c_idx * 1.1)
                phase_c1 += 2.0 * math.pi * cfreq * dt
                phase_c2 += 2.0 * math.pi * cfreq * detune_ratio * dt

                # Dual oscillator chorused synth pad
                sig_note = weight * c_env * shimmer * (
                    0.65 * math.sin(phase_c1) +
                    0.35 * math.sin(phase_c2) +
                    0.20 * math.sin(phase_c1 * 2.0)
                )

                left_buffer[i] += sig_note * pan_l * 1.18
                right_buffer[i] += sig_note * pan_r * 1.18

    # -----------------------------------------------------------------------
    # ANALOG 2-POLE LOWPASS & SPATIAL REVERB PROCESSING
    # -----------------------------------------------------------------------
    print("[4/5] Applying 2-pole analog IIR lowpass filter & spatial reverb...")
    filtered_l = apply_2pole_lowpass(left_buffer, cutoff_hz=7400.0, sample_rate=SAMPLE_RATE)
    filtered_r = apply_2pole_lowpass(right_buffer, cutoff_hz=7400.0, sample_rate=SAMPLE_RATE)

    reverbed_l, reverbed_r = apply_spatial_reverb(filtered_l, filtered_r, sample_rate=SAMPLE_RATE, wet_level=0.22)

    # -----------------------------------------------------------------------
    # MASTER LIMITING & 16-BIT PCM EXPORT
    # -----------------------------------------------------------------------
    print("[5/5] Applying master soft-clipping and packaging 16-bit PCM WAV...")

    wav_file = wave.open(OUTPUT_WAV, 'w')
    wav_file.setnchannels(2)     # Stereo
    wav_file.setsampwidth(2)     # 16-bit
    wav_file.setframerate(SAMPLE_RATE)

    packed_frames = bytearray()
    max_peak = 0.0

    for i in range(TOTAL_SAMPLES):
        val_l = soft_clip(reverbed_l[i])
        val_r = soft_clip(reverbed_r[i])

        max_peak = max(max_peak, abs(val_l), abs(val_r))

        int_l = int(max(-32767, min(32767, val_l * 32760)))
        int_r = int(max(-32767, min(32767, val_r * 32760)))

        packed_frames.extend(struct.pack('<hh', int_l, int_r))

    wav_file.writeframes(packed_frames)
    wav_file.close()

    file_size_mb = os.path.getsize(OUTPUT_WAV) / (1024 * 1024)
    print(f"\n[SUCCESS] Generated v2.0 Audio: {OUTPUT_WAV} ({file_size_mb:.2f} MB)")
    print(f" - Duration:    {DURATION:.2f}s ({TOTAL_SAMPLES} samples @ {SAMPLE_RATE}Hz)")
    print(f" - Channels:    2 (Stereo)")
    print(f" - Peak Level:  {max_peak:.2f}")
    print("=" * 72)

if __name__ == "__main__":
    synthesize_soundtrack()
