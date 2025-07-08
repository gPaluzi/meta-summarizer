from src.extraction import *
import time

def calculate_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args,  **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"\nExecution time: {execution_time} seconds")
    return wrapper

@calculate_time
def main():
    # Load metadata from desired folder
    folder_path = r"./data"
    data = initial_check(folder_path)
    id_table = create_id_table(data)

    # Extract metadata
    image_data = [row for row in data if row[3].endswith(".JPG")]
    video_data = [row for row in data if row[3].endswith((".MOV", "MP4"))]

    image_table = create_photos_table(image_data)
    video_table = create_vid_table(video_data)


    # Export raw dataframe contains metadata
    id_table.to_csv("./outputs/id_table.csv", index= "cameraID")
    image_table.to_csv("./outputs/image_table.csv", index= "cameraID")
    video_table.to_csv("./outputs/video_table.csv", index= "cameraID")

    # Print statements
    print(f"\n\nTotal inserted camera: {len(id_table)}")
    print(f"Total extracted photos: {len(image_table)}")
    print(f"Total extracted videos: {len(video_table)}")
    print(image_table.head())
    print(video_table.head())


if __name__ == "__main__":
    main()