import pygame
from core.game_manager import GameManager

def main():
    """纯粹的程序入口"""
    pygame.init()
    screen = pygame.display.set_mode((658, 370), 0, 32)
    pygame.display.set_caption("愤怒的小鸟 - 状态机架构版")
    
    # 把整个游戏的控制权，全权移交给大脑 (GameManager)
    game = GameManager(screen)
    game.run()

if __name__ == '__main__':
    main()