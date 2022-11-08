import sys
from time import sleep
import pygame

import ship
from settings import Settings
from game_start import GameStarts
from ship import Ship
from bullet import Bullet
from alien import Alien
from  button import Button

class AlienInvasion:
    '''管理游戏资源和行为的类'''
    def __init__(self):
        '''初始化游戏并创建游戏资源'''
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption('Alien Invasion')
        self.starts = GameStarts(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.create_fleet()
        self.play_button = Button(self, "Play")
        self.game_active = True

    def run_game(self):
        '''开始游戏的主循环'''
        while True:
            self.check_events()
            if self.starts.game_active:
                self.ship.update()
                self.update_bullets()
                self.update_aliens()
            self.update_screen()

    def check_aliens_bottom(self):
        '''检测是否有外星人到最低端'''
        screen_rect =  self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self.ship_hit()
                break

    def ship_hit(self):
        '''响应飞船相撞'''
        if self.starts.ship_left > 0:
            self.starts.ship_left -= 1
            self.aliens.empty()
            self.bullets.empty()
            self.create_fleet()
            self.ship.create_ship()
            sleep(0.5)
        else:
            self.starts.game_active = False
            pygame.mouse.set_visible(True)


    def check_fleet_edges(self):
        '''有外星人到达边界时，采取相应的措施'''
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self.change_fleet_direction()
                break

    def change_fleet_direction(self):
        '''将整群外星人下移，并改变方向'''
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def update_aliens(self):
        '''更新外星人群中所以外星人的位置'''
        self.check_fleet_edges()
        self.aliens.update()
        # 检测外星人和飞船的碰撞
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self.ship_hit()
        self.check_aliens_bottom()

    def check_events(self):
        '''响应按键和鼠标的行为'''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self.check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self.check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.check_play_button(mouse_pos)

    def check_play_button(self, mouse_pos):
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.starts.game_active:
            self.starts.reset_starts()
            self.starts.game_active = True
            self.aliens.empty()
            self.bullets.empty()
            self.create_fleet()
            self.ship.create_ship()
            pygame.mouse.set_visible(False)

    def check_keydown_events(self, event):
        '''响应按键'''
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self.fire_bullet()

    def check_keyup_events(self, event):
        '''响应松开'''
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def create_fleet(self):
        '''创建外星人群'''
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # 计算屏幕可容纳多少行外星人
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                             (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
        # 创建第一行外星人
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self.create_alien(alien_number, row_number)

    def create_alien(self, alien_number, row_number):
        # 创建第一个外星人并加入当前行
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def fire_bullet(self):
        '''创建一颗子弹，并将其加入编组bullets中'''
        new_bullet = Bullet(self)
        self.bullets.add(new_bullet)
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def update_bullets(self):
        '''更新子弹的位置并删除消失的子弹'''
        # 子弹位置的更新
        self.bullets.update()

        # 删除消失的子弹
        # 删除消失的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self.check_bullet_alien_collision()

    def check_bullet_alien_collision(self):
        # for bullet in self.bullets.sprites():
        #     bullet.draw_bullet()
        # self.aliens.draw(self.screen)
        # pygame.display.flip()
        # # 检查是否有子弹击中了外星人
        # # 如果是，就删除相应的子弹和外星人
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)

        if not self.aliens:
            # 删除现有的子弹并新建机器人群
            self.bullets.empty()
            self.create_fleet()

    def update_screen(self):
        '''更新屏幕的图像，并切换到新屏幕'''
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        if not self.starts.game_active:
            self.play_button.draw_button()
        pygame.display.flip()
if __name__ == '__main__':
    # 创建游戏实例并运行
    ai = AlienInvasion()
    ai.run_game()


