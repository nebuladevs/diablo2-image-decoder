import struct
from PIL import Image
from dataclasses import dataclass
from typing import List

@dataclass
class DT1Header:
    major_version: int
    minor_version: int
    zeros1: bytes
    number_of_tiles: int
    block_headers_pointer: int
    
    @staticmethod
    def from_file(f):
        header_format = 'ii260sii'
        header_size = struct.calcsize(header_format)
        header_data = f.read(header_size)
        
        if len(header_data) != header_size:
            raise ValueError("wrong file header size")
        
        return DT1Header(*struct.unpack(header_format, header_data))
    
@dataclass
class DT1Tile:
    direction: int
    roof_height: int
    sound_index: int
    animated: int
    height: int
    width: int
    tiles_ptr: int
    subtile_flags: List[int]
    
    @staticmethod
    def from_file(f):
        tile_format = 'i h b b i i i 25B'
        tile_size = struct.calcsize(tile_format)
        tile_data = f.read(tile_size)
        if len(tile_data) != tile_size:
            raise ValueError("wrong tile header size")

        unpacked_data = struct.unpack(tile_format, tile_data)
        subtile_flags = list(unpacked_data[7:32])

        return DT1Tile(
            direction=unpacked_data[0],
            roof_height=unpacked_data[1],
            sound_index=unpacked_data[2],
            animated=unpacked_data[3],
            height=unpacked_data[4],
            width=unpacked_data[5],
            tiles_ptr=unpacked_data[6],
            subtile_flags=subtile_flags
        )

def load_dt1_file(file_path):
    with open(file_path, 'rb') as f:
        header = DT1Header.from_file(f)
        print(f"file header: {header}")
        
        f.seek(header.block_headers_pointer)
        
        tiles = []
        for _ in range(header.number_of_tiles):
            tile = DT1Tile.from_file(f)
            print(f"tile: {tile}")
            raise Exception
            # tiles.append(tile)
        
    return header, tiles

def draw_tile(tile, width, height):
    """
    Renderiza o tile em uma imagem.
    """
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))  # Fundo transparente
    pixel_data = image.load()

    for y in range(height):
        for x in range(width):
            pixel_data[x, y] = (255, 0, 0, 255) if (x + y) % 2 == 0 else (0, 0, 255, 255)

    return image

def render_all_tiles(tiles):
    """
    Renderiza todos os tiles lidos de um arquivo `.dt1`.
    """
    tile_images = []
    for tile in tiles:
        width, height = tile.width, tile.height
        image = draw_tile(tile, width, height)
        tile_images.append(image)
    
    return tile_images

def main():
    file_path = 'floor.dt1'  # Substitua pelo caminho do seu arquivo .dt1
    header, tiles = load_dt1_file(file_path)
    # for tile in tiles:
    #     print(tile)
    # tile_images = render_all_tiles(tiles)
    
    # # Exibir ou salvar as imagens dos tiles
    # for idx, image in enumerate(tile_images):
    #     image.show()  # Mostra cada tile (pode abrir múltiplas janelas de imagem)
    #     # image.save(f'tile_{idx}.png')  # Ou salve como arquivo PNG

main()