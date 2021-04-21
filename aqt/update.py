# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import time

import requests
from PyQt5 import QtCore

from aqt.qt import *
import aqt
from aqt.utils import openLink, showText
from anki.utils import getCurrentTime
from anki.utils import platDesc, versionWithBuild
from anki.lang import _


class LatestVersionFinder(QThread):

    newVerAvail = pyqtSignal(str)
    newMsg = pyqtSignal(dict)
    clockIsOff = pyqtSignal(float)
    forceUpdate = pyqtSignal(bool)

    def __init__(self, main):
        QThread.__init__(self)
        self.main = main
        self.config = main.pm.meta

    def _data(self):
        d = {"ver": versionWithBuild(),
             "os": platDesc(),
             "id": self.config['id'],
             "lm": self.config['lastMsg'],
             "crt": self.config['created']}
        return d

    def run(self):
        if not self.config['updates']:
            return
        d = self._data()
        d['proto'] = 1
        time.sleep(6)
        try:
            # Todo
            # 请求数据可以作为例子
            # r = requests.post(aqt.appUpdate, data=d)

            if isWin:
                r = requests.get('')
            elif isMac:
                r = requests.get('')

            # r.raise_for_status()
            # print(r.text)
            resp = r.json()
            # title = resp['data']['title']
            # description = resp['data']['description']
            # download_url = resp['data']['download_url']
        except:
            # behind proxy, corrupt message, etc
            # print("update check failed")
            return
        resp['ver'] = '2.1.1.1'
        # if resp['msg']:
        self.newMsg.emit(resp)
        # if resp['ver']:
        #     self.newVerAvail.emit(resp['ver'])
        resp['ver'] = '2.1.1.1'
        # self.newVerAvail.emit(resp['ver'])
        # 强制更新状态
        # if resp['foreceUpdate']:
        #     self.forceUpdate.emit(resp['ver'])
        # diff = resp['time'] - time.time()
        # if abs(diff) > 300:
        #     self.clockIsOff.emit(diff)



def askAndUpdate(mw, data):
    def onAction( ):
        if typeLoc == "N":
            # pass
            openLink(download_url)
            d.close()
            d.done(1)
        else:
            openLink(download_url)
            d.close()
            mw.close()


    currentTime = getCurrentTime()

    try:
        if 'data' in data:
            if 'type' in data['data']:
                typeLoc = data['data']['type']
                # return 
                # d = QDialog(self,(Qt.WindowFlags())&(~(Qt.WindowCloseButtonHint|Qt.WindowSystemMenuHint)))
                if data['data']['type'] == "F":
                    # 带关闭按钮的
                    d = QDialog(mw,Qt.CustomizeWindowHint)
                    d.setWindowTitle("Tip")
                else:
                    if currentTime - mw.pm.meta['updataTime'] < 7*24*60*60:
                        return
                    d = QDialog(mw,Qt.WindowCloseButtonHint)
                    d.setWindowTitle("Tip")
            else:
                return
    except:
        return

    # 不带关闭按钮的
    # Todo
    # d = QDialog(self,Qt.CustomizeWindowHint)
    
    # d.setWindowFlags(QtCore.Qt.WindowCloseButtonHint|QtCore.Qt.WindowStaysOnTopHint)
    vbox = QVBoxLayout()
    vbox.setSpacing(30)
    hlabel = QLabel(_("""<h2>%s</h2>""")%data['data']['title'])
    hlabel.setAlignment(Qt.AlignCenter)
    vbox.addWidget(hlabel)

    baseStr =  _('''%s'''%data['data']['description']) 
    clabel = QLabel(baseStr)
    clabel.setAlignment(Qt.AlignLeft)
    vbox.addWidget(clabel)
    upbtn = QPushButton("立即更新")
    upbtn.setFocusPolicy(Qt.NoFocus)
    upbtn.clicked.connect(onAction)
    download_url = data['data']['download_url']
    # upbtn.acc
    vbox.addWidget(upbtn)
    d.setLayout(vbox)
    # 设定为置顶
    d.setModal(True)
    d.show()
    # self.setDisabled(True)
    # self.app.setD
    accept = d.exec_()
    
    if not accept:
        # 提示七天后不显示
        mw.pm.meta['updataTime'] = currentTime
        # print(currentTime)
    # baseStr = (
    #     _('''<h1>Anki Updated</h1>Anki %s has been released.<br><br>''') %
    #     ver)
    # baseStr = (
    #     _('''<h1>%s</h1><br><br> %s''') %
    #     (title,description))
    # msg = QMessageBox(mw)
    # msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    # msg.setIcon(QMessageBox.Information)
    # msg.setText(baseStr)

    
    # button = QPushButton(_("Ignore this update"))
    # msg.addButton(button, QMessageBox.RejectRole)
    # msg.setDefaultButton(QMessageBox.Yes)
    
    # bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    # bb.button(QDialogButtonBox.Ok).setAutoDefault(True)
    # bb.button(QDialogButtonBox.Ok).setText("Log in")
    # # bb.button(QDialogButtonBox.Ok).clicked.connect(Action)

    # ret = msg.exec_()
    # if msg.clickedButton() == button:
    #     # ignore this update
    #     mw.pm.meta['suppressUpdate'] = ver
    # elif ret == QMessageBox.Yes:
    #     # openLink(aqt.appWebsite)
    #     openLink(download_url)

def showMessages(mw, data):
    showText(data['msg'], parent=mw, type="html")
    mw.pm.meta['lastMsg'] = data['msgId']
