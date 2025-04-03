import matplotlib
import os
import pandas as pd
import numpy as np
import shutil

def load_data():
    print("Reading table...")
    id_table = pd.read_csv("./outputs/id_table.csv")
    image_table = pd.read_csv("./outputs/image_table.csv")
    video_table = pd.read_csv("./outputs/video_table.csv")
    
    return id_table, image_table, video_table

def check_output_directory(path: str):

    if not os.path.exists(path):
        os.makedirs(path)

    path = os.path.join(path, 'corrupted_file')

    if not os.path.exists(path):
        os.makedirs(path)

    return print(f"corrupted file will be stored here '{path}'")

def list_corrupted_file(img_table, vid_table):
    
    corrupted_img = img_table[img_table['Datetime'].isna()]

    corrupted_vid = vid_table[vid_table['Datetime'].isna()]

    corrupted_files = corrupted_img['File_path'].to_list() + corrupted_vid['File_path'].to_list()

    return corrupted_files

"""# 
Copying corrupted file is not necessary, because corrupted file cant opened and has no any information
maybe its better to delete it and create a list of which files is corrupted
"""
def copy_corrupted_file(corrupted_file, output_folder: str = ".\outputs"):

    check_output_directory(output_folder)

    for filepath in corrupted_file:
        filename = os.path.basename(filepath)

        try:

            part = os.path.normpath(filepath).split(os.sep)

            station = part[-4] if len(part) == 5 else part[-3]

            
            destination = os.path.join(output_folder, station, filename)

            station_dir = os.path.join(output_folder, station)
            if not os.path.exists(station_dir):
                os.makedirs(station_dir)

            # print(destination)
            shutil.copy(filepath, destination)


        except Exception as e:
            print(f"Failed to copy this file {filepath}")





id_table, image_table, video_table = load_data()

path = r".\outputs\corrupted_file"


corrupted_list = list_corrupted_file(image_table, video_table)

print(f"Total corrupted file: {len((corrupted_list))}")
print(corrupted_list[:5])

copy_corrupted_file(corrupted_list, output_folder=path)








# table = pd.merge(id_table, image_table, on="Camera_id", how="outer")
# print(table.columns)
# print(table.head())

# print(f"Total corrupted image: {image_table['Datetime'].isnull().sum()}")
# print(f"Total corrupted video: {video_table['Datetime'].isnull().sum()}")
# print(image_table.head())
# print(video_table.head())