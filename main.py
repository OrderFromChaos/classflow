from graphfuncs import importData, constructGraph
import json
from graphviz import Digraph

### Hyperparameters
# The set of majors you want to draw a graph for.
MAJOR = {'PHYS','CS','MATH'}
SPECIALFLAG = None # If SPECIALFLAG is set to 'all' instead of None, you can get a graph of every class at UCR.

# Whether to remove classes that aren't a part of the requested major and instead list them as prereqs under
#    the specific class box they're for.
REMOVENONMAJOR = False

# Whether to remove 2xx+ (grad) classes
REMOVEGRADCLASS = True

# Whether to color classes provided in the REQUIRED set.
# REQUIRED classes are colored gold, else colored light blue.
REQUIREMENTCOLOR = False
REQUIRED = {'PHYS039','MATH009A','MATH009B','MATH009C','CHEM001A',
                'CHEM001B','CHEM001C','CS010','MATH010A','MATH010B','MATH046',
                'PHYS041A','PHYS041B','PHYS041C','PHYS130A','PHYS130B','PHYS132',
                'PHYS135A','PHYS135B','PHYS156A','PHYS156B','PHYS139L','PHYS142W'}
# TODO: Add ability to control colors of REQUIRED and ELECTIVE courses

# Whether to enable dark theme and what that means color-wise.
DARKTHEME = True
DARKTHEMECOLORS = {'background':'#043742',
                   'boxes':'#6a8690',
                   'lines':'#3fc6b4',
                   'textcolor':'white'}





### Main program
if REMOVENONMAJOR:
    assert SPECIALFLAG is None, 'REMOVENONMAJOR cannot be true if SPECIALFLAG = "all"'
courseList = importData('./ucr-course-graph/data')
dot = constructGraph(courseList,
                     REMOVEGRADCLASS=REMOVEGRADCLASS,
                     REQUIREMENTCOLOR=REQUIREMENTCOLOR,
                     REQUIRED=REQUIRED,
                     REMOVENONMAJOR=REMOVENONMAJOR,
                     MAJOR=MAJOR,
                     SPECIALFLAG=SPECIALFLAG,
                     DARKTHEME=DARKTHEME,
                     DARKTHEMECOLORS=DARKTHEMECOLORS)

dot.render(filename='./generated/out',view=True,format='png')
