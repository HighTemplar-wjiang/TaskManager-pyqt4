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

class CpuStat:

    User = 0
    Nice = 1
    System = 2
    Idle = 3
    Iowait = 4
    Irq = 5
    Softirq = 6
    counter = 0
    
    def __init__(self):
        self.procValues = self.__lookup()

    # __init__()
  
    def statistic(self):
        result = []
        values = self.__lookup()
        
        for x in xrange(0, len(values)):
            value     = values[x]
            procValue = self.procValues[x]
            busyDelta = 0.0
            for i in xrange(CpuStat.User, CpuStat.System + 1):
                busyDelta += (value[1][i] - procValue[1][i])
            totalDelta = 0.0
            for i in range(len(procValue[1])):
                totalDelta += (value[1][i] - procValue[1][i])
            result += [[value[0], 0 if totalDelta == 0 else 100.0 * busyDelta / totalDelta]]

        self.procValues = values
        return result

    # statistics()
    '''
    def upTime(self):
        result = Qt.QTime()
        for item in self.procValues:
            result = result.addSecs(item/100)
        return result
    '''
    # upTime()

    def __lookup(self):
        values = []
        for line in open("/proc/stat"):
            words = line.split()
            if words[0].find("cpu") != -1 and len(words) >= 5:
                values += [[words[0], [float(w) for w in words[1:]]]]
        return values
    # __lookup

# class CpuStat


#-- cpupiemarker.cpp --#
'''
class CpuPieMarker(Qwt.QwtPlotMarker):
    
    def __init__(self, *args):
        Qwt.QwtPlotMarker.__init__(self, *args)
        self.setZ(1000.0)
        self.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased, True)
        
    # __init__()

    def rtti(self):
        return Qwt.QwtPlotItem.Rtti_PlotUserItem

    # rtti()
    
    def draw(self, painter, xMap, yMap, rect):
        margin = 5
        pieRect = Qt.QRect()
        pieRect.setX(rect.x() + margin)
        pieRect.setY(rect.y() + margin)
        pieRect.setHeight(yMap.transform(80.0))
        pieRect.setWidth(pieRect.height())

        angle = 3*5760/4
        for key in ["User", "System", "Idle"]:
            curve = self.plot().cpuPlotCurve(key)
            if curve.dataSize():
                value = int(5760*curve.y(0)/100.0)
                painter.save()
                painter.setBrush(Qt.QBrush(curve.pen().color(),
                                              Qt.Qt.SolidPattern))
                painter.drawPie(pieRect, -angle, -value)
                painter.restore()
                angle += value
'''
    # draw()

# class CpuPieMarker
                        

#-- cpuplot.cpp --#

class TimeScaleDraw(Qwt.QwtScaleDraw):

    def __init__(self, base, *args):
        Qwt.QwtScaleDraw.__init__(self, *args)
        self.base = base
 
    # __init__()

    def label(self, value):
        return Qwt.QwtText(str(value))

    # label()

# class TimeScaleDraw


class Background(Qwt.QwtPlotItem):

    def __init__(self):
        Qwt.QwtPlotItem.__init__(self)
        self.setZ(0.0)

    # __init__()

    def rtti(self):
        return Qwt.QwtPlotItem.Rtti_PlotUserItem

    # rtti()

    def draw(self, painter, xMap, yMap, rect):
        c = Qt.QColor(Qt.Qt.white)
        r = Qt.QRect(rect)

        for i in range(100, 0, -10):
            r.setBottom(yMap.transform(i - 10))
            r.setTop(yMap.transform(i))
            painter.fillRect(r, c)
            c = c.dark(110)

    # draw()

# class Background


class CpuCurve(Qwt.QwtPlotCurve):

    def __init__(self, *args):
        Qwt.QwtPlotCurve.__init__(self, *args)
        self.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)

    # __init__()

    def setColor(self, color):
        c = Qt.QColor(color)
        #c.setAlpha(150)

        self.setPen(c)
        #self.setBrush(c)

    # setColor()

# class CpuCurve

HISTORY = 60    
class CpuPlot(Qwt.QwtPlot):

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
        self.cpuStat = CpuStat()

        self.setAutoReplot(False)

        self.plotLayout().setAlignCanvasToScales(True)
        
        #legend = Qwt.QwtLegend()
        #legend.setItemMode(Qwt.QwtLegend.CheckableItem)
        #self.insertLegend(legend, Qwt.QwtPlot.RightLegend)
        
        #self.setAxisTitle(Qwt.QwtPlot.xBottom, "System Uptime [h:m:s]")
        #self.setAxisScaleDraw(
        #    Qwt.QwtPlot.xBottom, TimeScaleDraw(self.cpuStat.upTime()))
        #draw = range(60, -1, -10)
        #self.setAxisScaleDraw(Qwt.QwtPlot.xBottom, TimeScaleDraw(60))
        self.setAxisScale(Qwt.QwtPlot.xBottom, HISTORY, 0)
        #self.setAxisLabelRotation(Qwt.QwtPlot.xBottom, -50.0)
        self.setAxisLabelAlignment(
            Qwt.QwtPlot.xBottom, Qt.Qt.AlignLeft | Qt.Qt.AlignBottom)

        #self.setAxisTitle(Qwt.QwtPlot.yLeft, "Cpu Usage [%]")
        self.setAxisScale(Qwt.QwtPlot.yLeft, 0, 100)

        grid = Qwt.QwtPlotGrid()
        grid.enableXMin(True)
        grid.enableYMin(True)
        grid.setMajPen(Qt.QPen(Qt.Qt.black, 0, Qt.Qt.DotLine));
        grid.setMinPen(Qt.QPen(Qt.Qt.gray, 0 , Qt.Qt.DotLine));
         
        grid.attach(self)

        #background = Background()
        #background.attach(self)

        #pie = CpuPieMarker()
        #pie.attach(self)
        
        stat = self.cpuStat.statistic()
        for x in xrange(1, len(stat)):
            curve = CpuCurve(stat[x][0])
            curve.setColor(self.colors[x])
            curve.attach(self)
            self.curves[stat[x][0]] = curve
            self.data[stat[x][0]] = zeros(HISTORY, float)
            self.showCurve(self.curves[stat[x][0]], False)

        curve = CpuCurve('Total')
        curve.setColor(self.colors[0])
        #curve.setZ(curve.z() - 2.0)
        curve.attach(self)
        self.curves['Total'] = curve
        self.data['Total'] = zeros(HISTORY, float)
        self.showCurve(self.curves['Total'], False)

        #self.showCurve(self.curves['System'], True)
        #self.showCurve(self.curves['User'], True)
        #self.showCurve(self.curves['Idle'], False)

        self.startTimer(1000)

        #self.connect(self,
        #             Qt.SIGNAL('legendChecked(QwtPlotItem*, bool)'),
        #             self.showCurve)
        self.replot()

    # __init__()
    
    def timerEvent(self, e):
        for data in self.data.values():
            data[1:] = data[0:-1]

        stat = self.cpuStat.statistic()
        self.data["Total"][0] = stat[0][1]
        self.curves["Total"].setData(self.timeData, self.data["Total"])

        for x in xrange(1, len(stat)):
            self.data[stat[x][0]][0] = stat[x][1]
            self.curves[stat[x][0]].setData(self.timeData, self.data[stat[x][0]])
        
        #self.setAxisScale(Qwt.QwtPlot.xBottom, HISTORY, 0)

        self.replot()

    # timerEvent()
    
    def showCurve(self, item, on):
        #item.setVisible(on)
        #widget = self.legend().find(item)
        #if isinstance(widget, Qwt.QwtLegendItem):
        #    widget.setChecked(on)
        #self.replot()
        pass

    # showCurve()

    def cpuPlotCurve(self, key):
        return self.curves[key]

    # cpuPlotCurve()
    
# class CpuPlot

def make():
    demo = Qt.QWidget()
    demo.setWindowTitle('Cpu Plot')
    
    plot = CpuPlot(demo)
    plot.setTitle("History")
    plot.setMargin(5)
    
    label = Qt.QLabel("Press the legend to en/disable a curve", demo)

    layout = Qt.QVBoxLayout(demo)
    layout.addWidget(plot)
    layout.addWidget(label)

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
