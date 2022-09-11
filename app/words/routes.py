import typing

from app.words.views import (

    WordAddView, WordListView, SettingAddView, SettingListView, SettingGetView, SettingPatchView, WordPatchView,
    WordDeleteView, WordGetView, SettingDeleteView)

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
