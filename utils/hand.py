from utils.mjSet import MjSet
from utils.suit import Suit
class Hand(object):
    def __init__(self, players: list = None, prevailingWind: str = '东'):
        if not players:
            raise ValueError("Need players!")
        self._mjSet = MjSet()
        self._players = players
        self._positions = dict()
        for idx, player in enumerate(self._players):
            wind = Suit.getWindByIndex(idx)
            player.position = wind
            self._positions[wind] = player
        self._prevailingWind = prevailingWind