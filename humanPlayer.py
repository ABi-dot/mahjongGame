import sys

import pygame
from utils.player import Player
from setting import Setting
from utils.tile import Tile
from utils.mjSet import MjSet
from sprite import Sprite
from utils.rule import Rule
from utils.mjMath import MjMath
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.shanten import Shanten
from mahjong.tile import TilesConverter



class HumanPlayer(Player):
    def __init__(self, nick="bot", score: int = 25000, isViewer: bool = False, viewerPosition: str = '东',
                 screen=None, clock=None):
        super().__init__(nick=nick, score=score, isViewer=isViewer, viewerPosition=viewerPosition,
                         screen=screen, clock=clock)
        self.cmd = ' '
        self.waiting_cmd = []
        self.waiting_group = pygame.sprite.Group()

    def draw(self, mjSet: MjSet):
        return super().draw(mjSet)

    def decide_discard(self) -> Tile:
        self.currentIdx = len(self.concealed) - 1
        choices = [[i] for i in range(len(self.concealed))]
        self.currentTiles = choices[self.currentIdx]
        if self.hand:
            self.hand.refresh_screen()
        allowed_cmd = ['discard']
        self.waiting_4_cmd(allowed_cmd=allowed_cmd, choices=choices)
        tile = self.concealed[self.currentIdx]
        self.currentTiles = []
        return tile

    def draw_waiting_cmd(self):
        self.waiting_group.empty()
        if not self.waiting_cmd:
            return
        left = Setting.concealed_bottom
        bottom = Setting.WinH - Setting.concealed_bottom
        for cmd in self.waiting_cmd:
            if cmd not in Setting.waiting_img:
                continue
            cmd_img = Setting.sprite_base + Setting.waiting_img[cmd]
            image = pygame.image.load(cmd_img)
            sprite = Sprite(image)
            sprite.rect.left = left
            sprite.rect.bottom = bottom
            self.waiting_group.add(sprite)
            left += sprite.rect.w + Setting.waiting_img_span
            self.waiting_group.draw(self.screen)

    def draw_screen(self, state=''):
        super().draw_screen(state=state)
        self.draw_waiting_cmd()

    def try_mahjong(self, tile=None) -> bool:
        test = self.concealed[:]
        if tile:
            test.append(tile)
        if Rule.is_rong(test):
            choices = []
            allowed_cmd = ['hu', 'cancel']
            cmd = self.waiting_4_cmd(allowed_cmd=allowed_cmd, choices=choices)
            if cmd == 'cancel':
                return False
            elif cmd == 'hu':
                return True
            else:
                raise ValueError("exposed hu error cmd:", cmd)
        return False

    def try_exposed_pong(self, tile: Tile, owner) -> bool:
        count = 0
        arr = []
        for index, test in enumerate(self.concealed):
            if tile.key == test.key:
                count += 1
                arr.append(index)
                if count >= 2:
                    break
        if count < 2:
            return False

        choices = [arr]
        allowed_cmd = ['pong', 'cancel']
        cmd = self.waiting_4_cmd(allowed_cmd=allowed_cmd, choices=choices)
        if cmd == 'cancel':
            return False
        elif cmd == 'pong':
            self.exposed_pong(tile, owner=owner)
            return True
        else:
            raise ValueError("exposed pong error cmd:", cmd)

    def try_riichi(self):
        if not self._is_closed:
            return False
        shanten = Shanten()
        m, p, s, h = Rule.convert_arr_to_mpsh(Rule.convert_tiles_to_arr(self.concealed))
        for expose in self.exposed:
            if expose.expose_type != 'concealed kong': return False
        tiles = TilesConverter.string_to_34_array(man=m, sou=s, pin=p, honors=h)
        result = shanten.calculate_shanten(tiles)
        if result <= 0:
            allowed_cmd = ['riichi', 'cancel']
            choices = []
            for index in range(len(self.concealed)):
                test_tiles = []
                for i, tile in enumerate(self.concealed):
                    if i != index:
                        test_tiles.append(tile)
                shanten = Shanten()
                m, p, s, h = Rule.convert_arr_to_mpsh(Rule.convert_tiles_to_arr(test_tiles))
                tiles = TilesConverter.string_to_34_array(man=m, sou=s, pin=p, honors=h)
                res = shanten.calculate_shanten(tiles)
                if res <= 0:
                    choices.append([index])
            cmd = self.waiting_4_cmd(allowed_cmd=allowed_cmd, choices=choices)
            if cmd == 'cancel':
                return False
            elif cmd == 'riichi':
                self.currentIdx = 0
                tile_index = choices[self.currentIdx][0]
                tile = self.concealed[tile_index]
                self.discard(tile)
                self.riichi()
                self.hand.currentDiscard = tile
                return True
        else:
            return False

    def try_conceal_kong(self, mjSet: MjSet) -> bool:
        if not self.concealed:
            return False
        if not mjSet.get_left_tiles_cnt():
            return False
        test_tiles = list(set(self.concealed))
        choices = []
        for x in test_tiles:
            choice = []
            if self.concealed.count(x) < 4:
                continue
            count = 0
            for index, y in enumerate(self.concealed):
                if x.key == y.key:
                    choice.append(index)
                    count += 1
                    if count >= 4:
                        break
            choices.append(choice)
        if not choices:
            return False

        allowed_cmd = ['kong', 'cancel']
        self.currentIdx = 0
        cmd = self.waiting_4_cmd(allowed_cmd=allowed_cmd, choices=choices)
        if cmd == 'cancel':
            return False
        elif cmd == 'kong':
            print("self.current_index:", self.currentIdx)
            print("choices:", choices)
            tile_index = choices[self.currentIdx][0]
            tile = self.concealed[tile_index]
            self.concealed_kong(tile=tile, mjSet=mjSet)
            return True
        else:
            raise ValueError("concealed kong error cmd:", cmd)

    def try_exposed_kong_from_exposed_pong(self, mjSet: MjSet) -> bool:
        tile = self.concealed[-1]
        if not mjSet.get_left_tiles_cnt():
            return False
        if not self.exposed:
            return False
        for expose in self.exposed:
            if expose.expose_type == 'exposed pong' and expose.outer.key == tile.key:
                print("human player's try_exposed_kong_from_exposed_pong")
                print("tile:", tile)
                print("expose:", expose)
                allowed_cmd = ['kong', 'cancel']
                self.currentIdx = 0
                choices = [[len(self.concealed) - 1]]
                cmd = self.waiting_4_cmd(allowed_cmd=allowed_cmd, choices=choices)
                if cmd == 'cancel':
                    return False
                elif cmd == 'kong':
                    self.exposed_kong_from_exposed_pong(tile=tile,expose=expose,mjSet=mjSet)
                    return True
        return False

    def try_exposed_kong(self, tile: Tile, owner, mjSet: MjSet) -> bool:
        count = 0
        arr = []
        for index, test in enumerate(self.concealed):
            if test.key == tile.key:
                count += 1
                arr.append(index)
                if count >= 3:
                    break
        if count < 3:
            return False

        choices = [arr]
        allowed_cmd = ['kong', 'cancel']
        cmd = self.waiting_4_cmd(allowed_cmd=allowed_cmd, choices=choices)
        if cmd == 'cancel':
            return False
        elif cmd == 'kong':
            self.exposed_kong(tile=tile, owner=owner, mjSet=mjSet)
            return True
        else:
            raise ValueError("exposed kong error cmd:", cmd)

    def try_exposed_chow(self, tile: Tile, owner) -> bool:
        arr = Rule.convert_tiles_to_arr(self.concealed)
        outer = tile.key
        combins = MjMath.get_chow_combins_from_arr(arr=arr, outer=outer)
        if not combins:
            return False
        choices = []
        for combin in combins:
            choice = []
            for x in combin:
                index = arr.index(x)
                choice.append(index)
            choices.append(choice)

        allowed_cmd = ['chow', 'cancel']
        cmd = self.waiting_4_cmd(allowed_cmd=allowed_cmd, choices=choices)
        if cmd == 'cancel':
            return False
        elif cmd == 'chow':
            arr = choices[self.currentIdx]
            inners = []
            for index in arr:
                inners.append(self.concealed[index])
            super().exposed_chow(inners=inners,tile=tile,owner=owner)
            return True
        else:
            raise ValueError("exposed chow error cmd:", cmd)

    def waiting_4_cmd(self, allowed_cmd=[], choices=[], draw_screen=True):
        if not allowed_cmd:
            raise ValueError("need cmd")
        default_cmd = allowed_cmd[0]

        if choices:
            if self.currentIdx < 0 or self.currentIdx >= len(choices):
                self.currentIdx = 0
            self.currentTiles = choices[self.currentIdx]
        self.waiting_cmd = allowed_cmd
        if draw_screen:
            self.draw_screen()
            if self.hand:
                self.hand.refresh_screen()

        cmd = ''
        while not cmd or cmd not in allowed_cmd:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_r]:
                        cmd = 'riichi'
                    if keys[pygame.K_c]:
                        cmd = 'chow'
                    if keys[pygame.K_p]:
                        cmd = 'pong'
                    if keys[pygame.K_k]:
                        cmd = 'kong'
                    if keys[pygame.K_h]:
                        cmd = 'hu'
                    if keys[pygame.K_e]:
                        cmd = 'cancel'
                    if keys[pygame.K_KP_ENTER] or keys[pygame.K_RETURN]:
                        cmd = default_cmd
                    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                        if choices:
                            self.currentIdx -= 1
                            if self.currentIdx < 0:
                                self.currentIdx = len(choices) - 1
                            self.currentTiles = choices[self.currentIdx]
                    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                        if choices:
                            self.currentIdx += 1
                            if self.currentIdx >= len(choices):
                                self.currentIdx = 0
                            self.currentTiles = choices[self.currentIdx]
            if cmd not in allowed_cmd:
                cmd = ''

            self.clock.tick(Setting.cmd_FPS)

            self.draw_screen()
            self.hand.refresh_screen()
        return cmd