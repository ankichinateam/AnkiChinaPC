# Copyright: Ankitects Pty Ltd and contributors
# -*- coding: utf-8 -*-
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import requests
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

from PyQt5.QtCore import pyqtSignal

# from PyQt5.QtWebKitWidgets import *
from aqt.qt import *
from aqt.utils import askUser, getOnlyText, openLink, showWarning, shortcut, \
    openHelp
from anki.utils import ids2str, fmtTimeSpan
from anki.errors import DeckRenameError
import aqt
from anki.sound import clearAudioQueue
from anki.hooks import runHook
from copy import deepcopy
from anki.lang import _, ngettext
import time


class WebViewPay(QWidget):
    def __init__(self, browser, parent= None):
        QWidget.__init__(self)
        self.brow = browser
        self.setWindowTitle("云空间升级")
        self.setWindowModality(Qt.ApplicationModal)
        browser = QWebEngineView()
        browser.load(QUrl(_("")%(self.brow.mw.pm.profile['syncUser'])))
        # browser.urlChanged.connect(self.setUrlLine)
        vbox = QVBoxLayout()

        vbox.addWidget(browser)

        self.setLayout(vbox)
        self.resize(600,700)
        # self.close.connect(self.closeWebView)
        # d.setModal(True)
        self.show()

    def closeEvent(self,event):
        self.brow.refresh()

class StartBrowzer(QThread):

    paySignal = pyqtSignal()

    def __init__(self, main):
        QThread.__init__(self)

    def run(self):
        
        time.sleep(1)
        self.paySignal.emit()

class DeckBrowser(QWidget):
    paySignal = pyqtSignal()

    def __init__(self, mw):
        super(QWidget, self).__init__()
        self.mw = mw
        self.web = mw.web
        self.bottom = aqt.toolbar.BottomBar(mw, mw.bottomWeb)
        self.scrollPos = QPoint(0, 0)
        # 支付信号
        
        

    def show(self):
        clearAudioQueue()
        self.web.resetHandlers()
        self.web.onBridgeCmd = self._linkHandler
        self._renderPage()

    def refresh(self):
        self._renderPage()

    # Event handlers
    ##########################################################################

    def setUrlLine(self,url):
        print(url.toString())

    def closeWebView(self):
        self.refresh()

    def _cloudUpdataWarnMessage(self):
        self.d = WebViewPay(self)
        # self.d = QWidget()
        # self.d.setWindowTitle("云空间升级")
        # self.d.setWindowModality(Qt.ApplicationModal)
        # # d.setWindowflags(Qt.Dialog)
        # # todo 打开网页
        # browser = QWebEngineView()
        # browser.load(QUrl(_("http://ankichinas.com?phone=%s")%(self.mw.pm.profile['syncUser'])))
        # browser.urlChanged.connect(self.setUrlLine)
        # # self.d.setBaseSize(800,800)
        # # browser.load(QUrl("http://www.baidu.com"))
        # # browser.showMaximized()
        # vbox = QVBoxLayout()

        # vbox.addWidget(browser)

        # self.d.setLayout(vbox)
        # self.d.resize(600,700)
        # self.close.connect(self.closeWebView)
        # # d.setModal(True)
        # self.d.show()

    def _linkHandler(self, url):
        if ":" in url:
            (cmd, arg) = url.split(":")
        else:
            cmd = url
        if cmd == "open":
            self._selDeck(arg)
        elif cmd == "opts":
            self._showOptions(arg)
        elif cmd == "shared":
            self._onShared()
        elif cmd == "import":
            self.mw.onImport()
        elif cmd == "lots":
            openHelp("using-decks-appropriately")
        elif cmd == "hidelots":
            self.mw.pm.profile['hideDeckLotsMsg'] = True
            self.refresh()
        elif cmd == "create":
            deck = getOnlyText(_("Name for deck:"))
            if deck:
                self.mw.col.decks.id(deck)
                self.refresh()
        elif cmd == "drag":
            draggedDeckDid, ontoDeckDid = arg.split(',')
            self._dragDeckOnto(draggedDeckDid, ontoDeckDid)
        elif cmd == "collapse":
            self._collapse(arg)
        elif cmd == "course":
            self._onCourse()
        elif cmd == 'expand':
            self._cloudUpdataWarnMessage()
        return False

    def _selDeck(self, did):
        self.mw.col.decks.select(did)
        self.mw.onOverview()

    # HTML generation
    ##########################################################################

    _body = """
<center>
<table cellspacing=0 cellpading=3>
%(tree)s
</table>

<br>
%(stats)s
%(countwarn)s
<br>
<br>
%(space)s
</center>
"""

    def _renderPage(self, reuse=False):
        if not reuse:
            self._dueTree = self.mw.col.sched.deckDueTree()
            self._get_extra_button_info()
            self.__renderPage(None)
            return
        self.web.evalWithCallback("window.pageYOffset", self.__renderPage)

    def _get_extra_button_info(self):
        try:
            # Todo
            # 请求数据可以作为例子
            # r = requests.post(aqt.appUpdate, data=d)

            r = requests.get('')
            resp = r.json()
            self.courseText = resp['data'][0]['title']
            self.supportText = resp['data'][1]['title']
            self.wechatText = resp['data'][2]['title']
            self.suggestText = resp['data'][3]['title']
            self.courseUrl = resp['data'][0]['target_url']
            self.supportUrl = resp['data'][1]['target_url']
            self.wechatUrl = resp['data'][2]['target_url']
            self.suggestUrl = resp['data'][3]['target_url']
        except:
            self.courseText = 'ANKI教程'
            self.supportText = '加入志愿者团队'
            self.wechatText = '微信交流群'
            self.suggestText = '改进意见'
            self.courseUrl = 'https://shimo.im/docs/863PvjjHQkCwccX9/'
            self.supportUrl = 'https://shimo.im/docs/ppqpCqjgty9pykk8/'
            self.wechatUrl = 'https://shimo.im/docs/6qhTdwyCXCp8HPXC/'
            self.suggestUrl = 'https://shimo.im/docs/XgWvhqTdKQDkhG8r/'
            # behind proxy, corrupt message, etc
            # print("get Failed")
            return

    def __renderPage(self, offset):
        tree = self._renderDeckTree(self._dueTree)
        stats = self._renderStats()
        self.web.stdHtml(self._body%dict(
            tree=tree, stats=stats, countwarn=self._countWarn(), space=self._renderSpace()),
                         css=["deckbrowser.css"],
                         js=["jquery.js", "jquery-ui.js", "deckbrowser.js"])
        self.web.key = "deckBrowser"
        self._drawButtons()
        if offset is not None:
            self._scrollToOffset(offset)

    def _scrollToOffset(self, offset):
        self.web.eval("$(function() { window.scrollTo(0, %d, 'instant'); });" % offset)

    def _renderStats(self):
        cards, thetime = self.mw.col.db.first("""
select count(), sum(time)/1000 from revlog
where id > ?""", (self.mw.col.sched.dayCutoff-86400)*1000)
        cards = cards or 0
        thetime = thetime or 0
        msgp1 = ngettext("<!--studied-->%d card", "<!--studied-->%d cards", cards) % cards
        buf = _("Studied %(a)s %(b)s today.") % dict(a=msgp1,
                                                     b=fmtTimeSpan(thetime, unit=1, inTime=True))
        return buf

    def _countWarn(self):
        if (self.mw.col.decks.count() < 25 or
                self.mw.pm.profile.get("hideDeckLotsMsg")):
            return ""
        return "<br><div style='width:50%;border: 1px solid #000;padding:5px;'>"+(
            _("You have a lot of decks. Please see %(a)s. %(b)s") % dict(
                a=("<a href=# onclick=\"return pycmd('lots')\">%s</a>" % _(
                    "this page")),
                b=("<br><small><a href=# onclick='return pycmd(\"hidelots\")'>("
                   "%s)</a></small>" % (_("hide"))+
                    "</div>")))

    def _renderSpace(self):
        if not self.mw.pm.profile["syncKey"]:
            buf = ""
        else:
            # Todo
            # 获取剩余空间
            # 
            # <font color="gray"></font>
            # buf = "云空间%0.1fMB/%0.1fMB&nbsp;<a href=\"https://home.firefoxchina.cn/\">扩容</a>" % (aqt.localSpace, aqt.cloudSpace)
            # 获取本地空间
            # aqt.localSpace = self.mw.pm.getLocalDataSize()
            # aqt.localSpace /= 1024*1014
            # 更新本地空间
            self.updateLocalDataSize()
            self.getSpace()
            # buf = "云空间%0.1fMB/%0.1fMB&nbsp;<button title= 扩1容 style=\"background-color:#F0F0F0;color:blue;\" onclick='pycmd(\"expand\");'>  扩容</button>" % (aqt.localSpace, aqt.cloudSpace)
            buf = "云空间%s/%s&nbsp;<button title= 扩1容 style=\"background-color:#F0F0F0;color:blue;\" onclick='pycmd(\"expand\");'>  扩容</button>" % (aqt.localSpace, aqt.cloudSpace)
            # if (aqt.cloudSpace - aqt.localSpace) < 5.0 :
            if (self.cloudSpaceReal - self.mw.pm.getLocalDataSize()) < 0 :
            # if True:
                buf += "<br><br><label title='tip' style=\"background-color:gray;color:white;\">" \
                        "&#12288;云存储空间已不足，请升级&#12288;</label>"
                # self._cloudUpdataWarnMessage()
        return buf
    def updateLocalDataSize(self):
        try:
            # {'key':self.key,'code':idcode.text(),'phone':pnumber.text()}
            # data = {'token':self.prof['token']}
            headers = {"Content-Type": "application/json"}
            headers["Authorization"] = _("Bearer %s"%self.mw.pm.profile['token'])
            data = {"used_size":self.mw.pm.getLocalDataSize()}
            # auth = {'Content-Type':'application/json'},data = data
            r = requests.put('',headers=headers,data= data)
            # print(r.status_code)
            # print(r.text)
        except:
            # behind proxy, corrupt message, etc
            # print("failed",r.text)
            return
    def getSpace(self):
        try:
            # {'key':self.key,'code':idcode.text(),'phone':pnumber.text()}
            # data = {'token':self.prof['token']}
            headers = {"Content-Type": "application/json"}
            headers["Authorization"] = _("Bearer %s"%self.mw.pm.profile['token'])
            # auth = {'Content-Type':'application/json'},data = data
            r = requests.get('',headers=headers)
            resp = r.json()
            # print(r.status_code)
            if(resp['status_code'] != 0):
                self.cloudSpaceReal = 0
                aqt.cloudSpace = '0'
                aqt.localSpace = '0'
                return
            aqt.cloudSpace = resp["data"]["size"]
            aqt.localSpace = resp["data"]["used_size"]
            self.cloudSpaceReal = float(resp["data"]["origin_size"])
            aqt.cloudTotalSpace = self.cloudSpaceReal
            # aqt.cloudTotalSpace = 120586240
            aqt.cloudUsedSpace = float(resp["data"]["origin_used_size"])
            # print(r.text)
        except:
            self.cloudSpaceReal = 0
            aqt.cloudSpace = '0'
            aqt.localSpace = '0'
            # behind proxy, corrupt message, etc
            # print("failed")
            return
    def _renderDeckTree(self, nodes, depth=0):
        if not nodes:
            return ""
        if depth == 0:
            buf = """
<tr><th colspan=5 align=left>%s</th><th class=count>%s</th>
<th class=count>%s</th><th class=optscol></th></tr>""" % (
            _("Deck"), _("Due"), _("New"))
            buf += self._topLevelDragRow()
        else:
            buf = ""
        nameMap = self.mw.col.decks.nameMap()
        for node in nodes:
            buf += self._deckRow(node, depth, len(nodes), nameMap)
        if depth == 0:
            buf += self._topLevelDragRow()
        return buf

    def _deckRow(self, node, depth, cnt, nameMap):
        name, did, due, lrn, new, children = node
        deck = self.mw.col.decks.get(did)
        if did == 1 and cnt > 1 and not children:
            # if the default deck is empty, hide it
            if not self.mw.col.db.scalar("select 1 from cards where did = 1"):
                return ""
        # parent toggled for collapsing
        for parent in self.mw.col.decks.parents(did, nameMap):
            if parent['collapsed']:
                buff = ""
                return buff
        prefix = "-"
        if self.mw.col.decks.get(did)['collapsed']:
            prefix = "+"
        due += lrn
        def indent():
            return "&nbsp;"*6*depth
        if did == self.mw.col.conf['curDeck']:
            klass = 'deck current'
        else:
            klass = 'deck'
        buf = "<tr class='%s' id='%d'>" % (klass, did)
        # deck link
        if children:
            collapse = "<a class=collapse href=# onclick='return pycmd(\"collapse:%d\")'>%s</a>" % (did, prefix)
        else:
            collapse = "<span class=collapse></span>"
        if deck['dyn']:
            extraclass = "filtered"
        else:
            extraclass = ""
        buf += """

        <td class=decktd colspan=5>%s%s<a class="deck %s"
        href=# onclick="return pycmd('open:%d')">%s</a></td>"""% (
            indent(), collapse, extraclass, did, name)
        # due counts
        def nonzeroColour(cnt, colour):
            if not cnt:
                colour = "#e0e0e0"
            if cnt >= 1000:
                cnt = "1000+"
            return "<font color='%s'>%s</font>" % (colour, cnt)
        buf += "<td align=right>%s</td><td align=right>%s</td>" % (
            nonzeroColour(due, "#007700"),
            nonzeroColour(new, "#000099"))
        # options
        buf += ("<td align=center class=opts><a onclick='return pycmd(\"opts:%d\");'>"
        "<img src='/_anki/imgs/gears.svg' class=gears></a></td></tr>" % did)
        # children
        buf += self._renderDeckTree(children, depth+1)
        return buf

    def _topLevelDragRow(self):
        return "<tr class='top-level-drag-row'><td colspan='6'>&nbsp;</td></tr>"

    # Options
    ##########################################################################

    def _showOptions(self, did):
        m = QMenu(self.mw)
        a = m.addAction(_("Rename"))
        a.triggered.connect(lambda b, did=did: self._rename(did))
        a = m.addAction(_("Options"))
        a.triggered.connect(lambda b, did=did: self._options(did))
        a = m.addAction(_("Export"))
        a.triggered.connect(lambda b, did=did: self._export(did))
        a = m.addAction(_("Delete"))
        a.triggered.connect(lambda b, did=did: self._delete(did))
        runHook("showDeckOptions", m, did)
        m.exec_(QCursor.pos())

    def _export(self, did):
        self.mw.onExport(did=did)

    def _rename(self, did):
        self.mw.checkpoint(_("Rename Deck"))
        deck = self.mw.col.decks.get(did)
        oldName = deck['name']
        newName = getOnlyText(_("New deck name:"), default=oldName)
        newName = newName.replace('"', "")
        if not newName or newName == oldName:
            return
        try:
            self.mw.col.decks.rename(deck, newName)
        except DeckRenameError as e:
            return showWarning(e.description)
        self.show()

    def _options(self, did):
        # select the deck first, because the dyn deck conf assumes the deck
        # we're editing is the current one
        self.mw.col.decks.select(did)
        self.mw.onDeckConf()

    def _collapse(self, did):
        self.mw.col.decks.collapse(did)
        self._renderPage(reuse=True)

    def _dragDeckOnto(self, draggedDeckDid, ontoDeckDid):
        try:
            self.mw.col.decks.renameForDragAndDrop(draggedDeckDid, ontoDeckDid)
        except DeckRenameError as e:
            return showWarning(e.description)

        self.show()

    def _delete(self, did):
        if str(did) == '1':
            return showWarning(_("The default deck can't be deleted."))
        self.mw.checkpoint(_("Delete Deck"))
        deck = self.mw.col.decks.get(did)
        if not deck['dyn']:
            dids = [did] + [r[1] for r in self.mw.col.decks.children(did)]
            cnt = self.mw.col.db.scalar(
                "select count() from cards where did in {0} or "
                "odid in {0}".format(ids2str(dids)))
            if cnt:
                extra = ngettext(" It has %d card.", " It has %d cards.", cnt) % cnt
            else:
                extra = None
        if deck['dyn'] or not extra or askUser(
            (_("Are you sure you wish to delete %s?") % deck['name']) +
            extra):
            self.mw.progress.start(immediate=True)
            self.mw.col.decks.rem(did, True)
            self.mw.progress.finish()
            self.show()

    # Top buttons
    ######################################################################

    # drawLinks = [
    #         ["", "course", _(self.courseText)],
    #         ["", "shared", _("Get Shared")],
    #         ["", "create", _("Create Deck")],
    #         ["Ctrl+I", "import", _("Import File")],  # Ctrl+I works from menu
    # ]

    # drawLinks2 = [
    #     ["", self.supportUrl, 2, _(self.supportText)],
    #     ["", self.wechatUrl, 2, _(self.wechatText)],
    #     ["", self.suggestUrl, 2, _(self.suggestText)],
    # ]

    def _drawButtons(self):
        buf = ""

        drawLinks = []
        drawLinks.append(["", "course", _(self.courseText)])
        drawLinks.append(["", "shared", _("Get Shared")])
        drawLinks.append(["", "create", _("Create Deck")])
        drawLinks.append(["Ctrl+I", "import", _("Import File")])
        # drawLinks = deepcopy(drawLinks)
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        for b in drawLinks:
            if b[0]:
                b[0] = _("Shortcut key: %s") % shortcut(b[0])
            buf += """
<button title='%s' onclick='pycmd(\"%s\");'>%s</button>""" % tuple(b)
        drawLinks2 = []
        drawLinks2.append(["", self.supportUrl, 2, _(self.supportText)])
        drawLinks2.append(["", self.wechatUrl, 2, _(self.wechatText)])
        drawLinks2.append(["", self.suggestUrl, 2, _(self.suggestText)])

        # drawLinks2 = deepcopy(self.drawLinks2)
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        # buf += """&nbsp;&nbsp;&nbsp;"""
        for b2 in drawLinks2:
            buf += """&nbsp;&nbsp;&nbsp;"""
            buf += """
                    <label title='%s'><a href=\"%s\"><font size=%d>%s</font></a></label>""" % tuple(
                b2
            )
        self.bottom.draw(buf)
        self.bottom.web.onBridgeCmd = self._linkHandler

    def _onShared(self):
        openLink(aqt.appShared+"decks/")

    def _onCourse(self):
        openLink(self.courseUrl)