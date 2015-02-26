# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'input.ui'
#
# Created: Fri Jun 06 17:25:41 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_Input(object):

    def setupUi(self, Input):
        Input.setObjectName(_fromUtf8("Input"))
        Input.resize(427, 233)
        self.verticalLayout = QtGui.QVBoxLayout(Input)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.serviceURLBox = QtGui.QLineEdit(Input)
        self.serviceURLBox.setObjectName(_fromUtf8("serviceURLBox"))
        self.formLayout.setWidget(
            1, QtGui.QFormLayout.FieldRole, self.serviceURLBox)
        self.label = QtGui.QLabel(Input)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label)
        self.label_2 = QtGui.QLabel(Input)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtGui.QLabel(Input)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_3)
        self.usernameBox = QtGui.QLineEdit(Input)
        self.usernameBox.setObjectName(_fromUtf8("usernameBox"))
        self.formLayout.setWidget(
            2, QtGui.QFormLayout.FieldRole, self.usernameBox)
        self.passwordBox = QtGui.QLineEdit(Input)
        self.passwordBox.setObjectName(_fromUtf8("passwordBox"))
        self.formLayout.setWidget(
            3, QtGui.QFormLayout.FieldRole, self.passwordBox)
        self.nameBox = QtGui.QLineEdit(Input)
        self.nameBox.setObjectName(_fromUtf8("nameBox"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.nameBox)
        self.label_4 = QtGui.QLabel(Input)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_4)
        self.verticalLayout.addLayout(self.formLayout)
        spacerItem = QtGui.QSpacerItem(
            20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem1 = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.cancelButton = QtGui.QPushButton(Input)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.horizontalLayout.addWidget(self.cancelButton)
        self.OKButton = QtGui.QPushButton(Input)
        self.OKButton.setObjectName(_fromUtf8("OKButton"))
        self.horizontalLayout.addWidget(self.OKButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Input)
        QtCore.QMetaObject.connectSlotsByName(Input)

    def retranslateUi(self, Input):
        Input.setWindowTitle(_translate("Input", "Dialog", None))
        self.label.setText(_translate("Input", "Service URL:", None))
        self.label_2.setText(_translate("Input", "Username", None))
        self.label_3.setText(_translate("Input", "Password", None))
        self.label_4.setText(_translate("Input", "Name", None))
        self.cancelButton.setText(_translate("Input", "Cancel", None))
        self.OKButton.setText(_translate("Input", "OK", None))
