# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './kollektiv5gui/views/ea_options_widget.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Options(object):
    def setupUi(self, Options):
        Options.setObjectName("Options")
        Options.resize(593, 449)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Options.sizePolicy().hasHeightForWidth())
        Options.setSizePolicy(sizePolicy)
        Options.setMinimumSize(QtCore.QSize(593, 449))
        Options.setMaximumSize(QtCore.QSize(593, 449))
        self.presetsLabel = QtWidgets.QLabel(Options)
        self.presetsLabel.setGeometry(QtCore.QRect(10, 10, 131, 21))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.presetsLabel.setFont(font)
        self.presetsLabel.setObjectName("presetsLabel")
        self.groupBox_4 = QtWidgets.QGroupBox(Options)
        self.groupBox_4.setGeometry(QtCore.QRect(400, 60, 171, 381))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.groupBox_4.setFont(font)
        self.groupBox_4.setFlat(False)
        self.groupBox_4.setCheckable(False)
        self.groupBox_4.setObjectName("groupBox_4")
        self.label_21 = QtWidgets.QLabel(self.groupBox_4)
        self.label_21.setGeometry(QtCore.QRect(10, 20, 161, 20))
        self.label_21.setObjectName("label_21")
        self.initialPopulationSizeSpinBox = QtWidgets.QSpinBox(self.groupBox_4)
        self.initialPopulationSizeSpinBox.setGeometry(QtCore.QRect(10, 40, 61, 22))
        self.initialPopulationSizeSpinBox.setMaximum(1000)
        self.initialPopulationSizeSpinBox.setProperty("value", 60)
        self.initialPopulationSizeSpinBox.setObjectName("initialPopulationSizeSpinBox")
        self.targetConfidenceSpinBox = QtWidgets.QSpinBox(self.groupBox_4)
        self.targetConfidenceSpinBox.setGeometry(QtCore.QRect(10, 90, 61, 22))
        self.targetConfidenceSpinBox.setMaximum(100)
        self.targetConfidenceSpinBox.setSingleStep(1)
        self.targetConfidenceSpinBox.setProperty("value", 90)
        self.targetConfidenceSpinBox.setObjectName("targetConfidenceSpinBox")
        self.label_22 = QtWidgets.QLabel(self.groupBox_4)
        self.label_22.setGeometry(QtCore.QRect(10, 70, 161, 20))
        self.label_22.setObjectName("label_22")
        self.label_23 = QtWidgets.QLabel(self.groupBox_4)
        self.label_23.setGeometry(QtCore.QRect(10, 120, 161, 20))
        self.label_23.setObjectName("label_23")
        self.targetPopulationSizeSpinBox = QtWidgets.QSpinBox(self.groupBox_4)
        self.targetPopulationSizeSpinBox.setGeometry(QtCore.QRect(10, 140, 61, 22))
        self.targetPopulationSizeSpinBox.setMaximum(100)
        self.targetPopulationSizeSpinBox.setSingleStep(1)
        self.targetPopulationSizeSpinBox.setProperty("value", 5)
        self.targetPopulationSizeSpinBox.setObjectName("targetPopulationSizeSpinBox")
        self.colorsGroupBox = QtWidgets.QGroupBox(Options)
        self.colorsGroupBox.setGeometry(QtCore.QRect(10, 60, 201, 381))
        self.colorsGroupBox.setFlat(False)
        self.colorsGroupBox.setObjectName("colorsGroupBox")
        self.colorMutationRateSpinBox = QtWidgets.QSpinBox(self.colorsGroupBox)
        self.colorMutationRateSpinBox.setGeometry(QtCore.QRect(10, 40, 61, 22))
        self.colorMutationRateSpinBox.setMaximum(1000)
        self.colorMutationRateSpinBox.setProperty("value", 5)
        self.colorMutationRateSpinBox.setObjectName("colorMutationRateSpinBox")
        self.label_19 = QtWidgets.QLabel(self.colorsGroupBox)
        self.label_19.setGeometry(QtCore.QRect(10, 20, 191, 20))
        self.label_19.setObjectName("label_19")
        self.colorRangeGroupBox = QtWidgets.QGroupBox(self.colorsGroupBox)
        self.colorRangeGroupBox.setGeometry(QtCore.QRect(10, 70, 181, 301))
        self.colorRangeGroupBox.setCheckable(False)
        self.colorRangeGroupBox.setChecked(False)
        self.colorRangeGroupBox.setObjectName("colorRangeGroupBox")
        self.contrastFromSpinBox = QtWidgets.QSpinBox(self.colorRangeGroupBox)
        self.contrastFromSpinBox.setGeometry(QtCore.QRect(20, 200, 61, 22))
        self.contrastFromSpinBox.setMaximum(765)
        self.contrastFromSpinBox.setObjectName("contrastFromSpinBox")
        self.colorsToRSpinBox = QtWidgets.QSpinBox(self.colorRangeGroupBox)
        self.colorsToRSpinBox.setGeometry(QtCore.QRect(110, 70, 61, 22))
        self.colorsToRSpinBox.setMaximum(255)
        self.colorsToRSpinBox.setProperty("value", 255)
        self.colorsToRSpinBox.setObjectName("colorsToRSpinBox")
        self.label_15 = QtWidgets.QLabel(self.colorRangeGroupBox)
        self.label_15.setGeometry(QtCore.QRect(100, 100, 21, 20))
        self.label_15.setObjectName("label_15")
        self.label_7 = QtWidgets.QLabel(self.colorRangeGroupBox)
        self.label_7.setGeometry(QtCore.QRect(10, 30, 161, 20))
        self.label_7.setObjectName("label_7")
        self.colorsFromBSpinBox = QtWidgets.QSpinBox(self.colorRangeGroupBox)
        self.colorsFromBSpinBox.setGeometry(QtCore.QRect(20, 130, 61, 22))
        self.colorsFromBSpinBox.setMaximum(255)
        self.colorsFromBSpinBox.setObjectName("colorsFromBSpinBox")
        self.label_17 = QtWidgets.QLabel(self.colorRangeGroupBox)
        self.label_17.setGeometry(QtCore.QRect(110, 180, 31, 20))
        self.label_17.setObjectName("label_17")
        self.label_8 = QtWidgets.QLabel(self.colorRangeGroupBox)
        self.label_8.setGeometry(QtCore.QRect(20, 50, 51, 20))
        self.label_8.setObjectName("label_8")
        self.label_12 = QtWidgets.QLabel(self.colorRangeGroupBox)
        self.label_12.setGeometry(QtCore.QRect(10, 130, 21, 20))
        self.label_12.setObjectName("label_12")
        self.contrastToSpinBox = QtWidgets.QSpinBox(self.colorRangeGroupBox)
        self.contrastToSpinBox.setGeometry(QtCore.QRect(110, 200, 61, 22))
        self.contrastToSpinBox.setMaximum(765)
        self.contrastToSpinBox.setProperty("value", 765)
        self.contrastToSpinBox.setObjectName("contrastToSpinBox")
        self.label_16 = QtWidgets.QLabel(self.colorRangeGroupBox)
        self.label_16.setGeometry(QtCore.QRect(20, 180, 31, 20))
        self.label_16.setObjectName("label_16")
        self.colorsFromRSpinBox = QtWidgets.QSpinBox(self.colorRangeGroupBox)
        self.colorsFromRSpinBox.setGeometry(QtCore.QRect(20, 70, 61, 22))
        self.colorsFromRSpinBox.setMaximum(255)
        self.colorsFromRSpinBox.setObjectName("colorsFromRSpinBox")
        self.label_6 = QtWidgets.QLabel(self.colorRangeGroupBox)
        self.label_6.setGeometry(QtCore.QRect(10, 160, 161, 20))
        self.label_6.setObjectName("label_6")
        self.label_9 = QtWidgets.QLabel(self.colorRangeGroupBox)
        self.label_9.setGeometry(QtCore.QRect(110, 50, 21, 16))
        self.label_9.setObjectName("label_9")
        self.colorsToBSpinBox = QtWidgets.QSpinBox(self.colorRangeGroupBox)
        self.colorsToBSpinBox.setGeometry(QtCore.QRect(110, 130, 61, 22))
        self.colorsToBSpinBox.setMaximum(255)
        self.colorsToBSpinBox.setProperty("value", 255)
        self.colorsToBSpinBox.setObjectName("colorsToBSpinBox")
        self.colorsFromGSpinBox = QtWidgets.QSpinBox(self.colorRangeGroupBox)
        self.colorsFromGSpinBox.setGeometry(QtCore.QRect(20, 100, 61, 22))
        self.colorsFromGSpinBox.setMaximum(255)
        self.colorsFromGSpinBox.setObjectName("colorsFromGSpinBox")
        self.colorsToGSpinBox = QtWidgets.QSpinBox(self.colorRangeGroupBox)
        self.colorsToGSpinBox.setGeometry(QtCore.QRect(110, 100, 61, 22))
        self.colorsToGSpinBox.setMaximum(255)
        self.colorsToGSpinBox.setProperty("value", 255)
        self.colorsToGSpinBox.setObjectName("colorsToGSpinBox")
        self.label_13 = QtWidgets.QLabel(self.colorRangeGroupBox)
        self.label_13.setGeometry(QtCore.QRect(100, 130, 21, 20))
        self.label_13.setObjectName("label_13")
        self.label_10 = QtWidgets.QLabel(self.colorRangeGroupBox)
        self.label_10.setGeometry(QtCore.QRect(10, 70, 21, 20))
        self.label_10.setObjectName("label_10")
        self.label_14 = QtWidgets.QLabel(self.colorRangeGroupBox)
        self.label_14.setGeometry(QtCore.QRect(100, 70, 21, 20))
        self.label_14.setObjectName("label_14")
        self.label_11 = QtWidgets.QLabel(self.colorRangeGroupBox)
        self.label_11.setGeometry(QtCore.QRect(10, 100, 21, 20))
        self.label_11.setObjectName("label_11")
        self.setOptionsButton = QtWidgets.QPushButton(Options)
        self.setOptionsButton.setGeometry(QtCore.QRect(484, 22, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.setOptionsButton.setFont(font)
        self.setOptionsButton.setDefault(True)
        self.setOptionsButton.setObjectName("setOptionsButton")
        self.shapesGroupBox = QtWidgets.QGroupBox(Options)
        self.shapesGroupBox.setEnabled(True)
        self.shapesGroupBox.setGeometry(QtCore.QRect(220, 60, 171, 381))
        self.shapesGroupBox.setFlat(False)
        self.shapesGroupBox.setCheckable(False)
        self.shapesGroupBox.setObjectName("shapesGroupBox")
        self.shapePolygonPointCountSpinBox = QtWidgets.QSpinBox(self.shapesGroupBox)
        self.shapePolygonPointCountSpinBox.setGeometry(QtCore.QRect(10, 90, 61, 22))
        self.shapePolygonPointCountSpinBox.setProperty("value", 5)
        self.shapePolygonPointCountSpinBox.setObjectName("shapePolygonPointCountSpinBox")
        self.label_5 = QtWidgets.QLabel(self.shapesGroupBox)
        self.label_5.setGeometry(QtCore.QRect(10, 70, 161, 16))
        self.label_5.setObjectName("label_5")
        self.label_20 = QtWidgets.QLabel(self.shapesGroupBox)
        self.label_20.setGeometry(QtCore.QRect(10, 20, 161, 20))
        self.label_20.setObjectName("label_20")
        self.shapeMutationRateSpinBox = QtWidgets.QSpinBox(self.shapesGroupBox)
        self.shapeMutationRateSpinBox.setGeometry(QtCore.QRect(10, 40, 61, 22))
        self.shapeMutationRateSpinBox.setMaximum(1000)
        self.shapeMutationRateSpinBox.setProperty("value", 5)
        self.shapeMutationRateSpinBox.setObjectName("shapeMutationRateSpinBox")
        self.newPresetButton = QtWidgets.QPushButton(Options)
        self.newPresetButton.setGeometry(QtCore.QRect(150, 30, 151, 23))
        self.newPresetButton.setDefault(False)
        self.newPresetButton.setFlat(False)
        self.newPresetButton.setObjectName("newPresetButton")
        self.presetComboBox = QtWidgets.QComboBox(Options)
        self.presetComboBox.setGeometry(QtCore.QRect(10, 30, 131, 21))
        self.presetComboBox.setEditable(False)
        self.presetComboBox.setCurrentText("")
        self.presetComboBox.setObjectName("presetComboBox")
        self.removePresetButton = QtWidgets.QPushButton(Options)
        self.removePresetButton.setGeometry(QtCore.QRect(310, 30, 151, 23))
        self.removePresetButton.setDefault(False)
        self.removePresetButton.setFlat(False)
        self.removePresetButton.setObjectName("removePresetButton")

        self.retranslateUi(Options)
        QtCore.QMetaObject.connectSlotsByName(Options)

    def retranslateUi(self, Options):
        _translate = QtCore.QCoreApplication.translate
        Options.setWindowTitle(_translate("Options", "EA Settings"))
        self.presetsLabel.setText(_translate("Options", "Presets"))
        self.groupBox_4.setTitle(_translate("Options", "EA specific"))
        self.label_21.setText(_translate("Options", "initial population size"))
        self.label_22.setText(_translate("Options", "target confidence in %"))
        self.label_23.setText(_translate("Options", "target population size"))
        self.colorsGroupBox.setTitle(_translate("Options", "Colors and Contrast"))
        self.label_19.setText(_translate("Options", "color mutation rate"))
        self.colorRangeGroupBox.setTitle(_translate("Options", "Range Selection"))
        self.label_15.setText(_translate("Options", "G"))
        self.label_7.setText(_translate("Options", "colors range"))
        self.label_17.setText(_translate("Options", "to"))
        self.label_8.setText(_translate("Options", "from"))
        self.label_12.setText(_translate("Options", "B"))
        self.label_16.setText(_translate("Options", "from"))
        self.label_6.setText(_translate("Options", "contrast range "))
        self.label_9.setText(_translate("Options", "to"))
        self.label_13.setText(_translate("Options", "B"))
        self.label_10.setText(_translate("Options", "R"))
        self.label_14.setText(_translate("Options", "R"))
        self.label_11.setText(_translate("Options", "G"))
        self.setOptionsButton.setText(_translate("Options", "Apply"))
        self.shapesGroupBox.setTitle(_translate("Options", "Shapes"))
        self.label_5.setText(_translate("Options", "polygon point count"))
        self.label_20.setText(_translate("Options", "shape mutation rate"))
        self.newPresetButton.setText(_translate("Options", "Save as new preset"))
        self.removePresetButton.setText(_translate("Options", "Remove preset"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Options = QtWidgets.QWidget()
    ui = Ui_Options()
    ui.setupUi(Options)
    Options.show()
    sys.exit(app.exec_())

