# V1 draws the game board and allows the player 'X'
# to select tiles using a regular cursor.
# There is no player O. A tile flashes when an
# occupied tile is selected, but there is no win or draw
# indication at the end. The game runs until the player
# closes the window.

from uagame import Window
import pygame, time, random
from pygame.locals import *


# User-defined functions

def main():
    window = Window('Tic Tac Toe', 500, 400)
    window.set_auto_update(False)
    game = Game(window)
    game.play()
    window.close()


# User-defined classes
class Tile:
    window = None
    fg_color = pygame.Color("white")
    font_size = 100
    border_width = 3

    # ALL class methods need @classmethod on the line
    # before they are defined.
    @classmethod
    def set_window(cls, window):
        # All class methods use cls instead of self.
        # cls is the CLASS which is calling the method.
        # in our case, this will always be Tile.
        cls.window = window
    @classmethod
    def set_border_width(cls, border_width):
        cls.border_width = border_width

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.flashing = False
        self.content = ""

    # this over rides the ==
    # If I say Tile_A == Tile_B
    # then self is Tile_A and other_tile is Tile_B
    def __eq__(self, other_tile):
        if self.content != '' and self.content == other_tile.content:
            return True
        return False


    def draw(self):
        if not self.flashing:
            pygame.draw.rect(Tile.window.get_surface(), Tile.fg_color, self.rect, Tile.border_width)
            self.window.set_font_size(Tile.font_size)
            x = self.rect.x + self.rect.width / 2 - self.window.get_string_width(self.content) / 2
            y = self.rect.y + self.rect.height / 2 - self.window.get_font_height() / 2
            self.window.draw_string(self.content, x, y)
        else:
            pygame.draw.rect(Tile.window.get_surface(), Tile.fg_color, self.rect, 0)
            self.flashing = False


    def select(self, pos, content):
        if self.rect.collidepoint(pos):
            if self.content == "":
                self.content = content
                return True
            else:
                self.flashing = True
        return False



    def flash(self):
        self.flashing = True


class Cursor:
    def __init__(self, filename):
        '''
        #if we didn't want to do file io, we could
        #explicitly create an ascii representation of
        #our cursor. Each Element of our list is a "row"
        #in our picture.
        list_data = ["X      X",
                    " X    X ",
                    "  X  X  ",
                    "   XX   ",
                    "   XX   ",
                    "  X  X  ",
                    " X    X ",
                    "X      X"]
        '''
        data = self.read_cursor_data(filename)
        list_data = data.splitlines()
        self.size = (len(list_data[0]), len(list_data))
        self.hitspot = (self.size[0] // 2, self.size[1] // 2)
        self.xormask, self.andmask = pygame.cursors.compile(list_data, "?", "*", "@")

    def read_cursor_data(self, filename):
        my_file = open(filename)
        data = my_file.read()
        my_file.close()
        return data

    def activate(self):
        pygame.mouse.set_cursor(self.size, self.hitspot, self.xormask, self.andmask)


class Game:
    # An object in this class represents a complete game.

    def __init__(self, window):
        # Initialize a Game.
        # - self is the Game to initialize
        # - window is the uagame window object

        self.window = window
        self.pause_time = 0.0000000001  # smaller is faster game
        self.close_clicked = False
        self.continue_game = True
        self.bg_color = pygame.Color('black')
        # Here, we're calling the class method set_window
        # notice we need to use the class  (Tile) to call the method
        # We need to do this before we create any tiles that need
        # to use window.
        Tile.set_window(self.window)
        self.board_size = (3, 3)  # number of rows, number of columns
        self.create_board()
        self.player_1 = "X"
        self.player_2 = "O"
        self.turn = self.player_1
        # how many tiles have an X or an O on them
        self.num_clicked = 0
        self.flashers = []
        self.flasher_index = 0

        self.x_cursor = Cursor("cursorx.txt")
        self.o_cursor = Cursor("cursoro.txt")
        self.x_cursor.activate()

    def create_board(self):
        # Creates the board. Our board is nested lists
        # where each list is a row of tiles.
        self.board = []
        for row_num in range(self.board_size[0]):
            new_row = self.create_row(row_num)
            # remember that append MODIFIES self.board to
            # add the new_row to the end of the list we use
            # to represent our board
            self.board.append(new_row)

    def create_row(self, row_num):
        row = []
        width = self.window.get_width() / self.board_size[1]
        height = self.window.get_height() / self.board_size[0]
        for col_num in range(self.board_size[1]):
            x = col_num * width
            y = row_num * height
            new_tile = Tile(x, y, width, height)
            row.append(new_tile)
        return row

    def play(self):
        # Play the game until the player presses the close box.
        # - self is the Game that should be continued or not.

        while not self.close_clicked:  # until player clicks close box
            # play frame
            self.handle_event()
            self.draw()
            if self.continue_game:
                self.update()
                self.decide_continue()
            time.sleep(self.pause_time)  # set game velocity by pausing

    def handle_event(self):
        # Handle each user event by changing the game state
        # appropriately.
        # - self is the Game whose events will be handled

        event = pygame.event.poll()
        if event.type == QUIT:
            self.close_clicked = True
        elif event.type == MOUSEBUTTONDOWN and self.continue_game:
            # for each tile, check if it's been clicked.
            # uncomment the following line if you want to see
            # the set_border_width method in action
            # Tile.set_border_width(7)

            for row in self.board:
                for tile in row:
                    if tile.select(event.pos, self.turn):
                        self.change_turn()
                        # increase number of tiles that have been flipped
                        self.num_clicked = self.num_clicked + 1

    def change_turn(self):
        if self.turn == self.player_1:
            self.turn = self.player_2
            self.o_cursor.activate()
        else:
            self.turn = self.player_1
            self.x_cursor.activate()

    def draw(self):
        # Draw all game objects.
        # - self is the Game to draw
        self.window.clear()
        # Draw anything you need to draw in between
        # these two lines
        # ---------------------#
        if self.flashers:
            # if you want the tiles to flash randomly, use the
            # code below:
            # random_index = random.randint(0,len(self.flashers)-1)
            # self.flashers[random_index].flash()
            self.flashers[self.flasher_index].flash()
            self.flasher_index = (self.flasher_index + 1) % len(self.flashers)

        self.draw_board()
        # ---------------------#
        self.window.update()

    def draw_board(self):
        # tell all the tiles in the board to draw themselves
        for row in self.board:
            for tile in row:
                tile.draw()

    def update(self):
        # Update the game objects.
        # - self is the Game to update

        pass

    def decide_continue(self):
        # Check and remember if the game should continue
        # - self is the Game to check
        # your code will look something like this, where you choose
        # what boolean logic to put into your if statement
        # to determine if the game is over (ie. the player
        # has won, or lost, or run out of time, etc.)

        if self.is_win() or self.is_tie():
            self.continue_game = False
            print("YAY! THE GAME IS OVER! TADAH!")

    def is_win(self):
        # return true if there is ANY line on the board
        if self.is_row_win() or self.is_column_win() or self.is_diagonal_win():
            return True
        return False

    def is_list_win(self, elements):
        ''' Takes in a list of tiles and returns TRUE if all the tiles are the same
        otherwise it returns false
        '''
        # could also do the following:
        # for index in range(1,len(elements)):
        #    if elements[index-1] != elements[index]:
        #        return False
        # return True
        current_element = elements[0]
        for index in range(1, len(elements)):
            if current_element != elements[index]:
                return False
            current_element = elements[index]
        return True

    def is_row_win(self):
        # returns true if there is a row of all Xs or a row of all Os
        for row in self.board:
            if self.is_list_win(row):
                self.flashers = row
                return True
        return False

    def is_column_win(self):
        # return true if there is a column of all Xs or a column of all Os
        for y_coord in range(self.board_size[1]):
            column = []
            for x_coord in range(self.board_size[0]):
                column.append(self.board[x_coord][y_coord])
            if self.is_list_win(column):
                self.flashers = column
                return True
        return False

    def is_diagonal_win(self):
        # return true if there is a diagonal line with all Xs or all Os
        diagonal1 = []
        diagonal2 = []
        for i in range(min(self.board_size)):
            diagonal1.append(self.board[i][i])
            diagonal2.append(self.board[i][self.board_size[1] - 1 - i])

        if self.is_list_win(diagonal1):
            self.flashers = diagonal1
            return True
        if self.is_list_win(diagonal2):
            self.flashers = diagonal2
            return True
        return False

    def is_tie(self):
        '''
        returns True if all the tiles are filled else returns False
        '''
        # COUNTING METHOD --- manually check all the tiles and count
        # how many are full
        # tile_count = 0
        # for row in self.board:
        # for tile in row:
        # if tile.content != "":
        # tile_count = tile_count + 1

        # return tile_count == 9

        # BREKAOUT METHOD --- manually check all the tiles and
        # stop and return False if ANY tile is empty. If we never break
        # out, we can safely return True because we've checked all the tiles
        # and non were empty.

        # for row in self.board:
        # for tile in row:
        # if tile.content == "":
        # return False

        # return True

        # here we assume that we've been keeping track of
        # the number of tiles that have been clicked & filled
        if self.num_clicked == self.board_size[0] * self.board_size[1]:
            # set flasher to be ALL THE TILES!
            new_list = []
            for row in self.board:
                for tile in row:
                    new_list.append(tile)

            self.flashers = new_list
            return True
        return False


main()
