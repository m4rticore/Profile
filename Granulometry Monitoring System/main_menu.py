from PyQt6 import QtCore, QtGui, QtWidgets
# -- coding: utf-8 --

import sys
import os
from ctypes import *
import datetime
import numpy
import cv2
import gc

sys.path.append("MVSDK")
sys.path.append("Runtime/x64/")
from IMVApi import *

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 900)
        MainWindow.setMinimumSize(QtCore.QSize(1280, 900))
        MainWindow.setMaximumSize(QtCore.QSize(2560, 1440))
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)

        self.centralwidget.setMinimumSize(QtCore.QSize(1280, 720))
        self.centralwidget.setMaximumSize(QtCore.QSize(2560, 1440))
        self.centralwidget.setAutoFillBackground(True)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textEdit = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.textEdit.setEnabled(True)
        self.textEdit.setMaximumSize(QtCore.QSize(16777215, 150))
        self.textEdit.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.textEdit.setAcceptDrops(True)
        self.textEdit.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit.setDocumentTitle("")
        self.textEdit.setReadOnly(True)
        self.textEdit.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.NoTextInteraction)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)


        #Виджет со списком устройств
        self.listWidget = QtWidgets.QListWidget(parent=self.centralwidget)
        self.listWidget.setObjectName("listWidget")
        item = QtWidgets.QListWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(36)
        item.setFont(font)

        #добавляем элемент
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(36)
        item.setFont(font)



        self.verticalLayout.addWidget(self.listWidget)
        self.horizontalGroupBox = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.horizontalGroupBox.setObjectName("horizontalGroupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalGroupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")


        #кнопка обновить
        self.pushButton = QtWidgets.QPushButton(parent=self.horizontalGroupBox)
        font = QtGui.QFont()
        font.setPointSize(46)
        self.pushButton.setFont(font)

        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        #Подключение функции обновления данных
        self.pushButton.clicked.connect(self.updateInfoBlock)


        #кнопка выбрать
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.horizontalGroupBox)
        font = QtGui.QFont()
        font.setPointSize(46)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        #подключение функции выбора камеры
        self.pushButton_2.clicked.connect(self.choose_device)
        self.horizontalLayout.addWidget(self.pushButton_2)




        self.verticalLayout.addWidget(self.horizontalGroupBox)
        self.lineEdit = QtWidgets.QLineEdit(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lineEdit.setFont(font)
        self.lineEdit.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.lineEdit.setFrame(True)
        self.lineEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom|QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft)
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1280, 21))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(parent=self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(parent=self.menubar)
        self.menu_2.setObjectName("menu_2")
        self.menu_3 = QtWidgets.QMenu(parent=self.menubar)
        self.menu_3.setObjectName("menu_3")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.action_2 = QtGui.QAction(parent=MainWindow)
        self.action_2.setObjectName("action_2")
        self.action_3 = QtGui.QAction(parent=MainWindow)
        self.action_3.setObjectName("action_3")
        self.actionYOLO_2 = QtGui.QAction(parent=MainWindow)
        self.actionYOLO_2.setObjectName("actionYOLO_2")
        self.action_4 = QtGui.QAction(parent=MainWindow)
        self.action_4.setObjectName("action_4")
        self.menu.addAction(self.action_4)
        self.menu_2.addAction(self.action_2)
        self.menu_3.addAction(self.actionYOLO_2)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menu_3.menuAction())

        self.retranslateUi(MainWindow)


        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.textEdit.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:72pt;\">Выберите камеру</span></p></body></html>"))
        __sortingEnabled = self.listWidget.isSortingEnabled()

        #Список устройств(камер)
        self.listWidget.setSortingEnabled(False)
        item = self.listWidget.item(0)
        item.setText(_translate("MainWindow", "Cam1"))



        self.listWidget.setSortingEnabled(__sortingEnabled)
        #Ивент на обновление списка
        self.pushButton.setText(_translate("MainWindow", "Обновить"))



        #запуск программы
        self.pushButton_2.setText(_translate("MainWindow", "Выбрать"))


        self.lineEdit.setText(_translate("MainWindow", "Консоль:"))
        self.menu.setTitle(_translate("MainWindow", "Файл"))
        self.menu_2.setTitle(_translate("MainWindow", "История"))
        self.menu_3.setTitle(_translate("MainWindow", "Настройки"))
        self.action_2.setText(_translate("MainWindow", "Открыть архив"))
        self.action_3.setText(_translate("MainWindow", "Изменить модель"))
        self.actionYOLO_2.setText(_translate("MainWindow", "YOLO Конфигурация"))
        self.action_4.setText(_translate("MainWindow", "Открыть файл из архива"))

    def choose_device(self,MainWindow):
        print("Choose Cam1")
    def updateInfoBlock(self, MainWindow):
        # Инициализация камеры+получение информации при нажатии обновить устройства
        cam_refresh=RefreshCamera()
        cam_refresh.initCamera()





class RefreshCamera():
    def initCamera(self):
        deviceList = IMV_DeviceList()
        interfaceType = IMV_EInterfaceType.interfaceTypeAll
        nWidth = c_uint()
        nHeight = c_uint()




        nRet = MvCamera.IMV_EnumDevices(deviceList, interfaceType)
        if IMV_OK != nRet:
            print("Enumeration devices failed! ErrorCode", nRet)
        if deviceList.nDevNum == 0:
            print("find no device!")
        print("deviceList size is", deviceList.nDevNum)
        displayDeviceInfo(deviceList)
        nConnectionNum = input("Please input the camera index: ")
        if int(nConnectionNum) > deviceList.nDevNum:
            print("intput error!")

        cam = MvCamera()
        # 创建设备句柄
        nRet = cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(int(nConnectionNum) - 1)))
        if IMV_OK != nRet:
            print("Create devHandle failed! ErrorCode", nRet)

        # 打开相机
        nRet = cam.IMV_Open()
        if IMV_OK != nRet:
            print("Open devHandle failed! ErrorCode", nRet)

        nRet = IMV_OK
        nRet = cam.IMV_SetEnumFeatureSymbol("TriggerSource", "Software")
        if IMV_OK != nRet:
            print("Set triggerSource value failed! ErrorCode[%d]" % nRet)

        nRet = cam.IMV_SetEnumFeatureSymbol("TriggerSelector", "FrameStart")
        if IMV_OK != nRet:
            print("Set triggerSelector value failed! ErrorCode[%d]" % nRet)

        nRet = cam.IMV_SetEnumFeatureSymbol("TriggerMode", "Off")
        if IMV_OK != nRet:
            print("Set triggerMode value failed! ErrorCode[%d]" % nRet)

        # 开始拉流
        nRet = cam.IMV_StartGrabbing()
        if IMV_OK != nRet:
            print("Start grabbing failed! ErrorCode", nRet)

        isGrab = True

        while isGrab:
            frame = IMV_Frame()
            stPixelConvertParam = IMV_PixelConvertParam()

            nRet = cam.IMV_GetFrame(frame, 1000)

            if IMV_OK != nRet:
                print("getFrame fail! Timeout:[1000]ms")
                continue
            else:
                print("getFrame success BlockId = [" + str(frame.frameInfo.blockId) + "], get frame time: " + str(
                    datetime.datetime.now()))

            if None == byref(frame):
                print("pFrame is NULL!")
                continue

            if IMV_EPixelType.gvspPixelMono8 == frame.frameInfo.pixelFormat:
                nDstBufSize = frame.frameInfo.width * frame.frameInfo.height
            else:
                nDstBufSize = frame.frameInfo.width * frame.frameInfo.height * 3

            pDstBuf = (c_ubyte * nDstBufSize)()
            memset(byref(stPixelConvertParam), 0, sizeof(stPixelConvertParam))

            stPixelConvertParam.nWidth = frame.frameInfo.width
            stPixelConvertParam.nHeight = frame.frameInfo.height
            stPixelConvertParam.ePixelFormat = frame.frameInfo.pixelFormat
            stPixelConvertParam.pSrcData = frame.pData
            stPixelConvertParam.nSrcDataLen = frame.frameInfo.size
            stPixelConvertParam.nPaddingX = frame.frameInfo.paddingX
            stPixelConvertParam.nPaddingY = frame.frameInfo.paddingY
            stPixelConvertParam.eBayerDemosaic = IMV_EBayerDemosaic.demosaicNearestNeighbor
            stPixelConvertParam.eDstPixelFormat = frame.frameInfo.pixelFormat
            stPixelConvertParam.pDstBuf = pDstBuf
            stPixelConvertParam.nDstBufSize = nDstBufSize

            # release frame resource at the end of use

            nRet = cam.IMV_ReleaseFrame(frame)
            if IMV_OK != nRet:
                print("Release frame failed! ErrorCode[%d]\n", nRet)

            # 如果图像格式是 Mono8 直接使用
            # no format conversion required for Mono8
            if stPixelConvertParam.ePixelFormat == IMV_EPixelType.gvspPixelMono8:
                imageBuff = stPixelConvertParam.pSrcData
                userBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)

                memmove(userBuff, imageBuff, stPixelConvertParam.nDstBufSize)
                grayByteArray = bytearray(userBuff)

                cvImage = numpy.array(grayByteArray).reshape(stPixelConvertParam.nHeight,
                                                             stPixelConvertParam.nWidth)

            else:

                # convert to BGR24
                stPixelConvertParam.eDstPixelFormat = IMV_EPixelType.gvspPixelBGR8
                # stPixelConvertParam.nDstBufSize=nDstBufSize

                nRet = cam.IMV_PixelConvert(stPixelConvertParam)
                if IMV_OK != nRet:
                    print("image convert to failed! ErrorCode[%d]" % nRet)
                    del pDstBuf
                rgbBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
                memmove(rgbBuff, stPixelConvertParam.pDstBuf, stPixelConvertParam.nDstBufSize)
                colorByteArray = bytearray(rgbBuff)
                cvImage = numpy.array(colorByteArray).reshape(stPixelConvertParam.nHeight,
                                                              stPixelConvertParam.nWidth, 3)
                if None != pDstBuf:
                    del pDstBuf
                    pass
            # Filename
            filename = 'savedImage.jpg'

            # Using cv2.imwrite() method
            # Saving the image
            cv2.imwrite(filename, cvImage)

    def displayDeviceInfo(deviceInfoList):
        print("Idx  Type   Vendor              Model           S/N                 DeviceUserID    IP Address")
        print("------------------------------------------------------------------------------------------------")
        for i in range(0, deviceInfoList.nDevNum):
            pDeviceInfo = deviceInfoList.pDevInfo[i]
            strType = ""
            strVendorName = pDeviceInfo.vendorName.decode("ascii")
            strModeName = pDeviceInfo.modelName.decode("ascii")
            strSerialNumber = pDeviceInfo.serialNumber.decode("ascii")
            strCameraname = pDeviceInfo.cameraName.decode("ascii")
            strIpAdress = pDeviceInfo.DeviceSpecificInfo.gigeDeviceInfo.ipAddress.decode("ascii")
            if pDeviceInfo.nCameraType == typeGigeCamera:
                strType = "Gige"
            elif pDeviceInfo.nCameraType == typeU3vCamera:
                strType = "U3V"
            print("[%d]  %s   %s    %s      %s     %s           %s" % (
            i + 1, strType, strVendorName, strModeName, strSerialNumber, strCameraname, strIpAdress))






if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)





    MainWindow.show()
    sys.exit(app.exec())
