import piexif
from datetime import datetime
from PIL import Image
from extraction import load_control_sheet


# How to offset a datetime in image metadata
def clean_exif(exifdict):
    for ifd in ("0th", "Exif", "GPS", "1st", "Interop"):
        if ifd in exifdict:
            _clean_ifd_tags(exifdict[ifd], ifd)


def _clean_ifd_tags(tags_dict, ifd_name):
    valid_types = (int, bytes, tuple)
    for tag in list(tags_dict.keys()):
        value = tags_dict[tag]
        try:
            if isinstance(value, str):
                tags_dict[tag] = value.encode('utf-8')
            elif isinstance(value, valid_types) or value is None:
                continue
            else:
                raise TypeError("Unsupported type")
        except Exception as e:
            print(f"Removed tag {tag} from {ifd_name} due to error: {e}")
            del tags_dict[tag]



def calc_offset(sheet, path):
    install_date = sheet[sheet["NoPetak"]== "O04"]["Tgl_pasang"].iloc[0]
    install_time = sheet[sheet["NoPetak"]== "O04"]['Jam_ambil'].iloc[0]

    install_datetime = f"{install_date} {install_time}"
    install_datetime = datetime.strptime(install_datetime, '%d/%m/%Y  %H.%M')

    image = Image.open(path)
    exifdict = piexif.load(image.info["exif"])

    origin_date = exifdict["0th"][piexif.ImageIFD.DateTime].decode("utf-8")
    origin_date = datetime.strptime(origin_date, '%Y:%m:%d %H:%M:%S')

    offset = install_datetime - origin_date

    corrected_date = origin_date + offset
    corrected_date = corrected_date.replace(second=origin_date.second)

    print(f"actual date: {install_datetime}")
    print(f"exif date: {origin_date}")
    print(f"corrected date: {corrected_date}")

    return corrected_date, exifdict

def offset_image(corrected_date, exifdict, path):
    corrected_date_str = corrected_date.strftime('%Y:%m:%d %H:%M:%S')
    corrected_date_bytes = corrected_date_str.encode('utf-8')

    # # Ensure the DateTime field in the EXIF dict is set correctly
    exifdict["0th"][piexif.ImageIFD.DateTime] = corrected_date_bytes
    exifdict["Exif"][piexif.ExifIFD.DateTimeOriginal] = corrected_date_bytes
    exifdict["Exif"][piexif.ExifIFD.DateTimeDigitized] = corrected_date_bytes

    if 41988 in exifdict["Exif"]:
        del exifdict["Exif"][41988]

    clean_exif(exifdict)

    try:
        exif_bytes = piexif.dump(exifdict)
        piexif.insert(exif_bytes, path)
        print(f"EXIF DateTime corrected: {corrected_date}")
    except ValueError as e:
        print(f"Error when dumping EXIF data: {e}")
        # Print the exifdict to debug and see the structure of the EXIF data
        print(exifdict)
    
if __name__ == "__main__":

    sheet = load_control_sheet("./data")
    path = r""
    date, exifdict = calc_offset(sheet, path)
    offset_image(date, exifdict, path)