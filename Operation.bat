@echo off
setlocal
color 0A

set "SCRIPT_DIR=%~dp0"
set "LOG_FILE=%TEMP%\Operation_%RANDOM%_%RANDOM%.log"

pushd "%SCRIPT_DIR%" || exit /b 1

echo Converting video to OLED and TFT GIFs...
python "%SCRIPT_DIR%video_to_gif.py" %* > "%LOG_FILE%" 2>&1
set "RESULT=%ERRORLEVEL%"
type "%LOG_FILE%"
if not "%RESULT%"=="0" goto :conversion_failed

set "OLED_GIF="
set "TFT_GIF="
for /f "tokens=1-4,*" %%A in ('findstr /b /c:"Created OLED GIF" "%LOG_FILE%"') do set "OLED_GIF=%%E"
for /f "tokens=1-4,*" %%A in ('findstr /b /c:"Created TFT GIF" "%LOG_FILE%"') do set "TFT_GIF=%%E"
del "%LOG_FILE%"

if not defined OLED_GIF (
    echo ERROR: The video converter did not report an OLED GIF path.
    set "RESULT=1"
    goto :failed
)
if not defined TFT_GIF (
    echo ERROR: The video converter did not report a TFT GIF path.
    set "RESULT=1"
    goto :failed
)

echo Creating OLED animation frames...
python "%SCRIPT_DIR%xmbgenarator.py" "%OLED_GIF%"
if errorlevel 1 goto :oled_failed

echo Combining OLED frames...
python "%SCRIPT_DIR%Monochrome.py"
if errorlevel 1 goto :header_failed

echo Creating TFT SD-card frames...
python "%SCRIPT_DIR%tft_boot_converter.py" "%TFT_GIF%"
if errorlevel 1 goto :tft_failed

echo Complete. OLED header: all_frames.h. TFT frames: tft_boot_frames.
popd
exit /b 0

:conversion_failed
del "%LOG_FILE%"
set "FAIL_MESSAGE=Video-to-GIF conversion failed."
goto :failed

:oled_failed
set "RESULT=%ERRORLEVEL%"
set "FAIL_MESSAGE=OLED frame conversion failed."
goto :failed

:header_failed
set "RESULT=%ERRORLEVEL%"
set "FAIL_MESSAGE=OLED header generation failed."
goto :failed

:tft_failed
set "RESULT=%ERRORLEVEL%"
set "FAIL_MESSAGE=TFT frame conversion failed."
goto :failed

:failed
if not defined RESULT set "RESULT=1"
if "%RESULT%"=="0" set "RESULT=1"
color 0C
if defined FAIL_MESSAGE echo FAILED: %FAIL_MESSAGE%
echo Stopping. Review the error above, fix it, and try again.
popd
exit /b %RESULT%
