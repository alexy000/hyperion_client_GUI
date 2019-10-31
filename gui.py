import sys
import PyQt5.QtWidgets as qtw # import QMainWindow, QApplication, QPushButton, QFrame, QVBoxLayout
from PyQt5 import QtCore as qtc
from functools import partial

import hyperion_client

h = hyperion_client.hyperion_client('192.168.0.109', 19444)
h.open_connection(timeout=100)

class MyMainWindow(qtw.QMainWindow):

    def __init__(self):
        super().__init__()

        self.button1 = qtw.QPushButton("Toggle White")
        self.button2 = qtw.QPushButton("SendRGB")
        self.slider1 = qtw.QSlider(qtc.Qt.Horizontal)
        self.slider1.setMinimum(0)
        self.slider1.setMaximum(255)
        # self.slider1.setSingleStep(10)
        self.slider2 = qtw.QSlider(qtc.Qt.Horizontal)
        self.slider2.setMinimum(0)
        self.slider2.setMaximum(255)
        self.slider3 = qtw.QSlider(qtc.Qt.Horizontal)
        self.slider3.setMinimum(0)
        self.slider3.setMaximum(255)
        self.label1 = qtw.QLabel("(R, G, B): ")
        self.labelsb1 = qtw.QLabel("Red: ")
        self.labelsb2 = qtw.QLabel("Green: ")
        self.labelsb3 = qtw.QLabel("Blue: ")
        # self.l1.setAlignment(Qt.AlignCenter)

        self.frame = qtw.QFrame()

        vbox = qtw.QVBoxLayout()
        vbox.addWidget(self.button1)
        vbox.addWidget(self.button2)

        hbox1 = qtw.QHBoxLayout()
        hbox2 = qtw.QHBoxLayout()
        hbox3 = qtw.QHBoxLayout()

        # hbox.addStretch(1)
        hbox1.addWidget(self.labelsb1)
        hbox1.addWidget(self.slider1)
        vbox.addLayout(hbox1)
        hbox2.addWidget(self.labelsb2)
        hbox2.addWidget(self.slider2)
        vbox.addLayout(hbox2)
        hbox3.addWidget(self.labelsb3)
        hbox3.addWidget(self.slider3)
        vbox.addLayout(hbox3)
        vbox.addWidget(self.label1)
        self.frame.setLayout(vbox)

        self.button1.setCheckable(True)
        # self.button2.setCheckable(True)
        self.button1.toggled.connect(partial(self.button_pressed, "button1"))
        self.slider1.valueChanged.connect(self.valuechange)
        self.slider2.valueChanged.connect(self.valuechange)
        self.slider3.valueChanged.connect(self.valuechange)
        self.button2.clicked.connect(self.valuechange)
        self.setCentralWidget(self.frame)
        self.show()

    def button_pressed(self, caller, status):
        if status:
            # print("button {} is down".format(caller))
            self.label1.setText("(R, G, B): (150, 150, 150)")
            h.send_led_data((150,150,150))

        else:
            # print("button {} is up".format(caller))
            self.label1.setText("(R, G, B): (0, 0, 0)")
            h.send_led_data((0, 0, 0))

    def valuechange(self):
        # print("current value red:" + str(self.slider1.value()))
        # print("current value green:" + str(self.slider2.value()))
        # print("current value blue:" + str(self.slider3.value()))
        red = self.slider1.value()
        green = self.slider2.value()
        blue = self.slider3.value()
        self.label1.setText("(R, G, B): " + str(red)+", "+str(green)+", "+str(blue))
        # print(str(red)+", "+str(green)+", "+str(blue))
        h.send_led_data((red, green, blue))


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    GUI = MyMainWindow()
    GUI.show()
    sys.exit(app.exec_())
