from core.typing_helpers import Result
from core.game import GameEngine, Player
from core.model import ModelConfig
from core.participant import Participant
import json
import chess.pgn
import chess
from itertools import combinations
import os


class Tournament(object):

    def __init__(self, player_models_list: list = [], player_models_path: str = "../models"):
        if len(player_models_list) > 0:
            self.player_models_list = player_models_list
        else:
            self.player_models_list = os.listdir(player_models_path)

        self.players = [(idx, name)
                        for (idx, name) in enumerate(self.player_models_list)]
        self.matches = [(idx, players) for (idx, players) in list(
            combinations(enumerate(self.player_models_list), 2))]
        self.no_of_cycles = 1
        self.games = []  # Store all the games

        # Participant objects only (we are not loading the DL model here)
        self.participants = [Participant(
            name=player[1], idx=player[0]) for player in self.players]

    def initialize_players(self, model_paths: list, base_model_directory: str = "../models"):

        # Throw error if we don't get two model paths
        assert len(model_paths) == 2

        with open("../assets/moves.json") as f:
            vocab_size = len(json.load(f))
            config = ModelConfig(vocab_size=vocab_size, n_positions=60,
                                 n_ctx=60, n_embd=128, n_layer=30, n_head=8)

        player1 = Player(config, os.path.join(base_model_directory, model_paths[0]),
                         "../assets/moves.json")  # assume to be white
        player2 = Player(config, os.path.join(base_model_directory, model_paths[1]),
                         "../assets/moves.json")  # assume to be black

        return player1, player2

    def expected(self, participant1: Participant, participant2: Participant):
        return 1 / (1 + 10 ** ((participant2.current_elo_rating - participant1.current_elo_rating) / 400))

    def calculate_elo_change(self, participant1: Participant, participant2: Participant, score, k=32):
        expected = self.expected(participant1, participant2)
        return k * (score - expected)

    def play_match(self, participant1: Participant, participant2: Participant):

        # Result.{WIN,DRAW,LOSE} is from participant1 perspective

        game = GameEngine()
        pgn_writer = chess.pgn.Game()
        pgn_writer_node = pgn_writer
        pgn_writer.headers["Event"] = "Round Robin Tournament"
        pgn_writer.headers["White"] = participant1.name
        pgn_writer.headers["Black"] = participant2.name

        player1, player2 = self.initialize_players(
            model_paths=[participant1.name, participant2.name])

        # play
        done = False
        p = 0
        res = Result.PLAYING
        while not done:
            # model returns move object, value, confidence of move
            if p == 0:
                m, v, c = player1.move(game)
                p += 1
            else:
                m, v, c = player2.move(game)
                p = 0
            done, res = game.step(m)
            pgn_writer_node = pgn_writer_node.add_variation(m)

            if res != Result.PLAYING:
                print("Game over")
                break

        pgn_writer.headers["Result"] = f"{int(res)}-{1-int(res)}"

        # Store all games: pgn string
        self.games.append(pgn_writer)

        # Update ratings
        elo_change = self.calculate_elo_change(participant1, participant2, res)

        if elo_change != 0.0:
            self.participants[participant1.idx].current_elo_rating += elo_change
            self.participants[participant2.idx].current_elo_rating -= elo_change

        return res

    def start_tournament(self):
        for match in self.matches:
            participant1 = self.participants[match[0][0]]
            participant2 = self.participants[match[1][0]]

            self.play_match(participant1, participant2)

    def save_pgn_file(self):
        for game in self.games:
            print(game, file=open("tournament_games.pgn", "a"), end="\n\n")
