import os
import pandas as pd
import numpy as np
import shutil
from functools import reduce
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

def load_data() -> pd.DataFrame: 
    print("Reading table...")
    id_table = pd.read_csv("./outputs/id_table.csv", index_col="Camera_id")
    image_table = pd.read_csv("./outputs/image_table.csv", index_col="Camera_id")
    video_table = pd.read_csv("./outputs/video_table.csv", index_col="Camera_id")
    
    return id_table, image_table, video_table

def check_output_directory(path: str) -> str:

    path = os.path.join(path, 'corrupted_file')

    if not os.path.exists(path):
        os.makedirs(path)

    print(f"corrupted file will be stored here '{path}'")

    return path


def list_corrupted_file(img_table, vid_table) -> list:
    
    corrupted_img = img_table[img_table['Datetime'].isna()]

    corrupted_vid = vid_table[vid_table['Datetime'].isna()]

    corrupted_files = corrupted_img['File_path'].to_list() + corrupted_vid['File_path'].to_list()

    return corrupted_files

"""
Copying corrupted file is not necessary, because corrupted file cant opened and has no any information
maybe its better to delete/move it and create a list of which files is corrupted
"""
def copy_corrupted_file(corrupted_file: list, output_folder: str):

    output_folder = check_output_directory(output_folder)

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

def create_heatmap(image_table=None, video_table=None, id_table=None):

    print("Creating Heatmap...")
    
    if None in (image_table, video_table, id_table):
        id_table, image_table, video_table = load_data()

    # join table with id
    image_table = pd.merge(image_table, id_table, on="Camera_id", how="left")
    video_table = pd.merge(video_table, id_table, on="Camera_id", how="left")

    # convert string to datetime type
    image_table["Datetime"] = pd.to_datetime(image_table["Datetime"], format='%Y-%m-%d %H:%M:%S')
    video_table["Datetime"] = pd.to_datetime(video_table["Datetime"], format='%Y-%m-%d %H:%M:%S')

    # Extract date from datetime
    image_table['Date'] = image_table["Datetime"].dt.date
    video_table["Date"] = video_table["Datetime"].dt.date

    # get camera id, station id and date column
    image_table = image_table[["Station_Id", "Date"]]
    video_table = video_table[["Station_id", "Date"]]

    # Concate both table with assumption there is no twin id
    table = pd.concat([image_table, video_table]).dropna()

    # Count number of capture per camera per day
    capture_counts = table.groupby(["Camera_id", "Date"]).size().reset_index(name='capture_count')

    # Create pivot, and sort it by station id
    pivot_table = capture_counts.pivot(index='Camera_id', columns='Date', values='capture_count')
    pivot_table = pd.merge(pivot_table, id_table, on="Camera_id", how="left")
    pivot_table = pivot_table.sort_values(by="Station_id")
    pivot_table = pivot_table.iloc[:, :-4]

    # Create plot
    plt.figure(figsize=(10,6))

    palette = sns.color_palette("flare", as_cmap=True)
    sns.heatmap(pivot_table, cmap=palette, cbar_kws={'label': 'Capture Count'},
                zorder=2)

    plt.title('Camera Capture Counts by Date')
    plt.xlabel('Date')
    plt.ylabel('Camera ID')

    
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.grid(True, zorder=0, alpha=0.5, which="both",
             axis="x", )
    plt.show()
    
""" create an insertion to missing value in dates feature by concatenate foldername """

if __name__ == "__main__":

    create_heatmap()