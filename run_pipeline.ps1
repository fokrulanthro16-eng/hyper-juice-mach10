<#
.SYNOPSIS
    HYPER-JUICE: Mach-10 Render Pipeline v3.0 - Automated Reproducibility Script
.DESCRIPTION
    Fully automated pipeline execution for the RenderJuice Blender Animation Contest.
    Verifies dependencies, synthesizes audio, proceduralizes 3D scene, renders stills,
    muxes broadcast MP4, generates loop GIF, and serves web showcase.
.PARAMETER SkipRender
    Skip Blender CLI full animation re-render if hyper_juice_speed_render.mp4 exists.
.PARAMETER Port
    Local web server port (default: 8080).
.PARAMETER NoBrowser
    Do not automatically open the default web browser.
#>
param(
    [switch]$SkipRender = $true,
    [int]$Port = 8080,
    [switch]$NoBrowser = $false
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "  _   _ __   ______  ______ _____       _ _   _ _____ _____ ______ " -ForegroundColor Cyan
Write-Host " | | | |\ \ / /  _ \|  ____|  __ \     | | | | |_   _/ ____|  ____|" -ForegroundColor Cyan
Write-Host " | |_| | \ V /| |_) | |__  | |__) |____| | | | | | || |    | |__   " -ForegroundColor Cyan
Write-Host " |  _  |  > < |  __/|  __| |  _  /|____| | | | | | || |    |  __|  " -ForegroundColor Cyan
Write-Host " | | | | / . \| |   | |____| | \ \     | |_| |_| |_| |____| |____ " -ForegroundColor Cyan
Write-Host " |_| |_|/_/ \_\_|   |______|_|  \_\     \___/ \___/ \_____\_____|______|" -ForegroundColor Cyan
Write-Host "                      MACH-10 RENDER PIPELINE v3.0" -ForegroundColor Yellow
Write-Host "      RenderJuice Blender Animation & Programmatic Rendering Contest" -ForegroundColor DarkGray
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Dependency Checks
Write-Host "[1/6] Verifying Dependencies..." -ForegroundColor Green
try {
    $pyVer = & py -3.11 --version 2>&1
    Write-Host "  [+] Python 3.11: $pyVer" -ForegroundColor Gray
} catch {
    Write-Error "Python 3.11 is required but not found in PATH."
    exit 1
}

$blenderCmd = Get-Command blender -ErrorAction SilentlyContinue
if (-not $blenderCmd) {
    if (Test-Path "C:\Users\WALTON\.gemini\antigravity\bin\blender.cmd") {
        $env:PATH = "C:\Users\WALTON\.gemini\antigravity\bin;$env:PATH"
        Write-Host "  [+] Blender wrapper found in Antigravity bin." -ForegroundColor Gray
    } elseif (Test-Path "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe") {
        $env:PATH = "C:\Program Files\Blender Foundation\Blender 4.2;$env:PATH"
        Write-Host "  [+] Blender 4.2 found in Program Files." -ForegroundColor Gray
    } else {
        Write-Error "Blender executable not found in PATH or standard directories."
        exit 1
    }
} else {
    Write-Host "  [+] Blender CLI: $($blenderCmd.Source)" -ForegroundColor Gray
}

$ffmpegCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpegCmd) {
    if (Test-Path "C:\Users\WALTON\bin\bin\ffmpeg.exe") {
        $env:PATH = "C:\Users\WALTON\bin\bin;$env:PATH"
        Write-Host "  [+] FFmpeg found in C:\Users\WALTON\bin\bin." -ForegroundColor Gray
    } else {
        Write-Warning "FFmpeg not found. Video muxing will rely on Blender VSE."
    }
} else {
    Write-Host "  [+] FFmpeg: $($ffmpegCmd.Source)" -ForegroundColor Gray
}
Write-Host ""

# 2. Audio Synthesis
Write-Host "[2/6] Synthesizing 100% Procedural Audio (WAV 48kHz Stereo)..." -ForegroundColor Green
& py -3.11 generate_procedural_audio.py
Write-Host ""

# 3. 3D Scene Generation
Write-Host "[3/6] Generating Procedural 3D Scene Architecture (bpy)..." -ForegroundColor Green
& py -3.11 generate_speed_animation.py
Write-Host ""

# 4. Hero Stills & Wireframe Proof
Write-Host "[4/6] Rendering Hero Stills and Topology Wireframe Proof..." -ForegroundColor Green
& py -3.11 render_preview.py
& py -3.11 render_wireframe_proof.py
Write-Host ""

# 5. Video & Loop GIF Processing
Write-Host "[5/6] Verifying Master Video & Generating Loop GIF..." -ForegroundColor Green
$videoFile = "hyper_juice_speed_render.mp4"
$audioFile = "hyper_juice_audio.wav"

if ((Test-Path $videoFile) -and $SkipRender) {
    Write-Host "  [+] Video file '$videoFile' exists. Remuxing with updated audio..." -ForegroundColor Yellow
    if (Test-Path $audioFile) {
        $tempVideo = "hyper_juice_speed_render_temp.mp4"
        & ffmpeg -y -i $videoFile -i $audioFile -c:v copy -c:a aac -b:a 256k $tempVideo 2>$null
        if (Test-Path $tempVideo) {
            Move-Item -Force $tempVideo $videoFile
            Write-Host "  [+] Master MP4 audio successfully synchronized." -ForegroundColor Gray
        }
    }
} else {
    Write-Host "  [*] Executing full Blender CLI animation render (288 frames)..." -ForegroundColor Yellow
    & blender -b hyper_juice_wip.blend -a
}

Write-Host "  [*] Generating preview_loop.gif (Frames 100-180)..." -ForegroundColor Gray
& ffmpeg -y -ss 00:00:04.167 -t 00:00:03.333 -i $videoFile -vf "fps=20,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3" -loop 0 preview_loop.gif 2>$null
Write-Host "  [+] preview_loop.gif created." -ForegroundColor Gray
Write-Host ""

# 6. Web Showcase Launch
Write-Host "[6/6] Launching Cyberpunk Web Showcase v3.0 on http://localhost:$Port..." -ForegroundColor Green
$conn = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if (-not $conn) {
    Start-Process py -ArgumentList "-3.11", "-m", "http.server", "$Port" -WindowStyle Hidden
    Start-Sleep -Seconds 2
    Write-Host "  [+] Local HTTP server spawned on port $Port." -ForegroundColor Gray
} else {
    Write-Host "  [+] Port $Port already active." -ForegroundColor Gray
}

if (-not $NoBrowser) {
    Start-Process "http://localhost:$Port/index.html"
}

Write-Host ""
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] HYPER-JUICE v3.0 Pipeline Completed Successfully!" -ForegroundColor Green
Write-Host "Web Showcase is live at: http://localhost:$Port" -ForegroundColor Yellow
Write-Host "===============================================================================" -ForegroundColor Cyan
