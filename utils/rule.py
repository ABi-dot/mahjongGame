from utils.mjSet import MjSet
from utils.mjMath import MjMath
from utils.tile import Tile
class Rule(object):
    @staticmethod
    def convert_tiles_to_arr(tiles: list):
        if not tiles:
            return []
        return [tile.key for tile in tiles]

    @staticmethod
    def tile_key(tile: Tile):
        return tile.key

    @classmethod
    def sort(cls, tiles: list):
        tiles.sort(key=cls.tile_key)

    @staticmethod
    def convert_tiles_to_str(tiles):
        return ' '.join([f'{x}' for x in tiles])

    @staticmethod
    def convert_key_to_tile(key: int):
        if not key:
            raise ValueError(f"key is 0")
        if key in MjSet.dictionary:
            return MjSet.dictionary[key]
        raise ValueError(f"can't convert {key} to tile")

    @staticmethod
    def convert_arr_to_tiles(arr: list):
        if not arr:
            return []
        return [MjSet.dictionary[x] for x in arr]

    @classmethod
    def is_rong(cls, tiles):
        if not tiles: return False
        arr = cls.convert_tiles_to_arr(tiles)
        arr.sort()
        result = MjMath.is_rong(arr)
        return result

def main():
    mj_set = MjSet()
    concealed = []
    mj_set.shuffle()
    for _ in range(13):
        concealed.append(mj_set.draw())
    print(Rule.convert_tiles_to_arr(concealed))


if __name__ == '__main__':
    main()
