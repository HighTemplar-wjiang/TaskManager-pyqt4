import sys, os, time, thread
from numpy import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qwt5 import *
from MainWindow import *
from ProcStat import *


class TaskMgr(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(TaskMgr, self).__init__()
        self.setupUi(self)

        QObject.connect(self.pushButton_shutdown, SIGNAL("clicked()"), self.__poweroff)
        QObject.connect(self.pushButton_reboot, SIGNAL("clicked()"), self.__reboot)
        QObject.connect(self.pushButton_kill, SIGNAL("clicked()"), self.__kill)
        
        paletteColor = self.label_CPU_Total.palette()
        paletteColor.setColor(QPalette.WindowText, QColor(CpuPlot.colors[0]))
        self.label_CPU_Total.setPalette(paletteColor)

        self.label_CPU_Cores.setText("")
        self.label_CPU_list = {}

        keys = self.qwtPlot_CPU.data.keys()
        for x in xrange(0, len(keys)):
            key = keys[x]
            if str(key).find("cpu") == 0:
                paletteColor = self.label_CPU_Total.palette()
                paletteColor.setColor(QPalette.WindowText, 
                    QColor(CpuPlot.colors[int(str(key).strip("cpu")) + 1]))
                label_CPU = QtGui.QLabel(self.tab_mem)
                label_CPU.setGeometry(QtCore.QRect(20 + 100 * (x - 1), 235, 321, 31))
                label_CPU.setText(str(key).upper())
                label_CPU.setPalette(paletteColor)
                self.label_CPU_list.update({str(key):label_CPU})

        paletteColor = self.label_CPU_Total.palette()
        paletteColor.setColor(QPalette.WindowText, QColor(CpuPlot.colors[0]))
        self.label_mem_usage.setPalette(paletteColor)

        paletteColor = self.label_CPU_Total.palette()
        paletteColor.setColor(QPalette.WindowText, QColor(CpuPlot.colors[1]))
        self.label_swap_usage.setPalette(paletteColor)

        self.tableWidget_process.verticalHeader().setVisible(False)
        self.tableWidget_process.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget_process.setHorizontalHeaderLabels(
            ["PID".center(10), "PPID".center(10), "Name".center(38), "St.", "Pri.".center(7), "Memory(KB)".center(15)])
        self.tableWidget_process.resizeColumnsToContents()
        self.tableWidget_process.setSortingEnabled(True)

        self.tableWidget_module.verticalHeader().setVisible(False)
        self.tableWidget_module.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget_module.setHorizontalHeaderLabels(["Name".center(50), "Memory(KB)".center(15), "Usage"])
        self.tableWidget_module.resizeColumnsToContents()
        self.tableWidget_module.setSortingEnabled(True)

        self.procStat = ProcStat()
        self.statInfo = {}

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1000)


    def __displayInfo(self):
        self.label_CPU_name.setText(self.statInfo["CPUInfo"]["name"])
        self.label_CPU_type.setText(self.statInfo["CPUInfo"]["type"])
        self.label_CPU_freq.setText(self.statInfo["CPUInfo"]["frequency"] + " MHz")
        self.label_OS_type.setText(self.statInfo["OSInfo"]["type"])
        self.label_OS_version.setText(self.statInfo["OSInfo"]["version"])
        self.label_GCC_version.setText(self.statInfo["OSInfo"]["GCCversion"])


    def __displaySources(self):
        try:
            x = numpy.arange(0, 60, 1)
            y = x * 0
            curve = QwtPlotCurve()
            curve.setData(x, y)
            curve.attach(self.qwtPlot_CPU)
        except:
            print("Exception: TaskMgr.__displaySources()")
            print(sys.exc_info())


    def __displayProcs(self):
        try:
            rows_new = len(self.statInfo["ProcInfos"])
            self.tableWidget_process.setRowCount(rows_new)
            for x in xrange(0, rows_new):
                item = QTableWidgetItem()
                item.setData(QtCore.Qt.DisplayRole, int(self.statInfo["ProcInfos"][x]["pid"]))
                self.tableWidget_process.setItem(x, 0, item)

                item = QTableWidgetItem()
                item.setData(QtCore.Qt.DisplayRole, int(self.statInfo["ProcInfos"][x]["ppid"]))
                self.tableWidget_process.setItem(x, 1, QTableWidgetItem(item))

                self.tableWidget_process.setItem(x, 2, QTableWidgetItem(self.statInfo["ProcInfos"][x]["name"]))

                item = QTableWidgetItem(self.statInfo["ProcInfos"][x]["status"])
                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                self.tableWidget_process.setItem(x, 3, item)
                self.tableWidget_process.setItem(x, 4, QTableWidgetItem(self.statInfo["ProcInfos"][x]["priority"]))

                item = QTableWidgetItem()
                item.setData(QtCore.Qt.DisplayRole, int(self.statInfo["ProcInfos"][x]["memory"]) / 1024)
                self.tableWidget_process.setItem(x, 5, item)
        except:
            print("Exception: TaskMgr.__displayProcs()")
            print(sys.exc_info())


    def __displayModules(self):
        try:
            rows = len(self.statInfo["ModuleInfos"])
            self.tableWidget_module.setRowCount(rows)

            for x in xrange(0, rows):
                self.tableWidget_module.setItem(x, 0, QTableWidgetItem(self.statInfo["ModuleInfos"][x]["name"]))

                item = QTableWidgetItem()
                item.setData(QtCore.Qt.DisplayRole, int(self.statInfo["ModuleInfos"][x]["memory"]))
                self.tableWidget_module.setItem(x, 1, QTableWidgetItem(item))

                item = QTableWidgetItem()
                item.setData(QtCore.Qt.DisplayRole, int(self.statInfo["ModuleInfos"][x]["usage"]))
                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                self.tableWidget_module.setItem(x, 2, item)
        except:
            print("Exception: TaskMgr.__displayModules()")
            print(sys.exc_info())


    def __displayAbout(self):
        self.label_about.setText(
            '<pre>'
            '<h3 style = "color:fuchsia">Task Manager</h3>'
            '<h4>&#9;for Linux  version 1.0.0</h4>'
            'This is a task manager for Linux<br><br>'
            'If you want to use the shutdown and reboot function,<br>' 
            'please confirm that you are root.<br><br>'
            'Besides, you can\'t kill other users\' processes<br>'
            'if you are not root.<br>'
            '<br><br>'
            'For more information, please contact me:<br>'
            'Email: weiweijiangcn@gmail.com<br>'
            '<br><br><br><br><br>'
            '<h4 style = "color:fuchsia">Written by Weiwei Jiang in python2.7 with qt4&qwt5<br></h4>'
            '2013/6/15'
            '</pre>'
            )


    def __poweroff(self):
        os.system("poweroff") 


    def __reboot(self):
        os.system("reboot") 


    def __kill(self):
        rowIndex = self.tableWidget_process.currentRow()
        os.system("kill " + str(self.tableWidget_process.item(rowIndex, 0).data(0).toString()))


    def refresh(self):
        try:
            #print "refresh"
            self.procStat.refresh()
            self.statInfo = {}
            self.statInfo.update({"CPUInfo":self.procStat.getCPUInfo()})
            self.statInfo.update({"OSInfo":self.procStat.getOSInfo()})
            #self.statInfo.update({"MemoryInfo:":self.procStat.getMemInfo()})
            #self.statInfo.update({"CPUUsage":self.procStat.getCPUStat()})
            procInfo_stat = self.procStat.getProcInfos()
            self.statInfo.update({"ProcInfos":procInfo_stat[0]})
            self.modInfo_stat = self.procStat.getModuleInfos()
            self.statInfo.update({"ModuleInfos":self.modInfo_stat[0]})

            self.__displayInfo()
            #self.__displaySources()
            self.__displayProcs()
            self.__displayModules()
            self.__displayAbout()

            
            self.label_CPU_Total.setText("Total: " + 
                "%.1f" % self.qwtPlot_CPU.data["Total"][0] + "%")
            
            for key in self.qwtPlot_CPU.data.keys():
                if str(key).find("cpu") == 0:
                    self.label_CPU_list[key].setText(str(key).upper() + ": " + 
                        "%.1f" % self.qwtPlot_CPU.data[key][0] + "%")

            self.label_mem_usage.setText("Memory: Usage " + 
                "%.2f" % ((self.qwtPlot_memory.data["MemTotal"][0] - self.qwtPlot_memory.data["MemFree"][0]) / 1024) + "MB" + 
                "(" +  "%.2f" % (self.qwtPlot_memory.data["Memory"][0]) + "%)     " +
                "Total " + "%.2f" % (self.qwtPlot_memory.data["MemTotal"][0] / 1024) + "MB")
            self.label_swap_usage.setText("Swap: Usage " + 
                "%.2f" % ((self.qwtPlot_memory.data["SwapTotal"][0] - self.qwtPlot_memory.data["SwapFree"][0]) / 1024) + "MB" + 
                "(" +  "%.2f" % (self.qwtPlot_memory.data["Swap"][0]) + "%)     " +
                "Total " + "%.2f" % (self.qwtPlot_memory.data["SwapTotal"][0] / 1024) + "MB")

            self.label_process.setText("Total: " + str(procInfo_stat[1]["Total"]) + "\n" + 
                "Runnable: " + str(procInfo_stat[1]["Runnable"]) + 
                "\tSleeping: " + str(procInfo_stat[1]["Sleeping"]) + 
                "\tDefunct: " + str(procInfo_stat[1]["Defunct"]))

            self.label_module.setText("Total: " + str(self.modInfo_stat[1]))

            curTime  = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))
            CPUUsage = "%.1f" % self.qwtPlot_CPU.data["Total"][0] + "%"
            MemUsage = "%.1f" % self.qwtPlot_memory.data["Memory"][0] + "%"
            #self.label_status.setText("<pre style=\"\">" + "Time: " + curTime + 
            #    "&#9;CPU: " + CPUUsage + "&#9;Memory: " + MemUsage + 
            #    "</pre>")
            self.label_status.setText("Time: " + curTime + 
                "            CPU: " + CPUUsage + "            Memory: " + MemUsage)
        except:
            print("Exception: TaskMgr.refresh()")
            print(sys.exc_info())
        

app = QApplication(sys.argv)
taskManager = TaskMgr()
QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("GTK+"))
taskManager.show()
sys.exit(app.exec_())
