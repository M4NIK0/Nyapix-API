import os
import subprocess

def split_video(video_path: str, output_path: str, duration: int=10):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file {video_path} not found")
    subprocess.run(
        [
            "ffmpeg", "-i", video_path, "-c:v", "libx264", "-c:a", "aac", "-f", "segment",
            "-segment_time", str(duration), "-reset_timestamps", "1", "-movflags",
            "frag_keyframe+empty_moov", f"{output_path}/%04d.mp4"
        ],
        check=True
    )

def convert_image_to_png(image_path: str):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file {image_path} not found")
    subprocess.run(
        [
            "ffmpeg", "-i", image_path, f"{image_path}.png"
        ],
        check=True
    )
