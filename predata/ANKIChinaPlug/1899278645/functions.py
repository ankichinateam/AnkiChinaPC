"""
Copyright:  (c) 2019 ignd
            (c) 2014-2018 Stefan van den Akker
            (c) 2017-2018 Damien Elmes
            (c) 2018 Glutanimate
License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
Use this at your own risk
"""

import json
from anki.utils import (
    isMac,
    isWin,
)

from aqt.editor import Editor


def setmycategories(editor):
    editor.mycategories = {
        'class': editor.my_apply_span_class,
        'style': editor.my_apply_style,
        'Backcolor (inline)': editor.setBackcolor,
        'Backcolor (via class)': editor.my_apply_span_class,
        'Forecolor': editor.setForecolor,
    }
Editor.setmycategories = setmycategories


def setBackcolor(editor, color):
    # from miniformat pack _wrapWithBgColour
    """
    Wrap the selected text in an appropriate tag with a background color.
    """
    # On Linux, the standard 'hiliteColor' method works. On Windows and OSX
    # the formatting seems to get filtered out

    editor.web.eval("""
        if (!setFormat('hiliteColor', '%s')) {
            setFormat('backcolor', '%s');
        }
        """ % (color, color))

    if isWin or isMac:
        # remove all Apple style classes, which is needed for
        # text highlighting on platforms other than Linux
        editor.web.eval("""
            var matches = document.querySelectorAll(".Apple-style-span");
            for (var i = 0; i < matches.length; i++) {
                matches[i].removeAttribute("class");
            }
        """)
Editor.setBackcolor = setBackcolor


def setForecolor(editor, color):
    editor.web.eval("setFormat('forecolor', '%s')" % color)
Editor.setForecolor = setForecolor


def my_apply_style(editor, style):
    selected = editor.web.selectedText()
    styled = "".join(['<span style="{}">'.format(style), selected, '</span>'])
    editor.web.eval("document.execCommand('inserthtml', false, %s);"
                    % json.dumps(styled))
    # before = """<span style="{}">""".format(style)
    # after = """</span>"""
    # editor.web.eval("wrap('{}', '{}');".format(before, after))
Editor.my_apply_style = my_apply_style


def my_apply_span_class(editor, _class):
    selected = editor.web.selectedText()
    styled = "".join(['<span class="{}">'.format(_class), selected, '</span>'])
    editor.web.eval("document.execCommand('inserthtml', false, %s);"
                    % json.dumps(styled))
Editor.my_apply_span_class = my_apply_span_class
