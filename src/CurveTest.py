#!/usr/bin/env python

# The Python version of qwt-*/examples/cpuplot


import os
import sys

from PyQt4 import Qt
from PyQt4 import QtGui
from PyQt4 import QtCore
import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *


#-- cpustat.cpp --#

class CpuStat:

    User = 0
    Nice = 1
    System = 2
    Idle = 3
    counter = 0
    
    def __init__(self):
        self.procValues = self.__lookup()

    # __init__()
  
    def statistic(self):
        values = self.__lookup()
        userDelta = 0.0
        for i in [CpuStat.User, CpuStat.Nice]:
            userDelta += (values[i] - self.procValues[i])
        systemDelta = values[CpuStat.System] - self.procValues[CpuStat.System]
        totalDelta = 0.0
        for i in range(len(self.procValues)):
            totalDelta += (values[i] - self.procValues[i])
        self.procValues = values
        return 100.0*userDelta/totalDelta, 100.0*systemDelta/totalDelta

    # statistics()
    
    def upTime(self):
        result = Qt.QTime()
        for item in self.procValues:
            result = result.addSecs(item/100)
        return result

    # upTime()

    def __lookup(self):
        for line in open("/proc/stat"):
            words = line.split()
            if words[0] == "cpu" and len(words) >= 5:
                return [float(w) for w in words[1:]]
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

    def __init__(self, *args):
        Qwt.QwtPlot.__init__(self, *args)

        self.curves = {}
        self.data = {}
        self.timeData = 1.0 * arange(HISTORY-1, -1, -1)
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
        self.setAxisScale(Qwt.QwtPlot.xBottom, -HISTORY, 0)
        #self.setAxisLabelRotation(Qwt.QwtPlot.xBottom, -50.0)
        self.setAxisLabelAlignment(
            Qwt.QwtPlot.xBottom, Qt.Qt.AlignLeft | Qt.Qt.AlignBottom)

        #self.setAxisTitle(Qwt.QwtPlot.yLeft, "Cpu Usage [%]")
        self.setAxisScale(Qwt.QwtPlot.yLeft, 0, 100)

        #background = Background()
        #background.attach(self)

        #pie = CpuPieMarker()
        #pie.attach(self)
        
        '''
        curve = CpuCurve('System')
        curve.setColor(Qt.Qt.red)
        curve.attach(self)
        self.curves['System'] = curve
        '''
        self.data['System'] = zeros(HISTORY, Float)

        '''
        curve = CpuCurve('User')
        curve.setColor(Qt.Qt.blue)
        curve.setZ(curve.z() - 1.0)
        curve.attach(self)
        self.curves['User'] = curve
        '''
        self.data['User'] = zeros(HISTORY, Float)
        

        curve = CpuCurve('Total')
        curve.setColor(Qt.Qt.red)
        curve.setZ(curve.z() - 2.0)
        curve.attach(self)
        self.curves['Total'] = curve
        
        self.data['Total'] = zeros(HISTORY, Float)

        '''
        curve = CpuCurve('Idle')
        curve.setColor(Qt.Qt.darkCyan)
        curve.setZ(curve.z() - 3.0)
        curve.attach(self)
        self.curves['Idle'] = curve
        self.data['Idle'] = zeros(HISTORY, Float)
        '''

        #self.showCurve(self.curves['System'], True)
        #self.showCurve(self.curves['User'], True)
        self.showCurve(self.curves['Total'], False)
        #self.showCurve(self.curves['Idle'], False)

        self.startTimer(1000)

        self.connect(self,
                     Qt.SIGNAL('legendChecked(QwtPlotItem*, bool)'),
                     self.showCurve)
        self.replot()

    # __init__()
    
    def timerEvent(self, e):
        for data in self.data.values():
            data[1:] = data[0:-1]
        self.data["User"][0], self.data["System"][0] = self.cpuStat.statistic()
        self.data["Total"][0] = self.data["User"][0] + self.data["System"][0]
        #self.data["Idle"][0] = 100.0 - self.data["Total"][0]

        self.timeData += 1.0

        self.setAxisScale(
            Qwt.QwtPlot.xBottom, self.timeData[-1], self.timeData[0])
        #self.setAxisScale(Qwt.QwtPlot.xBottom, HISTORY, 0)
        self.curves["Total"].setData(self.timeData, self.data["Total"])

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
