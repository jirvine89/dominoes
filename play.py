from player import RandomBot, GreedyScoringBot, GreedyScoringDefensiveBot, User, is_valid_move_str, parse_move_str
from game import Game
from dominoes_util import Orientation
from kivy.app import App
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
)
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.vector import Vector

#TODO:
# * Bend corners when ends are too long
# * Make board centered on page
# * Better move interface

TILE_WIDTH = 60
TILE_HEIGHT = 120

class TileWidget(Widget):
    image_file = StringProperty("/Users/jirvine/dominoes/tile_images/upside_down.png")
    angle = NumericProperty(0)
    width = NumericProperty(TILE_WIDTH)
    height = NumericProperty(TILE_HEIGHT)
    #orientation = Orientation.NOT_ON_BOARD

class BoardWidget(Widget):
    tile_widgets = []

    def reset(self):
        self.width = 0
        for tile_widget in self.tile_widgets:
           self.remove_widget(tile_widget)

    def set_board(self, board):
        self.reset()
        for tile in board.main_row:
            tile_widget = TileWidget()
            tile_widget.image_file = tile.get_image_file()
            rotation_width = 0
            if tile.orientation == Orientation.BIG_LEFT:
                tile_widget.angle = 270
                rotation_width = tile_widget.width
            elif tile.orientation == Orientation.BIG_RIGHT:
                tile_widget.angle = 90
                rotation_width = tile_widget.width
            tile_widget.x = self.x + self.width + rotation_width / 2
            tile_widget.y = self.y + self.height / 2 - tile_widget.height / 2
            self.add_widget(tile_widget)
            self.tile_widgets.append(tile_widget)
            self.width += tile_widget.width + rotation_width
            if board.spinner and tile == board.spinner:
                top = tile_widget.top
                bottom = tile_widget.y
                for up_tile in board.up:
                    up_tile_widget = TileWidget()
                    up_tile_widget.image_file = up_tile.get_image_file()
                    up_rotation_height = 0
                    if up_tile.orientation == Orientation.BIG_UP:
                        up_tile_widget.angle = 180
                    elif up_tile.orientation == Orientation.DOUBLE:
                        up_tile_widget.angle = 90
                        up_rotation_height = up_tile_widget.width
                    up_tile_widget.x = tile_widget.x
                    up_tile_widget.y = top - up_rotation_height / 2
                    self.add_widget(up_tile_widget)
                    self.tile_widgets.append(up_tile_widget)
                    top += up_tile_widget.height - up_rotation_height
                for down_tile in board.down:
                    down_tile_widget = TileWidget()
                    down_tile_widget.image_file = down_tile.get_image_file()
                    down_rotation_height = 0
                    if down_tile.orientation == Orientation.BIG_UP:
                        down_tile_widget.angle = 180
                    elif down_tile.orientation == Orientation.DOUBLE:
                        down_tile_widget.angle = 90
                        down_rotation_height = down_tile_widget.width
                    down_tile_widget.x = tile_widget.x
                    down_tile_widget.y = bottom - down_tile_widget.height + down_rotation_height / 2
                    self.add_widget(down_tile_widget)
                    self.tile_widgets.append(down_tile_widget)
                    bottom -= down_tile_widget.height - down_rotation_height


class ScoreboardWidget(GridLayout):
    player1_name = ObjectProperty()
    player2_name = ObjectProperty()
    player1_score = ObjectProperty()
    player2_score = ObjectProperty()

    def set_scoreboard(self, player1, player2):
        self.player1_name.text = player1.name
        self.player2_name.text = player2.name
        self.player1_score.text = str(player1.total_score)
        self.player2_score.text = str(player2.total_score)


class BoneyardWidget(GridLayout):
    tile_widgets = []

    def reset(self):
        for tile_widget in self.tile_widgets:
            self.remove_widget(tile_widget)

    def set_boneyard(self, count):
        self.reset()
        for i in range(count):
            tile_widget = TileWidget()
            self.tile_widgets.append(tile_widget)
            self.add_widget(tile_widget)

class HandWidget(BoxLayout):
    tile_widgets = []

    def reset(self):
        self.width = 0
        self.height = TILE_HEIGHT
        self.cols = 0
        for tile_widget in self.tile_widgets:
            self.remove_widget(tile_widget)

    def set_hand(self, hand, hidden=False):
        self.reset()
        self.cols = len(hand)
        for tile in sorted(list(hand)):
            tile_widget = TileWidget()
            if not hidden:
                tile_widget.image_file = tile.get_image_file()
            self.tile_widgets.append(tile_widget)
            self.add_widget(tile_widget)
            self.width += TILE_WIDTH + self.spacing

class TextWidget(Widget):
    pass

class DominoGame(Widget):
    player1_hand = ObjectProperty(None)
    player2_hand = ObjectProperty(None)
    boneyard = ObjectProperty(None)
    board = ObjectProperty(None)
    scoreboard = ObjectProperty(None)
    text = ObjectProperty(None)
    tile_width = NumericProperty(TILE_WIDTH)
    tile_height = NumericProperty(TILE_HEIGHT)

    def update_widgets(self):
        self.player1_hand.set_hand(self.player1.hand)
        self.player2_hand.set_hand(self.player2.hand) #, hidden=True)
        self.boneyard.set_boneyard(len(self.game.board.bone_yard))
        self.board.set_board(self.game.board)
        self.scoreboard.set_scoreboard(self.player1, self.player2)
        self.text.ids["label"].text = self.game.last_move.replace('\n', ' -- ')

    def __init__(self, **kwargs):
        super(DominoGame, self).__init__(**kwargs)
        self.player1 = RandomBot("player")
        self.player2 = RandomBot("bot")
        self.game = Game([self.player1, self.player2], 1000)
        self.game.start_first_game()
        self.update_widgets()
        self.update_widgets()

    def make_move(self, move_str):
        if self.game.game_over:
            return
        if True: #self.game.current_player() == self.player2:
            bot_move = self.game.current_player().pick_move(self.game.board)
            self.game.make_move_or_knock(*bot_move)
            if self.game.game_over:
                self.update_widgets()
                return
            if self.game.round_over:
                self.game.deal_tiles()
                self.game.round_over = False
            self.update_widgets()
        else:
            if not is_valid_move_str(move_str):
                self.text.ids["label"].text = "%s is not a valid move string" % move_str
            else:
                tile, direction = parse_move_str(move_str)
                if tile:
                    if tile not in self.player1.hand:
                        self.text.ids["label"].text = "%s not in hand" % (str(tile))
                        return
                    if not self.game.board.valid_move(tile, direction):
                        self.text.ids["label"].text = ("%s, %s is not a valid move"
                                                       % (str(tile), str(direction)))
                        return
                self.game.make_move_or_knock(tile, direction)
                self.update_widgets()

class DominoApp(App):
    def build(self):
        Config.set('graphics', 'width', '1500')
        Config.set('graphics', 'height', '1000')
        game = DominoGame()
        return game


if __name__ == "__main__":
    DominoApp().run()
