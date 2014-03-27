# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_connector.ui'
#
# Created: Wed Mar 26 15:07:40 2014
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
        Connector.resize(502, 456)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Connector)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_3 = QtGui.QLabel(Connector)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.serviceURL = QtGui.QLineEdit(Connector)
        self.serviceURL.setObjectName(_fromUtf8("serviceURL"))
        self.gridLayout_2.addWidget(self.serviceURL, 0, 2, 1, 1)
        self.protocol = QtGui.QComboBox(Connector)
        self.protocol.setObjectName(_fromUtf8("protocol"))
        self.protocol.addItem(_fromUtf8(""))
        self.protocol.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.protocol, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(Connector)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 3, 1, 1)
        self.label = QtGui.QLabel(Connector)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.password = QtGui.QLineEdit(Connector)
        self.password.setObjectName(_fromUtf8("password"))
        self.gridLayout.addWidget(self.password, 0, 4, 1, 1)
        self.line = QtGui.QFrame(Connector)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 0, 2, 1, 1)
        self.username = QtGui.QLineEdit(Connector)
        self.username.setObjectName(_fromUtf8("username"))
        self.gridLayout.addWidget(self.username, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.loadServices = QtGui.QPushButton(Connector)
        self.loadServices.setObjectName(_fromUtf8("loadServices"))
        self.horizontalLayout_2.addWidget(self.loadServices)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.treeView = QtGui.QTreeWidget(Connector)
        self.treeView.setObjectName(_fromUtf8("treeView"))
        self.verticalLayout.addWidget(self.treeView)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.importLayers = QtGui.QPushButton(Connector)
        self.importLayers.setObjectName(_fromUtf8("importLayers"))
        self.horizontalLayout.addWidget(self.importLayers)
        self.cancelButton = QtGui.QPushButton(Connector)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(Connector)
        QtCore.QMetaObject.connectSlotsByName(Connector)
        Connector.setTabOrder(self.protocol, self.serviceURL)
        Connector.setTabOrder(self.serviceURL, self.username)
        Connector.setTabOrder(self.username, self.password)
        Connector.setTabOrder(self.password, self.loadServices)
        Connector.setTabOrder(self.loadServices, self.treeView)
        Connector.setTabOrder(self.treeView, self.importLayers)
        Connector.setTabOrder(self.importLayers, self.cancelButton)

    def retranslateUi(self, Connector):
        Connector.setWindowTitle(_translate("Connector", "Connector", None))
        self.label_3.setText(_translate("Connector", "REST Service URL:", None))
        self.protocol.setItemText(0, _translate("Connector", "http://", None))
        self.protocol.setItemText(1, _translate("Connector", "https://", None))
        self.label_2.setText(_translate("Connector", "Password:", None))
        self.label.setText(_translate("Connector", "Username:", None))
        self.loadServices.setText(_translate("Connector", "Load Services", None))
        self.treeView.headerItem().setText(0, _translate("Connector", "Services", None))
        self.importLayers.setText(_translate("Connector", "Import Layer", None))
        self.cancelButton.setText(_translate("Connector", "Cancel", None))

