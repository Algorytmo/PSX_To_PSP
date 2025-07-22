# PSX_To_PSP
Convert VPM, srm and mcd savefiles for PSX/PSP/emulators


# INTRODUCTION

When using emulators and original Sony consoles, save files generated across different systems like PlayStation 1 (PSX) memory cards or emulators (such as ePSXe, DuckStation, or RetroArch) are often not compatible with each other. This makes it difficult to transfer game progress between platforms, especially when moving between console and emulator.

Sony’s PlayStation (PSX/PS1), PSP, and related emulators use various save file formats:
- .VMP: A proprietary format used by the PSP for PSX virtual memory card saves. It includes AES-based signatures and system-specific metadata.
- .SRM: A generic save format used by many emulators, commonly found in RetroArch or Mednafen.
- .MCD: A virtual memory card file used in emulators like ePSXe and DuckStation; typically emulates a 128KB PS1 memory card.

Though these formats contain similar game data, they differ in structure, offsets, encoding, and in some cases use cryptographic verification (such as signed hashes).

That’s why I tried to designed a tool that performs smart conversions between these formats, giving users a simple and safe way to preserve their game progress across platforms.


# VMP Conversion Explained

The .VMP file format, used by Sony PSP to emulate PSX memory cards, differs significantly from .SRM and .MCD formats—not only structurally, but cryptographically. One of its distinctive features is a 128-bit header (0x80 bytes) at the beginning of the file, which includes metadata and a cryptographically signed hash used to verify the integrity of the save file.

The VMP header is created as part of the conversion process using the following steps:

Magic number and offset setup:
- First 4 bytes (0x00–0x03): magic value PMV_MAGIC (0x564D5000)
- Next 4 bytes (0x04–0x07): offset that stores a numeric value (32-bit, little endian) that indicates the point in the file where the actual payload begins (game data).
- In our case, we place the value 0x80 there, which means: “The data starts at offset 0x80 (128 in decimal).”

Save data embedding:
- The payload (converted MCD/SRM data) is placed starting at MCD_OFFSET (0x80), which mimics the layout expected by the PSP.
- A random seed of 20 bytes is generated and inserted at SEED_OFFSET (0x0C)
- Using AES encryption (ECB mode), a 64-byte salt is built from the seed, a static key and IV
- The salt is processed with XOR operations and then hashed with SHA-1, producing a signed digest
- This digest is placed at HASH_OFFSET (0x20)

These cryptographic operations ensure compatibility with the PSP's save file validation, making the .VMP file usable and recognizable.

In summary:

- Offset 0x00–0x03	--> Magic number (PMV_MAGIC)
- Offset 0x04–0x07	--> Data that indicates where payload begins (0x80)
- Offset 0x08–0x0B	--> (free or reserved)
- Offset 0x0C–0x1F	--> Random seed (20 bytes)
- Offset 0x20–0x33	--> Signed hash (20 bytes)
- Offset 0x34–0x7F	--> (extra / padding / reserved)
- Offset 0x80 --> Real savedata (our payload)


# MCD/SRM Conversion Explained

Converting to .MCD or .SRM is straightforward, as these formats consist of raw save data without additional headers. To perform the conversion, we simply remove the first 0x80 bytes (128 in decimal) from the original VMP file and save the remaining binary content using the appropriate extension: .MCD or .SRM.


# HOW TO USE

- Download the folder called psx_to_psp
- Start the exe
- Drag and drop .VMP, .MCD or .SRM savedata and press enter
- You'll find the new created file inside the folder

REMEMBER THIS:

When working with .MCD or .SRM files, it's important to match the exact filename expected by the emulator—otherwise the save won't be recognized.
To ensure this, I recommend starting the game normally within the emulator and creating a fresh save file.



Then, locate the newly created file, copy its name, convert your .VMP file to .MCD or .SRM, and rename the converted file using that exact filename.
