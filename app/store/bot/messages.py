import typing

from app.store.vk_api.dataclasses import Message

if typing.TYPE_CHECKING:
    from app.store.vk_api.accessor import VkApiAccessor


async def start_message(api: "VkApiAccessor", peer_id: int,):
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=f"Для начала игры напишите слова или города",
        )
    )


async def registration_message(api: "VkApiAccessor", peer_id: int, timeout: int, setting: str):
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=f'Регистрация игроков в игру {setting}. Если хотите участвовать, напишите "я". Время на регистрацию {timeout} секунд',
        )
    )


async def registration_ack_message(api: "VkApiAccessor", peer_id: int, name: str):
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=f"Игрок {name} зарегистрирован",
        )
    )


async def registration_conflict_message(api: "VkApiAccessor", peer_id: int, name: str):
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=f"Игрок {name}. Вы уже зарегистрированы",
        )
    )


async def registration_error_message(api: "VkApiAccessor", peer_id: int, name: str):
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=f"Игрок {name}. Ошибка регистрации",
        )
    )


async def registration_failed_message(api: "VkApiAccessor", peer_id: int):
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=f"Для игры необходимо хотя бы 2 участника",
        )
    )


async def registration_success_message(api: "VkApiAccessor", peer_id: int):
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=f"Регистрация завершена. Если захотите узнать счет игры - напишите '!статус'",
        )
    )


async def player_move_message(api: "VkApiAccessor", peer_id: int, user: str, last_word: str, timeout: int):
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=f"Ходит игрок {user}. Предыдущее слово - {last_word}. Время на ход {timeout} секунд",
        )
    )


async def player_timeout_message(api: "VkApiAccessor", peer_id: int, user: str):
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=f"Игрок {user} - время вышло. Вы покидаете игру",
        )
    )


async def player_used_word_message(api: "VkApiAccessor", peer_id: int, user: str, word: str):
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=f"Игрок {user} - слово {word} уже называлось. Вы покидаете игру",
        )
    )


async def player_word_in_black_list(api: "VkApiAccessor", peer_id: int, user: str, word: str):
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=f"Игрок {user} - слова {word} не существует. Вы покидаете игру",
        )
    )


async def city_doesnt_exist(api: "VkApiAccessor", peer_id: int, user: str, word: str):
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=f"Игрок {user} - города {word} не существует. Вы покидаете игру",
        )
    )


async def player_word_wrong(api: "VkApiAccessor", peer_id: int, user: str, word: str, last_word):
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=f"Игрок {user} - слово {word} не начинается на последнюю букву предыдущего слова {last_word}."
            f"Вы покидаете игру",
        )
    )


async def game_finished_message(api: "VkApiAccessor", peer_id: int, name: typing.Optional[str] = None):
    if name:
        msg = f"Игра завершена. Победитель - {name}"
    else:
        msg = f"Игра завершена."
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=msg,
        )
    )


async def status_message(api: "VkApiAccessor", peer_id: int, status: str, data: typing.Optional[list] = None):
    if status == "init":
        msg = f"Игра еще не началась. Для начала регистрации напишите слова или города"
    elif status == "registration":
        msg = f"Идет регистрация. Зарегистрированы следующие игроки\n"
        msg += ' '.join([f"{player[0]}. {player[1]}" for player in data])
    else:
        msg = f"Счет игры: "
        msg += ' '.join([f"{player[0]}. {player[1]}: {player[2]}" for player in data])

    await api.send_message(
        Message(
            peer_id=peer_id,
            text=msg,
        )
    )


async def vote_ack_message(api: "VkApiAccessor", peer_id: int, name: str):
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=f"Игрок {name} проголосовал",
        )
    )


async def vote_conflict_message(api: "VkApiAccessor", peer_id: int, name: str):
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=f"Игрок {name}. Вы уже голосовали",
        )
    )


async def vote_message(api: "VkApiAccessor", peer_id: int, word: str, timeout: int):
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=f"Неизвестное слово {word}, голосование продлится {timeout} секунд"
                 f" если вы считаете, что оно существует, напишите 'Да', если не существует - 'Нет' ",
        )
    )


async def vote_result_message(api: "VkApiAccessor", peer_id: int, word: str, result: bool):
    if result:
        result_str = f" существует"
    else:
        result_str = f" не существует"
    msg = f"Голосование окончено. Слово {word}" + result_str
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=msg,
        )
    )


async def vote_self_message(api: "VkApiAccessor", peer_id: int, name: str):
    await api.send_message(
        Message(
            peer_id=peer_id,
            text=f"Игрок {name}. Вы не можете голосовать за свое слово",
        )
    )