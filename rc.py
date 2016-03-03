# -*- coding: utf-8 -*-
"""
Created on Tue Jul 09 15:43:20 2013

Plothilfen, abschrieben aus der TBrc meiner Diss
"""

from __future__ import division

import pylab, csv

phi = (1+pylab.sqrt(5))/2

pylab.rcParams['figure.figsize'] = (phi*6, 6) # inches
pylab.rcParams['lines.linewidth'] = 2.0


def color(r, g, b):
    return (r/255, g/255, b/255)
#CD-Handbuch Mai 2001, 1.3 FARBEN
fhg_blau  = color( 31, 130, 192) #  3
fhg_lila  = color( 57,  55, 139) #  8
fhg_rot   = color(226,   0,  26) # 10
fhg_orange= color(242, 148,   0) # 15
fhg_gelb  = color(255, 220,   0) # 19
fhg_ggruen= color(177, 200,   0) # 23
fhg_gruen = color( 23, 156, 125) # 28
fhg_braun = color( 70,  41,  21) # 31
fhg_blgrau= color(  0, 110, 146) # 35
fhg_grau  = color(168, 175, 175) # 36

color_cycle = [fhg_gruen, fhg_orange, fhg_blau, fhg_rot, fhg_lila, fhg_blgrau, fhg_gelb, fhg_rot, fhg_ggruen]
color_cycle = [tuple([c*255 for c in color]) for color in color_cycle]
color_cycle = [ "#%02x%02x%02x"%color for color in color_cycle]
pylab.rcParams['axes.color_cycle'] = color_cycle

def readfile(filename, cols):
    '''read $filename as csv, expecting $cols entries per row'''
    reader = csv.reader(open(filename, 'rb'), delimiter="\t")
    rows = [row for row in reader]
    rows = filter(lambda x: len(x) == cols, rows)

    Data = [[float(row[col]) for row in rows] for col in range(cols)]

    return Data

if __name__ == "__main__":
    lorder = lambda x, x0: -2*(x-x0)/(1+(x-x0)**2)/pylab.pi
    xs = map(lambda x: x-50, range(100))
    ys = map(lambda x: lorder(x/5,-1), xs)

    ### Ab hier kopieren als Default-Abbildung ###

    fig = pylab.figure()
    ax = fig.add_subplot(111)
    for i in range(10):
        ax.plot(xs, [y+i/10 for y in ys], label="Phase %d"%i)

    ax.set_xlabel(r"$x$-Achse / \textmu m")
    ax.set_ylabel(r"$\frac{\mathrm{d}}{\mathrm{d}x}\mathrm{Lor}(x)$")
    ax.set_xlim([min(xs), max(xs)])
    #ax.set_ylim([phi*min(ys), phi*max(ys)])

    pylab.legend()

    pylab.show()