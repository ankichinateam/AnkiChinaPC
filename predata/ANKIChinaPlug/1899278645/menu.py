"""
Copyright:  (c) 2019 ignd
            (c) Glutanimate 2015-2017
License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
Use this at your own risk
"""

import os

from aqt.editor import Editor
from aqt.qt import *
from anki.hooks import addHook

from .colors import hex_to_rgb_string
from .contextmenu import co_hex_to_rgb


def my_highlight_helper(editor, category, setting):
    func = editor.mycategories[category]
    func(editor, setting)
Editor.my_highlight_helper = my_highlight_helper


"""
Stylesheet for QMenu?
- stylesheet refers not to QAction but to QMenu
- idea for QActionWidget from  https://www.python-forum.de/viewtopic.php?t=42747
- some unanswered questions from 2018 about QAction
  https://stackoverflow.com/questions/49882834/pyqt-setting-background-color-of-individual-qmenu-qaction-objects
  https://stackoverflow.com/questions/50159451/style-sheets-how-can-i-manipulate-a-single-qactions-of-qmenu
"""


def return_stylesheet(editor, e):
    if e['Category'] == 'Backcolor (inline)':
        thiscolor = hex_to_rgb_string(e['Setting'])
        line1 = "background-color: rgba({}); ".format(thiscolor)
    elif e['Category'] == 'Backcolor (via class)':
        thiscolor = co_hex_to_rgb(e['Text_in_menu_styling'])
        line1 = "background-color: rgba({}); ".format(thiscolor)
    elif e['Category'] == 'Forecolor':
        thiscolor = hex_to_rgb_string(e['Setting'])
        line1 = "color: rgba({}); ".format(thiscolor)
    else:
        line1 = e['Text_in_menu_styling']

    stylesheet = """QLabel {{
        {}
        font-size: 15px;
        padding-top: 7px;
        padding-bottom: 7px;
        padding-right: 5px;
        padding-left: 5px;
        }}
    """.format(line1)
    return stylesheet
Editor.return_stylesheet = return_stylesheet


def my_label_text(editor, _dict, fmt):
    from .color_style_class_buttons import config
    totallength = config['maxname'] + config['maxshortcut'] + 3
    remaining = totallength - len(_dict.get("Hotkey", 0))
    t1 = _dict.get("Text_in_menu", "Variable Text_in_menu missing")
    # ideally hotkey would be right aligned
    # in html I can use:
    #    <span style="text-align:left;">left<span style="float:right;">right</span></span>
    # BUT float is not supported for text in a QLabel/QString
    # https://doc.qt.io/qt-5/richtext-html-subset.html
    # so I would need two QLabels and some container: complicated
    # I don't want to set the shortcut here with 
    #       a.setShortcut(QKeySequence(e["Hotkey"]))
    #       a.setShortcutVisibleInContextMenu(True)
    # because I set them globally in a different place
    # and setting the same shortcut multiple times disables them. 
    # Also this only works for an unstyled menu and might need to be adjusted for QActionWidget
    if fmt:
        # formatted 
        h = _dict.get("Hotkey", "")
        if h:
            out = t1 + "  (" + h + ")" 
        else:
            out = t1
    else:
        # unformatted
        out = t1.ljust(remaining) + _dict.get("Hotkey", "")
    return out
Editor.my_label_text = my_label_text


def create_menu_entry(editor, e, parentmenu):
    if e.get('IconInMenu', False):
        y = QLabel()
        path = os.path.join(icon_path, e['IconInMenu'])
        pixmap = QPixmap(path)
        y.setPixmap(pixmap)
    else:
        t = editor.my_label_text(e, True)
        y = QLabel(t)
    # https://stackoverflow.com/a/6876509
    y.setAutoFillBackground(True)
    stylesheet = editor.return_stylesheet(e)
    y.setStyleSheet(stylesheet)
    x = QWidgetAction(parentmenu)
    x.setDefaultWidget(y)
    cat = e["Category"]
    se = e.get("Setting", e.get("Category", False))
    x.triggered.connect(lambda _, a=cat, b=se: my_highlight_helper(editor, a, b))
    return x
Editor.create_menu_entry = create_menu_entry


def additional_menu_styled(editor):
    # mod of onAdvanced from editor.py
    from .color_style_class_buttons import config
    m = QMenu(editor.mw)
    for e in config['v3']:
        if e.get('Show_in_menu', False):
            m.addAction(editor.create_menu_entry(e, m))
    m.exec_(QCursor.pos())
Editor.additional_menu_styled = additional_menu_styled


basic_stylesheet = """
QMenu::item {
    padding-top: 5px;
    padding-bottom: 5px;
    padding-right: 5px;
    padding-left: 5px;
    font-family: Roboto Mono;
}
QMenu::item:selected {
    color: black;
    background-color: #D9CD6D;
}
"""


def additional_menu_basic(editor):
    from .color_style_class_buttons import config
    # mod of onAdvanced from editor.py
    m = QMenu(editor.mw)
    # m.setStyleSheet(basic_stylesheet)
    m.setFont(QFont('Courier New', 11))
    for e in config['v3']:
        if e.get('Show_in_menu', False):
            text = editor.my_label_text(e, False)
            a = m.addAction(text)
            cat = e["Category"]
            se = e.get("Setting", e.get("Category", False))
            a.triggered.connect(lambda _, a=cat, b=se: my_highlight_helper(editor, a, b))
    m.exec_(QCursor.pos())
Editor.additional_menu_basic = additional_menu_basic
