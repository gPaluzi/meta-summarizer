import os
import exifread
import ffmpeg
import pandas as pd
from datetime import datetime
from tqdm import tqdm
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

def load_control_sheet(folder_path):

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".csv"):
                path = os.path.join(root, file)
                break
        if path:
            break

    sheet = pd.read_csv(path)
    return sheet

def _check_extension(dir):
    if dir.endswith((".JPG", ".MP4", ".MOV")):
        return True
    else:
        return False

def concatenate_folder(root:str, file:str) -> list:

    if _check_extension(file):

        file_path = os.path.join(root, file)
        file_path = os.path.normpath(file_path)

        path_parts = os.path.normpath(root).split(os.sep)
        
        station_id = path_parts[1]
        camera_id = path_parts[2]
        filesize = os.path.getsize(file_path)

    return [station_id, camera_id, filesize, file_path]

def initial_check(folder_path) -> list:

    """
    load the control sheet and check is the directory is already correct with the sheet
    if something there is something miss, dont continue the process and check the corresponding one
    q: what if there is something wrong and keep want to continue? so edit the folder name follow the control sheet
    note: maybe its better to create the folder based on the control sheet...
    """

    data = []

    for root, dirs, files in os.walk(folder_path):

        for file in files:
            if not _check_extension(file):
                continue
            
            data.append(concatenate_folder(root, file))

    return data

def create_id_table(data:list):
    unique_camera_id = {}

    for row in data:
        station_id, camera_id, filesize, file_path= row

        if camera_id not in unique_camera_id:
            unique_camera_id[camera_id] = [station_id, camera_id, file_path]
    
    id_data = list(unique_camera_id.values())

    df = pd.DataFrame(id_data, columns=["stationID", "cameraID", "filePath"])

    return df

def extract_img_metadata(image_path):
    filesize = os.path.getsize(image_path)
    try:
        with Image.open(image_path) as img:
            img.verify()

        with open(image_path, 'rb') as img_file:
            tags = exifread.process_file(img_file, details= False)

            maker = tags.get('Image Make', None)
            model = tags.get('Image Model', None)
            datetime = tags.get('EXIF DateTimeOriginal', None)
            

        return [maker, model, datetime, filesize]
    
    except (IOError, Exception) as e:
        return [None, None, None, filesize]

def extract_vid_metadata(mp4_path):
    filesize = os.path.getsize(mp4_path)
    try:
        metadata = ffmpeg.probe(mp4_path, v='error', show_entries='format_tags=creation_time,format=duration')

        datetime_str = metadata.get('streams')[0].get('tags', {}).get("creation_time", {})
        dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        duration = metadata.get('streams')[0].get('duration')

        return [dt, duration, filesize]
    except ffmpeg.Error as e:
        return [None, None, filesize]

def process_photos(row):
    station_id, camera_id, filesize, file_path= row
    if not file_path.endswith(".JPG"):
        return None
    
    maker, model, dt, filesize = extract_img_metadata(file_path)
    return [station_id, camera_id, maker, model, dt, filesize, file_path]

def create_photos_table(data: list):
    photos_data = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        result = list(tqdm(executor.map(process_photos, data), total=len(data), desc="Extracting Photos"))

    photo_id_counter = 1
    for res in result:
        if res:
            station_id, camera_id, maker, model, dt, file_size, file_path = res
            photos_data.append([photo_id_counter, station_id, camera_id, maker, model, dt, file_size, file_path])
            photo_id_counter =+ 1

    photos_df = pd.DataFrame(photos_data, columns=["photoID", "stationID", "cameraID", "maker", "model", "dateTime", "filesize", "filePath"])
    photos_df["dateTime"] = pd.to_datetime(photos_df["dateTime"], format='%Y:%m:%d %H:%M:%S')

    return photos_df

def process_videos(row):
    station_id, camera_id, filesize, file_path = row
    if not file_path.endswith((".MP4", ".MOV")):
        return None
    dt, duration, filesize = extract_vid_metadata(file_path)
    return [station_id, camera_id, dt, duration, filesize, file_path]

def create_vid_table(data: list):
    video_data = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        result = list(tqdm(executor.map(process_videos, data), total=len(data), desc="Extracting Videos"))

    video_id_counter = 1
    for res in result:
        if res:
            station_id, camera_id, dt, duration, filesize, file_path = res
            video_data.append([video_id_counter, station_id, camera_id, dt, duration, filesize, file_path])
            video_id_counter =+ 1

    video_df = pd.DataFrame(video_data, columns=["videoID", "stationID", "cameraID", "dateTime", "duration", "filesize", "filePath"])
    return video_df