# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './settings_forecolor_bgcolor.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(490, 299)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.pb_hotkeyset = QtWidgets.QPushButton(Dialog)
        self.pb_hotkeyset.setObjectName("pb_hotkeyset")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.pb_hotkeyset)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.pb_color = QtWidgets.QPushButton(Dialog)
        self.pb_color.setObjectName("pb_color")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.pb_color)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setText("")
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.cb_contextmenu_show = QtWidgets.QCheckBox(Dialog)
        self.cb_contextmenu_show.setObjectName("cb_contextmenu_show")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.cb_contextmenu_show)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.le_contextmenu_text = QtWidgets.QLineEdit(Dialog)
        self.le_contextmenu_text.setObjectName("le_contextmenu_text")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.le_contextmenu_text)
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setText("")
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.cb_extrabutton_show = QtWidgets.QCheckBox(Dialog)
        self.cb_extrabutton_show.setObjectName("cb_extrabutton_show")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.cb_extrabutton_show)
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.le_extrabutton_text = QtWidgets.QLineEdit(Dialog)
        self.le_extrabutton_text.setObjectName("le_extrabutton_text")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.le_extrabutton_text)
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.le_tooltip_text = QtWidgets.QLineEdit(Dialog)
        self.le_tooltip_text.setObjectName("le_tooltip_text")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.le_tooltip_text)
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
        self.label.setText(_translate("Dialog", "Hotkey"))
        self.pb_hotkeyset.setText(_translate("Dialog", "... (click to change)"))
        self.label_2.setText(_translate("Dialog", "Color"))
        self.pb_color.setText(_translate("Dialog", "... (click to change)"))
        self.cb_contextmenu_show.setText(_translate("Dialog", "show in context menu and drop down button"))
        self.label_4.setText(_translate("Dialog", "Text in context menu"))
        self.cb_extrabutton_show.setText(_translate("Dialog", "show extra button"))
        self.label_6.setText(_translate("Dialog", "text for extra button"))
        self.label_7.setText(_translate("Dialog", "tooltip for extra button"))
