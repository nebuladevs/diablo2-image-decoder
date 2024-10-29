import struct
from PIL import Image

def read_header(file_path):
    with open(file_path, 'rb') as f:
        header_data = f.read(32)
        
        version, unknown, tiles = struct.unpack('<III', header_data[:12])
        print(f"Version: {version}, Unknown: {unknown}, Tiles: {tiles}")

read_header('floor.dt1')