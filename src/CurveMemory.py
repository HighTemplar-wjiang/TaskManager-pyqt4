#!/usr/bin/env python

# The Python version of qwt-*/examples/cpuplot


import os
import sys

from PyQt4 import Qt
from PyQt4 import QtGui
from PyQt4 import QtCore
import PyQt4.Qwt5 as Qwt
from numpy import *
# from PyQt4.Qwt5.anynumpy import *


#-- cpustat.cpp --#

class MemoryStat:
    @staticmethod
    def statistic():
        values = {}
        for line in open("/proc/meminfo"):
            words = line.split(":")
            if words[0].find("MemTotal") != -1:
                memTotal = float(words[1].strip().split()[0])
                values.update({"MemTotal":memTotal})
                continue
            if words[0].find("MemFree") != -1:
                memFree = float(words[1].strip().split()[0])
                values.update({"MemFree":memFree})
                continue
            if words[0].find("SwapTotal") != -1:
                swapTotal = float(words[1].strip().split()[0])
                values.update({"SwapTotal":swapTotal})
                continue
            if words[0].find("SwapFree") != -1:
                swapFree = float(words[1].strip().split()[0])
                values.update({"SwapFree":swapFree})
                continue
        values.update({"MemUsage":str(100 * (memTotal - memFree) / memTotal)})
        values.update({"SwapUsage":str(100 * (swapTotal - swapFree) / swapTotal)})
        return values

    # statistics()

# class MemoryStat

class MemoryCurve(Qwt.QwtPlotCurve):

    def __init__(self, *args):
        Qwt.QwtPlotCurve.__init__(self, *args)
        self.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)

    # __init__()

    def setColor(self, color):
        c = Qt.QColor(color)
        self.setPen(c)

    # setColor()

# class MemoryCurve

HISTORY = 60    
class MemoryPlot(Qwt.QwtPlot):

    colors  = [Qt.Qt.red, Qt.Qt.blue, Qt.Qt.darkGreen, 
               Qt.Qt.darkYellow, Qt.Qt.darkRed, Qt.Qt.darkGray, 
               Qt.Qt.green, Qt.Qt.darkMagenta, Qt.Qt.darkCyan,
               Qt.Qt.darkBlue, Qt.Qt.gray, Qt.Qt.cyan,
               Qt.Qt.lightGray, Qt.Qt.magenta, Qt.Qt.black, 
               Qt.Qt.white, Qt.Qt.yellow, Qt.Qt.transparent]

    def __init__(self, *args):
        Qwt.QwtPlot.__init__(self, *args)

        self.curves = {}
        self.data = {}
        self.timeData = 1.0 * arange(0, HISTORY, 1)

        self.setAutoReplot(False)

        self.plotLayout().setAlignCanvasToScales(True)
        self.setAxisScale(Qwt.QwtPlot.xBottom, HISTORY, 0)
        self.setAxisScale(Qwt.QwtPlot.yLeft, 0, 100)
        self.setAxisLabelAlignment(
            Qwt.QwtPlot.xBottom, Qt.Qt.AlignLeft | Qt.Qt.AlignBottom)

        grid = Qwt.QwtPlotGrid()
        grid.enableXMin(True)
        grid.enableYMin(True)
        grid.setMajPen(Qt.QPen(Qt.Qt.black, 0, Qt.Qt.DotLine));
        grid.setMinPen(Qt.QPen(Qt.Qt.gray, 0 , Qt.Qt.DotLine));
         
        grid.attach(self)
        
        stat = MemoryStat.statistic()

        self.data["MemTotal"] = zeros(HISTORY, float)
        self.data["MemFree"] = zeros(HISTORY, float)
        self.data["SwapTotal"] = zeros(HISTORY, float)
        self.data["SwapFree"] = zeros(HISTORY, float)

        curve = MemoryCurve("Memory")
        curve.setColor(self.colors[0])
        curve.attach(self)
        self.curves["Memory"] = curve
        self.data["Memory"] = zeros(HISTORY, float)

        curve = MemoryCurve("Swap")
        curve.setColor(self.colors[1])
        curve.attach(self)
        self.curves["Swap"] = curve
        self.data["Swap"] = zeros(HISTORY, float)

        self.startTimer(1000)
        self.replot()

    # __init__()
    
    def timerEvent(self, e):
        for data in self.data.values():
            data[1:] = data[0:-1]

        stat = MemoryStat.statistic()
        self.data["MemTotal"][0] = stat["MemTotal"]
        self.data["MemFree"][0] = stat["MemFree"]
        self.data["SwapTotal"][0] = stat["SwapTotal"]
        self.data["SwapFree"][0] = stat["SwapFree"]
        
        self.data["Memory"][0] = stat["MemUsage"]
        self.curves["Memory"].setData(self.timeData, self.data["Memory"])

        self.data["Swap"][0] = stat["SwapUsage"]
        self.curves["Swap"].setData(self.timeData, self.data["Swap"])
        
        self.replot()

    # timerEvent()

    def memoryPlotCurve(self, key):
        return self.curves[key]

    # memoryPlotCurve()
    
# class MemoryPlot

def make():
    demo = Qt.QWidget()
    demo.setWindowTitle('Memory Plot')
    
    plot = MemoryPlot(demo)
    plot.setTitle("History")
    plot.setMargin(5)

    layout = Qt.QVBoxLayout(demo)
    layout.addWidget(plot)

    demo.resize(600, 400)
    demo.show()
    return demo

# make()


def main(args):
    app = Qt.QApplication(args)
    demo = make()
    QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("GTK+"))
    sys.exit(app.exec_())

# main()


# Admire!
if __name__ == '__main__':
    if 'settracemask' in sys.argv:
        # for debugging, requires: python configure.py --trace ...
        import sip
        sip.settracemask(0x3f)

    main(sys.argv)

# Local Variables: ***
# mode: python ***
# End: ***
