class GameStarts:
    '''跟踪游戏的统计信息'''

    def __init__(self, ai_game):
        '''初始化游戏信息'''
        self.settings = ai_game.settings
        self.reset_starts()
        self.game_active = False
    def reset_starts(self):
        self.ship_left = self.settings.ship_limit


