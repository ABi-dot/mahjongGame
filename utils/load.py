import os
import sys

from setting import Setting
import pygame
from sprite import Sprite
from color import Color

class Load(object):
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.savings = []
        self.check_savings()
        self.savings_len = len(self.savings)
        self.pages_len = 0
        self.savings_group = pygame.sprite.Group()
        if self.savings_len > 0:
            self.pages_len = (self.savings_len - 1) // 10 + 1
        self.current_pages = 0
        self.current_record = 0
        self.file_name = ''

    def draw_savings(self):
        font = pygame.font.Font(Setting.font, Setting.bigFontSize)
        self.savings_group.empty()
        centerx = Setting.WinW // 2
        centery = Setting.saving_start_h
        for idx in range(self.current_pages * 10, min((self.current_pages + 1) * 10, self.savings_len)):
            if self.current_record == idx % 10:
                text = font.render(str(idx + 1) + '. ' + self.savings[idx], True, Color.RED)
            else:
                text = font.render(str(idx + 1) + '. ' + self.savings[idx], True, Color.YELLOW)
            sprite = Sprite(text)
            sprite.rect.centerx = centerx
            sprite.rect.centery = centery
            self.savings_group.add(sprite)
            centery += Setting.saving_h_span
        self.savings_group.draw(self.screen)
        pygame.display.flip()

    def draw_screen(self):
        self.draw_background()
        self.draw_savings()

    def load(self):
        while True:
            self.draw_screen()
            allowed_cmd = ['exit', 'move', 'ok']
            res = self.waiting_4_cmd(allowed_cmd)
            if res == 'exit':
                self.file_name = ''
                break
            if res == 'ok':
                if self.savings:
                    self.file_name = self.savings[self.current_pages * 10 + self.current_record]
                break
            pygame.display.flip()
        return self.file_name

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
                        self.current_pages -= 1
                        if self.current_pages < 0:
                            self.current_pages = 0
                        self.current_record = 0
                    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                        cmd = 'move'
                        self.current_pages += 1
                        if self.current_pages >= self.pages_len:
                            self.current_pages = self.pages_len - 1
                        self.current_record = 0
                    if keys[pygame.K_w] or keys[pygame.K_UP]:
                        cmd = 'move'
                        self.current_record -= 1
                        if self.current_record < 0:
                            self.current_record = 0
                    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                        cmd = 'move'
                        self.current_record += 1
                        while self.current_record >= 10 or self.current_pages * 10 + self.current_record >= self.savings_len:
                            self.current_record -= 1
                    if keys[pygame.K_KP_ENTER] or keys[pygame.K_RETURN]:
                        cmd = 'ok'

                    if keys[pygame.K_q] or keys[pygame.K_ESCAPE]:
                        cmd = 'exit'
        return cmd

    def check_savings(self):
        #abs_path = os.path.abspath(__file__)
        #print(abs_path + '/../..' + Setting.save_file_path)
        for root, dirs, files in os.walk(Setting.save_file_path):
            self.savings = files
        print(self.savings)

    def draw_background(self):
        bgImgGroup = pygame.sprite.Group()
        bgImg = pygame.image.load(Setting.bgImg)
        bgImg = pygame.transform.scale(bgImg, (Setting.WinW, Setting.WinH))
        sprite = Sprite(bgImg)
        bgImgGroup.add(sprite)
        bgImgGroup.draw(self.screen)
        pygame.display.flip()

def main():
    load = Load()

if __name__ == '__main__':
    main()