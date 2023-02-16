import time

from utils.hand import Hand
import pygame
from setting import Setting
from sprite import Sprite
from color import Color
from utils.error import *
from utils.suit import Suit
from utils.rule import Rule
from utils.mjMath import MjMath
from utils.tile import Tile

class HandS(Hand):
    def __init__(self, players: list = None, prevailingWind: str = '东',
                 number = 1, screen=None, clock=None, viewer=None):
        if not screen:
            raise ValueError("Need a screen!")
        if not clock:
            raise ValueError("Need a clock!")
        if not viewer:
            raise ValueError("Need a viewer!")
        self._screen = screen
        self._clock = clock
        self._player = viewer
        self._font = pygame.font.Font(Setting.font, Setting.normalFontSize)
        self._bgImgGroup = pygame.sprite.Group()
        self._infoGroup = pygame.sprite.Group()
        self._bonusGroup = pygame.sprite.Group()
        self._handName = pygame.sprite.Group()
        self.currentDiscard = None

        handName = prevailingWind + str(number) + '局'
        print(handName)
        normalFont = pygame.font.Font(Setting.font, Setting.normalFontSize)
        img = normalFont.render(handName, True, Color.WHITE)
        sprite = pygame.sprite.Sprite()
        sprite.image = img
        sprite.rect = img.get_rect()
        sprite.rect.top = Setting.handNameTop
        sprite.rect.left = Setting.handNameLeft
        self._handName.add(sprite)
        #self._handName.draw(self._screen)

        bgImg = pygame.image.load(Setting.bgImg)
        bgImg = pygame.transform.scale(bgImg, (Setting.WinW, Setting.WinH))
        rect = bgImg.get_rect()
        sprite = pygame.sprite.Sprite()
        sprite.image = bgImg
        sprite.rect = rect
        self._bgImgGroup.add(sprite)
        self.drawbackground()


        if players:
            viewer = None
            for idx, player in enumerate(players):
                player.position = Suit.getWindByIndex(idx)
                if player.isViewer:
                    viewer = player
                    player.hand = self
            for player in players:
                player.viewerPosition = viewer.position
            if viewer:
                font = pygame.font.Font(Setting.font, Setting.normalFontSize)
                for idx, player in enumerate(players):
                    suit = player.position
                    image = font.render(suit, True, Color.YELLOW)
                    scoreImg = font.render(str(player.score), True, Color.WHITE)
                    nickImg = font.render(str(player.nick), True, Color.WHITE)

                    score = Sprite(scoreImg)
                    nick = Sprite(nickImg)
                    if suit == Suit.getNextWind(player.viewerPosition):
                        angle = 90
                        image = pygame.transform.rotate(image, angle)
                        sprite = Sprite(image)
                        sprite.rect.centery = Setting.WinH // 2
                        sprite.rect.left = Setting.WinW // 2 + Setting.dealerWind

                        nick.rect.top = Setting.nickRightTop
                        nick.rect.right = Setting.WinW - Setting.concealedBottom
                        score.rect.top = Setting.nickRightTop + nick.rect.h
                        score.rect.centerx = Setting.WinW - Setting.concealedBottom - nick.rect.w // 2
                    elif suit == Suit.getBeforeWind(player.viewerPosition):
                        angle = 270
                        image = pygame.transform.rotate(image, angle)
                        sprite = Sprite(image)
                        sprite.rect.centery = Setting.WinH // 2
                        sprite.rect.right = Setting.WinW // 2 - Setting.dealerWind

                        nick.rect.bottom = Setting.WinH - Setting.concealedBottom
                        nick.rect.left = Setting.concealedBottom
                        score.rect.bottom = Setting.WinH - Setting.concealedBottom - nick.rect.w // 2
                        score.rect.centerx = Setting.concealedBottom + nick.rect.w // 2
                    elif suit == player.viewerPosition:
                        sprite = Sprite(image)
                        sprite.rect.top = Setting.WinH // 2 + Setting.dealerWind
                        sprite.rect.centerx = Setting.WinW // 2

                        nick.rect.bottom = Setting.WinH - Setting.concealedBottom
                        nick.rect.left = 295
                        score.rect.top = Setting.WinH - Setting.concealedBottom
                        score.rect.centerx = 295 + nick.rect.w // 2
                    else:
                        angle = 180
                        image = pygame.transform.rotate(image, angle)
                        sprite = Sprite(image)
                        sprite.rect.bottom = Setting.WinH // 2 - Setting.dealerWind
                        sprite.rect.centerx = Setting.WinW // 2

                        nick.rect.bottom = Setting.concealedBottom
                        nick.rect.right = Setting.WinW - 295
                        score.rect.top = Setting.concealedBottom
                        score.rect.centerx = Setting.WinW - 295 - nick.rect.w // 2


                    self._handName.add(sprite)
                    self._handName.add(score)
                    self._handName.add(nick)
                    self.drawbackground()
        super().__init__(players=players, prevailingWind=prevailingWind)






    @property
    def screen(self):
        return self._screen

    def drawbackground(self):
        self._bgImgGroup.draw(self.screen)
        self._handName.draw(self.screen)

    def deal(self):
        for _ in range(max(MjMath.concealed_count) // 4):
            for player in self.players:
                player.drawstack(self.mjSet)
        for player in self.players:
            player.draw(self.mjSet)
            player.sortconcealed()
            self.refresh_screen()

        self._stateMachine.deal()

    def play(self):
        current = self._dealer
        before = None
        self.currentDiscard = None

        haveWinner = False
        while not haveWinner and self.mjSet.get_left_tiles_cnt() >= 0:
            if self.currentDiscard:
                wind = current.position
                player = current
                for index in range(3):
                    if player.try_mahjong(self.currentDiscard):
                        player.concealed.append(self.currentDiscard)
                        print(f"winner is {player}, by {before}")
                        self._winner = before
                        self.firer = before
                        self._stateMachine.mahjong()
                        haveWinner = True
                        self.refresh_screen(state='mahjong')
                        break
                    wind = Suit.getNextWind(wind)
                    player = self.positions[wind]
            if haveWinner:
                break

            interrupted = False
            if self.currentDiscard:
                player = None
                # try kong ( must have tiles ):
                if self.mjSet.get_left_tiles_cnt() > 0 and self.mjSet.bonus_count < 5:
                    wind = current.position
                    player = current
                    for index in range(3):
                        try:
                            if not player.is_riichi and player.try_exposed_kong(tile=self.currentDiscard, owner=before, mjSet=self._mjSet):
                                self.refresh_screen('drawing')
                                self.mjSet.bonus_count += 1
                                # self._sound_kong.play()
                                interrupted = True
                                break
                        except OutOfTilesError as e:
                            self.withdraw()
                        except HaveWinnerError as e:
                            self._winner = player
                            self.mahjong_on_kong = True
                            self.firer = player
                            self._stateMachine.mahjong()
                            have_winner = True
                            self.refresh_screen(state='mahjong')
                            break
                        wind = Suit.getNextWind(wind)
                        player = self.positions[wind]
                    if self._winner:
                        break

                # try pong
                if not interrupted:
                    wind = current.position
                    player = current
                    for index in range(3):
                        if not player.is_riichi and player.try_exposed_pong(tile=self.currentDiscard, owner=before):
                            self.refresh_screen()
                            interrupted = True
                            break
                        wind = Suit.getNextWind(wind)
                        player = self.positions[wind]

                # try chow
                if not interrupted:
                    # wind = current.position
                    player = current
                    if not player.is_riichi and player.try_exposed_chow(self.currentDiscard, before):
                        self.refresh_screen()
                        interrupted = True
                if not interrupted:
                    before.put_on_desk(self.currentDiscard)
                before.discarding = None
            # end if currentDiscard

            if interrupted:
                current = player
            else:
                # test for out of tiles
                if self.mjSet.get_left_tiles_cnt() == 0:
                    self.withdraw()
                    break

                # draw
                new_tile = current.draw(self.mjSet)
                if not new_tile:
                    self.withdraw()
                    break
                self.refresh_screen(state='drawing')

                # test for hu by self
                if current.try_mahjong(tile=None):
                    print(f"winner is {current}, by self!")
                    self._winner = current
                    self.firer = current
                    self._stateMachine.mahjong()
                    self.refresh_screen(state='mahjong')
                    break
                if current.is_riichi:
                    current.discard(new_tile)
                    print(current, 'discard tile:', new_tile)
                    self.currentDiscard = new_tile
                if self.winner:
                    break
                if not current.is_riichi and current.try_riichi():
                    self.refresh_screen()
                # self kong
                try:
                    if not current.is_riichi and current.try_conceal_kong(self.mjSet) and self.mjSet.bonus_count < 5:
                        self.mjSet.bonus_count += 1
                except OutOfTilesError as e:
                    self.withdraw()
                except HaveWinnerError as e:
                    self._winner = current
                    self.mahjong_on_kong = True
                    self.firer = current
                    self._stateMachine.mahjong()
                    haveWinner = True
                    self.refresh_screen(state='mahjong')
                    break
                if self.winner:
                    break

                # test for exposed kong from exposed pong
                result_of_try = False
                try:
                    if not current.is_riichi and self.mjSet.bonus_count < 5:
                        result_of_try = current.try_exposed_kong_from_exposed_pong(mjSet=self.mjSet)
                        if result_of_try:
                            self.mjSet.bonus_count += 1
                except OutOfTilesError as e:
                    self.withdraw()
                except HaveWinnerError as e:
                    self._winner = current
                    self.mahjong_on_kong = True
                    self.firer = current
                    self._stateMachine.mahjong()
                    haveWinner = True
                    self.refresh_screen(state='mahjong')

                if result_of_try:
                    # try rob kong by others
                    self.refresh_screen()

                    # others try mahjong
                    player = None
                    wind = current.position
                    for index in range(3):
                        wind = Suit.getNextWind(wind)
                        player = self.positions[wind]
                        if player.try_mahjong(tile=new_tile):
                            print(f"winner is {player}, by rob {current}!")
                            player.concealed.append(new_tile)
                            self._winner = player
                            self.firer = current
                            self._stateMachine.mahjong()
                            self.refresh_screen(state='mahjong')
                            self.robbing_a_kong = True
                            break
                    if self._winner:
                        break
                if self._winner:
                    break
            if not current.is_riichi:
                tile = current.decide_discard()
                current.discard(tile)
                self.currentDiscard = tile
                print(current, 'discard tile:', tile)


            current.sortconcealed()

            # next player
            next = self._get_next_player(current)
            before = current
            current = next

            self.refresh_screen()

        # end while

        self.refresh_screen(state='scoring')
        print("tiles left :", self.mjSet.get_left_tiles_cnt())
        for player in self.players:
            if player == self.winner:
                print(f"winner {player}: ", Rule.convert_tiles_to_str(player.concealed))
            else:
                print(f"{player}: ", Rule.convert_tiles_to_str(player.concealed))

    # end def play()

    def drawbonus(self):
        self._bonusGroup.empty()
        text = self._font.render('宝牌指示牌', True, Color.YELLOW)
        sprite = Sprite(text)
        sprite.rect.left = Setting.bonus_text_left
        sprite.rect.bottom = Setting.WinH - Setting.bonus_text_bottom
        self._bonusGroup.add(sprite)
        left = Setting.bonus_text_left
        top = Setting.WinH - Setting.bonus_text_bottom + Setting.bonus_text_img_span
        for i in range(5):
            if i + 1 <= self.mjSet.bonus_count:
                tile = self.mjSet.bonus[i]
                path = Setting.tileImgPath + tile.img
            else:
                path = Setting.tileImgPath + Setting.facedownImg
            image = pygame.image.load(path)
            sprite = Sprite(image)
            sprite.rect.left = left
            sprite.rect.top = top
            self._bonusGroup.add(sprite)
            left += sprite.rect.w

        self._bonusGroup.draw(self.screen)

    def refresh_screen(self, state: str = ''):
        self.drawbackground()
        self.drawbonus()
        for player in self.players:
            player.draw_screen(state=state)

        text = self._font.render(u'%d' % self.mjSet.get_left_tiles_cnt(), True, Color.WHITE)
        sprite = Sprite(text)
        sprite.rect.centerx = Setting.WinW // 2
        sprite.rect.centery = Setting.WinH // 2
        info_group = pygame.sprite.Group()
        info_group.add(sprite)
        info_group.draw(self.screen)

        self._clock.tick(Setting.FPS)
        pygame.display.flip()

    def withdraw(self):
        print("out of tiles!")
        self._winner = None
        self.out_of_tiles = True
        self._stateMachine.withdraw()