import conversions
import savedata
import title
import os



OFFSET_MCD_SRM_COUNTRYCODE = 0x8A
OFFSET_MCD_SRM_PRODUCTCODE = 0x8C
OFFSET_MCD_SRM_SAVEINFO = 0x2004

OFFSET_VMP_COUNTRYCODE = 0x10A
OFFSET_VMP_PRODUCTCODE = 0x10C
OFFSET_VMP_SAVEINFO = 0x2084

PMV_MAGIC = 0x564D5000
MCD_OFFSET = 0x80
SEED_OFFSET = 0x0C
HASH_OFFSET = 0x20
VMP_SZ = 0x20080

KEY = bytes([0xAB, 0x5A, 0xBC, 0x9F, 0xC1, 0xF4, 0x9D, 0xE6,
              0xA0, 0x51, 0xDB, 0xAE, 0xFA, 0x51, 0x88, 0x59])
IV = bytes([0xB3, 0x0F, 0xFE, 0xED, 0xB7, 0xDC, 0x5E, 0xB7,
             0x13, 0x3D, 0xA6, 0x0D, 0x1B, 0x6B, 0x2C, 0xDC])

print(title.title)

def identify_and_convert():
    input_file = input("Drag and drop savedata file here: ").strip().replace('"', "")
    file_ext = os.path.splitext(input_file)[1].lower()

    if file_ext == ".vmp":
        prompt = "Convert from .vmp --> press 1 for .srm | 2 for .mcd: "
        country, product, info = OFFSET_VMP_COUNTRYCODE, OFFSET_VMP_PRODUCTCODE, OFFSET_VMP_SAVEINFO
    elif file_ext == ".srm":
        prompt = "Convert from .srm --> press 1 for .vmp | 2 for .mcd: "
        country, product, info = OFFSET_MCD_SRM_COUNTRYCODE, OFFSET_MCD_SRM_PRODUCTCODE, OFFSET_MCD_SRM_SAVEINFO
    elif file_ext == ".mcd":
        prompt = "Convert from .mcd --> press 1 for .vmp | 2 for .srm: "
        country, product, info = OFFSET_MCD_SRM_COUNTRYCODE, OFFSET_MCD_SRM_PRODUCTCODE, OFFSET_MCD_SRM_SAVEINFO
    else:
        print("Not supported format")
        return
    
    conversion_map = {
    ".vmp": {
        "1": lambda: conversions.vmp_to_srm(input_file, country, product, info),
        "2": lambda: conversions.vmp_to_mcd(input_file, country, product, info)
        },
    ".srm": {
        "1": lambda: conversions.mcd_srm_to_vmp(input_file, KEY, IV, VMP_SZ, PMV_MAGIC, MCD_OFFSET, HASH_OFFSET, SEED_OFFSET),
        "2": lambda: conversions.srm_to_mcd(input_file, country, product, info)
        },
    ".mcd": {
        "1": lambda: conversions.mcd_srm_to_vmp(input_file, KEY, IV, VMP_SZ, PMV_MAGIC, MCD_OFFSET, HASH_OFFSET, SEED_OFFSET),
        "2": lambda: conversions.mcd_to_srm(input_file, country, product, info)
        }
    }

    choice = input(prompt)
    game_data = savedata.read_savedata(input_file, country, product, info)
    print(f'\nConverting savedata: {game_data["TITLE"]}\nVersion: {game_data["VERSION"]}\nProduct Code: {game_data["PRODUCT CODE"]}\nRegion: {game_data["REGION"]}\nGame info: {game_data["SAVEDATA INFO"]}')

    try:
        conversion_map[file_ext][choice]()
        print("\nConversion done!")
    except KeyError:
        print("\nNot valid")
    finally:
        input("\nPress ENTER to close...")


if __name__ == "__main__":
    identify_and_convert()