from utils.saving import Saving
from utils.player import Player
import pygame
from setting import Setting
from utils.suit import Suit
from color import Color
from sprite import Sprite
from utils.mjSet import MjSet
import sys

class Review:
    def __init__(self, filename, screen, clock):
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
        self.mjSet: MjSet = None

        self._bgImgGroup = pygame.sprite.Group()
        self._infoGroup = pygame.sprite.Group()
        self._bonusGroup = pygame.sprite.Group()
        self._scorebonusGroup = pygame.sprite.Group()
        self._handName = pygame.sprite.Group()

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
            print(r)
            for player in self.players:
                if player.nick == nick:
                    player._concealed = r['concealed']
                    player._exposed = r['exposed']
                    player._discarded = r['discarded']
                    player._discarding = r['discarding']
                    player._desk = r['desk']
                    player._position = r['position']
                    break
        self.mjSet = record['mjSet']
        self.refresh_screen(state)


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