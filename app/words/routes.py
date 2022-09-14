import typing

from app.words.views import (
    WordAddView,
    WordListView,
    SettingAddView,
    SettingListView,
    SettingGetView,
    SettingPatchView,
    WordPatchView,
    WordDeleteView,
    WordGetView,
    SettingDeleteView, PlayerAddView, PlayerGetView, PlayerListView, PlayerDeleteView, PlayerPatchView, GameAddView,
    GameGetView, GameListView, GamePatchView, GameDeleteView,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/words.add_word", WordAddView)
    app.router.add_view("/words.list_words", WordListView)
    app.router.add_view("/words.patch_word", WordPatchView)
    app.router.add_view("/words.delete_word", WordDeleteView)
    app.router.add_view("/words.get_word", WordGetView)

    app.router.add_view("/words.add_setting", SettingAddView)
    app.router.add_view("/words.get_setting", SettingGetView)
    app.router.add_view("/words.list_settings", SettingListView)
    app.router.add_view("/words.patch_setting", SettingPatchView)
    app.router.add_view("/words.delete_setting", SettingDeleteView)

    app.router.add_view("/words.add_player", PlayerAddView)
    app.router.add_view("/words.get_player", PlayerGetView)
    app.router.add_view("/words.list_players", PlayerListView)
    app.router.add_view("/words.patch_player", PlayerPatchView)
    app.router.add_view("/words.delete_player", PlayerDeleteView)

    app.router.add_view("/words.add_game", GameAddView)
    app.router.add_view("/words.get_game", GameGetView)
    app.router.add_view("/words.list_games", GameListView)
    app.router.add_view("/words.patch_game", GamePatchView)
    app.router.add_view("/words.delete_game", GameDeleteView)
