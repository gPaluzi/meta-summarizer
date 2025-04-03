import os
import exifread
import ffmpeg
import pandas as pd
from datetime import datetime

def concatenate_folder(root:str, file:str):
    
    if file.endswith((".JPG", ".MP4", ".MOV")):

        file_path = os.path.join(root, file)
        file_path = os.path.normpath(file_path)

        path_parts = os.path.normpath(root).split(os.sep)
                
        station_id = path_parts[-3] if len(path_parts) == 4 else path_parts[-2]

        picture_folder = path_parts[-2] if len(path_parts) == 4 else path_parts[-1]

    if not picture_folder.startswith(("PIC", "VID")) and len(picture_folder.split("_") != 4):
        print(f"{file_path} is incorrect path")
        return None

    parts = picture_folder.split("_")
    mode, camera_id, memory_id, _ = parts

    camera_id = camera_id[-3:]
    memory_id = memory_id[-3:]
                
    return [station_id, camera_id, memory_id, mode, file_path]

def initial_check(folder_path):

    """
    load the control sheet and check is the directory is already correct with the sheet

    if something there is something miss, dont continue the process and check the corresponding one

    q: what if there is something wrong and keep want to continue? so edit the folder name follow the control sheet

    maybe its better to create the folder based on the control sheet...
    """

    data = []

    for root, dirs, files in os.walk(folder_path):

        for file in files:
            
            data.append(concatenate_folder(root, file))

    return data


def create_id_table(data:list):
    unique_camera_id = {}

    for row in data:
        station_id, camera_id, memory_id, mode, _ = row

        if camera_id not in unique_camera_id:
            unique_camera_id[camera_id] = [station_id, camera_id, memory_id, mode]
    
    id_data = list(unique_camera_id.values())

    df = pd.DataFrame(id_data, columns=["Station_id", "Camera_id", "Memory_id", "Mode"])

    return df

## This is how to extract metadata from image file
def extract_img_metadata(image_path):
    try:
        with open(image_path, 'rb') as img_file:
            tags = exifread.process_file(img_file, details= False)

            maker = tags.get('Image Make', None)
            model = tags.get('Image Model', None)
            datetime = tags.get('EXIF DateTimeOriginal', None)

        return [maker, model, datetime]
    
    except (IOError, Exception) as e:
        print(f"Error reading EXIF data for {image_path}: {e}")
        return None

def extract_vid_metadata(mp4_path):
    try:
        metadata = ffmpeg.probe(mp4_path, v='error', select_streams='v:0', show_entries='stream=codec_name,width,height,nb_frames,duration')

        datetime_str = metadata.get('streams')[0].get('tags', {}).get("creation_time", {})
        dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        duration = metadata.get('streams')[0].get('duration')

        return [dt, duration]
    except ffmpeg.Error as e:
        print(f"Error extracting metadata for {mp4_path}: {e}")
        return None

def create_photos_table(data: list):
    photos_data = []
    photo_id_counter = 1

    """
    inside for loop, check is the filepath is extracted in img/video table so its not extracted twice.

    after the extraction add the new table to the existed one,

    maybe its better to add this function in intitial check, add a new index in the data represent metadata presence by img/video path
    """

    for row in data:
        _, camera_id, _, _, file_path = row

        if not file_path.endswith(".JPG"):
            continue

        print(f"extracting: {file_path}")

        maker, model, datetime = extract_img_metadata(file_path) 

        photo_id = photo_id_counter
        photo_id_counter += 1

        photos_data.append([photo_id, camera_id, maker, model, datetime, file_path])

    photos_df = pd.DataFrame(photos_data, columns=["Photo_id", "Camera_id", "Maker", "Model", "Datetime", "File_path"])

    return photos_df

def create_vid_table(data: list):
    video_data = []
    video_id_counter = 1

    for row in data:
        video_id = video_id_counter
        video_id_counter += 1
        _, camera_id, _, _, file_path = row

        if not file_path.endswith((".MOV", ".MP4")):
            continue

        print(f"extracting: {file_path}")
        metadata = extract_vid_metadata(file_path)

        if metadata:
            dt, duration = metadata
            video_data.append([video_id, camera_id, dt, duration, file_path])

        else:
            video_data.append([video_id, camera_id, None, None, file_path])

        

    video_df = pd.DataFrame(video_data, columns=["Video_id", "Camera_id", "Datetime", "Duration", "File_path"])

    return video_df