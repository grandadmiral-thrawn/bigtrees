import sys
import csv
import math
import decimal 
import matplotlib.pyplot as plt
import numpy as np
import os
import itertools
import pymssql

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, "bigtrees"))

import biggest_trees as bt

def genrange():
    """ generates a range of 
    the correct precision for a test"""

    r = bt.drange(0,500,10)
    return r

def runrange():
    y = genrange()
    ranger = [['SEGI', x, round(bt.segi(x),5), 'PISI', round(bt.pisi(x),5),
    'CHNO', round(bt.chno(x),5), 'THPL', round(bt.rockythpl(x),5), 
    round(bt.andrewsthpl(x),5), 'PSME', round(bt.rockypsme(x),5), 
    round(bt.andrewspsme(x,'RS13'),5), 'ABPR', round(bt.abpr(x),5)] for x in y]
    print ranger

def makepretty():
    y = genrange()
    u = [x for x in y]
    
    seg = [round(bt.segi(x),3) for x in u]
    pis = [round(bt.pisi(x),3) for x in u]
    chn = [round(bt.chno(x),3) for x in u]
    rok = [round(bt.rockythpl(x),3) for x in u]
    andy = [round(bt.andrewsthpl(x),3) for x in u]
    rokp = [round(bt.rockypsme(x),3) for x in u]
    andp = [round(bt.andrewspsme(x,'RS13'),3) for x in u]
    ab = [round(bt.abpr(x),3) for x in u]
    
    fig = plt.figure()
    segip, = plt.plot(u, seg,'r-',label = "SEGI")
    pisip, = plt.plot(u, pis,'b-', label = "PISI")
    chnop, = plt.plot(u, chn,'g-', label = "CHNO")
    rockyth, = plt.plot(u, rok,'k-', label = "R.THPL")
    andrewsth, = plt.plot(u, andy,'r--', label = "A.THPL")
    rockydoug, = plt.plot(u, rokp,'b--', label = "R.PSME")
    andrewsdoug, = plt.plot(u, andp,'g--', label = "A.PSME")
    abprp, = plt.plot(u, ab,'k--', label = "ABPR")
    plt.xlabel('dbh ranges 0-500 cm')
    plt.ylabel('generated ranges for big trees')
    plt.legend(bbox_to_anchor=(0., 1., 1., .102), loc="best",
           ncol=2, borderaxespad=0.)
    
    fig.legend("best",[segip, pisip, chnop, rockyth, andrewsth, rockydoug, andrewsdoug, abprp],["SEGI","PISI","CHNO","RTHPL","ATHPL","RPSME","APSME","ABPR"])
    plt.show()


def runtests():
    try:
        assert bt.segi(100) > 1.0
    except Exception as exc:
        print("error on SEGI 100 as %s\n") %exc

    try:
        assert bt.pisi(100) > 1.0
    except Exception as exc:
        print("error on PISI 100 as %s\n") %exc


    try:
        assert bt.chno(100) > 1.0
    except Exception as exc:
        print("error on CHNO 100 as %s\n") %exc

    try:
        assert bt.rockythpl(100) > 1.0
    except Exception as exc:
        print("error on ROCKYTHUJA 100 as %s\n") %exc

    try:
        assert bt.andrewsthpl(100) > 1.0
    except Exception as exc:
        print("error on THUJA 100 as %s\n") %exc

    try:
        assert bt.rockypsme(100) > 1.0
    except Exception as exc:
        print("error on ROCKYPSME 100 as %s\n") %exc

    try:
        assert bt.andrewspsme(100,'RS13') > 1.0
    except Exception as exc:
        print("error on PSME 100 as %s\n") %exc

    try:
        assert bt.abpr(100) > 1.0
    except Exception as exc:
        print("error on ABPR 100 as %s\n") %exc

"""
EXECUTION STUFF BELOW (running tests)
"""
runtests()
makepretty()
