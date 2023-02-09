import pygame
import sys
from setting import Setting
from color import *
from utils.game import Game

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((Setting.WinW, Setting.WinH))
screen.fill(Color.WHITE)
pygame.display.set_caption(Setting.GameName)
pygame.font.init()
pygame.mixer.init()

game = Game(screen=screen, clock=clock)
game.prepare()
game.play()