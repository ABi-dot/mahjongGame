from utils.suit import Suit
from utils.tile import Tile
from random import shuffle

class MjSet(object):
    dictionary = None

    @classmethod
    def generateDictionary(cls):
        if cls.dictionary: return
        cls.dictionary = dict()
        for suitName in Suit.Suit:
            suit = Suit.Suit[suitName]
            if suitName in '万饼条':
                for value in range(1, 10):
                    key = suit['base'] + value
                    face = str(value) + suitName
                    img = suit['eng'] + str(value) + '.png'
                    tile = Tile(suit=suitName, value=value, face=face, key=key, img=img)
                    cls.dictionary[key] = tile

            elif suitName in '字风':
                if suitName == '字':
                    dic = Suit.Dragon
                elif suitName == '风':
                    dic = Suit.Wind

                for text in dic:
                    character = dic[text]
                    key = suit['base'] + character['value']
                    face = text
                    value = character['value']
                    img = suit['eng'] + '-' + character['eng'] + '.png'
                    tile = Tile(suit=suitName, value=value, face=face, key=key, img=img)
                    cls.dictionary[key] = tile
            else:
                raise LookupError(f"suitName Error: {suitName}")

        return

    def __init__(self):
        MjSet.generateDictionary()
        self._tiles = []
        for key in MjSet.dictionary:
            tile = MjSet.dictionary[key]
            for i in range(4):
                self._tiles.append(tile)
        self._total = self._tiles[:]

    def __str__(self):
        arr = [f'{x._face}' for x in self._tiles]
        text = ' '.join(arr)
        return text

    @property
    def tiles(self):
        return self._tiles

    @property
    def total(self):
        return self._total

    def shuffle(self):
        shuffle(self._tiles)

def main():
    mj_set = MjSet()
    mj_set.shuffle()
    print(f"{mj_set}")
    print(len(mj_set.tiles))


if __name__ == '__main__':
    main()