from utils.saving import Saving
from utils.player import Player
import pygame
from setting import Setting
from utils.suit import Suit
from color import Color
from sprite import Sprite
from utils.mjSet import MjSet
from utils.tile import Tile
import os
import sys
import torch
import collections
import torch.nn as nn
import torch.nn.functional as F
from utils.rule import Rule
import numpy as np


class QNet(nn.Module):
    """QNet.
    Input: feature
    Output: num_act of values
    """

    def __init__(self, dim_state, num_action):
        super().__init__()
        self.fc1 = nn.Linear(dim_state, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, num_action)

    def forward(self, state):
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

class DQN:
    def __init__(self, dim_state=None, num_action=None, discount=0.9):
        self.discount = discount
        self.Q = QNet(dim_state, num_action)
        self.target_Q = QNet(dim_state, num_action)
        self.target_Q.load_state_dict(self.Q.state_dict())

    def get_qvals(self, state):
        return self.Q(state)

    def get_action(self, state):
        qvals = self.Q(state)
        return qvals.argmax()

    def compute_loss(self, s_batch, a_batch, r_batch, d_batch, next_s_batch):
        # 计算s_batch，a_batch对应的值。
        qvals = self.Q(s_batch).gather(1, a_batch.unsqueeze(1)).squeeze()
        # 使用target Q网络计算next_s_batch对应的值。
        next_qvals, _ = self.target_Q(next_s_batch).detach().max(dim=1)
        # 使用MSE计算loss。
        loss = F.mse_loss(r_batch + self.discount * next_qvals * (1 - d_batch), qvals)
        return loss


class Review:
    def __init__(self, filename, screen, clock, model):
        saving = Saving(filename)
        self.data = saving.load_data()
        self.info = self.data['info']
        self.step = 0
        self.screen = screen
        self.clock = clock
        self.players = []
        self.prevailingWind = ''
        self.number = 0
        self.seq = self.data['seq']
        self.seq_len = len(self.seq)
        self.font = pygame.font.Font(Setting.font, Setting.normalFontSize)
        self.mjSet: MjSet = MjSet()
        self.model = model
        if self.model:
            self.card_encoding_dict = {}
            self._init_card_encoding()
            self.action_id = self.card_encoding_dict
            self.de_action_id = {self.action_id[key]: key for key in self.action_id.keys()}
            self.agent = DQN(34*4, 34)
            model_path = os.path.join('.', "model.bin")
            self.agent.Q.load_state_dict(torch.load(model_path))

        self._bgImgGroup = pygame.sprite.Group()
        self._infoGroup = pygame.sprite.Group()
        self._bonusGroup = pygame.sprite.Group()
        self._scorebonusGroup = pygame.sprite.Group()
        self._handName = pygame.sprite.Group()

    def _init_card_encoding(self):
        for i in range(101, 110):
            self.card_encoding_dict[i] = i - 101
        for i in range(201, 210):
            self.card_encoding_dict[i] = i - 192
        for i in range(301, 310):
            self.card_encoding_dict[i] = i - 283
        for i in range(410, 435, 10):
            self.card_encoding_dict[i] = (i // 10) % 10 + 26
        for i in range(510, 545, 10):
            self.card_encoding_dict[i] = (i // 10) % 10 + 29
        self.card_encoding_dict['pong'] = 34
        self.card_encoding_dict['chow'] = 35
        self.card_encoding_dict['kong'] = 36
        self.card_encoding_dict['riichi'] = 37
        self.card_encoding_dict['stand'] = 38

    def convert_arr_to_index(self, arr):
        d = []
        for num in arr:
            if num < 200:
                d.append(num-101)
            elif num < 300:
                d.append(num - 192)
            elif num < 400:
                d.append(num - 283)
            elif num < 500:
                d.append((num // 10) % 10 + 26)
            else:
                d.append((num // 10) % 10 + 29)
        return d

    def generate_status(self, c):
        arr = self.convert_arr_to_index(Rule.convert_tiles_to_arr(c))
        c = collections.Counter(arr)
        state = np.zeros((34, 4), dtype=float)
        for k, v in c.items():
            state[k][:v] = 1
        flat = np.ndarray.flatten(state)
        return flat

    def play(self):
        self.handle_data()
        while True:
            self.draw_stat()
            allowed_cmd = ['exit', 'move']
            res = self.waiting_4_cmd(allowed_cmd)
            if res == 'exit':
                break
            pygame.display.flip()

    def handle_data(self):
        self.prevailingWind = self.info['prevailingWind']
        self.number = self.info['number']
        players_info = self.info['players']
        for player_info in players_info:
            nick = player_info['nick']
            score = player_info['score']
            isviewer = player_info['isviewer']
            viewerposition = player_info['viewerposition']
            player = Player(nick=nick, score=score, isViewer=isviewer, viewerPosition=viewerposition,
                            screen=self.screen, clock=self.clock)
            self.players.append(player)

        self.draw_info()
        self.draw_players()


    def waiting_4_cmd(self, allowed_cmd=[]):
        if not allowed_cmd:
            raise ValueError("need cmd")
        cmd = ''
        while not cmd or cmd not in allowed_cmd:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                        cmd = 'move'
                        self.step -= 1
                        if self.step < 0:
                            self.step = 0
                    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                        cmd = 'move'
                        self.step += 1
                        if self.step >= self.seq_len:
                            self.step = self.seq_len - 1
                    if keys[pygame.K_q] or keys[pygame.K_ESCAPE]:
                        cmd = 'exit'
        return cmd

    def drawbonus(self):
        self._bonusGroup.empty()
        text = self.font.render('宝牌指示牌', True, Color.YELLOW)
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

    def refresh_screen(self, state = ''):
        self.drawbackground()
        self.drawbonus()
        for player in self.players:
            player.draw_screen(state)
        text = self.font.render(u'%d' % self.mjSet.get_left_tiles_cnt(), True, Color.WHITE)
        sprite = Sprite(text)
        sprite.rect.centerx = Setting.WinW // 2
        sprite.rect.centery = Setting.WinH // 2
        info_group = pygame.sprite.Group()
        info_group.add(sprite)
        info_group.draw(self.screen)
        pygame.display.flip()

    def draw_stat(self, state=''):
        record = self.seq[self.step]
        for r in record['players']:
            nick = r['nick']
            for player in self.players:
                if player.nick == nick:
                    player._concealed = r['concealed']
                    player._exposed = r['exposed']
                    player._discarded = r['discarded']
                    player._discarding = r['discarding']
                    player._desk = r['desk']
                    player._position = r['position']
                    break
        if self.model:
            for player in self.players:
                if player.nick == 'lyf':
                    if len(player.concealed) % 3 == 2:
                        state = self.generate_status(player.concealed)
                        qvals = self.agent.get_qvals(torch.from_numpy(state).float())
                        for i in range(34):
                            tile = Rule.convert_key_to_tile(self.get_de_action_id(i))
                            exist = False
                            for t in player.concealed:
                                if tile.key == t.key:
                                    exist = True
                                    break
                            if not exist:
                                qvals[i] = float("-inf")
                        print(qvals)
                        action = qvals.argmax()
                        action = action.item()
                        print(Rule.convert_key_to_tile(self.get_de_action_id(action)))

        self.mjSet = record['mjSet']
        self.refresh_screen(state)

    def get_de_action_id(self, action):
        return self.de_action_id[action]

    def drawbackground(self):
        self._bgImgGroup.draw(self.screen)
        self._handName.draw(self.screen)

    def draw_info(self):
        handName = self.prevailingWind + str(self.number) + '局'
        print(handName)
        normalFont = pygame.font.Font(Setting.font, Setting.normalFontSize)
        img = normalFont.render(handName, True, Color.WHITE)
        sprite = pygame.sprite.Sprite()
        sprite.image = img
        sprite.rect = img.get_rect()
        sprite.rect.top = Setting.handNameTop
        sprite.rect.left = Setting.handNameLeft
        self._handName.add(sprite)
        # self._handName.draw(self._screen)

        bgImg = pygame.image.load(Setting.bgImg)
        bgImg = pygame.transform.scale(bgImg, (Setting.WinW, Setting.WinH))
        rect = bgImg.get_rect()
        sprite = pygame.sprite.Sprite()
        sprite.image = bgImg
        sprite.rect = rect
        self._bgImgGroup.add(sprite)
        self.drawbackground()

    def draw_players(self):
        if self.players:
            viewer = None
            for idx, player in enumerate(self.players):
                player.position = Suit.getWindByIndex(idx)
                if player.isViewer:
                    viewer = player
                player.hand = self
            for player in self.players:
                player.viewerPosition = viewer.position
            if viewer:
                font = pygame.font.Font(Setting.font, Setting.normalFontSize)
                for idx, player in enumerate(self.players):
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