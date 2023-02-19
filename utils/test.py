from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.shanten import Shanten
from mahjong.meld import Meld

calculator = HandCalculator()
def print_hand_result(hand_result):
    print(hand_result.han, hand_result.fu)
    print(hand_result.cost['main'])
    print(hand_result.yaku)

dora_indicators = [
    TilesConverter.string_to_136_array(man='3')[0],
    TilesConverter.string_to_136_array(man='1')[0],

]
tiles = TilesConverter.string_to_136_array(man='234', pin='22444567', sou='567')
win_tile = TilesConverter.string_to_136_array(man='2')[0]
melds = [Meld(meld_type=Meld.PON, tiles=TilesConverter.string_to_136_array(pin='444'), opened=False),
         Meld(meld_type=Meld.CHI, tiles=TilesConverter.string_to_136_array(sou='567'), opened=True)]

result = calculator.estimate_hand_value(tiles, win_tile, melds=melds, config=HandConfig(is_tsumo=True, options=OptionalRules(has_open_tanyao=True)))
print_hand_result(result)
