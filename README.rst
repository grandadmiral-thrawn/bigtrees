bigtrees
========

The bigtrees/ source contains Python functions for computing biomass for
trees > 150 cm in the long-term research plots. Of approximately 1.3
million unique instances of trees, those larger than 150 cm diameter
number roughly 3300. However, their biomass is a significant component
of the plots on which they are located and many equations are badly
calibrated for this range. The bigtrees/ tools are a starting point for
us to iterate through these large diameter trees and find the best
equations in our databases (TV00908, Gody/Lutz/Acker papers, Jenkins,
maybe others?)

Currently, bigtrees/ is implemented in python 2.7.8 on Mac OS X
Mavericks.

Using Pip or Conda, you must install the packages csv, math, decimal,
numpy, os, itertools, and pymssql to run bigtrees. If you wish to use
the plotting functions (not in the "run script") also install
MatPlotLib. If you cannot install these, or need a different bridge to
the MS SQL server, please edit the preamble to comment out or change the
modules you do not have.

::

        import csv
        import math
        import decimal 
        import matplotlib as plt
        import numpy as np
        import os
        import itertools
        import pymssql

If you use itertools in Python 3 be aware that some of the functionality
may not be the same as in 2.7.8. This toolkit does not attempt to be
forward compatible. But if you want to make it so, send me a pull
request!

Usage
-----

download the bigtrees source code and place it in a directory of your
choosing run at terminal as

::

        python biggest_trees.py

It should complete in almost "no time".

References
----------

Bigtreesource.csv contains a list of the equations used. This is easier
than reading them out of the code. A source list will be provided later
(soon, I hope!)

Output
------

In the writeoutput(cursor) function, you have the ability to change the
name of the output file. At the moment it is "bigtrees\_tp001\_v3.csv".
The name of this file has no effect on the program's running.

Quality Level Descriptions
--------------------------

Big Tree Biomass Generators These functions require an input of DBH,
species, and stand id. To obtain some test data, visit:
http://andrewsforest.oregonstate.edu/data/abstract.cfm?dbcode=Tp001

Notes: \* x is dbh, in cm \* "big trees" is any trees with cm dbh > 150
cm. \* equation priority: First select the best notch in Tier 1, then \*
select the best notch in Tier 2. Record as T1.1.T2.3, for example.

Tier 1: 1. same species, same dbh range, same geo-region 2. same
species, same dbh range, different geo-region 3. different species, same
dbh range, same geo-region 4. same species, different dbh range, same
geo-region 5. different species, same dbh range, different geo-region 6.
same species, different dbh range, different geo-region 7. different
species, different dbh range, different geo-region

Tier 2: 1. same equations used by gody and documented by gody and acker
2. uses a volume -> biomass conversion based on density in harmon's
studies (i.e. TV009, TV010, etc.) for conifers 3. directly calculates
total aboveground biomass 3a. directly calculates total aboveground
biomass but uses a height calculation that may or may not have a
reference to that species 4. sums tree components to get to total
aboveground biomass \* note that 3 is prefered to 4 because in some
cases parts, such as dead branches, may not be explicitly included when
maybe they should 5. calcuates biomass from volume, but we do not have a
density and must approximate with a proxy 6. calculates biomass from
volume for stem only, and we don't have a density, and must use a proxy
In the case of 4, 5 or 6, revisit Tier 1 and possibly step down a notch.
