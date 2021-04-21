# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import time
import gc

import aqt
import requests
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox
from aqt.qt import *
from anki import Collection
from anki.sync import Syncer, RemoteServer, FullSyncer, MediaSyncer, \
    RemoteMediaServer
from anki.hooks import addHook, remHook
from aqt.utils import tooltip, askUserDialog, showWarning, showText, showInfo
from anki.lang import _
from aqt.deckbrowser import WebViewPay

# Sync manager
######################################################################

class SyncManager(QObject):

    def __init__(self, mw, pm):
        QObject.__init__(self, mw)
        self.mw = mw
        self.pm = pm
        self._cloudFlg = False

    def sync(self):
        if not self.pm.profile['syncKey']:
            auth = self._getUserPass()
            if not auth:
                return
            self.pm.profile['syncUser'] = auth[0]
            self._sync(auth)
        else:
            self._sync()

    def _sync(self, auth=None):
        # Todo
        if not self._getCloudMemory():
            return
        # to avoid gui widgets being garbage collected in the worker thread,
        # run gc in advance
        self._didFullUp = False
        self._didError = False
        gc.collect()
        # create the thread, setup signals and start running
        t = self.thread = SyncThread(
            self.pm.collectionPath(), self.pm.profile['syncKey'],
            auth=auth, media=self.pm.profile['syncMedia'],
            hostNum=self.pm.profile.get("hostNum"),
        )
        t.event.connect(self.onEvent)
        self.label = _("Connecting...")
        prog = self.mw.progress.start(immediate=True, label=self.label)
        self.sentBytes = self.recvBytes = 0
        self._updateLabel()
        self.thread.start()
        while not self.thread.isFinished():
            if prog.wantCancel:
                self.thread.flagAbort()
                # make sure we don't display 'upload success' msg
                self._didFullUp = False
                # abort may take a while
                self.mw.progress.update(_("Stopping..."))
            self.mw.app.processEvents()
            self.thread.wait(100)
        self.mw.progress.finish()
        
        if self._cloudFlg:
            self._cloudFlg = False
            self._getNoCloudWindow()
        if self.thread.syncMsg:
            showText(self.thread.syncMsg)
        if self.thread.uname:
            self.pm.profile['syncUser'] = self.thread.uname
        self.pm.profile['hostNum'] = self.thread.hostNum
        def delayedInfo():
            if self._didFullUp and not self._didError:
                showInfo(_("""\
Your collection was successfully uploaded to AnkiWeb.

If you use any other devices, please sync them now, and choose \
to download the collection you have just uploaded from this computer. \
After doing so, future reviews and added cards will be merged \
automatically."""))
        self.mw.progress.timer(1000, delayedInfo, False, requiresCollection=False)

    def _updateLabel(self):
        # todo mark
        print(self.sentBytes, self.recvBytes)
        self.mw.progress.update(label="%s\n%s" % (
            self.label,
            _("%(a)0.1fkB up, %(b)0.1fkB down") % dict(
                a=self.sentBytes / 1024,
                b=self.recvBytes / 1024)))

    def onEvent(self, evt, *args):
        pu = self.mw.progress.update
        if evt == "badAuth":
            tooltip(
                _("AnkiWeb ID or password was incorrect; please try again."),
                parent=self.mw)
            # blank the key so we prompt user again
            self.pm.profile['syncKey'] = None
            self.pm.save()
        elif evt == "corrupt":
            pass
        elif evt == "newKey":
            self.pm.profile['syncKey'] = args[0]
            self.pm.save()
        elif evt == "offline":
            tooltip(_("Syncing failed; internet offline."))
        elif evt == "upbad":
            self._didFullUp = False
            self._checkFailed()
        elif evt == "sync":
            m = None; t = args[0]
            if t == "login":
                m = _("Syncing...")
            elif t == "upload":
                self._didFullUp = True
                m = _("Uploading to AnkiWeb...")
            elif t == "download":
                m = _("Downloading from AnkiWeb...")
            elif t == "sanity":
                m = _("Checking...")
            elif t == "findMedia":
                m = _("Checking media...")
            elif t == "upgradeRequired":
                showText(_("""\
Please visit AnkiWeb, upgrade your deck, then try again."""))
            if m:
                self.label = m
                self._updateLabel()
        elif evt == "syncMsg":
            self.label = args[0]
            self._updateLabel()
        elif evt == "error":
            self._didError = True
            showText(_("Syncing failed:\n%s")%
                     self._rewriteError(args[0]))
        elif evt == "clockOff":
            self._clockOff()
        elif evt == "checkFailed":
            self._checkFailed()
        elif evt == "mediaSanity":
            showWarning(_("""\
A problem occurred while syncing media. Please use Tools>Check Media, then \
sync again to correct the issue."""))
        elif evt == "noChanges":
            pass
        elif evt == "fullSync":
            self._confirmFullSync()
        elif evt == "downloadClobber":
            showInfo(_("Your AnkiWeb collection does not contain any cards. Please sync again and choose 'Upload' instead."))
        elif evt == "send":
            # posted events not guaranteed to arrive in order
            self.sentBytes = max(self.sentBytes, int(args[0]))
            self._updateLabel()
        elif evt == "recv":
            self.recvBytes = max(self.recvBytes, int(args[0]))
            self._updateLabel()
        elif evt == "noSize":
            self._cloudFlg =True
            print(evt)
            # self.mw.progress.finish()
            # self._getNoCloudWindow()
    def _rewriteError(self, err):
        if "Errno 61" in err:
            return _("""\
Couldn't connect to AnkiWeb. Please check your network connection \
and try again.""")
        elif "timed out" in err or "10060" in err:
            return _("""\
The connection to AnkiWeb timed out. Please check your network \
connection and try again.""")
        elif "code: 500" in err:
            return _("""\
AnkiWeb encountered an error. Please try again in a few minutes, and if \
the problem persists, please file a bug report.""")
        elif "code: 501" in err:
            return _("""\
Please upgrade to the latest version of Anki.""")
        # 502 is technically due to the server restarting, but we reuse the
        # error message
        elif "code: 502" in err:
            return _("AnkiWeb is under maintenance. Please try again in a few minutes.")
        elif "code: 503" in err:
            return _("""\
AnkiWeb is too busy at the moment. Please try again in a few minutes.""")
        elif "code: 504" in err:
            return _("504 gateway timeout error received. Please try temporarily disabling your antivirus.")
        elif "code: 409" in err:
            return _("Only one client can access AnkiWeb at a time. If a previous sync failed, please try again in a few minutes.")
        elif "10061" in err or "10013" in err or "10053" in err:
            return _(
                "Antivirus or firewall software is preventing Anki from connecting to the internet.")
        elif "10054" in err or "Broken pipe" in err:
            return _("Connection timed out. Either your internet connection is experiencing problems, or you have a very large file in your media folder.")
        elif "Unable to find the server" in err or "socket.gaierror" in err:
            return _(
                "Server not found. Either your connection is down, or antivirus/firewall "
                "software is blocking Anki from connecting to the internet.")
        elif "code: 407" in err:
            return _("Proxy authentication required.")
        elif "code: 413" in err:
            return _("Your collection or a media file is too large to sync.")
        elif "EOF occurred in violation of protocol" in err:
            return _("Error establishing a secure connection. This is usually caused by antivirus, firewall or VPN software, or problems with your ISP.") + " (eof)"
        elif "certificate verify failed" in err:
            return _("Error establishing a secure connection. This is usually caused by antivirus, firewall or VPN software, or problems with your ISP.") + " (invalid cert)"
        return err

    def _getUserPass(self):
        def getIDCode():
            if len(pnumber.text()) < 11:
                tooltip('请输入正确手机号码', period=2000)
                # QMessageBox.about(self.mw, "警告", "请输入正确手机号码")
                return
            # Todo
            # d = self._data()
            phoneNumber = {'phone':pnumber.text()}
            # phoneNumber = "{\n    \"phone\": \"%s\" \n}"%(pnumber.text())
            # phoneNumber = {'phone':pnumber.text()}
            import json
            j = json.dumps(phoneNumber)
            # 请求数据可以作为例子
            try:
                # Todo
                # 请求数据可以作为例子
                # headers = {"Accept": "application/json","Content-Type": "application/json"}
                r = requests.post(aqt.verificationCodeUrl,headers = {"Accept": "application/json","Content-Type": "application/json"}, data=j)
                # r = requests.post(aqt.verificationCodeUrl,headers=headers, data=phoneNumber)
                # print(r.url)
                # print(r.text)

                resp = r.json()
                if(resp['status_code'] != 0):
                    tooltip(resp['message'], period=2000)
                    return
                self.key = resp['data']['key']
            except:
                # behind proxy, corrupt message, etc
                tooltip('无网络，请检查网络后重试', period=2000)

                return
            self.waittime = 120
            getbtn.setEnabled(False)
            getbtn.setText("重新获取%dS" % (self.waittime))
            wtimer.start(1000)



            # resp = r.json()
            # Todo Http请求获取验证码
            
        def btnRefresh():
            if self.waittime:
                self.waittime -= 1
                getbtn.setText("重新获取%dS" % (self.waittime))
            else:
                getbtn.setEnabled(True)
                getbtn.setText("获取验证码")
                wtimer.stop()
        def Action():
            if len(pnumber.text()) < 11:
                tooltip('请输入正确手机号码', period=2000)
                # QMessageBox.about(self.mw, "警告", "请输入正确手机号码")
                return
            data = {'key':self.key,'code':idcode.text(),'phone':pnumber.text()}

            # 请求数据可以作为例子
            try:
                # Todo
                # 请求数据可以作为例子
                headers = {"Accept": "application/json","Content-Type": "application/json"}
                import json
                j = json.dumps(data)
                # r = requests.post(aqt.verificationCodeUrl,headers = {'Accept':'application/json','Content-Type': 'application/json'}, data=phoneNumber)
                r = requests.post('',headers=headers, data=j)
                # r.raise_for_status()
                # {"status_code":422,"message":"\u624b\u673a\u53f7\u7801\u4e0d\u80fd\u4e3a\u7a7a","data":[]}
                resp = r.json()
                # if(resp['message'] == '手机号码格式不对'):
                if(resp['status_code'] != 0):
                    tooltip(resp['message'], period=2000)
                    # QMessageBox.about(self.mw, "警告", resp['message'])
                    return
                # if(resp['status_code'] == 422):
                #     QMessageBox.about(self.mw, "警告", "请输入正确手机号码")
                #     return
                # elif(resp['status_code'] == 403):
                #     QMessageBox.about(self.mw, "警告", "验证码失效")
                # key = resp['data']['key']
                self.u = resp['data']['anki_username']
                self.p = resp['data']['anki_password']
                self.pm.profile['token'] = resp['data']['meta']['token']
                d.done(1)
                d.close()
                # self.pm.profile['syncKey'] = resp['data']['key']
            except:
                tooltip(_("无网络，请检查网络后重试"), period=1000)
                # behind proxy, corrupt message, etc
                # QMessageBox.about(self.mw, "警告", "无网络，请检查网络后重试")
                # print("update check failed")
                return
        def onChangeIDCode():
            if len(idcode.text()) >5:
                bb.button(QDialogButtonBox.Ok).setEnabled(True)
            else:
                bb.button(QDialogButtonBox.Ok).setEnabled(False)
        self.key = ''
        d = QDialog(self.mw,Qt.WindowCloseButtonHint)
        d.setWindowTitle("Anki")
        d.setWindowModality(Qt.WindowModal)
        vbox = QVBoxLayout()
        l = QLabel(
            _(
                """\
<h1>手机号登陆</h1>
ANKI中国已改用国内服务器，同步ANKI资料将更加稳定、快速，请输入你的手机号完成登录或注册。\
<br>\
<font color="gray">因为ANKI IOS版本未开源，所以同步功能目前仅限MAC版、Windows版和Android版之间同步，\
IOS版的同步我们也在考虑方案中，但还需要一定的时间。</font>"""
            )
        )
        self.u = ''
        self.p = ''
        # p = None
        l.setOpenExternalLinks(True)
        l.setWordWrap(True)
        vbox.addWidget(l)
        vbox.addSpacing(20)
        g = QGridLayout()
        pnumber = QLineEdit()
        # self._pnumber = pnumber
        pnumber.setPlaceholderText("输入手机号")
        pnumber.setMaxLength(11)
        pnumber.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[0-9]+$')))
        g.addWidget(pnumber, 0, 0)
        idcode = QLineEdit()
        idcode.setMaxLength(8)
        idcode.setPlaceholderText("验证码")
        idcode.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('^[A-Za-z0-9]+$')))
        idcode.textEdited[str].connect(lambda :onChangeIDCode())
        g.addWidget(idcode, 1, 0)
        getbtn = QPushButton("获取验证码")
        getbtn.clicked.connect(getIDCode)
        wtimer = QTimer()
        wtimer.timeout.connect(btnRefresh)
        g.addWidget(getbtn, 1, 1)
        vbox.addLayout(g)
        # bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb = QDialogButtonBox(QDialogButtonBox.Ok)
        bb.button(QDialogButtonBox.Ok).setAutoDefault(True)
        bb.button(QDialogButtonBox.Ok).setText("登录")
        bb.button(QDialogButtonBox.Ok).clicked.connect(Action)
        bb.button(QDialogButtonBox.Ok).setEnabled(False)
        # bb.accepted.connect(d.accept)
        bb.rejected.connect(d.reject)
        vbox.addWidget(bb)
        d.setLayout(vbox)
        d.show()
        accepted = d.exec_()
        wtimer.stop()
        # u = pnumber.text()
        # p = idcode.text()
        u = self.u
        p = self.p
        #  todo 等待修复
        # u = 'zhangsan'
        # p = 'zhangsan'
        if not accepted or not u or not p:
            return
        return (u, p)

    def _getCloudMemory(self):
        self.mw.deckBrowser.updateLocalDataSize()
        self.mw.deckBrowser.getSpace()

        # if ((self.mw.deckBrowser.cloudSpaceReal - self.pm.getLocalDataSize()) > 0) or self.mw.deckBrowser.cloudSpaceReal == 0 :
        if True:
            return True
        # else:
            # def getUpdate():
            #     self.web = WebViewPay(self.mw.deckBrowser)
            #     d.close()
            # # self.web = WebViewPay(self.mw.deckBrowser)
            # d = QDialog(self.mw)
            # d.setWindowTitle("Tip")
            # vbox = QVBoxLayout()
            # ml = QLabel(_("""<font size = 5><strong>你的云空间不足，请升级！</strong></font>"""))
            # vbox.addWidget(ml)
            # vbox.setSpacing(30)
            # upbtn = QPushButton("去升级")
            # upbtn.clicked.connect(getUpdate)
            # upbtn.setFocusPolicy(QtCore.Qt.NoFocus)
            # vbox.addWidget(upbtn)
            # d.setLayout(vbox)
            # d.show()
            # d.exec_()
        return False

    def _getNoCloudWindow(self):
        def getUpdate():
            self.web = WebViewPay(self.mw.deckBrowser)
            d.close()
        # self.web = WebViewPay(self.mw.deckBrowser)
        d = QDialog(self.mw)
        d.setWindowTitle("Tip")
        d.resize(320,170)
        vbox = QVBoxLayout()


        upLoadStr = ''
        renSizeStr = ''
        if aqt.upLoadSize/1024.0*1024.0 < 0.1:
            upLoadStr = _("""%0.2fKB""")%(aqt.upLoadSize/1024)
        elif aqt.upLoadSize/(1024.0*1024.0*1024.0) < 0.1:
            upLoadStr = _("""%0.2fMB""")%(aqt.upLoadSize/(1024.0*1024.0))
        else:
            upLoadStr = _("""%0.2fGB""")%(aqt.upLoadSize/(1024.0*1024.0*1024.0))

        renSize = aqt.cloudTotalSpace-aqt.cloudUsedSpace
        if renSize/1024.0*1024.0 < 0.1:
            renSizeStr = _("""%0.2fKB""")%(renSize/1024)
        elif renSize/(1024.0*1024.0*1024.0) < 0.1:
            renSizeStr = _("""%0.2fMB""")%(renSize/(1024.0*1024.0))
        else:
            renSizeStr = _("""%0.2fGB""")%(renSize/(1024.0*1024.0*1024.0))
        ml = QLabel(
            _(
                """\
<font size = 5><strong>你的云空间不足，请升级！</strong></font>
<br>\
<br>\
本次要上传%s，云空间剩余%s,\
请升级到更高的容量，再进行同步！
"""
            )%(upLoadStr,renSizeStr)
        )
        ml.setWordWrap(True)
        # ml = QLabel(_("""<font size = 5><strong>你的云空间不足，请升级！</strong></font>"""))
        vbox.addWidget(ml)
        vbox.setSpacing(30)
        upbtn = QPushButton("去升级")
        upbtn.clicked.connect(getUpdate)
        upbtn.setFocusPolicy(QtCore.Qt.NoFocus)
        vbox.addWidget(upbtn)
        d.setLayout(vbox)
        d.show()
        d.exec_()
    def _confirmFullSync(self):
        self.mw.progress.finish()
        if self.thread.localIsEmpty:
            diag = askUserDialog(
                _("Local collection has no cards. Download from AnkiWeb?"),
                [_("Download from AnkiWeb"), _("Cancel")])
            diag.setDefault(1)
        else:
            diag = askUserDialog(_("""\
Your decks here and on AnkiWeb differ in such a way that they can't \
be merged together, so it's necessary to overwrite the decks on one \
side with the decks from the other.

If you choose download, Anki will download the collection from AnkiWeb, \
and any changes you have made on your computer since the last sync will \
be lost.

If you choose upload, Anki will upload your collection to AnkiWeb, and \
any changes you have made on AnkiWeb or your other devices since the \
last sync to this device will be lost.

After all devices are in sync, future reviews and added cards can be merged \
automatically."""),
                [_("Upload to AnkiWeb"),
                 _("Download from AnkiWeb"),
                 _("Cancel")])
            diag.setDefault(2)
        ret = diag.run()
        if ret == _("Upload to AnkiWeb"):
            # todo 增加检查云空间逻辑
            self.thread.fullSyncChoice = "upload"
        elif ret == _("Download from AnkiWeb"):
            self.thread.fullSyncChoice = "download"
        else:
            self.thread.fullSyncChoice = "cancel"
        self.mw.progress.start(immediate=True)

    def _clockOff(self):
        showWarning(_("""\
Syncing requires the clock on your computer to be set correctly. Please \
fix the clock and try again."""))

    def _checkFailed(self):
        showWarning(_("""\
Your collection is in an inconsistent state. Please run Tools>\
Check Database, then sync again."""))

# Sync thread
######################################################################

class SyncThread(QThread):

    event = pyqtSignal(str, str)

    def __init__(self, path, hkey, auth=None, media=True, hostNum=None):
        QThread.__init__(self)
        self.path = path
        self.hkey = hkey
        self.auth = auth
        self.media = media
        self.hostNum = hostNum
        self._abort = 0 # 1=flagged, 2=aborting

    def flagAbort(self):
        self._abort = 1

    def run(self):
        # init this first so an early crash doesn't cause an error
        # in the main thread
        self.syncMsg = ""
        self.uname = ""
        try:
            self.col = Collection(self.path, log=True)
        except:
            self.fireEvent("corrupt")
            return
        self.server = RemoteServer(self.hkey, hostNum=self.hostNum)
        self.client = Syncer(self.col, self.server)
        self.sentTotal = 0
        self.recvTotal = 0
        def syncEvent(type):
            self.fireEvent("sync", type)
        def syncMsg(msg):
            self.fireEvent("syncMsg", msg)
        def sendEvent(bytes):
            if not self._abort:
                self.sentTotal += bytes
                self.fireEvent("send", str(self.sentTotal))
            elif self._abort == 1:
                self._abort = 2
                raise Exception("sync cancelled")
        def recvEvent(bytes):
            if not self._abort:
                self.recvTotal += bytes
                self.fireEvent("recv", str(self.recvTotal))
            elif self._abort == 1:
                self._abort = 2
                raise Exception("sync cancelled")
        addHook("sync", syncEvent)
        addHook("syncMsg", syncMsg)
        addHook("httpSend", sendEvent)
        addHook("httpRecv", recvEvent)
        # run sync and catch any errors
        try:
            self._sync()
        except:
            err = traceback.format_exc()
            self.fireEvent("error", err)
        finally:
            # don't bump mod time unless we explicitly save
            self.col.close(save=False)
            remHook("sync", syncEvent)
            remHook("syncMsg", syncMsg)
            remHook("httpSend", sendEvent)
            remHook("httpRecv", recvEvent)

    def _abortingSync(self):
        # todo 同步处理的核新
        try:
            return self.client.sync()
        except Exception as e:
            if "sync cancelled" in str(e):
                self.server.abort()
                raise
            else:
                raise

    def _sync(self):
        # mark Todo 登录
        if self.auth:
            # need to authenticate and obtain host key
            self.hkey = self.server.hostKey(*self.auth)
            if not self.hkey:
                # provided details were invalid
                return self.fireEvent("badAuth")
            else:
                # write new details and tell calling thread to save
                self.fireEvent("newKey", self.hkey)
        # run sync and check state
        try:
            ret = self._abortingSync()
        except Exception as e:
            log = traceback.format_exc()
            err = repr(str(e))
            if ("Unable to find the server" in err or
                "Errno 2" in err or "getaddrinfo" in err):
                self.fireEvent("offline")
            elif "sync cancelled" in err:
                pass
            elif "No cloud memory" in err:
                self.fireEvent("noSize")
                print('No cloud memory')
            else:
                self.fireEvent("error", log)
            return
        if ret == "badAuth":
            return self.fireEvent("badAuth")
        elif ret == "clockOff":
            return self.fireEvent("clockOff")
        elif ret == "basicCheckFailed" or ret == "sanityCheckFailed":
            return self.fireEvent("checkFailed")
        # full sync?
        if ret == "fullSync":
            return self._fullSync()
        # save and note success state
        if ret == "noChanges":
            self.fireEvent("noChanges")
        elif ret == "success":
            self.fireEvent("success")
        elif ret == "serverAbort":
            self.syncMsg = self.client.syncMsg
            return
        else:
            self.fireEvent("error", "Unknown sync return code.")
        self.syncMsg = self.client.syncMsg
        self.uname = self.client.uname
        self.hostNum = self.client.hostNum
        # then move on to media sync
        self._syncMedia()

    def _fullSync(self):
        # tell the calling thread we need a decision on sync direction, and
        # wait for a reply
        self.fullSyncChoice = False
        self.localIsEmpty = self.col.isEmpty()
        self.fireEvent("fullSync")
        while not self.fullSyncChoice:
            time.sleep(0.1)
        f = self.fullSyncChoice
        if f == "cancel":
            return
        self.client = FullSyncer(self.col, self.hkey, self.server.client,
                                 hostNum=self.hostNum)
        try:
            if f == "upload":
                if not self.client.upload():
                    self.fireEvent("upbad")
            else:
                ret = self.client.download()
                if ret == "downloadClobber":
                    self.fireEvent(ret)
                    return
        except Exception as e:
            if "sync cancelled" in str(e):
                return
            raise
        # reopen db and move on to media sync
        self.col.reopen()
        self._syncMedia()

    def _syncMedia(self):
        if not self.media:
            return
        self.server = RemoteMediaServer(self.col, self.hkey, self.server.client,
                                        hostNum=self.hostNum)
        self.client = MediaSyncer(self.col, self.server)
        try:
            ret = self.client.sync()
        except Exception as e:
            if "sync cancelled" in str(e):
                return
            elif "No cloud memory" in str(e):
                self.fireEvent("noSize")
                print('No cloud memory')
                return
            raise
        if ret == "noChanges":
            self.fireEvent("noMediaChanges")
        elif ret == "sanityCheckFailed" or ret == "corruptMediaDB":
            self.fireEvent("mediaSanity")
        else:
            self.fireEvent("mediaSuccess")

    def fireEvent(self, cmd, arg=""):
        self.event.emit(cmd, arg)


