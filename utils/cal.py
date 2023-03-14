from utils.mjSet import MjSet
from utils.tile import Tile
from mahjong.hand_calculating.hand import HandCalculator
from utils.rule import Rule
from mahjong.tile import TilesConverter
from mahjong.meld import Meld
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.constants import CHUN, EAST, HAKU, HATSU, NORTH, SOUTH, WEST
from mahjong.shanten import Shanten

class Calc(object):
    def __init__(self, mjSet: MjSet, concealed=None, exposed=None, winning_tile: Tile=None, winner_position = '', prevailing_wind = '', by_self = False,
                 robbing_a_kong = False, mahjong_on_kong = False, is_riichi = False, is_yifa = False):
        self.mjSet = mjSet
        self.concealed = []
        if concealed:
            self.concealed = concealed[:]
        self.exposed = exposed
        self.winning_tile = winning_tile
        self.winner_positon = winner_position
        self.prevailing_wind = prevailing_wind

        self.by_self = by_self
        self.robbing_a_kong = robbing_a_kong
        self.mahjong_on_kong = mahjong_on_kong
        self.is_riichi = is_riichi
        self.is_yifa = is_yifa

    @classmethod
    def convert_tile_to_mpsh_arr(self, tiles):
        return Rule.convert_arr_to_mpsh(Rule.convert_tiles_to_arr(tiles))

    @classmethod
    def transfer_wind(cls, s):
        if s == '东':
            return EAST
        if s == '南':
            return SOUTH
        if s == '西':
            return WEST
        if s == '北':
            return NORTH
        return None

    def print_hand_result(self, hand_result):
        print(hand_result.han, hand_result.fu)
        if hand_result.han and hand_result.han > 0:
            print(hand_result.cost['main'])
            print(hand_result.yaku)

    @classmethod
    def check_if_can_hu(cls, concealed, exposed, winning_tile, by_self, is_riichi, player_position, prevailing_wind):
        test = concealed[:]
        calculator = HandCalculator()
        tile_all = []
        if not by_self:
            test.append(winning_tile)
        for tile in test:
            tile_all.append(tile)
        for expose in exposed:
            for tile in expose.all:
                tile_all.append(tile)
        arr = cls.convert_tile_to_mpsh_arr(tile_all)
        wtarr = cls.convert_tile_to_mpsh_arr([winning_tile])
        tiles = TilesConverter.string_to_136_array(man=arr[0], pin=arr[1], sou=arr[2], honors=arr[3])
        winning_tile = TilesConverter.string_to_136_array(man=wtarr[0], pin=wtarr[1], sou=wtarr[2], honors=wtarr[3])[0]
        melds = cls.handle_exposed(exposed)
        result = calculator.estimate_hand_value(tiles=tiles, win_tile=winning_tile, melds=melds
                                                , config=HandConfig(is_tsumo=by_self, is_riichi=is_riichi,
                                                                    player_wind=cls.transfer_wind(player_position),
                                                                    round_wind=cls.transfer_wind(prevailing_wind),
                                                                    options=OptionalRules(has_open_tanyao=True)))
        if result.han and result.han > 0:
            return True
        return False

    @classmethod
    def handle_exposed(cls, exposed):
        melds = []
        for expose in exposed:
            if expose.expose_type == 'exposed chow':
                arr = cls.convert_tile_to_mpsh_arr(expose.all)
                melds.append(Meld(meld_type=Meld.CHI,
                                  tiles=TilesConverter.string_to_136_array(man=arr[0], pin=arr[1], sou=arr[2],
                                                                           honors=arr[3]), opened=True))
            elif expose.expose_type == 'concealed kong':
                arr = cls.convert_tile_to_mpsh_arr(expose.all)
                melds.append(Meld(meld_type=Meld.KAN,
                                  tiles=TilesConverter.string_to_136_array(man=arr[0], pin=arr[1], sou=arr[2],
                                                                           honors=arr[3]), opened=False))
            elif expose.expose_type == 'exposed kong' or expose.expose_type == "exposed kong from exposed pong" :
                arr = cls.convert_tile_to_mpsh_arr(expose.all)
                melds.append(Meld(meld_type=Meld.KAN,
                                  tiles=TilesConverter.string_to_136_array(man=arr[0], pin=arr[1], sou=arr[2],
                                                                           honors=arr[3]), opened=True))
            elif expose.expose_type == 'exposed pong':
                arr = cls.convert_tile_to_mpsh_arr(expose.all)
                melds.append(Meld(meld_type=Meld.PON,
                                  tiles=TilesConverter.string_to_136_array(man=arr[0], pin=arr[1], sou=arr[2],
                                                                           honors=arr[3]), opened=True))
        return melds

    def calc(self):
        calculator = HandCalculator()
        haidi, hedi = False, False
        if self.mjSet.get_left_tiles_cnt() == 0:
            if self.by_self:
                haidi = True
            else:
                hedi = True
        tile_all = []
        for tile in self.concealed:
            tile_all.append(tile)
        for expose in self.exposed:
            for tile in expose.all:
                tile_all.append(tile)
        arr = self.convert_tile_to_mpsh_arr(tile_all)
        wtarr = self.convert_tile_to_mpsh_arr([self.winning_tile])
        tiles = TilesConverter.string_to_136_array(man=arr[0], pin=arr[1], sou=arr[2], honors=arr[3])
        winning_tile = TilesConverter.string_to_136_array(man=wtarr[0], pin=wtarr[1], sou=wtarr[2], honors=wtarr[3])[0]
        melds = self.handle_exposed(self.exposed)
        dora_indicators = []
        for i in range(self.mjSet.bonus_count):
            arr = self.convert_tile_to_mpsh_arr([self.mjSet.bonus[i]])
            dora_indicators.append(TilesConverter.string_to_136_array(man=arr[0], pin=arr[1], sou=arr[2], honors=arr[3])[0])
        if self.is_riichi:
            for i in range(self.mjSet.bonus_count):
                arr = self.convert_tile_to_mpsh_arr([self.mjSet.li_bonus[i]])
                dora_indicators.append(
                    TilesConverter.string_to_136_array(man=arr[0], pin=arr[1], sou=arr[2], honors=arr[3])[0])
        result = calculator.estimate_hand_value(tiles=tiles, win_tile=winning_tile, melds=melds, dora_indicators=dora_indicators
                                                , config=HandConfig(is_tsumo=self.by_self, is_riichi=self.is_riichi,is_ippatsu=self.is_yifa,
                                                                    is_chankan=self.robbing_a_kong, is_rinshan=self.mahjong_on_kong, is_haitei=haidi, is_houtei=hedi,
                                                                    player_wind=self.transfer_wind(self.winner_positon), round_wind=self.transfer_wind(self.prevailing_wind),
                                                                    options=OptionalRules(has_open_tanyao=True)))
        self.print_hand_result(result)
        return result