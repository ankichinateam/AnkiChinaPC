# License: AGPLv3

import os

from aqt.editor import Editor, EditorWebView
from aqt.qt import *
from pprint import pprint as pp


def co_my_highlight_helper(view, category, setting):
    func = view.editor.mycategories[category]
    func(view.editor, setting)


def co_hex_to_rgb(color):
    # https://stackoverflow.com/a/29643643
    c = color.lstrip('#')
    red = int(c[0:2], 16)
    green = int(c[2:4], 16)
    blue = int(c[4:6], 16)
    alpha = 128
    values = "{}, {}, {}, {}".format(red, green, blue, alpha)
    return values


def co_return_stylesheet(e):
    if e['Category'] == 'Backcolor (inline)':
        thiscolor = co_hex_to_rgb(e['Setting'])
        line1 = "background-color: rgba({}); ".format(thiscolor)
    elif e['Category'] == 'Backcolor (via class)':
        thiscolor = co_hex_to_rgb(e['Text_in_menu_styling'])
        line1 = "background-color: rgba({}); ".format(thiscolor)
    elif e['Category'] == 'Forecolor':
        thiscolor = co_hex_to_rgb(e['Setting'])
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


def co_my_label_text(_dict, fmt):
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


def co_create_menu_entry(view, e, parentmenu):
    t = co_my_label_text(e, True)
    y = QLabel(t)
    # https://stackoverflow.com/a/6876509
    y.setAutoFillBackground(True)
    stylesheet = co_return_stylesheet(e)
    y.setStyleSheet(stylesheet)
    x = QWidgetAction(parentmenu)
    x.setDefaultWidget(y)
    cat = e["Category"]
    se = e.get("Setting", e.get("Category", False))
    x.triggered.connect(lambda _, a=cat, b=se: co_my_highlight_helper(view, a, b))  # ???
    return x


def add_to_context_styled(view, menu):
    from .color_style_class_buttons import config
    menu.addSeparator()

    cmbg, cmbgc, cmfc, cmst, cmcl = "", "", "", "", ""
    groups = {
        'Backcolor (inline)': cmbg,
        'Backcolor (via class)': cmbgc,
        'Forecolor': cmfc,
        'style': cmst,
        'class': cmcl,
    }
    for i in config['context_menu_groups']:
        groups[i] = menu.addMenu(i)

    for e in config['v3']:
        if e.get('Show_in_menu', True):
            relevantgroup = groups[e['Category']]
            relevantgroup.addAction(co_create_menu_entry(view, e, relevantgroup))
    # menu.exec_(QCursor.pos())


def add_to_context_unstyled(view, menu):
    from .color_style_class_buttons import config
    menu.addSeparator()

    cmbg, cmbgc, cmfc, cmst, cmcl = "", "", "", "", ""
    groups = {
        'Backcolor (inline)': cmbg,
        'Forecolor': cmfc,
        'Backcolor (via class)': cmbgc,
        'style': cmst,
        'class': cmcl,
    }
    for i in config['context_menu_groups']:
        groups[i] = menu.addMenu(i)

    for e in config['v3']:
        if e.get('Show_in_menu', False):
            text = co_my_label_text(e, False)
            relevantgroup = groups[e['Category']]
            a = relevantgroup.addAction(text)
            cat = e["Category"]
            se = e.get("Setting", e.get("Category", False))
            a.triggered.connect(lambda _, a=cat, b=se: co_my_highlight_helper(view, a, b))
            # a.setShortcutVisibleInContextMenu(True)


def add_to_context(view, menu):
    from .color_style_class_buttons import config
    if config["v2_menu_styling"]:
        add_to_context_styled(view, menu)
    else:
        add_to_context_unstyled(view, menu)
