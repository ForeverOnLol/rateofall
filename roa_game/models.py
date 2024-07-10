import json
from dataclasses import dataclass

from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from game_manager.models import Game
from db.core import async_session_maker
from lobby.models import Lobby, HiddenWord, WordProvider
from roa_game.errors import GameIsNotExist
from game_manager.errors import GameIsDone


@dataclass
class RoundData:
    users: [tuple[str, int]]
    total_score: int
    word: str


class RoaInstance:
    def __init__(self, words, participants):
        self.words = words
        self.participants = {user_id: name for user_id, name in participants}
        self.num_rounds = len(words)
        self.current_round = 1
        self.current_scores = {word: {user_id: 0 for user_id in self.participants} for word in self.words}
        self.word_total_scores = {word: 0 for word in self.words}

    async def _initialize_rounds(self):
        return [{word: {user_id: 0 for user_id in self.participants} for word in self.words}
                for _ in range(self.num_rounds)]

    async def _update_word_total_score(self, word):
        total_score = sum(score for score in self.current_scores[word].values())
        self.word_total_scores[word] = total_score

    async def get_player_ids(self):
        return list(self.participants.keys())

    async def set_score_for_word(self, user_id, score):
        if self.current_round <= self.num_rounds:
            word = self.words[self.current_round - 1]
            if user_id in self.participants and -10 <= score <= 10:
                self.current_scores[word][user_id] = score
                await self._update_word_total_score(word)

    async def get_total_scores_all(self):
        scores_dataclass = [
            RoundData(None, score, word)
            for word, score in self.word_total_scores.items()
        ]
        return scores_dataclass

    async def get_scores_for_current_word(self) -> RoundData:
        current_word: str = self.words[self.current_round - 1]
        users_scores = [
            (self.participants[user_id], self.current_scores[current_word][user_id])
            for user_id in self.participants
        ]
        total_score: int = self.word_total_scores[current_word]

        named_users_scores: list[tuple[str, int]] = [(name, score) for name, score in users_scores]

        return RoundData(
            users=named_users_scores,
            total_score=total_score,
            word=current_word
        )

    async def get_current_word(self):
        if self.current_round <= self.num_rounds:
            return self.words[self.current_round - 1]
        else:
            return None

    async def next_round(self):
        if self.current_round >= self.num_rounds:
            raise GameIsDone()
        else:
            self.current_round += 1

    async def serialize(self):
        return json.dumps({
            "words": self.words,
            "participants": list(self.participants.items()),  # Преобразуем в список кортежей
            "num_rounds": self.num_rounds,
            "current_round": self.current_round,
            "current_scores": self.current_scores,
            "word_total_scores": self.word_total_scores
        })

    @staticmethod
    async def deserialize(json_data):
        data = json.loads(json_data)
        game = RoaInstance(data["words"], data["participants"])  # Используем как словарь
        game.num_rounds = data["num_rounds"]
        game.current_round = data["current_round"]
        game.current_scores = {
            word: {int(user_id): score for user_id, score in scores.items()}
            for word, scores in data["current_scores"].items()
        }
        game.word_total_scores = data["word_total_scores"]
        return game


class RoaGame(Game):

    @classmethod
    async def create(cls, chat_id: int, session: AsyncSession, users, words):
        game_data = RoaInstance(words=words, participants=users)
        game_data = await game_data.serialize()
        session.add(RoaGame(lobby_id=chat_id, game_data=game_data, game_name='roa'))

    @classmethod
    async def get(cls, chat_id: int, session: AsyncSession):
        game = (await session.execute(
            select(cls).where(RoaGame.lobby_id == chat_id)
        )).scalar_one_or_none()
        return game

    async def __next_word_in_data(self):
        game_data = await self.get_game_data()
        await game_data.next_round()
        await self.load_game_data(new_game_data=game_data)

    async def get_game_data(self) -> RoaInstance:
        return await RoaInstance.deserialize(self.game_data)

    async def __get_scores_for_current_word(self) -> RoundData:
        game_data = await self.get_game_data()
        return await game_data.get_scores_for_current_word()

    async def __set_score(self, user_id, score: int) -> None:
        game_data = await self.get_game_data()
        await game_data.set_score_for_word(user_id=user_id, score=score)
        await self.load_game_data(new_game_data=game_data)

    async def load_game_data(self, new_game_data: RoaInstance):
        self.game_data = await new_game_data.serialize()

    @classmethod
    async def start(cls, chat_id, words_list: list[str], async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                if await Lobby.is_ready_for_game(session=session, chat_id=chat_id):
                    lobby = await Lobby.get(session=session, chat_id=chat_id)
                    users = await lobby.get_members_id_name_tuple()
                    await cls.create(session=session, chat_id=chat_id, users=users, words=words_list)
                    await lobby.game_running_state()
                else:
                    print('Лобби не соотвествует тому, что надо для запуска ROA')

    @classmethod
    async def get_current_word(cls, chat_id: int, async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                game = await RoaGame.get(chat_id=chat_id, session=session)
                game_data = await game.get_game_data()
                return await game_data.get_current_word()

    @classmethod
    async def next_word(cls, chat_id: int, async_session=async_session_maker):
        '''
        Переключает на следующее слово.
        :param chat_id:
        :param async_session:
        :return:
        '''
        async with async_session() as session:
            async with session.begin():
                game = await RoaGame.get(chat_id=chat_id, session=session)
                await game.__next_word_in_data()

    @classmethod
    async def get_round_score(cls, chat_id: int, async_session=async_session_maker) -> RoundData | None:
        '''
        Получить данные по раунду.
        :param chat_id:
        :param async_session:
        :return:
        '''
        async with async_session() as session:
            async with session.begin():
                game = await RoaGame.get(chat_id=chat_id, session=session)
                if not game:
                    raise GameIsNotExist()
                prev_word_data = await game.__get_scores_for_current_word()
                return prev_word_data

    @classmethod
    async def set_score(cls, user_id, chat_id: int, score: int, async_session=async_session_maker):
        '''
        Публичный метод чтобы поставить оценку текущему слову в раунде
        :param user_id:
        :param chat_id:
        :param score:
        :param async_session:
        :return:
        '''
        async with async_session() as session:
            async with session.begin():
                game = await RoaGame.get(chat_id=chat_id, session=session)
                if game is None:
                    raise GameIsNotExist()
                await game.__set_score(user_id=user_id, score=score)
                print('------------')
                print((await RoaGame.get(chat_id=chat_id, session=session)).game_data)
                return score

    @classmethod
    async def result(cls, chat_id: int, async_session=async_session_maker) -> list[RoundData]:
        '''
        Публичный метод чтобы поставить оценку текущему слову в раунде
        :param user_id:
        :param chat_id:
        :param score:
        :param async_session:
        :return:
        '''
        async with async_session() as session:
            async with session.begin():
                game = await RoaGame.get(chat_id=chat_id, session=session)
                game_data = await game.get_game_data()
                return await game_data.get_total_scores_all()


# async def main():
#     print(await RoaGame.get_current_word(chat_id=-4088510024))
#     print(await RoaGame.set_score(user_id=936885205, chat_id=-4088510024, score=4))
#     print(await RoaGame.set_score(user_id=936885205, chat_id=-4088510024, score=5))
#     print(await RoaGame.get_round_score(chat_id=-4088510024))
