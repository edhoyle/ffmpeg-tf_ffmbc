import subprocess
import os
from concurrent.futures import ThreadPoolExecutor
from pymediainfo import MediaInfo

def run_command(command):
    command.insert(1, '-nostdin')
    print(f"Running command: {' '.join(command)}")  # Print the command
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if process.stdout:
        print(f"STDOUT: {process.stdout}")
    if process.stderr:
        print(f"STDERR: {process.stderr}")

def get_video_duration(input_file):
    media_info = MediaInfo.parse(input_file)
    for track in media_info.tracks:
        if track.track_type == 'Video':
            return float(track.duration) / 1000  # Convert from milliseconds to seconds
    return None

def split_video(input_file, segment_time, output_folder):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-c', 'copy',
        '-map', '0',
        '-segment_time', str(segment_time),
        '-f', 'segment',
        f'{output_folder}/segment_%03d.mp4'
    ]
    run_command(command)

def apply_single_filter(input_path, output_path):
    command = [
        'ffmpeg',
        '-i', input_path,
        '-vf', 'scale=iw/2:-1', '-y',
        output_path
    ]
    run_command(command)

def apply_filter_concurrent(input_folder, output_folder):
    with ThreadPoolExecutor() as executor:
        futures = []
        
        for segment in os.listdir(input_folder):
            input_path = os.path.join(input_folder, segment)
            output_path = os.path.join(output_folder, segment)
            
            futures.append(executor.submit(apply_single_filter, input_path, output_path))
        
        for future in futures:
            future.result()

def concatenate_videos(input_folder, output_file):
    with open("concat_list.txt", "w") as f:
        for segment in sorted(os.listdir(input_folder)):
            f.write(f"file '{os.path.join(input_folder, segment)}'\n")
    
    command = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'concat_list.txt',
        '-c', 'copy', '-y',
        output_file
    ]
    run_command(command)


def main():
    input_file = 'input.mp4'
    total_duration = get_video_duration(input_file)
    
    if total_duration is None:
        print("Could not fetch video duration.")
        return
    
    num_pieces = 3  # Number of pieces to split the video into
    segment_time = total_duration / num_pieces
    
    temp_folder = 'temp_segments'
    filtered_folder = 'filtered_segments'
    output_file = 'output.mp4'
    
    os.makedirs(temp_folder, exist_ok=True)
    os.makedirs(filtered_folder, exist_ok=True)
    
    print(f'Splitting video into {num_pieces} pieces...')
    split_video(input_file, segment_time, temp_folder)
    
    print('Applying video filter concurrently...')
    apply_filter_concurrent(temp_folder, filtered_folder)
    
    print('Concatenating segments...')
    concatenate_videos(filtered_folder, output_file)
    
    print('Done!')

if __name__ == '__main__':
    main()
