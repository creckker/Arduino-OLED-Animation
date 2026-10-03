"""Convert an animated image to monochrome BMP frames for a TFT SD card."""

import argparse
from pathlib import Path

from PIL import Image, ImageSequence


TFT_FRAME_SIZE = (320, 240)


def make_tft_frame(frame: Image.Image) -> Image.Image:
    """Return a full-resolution, dithered black-and-white TFT frame."""
    rgba_frame = frame.convert("RGBA")
    black_background = Image.new("RGBA", rgba_frame.size, (0, 0, 0, 255))
    grayscale = Image.alpha_composite(black_background, rgba_frame).convert("L")
    scale = min(
        TFT_FRAME_SIZE[0] / grayscale.width,
        TFT_FRAME_SIZE[1] / grayscale.height,
    )
    fitted_size = (
        max(1, round(grayscale.width * scale)),
        max(1, round(grayscale.height * scale)),
    )
    fitted_frame = grayscale.resize(fitted_size, Image.Resampling.LANCZOS)
    tft_grayscale = Image.new("L", TFT_FRAME_SIZE, 0)
    position = (
        (TFT_FRAME_SIZE[0] - fitted_size[0]) // 2,
        (TFT_FRAME_SIZE[1] - fitted_size[1]) // 2,
    )
    tft_grayscale.paste(fitted_frame, position)
    monochrome = tft_grayscale.convert(
        "1", dither=Image.Dither.FLOYDSTEINBERG
    )
    return monochrome.convert("RGB")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create dithered black-and-white 320x240 BMP frames for an ILI9341 TFT."
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="animated image to convert (if omitted, use the only GIF in this folder)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="output folder (default: tft_boot_frames next to the input)",
    )
    args = parser.parse_args()

    if args.input is not None:
        input_path = args.input.resolve()
    else:
        script_dir = Path(__file__).resolve().parent
        gif_files = sorted(
            path
            for path in script_dir.iterdir()
            if path.is_file() and path.suffix.lower() == ".gif"
        )
        preferred_input = script_dir / "CONVERT.gif"
        if preferred_input in gif_files:
            input_path = preferred_input
        elif len(gif_files) == 1:
            input_path = gif_files[0]
        elif not gif_files:
            parser.error(
                f"No GIF found next to {Path(__file__).name}; "
                "provide an input image path."
            )
        else:
            names = ", ".join(path.name for path in gif_files)
            parser.error(
                f"Multiple GIFs found ({names}); provide the image path to convert."
            )

    if not input_path.is_file():
        parser.error(
            f"Input image not found: {input_path}. "
            "Provide its correct path or place the image next to this script."
        )

    output_dir = (
        args.output_dir.resolve()
        if args.output_dir is not None
        else input_path.parent / "tft_boot_frames"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    output_frames = []
    durations = []
    with Image.open(input_path) as animation:
        for index, frame in enumerate(ImageSequence.Iterator(animation)):
            output_frame = make_tft_frame(frame)
            frame_path = output_dir / f"frame_{index:03d}.bmp"
            output_frame.save(frame_path, format="BMP")
            output_frames.append(output_frame)
            durations.append(frame.info.get("duration", 100))
            print(f"Saved {frame_path.name}")

    if output_frames:
        preview_path = output_dir / "preview.gif"
        output_frames[0].save(
            preview_path,
            save_all=True,
            append_images=output_frames[1:],
            duration=durations,
            loop=0,
        )
        still_preview_path = output_dir / "preview.png"
        output_frames[0].save(still_preview_path)
        print(
            f"Created {len(output_frames)} frames at "
            f"{TFT_FRAME_SIZE[0]}x{TFT_FRAME_SIZE[1]} in {output_dir}"
        )
        print(
            f"Full-screen preview saved as {preview_path.name} "
            f"and {still_preview_path.name}"
        )


if __name__ == "__main__":
    main()
