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
        self._handName = pygame.sprite.Group()

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
        currentDiscard = None

        haveWinner = False
        while not haveWinner and self.mjSet.get_left_tiles_cnt() > 0:
            if currentDiscard:
                wind = current.position
                player = current
                for index in range(3):
                    if player.try_mahjong(currentDiscard):
                        player.concealed.append(currentDiscard)
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
            if currentDiscard:
                player = None
                # try kong ( must have tiles ):
                if self.mjSet.get_left_tiles_cnt() > 0:
                    wind = current.position
                    player = current
                    for index in range(3):
                        try:
                            if player.try_exposed_kong(tile=currentDiscard, owner=before, mjSet=self._mjSet):
                                self.refresh_screen('drawing')
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
                        if player.try_exposed_pong(tile=currentDiscard, owner=before):
                            self.refresh_screen()
                            interrupted = True
                            break
                        wind = Suit.getNextWind(wind)
                        player = self.positions[wind]

                # try chow
                if not interrupted:
                    # wind = current.position
                    player = current
                    if player.try_exposed_chow(currentDiscard, before):
                        self.refresh_screen()
                        interrupted = True
                if not interrupted:
                    before.put_on_desk(currentDiscard)
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

                # self kong
                try:
                    if current.try_conceal_kong(self.mjSet):
                        pass
                except OutOfTilesError as e:
                    self.withdraw()
                except HaveWinnerError as e:
                    self._winner = current
                    self.mahjong_on_kong = True
                    self.firer = current
                    self._stateMachine.mahjong()
                    have_winner = True
                    self.refresh_screen(state='mahjong')
                    break
                if self.winner:
                    break

                # test for exposed kong from exposed pong
                result_of_try = False
                try:
                    result_of_try = current.try_exposed_kong_from_exposed_pong(mjSet=self.mjSet)
                except OutOfTilesError as e:
                    self.withdraw()
                except HaveWinnerError as e:
                    self._winner = current
                    self.mahjong_on_kong = True
                    self.firer = current
                    self._stateMachine.mahjong()
                    have_winner = True
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

            tile = current.decide_discard()
            current.discard(tile)
            print(current, 'discard tile:', tile)

            currentDiscard = tile
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


    def refresh_screen(self, state: str = ''):
        self.drawbackground()

        for player in self.players:
            player.draw_screen(state=state)

        text = self._font.render(u'%d' % self.mjSet.get_left_tiles_cnt(), 1, Color.WHITE)
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