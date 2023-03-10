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
        self._wangPai = []
        self._tiles = []
        self._leftTiles = 136 - 14
        for key in MjSet.dictionary:
            tile = MjSet.dictionary[key]
            for i in range(4):
                self._tiles.append(tile)
        self._total = self._tiles[:]
        self._bonus = [] # 宝牌
        self._li_bonus = [] # 里宝
        self._bonus_count = 0

    def __str__(self):
        arr = [f'{x._face}' for x in (self._tiles + self._wangPai)]
        text = ' '.join(arr)
        return text

    @property
    def wangPai(self):
        return self._wangPai

    @property
    def bonus_count(self):
        return self._bonus_count

    @bonus_count.setter
    def bonus_count(self, v):
        self._bonus_count = v

    @property
    def bonus(self):
        return self._bonus

    @property
    def tiles(self):
        return self._tiles

    @property
    def bonus(self):
        return self._bonus

    @property
    def li_bonus(self):
        return self._li_bonus

    @property
    def total(self):
        return self._total

    def get_left_tiles_cnt(self):
        return self._leftTiles

    def shuffle(self):
        shuffle(self._tiles)
        for _ in range(14):
            t = self.tiles.pop()
            self._wangPai.append(t)
        self._bonus_count = 1
        for i in range(0, 10, 2):
            self._bonus.append(self._wangPai[i])
        for i in range(1, 10, 2):
            self._li_bonus.append((self._wangPai[i]))

    def draw(self) -> Tile:
        if not self._tiles:
            return None
        tile = self._tiles.pop()
        self._leftTiles -= 1
        return tile

    def draw_from_back(self) -> Tile:
        if not self._wangPai:
            return None
        tile = self._wangPai.pop()
        self._leftTiles -= 1
        return tile

def main():
    mj_set = MjSet()
    mj_set.shuffle()
    print(f"{mj_set}")
    print([x._face for x in mj_set.bonus])
    print([x._face for x in mj_set.li_bonus])


if __name__ == '__main__':
    main()