class GameState:
    def __init__(self):
        self.current_room = "laboratory"

        self.inventory = []

        self.discovered_clues = []

        self.solved_puzzles = []

        self.flags = {
            "safe_opened": False,
            "generator_on": False,
            "control_room_unlocked": False,
            "exit_unlocked": False
        }

        self.game_over = False
        self.ending = None


    def add_item(self, item):
        if item not in self.inventory:
            self.inventory.append(item)


    def has_item(self, item):
        return item in self.inventory


    def add_clue(self, clue):
        if clue not in self.discovered_clues:
            self.discovered_clues.append(clue)


    def solve_puzzle(self, puzzle):
        if puzzle not in self.solved_puzzles:
            self.solved_puzzles.append(puzzle)


    def set_flag(self, flag_name, value=True):
        if flag_name in self.flags:
            self.flags[flag_name] = value


    def get_summary(self):
        return {
            "current_room": self.current_room,
            "inventory": self.inventory,
            "discovered_clues": self.discovered_clues,
            "solved_puzzles": self.solved_puzzles,
            "flags": self.flags,
            "game_over": self.game_over,
            "ending": self.ending
        }