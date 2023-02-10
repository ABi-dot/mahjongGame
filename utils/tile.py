class Tile(object):
    def __init__(self, suit: str, value: int, face: str, key: int, img: str = ''):
        self._suit = suit       # 类别：万
        self._value = value     # 序数：2
        self._face = face       # 名称：2万
        self._key = key         # 标识：102
        self._img = img         # 图片

    @property
    def face(self):
        return self._face

    @property
    def suit(self):
        return self._suit

    @property
    def value(self):
        return self._value

    @property
    def key(self):
        return self._key

    @property
    def img(self):
        return self._img

    def __str__(self):
        return f'[{self._face}]'

    def equal(self, other):
        if self.key == other.key:
            return True
        return False
