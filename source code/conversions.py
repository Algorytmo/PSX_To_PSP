from Crypto.Cipher import AES
import struct
import hashlib
import savedata
import shutil
import os



output_folder = savedata.cwd


def xor_with_iv(data, iv):
    return bytes(b ^ iv[i % 16] for i, b in enumerate(data))


def create_signed_hash(key, seed, iv, vmp):
    cipher = AES.new(key, AES.MODE_ECB)

    salt = bytearray(64)
    work_buf = seed[:16]

    salt[0x00:0x10] = cipher.decrypt(work_buf)
    salt[0x10:0x20] = cipher.encrypt(work_buf)

    salt[0x00:0x20] = xor_with_iv(salt[0x00:0x20], iv)

    work_buf_xor = bytearray([0xFF] * 0x14)
    work_buf_xor[0:4] = seed[16:20]
    salt[0x10:0x24] = bytes(a ^ b for a, b in zip(salt[0x10:0x24], xor_with_iv(work_buf_xor, iv)))

    salt[0x14:] = bytes([0x00] * (64 - 0x14))
    salt = bytes(b ^ 0x36 for b in salt)

    sha1_a = hashlib.sha1()
    sha1_a.update(salt)
    sha1_a.update(vmp)
    digest1 = sha1_a.digest()

    salt = bytes(b ^ 0x6A for b in salt)
    sha1_b = hashlib.sha1()
    sha1_b.update(salt)
    sha1_b.update(digest1)
    
    return sha1_b.digest()


def vmp_to_srm(input_file, countrycode_offset, productcode_offset, saveinfo_offset):
    with open(input_file, "rb") as file:
        file_data = savedata.read_savedata(input_file, countrycode_offset, productcode_offset, saveinfo_offset)
        file.seek(0x80)
        conversion_data = file.read()
    out_file = os.path.join(output_folder, f'{file_data["TITLE"]}')
    with open(f"{out_file}.srm", "wb") as output_file:
        output_file.write(conversion_data)


def vmp_to_mcd(input_file, countrycode_offset, productcode_offset, saveinfo_offset):
    with open(input_file, "rb") as file:
        file_data = savedata.read_savedata(input_file, countrycode_offset, productcode_offset, saveinfo_offset)
        file.seek(0x80)
        conversion_data = file.read()
    out_file = os.path.join(output_folder, f'{file_data["TITLE"]}')
    with open(f"{out_file}.mcd", "wb") as output_file:
        output_file.write(conversion_data)


def srm_to_mcd(input_file, countrycode_offset, productcode_offset, saveinfo_offset):
    file_data = savedata.read_savedata(input_file, countrycode_offset, productcode_offset, saveinfo_offset)
    out_file = os.path.join(output_folder, f'{file_data["TITLE"]}.srm')
    dst = os.path.splitext(out_file)[0] + ".mcd"
    shutil.copy(out_file, dst)


def mcd_to_srm(input_file, countrycode_offset, productcode_offset, saveinfo_offset):
    file_data = savedata.read_savedata(input_file, countrycode_offset, productcode_offset, saveinfo_offset)
    out_file = os.path.join(output_folder, f'{file_data["TITLE"]}.mcd')
    dst = os.path.splitext(out_file)[0] + ".srm"
    shutil.copy(out_file, dst)


def mcd_srm_to_vmp(input_file, key, iv, vmp_sz, pmv_magic, mcd_offset, hash_offset, seed_offset):
    vmp = bytearray(vmp_sz)
    vmp[0:4] = struct.pack("<I", pmv_magic)
    vmp[4:8] = struct.pack("<I", mcd_offset)

    with open(input_file, "rb") as file:
        mcd_data = file.read(0x20000) # 128 KB
        vmp[mcd_offset:mcd_offset + len(mcd_data)] = mcd_data
        seed = os.urandom(20)
        vmp[seed_offset:seed_offset + 20] = seed
        final_hash = create_signed_hash(key, seed, iv, vmp)
        vmp[hash_offset:hash_offset + 20] = final_hash
    out_file = os.path.join(output_folder, "SCEVMC0")
    with open(f"{out_file}.VMP", "wb") as output_file:
        output_file.write(vmp)