class Tile(object):
    def __init__(self, suit: str, value: int, face: str, key: int, img: str = ''):
        self._suit = suit       # 类别：万
        self._value = value     # 序数：2
        self._face = face       # 名称：2万
        self._key = key         # 标识：102
        self._img = img         # 图片