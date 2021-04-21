# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './settings_shortcut.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 203)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label)
        self.cb_ctrl = QtWidgets.QCheckBox(Dialog)
        self.cb_ctrl.setObjectName("cb_ctrl")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.cb_ctrl)
        self.cb_shift = QtWidgets.QCheckBox(Dialog)
        self.cb_shift.setObjectName("cb_shift")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.cb_shift)
        self.cb_alt = QtWidgets.QCheckBox(Dialog)
        self.cb_alt.setObjectName("cb_alt")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.cb_alt)
        self.cb_metasuper = QtWidgets.QCheckBox(Dialog)
        self.cb_metasuper.setObjectName("cb_metasuper")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.cb_metasuper)
        self.le_key = QtWidgets.QLineEdit(Dialog)
        self.le_key.setObjectName("le_key")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.le_key)
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Button:"))
        self.cb_ctrl.setText(_translate("Dialog", "Ctrl (Cmd)"))
        self.cb_shift.setText(_translate("Dialog", "Shift"))
        self.cb_alt.setText(_translate("Dialog", "Alt"))
        self.cb_metasuper.setText(_translate("Dialog", "Meta (Win, Super)"))
