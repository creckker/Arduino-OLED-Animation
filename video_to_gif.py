"""Find a video and convert it to a display-sized animated grayscale GIF."""

import argparse
import math
import shutil
import subprocess
from pathlib import Path


DISPLAY_SIZES = {
    "oled": (128, 64),
    "tft": (320, 240),
}
VIDEO_EXTENSIONS = {
    ".3gp",
    ".avi",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".webm",
    ".wmv",
}


def find_video(search_dir: Path, parser: argparse.ArgumentParser) -> Path:
    if not search_dir.is_dir():
        parser.error(f"Search folder not found: {search_dir}")

    videos = sorted(
        path
        for path in search_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
    )
    if not videos:
        parser.error(f"No supported video files found under: {search_dir}")
    if len(videos) > 1:
        names = "\n".join(f"  {path}" for path in videos)
        parser.error(
            f"Found multiple videos under {search_dir}; provide an input path:\n"
            f"{names}"
        )
    return videos[0]


def convert_video(
    input_path: Path,
    output_path: Path,
    size: tuple[int, int],
    fps: float,
    ffmpeg: str,
    parser: argparse.ArgumentParser,
) -> None:
    width, height = size
    filters = (
        f"fps={fps:g},"
        f"scale={width}:{height}:force_original_aspect_ratio=decrease:flags=lanczos,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,"
        "format=gray,split[s0][s1];"
        "[s0]palettegen=max_colors=256:reserve_transparent=0[p];"
        "[s1][p]paletteuse=dither=sierra2_4a"
    )
    result = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(input_path),
            "-an",
            "-vf",
            filters,
            "-loop",
            "0",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip() or "FFmpeg returned an error."
        parser.error(f"Could not convert {input_path}:\n{detail}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Find a video in the project tree and make an OLED-sized, "
            "TFT-sized, or both display-sized GIFs."
        )
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="video to convert (default: find the only video in the project tree)",
    )
    parser.add_argument(
        "--search-dir",
        type=Path,
        help="tree to search when input is omitted (default: project folder)",
    )
    parser.add_argument(
        "--target",
        choices=("oled", "tft", "both"),
        default="both",
        help="display size to create (default: both)",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=10.0,
        help="output frame rate (default: 10; lower values make smaller GIFs)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="output folder (default: converted_gifs beside the video)",
    )
    args = parser.parse_args()

    if not math.isfinite(args.fps) or args.fps <= 0:
        parser.error("--fps must be a finite number greater than zero.")

    if args.input is not None:
        input_path = args.input.resolve()
    else:
        search_dir = (
            args.search_dir.resolve()
            if args.search_dir is not None
            else Path(__file__).resolve().parent.parent
        )
        input_path = find_video(search_dir, parser)

    if not input_path.is_file():
        parser.error(f"Input video not found: {input_path}")

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        parser.error(
            "FFmpeg was not found on PATH. Install FFmpeg, reopen the terminal, "
            "and confirm `ffmpeg -version` works."
        )

    output_dir = (
        args.output_dir.resolve()
        if args.output_dir is not None
        else input_path.parent / "converted_gifs"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    targets = (
        DISPLAY_SIZES
        if args.target == "both"
        else {args.target: DISPLAY_SIZES[args.target]}
    )
    for target, size in targets.items():
        output_path = output_dir / f"{input_path.stem}_{target}.gif"
        convert_video(input_path, output_path, size, args.fps, ffmpeg, parser)
        print(f"Created {target.upper()} GIF ({size[0]}x{size[1]}): {output_path}")


if __name__ == "__main__":
    main()
