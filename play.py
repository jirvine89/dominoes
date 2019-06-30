import sys, getopt
import algos
from player import Player, is_valid_move_str, parse_move_str
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
# * Have game tallies and restart game when over
# * Display info in corner: turn, spinner, board count
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

class BoardWidget(Widget):
    tile_widgets = []

    def reset(self):
        self.width = 0
        for tile_widget in self.tile_widgets:
           self.remove_widget(tile_widget)

    def add_tile(self, tile, x, y, direction):
        tile_widget = TileWidget()
        tile_widget.image_file = tile.get_image_file()
        x_offset, y_offset = 0, 0
        vertical = direction in ['UP', 'DOWN']
        if tile.orientation == Orientation.BIG_LEFT:
            tile_widget.angle = 270
            x_offset = tile_widget.width
        elif tile.orientation == Orientation.BIG_RIGHT:
            tile_widget.angle = 90
            x_offset = TILE_WIDTH
        elif tile.orientation == Orientation.BIG_UP:
            tile_widget.angle = 180
        elif tile.orientation == Orientation.DOUBLE and vertical:
            tile_widget.angle = 90
            if direction == 'UP':
                y_offset = -TILE_WIDTH
            else:
                y_offset = TILE_WIDTH
        tile_widget.x = x + x_offset / 2
        tile_widget.y = y + y_offset / 2
        self.add_widget(tile_widget)
        self.tile_widgets.append(tile_widget)
        return y_offset if vertical else x_offset


    def set_board(self, board):
        self.reset()
        x = self.x
        y = self.y + self.height / 2 - TILE_HEIGHT /2
        for tile in board.main_row:
            x_shift = TILE_WIDTH + self.add_tile(tile, x, y, 'RIGHT')
            if board.spinner and tile == board.spinner:
                bottom = y
                top = bottom + TILE_HEIGHT
                for up_tile in board.up:
                    top += TILE_HEIGHT + self.add_tile(up_tile, x, top, 'UP')
                for down_tile in board.down:
                    bottom -= TILE_HEIGHT - self.add_tile(down_tile, x, bottom - TILE_HEIGHT, 'DOWN')
            x += x_shift


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

    def __init__(self, hidden, bot1, bot2, play_to, **kwargs):
        super(DominoGame, self).__init__(**kwargs)
        self.hidden = hidden
        self.player1 = Player("P1")
        self.player2 = Player("P2")
        self.bot1 = getattr(algos, bot1)()
        self.bot2 = getattr(algos, bot2)()
        self.game = Game([self.player1, self.player2], play_to)
        self.game.start_first_game()
        self.update_widgets()
        self.update_widgets()
        print self.bot1
        print self.bot2

    def update_widgets(self):
        self.player1_hand.set_hand(self.player1.hand)
        self.player2_hand.set_hand(self.player2.hand, hidden=self.hidden)
        self.boneyard.set_boneyard(len(self.game.board.bone_yard))
        self.board.set_board(self.game.board)
        self.scoreboard.set_scoreboard(self.player1, self.player2)
        self.text.ids["label"].text = self.game.last_move.replace('\n', ' -- ')

    def make_move(self, move_str):
        if self.game.game_over:
            return
        if self.game.round_over:
            self.game.deal_tiles()
            self.game.round_over = False
            self.update_widgets()
            return
        player = self.game.current_player()
        if move_str == '':
            if player.name == "P1":
                bot_move = self.bot1.pick_move(self.game)
            else:
                bot_move = self.bot2.pick_move(self.game)
            self.game.make_move_or_knock(*bot_move)
            if self.game.game_over:
                self.update_widgets()
                return
            self.update_widgets()
        else:
            if move_str == 'Undo':
                self.game.undo_last_move()
                self.update_widgets()
                return
            if not is_valid_move_str(move_str):
                self.text.ids["label"].text = "%s is not a valid move string" % move_str
            else:
                tile, direction = parse_move_str(move_str)
                if tile:
                    if tile not in player.hand:
                        self.text.ids["label"].text = "%s not in %s's hand" % (str(tile), player.name)
                        return
                    if not self.game.board.valid_move(tile, direction):
                        self.text.ids["label"].text = ("%s, %s is not a valid move"
                                                       % (str(tile), str(direction)))
                        return
                self.game.make_move_or_knock(tile, direction)
                self.update_widgets()

class DominoApp(App):
    def __init__(self, hidden, bot1, bot2, **kwargs):
        super(DominoApp, self).__init__(**kwargs)
        self.hidden = hidden
        self.bot1 = bot1
        self.bot2 = bot2
        self.play_to = play_to

    def build(self):
        Config.set('graphics', 'width', '1500')
        Config.set('graphics', 'height', '1000')
        game = DominoGame(self.hidden, self.bot1, self.bot2, self.play_to)
        return game


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "h", ["bot1=","bot2=","play_to="])
    hidden = "-h" in opts
    bot1, bot2 = "RandomBot", "RandomBot"
    play_to = 150
    for opt, arg in opts:
        if opt == "--bot1":
            bot1 = arg
        if opt == "--bot2":
            bot2 = arg
        if opt == "--play_to":
            bot2 = arg
    DominoApp(hidden, bot1, bot2, play_to).run()
