from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.shanten import Shanten

calculator = HandCalculator()
def print_hand_result(hand_result):
    print(hand_result.han, hand_result.fu)
    print(hand_result.cost['main'])
    print(hand_result.yaku)

dora_indicators = [
    TilesConverter.string_to_136_array(man='3')[0],
    TilesConverter.string_to_136_array(man='1')[0],

]
tiles = TilesConverter.string_to_136_array(man='19', pin='91', honors='77654321', sou='19')
win_tile = TilesConverter.string_to_136_array(honors='4', pin='')[0]
result = calculator.estimate_hand_value(tiles, win_tile, dora_indicators=dora_indicators)
print_hand_result(result)

shanten = Shanten()
tiles = TilesConverter.string_to_34_array(man='123', pin='', sou='1',honors='')
result = shanten.calculate_shanten(tiles)

print(result)