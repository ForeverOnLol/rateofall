from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.core import async_session_maker
from game_manager.errors import GameIsDone

from game_manager.models import Game
from roa_game.errors import GameIsNotExist

from dataclasses import dataclass
import json
import random


@dataclass
class PositionData:
    position: str
    user_name: str


@dataclass
class RoundInfo:
    positions: tuple[PositionData]
    word: str


@dataclass
class PlayerResult:
    name: tuple[PositionData]
    score: str


@dataclass
class Result:
    players: tuple[PlayerResult]
    winner_name: str


class DebateGameInstance:
    def __init__(self, words, state=None, last_poll_id=None):
        self.words = words
        self.players = []
        self.current_round = 0
        self.current_word = None
        self.current_player_index = 0
        self.scores = {}
        self.positions = {}
        self.can_switch_player = True
        self.state = state
        self.last_poll_id = last_poll_id

    async def add_player(self, player):
        if len(self.players) >= 2:
            raise ValueError("Максимальное количество игроков уже достигнуто")
        self.players.append(player)
        self.scores[player[1]] = 0
        self.positions[player[1]] = None

    async def start(self):
        if len(self.players) != 2:
            raise ValueError("Недостаточно игроков для начала игры")
        self.choose_positions()
        self.current_word = self.words[0]
        self.state = 'ready_for_next_word'

    def choose_positions(self):
        random.shuffle(self.players)
        first_player = self.players[0]
        second_player = self.players[1]
        self.positions[first_player[1]] = random.choice(["за", "против"])
        if self.positions[first_player[1]] == 'за':
            self.positions[second_player[1]] = 'против'
        else:
            self.positions[second_player[1]] = 'за'

    async def get_round_info(self) -> RoundInfo:
        positions_data = tuple(
            [PositionData(position=self.positions[player], user_name=player) for player in self.positions])
        return RoundInfo(positions=positions_data, word=self.current_word)

    async def switch_can_switch_player(self):
        self.can_switch_player = not self.can_switch_player

    async def get_can_switch_player(self):
        return self.can_switch_player

    async def switch_positions(self):
        scores_copy = self.scores.copy()  # Создаем копию словаря с баллами игроков
        for player in self.players:
            player_name = player[1]
            if self.positions[player_name] == "за":
                self.positions[player_name] = "против"
            else:
                self.positions[player_name] = "за"
        self.scores = scores_copy

    async def switch_to_next_player(self):
        if not self.can_switch_player:
            raise ValueError("Все игроки уже ответили в этом раунде")

        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.can_switch_player = self.current_player_index != 0

    async def get_players_count(self):
        return len(self.players)

    async def set_round_score(self, player_name, score):
        self.scores[player_name] += score

    async def get_round_winner(self):
        round_winner = max(self.scores, key=self.scores.get)
        return round_winner

    async def next_round(self):
        self.current_round += 1
        if self.current_round < len(self.words):
            # Меняем роли игроков местами при смене раунда
            self.positions[self.players[0][1]], self.positions[self.players[1][1]] = (
                self.positions[self.players[1][1]],
                self.positions[self.players[0][1]],
            )
            self.current_word = self.words[self.current_round]
            self.current_player_index = 0
            self.can_switch_player = True
            self.state = 'ready_for_answer'
        else:
            raise GameIsDone()

    async def get_game_winner(self):
        max_score = max(self.scores.values())
        winners = [player for player, score in self.scores.items() if score == max_score]
        if len(winners) == 1:
            return winners[0]
        else:
            return None

    async def serialize(self):
        game_data = {
            "words": self.words,
            "players": self.players,
            "current_round": self.current_round,
            "current_word": self.current_word,
            "current_player_index": self.current_player_index,
            "scores": self.scores,
            "positions": self.positions,
            "can_switch_player": self.can_switch_player,
            "state": self.state,
            "last_poll_id": self.last_poll_id
        }
        return json.dumps(game_data, default=lambda o: o.__dict__, indent=4)

    @classmethod
    async def deserialize(cls, json_data):
        decoded_data = json.loads(json_data)
        game = cls(decoded_data['words'], decoded_data['state'], decoded_data['last_poll_id'])
        game.players = decoded_data['players']
        game.current_round = decoded_data['current_round']
        game.current_word = decoded_data['current_word']
        game.current_player_index = decoded_data['current_player_index']
        game.scores = decoded_data['scores']
        game.positions = decoded_data['positions']
        game.can_switch_player = decoded_data['can_switch_player']
        return game

    async def set_poll_id(self, poll_id):
        self.last_poll_id = poll_id

    async def get_poll_id(self):
        return self.last_poll_id

    async def get_current_player(self):
        self.state = 'answering'
        current_player = self.players[self.current_player_index]
        player_name = current_player[1]
        player_position = self.positions[player_name]
        return player_name, player_position

    async def get_player_names(self):
        return [player[1] for player in self.players]

    async def get_state(self):
        if self.state is None and len(self.players) == 2:
            self.state = 'ready_for_answer'
        return self.state

    async def get_game_result(self) -> Result:
        winner = await self.get_game_winner()
        if winner is None:
            winner_text = "Дружба"
        else:
            winner_text = f"Победитель: {winner}"

        player_results = [PlayerResult(name=player, score=self.scores[player]) for player in self.scores]
        return Result(players=player_results, winner_name=winner_text)


class DebateGame(Game):
    @classmethod
    async def __create(cls, session: AsyncSession, word_list: list, chat_id: int):
        game_data = DebateGameInstance(word_list)
        game_data = await game_data.serialize()
        session.add(DebateGame(game_data=game_data, lobby_id=chat_id, game_name='debate'))

    @classmethod
    async def get(cls, chat_id: int, session: AsyncSession):
        game = (await session.execute(
            select(cls).where(DebateGame.lobby_id == chat_id)
        )).scalar_one_or_none()
        return game

    async def get_game_data(self) -> DebateGameInstance:
        return await DebateGameInstance.deserialize(self.game_data)

    async def load_game_data(self, new_game_data: DebateGameInstance):
        self.game_data = await new_game_data.serialize()

    @classmethod
    async def create(cls, chat_id, words_list: list[str], async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                await cls.__create(session=session, word_list=words_list, chat_id=chat_id)

    @classmethod
    async def start(cls, chat_id, async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                game = await cls.get(chat_id=chat_id, session=session)
                game_data = await game.get_game_data()
                await game_data.start()
                await game.load_game_data(new_game_data=game_data)

    async def __add_player(self, user_id: int, user_name: str):
        game_data = await self.get_game_data()
        await game_data.add_player((user_id, user_name))
        await self.load_game_data(new_game_data=game_data)

    @classmethod
    async def add_player(cls, chat_id: int, player: tuple[int, str], async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                game = await cls.get(chat_id=chat_id, session=session)
                if game is None:
                    raise GameIsNotExist()
                await game.__add_player(user_id=player[0], user_name=player[1])

    @classmethod
    async def get_players_count(cls, chat_id: int, async_session=async_session_maker) -> int:
        async with async_session() as session:
            async with session.begin():
                game = await cls.get(chat_id=chat_id, session=session)
                game_data = await game.get_game_data()
                return await game_data.get_players_count()

    @classmethod
    async def get_state(cls, chat_id: int, async_session=async_session_maker) -> int:
        async with async_session() as session:
            async with session.begin():
                game = await cls.get(chat_id=chat_id, session=session)
                game_data = await game.get_game_data()
                return await game_data.get_state()

    @classmethod
    async def get_round_info(cls, chat_id: int, async_session=async_session_maker) -> RoundInfo:
        async with async_session() as session:
            async with session.begin():
                game = await cls.get(chat_id=chat_id, session=session)
                game_data = await game.get_game_data()
                round_info = await game_data.get_round_info()
                return round_info

    @classmethod
    async def set_state_new_round(cls, chat_id, async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                game = await cls.get(chat_id=chat_id, session=session)
                game_data = await game.get_game_data()
                game_data.state = 'ready_for_answer'
                await game.load_game_data(new_game_data=game_data)

    @classmethod
    async def get_current_player(cls, chat_id, async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                game = await cls.get(chat_id=chat_id, session=session)
                game_data = await game.get_game_data()
                player_name, player_position = await game_data.get_current_player()
                await game.load_game_data(game_data)
                return player_name, player_position

    @classmethod
    async def switch_player(cls, chat_id, async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                game = await cls.get(chat_id=chat_id, session=session)
                game_data = await game.get_game_data()
                await game_data.switch_to_next_player()
                await game.load_game_data(game_data)

    @classmethod
    async def set_score(cls, chat_id, player_name: str, score: int, async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                game = await cls.get(chat_id=chat_id, session=session)
                game_data = await game.get_game_data()
                print(f'Оцениваю игрока {player_name} на {score}')
                await game_data.set_round_score(player_name=player_name, score=score)
                await game.load_game_data(game_data)

    @classmethod
    async def next_word(cls, chat_id, async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                game = await cls.get(chat_id=chat_id, session=session)
                game_data = await game.get_game_data()
                await game_data.next_round()
                await game.load_game_data(game_data)

    async def get_player_names(cls, chat_id, async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                game = await cls.get(chat_id=chat_id, session=session)
                game_data = await game.get_game_data()
                player_names = await game_data.get_player_names()
                return player_names

    async def set_poll_id(cls, chat_id, poll_id, async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                game = await cls.get(chat_id=chat_id, session=session)
                game_data = await game.get_game_data()
                await game_data.set_poll_id(poll_id=poll_id)
                await game.load_game_data(game_data)

    async def get_poll_id(cls, chat_id, async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                game = await cls.get(chat_id=chat_id, session=session)
                game_data = await game.get_game_data()
                return await game_data.get_poll_id()

    async def finish_round(cls, chat_id, async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                game = await cls.get(chat_id=chat_id, session=session)
                game_data = await game.get_game_data()
                game_data.state = 'ready_for_next_word'
                await game.load_game_data(new_game_data=game_data)

    async def result(cls, chat_id, async_session=async_session_maker) -> Result:
        async with async_session() as session:
            async with session.begin():
                game = await cls.get(chat_id=chat_id, session=session)
                game_data = await game.get_game_data()
                return await game_data.get_game_result()
