# License: AGPLv3

import random
import os
import re
import json

from pprint import pprint as pp
from collections import OrderedDict

from aqt import mw
from aqt.qt import *
from aqt.utils import (
    askUser,
    getFile,
    getSaveFile,
    showInfo,
    tooltip
)

from .defaultconfig import defaultconfig
from .forms import settings_main_widgets
from .forms import settings_select_category
from .forms import settings_forecolor_bgcolor
from .forms import settings_style
from .forms import settings_class
from .forms import settings_shortcut


def bg_classname():
    alnum = 'abcdefghijklmnopqrstuvwxyz0123456789'
    id = 'bgCol_'
    for i in range(6):
        id += random.choice(alnum)
    return id


class HotkeySelect(QDialog):
    def __init__(self, parent=None, shortcut=None):
        self.parent = parent
        QDialog.__init__(self, parent, Qt.Window)
        self.dialog = settings_shortcut.Ui_Dialog()
        self.dialog.setupUi(self)
        if shortcut:
            if ("super" or "meta") in shortcut:
                text = ("illegal key name like 'super' or 'meta' in shortcut "
                        "defintion. In the following window make sure to check and "
                        "adjust the line/setting 'Button'."
                        )
                showInfo(text)
            shortcut = shortcut.lower()
            if "ctrl" in shortcut:
                shortcut = shortcut.replace("ctrl+", "")
                self.dialog.cb_ctrl.setChecked(True)
            if "shift" in shortcut:
                shortcut = shortcut.replace("shift+", "")
                self.dialog.cb_shift.setChecked(True)
            if "alt" in shortcut:
                shortcut = shortcut.replace("alt+", "")
                self.dialog.cb_alt.setChecked(True)
            if "meta" in shortcut:
                shortcut = shortcut.replace("meta+", "")
                self.dialog.cb_metasuper.setChecked(True)
            self.dialog.le_key.setText(shortcut)

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        self.hotkey = ""
        if self.dialog.cb_ctrl.isChecked():
            self.hotkey += "ctrl+"
        if self.dialog.cb_shift.isChecked():
            self.hotkey += "shift+"
        if self.dialog.cb_alt.isChecked():
            self.hotkey += "alt+"
        if self.dialog.cb_metasuper.isChecked():
            self.hotkey += "meta+"
        self.hotkey += self.dialog.le_key.text()
        QDialog.accept(self)


class SettingsForStyle(QDialog):
    def __init__(self, parent=None, config=None):
        self.parent = parent
        self.config = config
        QDialog.__init__(self, parent, Qt.Window)
        self.dialog = settings_style.Ui_Dialog()
        self.dialog.setupUi(self)
        self.dialog.pb_hotkeyset.clicked.connect(self.onHotkey)
        self.hotkey = ""
        self.color = ""
        if config:
            if config["Hotkey"]:
                self.hotkey = config["Hotkey"]
                self.dialog.pb_hotkeyset.setText(self.hotkey)
            if config["Setting"]:
                self.dialog.pte_style.insertPlainText(config["Setting"])
            if config["Show_in_menu"]:
                self.dialog.cb_contextmenu_show.setChecked(True)
            if config["Text_in_menu"]:
                self.dialog.le_contextmenu_text.setText(config["Text_in_menu"])
            if config["extrabutton_show"]:
                self.dialog.cb_extrabutton_show.setChecked(True)
            if config["extrabutton_text"]:
                self.dialog.le_extrabutton_text.setText(config["extrabutton_text"])
            if config["extrabutton_tooltip"]:
                self.dialog.le_tooltip_text.setText(config["extrabutton_tooltip"])

    def onHotkey(self):
        h = HotkeySelect(self, self.hotkey)
        if h.exec_():
            self.hotkey = h.hotkey
            self.dialog.pb_hotkeyset.setText(self.hotkey)

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        self.newsetting = {
            "Category": "",  # if new I add in the category in the parent
            "Hotkey": self.hotkey,
            "Setting": self.dialog.pte_style.toPlainText(),
            "Show_in_menu": self.dialog.cb_contextmenu_show.isChecked(),
            "Text_in_menu":  self.dialog.le_contextmenu_text.text(),
            "Text_in_menu_styling": self.dialog.pte_style.toPlainText(),
            "extrabutton_show": self.dialog.cb_extrabutton_show.isChecked(),
            "extrabutton_text":  self.dialog.le_extrabutton_text.text(),
            "extrabutton_tooltip":  self.dialog.le_tooltip_text.text(),
        }
        if self.config:   # new entries don't have this entry yet
            if "Category" in self.config:
                self.newsetting["Category"] = self.config["Category"]
        QDialog.accept(self)


class SettingsForClass(QDialog):
    def __init__(self, parent=None, config=None):
        self.parent = parent
        self.config = config
        QDialog.__init__(self, parent, Qt.Window)
        self.dialog = settings_class.Ui_Dialog()
        self.dialog.setupUi(self)
        self.dialog.pb_hotkeyset.clicked.connect(self.onHotkey)
        self.hotkey = ""
        self.color = ""
        if config:
            if config["Hotkey"]:
                self.hotkey = config["Hotkey"]
                self.dialog.pb_hotkeyset.setText(self.hotkey)
            if config["Setting"]:
                self.dialog.le_classname.setText(config["Setting"])
            if config["Text_in_menu_styling"]:
                self.dialog.pte_style.insertPlainText(config["Text_in_menu_styling"])
            if config["Show_in_menu"]:
                self.dialog.cb_contextmenu_show.setChecked(True)
            if config["Text_in_menu"]:
                self.dialog.le_contextmenu_text.setText(config["Text_in_menu"])
            if config["extrabutton_show"]:
                self.dialog.cb_extrabutton_show.setChecked(True)
            if config["extrabutton_text"]:
                self.dialog.le_extrabutton_text.setText(config["extrabutton_text"])
            if config["extrabutton_tooltip"]:
                self.dialog.le_tooltip_text.setText(config["extrabutton_tooltip"])

    def onHotkey(self):
        h = HotkeySelect(self, self.hotkey)
        if h.exec_():
            self.hotkey = h.hotkey
            self.dialog.pb_hotkeyset.setText(self.hotkey)

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        classname = self.dialog.le_classname.text()
        o = re.match("""-?[_a-zA-Z]+[_a-zA-Z0-9-]*""", classname)
        if not o:
            t = ("Illegal character in classname. "
                 "the name must begin with an underscore (_), a hyphen (-), or a letter(a–z), "
                 "followed by any number of hyphens, underscores, letters, or numbers. "
                 "If the first character is a hyphen, the second character must be a letter"
                 "or underscore, and the name must be at least 2 characters long."
                )
            showInfo(t)
            return
        self.newsetting = {
            "Category": "",  # if new I add in the category in the parent
            "Hotkey": self.hotkey,
            "Setting": self.dialog.le_classname.text(),
            "Show_in_menu": self.dialog.cb_contextmenu_show.isChecked(),
            "Text_in_menu":  self.dialog.le_contextmenu_text.text(),
            "Text_in_menu_styling": self.dialog.pte_style.toPlainText(),
            "extrabutton_show": self.dialog.cb_extrabutton_show.isChecked(),
            "extrabutton_text":  self.dialog.le_extrabutton_text.text(),
            "extrabutton_tooltip":  self.dialog.le_tooltip_text.text(),
        }
        if self.config:   # new entries don't have this entry yet
            if "Category" in self.config:
                self.newsetting["Category"] = self.config["Category"]
        QDialog.accept(self)


# TODO Merge with SettingsForForeBgColor (just some ifs neeeded)
class SettingsForBgColorClass(QDialog):
    def __init__(self, parent=None, category=None, config=None):
        self.category = category
        self.config = config
        self.parent = parent
        QDialog.__init__(self, parent, Qt.Window)
        self.dialog = settings_forecolor_bgcolor.Ui_Dialog()
        self.dialog.setupUi(self)
        self.dialog.pb_hotkeyset.clicked.connect(self.onHotkey)
        self.hotkey = ""
        self.color = ""
        self.thisclass = bg_classname()
        if config:
            if "Hotkey" in config:
                self.hotkey = config["Hotkey"]
                self.dialog.pb_hotkeyset.setText(self.hotkey)
            if "Setting" in config:
                if config["Setting"]:
                    self.thisclass = config["Setting"]
            if "Text_in_menu_styling" in config:
                self.color = config["Text_in_menu_styling"]
                self.dialog.pb_color.setText(str(self.color))
            if config["Show_in_menu"]:
                self.dialog.cb_contextmenu_show.setChecked(True)
            if config["Text_in_menu"]:
                self.dialog.le_contextmenu_text.setText(config["Text_in_menu"])
            if config["extrabutton_show"]:
                self.dialog.cb_extrabutton_show.setChecked(True)
            if config["extrabutton_text"]:
                self.dialog.le_extrabutton_text.setText(config["extrabutton_text"])
            if config["extrabutton_tooltip"]:
                self.dialog.le_tooltip_text.setText(config["extrabutton_tooltip"])
        self.dialog.pb_color.clicked.connect(self.getColor)

    def onHotkey(self):
        h = HotkeySelect(self, self.hotkey)
        if h.exec_():
            self.hotkey = h.hotkey
            self.dialog.pb_hotkeyset.setText(self.hotkey)

    def getColor(self):
        new = QColorDialog.getColor(QColor(self.color), None)
        if new.isValid():
            self.color = new.name()
        self.dialog.pb_color.setText(str(self.color))

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        self.newsetting = {
            "Category": self.category if self.category else "",
            "Hotkey": self.hotkey,
            "Setting": self.thisclass,
            "Show_in_menu": self.dialog.cb_contextmenu_show.isChecked(),
            "Text_in_menu":  self.dialog.le_contextmenu_text.text(),
            "Text_in_menu_styling": self.color,
            "extrabutton_show": self.dialog.cb_extrabutton_show.isChecked(),
            "extrabutton_text":  self.dialog.le_extrabutton_text.text(),
            "extrabutton_tooltip":  self.dialog.le_tooltip_text.text(),
        }
        QDialog.accept(self)


class SettingsForForeBgColor(QDialog):
    def __init__(self, parent=None, category=None, config=None):
        self.category = category
        self.config = config
        self.parent = parent
        QDialog.__init__(self, parent, Qt.Window)
        self.dialog = settings_forecolor_bgcolor.Ui_Dialog()
        self.dialog.setupUi(self)
        self.dialog.pb_hotkeyset.clicked.connect(self.onHotkey)
        self.hotkey = ""
        self.color = ""
        if config:
            if "Hotkey" in config:
                self.hotkey = config["Hotkey"]
                self.dialog.pb_hotkeyset.setText(self.hotkey)
            if "Setting" in config:
                self.color = config["Setting"]  # .replace("background-color: ","").replace(";","")
                self.dialog.pb_color.setText(str(self.color))
            if config["Show_in_menu"]:
                self.dialog.cb_contextmenu_show.setChecked(True)
            if config["Text_in_menu"]:
                self.dialog.le_contextmenu_text.setText(config["Text_in_menu"])
            if config["extrabutton_show"]:
                self.dialog.cb_extrabutton_show.setChecked(True)
            if config["extrabutton_text"]:
                self.dialog.le_extrabutton_text.setText(config["extrabutton_text"])
            if config["extrabutton_tooltip"]:
                self.dialog.le_tooltip_text.setText(config["extrabutton_tooltip"])
        self.dialog.pb_color.clicked.connect(self.getColor)

    def onHotkey(self):
        h = HotkeySelect(self, self.hotkey)
        if h.exec_():
            self.hotkey = h.hotkey
            self.dialog.pb_hotkeyset.setText(self.hotkey)

    def getColor(self):
        new = QColorDialog.getColor(QColor(self.color), None)
        if new.isValid():
            self.color = new.name()
        self.dialog.pb_color.setText(str(self.color))

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        self.newsetting = {
            "Category": self.category if self.category else "",
            "Hotkey": self.hotkey,
            "Setting": self.color,  # "background-color: " + self.color + ";",
            "Show_in_menu": self.dialog.cb_contextmenu_show.isChecked(),
            "Text_in_menu":  self.dialog.le_contextmenu_text.text(),
            "Text_in_menu_styling": "",
            "extrabutton_show": self.dialog.cb_extrabutton_show.isChecked(),
            "extrabutton_text":  self.dialog.le_extrabutton_text.text(),
            "extrabutton_tooltip":  self.dialog.le_tooltip_text.text(),
        }
        QDialog.accept(self)


def gui_dialog(inst, sel=None, config=None):
    if not sel:
        sel = config['Category']
    if sel in ["Backcolor (inline)", "Forecolor"]:
        return SettingsForForeBgColor(inst, sel, config)
    if sel in ["Backcolor (via class)"]:
        return SettingsForBgColorClass(inst, sel, config)
    elif sel == "style":
        return SettingsForStyle(inst, config)
    elif sel == "class":
        return SettingsForClass(inst, config)
    else:
        text = ("Error in config of add-on 'editor: apply font "
                "color, background color, custom class, custom style'"
                "\n\nThe following part of the config contains an error in"
                "the setting 'Category': "
                "\n\n%s"
                "\n\nClick Abort/Cancel and maybe delete this entry."
                "\n\nYou might encounter some error messages after this window."
                % str(config)
                )
        showInfo(text)
        return


class AddEntry(QDialog):
    def __init__(self, parent=None):
        self.parent = parent
        QDialog.__init__(self, parent, Qt.Window)
        self.dialog = settings_select_category.Ui_Dialog()
        self.dialog.setupUi(self)
        l = ["Backcolor (inline)", "Backcolor (via class)", "Forecolor", "class", "style"]
        self.dialog.list_categories.addItems(l)
        self.dialog.list_categories.itemDoubleClicked.connect(self.accept)

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        sel = self.dialog.list_categories.currentItem().text()
        if sel in ["Backcolor (inline)", "style"]:
            text = ("In Anki 2.1 when you copy text from one field to another "
                    "Anki will remove the background color and styles. "
                    "\n\nThis is not just a limitation of this add-on. The same "
                    "applies e.g. to the background color function of the "
                    "add-on 'Mini Format Pack'. "
                    "On the other hand when trying to apply the background color "
                    "to text that belongs to different html tags like a heading and "
                    "regular text the wrapping in a class will not work."
                    "\n\nContinue?"
                    )
            if not askUser(text):
                return
        a = gui_dialog(self, sel=sel, config=None)
        if a.exec_():
            self.newsetting = a.newsetting
            self.newsetting['Category'] = sel
            QDialog.accept(self)
        else:
            QDialog.reject(self)


class ButtonOptions(QDialog):
    """ """

    def __init__(self, c):
        parent = mw.app.activeWindow()
        QDialog.__init__(self, parent)
        self.config = c
        self.bo = settings_main_widgets.Ui_Dialog()
        self.bo.setupUi(self)
        self.setWindowTitle("Anki: Change Options for Add-on 'Buttons for Color and Style'")
        self.init_tables()
        self.init_buttons()

    def init_buttons(self):
        self.set_check_state_buttons()
        self.bo.pb_modify_active.clicked.connect(
            lambda _, w=self.bo.tw_active: self.process_row(w, "modify"))
        self.bo.pb_modify_inactive.clicked.connect(
            lambda _, w=self.bo.tw_inactive: self.process_row(w, "modify"))
        self.bo.pb_add.clicked.connect(self.onAdd)
        self.bo.pb_deactivate.clicked.connect(
            lambda _, w=self.bo.tw_active: self.process_row(w, "switch"))
        self.bo.pb_activate.clicked.connect(
            lambda _, w=self.bo.tw_inactive: self.process_row(w, "switch"))
        self.bo.pb_delete_from_active.clicked.connect(
            lambda _, w=self.bo.tw_active: self.process_row(w, "del"))
        self.bo.pb_delete_from_inactive.clicked.connect(
            lambda _, w=self.bo.tw_inactive: self.process_row(w, "del"))
        self.bo.cb_classes_to_styling.toggled.connect(self.onClassesToStyling)
        self.bo.pb_global_multibutton_show.clicked.connect(self.onHotkey)
        self.bo.pb_more.clicked.connect(self.onMore)

    def set_check_state_buttons(self):
        if self.config["v2_show_in_contextmenu"]:
            self.bo.cb_global_contextmenu_show.setChecked(True)
        if self.config["v2_menu_styling"]:
            self.bo.cb_global_contextmenu_with_styling.setChecked(True)
        if "write_classes_to_templates" in self.config:
            if self.config["write_classes_to_templates"]:
                self.bo.cb_classes_to_styling.setChecked(True)
        if self.config["v2_key_styling_menu"]:
            self.bo.pb_global_multibutton_show.setText(self.config["v2_key_styling_menu"])

    def onHotkey(self):
        h = HotkeySelect(self, self.config["v2_key_styling_menu"])
        if h.exec_():
            self.config["v2_key_styling_menu"] = h.hotkey
            self.bo.pb_global_multibutton_show.setText(self.config["v2_key_styling_menu"])

    def onMore(self):
        m = QMenu(mw)
        a = m.addAction("Restore default config")
        a.triggered.connect(self.restoreDefault)
        a = m.addAction("Export Button Config to json")
        a.triggered.connect(self.onExport)
        a = m.addAction("Import Button Config from json")
        a.triggered.connect(self.onImport)
        m.exec_(QCursor.pos())

    def restoreDefault(self):
        text = "Delete your setup and restore default buttons config?"
        if askUser(text, defaultno=False):
            self.config["v3"] = defaultconfig["v3"][:]
            self.config["v3_inactive"] = [][:]
            self.active = self.config["v3"]
            self.inactive = self.config["v3_inactive"]
            self.bo.tw_active.setRowCount(0)
            self.bo.tw_inactive.setRowCount(0)
            self.set_table(self.bo.tw_active, self.active)
            self.set_table(self.bo.tw_inactive, self.inactive)

    def onExport(self):
        o = getSaveFile(mw, title="Anki - Select file for export",
                        dir_description="jsonbuttons",
                        key=".json",
                        ext=".json",
                        fname="anki_addon_styling_buttons_config.json"
                        )
        if o:
            self.updateConfig()
            with open(o, 'w') as fp:
                json.dump(self.config, fp)

    def onImport(self):
        o = getFile(self, "Anki - Select file for import ", None, "json",
                            key="json", multi=False)
        if o:
            try:
                with open(o, 'r') as fp:
                    c = json.load(fp)
            except:
                showInfo("Aborting. Error while reading file.")
            try:
                self.config = c
            except:
                showInfo("Aborting. Error in file.")
            self.set_check_state_buttons()
            self.active = self.config["v3"]
            self.inactive = self.config["v3_inactive"]
            self.bo.tw_active.setRowCount(0)
            self.bo.tw_inactive.setRowCount(0)
            self.set_table(self.bo.tw_active, self.active)
            self.set_table(self.bo.tw_inactive, self.inactive)

    def onClassesToStyling(self):
        text = ("Only use this option if you have backups and know how to restore them. "
                "This option modifies all of your note types. If something went wrong "
                "there would be a lot of damage. But this option has been available for months "
                "and in this time the add-on had hundreds of downloads and so far I "
                "haven't seen a problem reported."
                )
        showInfo(text)

    def onAdd(self):
        e = AddEntry(self)
        if e.exec_():
            self.active.append(e.newsetting)
            self.active = sorted(self.active, key=lambda k: k['Category'])
            self.set_table(self.bo.tw_active, self.active)

    def process_row(self, activewidget, action):
        if activewidget == self.bo.tw_active:
            thisli = self.active
            otherli = self.inactive
            otherwidget = self.bo.tw_inactive
        else:
            thisli = self.inactive
            otherli = self.active
            otherwidget = self.bo.tw_active
        try:
            row = activewidget.currentRow()
        except:
            tooltip("No row selected.")
        else:
            if row != -1:
                if action == "modify":
                    config = thisli[row]
                    a = gui_dialog(self, sel=None, config=config)
                    if a.exec_():
                        thisli[row] = a.newsetting
                        self.set_table(activewidget, thisli)
                if action == "del":
                    text = "Delete row number %s" % str(row+1)
                    if askUser(text, defaultno=True):
                        del thisli[row]
                        self.set_table(activewidget, thisli)
                elif action == "switch":
                    text = "Toggle state row number %s" % str(row+1)
                    if askUser(text, defaultno=True):
                        otherli.append(thisli[row])
                        del thisli[row]
                        thisli = sorted(thisli, key=lambda k: k['Category'])
                        otherli = sorted(otherli, key=lambda k: k['Category'])
                        self.set_table(activewidget, thisli)
                        self.set_table(otherwidget, otherli)
            else:
                tooltip('no row selected.')

    def init_tables(self):
        headers = [("Category", "Category"),
                   ("Hotkey", "Hotkey"),
                   ("Class", "Class"),
                   ("Setting", "Setting\n(Color or style/class properties)"),
                   ("Show_in_menu", "Show in\nmenu"),
                   ("Text_in_menu", "Text in\nmenu"),
                   ("extrabutton_show", "extrabutton\nshow"),
                   ("extrabutton_text", "extrabutton\ntext"),
                   ("extrabutton_tooltip", "extrabutton\ntooltip"),
                   ]
        self.tableHeaders = OrderedDict(headers)

        self.active = self.config["v3"]
        if "v3_inactive" in self.config:
            self.inactive = self.config["v3_inactive"]
        else:
            self.inactive = []
        self.active = sorted(self.active, key=lambda k: k['Category'])
        self.inactive = sorted(self.inactive, key=lambda k: k['Category'])
        self.set_table(self.bo.tw_active, self.active)
        self.bo.tw_active.itemDoubleClicked.connect(self.ondoubleclick)
        self.set_table(self.bo.tw_inactive, self.inactive)
        self.bo.tw_inactive.itemDoubleClicked.connect(self.ondoubleclick)

    def set_table(self, widget, li):
        widget.setSelectionBehavior(QTableView.SelectRows)
        widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        widget.setRowCount(len(li))
        widget.setColumnCount(len(self.tableHeaders))
        widget.setHorizontalHeaderLabels(self.tableHeaders.values())
        # widget.verticalHeader().setVisible(False)
        widget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        widget.resizeColumnsToContents()
        widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # stretch all to resize
        widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)  # Stretch
        # per column https://stackoverflow.com/q/38098763
        # widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        # widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        # widget.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        widget.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        # widget.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        # widget.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        widget.horizontalHeader().setSectionResizeMode(8, QHeaderView.Stretch)

        # workaround for QTableWidget: add empty strings to all fields to make them clickable
        for i in range(len(li)):
            for j in range(len(self.tableHeaders)):
                newitem = QTableWidgetItem(str(" "))
                widget.setItem(j, i, newitem)

        for a, b in enumerate(li):
            for k, v in b.items():
                try:
                    index = list(self.tableHeaders.keys()).index(k)
                    if b["Category"] in ["Backcolor (via class)", "class"]:
                        if k == "Setting":
                            index = 2
                except ValueError:
                    # field "active" and ugly fix for class styling in Text_in_menu_styling
                    if b["Category"] in ["Backcolor (via class)", "class"]:
                        if k == "Text_in_menu_styling":
                            index = 3
                            newitem = QTableWidgetItem(str(v))
                            widget.setItem(a, index, newitem)
                else:
                    newitem = QTableWidgetItem(str(v))
                    widget.setItem(a, index, newitem)

    def ondoubleclick(self, item):
        row = item.row()
        w = item.tableWidget()
        if w == self.bo.tw_active:
            li = self.active
        else:
            li = self.inactive
        config = li[row]
        a = gui_dialog(self, sel=None, config=config)
        if a.exec_():
            li[row] = a.newsetting
            self.set_table(w, li)

    def updateConfig(self):
        self.config["v3"] = self.active
        self.config["v3_inactive"] = self.inactive

        if self.bo.cb_classes_to_styling.isChecked():
            self.update_all_templates = True
        else:
            self.update_all_templates = False

        if self.bo.cb_global_contextmenu_show.isChecked():
            self.config["v2_show_in_contextmenu"] = True
        else:
            self.config["v2_show_in_contextmenu"] = False

        if self.bo.cb_global_contextmenu_with_styling.isChecked():
            self.config["v2_menu_styling"] = True
        else:
            self.config["v2_menu_styling"] = False
        media_dir = mw.col.media.dir()
        fpath = os.path.join(media_dir, "syncdummy.txt")
        if not os.path.isfile(fpath):
            with open(fpath, "w") as f:
                f.write("anki sync dummy")
        os.remove(fpath)

    def accept(self):
        self.updateConfig()
        QDialog.accept(self)
