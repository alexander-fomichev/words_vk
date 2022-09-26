import asyncio
import random
import pytz
import typing
from asyncio import Task
from datetime import datetime, tzinfo
from typing import Optional

from sqlalchemy.exc import IntegrityError

from app.store import Store
from app.store.bot.messages import (
    player_move_message,
    game_finished_message,
    registration_ack_message,
    registration_conflict_message,
    registration_error_message,
    player_timeout_message,
    player_used_word_message,
    player_word_wrong,
    player_word_in_black_list,
    registration_success_message,
    registration_failed_message, vote_message, vote_result_message, vote_ack_message, vote_conflict_message,
    registration_message, city_doesnt_exist,
)
from app.store.vk_api.dataclasses import Player
from app.words.models import GameModel, SettingModel

if typing.TYPE_CHECKING:
    from app.store.bot.manager import BotManager


class Game:
    def __init__(
        self, manager: "BotManager", store: Store, peer_id: int, setting_title: str = "слова", game: GameModel = None
    ):
        self.manager = manager
        self.store = store
        self.setting_title = setting_title
        self.peer_id = peer_id
        self.game_db: Optional[GameModel] = game
        self.task: Optional[Task] = None

    @property
    def timeout_with_elapsed_time(self):
        """уставка таймаута с учетом остановки приложения"""
        timeout: int = self.game_db.setting.timeout - self.game_db.elapsed_time
        return timeout

    async def init(self):
        """создает запись игры в БД"""
        setting = await self.store.words.get_setting_by_title(self.setting_title)
        game_db = await self.store.words.create_game(setting.id, self.peer_id)
        self.game_db = await self.store.words.get_game_by_id(game_db.id)
        return self.game_db

    def get_player_name_by_user_id(self, user_id):
        """находит игрока в модели игры и возвращает его имя"""
        player = tuple(filter(lambda x: x.user_id == user_id, self.game_db.players))
        if player:
            return player[0].name

    def get_player_id_by_user_id(self, user_id):
        """находит игрока в модели игры и возвращает его имя"""
        player = tuple(filter(lambda x: x.user_id == user_id, self.game_db.players))
        if player:
            return player[0].id

    async def re_init(self):
        """восстановления состояния игры после перезагрузки"""
        self.setting_title = self.game_db.setting.title
        if self.game_db.status == "registration":
            # await registration_message(self.store.vk_api, self.peer_id, self.timeout_with_elapsed_time, self.setting_title)
            await self.registration()
        if self.game_db.status == "started":
            user_id = self.game_db.current_move
            name = self.get_player_name_by_user_id(user_id)
            await player_move_message(self.store.vk_api, self.peer_id, name, self.game_db.last_word, self.timeout_with_elapsed_time)
            self.task = asyncio.create_task(self._timer(self.timeout_with_elapsed_time, self.timeout_word))
        if self.game_db.status == "vote_word":
            await vote_message(self.store.vk_api, self.peer_id, self.game_db.vote_word, self.timeout_with_elapsed_time)
            self.task = asyncio.create_task(self._timer(self.timeout_with_elapsed_time, self.check_vote, self.game_db.vote_word))
        await self.store.words.patch_game(self.game_db.id, elapsed_time=0)

    async def registration(self, setting: Optional[SettingModel] = None):
        """переводит игру в состояние регистрации и запускает таймер"""
        if setting is None:
            setting_id = None
        else:
            setting_id = setting.id
        await self.store.words.patch_game(self.game_db.id, status="registration", event_timestamp=datetime.now(), setting_id=setting_id)
        self.task = asyncio.create_task(self._timer(self.timeout_with_elapsed_time, self.check_registration))
        return

    async def check_registration(self):
        """по окончании таймера регистрации проверяет количество игроков и запускает игру"""
        self.game_db = await self.store.words.get_game_by_id(self.game_db.id)
        players = [str(player.user_id) for player in self.game_db.players]
        await self.store.words.patch_game(self.game_db.id, elapsed_time=0)
        if len(players) < 2:
            self.game_db = await self.store.words.clear_game(self.game_db.id)
            await registration_failed_message(self.store.vk_api, self.peer_id)
            return
        await registration_success_message(self.store.vk_api, self.peer_id)
        await self.first_move(players)

    async def first_move(self, players: list[str]):
        # генерация очереди ходов
        random.shuffle(players)
        moves_order = " ".join(players)
        # генерация первого слова
        if self.game_db.setting.title == 'города':
            words = await self.store.words.list_cities()
        else:
            words = await self.store.words.list_words(True)
        if words:
            word = random.choice(tuple(word.title for word in words))
        else:
            await self.store.words.create_word("Орел", True)
            word = "Орел"
        await self.store.words.create_used_word(word, self.game_db.id)

        user_id = int(players[0])
        await self.store.words.patch_game(
            self.game_db.id,
            status="started",
            event_timestamp=datetime.now(),
            moves_order=moves_order,
            current_move=user_id,
            last_word=word,
        )
        name = self.get_player_name_by_user_id(user_id)
        await player_move_message(self.store.vk_api, self.peer_id, name, word, self.timeout_with_elapsed_time)
        await self.reload()
        self.task = asyncio.create_task(self._timer(self.timeout_with_elapsed_time, self.timeout_word))

    async def _timer(self, timeout: int, callback=None, *args, **kwargs):
        """асинхронный таймер с коллбаком"""
        try:
            await asyncio.sleep(timeout)
            if callback is not None:
                await callback(*args, **kwargs)
        except asyncio.CancelledError as e:
            if e != 'normal':
                print(e)
                now = datetime.now(tz=pytz.UTC)
                elapsed_time = (now - self.game_db.event_timestamp).seconds
                await self.store.words.patch_game(self.game_db.id, elapsed_time=elapsed_time)
            raise

    async def reload(self):
        """Обновляет данные игры из БД"""
        self.game_db = await self.store.words.get_game_by_id(self.game_db.id)
        return self

    async def next_player(self, result: bool, word):
        """переключает ход на следующего игрока"""
        # поиск следующего игрока
        moves_order_list = self.game_db.moves_order.split()
        prev_move_index = moves_order_list.index(str(self.game_db.current_move))
        if prev_move_index == len(moves_order_list) - 1:
            current_move = int(moves_order_list[0])
        else:
            current_move = int(moves_order_list[prev_move_index + 1])
        current_name = self.get_player_name_by_user_id(current_move)
        # обработка результата хода
        if result:
            player_id = self.get_player_id_by_user_id(self.game_db.current_move)
            await self.store.words.player_scored(player_id)
            last_word = word
        else:
            moves_order_list.remove(str(self.game_db.current_move))
            last_word = self.game_db.last_word
        moves_order = " ".join(map(str, moves_order_list))
        # проверка на последнего игрока
        if len(moves_order.split()) == 1:
            player_id = self.get_player_id_by_user_id(int(moves_order))
            await self.store.words.patch_game(
                self.game_db.id, status="finished", event_timestamp=datetime.now(), moves_order=moves_order
            )
            await self.store.words.patch_player(player_id, status='Winner')
            await self.reload()
            name = self.get_player_name_by_user_id(int(self.game_db.moves_order))
            await game_finished_message(self.store.vk_api, self.peer_id, name)
            return
        # переключение на следующего игрока
        await self.store.words.patch_game(
            self.game_db.id,
            event_timestamp=datetime.now(),
            current_move=current_move,
            last_word=last_word,
            moves_order=moves_order,
        )
        await self.reload()
        await player_move_message(self.store.vk_api, self.peer_id, current_name, last_word, self.game_db.setting.timeout)
        self.task = asyncio.create_task(self._timer(self.timeout_with_elapsed_time, self.timeout_word))

    async def add_player(self, user_id: int):
        """добавляет игрока в игру"""
        name = await self.get_player_name_from_vk(user_id)
        try:
            await self.store.words.create_player(self.game_db.id, user_id, name)
            await registration_ack_message(self.store.vk_api, self.peer_id, name)
        except IntegrityError:
            await registration_conflict_message(self.store.vk_api, self.peer_id, name)
        except Exception:
            await registration_error_message(self.store.vk_api, self.peer_id, name)

    async def get_player_name_from_vk(self, user_id: int):
        """запрашивает имя игрока из беседы вк"""
        players: list[Player] = await self.store.vk_api.get_players(self.peer_id)
        player = tuple(filter(lambda x: x.user_id == user_id, players))
        if player:
            player_name = player[0].name
        else:
            player_name = f"id_{user_id}"
        return player_name

    async def check_word(self, word: Optional[str]):
        """проверяет слово на соответствие правилам"""
        self.task.cancel(msg="normal")
        # проверяем было ли слово уже использовано
        used_words_objects = await self.store.words.list_used_words(self.game_db.id)
        used_words = [word.title for word in used_words_objects]
        if word in used_words:
            name = self.get_player_name_by_user_id(self.game_db.current_move)
            await player_used_word_message(self.store.vk_api, self.peer_id, name, word)
            await self.next_player(False, word)
            return
        await self.store.words.create_used_word(word, self.game_db.id)
        # проверка букв текущего и предыдущего слова
        if not self.check_letters(word, self.game_db.last_word):
            name = self.get_player_name_by_user_id(self.game_db.current_move)
            await player_word_wrong(
                self.store.vk_api,
                self.peer_id,
                name,
                word,
                self.game_db.last_word,
            )
            await self.next_player(False, word)
            return
        # проверка на наличие слова в словаре
        name = self.get_player_name_by_user_id(self.game_db.current_move)
        if self.game_db.setting.title == 'города':
            existed_city = await self.store.words.get_city_by_title(word.capitalize())
            if not existed_city:
                await city_doesnt_exist(self.store.vk_api, self.peer_id, name, word)
                await self.next_player(False, word)
                return
        else:
            existed_word = await self.store.words.get_word_by_title(word)
            if existed_word:
                if existed_word.is_correct is False:
                    await player_word_in_black_list(self.store.vk_api, self.peer_id, name, word)
                    await self.next_player(False, word)
                    return
            else:
                # запуск голосования
                await self.store.words.patch_game(
                    self.game_db.id, event_timestamp=datetime.now(), status="vote_word", vote_word=word
                )
                await vote_message(self.store.vk_api, self.peer_id, word, self.game_db.setting.timeout)
                self.task = asyncio.create_task(self._timer(self.timeout_with_elapsed_time, self.check_vote, word))
                return
        await self.next_player(True, word)

    @staticmethod
    def check_letters(word: str, last_word: str):
        """проверяет, что слово начинается на последнюю букву предыдущего"""
        if last_word[-1] in ("ь", "ъ", "ы"):
            letter = last_word[-2]
        else:
            letter = last_word[-1]
        return word[0] == letter

    async def timeout_word(self):
        """обрабатывает таймаут на ход игрока"""
        name = self.get_player_name_by_user_id(self.game_db.current_move)
        await player_timeout_message(self.store.vk_api, self.peer_id, name)
        await self.store.words.patch_game(self.game_db.id, elapsed_time=0)
        await self.next_player(False, None)

    async def check_vote(self, word):
        """ проверка результатов голосования"""
        await self.store.words.patch_game(self.game_db.id, elapsed_time=0)
        results = await self.store.words.list_votes(self.game_db.id, word)
        pos = len(list(filter(lambda x: x.is_correct, results)))
        neg = len(list(filter(lambda x: x.is_correct is False, results)))
        vote_result = pos >= neg
        try:
            await self.store.words.create_word(word, vote_result)
        except IntegrityError:
            pass
        await vote_result_message(self.store.vk_api, self.peer_id, word, vote_result)
        await self.store.words.patch_game(self.game_db.id, status='started', vote_word=None)
        await self.next_player(vote_result, word)

    async def add_vote(self, is_correct: bool, user_id: int):
        player_id = self.get_player_id_by_user_id(user_id)
        name = self.get_player_name_by_user_id(user_id)
        try:
            await self.store.words.create_vote(
                game_id=self.game_db.id,
                player_id=player_id,
                title=self.game_db.vote_word,
                is_correct=is_correct
            )
            await vote_ack_message(self.store.vk_api, self.peer_id, name)
        except IntegrityError:
            await vote_conflict_message(self.store.vk_api, self.peer_id, name)

