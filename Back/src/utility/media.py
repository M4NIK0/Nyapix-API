import os
import subprocess
import json

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

def convert_audio_to_wav(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file {file_path} not found")
    subprocess.run(
        [
            "ffmpeg", "-i", file_path, "-acodec", "pcm_s16le", "-ar", "48000", file_path + ".wav"
        ],
        check=True
    )
    return file_path + ".wav"

def get_video_definition(video_path: str) -> dict:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file {video_path} not found")
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", video_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    # Parse the JSON output
    data = json.loads(result.stdout)
    return data["streams"][0]

def get_image_definition(image_path: str) -> dict:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file {image_path} not found")
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", image_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    # Parse the JSON output
    data = json.loads(result.stdout)
    return data["streams"][0]

def generate_video_miniature(video_path: str, time: int = 15, max_size: int = 480) -> str:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file {video_path} not found")

    size = get_video_definition(video_path)

    if size["width"] > size["height"]:
        width_ratio = max_size / size["width"]
        height_ratio = width_ratio
    else:
        height_ratio = max_size / size["height"]
        width_ratio = height_ratio

    subprocess.run(
        [
            "ffmpeg", "-i", video_path, "-ss", str(time), "-vframes", "1", "-vf", f"scale={int(size['width'] * width_ratio)}:{int(size['height'] * height_ratio)}", f"{video_path}.png"
        ],
        check=True
    )

    return f"{video_path}.png"

def generate_image_miniature(image_path: str, max_size: int = 480) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file {image_path} not found")

    size = get_image_definition(image_path)

    if size["width"] > size["height"]:
        width_ratio = max_size / size["width"]
        height_ratio = width_ratio
    else:
        height_ratio = max_size / size["height"]
        width_ratio = height_ratio

    subprocess.run(
        [
            "ffmpeg", "-i", image_path, "-vf", f"scale={int(size['width'] * width_ratio)}:{int(size['height'] * height_ratio)}", f"{image_path}.png"
        ],
        check=True
    )

    return f"{image_path}.png"
