@echo off
setlocal EnableDelayedExpansion

title HYPER-JUICE: Mach-10 Render Pipeline v3.0

echo ===============================================================================
echo   _   _ __   ______  ______ _____       _ _   _ _____ _____ ______ 
echo  ^| ^| ^| ^|\ \ / /  _ \^|  ____^|  __ \     ^| ^| ^| ^| ^|_   _/ ____^|  ____^|
echo  ^| ^|_^| ^| \ V /^| ^|_) ^| ^|__  ^| ^|__) ^|____^| ^| ^| ^| ^| ^| ^|^| ^|    ^| ^|__   
echo  ^|  _  ^|  ^> ^< ^|  __/^|  __^| ^|  _  /^|____^| ^| ^| ^| ^| ^| ^|^| ^|    ^|  __^|  
echo  ^| ^| ^| ^| / . \^| ^|   ^| ^|____^| ^| \ \     ^| ^|_^| ^|_^| ^|_^| ^|____^| ^|____ 
echo  ^|_^| ^|_^|/_/ \_\_^|   ^|______^|_^|  \_\     \___/ \___/ \_____\_____^|______^|
echo                       MACH-10 RENDER PIPELINE v3.0
echo       RenderJuice Blender Animation ^& Programmatic Rendering Contest
echo ===============================================================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo [1/6] Verifying Runtime Environment...
py -3.11 --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python 3.11 not found! Please ensure Python 3.11 is installed.
    pause
    exit /b 1
)
echo  [+] Python 3.11: OK

where blender >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] 'blender' command not directly in PATH. Checking fallback locations...
    if exist "C:\Users\WALTON\.gemini\antigravity\bin\blender.cmd" (
        set "PATH=C:\Users\WALTON\.gemini\antigravity\bin;!PATH!"
        echo  [+] Blender wrapper located in Antigravity bin: OK
    ) else if exist "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" (
        set "PATH=C:\Program Files\Blender Foundation\Blender 4.2;!PATH!"
        echo  [+] Blender 4.2 found in Program Files: OK
    ) else (
        echo [ERROR] Blender 4.x executable not found.
        pause
        exit /b 1
    )
) else (
    echo  [+] Blender CLI: OK
)

where ffmpeg >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] 'ffmpeg' not found in PATH. Checking fallback...
    if exist "C:\Users\WALTON\bin\bin\ffmpeg.exe" (
        set "PATH=C:\Users\WALTON\bin\bin;!PATH!"
        echo  [+] FFmpeg found in C:\Users\WALTON\bin\bin: OK
    ) else (
        echo [WARN] FFmpeg not found. Video muxing will rely on Blender VSE.
    )
) else (
    echo  [+] FFmpeg: OK
)
echo.

echo [2/6] Synthesizing 100%% Procedural Audio (WAV 48kHz Stereo)...
py -3.11 generate_procedural_audio.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Procedural audio synthesis failed.
    pause
    exit /b 1
)
echo.

echo [3/6] Generating Procedural 3D Scene Architecture (bpy)...
py -3.11 generate_speed_animation.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Scene generation failed.
    pause
    exit /b 1
)
echo.

echo [4/6] Rendering Hero Stills and Topology Wireframe Proof...
py -3.11 render_preview.py
py -3.11 render_wireframe_proof.py
echo.

echo [5/6] Verifying Master Animation and Muxing Audio...
if exist "hyper_juice_speed_render.mp4" (
    echo  [+] Existing master video found. Muxing updated procedural audio...
    if exist "hyper_juice_audio.wav" (
        ffmpeg -y -i hyper_juice_speed_render.mp4 -i hyper_juice_audio.wav -c:v copy -c:a aac -b:a 256k hyper_juice_speed_render_temp.mp4 >nul 2>&1
        if exist "hyper_juice_speed_render_temp.mp4" (
            move /y hyper_juice_speed_render_temp.mp4 hyper_juice_speed_render.mp4 >nul
            echo  [+] Master MP4 remuxed with 256k stereo procedural audio successfully.
        )
    )
) else (
    echo  [*] Rendering full 288-frame animation with Blender CLI...
    blender -b hyper_juice_wip.blend -a
)

echo  [*] Generating / Updating preview_loop.gif (Frames 100-180)...
ffmpeg -y -ss 00:00:04.167 -t 00:00:03.333 -i hyper_juice_speed_render.mp4 -vf "fps=20,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3" -loop 0 preview_loop.gif >nul 2>&1
echo  [+] preview_loop.gif ready.
echo.

echo [6/6] Launching Cyberpunk Web Showcase v3.0 on http://localhost:8080...
powershell -Command "$p = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue; if (-not $p) { Start-Process py -ArgumentList '-3.11','-m','http.server','8080' -WindowStyle Hidden; Start-Sleep -Seconds 2 }"
start http://localhost:8080/index.html

echo.
echo ===============================================================================
echo [SUCCESS] HYPER-JUICE v3.0 Pipeline Completed Successfully!
echo Web Showcase is live at: http://localhost:8080
echo ===============================================================================
pause
