import os
import struct
from PIL import Image

OUTPUT_DIR = 'output/'
DC6_DIR = 'dc6/'

def read_dc6_header(file_path, palette_file):
    if ".dc6" not in file_path: return
    
    file_name = file_path.split('.')[0]
    
    with open(f"{DC6_DIR}{file_path}", 'rb') as f:
        header_data = f.read(24)
        
        version, dw_flags, e_format, pad_bytes, n_dirs, block_count = struct.unpack('6i', header_data)
        print(f"version: {version}, dw_flags: {dw_flags}, e_format: {e_format}, n_dirs: {n_dirs}, block_count: {block_count}")

        offsets = []
        
        for _ in range(block_count):
            offset = struct.unpack('i', f.read(4))[0]
            offsets.append(offset)
            
        palette = load_palette(palette_file)
            
        for i, offset in enumerate(offsets):
            f.seek(offset)
            
            block_header_data = f.read(32)
            b_flipped, width, height, x, y, unknown, next_block, length = struct.unpack('8i', block_header_data)

            print(f"block {i}: flipped: {b_flipped}, width: {width}, height: {height}, x: {x}, y: {y}, length: {length}")
            
            image_data = f.read(length)
            print(f"reading image data: expected {length} bytes, read {len(image_data)} bytes")
             
            if len(image_data) < length:
                print('oops')
                break
            
            image = decode_image_data(image_data, palette, width, height)
            image.save(f'{OUTPUT_DIR}{file_name}_{i}.png')

def load_palette(palette_file):
    with open(palette_file, 'rb') as f:
        palette = []
        while True:
            rgb = f.read(3)
            if not rgb:
                break
            palette.append(tuple(rgb))
    return palette

def decode_image_data(image_data, palette, width, height):
    x = 0
    y = 0
    pic = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    i = 0

    while i < len(image_data):
        cur_byte = image_data[i]
        i += 1
        
        if cur_byte == 0x80:
            x = 0
            y += 1
        elif cur_byte > 0x80:
            x += (cur_byte - 0x80)
        else:
            for _ in range(cur_byte):
                if i >= len(image_data):
                    print('insufficient image data to read the next byte.')
                    return pic
                
                temp_byte = image_data[i]
                i += 1
                
                if 0 <= temp_byte < len(palette) and 0 <= x < width and 0 <= (height - 1 - y) < height:
                    pic.putpixel((x, height - 1 - y), palette[temp_byte])
                else:
                    print(f'index out of bounds: x={x}, y={y}, temp_byte={temp_byte}')
                
                x += 1
    return pic

def main():
    dc6_files = os.listdir(DC6_DIR)
    for dc6_file in dc6_files:
        read_dc6_header(dc6_file, 'pal.dat')

main()