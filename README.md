Imported from Creckercodes(my account that I no longer have acsess to, thanks 2fa)

# Arduino-OLED-Animation
Convert animations into frames for Arduino displays.

## OLED animation

The existing OLED scripts create monochrome XBM frames and combine them into
`all_frames.h`. See `SSD1306.h` for the example Arduino playback sketch.

## TFT SD-card boot animation

For a 2.8-inch ILI9341 TFT driven by TFT_eSPI, `tft_boot_converter.py` converts
an animation into numbered BMP images for the SD card. Each frame uses the
TFT's full 320x240 landscape resolution and Floyd-Steinberg dithering to
represent grayscale detail using only black and white pixels. The source is
fitted proportionally and centered on black rather than stretched. The BMPs
are uncompressed 24-bit files for broad decoder compatibility, but every pixel
is strictly black or white. Transparent GIF areas become black.

1. Install Pillow if it is not already installed:

   ```powershell
   python -m pip install pillow
   ```

2. From this folder, run the converter. If `CONVERT.gif` is present it is used
   by default; otherwise, if there is exactly one GIF in the folder, that GIF
   is used:

   ```powershell
   python tft_boot_converter.py
   ```

   To choose a specific animation, provide its path:

   ```powershell
   python tft_boot_converter.py "C:\path\to\animation.gif"
   ```

3. Copy the numbered `frame_000.bmp`, `frame_001.bmp`, etc. from
   `tft_boot_frames` to the TFT's SD card. Open `preview.gif` to see the
   full-resolution animation, or `preview.png` for a still preview. These
   previews are for your computer and should not be copied to the SD card for
   firmware playback.

4. In the ESP32 firmware, initialize the SD card and TFT_eSPI, then have a BMP
   decoder draw each frame at `(0, 0)` at native size on a 320x240 landscape
   display. The firmware's BMP reader must support uncompressed 24-bit BMP
   files.

## Convert a video to a display-sized GIF

`video_to_gif.py` searches the folder containing this project and its
subfolders for a video. If exactly one is found, it creates both a 128x64 OLED
GIF and a 320x240 TFT GIF in a `converted_gifs` folder beside the video:

```powershell
python video_to_gif.py
```

If more than one video is found, provide the path to the one to convert.
Choose one display with `--target oled` or `--target tft`; the default is
`--target both`. Use `--search-dir` to change the search tree, `--fps` to
adjust the output frame rate, or `-o` to choose an output folder:

```powershell
python video_to_gif.py "C:\path\to\animation.mp4" --target oled --fps 8
```

Use the OLED GIF as the source GIF in `xmbgenarator.py`; pass the TFT GIF to
`tft_boot_converter.py` to create the SD-card BMP frames. Videos are fitted
proportionally on a black background and converted to grayscale. Audio is
omitted.

FFmpeg must be installed and available on `PATH` (`ffmpeg -version` should
work). Pillow is needed by the existing image-to-frame converters:

```powershell
python -m pip install pillow
```

## Run the complete conversion

From PowerShell, run `Operation.bat` to make the OLED header and TFT BMP
frames from a video. With no argument, it searches for exactly one video under
the folder containing this project. To select a video explicitly:

```powershell
.\Arduino-OLED-Animation\Operation.bat "C:\path\to\animation.mp4"
```

including the path should only be necessary for if you added multiple video files as running operation.bat should capture the video file automatically or if you plan on only converting for one use case instead of both at the same time.

The batch file runs from its own folder, so it can also be launched from
another working directory. It stops and reports an error if any conversion
step fails.
