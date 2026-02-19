# game.py
from Grid import Grid
from Fleet import Fleet
from Ship import Ship
from typing import Set,List,Tuple
class BattleshipGame:
    """
        VISHNU  - CB.SC.U4CSE24060
    """
    def __init__(self):
        SHIP_SIZES=[5,4,3,3,2]#hard coding ship sizes and grid size for now
        GRID_SIZE=12
        self.player_place_board = Grid(GRID_SIZE,SHIP_SIZES,Grid.Role.AI)#player places ships here,ai hits it
        self.ai_place_board =Grid(GRID_SIZE,SHIP_SIZES,Grid.Role.PLAYER)

        # tracking boards (what each side hits on)
        self.player_attack_board = self.ai_place_board#player hits on board which AI placed on
        self.ai_attack_board = self.player_place_board#AI hits on board which player placed on

        # place ships
        # player ships will be placed via UI; only AI auto‑place here
        self.ai_place_board.placeAllShips()
        self.current_turn = "PLAYER"
    
    # called by UI during placement
    def player_can_place(self, r:int, c:int, length:int, orient:chr):
        return self.player_place_board.can_place_ship(r, c, length, orient)

    def player_place(self, r:int, c:int, length:int, orient:chr):
        self.player_place_board.player_place_ship(r, c, length, orient)

    def all_player_ships_placed(self):
        # naive check: count S cells
        total = len(self.player_place_board.fleet.nodes)#nodes is dictionary which maps every coordinate to a ship
        return total == sum(self.SHIP_SIZES)