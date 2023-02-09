from utils.hand import Hand
import pygame
from setting import Setting
from color import Color

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



    @property
    def screen(self):
        return self._screen

    def drawbackground(self):
        self._bgImgGroup.draw(self.screen)
        self._handName.draw(self.screen)