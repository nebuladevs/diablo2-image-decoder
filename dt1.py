import struct
from PIL import Image
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class DT1Header:
    major_version: int
    minor_version: int
    unknown_header_bytes: bytes
    number_of_tiles: int
    block_headers_pointer: int

    @staticmethod
    def from_file(f):
        header_format = 'i i 260s i i'
        header_size = struct.calcsize(header_format)
        header_data = f.read(header_size)
        
        if len(header_data) != header_size:
            raise ValueError("wrong header size")
        
        return DT1Header(*struct.unpack(header_format, header_data))
@dataclass
class DT1Tile:
    direction: int
    roof_height: int
    material_flags: int
    height: int
    width: int
    type: int
    style: int
    sequence: int
    rarity_frame_index: int
    subtile_flags: List[int]
    block_header_pointer: int
    block_header_size: int
    num_blocks: int

    @staticmethod
    def from_file(f):
        tile_format = 'i h h i i i i i i 25B i i i'
        tile_size = struct.calcsize(tile_format)
        tile_data = f.read(tile_size)
        if len(tile_data) != tile_size:
            raise ValueError("wrong header size")

        unpacked_data = struct.unpack(tile_format, tile_data)
        subtile_flags = list(unpacked_data[9:34])
        
        height_ = unpacked_data[3]*-1 if unpacked_data[3] < 0 else unpacked_data[3]
        width_ = unpacked_data[4]*-1 if unpacked_data[4] < 0 else unpacked_data[4]

        return DT1Tile(
            direction=unpacked_data[0],
            roof_height=unpacked_data[1],
            material_flags=unpacked_data[2],
            height=height_,
            width=width_,
            type=unpacked_data[5],
            style=unpacked_data[6],
            sequence=unpacked_data[7],
            rarity_frame_index=unpacked_data[8],
            subtile_flags=subtile_flags,
            block_header_pointer=unpacked_data[34],
            block_header_size=unpacked_data[35],
            num_blocks=unpacked_data[36]
        )

@dataclass
class DT1Block:
    x: int
    y: int
    grid_x: int
    grid_y: int
    format: int
    length: int
    file_offset: int
    encoded_data: Optional[bytes] = None

    @staticmethod
    def from_file(f):
        block_format = 'hh2xBBhi2xi'
        block_size = struct.calcsize(block_format)
        block_data = f.read(block_size)
        if len(block_data) != block_size:
            raise ValueError("wrong header size")

        unpacked_data = struct.unpack(block_format, block_data)
        return DT1Block(
            x=unpacked_data[0],
            y=unpacked_data[1],
            grid_x=unpacked_data[2],
            grid_y=unpacked_data[3],
            format=unpacked_data[4],
            length=unpacked_data[5],
            file_offset=unpacked_data[6]
        )

def draw_tile(tile, width, height):
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    pixel_data = image.load()

    for y in range(height):
        for x in range(width):
            pixel_data[x, y] = (255, 0, 0, 255) if (x + y) % 2 == 0 else (0, 0, 255, 255)

    return image

def render_all_tiles(tiles):
    tile_images = []
    for tile in tiles:
        width, height = tile.width, tile.height
        image = draw_tile(tile, width, height)
        tile_images.append(image)
    
    return tile_images

def load_dt1_file(file_path):
    with open(file_path, 'rb') as f:
        header = DT1Header.from_file(f)
        print(f"file header: {header}")
        
        f.seek(header.block_headers_pointer)

        tiles = []
        for _ in range(1):
            tile = DT1Tile.from_file(f)
            tiles.append(tile)
            print(f"readed tile: {tile}")

            f.seek(tile.block_header_pointer)

            blocks = []
            for _ in range(tile.num_blocks):
                block = DT1Block.from_file(f)
                print(f"readed block: {block}")
                f.seek(tile.block_header_pointer + block.file_offset)
                block.encoded_data = f.read(block.length)
                blocks.append(block)

            tile.blocks = blocks

    return header, tiles

def main():
    file_path = 'floor.dt1'
    header, tiles = load_dt1_file(file_path)
    tile_images = render_all_tiles(tiles)
    for idx, image in enumerate(tile_images):
        image.show()

main()