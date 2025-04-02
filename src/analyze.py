import matplotlib
import pandas as pd
import numpy as np

def load_data():
    id_table = pd.read_csv("./outputs/id_table.csv")
    image_table = pd.read_csv("./outputs/image_table.csv")
    video_table = pd.read_csv("./outputs/video_table.csv")
    
    return id_table, image_table, video_table

id_table, image_table, video_table = load_data()

print(f"Total corrupted image: {image_table['Datetime'].isnull().sum()}")
print(f"Total corrupted video: {video_table['Datetime'].isnull().sum()}")