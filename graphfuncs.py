### LIBRARIES / HEADER STUFF {
import json                  # Initial dataset import
from graphviz import Digraph # Primary renderer
### }

### IMPORT FROM DATASET {

def importData(loc): # File location should have all_prereqs and subjects.json in it
    # Get relational prereq data
    with open(loc + '/201740_all_prereqs.json','r') as f:
        data = json.load(f)

    # Define course object (for code readability reasons)
    class course:
        def __init__(self, courseName, preReq, courseID, subject):
            self.courseName = courseName
            self.preReq = preReq
            self.courseID = courseID
            self.subject = subject

    # Now get all of the {'Computer Science': 'CS', ...} information for abbreviation conversion
    with open(loc + '/subjects.json') as f:
        codes = json.load(f)
    lookup = {x['description']:x['code'] for x in codes}

    # This parser is a bit brittle - weaknesses described below.
    def parseAndOr(testString):
        '''Input example:
        
        '''TODO: Input/output example for docstring'''
        # TODO: Allow for an "ignore" input for specific classes if they're causing issues,
        #       or just have better error reporting.
        # Presumption: AND statements are top level, then there are OR statements.
        # So there's nothing like (CS 111 AND CS 11) OR (MATH 031 AND MATH 10A)
        # This is likely, but not guaranteed.
        if testString == dict():
            return dict()
        if len(testString.split('\n')) < 3:
            return dict()
        if 'Score for' in testString: # TODO: EXTREMELY HACKY SOLUTION (ignores all required testing scores)
            return dict()
        mod = testString.split('and\n')
        mod = [x.split('or\n') for x in mod]
        mod = [[y.split('\n') for y in x] for x in mod]

        def classconvert(classname):
            '''TODO: Input/output example for docstring'''
            intermed = classname.split(' ')
            intermed = [' '.join(intermed[:-1]), intermed[-1]]
            # lookup is defined above
            if intermed[0] in lookup:
                return lookup[intermed[0]] + intermed[1]
            else:
                return classname

        try:
            # This is the most horrific list comprehension I've every written, but it works
            mod = [[[
                 classconvert(y[1][y[1].index('Test:')+6:].strip()), # Class name
                 y[2].split(' ')[-1],                                # Grade
                 'NC' if y[3].strip()[:7] == 'May not' else 'C'      # Concurrent allowed?
                    ] if y[0] == '(' else [
                 classconvert(y[0][y[0].index('Test:')+6:].strip()), # Class name
                 y[1].split(' ')[-1],                                # Grade
                 'NC' if y[2].strip()[:7] == 'May not' else 'C'      # Concurrent allowed?
                    ] for y in x] for x in mod]
        except:
            print(testString)
            print(mod)
            raise
        return mod

    courseList = []
    for currentCourse in data:
        try: # Dealing with situations where prereq didn't get written
            mycourse = course(currentCourse['subjectCourse'], parseAndOr(currentCourse['prereqs']), currentCourse['id'], currentCourse['subject'])
        except KeyError:
            mycourse = course(currentCourse['subjectCourse'], dict(), currentCourse['id'], currentCourse['subject'])
        courseList.append(mycourse)

    return courseList
### }

### RENDER GRAPH {

def constructGraph(courseList,REMOVEGRADCLASS,REQUIREMENTCOLOR,REQUIRED,REMOVENONMAJOR,MAJOR,SPECIALFLAG,DARKTHEME,DARKTHEMECOLORS):
    def undergradOnly(courseList):
        numbers = set('0123456789')
        return [x for x in courseList if [y for y in x.courseName if y in numbers][0] in {'0','1'}]

    def selectMajor(courseList,major,flag=None):
        # Use 4-code for major (eg 'PHYS')
        if flag == 'all':
            return [x for x in courseList if x.subject not in {'TFDP','PSYC'}] # These two have errors of some sort
        else:
            return [x for x in courseList if x.subject in major]

    if REMOVEGRADCLASS:
        majorList = undergradOnly(selectMajor(courseList, MAJOR, flag=SPECIALFLAG))
    else:
        majorList = selectMajor(courseList, MAJOR, flag=SPECIALFLAG)

    if DARKTHEME:
        dot = Digraph(comment='classflow test',graph_attr={'rankdir': 'LR', 'ranksep': '2', 'overlap': 'false', 'bgcolor':DARKTHEMECOLORS['background']})
    else:
        dot = Digraph(comment='classflow test',graph_attr={'rankdir': 'LR', 'ranksep': '2', 'overlap': 'false'})

    # Robustly add new classes (on a new line) to the labels inside the nodes
    def safeAddLabel(course_name, new_prereq):
        # Check to see if the node already has a label
        dotline = [x for x in dot.__dict__['body'] if x.split(' ')[0][1:] == course_name and 'label=' in x]
        if dotline: # If non-empty, then node already has a label
            dotline = dotline[-1] # We want the most recent label written
            def addPrereqHTML(label,new_prereq):
                posn = label.index('</FONT')
                return label[:posn] + '<br />' + new_prereq + label[posn:]
            # I have literally no idea why the ']' bug happens; I think it's a dot issue
            newlabel = addPrereqHTML(dotline[dotline.index('label=')+6:] if dotline[-1] != ']' else dotline[dotline.index('label=')+6:-1],new_prereq)
            dot.node(course_name,label=newlabel)
        else: # No current label (or node doesn't exist), so initialize it
            dot.node(course_name,label='<' + course_name + '<br /><FONT POINT-SIZE="10">' + new_prereq +'</FONT>>')

    # Define how to draw between courses (with all the relevant conditions)
    def requisiteLine(fromCourse,toCourse,graph,fromOrGroup=False,**args):
        """fromCourse example: "['ANTH001', 'D-', 'NC']"
           toCourse example: "course" object with courseName, etc.
           Creates nodes on both ends, then draws the requisite line between the two of them.
           Also references the global REQUIRED list"""

        shape = 'box'

        ### ALTERNATE ROUTE: If one of the edges isn't a part of the major, instead make a label under the
        ### class pointed to, then ignore the edge initialization
        if REMOVENONMAJOR:
            # Uses same code as not REMOVENONMAJOR, but intelligently changes the iterator
            numbers = set('0123456789')
            for i,x in enumerate(fromCourse[0]):
                if x in numbers:
                    index = i
                    break
            subj = fromCourse[0][:index]
            iterator = [fromCourse[0],toCourse.courseName] if subj in MAJOR else [toCourse.courseName]
            # Create nodes
            if REQUIREMENTCOLOR:
                for toNode in iterator:
                    if toNode in REQUIRED:
                        graph.node(toNode,style='filled',color='gold',shape=shape)
                    else:
                        graph.node(toNode,style='filled',color='lightblue2',shape=shape)
            else:
                for toNode in iterator:
                    if DARKTHEME:
                        graph.node(toNode,shape=shape,style='filled',color=DARKTHEMECOLORS['boxes'],fontcolor=DARKTHEMECOLORS['textcolor'])
                    else:
                        graph.node(toNode,shape=shape)

            # Since edge auto-creates nodes, now only run if len(iterator) == 2.
            if len(iterator) == 2:
                if DARKTHEME:
                    graph.edge(fromCourse[0],toCourse.courseName,color=DARKTHEMECOLORS['lines'],**args)
                else:
                    graph.edge(fromCourse[0],toCourse.courseName,color='black',**args)
            else: # If not, add a label for the missing class (unless already written as a part of the orGroup)
                if not fromOrGroup:
                    safeAddLabel(toCourse.courseName,fromCourse[0])

        else:
            # Create nodes
            if REQUIREMENTCOLOR:
                for toNode in [fromCourse[0],toCourse.courseName]:
                    if toNode in REQUIRED:
                        graph.node(toNode,style='filled',color='gold',shape=shape)
                    else:
                        graph.node(toNode,style='filled',color='lightblue2',shape=shape)
            else:
                for toNode in [fromCourse[0],toCourse.courseName]:
                    if DARKTHEME:
                        graph.node(toNode,shape=shape,style='filled',color=DARKTHEMECOLORS['boxes'],fontcolor=DARKTHEMECOLORS['textcolor'])
                    else:
                        graph.node(toNode,shape=shape)
            # Draw line
            if DARKTHEME:
                graph.edge(fromCourse[0],toCourse.courseName,color=DARKTHEMECOLORS['lines'],**args)
            else:
                graph.edge(fromCourse[0],toCourse.courseName,color='black',**args)

    # Create lines between courses
    runID = 0
    for _class in majorList:
        if _class.preReq != dict():
            # _class.preReq is an "and_group"
            for orGroup in _class.preReq:
                if len(orGroup) > 1:
                    for _prereq in orGroup:
                        requisiteLine(_prereq,_class,dot,style='dashed', fromOrGroup=True)
                    # Now add the or group as a prereq under the node
                    # Be careful to not overwrite other labels; automatically do a <BR /> if needed.
                    safeAddLabel(_class.courseName,' or '.join([x[0] for x in orGroup]))
                else:
                    requisiteLine(orGroup[0],_class,dot)
    return dot
