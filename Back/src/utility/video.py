import os

def split_video(video_path: str, output_path: str, duration: int=10):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file {video_path} not found")
    os.system(f"ffmpeg -i {video_path} -c:v libx264 -c:a aac -f segment -segment_time {duration} -reset_timestamps 1 -movflags frag_keyframe+empty_moov {output_path}/chunk%03d.mp4")
