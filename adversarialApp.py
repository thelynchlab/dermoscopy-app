# Callum Arthurs - ADVERSARIAL APP PROJECT - MADE FOR the LYNCHLAB- JAN2020
# MAC BUILD - run this to deploy the app on a MAC. note colon instead of semicolon. uses pyinstaller
# sudo pyinstaller -F --windowed --add-data "/Users/callum/callum/AdversarialScanner/images:images" --onefile --icon=images/icon.icns adversarialApp.py
# PC BUILD - remember the semicolon vs colon issue - .ico file instead of .icns for the KCL logo
# pyinstaller -F --windowed --add-data "C:/Users/Admin/callum/AdversarialScanner/images;images" --onefile --icon=images/icon.ico adversarialApp.py

from PyQt5.QtGui import QPixmap
import csv
from PyQt5 import uic
import qdarkgraystyle  # - https://github.com/mstuttgart/qdarkgraystyle
import sys
import os
import pickle
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication, QMainWindow
from PyQt5 import QtCore, QtWidgets


# sys._MEIPASS is only used to deploy the app with pyinstaller, to deploy comment next line:
sys._MEIPASS = "."


class AdversarialApp(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi(sys._MEIPASS + os.sep + "images" + os.sep + "adversarial_scanner_layout.ui", self)  # for deployment
        self.imagesloc = sys._MEIPASS + os.sep + "images" + os.sep  # for deployment
        self.statusBar()
        self.setWindowTitle('Dermoscopic Images Study')
        self.scores = []

        with open(self.imagesloc + 'fileorder.pkl', 'rb') as f:  # load file order
            self.files = pickle.load(f)

        # self.files = natsorted([f for f in os.listdir(self.imagesloc) if f.endswith(".jpg") and not f.startswith('.')])
        print("files - ", self.files)
        self.iter = 0
        self.total = len(self.files)
        self.statusbar.showMessage(f'Select a diagnosis 1 of {self.total}')
        self.btn1.clicked.connect(lambda: self.score(0))
        self.btn2.clicked.connect(lambda: self.score(1))
        self.delete_button.clicked.connect(lambda: self.deletebutton())
        self.delete_button.setStyleSheet("background-color:rgb(80,0,0)");

        # loading progress
        if os.path.exists(self.imagesloc + 'progressfile.dat'):
            with open(self.imagesloc + 'progressfile.dat', 'rb') as f:
                self.iter, self.scores = pickle.load(f)
        self.progressBar.setValue(self.iter)
        self.statusbar.showMessage(f'Select a diagnosis {self.iter + 1} of {self.total}')
        self.show()
        scene = QtWidgets.QGraphicsScene()
        self.pixmap = QtWidgets.QGraphicsPixmapItem()
        scene.addItem(self.pixmap)
        self.graphicsView.setScene(scene)
        self.im = QPixmap(self.imagesloc + self.files[self.iter])
        self.pixmap.setPixmap(self.im)
        self.graphicsView.fitInView(self.graphicsView.sceneRect(), QtCore.Qt.KeepAspectRatio)
        self.show()

    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        self.graphicsView.fitInView(self.graphicsView.sceneRect(), QtCore.Qt.KeepAspectRatio)
        self.show()

    def deletebutton(self):
        buttonReply = QMessageBox.question(self, 'PyQt5 message', "Delete all metadata and start test again?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            if os.path.exists(self.imagesloc + 'progressfile.dat'):
                os.remove(self.imagesloc + 'progressfile.dat')
            print('All metadata deleted, restarting')
            self.close()
            self.__init__()
        else:
            print('Not clicked')

    def score(self, score):
        self.scores.append([self.files[self.iter], score])
        self.progressBar.setMaximum(self.total)
        print(score)
        print(self.iter, self.total)
        if self.iter <= self.total - 2:
            self.iter += 1
            print(self.files[self.iter])
            pixmap = QPixmap(self.imagesloc + self.files[self.iter])
            self.pixmap.setPixmap(pixmap)
            self.statusbar.showMessage(f'Select a diagnosis {self.iter + 1} of {self.total}')
            print(self.iter)
            self.progressBar.setValue(self.iter)

            # saving progress
            with open(self.imagesloc + 'progressfile.dat', 'wb') as f:
                pickle.dump([self.iter, self.scores], f, protocol=2)

        else:
            while True:
                try:
                    self.progressBar.setValue(self.iter + 1)
                    self.statusbar.showMessage(f'Save File')
                    saveloc, _ = QFileDialog.getSaveFileName(self, "Save results to excel", ".", "*.csv")
                    with open(saveloc, 'w') as out:
                        csv_out = csv.writer(out)
                        csv_out.writerow(['Image_name', 'Diagnosis'])
                        for row in self.scores:
                            csv_out.writerow(row)
                except FileNotFoundError:
                    print("Sorry, I didn't understand that.")
                    continue
                else:
                    self.statusbar.showMessage(f'Results saved - please return results to study coordinator')
                    self.btn1.setEnabled(False)
                    self.btn2.setEnabled(False)
                    self.progressBar.setEnabled(False)
                    self.graphicsView.setEnabled(False)
                    self.listWidget.setEnabled(False)
                    break


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AdversarialApp()

    # style sheet - https://github.com/mstuttgart/qdarkgraystyle
    app.setStyleSheet(qdarkgraystyle.load_stylesheet())

    # execute
    ex.show()
    app.exec_()
