import pygame
import sys
from setting import Setting
from humanPlayer import HumanPlayer
from utils.aiPlayer import AIPlayer
from random import shuffle
from utils.suit import Suit
from handS import HandS

class Game(object):
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.circles = Setting.gameCircles
        self.startScore = Setting.gameStartScore
        self.opposites = Setting.gameOpposites[0:3]
        #self.player = HumanPlayer(Setting.gamePlayer, score=self.startScore, isViewer=True, screen=screen, clock=clock)
        self.player = AIPlayer(Setting.gamePlayer, score=self.startScore, isViewer=True, screen=screen, clock=clock)
        self.players = []


    def prepare(self):
        self.players.append(self.player)
        for name in self.opposites:
            ai = AIPlayer(nick=name, score=self.startScore, screen=self.screen, clock=self.clock)
            self.players.append(ai)

    def play(self):
        shuffle(self.players)
        for _ in range(self.circles):
            index = _ % 4
            prevailingWind = Suit.getWindByIndex(index)
            self.circle(prevailingWind=prevailingWind)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit(0)
            pygame.display.flip()

    #排座
    def circle(self, prevailingWind):
        for idx in range(4):
            hand = HandS(players=self.players, viewer=self.player,
                         number=idx+1, prevailingWind=prevailingWind,
                         screen=self.screen, clock=self.clock)
            hand.prepare()
            hand.deal()

            hand.play()
