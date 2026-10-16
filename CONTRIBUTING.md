# Contributing to HYPER-JUICE: Mach-10 Render Pipeline

Thank you for your interest in contributing to **HYPER-JUICE: Mach-10 Render Pipeline**! We welcome improvements, optimizations, and scientific extensions to our programmatic 3D and audio synthesis pipelines.

---

## 📜 The Golden Rule: 100% Programmatic Purity

Our project adheres strictly to **absolute mathematical determinism and programmatic procedural generation**:
- **Zero Third-Party Meshes:** All 3D geometry must be constructed procedurally via Python (`from_pydata()` or native mathematical generators).
- **Zero External Textures:** All materials must use procedural mathematical noise nodes (Voronoi, Musgrave, Perlin) and node graphs generated via `bpy.data.materials`.
- **Zero Pre-Recorded Audio Samples:** All sound effects, sweeps, booms, and ambiances must be synthesized using pure mathematical functions (`sin`, `cos`, DSP filters) via standard library Python (`wave`, `struct`, `math`).
- **Zero Generative AI Media:** No AI-generated images, 3D meshes, textures, or pre-rendered video clips may be introduced into the pipeline.

Any contribution that introduces external asset files or violates programmatic reproducibility will be closed.

---

## 🛠️ Development Setup & Workflow

### 1. Prerequisites
- **Blender 4.2+ LTS** (or Blender 4.x) accessible via PATH or default installation directory.
- **Python 3.11+** with standard library.
- **FFmpeg** installed and accessible in system PATH.

### 2. Local Reproducibility
Before opening a Pull Request, verify that your changes execute cleanly without warnings:

```powershell
# Run the complete automated pipeline
.\run_pipeline.ps1 -Port 8080
```

Ensure that:
1. `hyper_juice_wip.blend` generates cleanly with all 940 procedural objects.
2. `hyper_juice_audio.wav` synthesizes without sample clipping ($\le -0.1\text{ dBFS}$).
3. The rendered animation maintains consistent 24.0 FPS motion blur and AgX High-Contrast color grading.

---

## 🔀 Submitting Pull Requests

1. **Fork** the repository and create your feature branch:
   ```bash
   git checkout -b feature/dynamic-vortex-expansion
   ```
2. **Commit** your changes with clear, descriptive commit messages adhering to Conventional Commits:
   - `feat(shader): add procedural anodized sheen to speed rings`
   - `fix(audio): smooth IIR filter resonance at 1.6kHz cutoff`
   - `perf(eevee): reduce ray shadow steps in volumetric container`
3. **Push** to your fork and submit a Pull Request to `main`.
4. Provide a clear PR description detailing:
   - Mathematical rationale and equations used.
   - Scene object count and mesh statistics impact.
   - Benchmark render time comparison per frame.

---

## 📄 License
By contributing to HYPER-JUICE, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
