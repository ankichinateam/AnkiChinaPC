# -*- coding: utf-8 -*-
# pylint: disable=unsubscriptable-object,unused-import
from anki.lang import _
# Form implementation generated from reading ui file 'designer/profiles.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(423, 356)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/anki.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.profiles = QtWidgets.QListWidget(self.centralwidget)
        self.profiles.setObjectName("profiles")
        self.verticalLayout_2.addWidget(self.profiles)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.login = QtWidgets.QPushButton(self.centralwidget)
        self.login.setDefault(True)
        self.login.setObjectName("login")
        self.verticalLayout.addWidget(self.login)
        self.add = QtWidgets.QPushButton(self.centralwidget)
        self.add.setObjectName("add")
        self.verticalLayout.addWidget(self.add)
        self.rename = QtWidgets.QPushButton(self.centralwidget)
        self.rename.setObjectName("rename")
        self.verticalLayout.addWidget(self.rename)
        self.delete_2 = QtWidgets.QPushButton(self.centralwidget)
        self.delete_2.setObjectName("delete_2")
        self.verticalLayout.addWidget(self.delete_2)
        self.quit = QtWidgets.QPushButton(self.centralwidget)
        self.quit.setObjectName("quit")
        self.verticalLayout.addWidget(self.quit)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.openBackup = QtWidgets.QPushButton(self.centralwidget)
        self.openBackup.setObjectName("openBackup")
        self.verticalLayout.addWidget(self.openBackup)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setEnabled(False)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 423, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setEnabled(False)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_("Profiles"))
        self.login.setText(_("Open"))
        self.add.setText(_("Add"))
        self.rename.setText(_("Rename"))
        self.delete_2.setText(_("Delete"))
        self.quit.setText(_("Quit"))
        self.openBackup.setText(_("Open Backup..."))
from . import icons_rc
