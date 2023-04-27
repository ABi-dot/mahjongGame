import time

import socket

from utils.hand import Hand
import pygame
from setting import Setting
from sprite import Sprite
from color import Color
from utils.error import *
from utils.suit import Suit
from utils.rule import Rule
from utils.mjSet import MjSet
from utils.mjMath import MjMath
from utils.cal import Calc
from utils.tile import Tile
from utils.saving import Saving
from RL.train import DoubleDQN
import torch
import collections
import numpy as np
import os

class HandS(Hand):
    def __init__(self, players: list = None, prevailingWind: str = '东',
                 number = 1, screen=None, clock=None, viewer=None, model=False):
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
        self._scorebonusGroup = pygame.sprite.Group()
        self._handName = pygame.sprite.Group()
        self.currentDiscard = None

        self.model = model
        if self.model:
            self.card_encoding_dict = {}
            self._init_card_encoding()
            self.action_id = self.card_encoding_dict
            self.de_action_id = {self.action_id[key]: key for key in self.action_id.keys()}
            self.agent = DoubleDQN()
            model_path = os.path.join('.', "model.bin")
            self.agent.model.load_state_dict(torch.load(model_path))

        handName = prevailingWind + str(number) + '局'
        print(handName)
        self.saving = Saving(Setting.save_file_name + '_' + handName + '.pkl')
        self.saving.save_info(players=players, prevailingWind=prevailingWind,
                              number=number, viewer=viewer)
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
                    if player.try_mahjong(self.currentDiscard) and \
                            Calc.check_if_can_hu(player.concealed, player.exposed, self.currentDiscard,
                                                 by_self=False, is_riichi=player.is_riichi,
                                                 player_position=player.position, prevailing_wind=self._prevailingWind):
                        player.concealed.append(self.currentDiscard)
                        print(f"winner is {player}, by {before}")
                        self._winner = player
                        self.firer = before
                        self.winning_tile = self.currentDiscard
                        self._stateMachine.mahjong()
                        haveWinner = True
                        self.refresh_screen(state='mahjong')
                        self.saving.add_status(self.players, self.mjSet)
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
                                self.saving.add_status(self.players, self.mjSet)
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
                            self.saving.add_status(self.players, self.mjSet)
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
                            self.saving.add_status(self.players, self.mjSet)
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
                        self.saving.add_status(self.players, self.mjSet)
                if not interrupted:
                    before.put_on_desk(self.currentDiscard)
                    self.saving.add_status(self.players, self.mjSet)
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
                self.saving.add_status(self.players, self.mjSet)

                if current.try_mahjong(tile=None) and Calc.check_if_can_hu(current.concealed, current.exposed, new_tile,
                                                 by_self=True, is_riichi=current.is_riichi, player_position=current.position, prevailing_wind=self._prevailingWind):
                    print(f"winner is {current}, by self!")
                    self._winner = current
                    self.firer = current
                    self.winning_tile = new_tile
                    self._stateMachine.mahjong()
                    self.refresh_screen(state='mahjong')
                    break
                if current.is_riichi:
                    current._is_yifa = False
                    current.discard(new_tile)
                    print(current, 'discard tile:', new_tile)
                    self.currentDiscard = new_tile
                if self.winner:
                    break
                if not current.is_riichi and current.try_riichi():
                    current._is_yifa = True
                    self.refresh_screen()
                # self kong
                try:
                    if not current.is_riichi and current.try_conceal_kong(self.mjSet) and self.mjSet.bonus_count < 5:
                        self.mjSet.bonus_count += 1
                        self.saving.add_status(self.players, self.mjSet)
                except OutOfTilesError as e:
                    self.withdraw()
                except HaveWinnerError as e:
                    self._winner = current
                    self.mahjong_on_kong = True
                    self.firer = current
                    self._stateMachine.mahjong()
                    haveWinner = True
                    self.refresh_screen(state='mahjong')
                    self.saving.add_status(self.players, self.mjSet)
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
                            self.saving.add_status(self.players, self.mjSet)
                except OutOfTilesError as e:
                    self.withdraw()
                except HaveWinnerError as e:
                    self._winner = current
                    self.mahjong_on_kong = True
                    self.firer = current
                    self._stateMachine.mahjong()
                    haveWinner = True
                    self.refresh_screen(state='mahjong')
                    self.saving.add_status(self.players, self.mjSet)

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
                            self.winning_tile = new_tile
                            self._stateMachine.mahjong()
                            self.refresh_screen(state='mahjong')
                            self.robbing_a_kong = True
                            self.saving.add_status(self.players, self.mjSet)
                            break
                    if self._winner:
                        break
                if self._winner:
                    break
            if not current.is_riichi:
                if self.model:
                    for player in self.players:
                        if player.nick == 'lyf':
                            if len(player.concealed) % 3 == 2:
                                state = self.generate_status(player.concealed)
                                #qvals = self.agent.get_qvals(torch.from_numpy(state).float())
                                qvals = self.agent.get_qvals(self.transfer(state))
                                for i in range(34):
                                    tile = Rule.convert_key_to_tile(self.get_de_action_id(i))
                                    exist = False
                                    for t in player.concealed:
                                        if tile.key == t.key:
                                            exist = True
                                            break
                                    if not exist:
                                        qvals[0][i] = float("-inf")
                                print(qvals)
                                action = qvals.argmax()
                                action = action.item()
                                print(Rule.convert_key_to_tile(self.get_de_action_id(action)))
                tile = current.decide_discard()
                current.discard(tile)
                self.currentDiscard = tile
                print(current, 'discard tile:', tile)
                self.saving.add_status(self.players, self.mjSet)


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
        self.saving.save_status()
        self.saving.save()

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

    def score(self):
        self.refresh_screen(state='scoring')
        result = ''
        if not self.winner:
            result = 'draw'
        elif self.winner == self._player:
            result = 'win'
        else:
            result = 'lose'

        text = ''
        player_position = self._player.position
        if self._winner:
            if self._winner.position == player_position:
                text = 'self_win'
            elif self._winner.position == Suit.getNextWind(player_position):
                text = 'next_win'
            elif self._winner.position == Suit.getBeforeWind(player_position):
                text = 'before_win'
            else:
                text = 'opposite_win'
        else:
            text = 'draw'

        #show end screen
        self.draw_end_screen(result=result, text=text)
        #show scoreboard
        scores = []
        if not self.winner:
            self.screen.fill(Color.WHITE)
            self.draw_players(self.players, winner=None, score=0)
            self.waiting_return()
            return
        winner = self._winner
        by_self = False
        if self._winner == self.firer:
            by_self = True

        calculator = Calc(mjSet=self.mjSet, concealed=self.winner.concealed, exposed=self.winner.exposed, winning_tile=self.winning_tile,
                          winner_position=self.winner.position, prevailing_wind=self._prevailingWind, by_self=by_self, robbing_a_kong=self.robbing_a_kong,
                          mahjong_on_kong=self.mahjong_on_kong, is_riichi=self.winner.is_riichi, is_yifa = self.winner._is_yifa)
        result = calculator.calc()
        #need fixed!
        score = result.cost['main']
        self.screen.fill(Color.WHITE)

        self.draw_players(players=self.players, winner=self.winner, score=score, by_self=by_self, firer=self.firer)
        self.draw_bonus_screen(self.winner.is_riichi)
        self.draw_score_screen(concealed=winner.concealed, exposed=winner.exposed, result=result)
        self.waiting_return()

    def draw_bonus_screen(self, is_riichi):
        self._scorebonusGroup.empty()
        text = self._font.render('宝牌指示牌', True, Color.BLACK)
        sprite = Sprite(text)
        sprite.rect.left = Setting.score_bonus_text_left
        sprite.rect.bottom = Setting.score_bonus_text_bottom
        self._scorebonusGroup.add(sprite)
        left = Setting.score_bonus_text_left
        top = Setting.score_bonus_text_bottom + Setting.bonus_text_img_span
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
            self._scorebonusGroup.add(sprite)
            left += sprite.rect.w
        text = self._font.render('里宝牌指示牌', True, Color.BLACK)
        sprite = Sprite(text)
        sprite.rect.left = Setting.score_bonus_text_left
        sprite.rect.bottom = Setting.score_libonus_text_bottom
        self._scorebonusGroup.add(sprite)
        left = Setting.score_bonus_text_left
        top = Setting.score_libonus_text_bottom + Setting.bonus_text_img_span
        for i in range(5):
            if is_riichi and i + 1 <= self.mjSet.bonus_count:
                tile = self.mjSet.li_bonus[i]
                path = Setting.tileImgPath + tile.img
            else:
                path = Setting.tileImgPath + Setting.facedownImg
            image = pygame.image.load(path)
            sprite = Sprite(image)
            sprite.rect.left = left
            sprite.rect.top = top
            self._scorebonusGroup.add(sprite)
            left += sprite.rect.w

        self._scorebonusGroup.draw(self.screen)

    def draw_score_screen(self, concealed, exposed, result):
        score_group = pygame.sprite.Group()

        if concealed:
            left = Setting.score_board_concealed_left
            bottom = Setting.score_board_concealed_bottom
            for index, tile in enumerate(concealed):
                image = pygame.image.load(Setting.tileImgPath + tile.img)
                sprite = Sprite(image)
                sprite.rect.left = left
                sprite.rect.bottom = bottom
                left += sprite.rect.w
                if index == len(concealed) - 2:
                    left += sprite.rect.w
                score_group.add(sprite)

        if exposed:
            left = Setting.score_board_exposed_left
            bottom = Setting.score_board_exposed_bottom
            for expose in exposed:
                for index, tile in enumerate(expose.all):
                    image = pygame.image.load(Setting.tileImgPath + tile.img)
                    sprite = Sprite(image)
                    sprite.rect.left = left
                    sprite.rect.bottom = bottom
                    left += sprite.rect.w
                    score_group.add(sprite)
                left += sprite.rect.w

        left = Setting.score_bonus_text_left
        bottom = Setting.score_fushu_bottom
        font = pygame.font.Font(Setting.font, Setting.bigFontSize)
        image = font.render(str(result.han) + '番' + str(result.fu) + '符', True, Color.BLACK)
        sprite = Sprite(image)
        sprite.rect.left, sprite.rect.bottom = left, bottom
        score_group.add(sprite)

        font = pygame.font.Font(Setting.font, Setting.hugeFontSize)
        bottom += 100
        image = font.render(str(result.cost['main']) + '点', True, Color.RED)
        sprite = Sprite(image)
        sprite.rect.left, sprite.rect.bottom = left, bottom
        score_group.add(sprite)

        #points
        font = pygame.font.Font(Setting.font, Setting.bigFontSize)
        if result.yaku:
            left = Setting.score_board_left
            bottom = Setting.score_board_bottom
            for index, fan in enumerate(result.yaku):
                image = font.render(str(fan), True, Color.BLACK)
                sprite = Sprite(image)
                sprite.rect.left = left
                sprite.rect.bottom = bottom
                score_group.add(sprite)
                if index % 2 == 1:
                    left = Setting.score_board_left
                    bottom += Setting.score_board_score_y_span
                else:
                    left = Setting.score_board_left + Setting.score_board_score_width + Setting.score_board_score_x_span
        score_group.draw(self.screen)
        pygame.display.flip()

    def draw_end_screen(self, result = 'win', text = ''):
        score_group = pygame.sprite.Group()
        if result not in ['win', 'lose', 'draw']:
            raise ValueError(f"result:{result} not in ['win', 'lose', 'draw']")

        #hand result
        file = Setting.sprite_base + text + '.png'
        image = pygame.image.load(file)
        end_btn = Sprite(image)
        end_btn.rect.centerx = Setting.WinW // 2
        end_btn.rect.bottom = Setting.WinH - 100
        score_group.add(end_btn)

        #end_btn
        btn_img = Setting.sprite_base + Setting.btn_img['end']
        image = pygame.image.load(btn_img)
        btn = Sprite(image)
        btn.rect.centerx = Setting.WinW // 2
        btn.rect.centery = Setting.WinH // 2
        score_group.add(btn)
        score_group.draw(self.screen)
        pygame.display.flip()
        self.waiting_return()

    def waiting_return(self):
        allowed_cmd = ['discard']
        if not self._player:
            return
        self._player.waiting_4_cmd(allowed_cmd=allowed_cmd, draw_screen=False)

    def fix_score(self, score):
        score = int(score)
        if score % 100:
            t = score // 100
            return (t + 1) * 100
        return score


    def draw_players(self, players, winner, score, by_self=False, firer=None):
        if not players:
            raise ValueError("need players")

        players_group = pygame.sprite.Group()
        font = pygame.font.Font(Setting.font, Setting.normalFontSize)
        left = Setting.score_board_left
        bottom = Setting.WinH - 100
        if not winner:
            winner = None
            bottom = Setting.WinH // 2
        if not score:
            score = 0

        for player in players:
            text = player.nick + ': ' + str(player.score)
            if player == winner:
                image = font.render(text, True, Color.RED)
            else:
                image = font.render(text, True, Color.BLACK)
            sprite = Sprite(image)
            sprite.rect.left = left
            sprite.rect.bottom = bottom
            players_group.add(sprite)
            left += sprite.rect.w + 10

            #need fixed!
            if player == winner:
                text = "+ " + str(score)
                player.score += score
                image = font.render(text, True, Color.GREEN)
            else:
                if by_self:
                    if winner.position == '东':
                        fix_score = self.fix_score(score / 3)
                        text = "- " + str(fix_score)
                        player.score -= fix_score
                    else:
                        if player.position == '东':
                            fix_score = self.fix_score(score / 2)
                            text = "- " + str(fix_score)
                            player.score -= fix_score
                        else:
                            fix_score = self.fix_score(score / 4)
                            text = "- " + str(fix_score)
                            player.score -= fix_score
                elif player == firer:
                    text = "- " + str(score)
                    player.score -= score
                else:
                    text = ""
                image = font.render(text, True, Color.RED)
            sprite = Sprite(image)
            sprite.rect.left = left
            sprite.rect.bottom = bottom
            players_group.add(sprite)
            left += Setting.score_board_player_x_span

            players_group.draw(self.screen)
            pygame.display.flip()

    def get_de_action_id(self, action):
        return self.de_action_id[action]

    def generate_status(self, c):
        arr = self.convert_arr_to_index(Rule.convert_tiles_to_arr(c))
        c = collections.Counter(arr)
        state = np.zeros((34, 4), dtype=float)
        for k, v in c.items():
            state[k][:v] = 1
        flat = np.ndarray.flatten(state)
        return flat

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

    def transfer(self, state):
        return torch.reshape(torch.from_numpy(state).float(), (1, 34, 4))
