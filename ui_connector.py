# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_connector.ui'
#
# Created: Tue Jun 10 09:38:37 2014
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
        Connector.resize(830, 401)
        self.verticalLayout_3 = QtGui.QVBoxLayout(Connector)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(Connector)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.connections = QtGui.QComboBox(self.groupBox)
        self.connections.setObjectName(_fromUtf8("connections"))
        self.verticalLayout.addWidget(self.connections)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.connectButton = QtGui.QPushButton(self.groupBox)
        self.connectButton.setObjectName(_fromUtf8("connectButton"))
        self.horizontalLayout_3.addWidget(self.connectButton)
        self.newButton = QtGui.QPushButton(self.groupBox)
        self.newButton.setObjectName(_fromUtf8("newButton"))
        self.horizontalLayout_3.addWidget(self.newButton)
        self.editButton = QtGui.QPushButton(self.groupBox)
        self.editButton.setObjectName(_fromUtf8("editButton"))
        self.horizontalLayout_3.addWidget(self.editButton)
        self.deleteButton = QtGui.QPushButton(self.groupBox)
        self.deleteButton.setObjectName(_fromUtf8("deleteButton"))
        self.horizontalLayout_3.addWidget(self.deleteButton)
        spacerItem = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout_2)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.treeView = QtGui.QTreeWidget(Connector)
        self.treeView.setObjectName(_fromUtf8("treeView"))
        self.horizontalLayout_2.addWidget(self.treeView)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem1 = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.importLayers = QtGui.QPushButton(Connector)
        self.importLayers.setObjectName(_fromUtf8("importLayers"))
        self.horizontalLayout.addWidget(self.importLayers)
        self.cancelButton = QtGui.QPushButton(Connector)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.retranslateUi(Connector)
        QtCore.QMetaObject.connectSlotsByName(Connector)
        Connector.setTabOrder(self.importLayers, self.cancelButton)

    def retranslateUi(self, Connector):
        Connector.setWindowTitle(_translate("Connector", "Connector", None))
        self.groupBox.setTitle(_translate("Connector", "Connections", None))
        self.connectButton.setText(_translate("Connector", "Connect", None))
        self.newButton.setText(_translate("Connector", "New", None))
        self.editButton.setText(_translate("Connector", "Edit", None))
        self.deleteButton.setText(_translate("Connector", "Delete", None))
        self.treeView.headerItem().setText(
            0, _translate("Connector", "Services", None))
        self.importLayers.setText(
            _translate("Connector", "Import Layer", None))
        self.cancelButton.setText(_translate("Connector", "Cancel", None))
