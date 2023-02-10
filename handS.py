from utils.hand import Hand
import pygame
from setting import Setting
from sprite import Sprite
from color import Color
from utils.suit import Suit
from utils.mjMath import MjMath

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