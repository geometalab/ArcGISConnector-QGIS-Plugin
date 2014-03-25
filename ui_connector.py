# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_connector.ui'
#
# Created: Tue Mar 25 15:36:32 2014
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

class Ui_Connector(object):
    def setupUi(self, Connector):
        Connector.setObjectName(_fromUtf8("Connector"))
        Connector.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(Connector)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(Connector)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Connector.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Connector.reject)
        QtCore.QMetaObject.connectSlotsByName(Connector)

    def retranslateUi(self, Connector):
        Connector.setWindowTitle(_translate("Connector", "Connector", None))

