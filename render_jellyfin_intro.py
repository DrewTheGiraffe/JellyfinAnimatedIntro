#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


WIDTH = 1004
HEIGHT = 288
FPS = 30
DURATION = 3.0
FRAME_COUNT = int(FPS * DURATION)

ICON_RIGHT = 330
TEXT_LEFT = 330


def smoothstep(edge0: float, edge1: float, value):
    """Smooth interpolation from 0 to 1."""
    value = np.asarray(value, dtype=np.float32)
    amount = np.clip((value - edge0) / (edge1 - edge0), 0.0, 1.0)
    return amount * amount * (3.0 - 2.0 * amount)


def run_command(command: list[str]) -> None:
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg failed.\n\n"
            + result.stderr.strip()
        )


def load_logo(path: Path) -> np.ndarray:
    if not path.is_file():
        raise FileNotFoundError(f"Logo file not found: {path}")

    image = Image.open(path).convert("RGBA")

    source_ratio = image.width / image.height
    target_ratio = WIDTH / HEIGHT

    if abs(source_ratio - target_ratio) > 0.002:
        raise ValueError(
            f"Expected a {WIDTH}:{HEIGHT} aspect ratio, "
            f"but received {image.width} × {image.height}."
        )

    if image.size != (WIDTH, HEIGHT):
        image = image.resize(
            (WIDTH, HEIGHT),
            Image.Resampling.LANCZOS,
        )

    rgba = np.asarray(image, dtype=np.float32) / 255.0

    # Some exported versions of this logo contain an opaque black
    # background rather than real transparency. Detect and key it out.
    corners_rgb = np.stack(
        [
            rgba[0, 0, :3],
            rgba[0, -1, :3],
            rgba[-1, 0, :3],
            rgba[-1, -1, :3],
        ]
    )
    corners_alpha = np.array(
        [
            rgba[0, 0, 3],
            rgba[0, -1, 3],
            rgba[-1, 0, 3],
            rgba[-1, -1, 3],
        ]
    )

    opaque_black_background = (
        np.min(corners_alpha) > 0.99
        and np.max(corners_rgb) < 0.05
    )

    if opaque_black_background:
        brightness = np.max(rgba[..., :3], axis=2)
        keyed_alpha = smoothstep(
            2.0 / 255.0,
            20.0 / 255.0,
            brightness,
        )
        rgba[..., 3] = keyed_alpha

    rgba[rgba[..., 3] < 1.0 / 255.0, :3] = 0.0
    return rgba


def composite_over(
    background_premultiplied: np.ndarray,
    background_alpha: np.ndarray,
    foreground_rgb: np.ndarray,
    foreground_alpha: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Alpha-composite a foreground over a premultiplied background."""
    foreground_alpha = np.clip(foreground_alpha, 0.0, 1.0)
    foreground_alpha_3d = foreground_alpha[..., None]

    output_premultiplied = (
        foreground_rgb * foreground_alpha_3d
        + background_premultiplied * (1.0 - foreground_alpha_3d)
    )
    output_alpha = (
        foreground_alpha
        + background_alpha * (1.0 - foreground_alpha)
    )

    return output_premultiplied, output_alpha


def render_frames(logo: np.ndarray, directory: Path) -> None:
    rgb = logo[..., :3]
    source_alpha = logo[..., 3]

    y_grid, x_grid = np.mgrid[0:HEIGHT, 0:WIDTH]
    x_grid = x_grid.astype(np.float32)
    y_grid = y_grid.astype(np.float32)

    icon_region = (x_grid < ICON_RIGHT).astype(np.float32)
    text_region = (x_grid >= TEXT_LEFT).astype(np.float32)

    icon_alpha = source_alpha * icon_region
    text_alpha = source_alpha * text_region

    # Derive an outline from the source alpha mask.
    icon_mask_image = Image.fromarray(
        np.uint8(np.clip(icon_alpha, 0.0, 1.0) * 255.0),
        mode="L",
    )
    eroded = np.asarray(
        icon_mask_image.filter(ImageFilter.MinFilter(9)),
        dtype=np.float32,
    ) / 255.0

    outline_alpha = np.clip(
        (icon_alpha - eroded) * 2.0,
        0.0,
        1.0,
    )

    # Clockwise trace coordinate, beginning at the top.
    center_x = 145.0
    center_y = 144.0
    trace_coordinate = (
        (
            np.arctan2(
                y_grid - center_y,
                x_grid - center_x,
            )
            + np.pi / 2.0
        )
        % (2.0 * np.pi)
    ) / (2.0 * np.pi)

    # Diagonal gradient-fill sweep across the icon.
    sweep_coordinate = (
        x_grid + 0.38 * (HEIGHT - 1.0 - y_grid)
    ) / (
        ICON_RIGHT - 1.0 + 0.38 * (HEIGHT - 1.0)
    )
    sweep_coordinate = np.clip(sweep_coordinate, 0.0, 1.0)

    # Left-to-right coordinate across the wordmark.
    text_coordinate = (
        x_grid - 350.0
    ) / (
        WIDTH - 1.0 - 350.0
    )
    text_coordinate = np.clip(text_coordinate, 0.0, 1.0)

    bright_outline_rgb = np.clip(
        rgb * 0.68 + 0.32,
        0.0,
        1.0,
    )
    white_rgb = np.ones_like(rgb)

    for frame_number in range(FRAME_COUNT):
        time_seconds = frame_number / FPS

        # Symbol outline: 0.00–0.70 seconds.
        trace_progress = smoothstep(
            0.00,
            0.70,
            time_seconds,
        )
        trace_feather = 0.035
        trace_reveal = np.clip(
            (
                trace_progress * (1.0 + trace_feather)
                - trace_coordinate
            )
            / trace_feather,
            0.0,
            1.0,
        )

        # Let the bright trace disappear after the fill is established.
        trace_fade = 1.0 - smoothstep(
            0.95,
            1.22,
            time_seconds,
        )
        active_outline_alpha = (
            outline_alpha
            * trace_reveal
            * trace_fade
        )

        # Gradient sweep: 0.22–1.00 seconds.
        fill_progress = smoothstep(
            0.22,
            1.00,
            time_seconds,
        )
        sweep_feather = 0.10
        fill_reveal = np.clip(
            (
                fill_progress * (1.0 + sweep_feather)
                - sweep_coordinate
            )
            / sweep_feather,
            0.0,
            1.0,
        )
        active_fill_alpha = icon_alpha * fill_reveal

        # A narrow highlight follows the gradient sweep.
        highlight_band = np.exp(
            -0.5
            * (
                (sweep_coordinate - fill_progress)
                / 0.042
            )
            ** 2
        )
        highlight_strength = np.sin(
            np.pi * fill_progress
        )
        highlight_alpha = (
            icon_alpha
            * fill_reveal
            * highlight_band
            * highlight_strength
            * 0.28
        )

        # Wordmark: 0.72–1.42 seconds.
        text_progress = smoothstep(
            0.72,
            1.42,
            time_seconds,
        )
        text_feather = 0.12
        text_reveal = np.clip(
            (
                text_progress * (1.0 + text_feather)
                - text_coordinate
            )
            / text_feather,
            0.0,
            1.0,
        )
        active_text_alpha = (
            text_alpha
            * text_progress
            * text_reveal
        )

        premultiplied = np.zeros(
            (HEIGHT, WIDTH, 3),
            dtype=np.float32,
        )
        output_alpha = np.zeros(
            (HEIGHT, WIDTH),
            dtype=np.float32,
        )

        premultiplied, output_alpha = composite_over(
            premultiplied,
            output_alpha,
            rgb,
            active_fill_alpha,
        )
        premultiplied, output_alpha = composite_over(
            premultiplied,
            output_alpha,
            white_rgb,
            highlight_alpha,
        )
        premultiplied, output_alpha = composite_over(
            premultiplied,
            output_alpha,
            bright_outline_rgb,
            active_outline_alpha,
        )
        premultiplied, output_alpha = composite_over(
            premultiplied,
            output_alpha,
            rgb,
            active_text_alpha,
        )

        output_rgb = np.divide(
            premultiplied,
            output_alpha[..., None],
            out=np.zeros_like(premultiplied),
            where=output_alpha[..., None] > 1e-6,
        )

        frame = np.dstack(
            [
                np.clip(output_rgb, 0.0, 1.0),
                np.clip(output_alpha, 0.0, 1.0),
            ]
        )
        frame = np.uint8(frame * 255.0 + 0.5)

        Image.fromarray(
            frame,
            mode="RGBA",
        ).save(
            directory / f"frame_{frame_number:04d}.png"
        )


def encode_outputs(
    ffmpeg: str,
    frames: Path,
    output_directory: Path,
) -> tuple[Path, Path]:
    alpha_output = output_directory / "jellyfin_logo_intro_alpha.mov"
    mp4_output = output_directory / "jellyfin_logo_intro.mp4"
    frame_pattern = str(frames / "frame_%04d.png")

    # Transparent ProRes 4444 master.
    run_command(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-framerate",
            str(FPS),
            "-i",
            frame_pattern,
            "-frames:v",
            str(FRAME_COUNT),
            "-c:v",
            "prores_ks",
            "-profile:v",
            "4",
            "-pix_fmt",
            "yuva444p10le",
            "-an",
            str(alpha_output),
        ]
    )

    # Compatibility MP4 preview over black.
    filter_graph = (
        "[0:v]format=rgba[background];"
        "[background][1:v]"
        "overlay=0:0:shortest=1:format=auto,"
        "format=yuv420p,"
        "setsar=1[video]"
    )

    run_command(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            (
                f"color=c=black:"
                f"s={WIDTH}x{HEIGHT}:"
                f"r={FPS}:"
                f"d={DURATION}"
            ),
            "-framerate",
            str(FPS),
            "-i",
            frame_pattern,
            "-filter_complex",
            filter_graph,
            "-map",
            "[video]",
            "-frames:v",
            str(FRAME_COUNT),
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-preset",
            "medium",
            "-movflags",
            "+faststart",
            "-an",
            str(mp4_output),
        ]
    )

    return alpha_output, mp4_output


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Render a three-second Jellyfin logo entrance "
            "at 1004 × 288 pixels."
        )
    )
    parser.add_argument(
        "logo",
        type=Path,
        help="Path to the Jellyfin PNG logo.",
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path("."),
        help="Directory for the rendered MOV and MP4 files.",
    )
    args = parser.parse_args()

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise SystemExit(
            "FFmpeg was not found. Install FFmpeg and make sure "
            "the ffmpeg command is available in PATH."
        )

    args.output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    logo = load_logo(args.logo)

    with tempfile.TemporaryDirectory(
        prefix="jellyfin_intro_"
    ) as temporary_directory:
        frame_directory = Path(temporary_directory)
        render_frames(logo, frame_directory)

        alpha_output, mp4_output = encode_outputs(
            ffmpeg,
            frame_directory,
            args.output_directory,
        )

    print(f"Transparent master: {alpha_output.resolve()}")
    print(f"MP4 preview:       {mp4_output.resolve()}")


if __name__ == "__main__":
    main()