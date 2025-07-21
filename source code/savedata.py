import json
import os



cwd = os.getcwd()

with open(os.path.join(cwd, "psx_games.json"), encoding='utf-8') as jsonfile:
    data = json.load(jsonfile)

country_codes = {
    "BI": "Japan",
    "BA": "America",
    "BE": "Europe"
}


def read_savedata(input_file, countrycode_offset, productcode_offset, saveinfo_offset):
    
    file_data = {
        "TITLE": "",
        "VERSION": "",
        "PRODUCT CODE": "",
        "REGION": "",
        "SAVEDATA INFO": ""
    }

    with open(input_file, "rb") as psx_savedata:
        psx_savedata.seek(countrycode_offset)
        byte_country_code = psx_savedata.read(2).decode(errors="ignore")
        psx_savedata.seek(productcode_offset)
        byte_product_code = psx_savedata.read(10).decode(errors="ignore")
        psx_savedata.seek(saveinfo_offset)
        byte_savegame_info2 = psx_savedata.read(63).decode("shift_jis", errors="ignore")

    country_code = country_codes.get(byte_country_code, "Unknown")
    product_code = "".join(byte_product_code.split("-"))

    for game in data:
        if game["GAME-ID"] == product_code:
            file_data["TITLE"] = game["TITLE"]
            file_data["VERSION"] = game["VERSION"]
            break
    else:
        print(f"No match found for product code {product_code}")
        file_data["TITLE"] = "-"
        file_data["VERSION"] = "-"

    file_data["PRODUCT CODE"] = product_code
    file_data["REGION"] = country_code
    file_data["SAVEDATA INFO"] = byte_savegame_info2.rstrip("\x00^").rstrip("\x00")

    return file_data