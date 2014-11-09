#!/usr/bin/env python

"""Big Tree Biomass Generators
These functions require an input of DBH, species, and stand id. 
To obtain some test data, visit: 
http://andrewsforest.oregonstate.edu/data/abstract.cfm?dbcode=Tp001
"""
"""
x is dbh, in cm
"big trees" is any trees with cm dbh > 200 cm.
equation priority: First select the best notch in Tier 1, then 
select the best notch in Tier 2. Record as T1.1.T2.3, for example. 

Tier 1:
1. same species, same dbh range, same geo-region
2. same species, same dbh range, different geo-region
3. different species, same dbh range, same geo-region
4. same species, different dbh range, same geo-region
5. different species, same dbh range, different geo-region
6. same species, different dbh range, different geo-region
7. different species, different dbh range, different geo-region 

Tier 2:
1. same equations used by gody and documented by gody and acker
2. uses a volume -> biomass conversion based on density in
   harmon's studies (i.e. TV009, TV010, etc.) for conifers
3. directly calculates total aboveground biomass 
3a. directly calculates total aboveground biomass but uses a height
    calculation that may or may not have a reference to that species
4. sums tree components to get to total aboveground biomass
* note that 3 is prefered to 4 because in some cases parts, such as
dead branches, may not be explicitly included when maybe they should 
5. calcuates biomass from volume, but we do not have a density and
   must approximate with a proxy
6. calculates biomass from volume for stem only, and we don't have 
   a density, and must use a proxy
In the case of 4, 5 or 6, revisit Tier 1 and possibly step down a notch.
"""
import csv
import math
import decimal 
import matplotlib as plt
import numpy as np
import os
import itertools
import pymssql


def drange(start, stop, step):
    """ define decimal interval range over which to iterate
        note that this is a function generator and does not need
        a return clause.

    for example:
        thisrange = drange(0.0, 250.0, 0.1)
        ranger = [round(x,2) for x in thisrange]
    """
    r = start
    while r < stop:
        yield r
        r+=step

def segi(x):

    """ T1.1.T2.4. these are for sequoia in seq ntl park
    proxy: none
    badness: no foliage
    source: biopak, equation 395
    accuracy: biomass at 0.95, density is stated to be 0.358
    """

    biomass = math.exp(-11.0174 + 2.5907 * math.log1p(float(x)))
    jenkbio = round(0.001*math.exp(-2.2304+2.4435*math.log1p(round(x,2))),4)

    return (biomass, jenkbio)

def pisi(x):
    
    """ 
    T1.1.T2.1. these are sitka spruce in olympic np and northor coastal
    proxy: the height is from pisi on north oregon coastal
    badness: height from oregon coast instead of olympic
    source: documentation from ht4snag
    accuracy: biomass at 0.93, mult by cf factor of 1.0748
    density of wood and bark avg = 0.37 
    """

    # note that all heights are valid at the low-elevation range 
    # for the big trees (HR01-04 and NCNY stands)
    # The equations from TV00908 HAVE ALREADY DONE THE LNLN transform
    woodden = 0.369
    height = 1.37 + 65.2776*(1-math.exp(-0.012361*x)**0.9679)
    biomass = 1.0222*woodden*(0.0003460*x**2.3320)
    jenkbio = round(0.001*math.exp(-2.2304+2.4435*math.log1p(round(x,2))),4)
    """ 
    T1.3.T2.1. these are sitka spruce in olympic np 
    proxy: the height is from pisi on north oregon coastal
    badness: height from oregon coast instead of olympic; bio from coas also
    source: documentation from ht4snag; equations shared with becky fasth
    accuracy: biomass at 0.9
    density of wood and bark avg = 0.37 

    # it appears that this one gets about 2/3 the amount of mass 
    # when taken up to the scale of the one for oly park
    woodden = 0.37
    height = 1.37 + (65.2776*(1-math.exp(-0.012361*x))**0.9679)
    biomass = woodden*(0.2346*height*(0.01*x)**2)

    """

    """
    T1.6.T2.4. these are sitka spruce from central oregon
    proxy: none
    badness: these equations are for the central oregon region
    source: documentation from ht4snag; equations shared with becky fasth
    accuracy: biomass at 0.95
    density of wood and bark avg = 0.36 


    # these equations are only valid between 35 and 283 biomass
    biomass = math.exp(4.871437 + 2.3320*math.log1p(x))  # total stem biomass

    """
    return(biomass, jenkbio)

def chno(x):

    """
    T1.3.T2.1. these are alaska "cedar" in the rocky mountains
    proxy: the rocky-mountain thuja plicata
    badness: not CHNO
    source: from a call to tv009, MRRS as stand, looking for THPL
    accuracy: biomass at 0.99, mult by cf factor of 1.016
    density of wood and bark avg = 0.31 
    """

    woodden = 0.31
    biomass = 1.016*woodden*(0.000186*x**2.4024)
    jenkbio = round(0.001*math.exp(-2.5384+2.4814*math.log1p(round(x,2))),4)

    """ T1.2.T2.4 these are alaska "cedar" in the west cascades
    proxy: none
    badness: valid up to 109 cm only
    source: Biopak 324, 325, 326 via SQL query to TP07202
    accuracy: BSW at 0.969, BSB at 0.832, BST at 0.968 respectively

    biostemwood = math.exp(-10.1534 + 2.5799*math.log1p(x))
    biostembark = math.exp(-11.9695 + 2.3652 * math.log1p(x))
    biostemtotal = math.exp(-10.0153 + 2.5616 * math.log1p(x))

    biomass = biostemwood + biostembark + biostemtotal

    """
    """ T1.6.T2.3a these are alaska "cedar" for general
    proxy: none
    badness: valid up to 43 cm only
    source: BioPak 927 via SQL query to TP07202; height from
    TP01 documentation for ht4snag (for THPL, not CHNO)
    accuracy: height at 0.99 for THPL

    height = 1.37 + (56.9157*(1-math.exp(-0.012625*x))**0.9359)
    biomass = (9.2 + 191.6*(0.01*x)**2)*height

    """
    return(biomass, jenkbio)

def rockythpl(x):

    """T1.1.T2.1. this is THPL for the rocky mountains
    in the stands 'TO11, TO04, AO03'
    proxy: none
    badness: none
    source: TP01 dcoumentation from ht4snag and tv00908
    accuracy: biomass at 0.95, mult by cf factor of 1.016
    """

    woodden = 0.31
    biomass = 1.016*woodden*(0.000186*x**2.4024)
    jenkbio = round(0.001*math.exp(-2.5384+2.4814*math.log1p(round(x,2))),5)
    return(biomass, jenkbio)

def andrewsthpl(x):

    """T1.1.T2.1. this is THPL for the andrews forest based on RS
    in the stand 'RS29'
    proxy: none
    badness: none
    source: TP01 dcoumentation from ht4snag and tv00908
    accuracy: biomass at 0.95, no cf because b0 = 0
    """

    woodden = 0.31
    height = 1.37 + (56.9157*(1-math.exp(-0.012625*x))**0.9359)
    jenkbio = round(0.001*math.exp(-2.5384+2.4814*math.log1p(round(x,2))),5)
    biomass = woodden*(0.218*height*(0.01*x)**2)
    
    """
    T1.4.T2.3. this is THPL for the andrews forest based on RS
    in the stand 'RS29'
    proxy: none
    badness: dbh only up to 119 cm
    source: biopak equations 457
    accuracy: biomass at 0.90

    height = 1.37 + (56.9157*(1-math.exp(-0.012625*x))**0.9359)
    biomass = 1.270 + 0.01501*(x**2*height)
    """

    """
    T1.4.T2.4. this is THPL for the andrews forest based on RS
    in the stand 'RS29'
    proxy: none
    badness: dbh only up to 119 cm
    source: biopak equations 458, 459, 460, 461
    accuracy: 0.99, 0.95, 0.60, 0.93, respectively

    height = 1.37 + (56.9157*(1-math.exp(-0.012625*x))**0.9359)
    biofoliage = 0.298 + 0.00365*(x**2*height)
    biolivebranch = 0.199 + 0.00381*(x**2*height)
    biostemwood = 0.452 + 0.00697*(x**2*height) 
    biostembark =  0.336 + 0.00058*(x**2*height)

    biomass = biofoliage + biolivebranch + biostemwood + biostembark
    """

    return(biomass, jenkbio)

def rockypsme(x):

    """T1.1.T2.1. this is PSME for the rocky mountains
    in the stands 'TO11, TO04, AO03'
    proxy: none
    badness: none
    source: TP01 dcoumentation from ht4snag and tv00908
    accuracy: biomass at 0.96, mult by cf factor of 1.0309
    """

    woodden = 0.45
    biomass = 1.0309*woodden*(0.000215*x**2.4367)
    jenkbio = round(0.001*math.exp(-2.2304+2.4435*math.log1p(round(x,2))),5)
    return(biomass, jenkbio)

def abco(x):

    """T1.1.T2.1. equations for ABCO from SQNP
    applied to SQNP
    proxy: none
    source: TP01 documentation from ht4snag and tv00908
    accuracy: 0.95 
    """
    woodden = 0.417
    biomass = 1.0306*woodden*(0.0000932*x**2.6206)
    jenkbio = round(0.001*math.exp(-2.5384+2.4814*math.log1p(round(x,2))),5)
    return(biomass, jenkbio)

def andrewspsme(x, standid):
    
    """
    T1.1.T2.1. this is PSME for andrews forest
    in the stands RS29, RS34, RS28, RS13, RS25
    T1.2.T2.1. (as it applies to the NFGY)
    proxy: andrews for NFGY in some cases
    badness: none
    source: TP01 dcoumentation from ht4snag and tv00908
    accuracy: biomass at 0.96, no cf factor
    """

    woodden = 0.45

    # height calculation for high elevation
    if standid == "RS28":
        height = 1.37+ 56.8776*(1-math.exp(-0.016381*x))**1.0688

    else:
        # height calcluation low elevation
        height = 1.37 + 76.8553*(1-math.exp(-0.011561*x))**0.9288
        
    # regardless of elevation
    biomass = woodden*(0.2346*height*(0.01*x)**2)
    jenkbio = round(0.001*math.exp(-2.2304+2.4435*math.log1p(round(x,2))),5)
    

    """T1.1.T2.2. this is PSME for "old hja"
    proxy: cascade head instead of andrews forest
    badness: none
    source: TP01 dcoumentation from ht4snag and tv00908
    accuracy: biomass at 0.96, 1.0296 correction factor

    woodden = 0.45
    biomass = 1.0296*woodden*(0.0003091*x**2.3602)
    """

    """
    T1.1.T2.2. this is PSME for cascade head
    proxy: cascade head instead of andrews forest
    badness: none
    source: TP01 dcoumentation from ht4snag and tv00908
    accuracy: biomass at 0.96, 1.0296 correction factor

    woodden - 0.45
    biomass = 1.0296*woodden*(0.0002286*x**2.4247)
    """

    return(biomass,jenkbio)

def pila(x):

    """T1.3.T2.1 PILA from SQNP used in W Cascades
    proxy: location, SQNP, range may be different (unknown)
    badness: potentially too broad
    source: tv009
    accuracy: 0.981
    """

    woodden = 0.396
    biomass = 1.0211*woodden*(0.0000557*x**2.7089)
    jenkbio = round(0.001*math.exp(-2.5356+2.4349*math.log1p(round(x,2))),5)

    return(biomass, jenkbio)

def tshe(x, standid):

    """
    T1.1.T2.2. TSHE from the COAS applied to all west
    proxy: coastal west for all west...
    -- the MRRS ones appear to be less accurate, skipping for now.
    badness: may not be perfect for inland
    source: tv009, ht from ht4snag
    accuracy: 0.953
    """    
    woodden = 0.42

    if standid in ["RS04", "RS18", "CMNF", "RS21", "RS22", "RS23", "RS28"]:
        # for elevations > 1000
        height = 1.37+57.1592*(1-math.exp(-0.023814*x))**1.5623
    else:
        height = 1.37+61.5681*(1-math.exp(-0.017278*x))**1.0723

    biomass = woodden*(0.2723*height*(0.01*x)**2) 

    jenkbio = round(0.001*math.exp(-2.5384+2.4814*math.log1p(round(x,2))),5)

    return(biomass, jenkbio)

def abpr(x):

    """T1.1.T2.1. equations for ABPR from NFGY
    applied to GFMY
    proxy: none
    source: TP01 documentation from ht4snag and tv00908
    accuracy: 0.99 for the lnln based equation
    """

    woodden = 0.438
    biomass = 1.0171*woodden*(0.000123*x**2.5812)
    jenkbio = round(0.001*math.exp(-2.5384+2.4814*math.log1p(round(x,2))),5)
    """T1.1.T2.3a equations for ABPR from NFGY
    but the height measurement is for PSME
    proxy: PSME
    source: TP01 documentation from ht4snag and tv00908
    accuracy: --?

    woodden = 0.438
    height = 1.37 + (78.6035*(1-math.exp(-0.01333*x))**1.1851)
    biomass = woodden*(0.2974*height*(0.01*x)**2)

    """

    return(biomass,jenkbio)

def formconnection():
    """
    Connect to the MS SQL server and execute a query to get the data 
    which contains trees with DBH > 200 cm.
    """

    # Connect to MSSQL Server
    conn = pymssql.connect(server="stewartia.forestry.oregonstate.edu:1433",
                            user="petersonf",
                            password="D0ntd1sATLGA!!",
                            database="FSDBDATA")
 
    # Create a database cursor
    cursor = conn.cursor()
 
    # Replace this nonsense with your own query :)
    query = """SELECT fsdbdata.dbo.tp00101.treeid, fsdbdata.dbo.tp00101.psp_studyid,
            fsdbdata.dbo.tp00101.species, fsdbdata.dbo.tp00101.standid, fsdbdata.dbo.tp00102.treeid, 
            fsdbdata.dbo.tp00102.dbh, fsdbdata.dbo.tp00102.tree_vigor FROM fsdbdata.dbo.tp00101 
            LEFT JOIN fsdbdata.dbo.tp00102 
            ON fsdbdata.dbo.tp00101.treeid = fsdbdata.dbo.tp00102.treeid
            WHERE fsdbdata.dbo.tp00102.dbh > 150 
            ORDER BY fsdbdata.dbo.tp00102.treeid ASC"""
 
    # Execute the query
    cursor.execute(query)
 
    return cursor

def caseof(species, x, standid):

    options = {"SEGI":segi(x),
                "ABPR": abpr(x),
                "CHNO": chno(x),
                "PISI": pisi(x),
                "PILA": pila(x),
                "ABCO": abco(x),
                "ABMA": abco(x),
                "TSHE": tshe(x, standid),
                "PSME": [andrewspsme(x,standid), rockypsme(x)],
                "THPL": [andrewsthpl(x), rockythpl(x)],}

    if species == "PSME":
        if standid != "MRRS":
            (b,b1)= options[species][0]
        else: 
            (b,b1) = options[species][1]
    elif species == "THPL":
        if standid != "MRRS":
            (b,b1) = options[species][0]
        else: 
            (b,b1) = options[species][1]
    else:
        (b,b1) = options[species]
    return (b,b1)

def writeoutput(cursor):

    # Go through the results row-by-row and write the output to a CSV file
    # (QUOTE_NONNUMERIC applies quotes to non-numeric data; change this to
    # QUOTE_NONE for no quotes.  See https://docs.python.org/2/library/csv.html
    # for other settings options)
    with open("bigtrees_tp001_v3.csv", "w") as outfile:
        writer = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC, delimiter = ",")
        writer.writerow(["PSP_STUDYID", "STANDID", "SPECIES", "TREEID", "DBH", "BEST_BIOMASS", "JENKINS_BIOMASS"])
        for row in cursor:
            treeid = str(row[0])

            species = str(row[2]).strip()
            
            dbh = float(row[5])
            
            standid = str(row[3])
            
            study = str(row[1])
            
            (biomass, jenkbio) = caseof(species, dbh, study)
            
            myrow = [study, standid, species, treeid, dbh, round(biomass,4), round(jenkbio,4)]
            
            writer.writerow(myrow)
        #writer.writerow(row)

c = formconnection()
writeoutput(c)
'''
Extract the TREEID, SPECIES, DBH, STAND, STUDY...
If Bio can be computed from volume based on density, put it in, otherwise None
If Bio can be computed as a total put it in, otherwise None
If Bio can be computed as a sum of its parts, put it in, otherwise None
If Bio can be computed as a sum of its parts, put the parts in the last three columns
'''

