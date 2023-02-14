from utils.mjSet import MjSet
from utils.rule import Rule
from utils.tile import Tile
from utils.expose import Expose
import pygame
from utils.error import *
from utils.mjMath import MjMath
import random
from setting import Setting
from sprite import Sprite
from utils.suit import Suit

class Player(object):
    def __init__(self, nick="bot", score: int = 25000, isViewer: bool = False, viewerPosition: str = '东',
                 screen=None, clock=None):
        self._nick = nick
        self._concealed = []
        self._exposed = []
        self._discarded = []
        self._discardedByRandomCount = 0
        self._desk = []
        self._position = ''
        self._hand = None
        self._discarding = None

        self._score = score
        self._isViewer = isViewer
        self.viewerPosition = viewerPosition
        self._screen = screen
        self._clock = clock
        self.currentTiles = []
        self.currentIdx = -1

        self.info_group = pygame.sprite.Group()
        self.concealed_group = pygame.sprite.Group()
        self.exposed_group = pygame.sprite.Group()
        self.discarded_group = pygame.sprite.Group()
        self.all_group = pygame.sprite.Group()

    def reset(self):
        self._concealed = []
        self._exposed = []
        self._discarded = []
        self._desk = []
        self._discardedByRandomCount = 0
        self._discarding = None
        self.currentIdx = -1
        self.currentTiles = []

    @property
    def discarding(self):
        return self._discarding

    @discarding.setter
    def discarding(self, value):
        self._discarding = value

    @property
    def nick(self):
        return self._nick

    @property
    def clock(self):
        return self._clock

    @property
    def concealed(self):
        return self._concealed

    @property
    def score(self):
        return self._score

    @property
    def position(self):
        return self._position

    @property
    def exposed(self):
        return self._exposed

    @position.setter
    def position(self, value):
        self._position = value

    @property
    def screen(self):
        return self._screen

    @screen.setter
    def screen(self, value):
        self._screen = value

    @property
    def isViewer(self):
        return self._isViewer

    @property
    def hand(self):
        return self._hand

    @property
    def desk(self):
        return self._desk

    @hand.setter
    def hand(self, v):
        self._hand = v

    def draw(self, mjSet: MjSet):
        tile = mjSet.draw()
        if not tile:
            raise ValueError("No Tiles!")
        self.add(tile)
        return tile

    def add(self, tile: Tile):
        self._concealed.append(tile)

    def drawstack(self, mjSet: MjSet):
        for _ in range(4):
            self.draw(mjSet)

    def sortconcealed(self):
        arr = Rule.convert_tiles_to_arr(self._concealed)
        arr.sort()
        self._concealed = Rule.convert_arr_to_tiles(arr)

    def try_exposed_kong(self, tile: Tile, owner, mjSet: MjSet) -> bool:
        cnt = 0
        for test in self.concealed:
            if tile.key == test.key:
                cnt += 1
        if cnt == 3:
            self.exposed_kong(tile=tile, owner=owner, mjSet=mjSet)
            return True
        return False

    def exposed_kong(self, tile: Tile, owner, mjSet: MjSet):
        count = 0
        inner = []
        for test in self._concealed[::-1]:
            if tile.key == test.key:
                inner.append(test)
                self._concealed.remove(test)
                count += 1
                if count == 3:
                    break
        if count < 3:
            raise ValueError(f"{self.nick} don't have enough {tile}!")
        expose = Expose('exposed kong', inners=inner, outer=tile, outer_owner=owner)
        self._exposed.append(expose)
        tile = self.draw_from_back(mjSet)
        if not tile:
            raise OutOfTilesError()
        # 杠上开花
        if self.try_mahjong():
            raise HaveWinnerError(winner=self)

    def try_exposed_pong(self, tile: Tile, owner) -> bool:
        cnt = 0
        for test in self._concealed:
            if tile.key == test.key:
                cnt += 1
        if cnt >= 2:
            self.exposed_pong(tile=tile,owner=owner)
            return True

        return False

    def exposed_pong(self, tile: Tile, owner):
        count = 0
        inner = []
        for test in self._concealed[::-1]:
            if tile.key == test.key:
                inner.append(test)
                self._concealed.remove(test)
                count += 1
                if count == 2:
                    break
        if count < 2:
            raise ValueError(f"{self.nick} don't have enough {tile}!")
        expose = Expose('exposed pong', inners=inner, outer=tile, outer_owner=owner)
        self._exposed.append(expose)

    def try_exposed_kong_from_exposed_pong(self, mjSet: MjSet) -> bool:
        tile = self.concealed[-1]
        if not mjSet.get_left_tiles_cnt():
            return False
        if not self.exposed:
            return False
        for expose in self.exposed:
            if expose.expose_type == 'exposed pong' and expose.outer.key == tile.key:
                # 有杠就杠
                return self.exposed_kong_from_exposed_pong(tile=tile, expose=expose, mjSet=mjSet)
        return False

    def exposed_kong_from_exposed_pong(self, tile: Tile, expose: Expose, mjSet: MjSet) -> bool:
        expose.expose_type = 'exposed kong from exposed pong'
        expose.inners.append(tile)
        expose.all.append(tile)
        self.concealed.pop()
        tile = self.draw_from_back(mjSet)
        if not tile:
            raise OutOfTilesError()
            # 杠上开花
        if self.try_mahjong():
            raise HaveWinnerError(winner=self)
        return True

    def try_exposed_chow(self, tile: Tile, owner) -> bool:
        arr = Rule.convert_tiles_to_arr(self.concealed)
        outer = tile.key

        # chow!!!
        combins = MjMath.get_chow_combins_from_arr(arr=arr, outer=outer)
        if not combins:
            return False
        combin = random.choice(combins)
        inners = Rule.convert_arr_to_tiles(combin)
        self.exposed_chow(inners=inners, tile=tile, owner=owner)
        return True

    def exposed_chow(self, inners, tile, owner):
        if len(inners) != 2:
            raise ValueError(f"self_tiles length should be 2:{inners}")
        for x in inners:
            for test in self._concealed[::-1]:
                if x.key == test.key:
                    self._concealed.remove(test)
                    break

        expose = Expose('exposed chow', inners=inners, outer=tile, outer_owner=owner)
        self._exposed.append(expose)

    def draw_from_back(self, mjSet):
        tile = mjSet.draw_from_back()
        if not tile:
            raise ValueError("No tiles!")
            return None
        self.add(tile)
        return tile

    def put_on_desk(self, tile):
        self._desk.append(tile)


    def try_conceal_kong(self, mjSet: MjSet) -> bool:
        if not self._concealed: return False
        if mjSet.get_left_tiles_cnt() == 0: return False
        test_tiles = list(set(self._concealed))
        for x in test_tiles:
            count = self.concealed.count(x)
            if count == 4:
                # concealed kong when possible
                self.concealed_kong(tile=x, mjSet=mjSet)
                return True
        return False

    def concealed_kong(self, tile, mjSet):
        count = 0
        inners = []
        for x in self.concealed[::-1]:
            if x.key == tile.key:
                count += 1
                inners.append(x)
                self.concealed.remove(x)
                if count >= 4:
                    break
        expose = Expose(expose_type='concealed kong', inners=inners, outer=None, outer_owner=None)
        self._exposed.append(expose)
        tile = self.draw_from_back(mjSet)
        if not tile:
            raise OutOfTilesError()
        # 杠上开花
        if self.try_mahjong():
           raise HaveWinnerError(winner=self)

    def try_mahjong(self, tile=None) -> bool:
        test = self.concealed[:]
        if tile:
            test.append(tile)
        if Rule.is_rong(test):
            return True
        return False

    def decide_discard(self) -> Tile:
        return self.decide_discard_random()

    def decide_discard_random(self):
        if not self.concealed:
            raise ValueError(f"{self.nick} have no concealed tiles!")
        # finally, random discard one
        tile = random.choice(self.concealed)
        # self._discard_by_random_count += 1
        return tile

    def discard(self, tile: Tile):
        if tile not in self._concealed:
            raise LookupError(f"{self.nick} have not tile:{tile}")

        self._concealed.remove(tile)
        self._discarded.append(tile)
        self._discarding = tile
        return tile

    def draw_info(self):
        self.info_group.empty()
        centerx = Setting.WinW // 2
        bottom = Setting.WinH // 2 - Setting.info

        # draw player's discarding tile
        if self.discarding:
            fileName = Setting.tileImgPath + self.discarding.img
            image = pygame.image.load(fileName)
            sprite = Sprite(image)
            sprite.rect.centerx = centerx
            sprite.rect.bottom = bottom
            self.info_group.add(sprite)

    def draw_concealed(self, state = ''):
        self.concealed_group.empty()
        left = Setting.concealed_left
        bottom = Setting.concealed_bottom

        for index, tile in enumerate(self.concealed):
            if self.isViewer or state == 'scoring':
                image = pygame.image.load(Setting.tileImgPath + tile.img)
            else:
                image = pygame.image.load(Setting.tileImgPath + Setting.facedownImg)
            sprite = Sprite(image)
            if not self.isViewer:
                image = pygame.transform.scale(image, (sprite.rect.w // 4 * 3, sprite.rect.h // 4 * 3))
            sprite = Sprite(image)
            sprite.rect.left = left
            sprite.rect.bottom = bottom
            if self.isViewer and index in self.currentTiles:
                sprite.rect.bottom += Setting.current_jump
            self.concealed_group.add(sprite)
            left += sprite.rect.width

    def draw_discard(self):
        self.discarded_group.empty()
        left = Setting.discarded_left
        bottom = Setting.discarded_bottom
        for index, tile in enumerate(self.desk):
            image = pygame.image.load(Setting.tileImgPath + tile.img)
            sprite = Sprite(image)
            image = pygame.transform.scale(image, (sprite.rect.w // 4 * 3, sprite.rect.h // 4 * 3))
            sprite = Sprite(image)
            sprite.rect.left = left
            sprite.rect.bottom = bottom
            self.discarded_group.add(sprite)
            left += sprite.rect.width
            if index != 0 and (index + 1) % Setting.discarded_line_limit == 0:
                left += min(sprite.rect.width, sprite.rect.height)
            if index != 0 and (index + 1) % (Setting.discarded_line_limit * 2) == 0:
                left = Setting.discarded_left
                bottom += max(sprite.rect.w, sprite.rect.h) + 5

    def draw_exposed(self, state = ''):
        self.exposed_group.empty()
        left = Setting.exposed_left
        bottom = Setting.exposed_bottom

        for exposed in self.exposed:
            space_width = 0
            for i2, tile in enumerate(exposed.all):
                adjust = 0  # adjust for exposed chow / pong / kong
                image = pygame.image.load(Setting.tileImgPath + tile.img)

                # lay down the tile for chow
                if exposed.expose_type == "exposed chow":
                    if tile == exposed.outer:
                        adjust = 90

                # lay down the tile for pong
                if exposed.expose_type == "exposed pong":
                    if exposed.outer_owner.position == Suit.getBeforeWind(self.position):
                        if i2 == 0:
                            adjust = 90
                    if exposed.outer_owner.position == Suit.getNextWind(self.position):
                        if i2 == 2:
                            adjust = 90
                    if exposed.outer_owner.position != Suit.getBeforeWind(self.position) and \
                            exposed.outer_owner.position != Suit.getNextWind(self.position):
                        if i2 == 1:
                            adjust = 90

                # lay down the tile for kong
                if exposed.expose_type in ["exposed kong", "exposed kong from exposed pong"]:
                    if exposed.outer_owner.position == Suit.getBeforeWind(self.position):
                        if i2 == 0:
                            adjust = 90
                    if exposed.outer_owner.position == Suit.getNextWind(self.position):
                        if i2 == 2:
                            adjust = 90
                    if exposed.outer_owner.position != Suit.getBeforeWind(self.position) and \
                            exposed.outer_owner.position != Suit.getNextWind(self.position):
                        if i2 == 3:
                            adjust = 90

                # cover the concealed kong
                if exposed.expose_type == "concealed kong" and state != 'scoring':
                    image = pygame.image.load(Setting.tileImgPath + Setting.facedownImg)
                    pass
                image = pygame.transform.rotate(image, adjust)
                sprite = Sprite(image)
                image = pygame.transform.scale(image, (sprite.rect.w // 4 * 3, sprite.rect.h // 4 * 3))
                sprite = Sprite(image)
                sprite.rect.left = left
                sprite.rect.bottom = bottom
                self.exposed_group.add(sprite)

                left += sprite.rect.width
                space_width = min(sprite.rect.width, sprite.rect.height)
            #end for an expose
            left += space_width
        #end for exposed

    def adjust_screen_position_for_left_bottom(self):
        self.all_group.empty()
        for sprite in self.concealed_group:
            self.all_group.add(sprite)
        for sprite in self.exposed_group:
            self.all_group.add(sprite)
        for sprite in self.discarded_group:
            self.all_group.add(sprite)

        for sprite in self.all_group:
            img_original = sprite.image
            rect_original = sprite.rect
            rotated = None
            rect = None
            left, bottom = rect_original.left, rect_original.bottom
            if self._isViewer:
                left += Setting.win_w_h_half
                rotated = img_original
                rect = rect_original
                rect.left, rect.bottom = left, Setting.WinH - bottom
            elif self.position == Suit.getNextWind(self.viewerPosition):
                angel = 90
                rotated = pygame.transform.rotate(img_original, angel)
                rect = rotated.get_rect()
                rect.bottom, rect.right = Setting.WinH - left, Setting.WinW - bottom
            elif self.position == Suit.getBeforeWind(self.viewerPosition):
                angel = 270
                rotated = pygame.transform.rotate(img_original, angel)
                rect = rotated.get_rect()
                rect.top, rect.left = left, bottom
            elif self.position == Suit.getOppositionWind(self.viewerPosition):
                left += Setting.win_w_h_half
                angel = 180
                rotated = pygame.transform.rotate(img_original, angel)
                rect = rotated.get_rect()
                rect.right, rect.top = Setting.WinW - left, bottom
            else:
                sprite.kill()

            sprite.image = rotated
            sprite.rect = rect

    def adjust_screen_position_for_centerx_bottom(self):
        for sprite in self.info_group:
            img_original = sprite.image
            rect_original = sprite.rect
            rotated = None
            rect = None
            centerx, bottom = rect_original.centerx, rect_original.bottom
            if self.isViewer:
                rotated = img_original
                rect = rect_original
                rect.centerx, rect.bottom = centerx, Setting.WinH - bottom
            elif self.position == Suit.getNextWind(self.viewerPosition):
                angel = 90
                rotated = pygame.transform.rotate(img_original, angel)
                rect = rotated.get_rect()
                rect.centery, rect.right = (Setting.WinH - Setting.WinW) // 2 + centerx, Setting.WinW - bottom
            elif self.position == Suit.getBeforeWind(self.viewerPosition):
                angel = 270
                rotated = pygame.transform.rotate(img_original, angel)
                rect = rotated.get_rect()
                rect.centery, rect.left = (Setting.WinH - Setting.WinW) // 2 + centerx, bottom
            elif self.position == Suit.getOppositionWind(self.viewerPosition):
                angel = 180
                rotated = pygame.transform.rotate(img_original, angel)
                rect = rotated.get_rect()
                rect.centerx, rect.top = centerx, bottom
            else:
                sprite.kill()

            sprite.image = rotated
            sprite.rect = rect

    def draw_screen(self, state = ''):
        if not self._screen: return
        self.draw_info()
        self.draw_concealed(state)
        self.draw_exposed(state)
        self.draw_discard()
        self.adjust_screen_position_for_centerx_bottom()
        self.adjust_screen_position_for_left_bottom()
        self.info_group.draw(self.screen)
        self.all_group.draw(self.screen)