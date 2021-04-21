"""
Copyright:  (c) 2019 ignd
            (c) 2014-2018 Stefan van den Akker
            (c) 2017-2018 Damien Elmes
            (c) 2018 Glutanimate
License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
Use this at your own risk
"""

from pprint import pprint as pp

from aqt.editor import Editor
from aqt.utils import showInfo

from .menu import *
from .functions import *

addon_path = os.path.dirname(__file__)
iconfolder = os.path.join(addon_path, "icons")


def makethisbutton21(editor, e, func):
    from .color_style_class_buttons import config
    try:
        name = e["Text_in_menu"]
        tooltip = e["extrabutton_tooltip"] + ' ' + e["Setting"]
        label = e["extrabutton_text"]
        hotkey = e["Hotkey"]
        function = lambda e=editor, c=e["Setting"]: func(e, c)
    except KeyError:
        showInfo("Multi Highlight add-on not configured properly")
        return ""
    else:
        b = editor.addButton(icon=None,
                             cmd=name,
                             func=function,
                             tip="{} ({})".format(tooltip, hotkey),
                             label=label,
                             keys=None,
                             )
    return b


def SetupShortcuts21(cuts, editor):
    from .color_style_class_buttons import config
    for e in config['v3']:
        if e.get("Hotkey", False):  # and not config["v2_show_in_contextmenu"]:
            func = editor.mycategories[e['Category']]
            cuts.append((e["Hotkey"], lambda s=e["Setting"], f=func: f(editor, s)))


def setupButtons21(buttons, editor):
    from .color_style_class_buttons import config
    for e in config['v3']:
        # check if extrabutton_show is set and if True:
        if e.get('extrabutton_show', False):
            func = editor.mycategories[e['Category']]
            buttons.append(makethisbutton21(editor, e, func))

    # collapsible menu
    show_style_selector_button = False
    for e in config['v3']:
        if e['Show_in_menu']:
            show_style_selector_button = True
    if show_style_selector_button:
        if config['v2_menu_styling'] is True:
            func = additional_menu_styled
        else:
            func = additional_menu_basic
        b = editor.addButton(os.path.join(iconfolder, "more_rotated.png"),
                             "XX",
                             func,
                             tip="apply styles",
                             keys=config['v2_key_styling_menu'])
        buttons.append(b)

    return buttons
