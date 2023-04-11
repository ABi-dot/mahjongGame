import time

import pygame
import sys
from setting import Setting
from color import *
from utils.game import Game
from sprite import Sprite
from utils.review import Review
from utils.load import Load

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((Setting.WinW, Setting.WinH))
screen.fill(Color.WHITE)
pygame.display.set_caption(Setting.GameName)
pygame.font.init()
pygame.mixer.init()

def draw_interface(screen):
    bgImgGroup = pygame.sprite.Group()
    functionGroup = pygame.sprite.Group()
    font = pygame.font.Font(Setting.font, Setting.bigFontSize)
    bgImg = pygame.image.load(Setting.bgImg)
    bgImg = pygame.transform.scale(bgImg, (Setting.WinW, Setting.WinH))
    sprite = Sprite(bgImg)
    bgImgGroup.add(sprite)
    fontimage1 = font.render('对战功能：1', True, Color.YELLOW)
    fs = Sprite(fontimage1)
    fs.rect.centerx = Setting.WinW // 2
    fs.rect.centery = Setting.WinH // 2 - 50
    functionGroup.add(fs)
    fontimage2 = font.render('复盘分析功能：2', True, Color.YELLOW)
    fs = Sprite(fontimage2)
    fs.rect.centerx = Setting.WinW // 2
    fs.rect.centery = Setting.WinH // 2
    functionGroup.add(fs)
    bgImgGroup.draw(screen)
    functionGroup.draw(screen)
    pygame.display.flip()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                game = Game(screen=screen, clock=clock)
                game.prepare()
                game.play()
            if keys[pygame.K_2]:
                load = Load(screen=screen, clock=clock)
                file_name = load.load()
                if file_name:
                    review = Review(Setting.save_file_path + '/' + file_name, screen=screen, clock=clock, model=True)
                    review.play()
        draw_interface(screen)

