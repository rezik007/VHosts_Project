from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QSlider
from PyQt5.QtCore import pyqtSlot, Qt
import sys, json, requests
import gui
import numpy as np
import sys
import csv

class Application(QtWidgets.QMainWindow, gui.Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # Events handlers
        button = self.pushButton
        button.clicked.connect(self.on_click1)
        #QtCore.QObject.connect(self.pushButton, QtCore('clicked()'), lambda msg ="" : self.SetDataSets())


    @pyqtSlot()
    def on_click1(self):
        self.AnalyzeTopDomains()

    def FindHosts(self):

        domainName = self.textEdit.toPlainText()
        requestOne = requests.get("http://reverseip.logontube.com/?url="+domainName+"&output=json")
        requestOne.raise_for_status()
        jsonRead = json.loads(requestOne.content.decode('utf-8'))
        # works for Python2 and Python3

        requestTwo = requests.get("http://api.hackertarget.com/reverseiplookup/?q="+domainName)
        requestTwo.raise_for_status()

        self.textBrowser.append("<span style='color: red; font-weight: bold;'>Wyniki dla hosta o domenie: "+domainName+"</span>")
        self.textBrowser.append("Adres IP: "+jsonRead['hostip'])
        self.textBrowser.append("Nazwa Hosta: " + jsonRead['hostname'])
        self.textBrowser.append("Domeny podpięte pod adres IP:")
        for i in range(0, len(jsonRead['response']['domains'])):
            self.textBrowser.append(jsonRead['response']['domains'][i])
        self.textBrowser.append(requestTwo.text)

    def AnalyzeTopDomains(self):
        summaryResult = {}

        databaseOfDomains = np.genfromtxt(r'top500domains.csv', dtype='U',skip_header=1, delimiter=',', usecols=(1,))
        databaseOfRootDomains = np.genfromtxt(r'top500domains.csv', dtype='U',skip_header=1, delimiter=',', usecols=(2,))

        for i in range(50, 60):
            requestOneAuto = requests.get("http://reverseip.logontube.com/?url="+databaseOfDomains[i]+"&output=json")
            requestOneAuto.raise_for_status()
            jsonRead = json.loads(requestOneAuto.content.decode('utf-8'))
            numberOfDomainsOne = len(jsonRead['response']['domains'])
            requestTwoAuto = requests.get("http://api.hackertarget.com/reverseiplookup/?q=" +databaseOfDomains[i])
            requestTwoAuto.raise_for_status()
            numberOfDomainsTwo = len(requestTwoAuto.text.split('\n'))
            summaryResult[databaseOfDomains[i]] = numberOfDomainsOne+numberOfDomainsTwo, databaseOfRootDomains[i]

        print(summaryResult)
        with open('new.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file )
            for key, value in summaryResult.items():
                writer.writerow([key, value])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainDesing = Application()
    mainDesing.show()
    sys.exit(app.exec_())