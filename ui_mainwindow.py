# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QHBoxLayout,
    QLabel, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QTextEdit, QVBoxLayout,
    QWidget, QScrollArea)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1280, 720)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mainLayout = QVBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.titleLabel = QLabel(self.centralwidget)
        self.titleLabel.setObjectName(u"titleLabel")
        font = QFont()
        font.setFamilies([u"Microsoft YaHei"])
        font.setPointSize(24)
        font.setBold(True)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.mainLayout.addWidget(self.titleLabel)

        self.contentLayout = QHBoxLayout()
        self.contentLayout.setObjectName(u"contentLayout")
        self.leftLayout = QVBoxLayout()
        self.leftLayout.setObjectName(u"leftLayout")
        self.operationGroupBox = QGroupBox(self.centralwidget)
        self.operationGroupBox.setObjectName(u"operationGroupBox")
        self.operationLayout = QVBoxLayout(self.operationGroupBox)
        self.operationLayout.setObjectName(u"operationLayout")
        self.imageLabel = QLabel(self.operationGroupBox)
        self.imageLabel.setObjectName(u"imageLabel")
        self.imageLabel.setMinimumSize(QSize(400, 300))
        self.imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.operationLayout.addWidget(self.imageLabel)

        self.loadImageButton = QPushButton(self.operationGroupBox)
        self.loadImageButton.setObjectName(u"loadImageButton")

        self.operationLayout.addWidget(self.loadImageButton)

        self.processButton = QPushButton(self.operationGroupBox)
        self.processButton.setObjectName(u"processButton")

        self.operationLayout.addWidget(self.processButton)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.llmAnalysisButton = QPushButton(self.operationGroupBox)
        self.llmAnalysisButton.setObjectName(u"llmAnalysisButton")

        self.buttonLayout.addWidget(self.llmAnalysisButton)

        self.quitButton = QPushButton(self.operationGroupBox)
        self.quitButton.setObjectName(u"quitButton")

        self.buttonLayout.addWidget(self.quitButton)

        self.operationLayout.addLayout(self.buttonLayout)

        self.leftLayout.addWidget(self.operationGroupBox)

        self.contentLayout.addLayout(self.leftLayout)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setObjectName(u"rightLayout")
        self.confidenceChartGroupBox = QGroupBox(self.centralwidget)
        self.confidenceChartGroupBox.setObjectName(u"confidenceChartGroupBox")
        self.confidenceChartLayout = QVBoxLayout(self.confidenceChartGroupBox)
        self.confidenceChartLayout.setObjectName(u"confidenceChartLayout")

        self.rightLayout.addWidget(self.confidenceChartGroupBox)

        self.detectionResultGroupBox = QGroupBox(self.centralwidget)
        self.detectionResultGroupBox.setObjectName(u"detectionResultGroupBox")
        self.detectionResultLayout = QVBoxLayout(self.detectionResultGroupBox)
        self.detectionResultLayout.setObjectName(u"detectionResultLayout")
        self.targetSelector = QComboBox(self.detectionResultGroupBox)
        self.targetSelector.setObjectName(u"targetSelector")
        self.targetSelector.setMinimumSize(QSize(200, 30))

        self.detectionResultLayout.addWidget(self.targetSelector)

        # 创建一个 QScrollArea 用于检测结果
        self.scrollArea = QScrollArea(self.detectionResultGroupBox)
        self.scrollArea.setWidgetResizable(True)  # 允许内容调整大小
        self.scrollArea.setMinimumHeight(100)  # 设置最小高度
        self.scrollArea.setMaximumHeight(200)  # 设置最大高度，防止过长

        # 创建一个 QWidget 作为滚动区域的内容
        self.scrollWidget = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setAlignment(Qt.AlignTop)

        # 添加检测结果的标签到滚动区域
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(12)

        self.objectTypeLabel = QLabel(self.scrollWidget)
        self.objectTypeLabel.setObjectName(u"objectTypeLabel")
        self.objectTypeLabel.setFont(font1)
        self.objectTypeLabel.setWordWrap(True)  # 启用自动换行
        self.scrollLayout.addWidget(self.objectTypeLabel)

        self.confidenceLabel = QLabel(self.scrollWidget)
        self.confidenceLabel.setObjectName(u"confidenceLabel")
        self.confidenceLabel.setFont(font1)
        self.confidenceLabel.setWordWrap(True)  # 启用自动换行
        self.scrollLayout.addWidget(self.confidenceLabel)

        self.positionLabel = QLabel(self.scrollWidget)
        self.positionLabel.setObjectName(u"positionLabel")
        self.positionLabel.setFont(font1)
        self.positionLabel.setWordWrap(True)  # 启用自动换行
        self.scrollLayout.addWidget(self.positionLabel)

        # 将 scrollWidget 设置为 scrollArea 的内容
        self.scrollArea.setWidget(self.scrollWidget)
        self.detectionResultLayout.addWidget(self.scrollArea)

        self.rightLayout.addWidget(self.detectionResultGroupBox)

        self.warningGroupBox = QGroupBox(self.centralwidget)
        self.warningGroupBox.setObjectName(u"warningGroupBox")
        self.warningLayout = QVBoxLayout(self.warningGroupBox)
        self.warningLayout.setObjectName(u"warningLayout")
        self.lightLayout = QHBoxLayout()
        self.lightLayout.setObjectName(u"lightLayout")
        self.greenLightLabel = QLabel(self.warningGroupBox)
        self.greenLightLabel.setObjectName(u"greenLightLabel")
        self.greenLightLabel.setMinimumSize(QSize(40, 40))
        self.greenLightLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lightLayout.addWidget(self.greenLightLabel)

        self.yellowLightLabel = QLabel(self.warningGroupBox)
        self.yellowLightLabel.setObjectName(u"yellowLightLabel")
        self.yellowLightLabel.setMinimumSize(QSize(40, 40))
        self.yellowLightLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lightLayout.addWidget(self.yellowLightLabel)

        self.redLightLabel = QLabel(self.warningGroupBox)
        self.redLightLabel.setObjectName(u"redLightLabel")
        self.redLightLabel.setMinimumSize(QSize(40, 40))
        self.redLightLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lightLayout.addWidget(self.redLightLabel)

        self.warningLayout.addLayout(self.lightLayout)

        self.llmAnalysisLabel = QLabel(self.warningGroupBox)
        self.llmAnalysisLabel.setObjectName(u"llmAnalysisLabel")
        self.llmAnalysisLabel.setFont(font1)

        self.warningLayout.addWidget(self.llmAnalysisLabel)

        self.llmResultTextEdit = QTextEdit(self.warningGroupBox)
        self.llmResultTextEdit.setObjectName(u"llmResultTextEdit")

        self.warningLayout.addWidget(self.llmResultTextEdit)

        self.rightLayout.addWidget(self.warningGroupBox)

        self.contentLayout.addLayout(self.rightLayout)

        self.mainLayout.addLayout(self.contentLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1280, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u65e0\u4eba\u673a\u56fe\u50cf\u53bb\u96fe\u4e0e\u76ee\u6807\u68c0\u6d4b\u4e00\u4f53\u5316\u7cfb\u7edf", None))
        self.titleLabel.setText(QCoreApplication.translate("MainWindow", u"\u65e0\u4eba\u673a\u56fe\u50cf\u53bb\u96fe\u4e0e\u76ee\u6807\u68c0\u6d4b\u4e00\u4f53\u5316\u7cfb\u7edf", None))
        self.operationGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u64cd\u4f5c", None))
        self.imageLabel.setText(QCoreApplication.translate("MainWindow", u"\u56fe\u7247\u663e\u793a\u533a\u57df", None))
        self.loadImageButton.setText(QCoreApplication.translate("MainWindow", u"\u70b9\u51fb\u4e0a\u4f20\u56fe\u7247", None))
        self.processButton.setText(QCoreApplication.translate("MainWindow", u"\u70b9\u51fb\u8fdb\u884c\u53bb\u96fe\u548c\u76ee\u6807\u68c0\u6d4b", None))
        self.llmAnalysisButton.setText(QCoreApplication.translate("MainWindow", u"\u667a\u80fd\u5206\u6790", None))
        self.quitButton.setText(QCoreApplication.translate("MainWindow", u"\u9000\u51fa", None))
        self.confidenceChartGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u7f6e\u4fe1\u5ea6\u5206\u5e03", None))
        self.detectionResultGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u68c0\u6d4b\u7ed3\u679c", None))
        self.objectTypeLabel.setText(QCoreApplication.translate("MainWindow", u"\u76ee\u6807\u7c7b\u578b: ", None))
        self.confidenceLabel.setText(QCoreApplication.translate("MainWindow", u"\u7f6e\u4fe1\u5ea6: ", None))
        self.positionLabel.setText(QCoreApplication.translate("MainWindow", u"\u76ee\u6807\u4f4d\u7f6e: ", None))
        self.warningGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u9884\u8b66\u63d0\u793a", None))
        self.greenLightLabel.setText("")
        self.yellowLightLabel.setText("")
        self.redLightLabel.setText("")
        self.llmAnalysisLabel.setText(QCoreApplication.translate("MainWindow", u"\u9884\u8b66\u72b6\u6001: ", None))
    # retranslateUi
