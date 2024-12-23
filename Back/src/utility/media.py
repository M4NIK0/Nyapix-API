import os
import subprocess

def split_video(video_path: str, output_path: str, duration: int = 10, bitrate: str = "1000k"):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file {video_path} not found")

    # Ensure the output path ends with a slash
    output_path = os.path.join(output_path, "")

    # Run ffmpeg command
    subprocess.run(
        [
            "ffmpeg", "-i", video_path, "-map", "0",
            "-b:v", bitrate, "-b:a", "128k",
            "-seg_duration", str(duration), "-frag_duration", str(duration),
            "-init_seg_name", "init.mp4",
            "-f", "dash", os.path.join(output_path, "manifest.mpd")
        ],
        check=True
    )

def convert_video_to_mp4(video_path: str) -> str:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file {video_path} not found")
    subprocess.run(
        [
            "ffmpeg", "-i", video_path, "-c", "copy", video_path + ".converted.mp4"
        ],
        check=True
    )
    return video_path + ".converted.mp4"

def get_video_length(file_path: str) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return float(result.stdout)

def convert_image_to_png(image_path: str) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file {image_path} not found")
    subprocess.run(
        [
            "ffmpeg", "-i", image_path, f"{image_path}.png"
        ],
        check=True
    )

    return f"{image_path}.png"

def generate_video_miniature(video_path: str, time: int = 15, size: str = "320x240") -> str:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file {video_path} not found")

    # Ensure the output path ends with a slash
    output_path = os.path.join(video_path, ".miniature")

    # Run ffmpeg command
    subprocess.run(
        [
            "ffmpeg", "-i", video_path, "-ss", str(time), "-vframes", "1", "-s", size, os.path.join(output_path, ".png")
        ],
        check=True
    )
    return os.path.join(output_path, ".png")
