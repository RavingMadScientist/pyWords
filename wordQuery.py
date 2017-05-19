# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 17:31:47 2015

@author: legitz7
"""

from PyQt4 import QtGui, QtCore
import sys, os, time
import pickle, copy
import wpsyfuncs


class QHolder(QtGui.QWidget):
    def __init__(self, callsesh=None):
        super(QHolder, self).__init__()

        self.firstWQI=WQInterface(owner=self)
        self.WQIList=[]        
        self.holderWidget=QtGui.QTabWidget()
        self.addWQI(specified=self.firstWQI)   
        
        self.hasWordExpand = False
        #self.wordExpandWidget
        self.wordExpandDictList = []
                
        
        #self.expButton=QtGui.QPushButton("Expand Checked Sequences")
        #self.allButton=QtGui.QPushButton("Select All")
        #self.noneButton=QtGui.QPushButton("Select None")
        
        #self.expButton.clicked.connect(self.expandAction)
#        self.allButton.clicked.connect(self.selAllAction)
#        self.noneButton.clicked.connect(self.selNoneAction)        
#        
        
        #botButtonList=[self.expButton]
        #lowerlayout=QtGui.QHBoxLayout()
        #for button in botButtonList:
        #    lowerlayout.addWidget(button)
            
        masterLayout=QtGui.QVBoxLayout()
        masterLayout.addWidget(self.holderWidget)
        #masterLayout.addLayout(lowerlayout)
        self.setLayout(masterLayout)
        self.setGeometry(100,100,600,400)

    #specified param allows default widget creation, while allowing user option of
    #passing custom widget
    def addWQI(self, specified=False):
        if not specified:
            thisWQI=WQInterface(owner=self)
        else:
            thisWQI=specified
            
        tabString='Query_' + str(len(self.WQIList)//2)
        self.holderWidget.addTab(thisWQI, tabString)
        self.WQIList.append(thisWQI)
        self.holderWidget.setCurrentIndex(len(self.WQIList)-1)
        
        #This is the method that converts an idlist returned from the complex query into
        #a display-tab
        
        #Note that the queryResultsTab is an entirely distinct Widget from WQInterface,
        
    def addResultsTab(self, idlist):
        querynum=len(self.WQIList) // 2 
        thisRT=queryResultsTab(idlist, querynum, owner=self)
        rtString='Results_'+str(querynum)        
        self.holderWidget.addTab(thisRT, rtString)
        self.WQIList.append(thisRT)
        self.addWQI()
        self.holderWidget.setCurrentIndex(len(self.WQIList)-2)
        
    def expandAction(self):
        1          
        
class WQInterface(QtGui.QWidget):
    def __init__(self, owner=None):
        super(WQInterface, self).__init__()
        self.mode='virgin' # =>executed
        self.owner=owner

        self.runButton=QtGui.QPushButton('Run Query')
        self.runButton.setFixedWidth(100)
        self.runButton.clicked.connect(self.runQuery) 

        self.maxLabel=QtGui.QLabel('Max Returns')
        self.maxLabel.setFixedWidth(100)
        self.maxEntry=QtGui.QLineEdit('100')
        self.maxEntry.setFixedWidth(100)

        self.regexButton = QtGui.QPushButton('Regex Syntax')
        self.regexButton.clicked.connect(self.showRegexSyntax)
        self.regexButton.setFixedWidth(100)
        self.queryLabel=QtGui.QLabel('')
        
        
        self.conditionWidgets=[]
        self.conditionLayout=QtGui.QVBoxLayout()
        for c in self.conditionWidgets:
            self.conditionLayout.addWidget(c)


        dashlabel1=QtGui.QLabel('----------------------------')
        dashlabel2=QtGui.QLabel('----------------------------')
        dashlabel3=QtGui.QLabel('----------------------------')
        dashlabel4=QtGui.QLabel('----------------------------')
        dashlayout=QtGui.QHBoxLayout()
        dashlayout.addWidget(dashlabel1)
        dashlayout.addWidget(dashlabel2)
        dashlayout.addWidget(dashlabel3)
        dashlayout.addWidget(dashlabel4)

        self.entryWidget=queryConditionRow(owner=self)        
        
        self.rawModeBox=QtGui.QCheckBox('Use Raw SQL Query')
        self.rawModeBox.setChecked(False)
        self.rawTextEdit=QtGui.QTextEdit()
        self.rawModeBox.setFixedHeight(40)
        self.rawTextEdit.setFixedHeight(80)
        rawLayout=QtGui.QHBoxLayout()
        rawLayout.addWidget(self.rawModeBox)
        rawLayout.addWidget(self.rawTextEdit)
        
        
        self.masterLayout=QtGui.QVBoxLayout()
        self.masterLayout.addWidget(self.runButton)
#        self.masterLayout.addWidget(self.istatusbox)
        self.masterLayout.addWidget(self.maxLabel)
        self.masterLayout.addWidget(self.maxEntry)
        self.masterLayout.addWidget(self.regexButton)
        self.masterLayout.addWidget(self.queryLabel)
        self.masterLayout.addLayout(self.conditionLayout)
        self.masterLayout.addLayout(dashlayout)  
        self.masterLayout.addWidget(self.entryWidget)
        self.masterLayout.addLayout(rawLayout)
        
        
        self.setLayout(self.masterLayout)
        self.setGeometry(100,100,400,500)
        
    def addConditionLine(self, callingRow):
        #first, initialize an 'added' rowMode queryConditionRow
        newpos=len(self.conditionWidgets)
        newCondition=queryConditionRow(owner=self, rowMode='added', layoutPos=newpos)
        #grab data
        lparenthVal=str(callingRow.lParenthEntry.text()).strip()
        propNum=callingRow.propCombo.currentIndex()
        invNum=callingRow.invCombo.currentIndex()
        equalNum=callingRow.equalCombo.currentIndex()
        condVal=str(callingRow.condEntry.text()).strip()
        rparenthVal=str(callingRow.rParenthEntry.text()).strip()
        #set data
        newCondition.lParenthEntry.setText(lparenthVal)
        newCondition.propCombo.setCurrentIndex(propNum)
        newCondition.invCombo.setCurrentIndex(invNum)
        newCondition.equalCombo.setCurrentIndex(equalNum)
        newCondition.condEntry.setText(condVal)
        newCondition.condPosCombo.setCurrentIndex(callingRow.condPosCombo.currentIndex())
        newCondition.condLangCombo.setCurrentIndex(callingRow.condLangCombo.currentIndex())
        newCondition.rParenthEntry.setText(rparenthVal)
        newCondition.condStack.setCurrentIndex(callingRow.condStack.currentIndex())
        if callingRow.addConj:
            conjNum=callingRow.conjCombo.currentIndex()
            newCondition.conjCombo.setCurrentIndex(conjNum)
        self.conditionWidgets.append(newCondition)
        self.conditionLayout.addWidget(newCondition)
        

        
    def removeConditionLine(self, callingRow):
        #removeRowPos=callingRow.layoutPos
        #self.conditionLayout.removeWidget(callingRow)
        callingRow.hide()
        self.conditionWidgets.remove(callingRow)
        for pos, widget in enumerate(self.conditionWidgets):
            widget.layoutPos=pos
        self.update()
        
        
    def runQuery(self):
        #blablabla actually run the query...
        dbConn=wpsyfuncs.ppgConn('worddb1', 'biouser', passwd='biouser')
        dbCursor=dbConn.cursor()
    #First thing is, this command is Totally different if we are are in verbatim command mode
        if self.rawModeBox.isChecked():
            queryString=str(self.rawTextEdit.toPlainText()).strip()
            dbCursor.execute(queryString)
            qidlist=[]
            for etuple in dbCursor.fetchall():
                if etuple[0] is not None:
                    qidlist.append(etuple[0])
        else:
            #If we opt to use the GUI (ie queryConditionRows),
            #first lets check the parenthetical nesting, and assign a depth to each statement
            condLength=len(self.conditionWidgets)
            legalParens=True
            pdepth=0
            depthList=[]
            retIDList=[] #thisis where we store IDs associated w each query
            for condPos, cond in enumerate(self.conditionWidgets):
                retIDList.append([])
                lParens=str(cond.lParenthEntry.text()).count('(')
                pdepth += lParens
                depthList.append(pdepth)
                rParens=str(cond.rParenthEntry.text()).count(')')
                pdepth -= rParens
                if pdepth < 0:
                    legalParens=False
            if pdepth != 0:
                legalParens=False
            if legalParens:
                print 'parentheses legal:'
                print depthList
            else:
                print 'illegal parentheses placement'
                print depthList
                print pdepth
            #queries are evaluated one by one, from deepest to shallowest nesting, then logic is applied to the returned seqIDs for each query
            depthIndices=[]
            dmax=max(depthList)
            for d in range(dmax+1):
                dcount=depthList.count(d)
                dlist=[]
                lastd=0
                for instance in range(dcount):
                    nextd=depthList.index(d,lastd)
                    dlist.append(nextd)
                    lastd=nextd+1
                depthIndices.append(dlist)
            #final result is we have two lists: depthList gives depth of each condition, 
            #whereas depthIndices gives list of chronological conditions matching each depth
            print 'depthIndices'
            #d[-1]->d[-2]...d[0]

            for conditionPos in range(condLength):
    #THIS is the important line, ie the 
    #queryConditionRow.makeQueryString() provides the atomic SQL string creation, 
    #With All Boolean logic handled by Python!
                qPair=self.conditionWidgets[conditionPos].makeQueryString()
                qString=qPair[0]
                qVals=qPair[1]
                print 'qstring %s :\n' % (conditionPos)                
                print qString
                print 'qvals %s :\n' % (conditionPos)                
                print qVals                
                dbCursor.execute(qString, qVals)
                tupleList=dbCursor.fetchall()
                for t in tupleList:
                    if t[0] is not None: # the SQL queries we construct always return the ID as the first element of a row
                        retIDList[conditionPos].append(t[0])

            aggIDList=retIDList
            
            #ok so here, we are working back from the deepest-nested queryConditionRow,
            #and at each level of nesting we perform the specified conjunction set operations (and, or)
            #between any *contiguous QCR's at that depth. Then we pop those results up a level, and repeat until we have performed 
            #all logic operations between QCR's
            for edepth in range(len(depthIndices)-1, -1, -1):
                #working from deepest to shallowest nesting, we always do the same thing which is, 
                #i) find adjacents
                #2) perform appropriate set operation
                #3 pop up a level
                cPosList=depthIndices[edepth]
                for cpos in cPosList:
                    #is this condition part of a comparison pair at this depth?
                    if (cpos + 1) in cPosList:
                        combIDList=[]
                        if self.conditionWidgets[cpos].conjCombo.currentIndex() == 0:
                            #AND
                            for eid in retIDList[cpos]:
                                if eid in retIDList[cpos+1]:
                                    combIDList.append(eid)
                            
                        else:
                            #OR
                            for eid in retIDList[cpos]:
                                combIDList.append(eid)
                            for fid in retIDList[cpos+1]:
                                if fid not in combIDList:
                                    combIDList.append(fid)
                        aggIDList[cpos]=combIDList
                        aggIDList[cpos+1]=combIDList
                    #InterDepth aggregation (aka popping)                        
                    elif len(depthList)-cpos > 1:
                        if depthList[cpos+1] > edepth:
                            combIDList=[]
                            if self.conditionWidgets[cpos].conjCombo.currentIndex() == 0:
                                #AND
                                for eid in retIDList[cpos]:
                                    if eid in aggIDList[cpos+1]:
                                        combIDList.append(eid)
                                
                            else:
                                #OR
                                for eid in retIDList[cpos]:
                                    combIDList.append(eid)
                                for fid in aggIDList[cpos+1]:
                                    if fid not in combIDList:
                                        combIDList.append(fid)
                            aggIDList[cpos]=combIDList
                            aggIDList[cpos+1]=combIDList
                            for i in range(cpos+1, len(aggIDList)):
                                if depthList[i] > depthList[cpos]:
                                    aggIDList[cpos]=combIDList
                                else:
                                    break
            print aggIDList
            qidlist=aggIDList[0]
        qidlist=sorted(qidlist)
        print 'matches:'    
        for qid in qidlist:
            print qid
                
    # generate tableWidget from qidlist, each qidlist defaults to import-as-sandbox
    #so basically just 1 addtl gui layer separating the ImportByseqID function called here
    #from what we call in order to recreate a saved session
        self.owner.addResultsTab(qidlist)
    
    #handle displays
        self.runButton.setVisible(False)
#        self.istatusbox.setChecked(True)
#        self.istatusbox.setVisible(True)
        self.mode='executed'
       # self.owner.addDBI()
        self.update()
        
    def showRegexSyntax(self):
        print 'showRegex Button clicked!'
        self.rw=regexWidget()
        self.rw.show()        
 
#recall, that the key method of this class is the .makeQueryString(),
#which returns an SQL string. However, this method is always called from the Parent tab in which the
#queryConditionRow is embedded, since there is considerable processing involved in order to implement 
#the user-specified Boolean logic amongst multiple condition rows       
class queryConditionRow(QtGui.QWidget): #3 rowmodes: 'entry', 'added', and 'searched'
    def __init__(self, owner=None, rowMode='entry',addConj=True, layoutPos=-1):
        super(queryConditionRow,self).__init__()
        self.owner = owner
        self.addConj=addConj
        self.layoutPos=layoutPos         
        if rowMode == 'entry':
            addLabels=True
            self.layoutPos=-1
        else:
            addLabels=False
            
 
        lParenthLabel=QtGui.QLabel('(')
        propLabel=QtGui.QLabel('Property')
        invLabel=QtGui.QLabel('Invert?')
        equalLabel=QtGui.QLabel('Equality')
        condLabel=QtGui.QLabel('Condition')
        rParenthLabel=QtGui.QLabel(')')
        
        self.lParenthEntry=QtGui.QLineEdit('(')
        self.lParenthEntry.setFixedWidth(40)
        self.propCombo=QtGui.QComboBox()
        self.propCombo.currentIndexChanged.connect(self.updateCondStack)
        self.invCombo=QtGui.QComboBox()
        self.equalCombo=QtGui.QComboBox()
        
        self.condEntry=QtGui.QLineEdit()
        self.condEntry.setMinimumWidth(150)
        self.condPosCombo=QtGui.QComboBox()
        self.condPosCombo.setMinimumWidth(150)
        self.condLangCombo=QtGui.QComboBox()
        self.condLangCombo.setMinimumWidth(150)
        
        self.condStack=QtGui.QStackedWidget()
        self.condStackList=[self.condEntry, self.condPosCombo, self.condLangCombo]
        for ew in self.condStackList:
            self.condStack.addWidget(ew)
        self.condStack.setCurrentIndex(0)
        
        
        self.rParenthEntry=QtGui.QLineEdit(')')
        self.rParenthEntry.setFixedWidth(40)
        addButton=QtGui.QPushButton('Add Condition to Query')
        removeButton=QtGui.QPushButton('Remove Condition from Query')
        

        addButton.clicked.connect(self.addCondition)
        removeButton.clicked.connect(self.removeCondition)
        propList=['Word', 'ID', 'Length', 'Language', 'Prefix','Part of Speech', 'Synonym', 'Tag']
        eqList=['=', '<', '<=' , '>','>=','regex', 'caseless regex']
        invList=['', '!']
        langList=['afrikaans','czech','dutch','english', 'french', 'german' , 'greek', 'hungarian','hindi','italian', 'japanese','latin', 'portuguese','romanian','russian','spanish','turkish', 'ukranian']
        posList=['noun','verb','adjective','adverb','preposition','conjunction','pronoun', 'profanity', 'saying', 'salutation']        
        self.propCombo.addItems(propList)
        self.equalCombo.addItems(eqList)        
        self.invCombo.addItems(invList)
        self.condLangCombo.addItems(langList)
        self.condPosCombo.addItems(posList)
        self.addConj=addConj
        self.addLabels=addLabels
        if addConj:
            conjLabel=QtGui.QLabel('Conjunction')
            self.conjCombo=QtGui.QComboBox()
            self.conjCombo.addItem('and')
            self.conjCombo.addItem('or')
            self.conjCombo.addItem('xor')
            self.conjCombo.addItem('nor')
            labels=[ lParenthLabel, propLabel, invLabel, equalLabel, condLabel, rParenthLabel, conjLabel]        
            self.paramWidgets=[ self.lParenthEntry, self.propCombo, self.invCombo, self.equalCombo, self.condStack, self.rParenthEntry, self.conjCombo]
        else:
            labels=[lParenthLabel, propLabel, invLabel, equalLabel, condLabel, rParenthLabel]        
            self.paramWidgets=[self.lParenthEntry, self.propCombo, self.invCombo, self.equalCombo, self.condStack, self.rParenthEntry]

        qgw=QtGui.QGridLayout()
        if self.addLabels:
            labels.append(QtGui.QLabel(''))
            self.paramWidgets.append(addButton)
            for i in range(len(labels)):
                qgw.addWidget(labels[i], 0,i)
                qgw.addWidget(self.paramWidgets[i], 1, i)
            #qgw.addWidget(addButton, 1, len(labels))
  
        else:
            self.paramWidgets.append(removeButton)
            for i in range(len(self.paramWidgets)):
                qgw.addWidget(self.paramWidgets[i], 0, i)

        self.setLayout(qgw)
        self.setMaximumHeight(80)

    def updateCondStack(self):
        if str(self.propCombo.currentText())=='Part of Speech':
            self.condStack.setCurrentIndex(1)
        elif str(self.propCombo.currentText())=='Language':
            self.condStack.setCurrentIndex(2)
        else:
            self.condStack.setCurrentIndex(0)

    def addCondition(self):
        self.owner.addConditionLine(self)
    def removeCondition(self):
        self.owner.removeConditionLine(self)

    def makeQueryString(self):
#       propList=['Word', 'ID', 'Length', 'Language', 'Prefix','Part of Speech', 'Synonym', 'Tag']
        propList=["""wordname""", """wordid""", """wordlength""", """language""", """prefix""","""pos""", """synonym""", """tag"""]
        invsyms=[""" != """, """ >= """, """ > """, """ <= """, """ < """, """ !~ """, """ !~* """]        
        regsyms=[""" = """, """ < """, """ <= """, """ > """, """ >= """, """ ~ """, """ ~* """]        
        header="""SELECT wordid FROM wordtable WHERE """
        proppos=self.propCombo.currentIndex()
        header += propList[proppos]
        if self.invCombo.currentIndex() == 1:
            logop = invsyms[self.equalCombo.currentIndex()]
        else:
            logop = regsyms[self.equalCombo.currentIndex()]
        header += logop
        
        header += ' %s '
        #Here is where we use the stackedWidget currentIndex to determine whether we are reading a
        #QLineEdit, or grabbing a .currentText()
        csIndex=self.condStack.currentIndex()
        if csIndex == 0:
            qval =  str(self.condEntry.text()).strip() 
        elif csIndex == 1:
            qval = str(self.condPosCombo.currentText()).strip()
        else:
            qval = str(self.condLangCombo.currentText()).strip()            
        
        valtuple = (qval,)
        try:
            maxint=int(str(self.owner.maxEntry.text()))
            maxint=str(maxint)
            header += """ LIMIT """
            header += maxint
            header += """ ;"""            
        except:
            header += """ ;"""

        print header
        return [header, valtuple]
        
        
                
#So every query run generates one of these first, and then a new query tab
#*** 2 lines below NOT APPLICABLE to the wordQuery/pyWords implementation of the database interface                
#these guys have the checkbox that corresponds to the IMPORT selections for the
#global DBIHolder, but also has a local selectability for partial imports of the tab results
#***Ignore 2 lines above                
class queryResultsTab(QtGui.QWidget):
    def __init__(self, idlist, querynum=1, owner=None):
        super(queryResultsTab,self).__init__()        
        self.idlist=idlist
        self.querynum=querynum
        self.owner=owner #note, owner here is the master TabWidget() holding this display,
                        #NOT the callingSesh responsible for the query
        

        self.createWidgets()
        self.layoutWidgets()
    def createWidgets(self):
        confirmedWords=[] #This is where we store all successfully returned previewDicts from 
                                # the .makePreviewFromSeqID routine
        for wordid in self.idlist:
            wordPreview=self.makePreviewFromWordID(wordid)
            if wordPreview is not -1: #(error code from the makePreview routine)
                confirmedWords.append(wordPreview)
        self.previewTable=QtGui.QTableWidget()
        #need to implement a language aggregator here so that we can display all relevant translations on the right side of the returned table
        langlist = []
        for epreview in confirmedWords:
            for elang in epreview['translations'].keys():
                if elang not in langlist:
                    langlist.append(elang)
        langlist=sorted(langlist)
        
        
        self.previewTable.setColumnCount(8+len(langlist))
#        propList=["""wordname""", """wordid""", """wordlength""", """language""", """pos""", """synonym""", """tag"""]

        baseHeaders=['sel','prefix','wordname','wordlength','language','pos','synonym','adddate']
        allHeaders=baseHeaders+langlist 
        
         

        self.previewTable.setRowCount(len(confirmedWords))
        for epos, epreview in enumerate(confirmedWords):
            for ppos, param in enumerate(baseHeaders):
                if ppos > 0: # calling dict key/val by param string EXCEPT first col is selection checkbox
                    try:
                        pval = epreview[param]
                        if pval is not None:
                            qtwi=QtGui.QTableWidgetItem(str(pval))
                        else:
                            qtwi=QtGui.QTableWidgetItem('')
                    except:
                        qtwi=QtGui.QTableWidgetItem('')
                else: #first column is just a checkbox
                    qtwi=QtGui.QTableWidgetItem()                                        
                    qtwi.setFlags(QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsEditable)
                    qtwi.setCheckState(QtCore.Qt.Unchecked)
                    #qtwi.setFlags(QtCore.Qt.ItemIsUserCheckable)
                    
                    
                    
                self.previewTable.setItem(epos, ppos, qtwi)
            for lpos, lang in enumerate(langlist):
                if lang in epreview['translations'].keys():
                    lval = epreview['translations'][lang]
                else:
                    lval=""
                qtwi=QtGui.QTableWidgetItem(lval)
                self.previewTable.setItem(epos, lpos+len(baseHeaders),qtwi)
        
       
        self.previewTable.setHorizontalHeaderLabels(allHeaders)
        self.previewTable.resizeColumnsToContents()
        
        self.ascList=[]
        for i in range(self.previewTable.columnCount()): 
            self.ascList.append(True)
        
        #add sorting and expansion routines:
        #important reminder: need to reupdate the idlist after EVERY sort, that way any edits dont required a wordid search 
        topheads=self.previewTable.horizontalHeader()
        self.connect(topheads, QtCore.SIGNAL("sectionClicked(int)"), self.sortColumns)
        expheads=self.previewTable.verticalHeader()
        self.connect(expheads, QtCore.SIGNAL("sectionClicked(int)"), self.expandWordFromRow)
        
        
        self.resultString='Query ' + str(self.querynum) + ' Results: ' + str(len(confirmedWords))
        self.resLabel=QtGui.QLabel(self.resultString)
        
        self.selAllButton = QtGui.QPushButton('Select All')
        self.selNoneButton = QtGui.QPushButton('Select None')
        self.expandButton = QtGui.QPushButton('Expand Selected')

        self.selAllButton.clicked.connect(self.selAllAction)
        self.selNoneButton.clicked.connect(self.selNoneAction)
        self.expandButton.clicked.connect(self.expandSelAction)

        self.botbutlist = [self.selAllButton, self.selNoneButton, self.expandButton]
    def layoutWidgets(self):
        layout=QtGui.QVBoxLayout()
        layout.addWidget(self.resLabel)
        layout.addWidget(self.previewTable)
        
        buttonrow = QtGui.QHBoxLayout()
        for q in self.botbutlist:
            buttonrow.addWidget(q)
        layout.addLayout(buttonrow)
        #hlayout=QtGui.QHBoxLayout()
        #bottomButtons=[ self.selAllButton, self.selNoneButton]
        #for ebutton in bottomButtons:
        #    hlayout.addWidget(ebutton)
        #layout.addLayout(hlayout)
        self.setLayout(layout)
                
    def selAllAction(self):
        for i in range(self.previewTable.rowCount()):
            thisitem=self.previewTable.item(i,0)
            thisitem.setCheckState(QtCore.Qt.Checked)
    def selNoneAction(self):
        for i in range(self.previewTable.rowCount()):
            thisitem=self.previewTable.item(i,0)
            thisitem.setCheckState(QtCore.Qt.Unchecked)
    
#add sorting and expansion routines:
        #important reminder: need to reupdate the idlist after EVERY sort, that way any edits dont required a wordid search         
    def sortColumns(self, sortCol):
        #so we start by making a deepcopy of .idlist, hash these entries to the column to be sorted, sort by that column, and update display according to new idlist
        idhashmap = []
        idcopy=copy.deepcopy(self.idlist)    
        floatGood=True
        for erow in range(self.previewTable.rowCount()):
            try:
                thisfloat=float(str(self.previewTable.item(erow, sortCol).text()).strip())
            except:
                floatGood=False
                break
        #now that we know whether we are sorting floats or strings, we can make a hashmap from idlist, and sort                
        for erow in range(self.previewTable.rowCount()):
            thiskey=idcopy[erow]            
            if floatGood:
                thisval=float(str(self.previewTable.item(erow, sortCol).text()).strip())
            else:
                thisval=str(self.previewTable.item(erow, sortCol).text()).strip()
            idhashmap.append([thiskey, thisval])
        #ok now that we have hashmap, we can run a sort
        if self.ascList[sortCol]:
            sortresult=sorted(idhashmap, key = lambda val : val[1] )
            self.ascList[sortCol]=False
        else:
            sortresult=sorted(idhashmap, key = lambda val : val[1], reverse = True )
            self.ascList[sortCol]=True
        #additionally, we want to subsort alphabetically by word for sets of equal sort values.
        subsorts=[]#start, length
        subOn=False
        for ss in range(1,len(sortresult)):
            if sortresult[ss][1] == sortresult[ss-1][1]:
                if subOn:
                    subsorts[-1][1]+=1
                else:
                    subsorts.append([ss-1,2])
                    subOn=True
            else:
                subOn = False
        for subsort in subsorts:
            subhash=[]
            sublist=sortresult[subsort[0]:subsort[0]+subsort[1]]
            for subrow in sublist:
                locFound=False
                thisid=subrow[0]
                #print 'thisid=%d' % (thisid)
                k=0
                while locFound == False:
                    testid=self.idlist[k]
                    if testid == thisid:
                        locFound=True
                    else:
                        k+=1                
                #print 'kfound at row = %d' % (k)                       
                wordname=str(self.previewTable.item(k,2).text()).strip()
                #print 'word=%s' % wordname 
                subhash.append([thisid, wordname])
            subhash=sorted(subhash, key = lambda sval: sval[1])
            for subpos, subrow in enumerate(subhash):
                sortresult[subsort[0]+subpos][0]=subrow[0]
        #end subsorting loops
                
        #then we grab all info from the table, and iterate through the new hashmap to post values
        newDispVals=[]
        for j in range(len(sortresult)):
            thisid=sortresult[j][0]
            locFound=False
            k=0
            thisrow=[]
            while locFound == False:
                testid=self.idlist[k]
                if testid == thisid:
                    locFound=True
                else:
                    k+=1
            for ecol in range(self.previewTable.columnCount()):
                if ecol > 0:
                    cellval=str(self.previewTable.item(k,ecol).text()).strip()
                    thisrow.append(cellval)
                else:
                    thisrow.append('')
                #else:
                 #   thisrow.append(self.previewTable.item(k, 0))
            newDispVals.append(thisrow)
        for newrow in range(len(newDispVals)):
            for newcol in range(self.previewTable.columnCount()):
                if newcol > 0:
                    qtwi = QtGui.QTableWidgetItem(newDispVals[newrow][newcol])
                #else:
                    #qtwi = newDispVals[newrow][0]
                 #   qtwi = QtGui.QTableWidgetItem(newDispVals[newrow][newcol])
                    self.previewTable.setItem(newrow, newcol, qtwi)
        newidlist=[]
        for i in range(len(sortresult)):
            newidlist.append(sortresult[i][0])
        self.idlist=newidlist
            
    def expandWordFromRow(self, wordRow):
        print 'expandWordFromRow called'
        idfromrow=self.idlist[wordRow]
        self.expandWord(idfromrow)
    
    def expandWord(self, wordid):
        #first need to get the id
        print 'wordid: %d' % (wordid)
        wordDict=self.makePreviewFromWordID(wordid)
        print 'wordDict'
        print wordDict
        
        if self.owner.hasWordExpand:
            print 'adding tab to existing expandWidget'
            self.expandWidget.addExpandTab(wordid, doneDict=wordDict)
        else:
            print 'creating new expandHolder as self.expandWidget'
            self.expandWidget=expandHolder([wordid], owner=self.owner)
            #self.owner.wordExpandWidget=self.expandWidget
            #self.owner.hasWordExpand=True
            self.expandWidget.show()
        print 'expandWord routine complete'
        
                                                            
    def expandSelAction(self):
        print 'expandSelAction called'
#        for i in range(self.previewTable.rowCount()):
#            thisitem = self.previewTable.item(i,0)
#            if thisitem.checkState == QtCore.Qt.Checked:
#                print 'checked item found at row %d' % (i)
#                self.expandWordFromRow(i)
#            if thisitem.
        
#        self.selAllButton=QtGui.QPushButton('Select All')
#        self.selNoneButton=QtGui.QPushButton('Select None')
#        self.selAllButton.clicked.connect(self.selAllAction)
#        self.selNoneButton.clicked.connect(self.selNoneAction)
        
                

        
    #we are constructing a dict to be used in tabular display
    def makePreviewFromWordID(self, wordid):
        getParamsString="""SELECT prefix, wordname, wordlength, language, pos, adddate, synonym, synlist FROM wordtable WHERE wordid = %s ;"""
        idval=(wordid,)
        dbConn=wpsyfuncs.ppgConn('worddb1', 'biouser', passwd='biouser')
        dbCursor=dbConn.cursor()
        dbCursor.execute(getParamsString, idval)
        paramVals=dbCursor.fetchone()
        dispDict={}
        fineread=True
        try:
            dispDict['prefix']=paramVals[0]
            dispDict['wordname']=paramVals[1]
            dispDict['wordlength']=paramVals[2]
            dispDict['language']=paramVals[3]
            dispDict['pos']=paramVals[4]
            dispDict['adddate']=paramVals[5]
        except:
            fineread=False
            return -1
            
        #If we have loaded the 'easy' parameters into the dispDict without problem, then we proceed to grabbing synonyms.
        #since we dont naively know whether they are stored as single synonym foreign key or synlist array, we check both to 
        #produce a list of foreign ids over which we can iterate regardless
        if fineread:
            synidlist=[]
            checksyn=False
            try:
                synlist=paramVals[7]
                if len(synlist)>0:
                    synidlist=synlist
                else:
                    checksyn=True
            except:
                checksyn=True
            if checksyn:
                synidlist=[paramVals[6]]
            #ok so at this point we have an internal variable synidlist over which to iterate.
            transdict={}
            synamelist=[]
            synInfoString="""SELECT wordname, synlist FROM wordtable WHERE wordid = %s;"""
            trInfoString="""SELECT prefix, wordname, language FROM wordtable WHERE wordid = %s;"""            
            for synid in synidlist:
                s=(synid,)
                dbCursor.execute(synInfoString, s)
                sinfo=dbCursor.fetchone()
                print 'sinfo'
                print sinfo
                if sinfo is not None:
                    synamelist.append(sinfo[0])
                    if sinfo[1] is not None:
                        for trid in sinfo[1]:
                            if trid != wordid:
                                tr=(trid,)
                                dbCursor.execute(trInfoString, tr)
                                tinfo=dbCursor.fetchone()
                                if ((tinfo[0] is not None) and (len(tinfo[0]) > 0)):
                                    tstring='('+tinfo[0]+') ' + tinfo[1]
                                else:
                                    tstring = tinfo[1]
                                transdict[tinfo[2]]=tstring

            if len(synamelist) > 1:
                dispDict['synonym']=str(synamelist).strip('[').strip(']')
            elif len(synamelist) == 1:
                dispDict['synonym'] = synamelist[0]
            dispDict['translations']=transdict
            
            return dispDict

class expandHolder(QtGui.QTabWidget):
    def __init__(self, owner=None, idlist=None):
        super(expandHolder, self).__init__()
        self.owner = owner
        self.tabList=[]
        self.dictList=[]
        try:
            x=len(idlist)
            self.idList=idlist
        except:
            if idlist is None:
                self.idList=[]
            else:
                self.idList=[idlist]
        for eid in self.idList:
            self.addExpandTab(eid)
            
        if self.owner is not None:
            if self.owner.hasWordExpand == False:
                self.owner.hasWordExpand = True
            self.owner.wordExpandWidget = self
            self.owner.wordExpandDictList=self.dictList
            
    def addExpandTab(self, addid, doneDict=None):
        newtab=expandWordTab(addid, self,autoDict=doneDict)
        self.tabList.append(newtab)
        self.addTab(newtab, newtab.masterDict['wordName'])
    def killExpandTab(self, tabPos):
        if (tabPos+1)<len(self.tabList):
            self.tabList=self.tabList[:tabPos]+self.tabList[tabPos+1:]
        else:
            self.tabList = self.tabList[:-1]
    
            
class expandWordTab(QtGui.QWidget):
    def __init__(self, wordid, owner=None, autoDict=None, tabNum=0):
        super(expandWordTab, self).__init__()
        self.tabNum = tabNum
        if autoDict is not None:
            self.wordDict = autoDict
        else: #if we need to generate a param dict still, then we do it by stealing the makePreviewFromID method
                #from a dummy queryResultsTab
            ff=queryResultsTab([wordid])
            self.wordDict = ff.makePreviewFromWordID(wordid)
        self.wordDict['id']=wordid
            
        self.createWidgets()
        self.layoutWidgets()                        
        
        
    def createWidgets(self):
        #format is essentially a grid layout, with a bottom button row
        self.paramList=['prefix','wordname','wordlength','language','pos','adddate','synonym', 'etymology','tags','translations']
        self.pLabelList=[]
        for param in self.paramList:
            plabel=QtGui.QLabel(param)
            self.pLabelList.append(plabel)
        self.prefixEntry = QtGui.QLineEdit()
        self.nameEntry = QtGui.QLineEdit()
        self.lengthLabel = QtGui.QLabel()
        self.langEntry = QtGui.QLineEdit()
        self.posEntry = QtGui.QLineEdit()
        self.dateLabel = QtGui.QLabel()
        self.synEntry = QtGui.QLineEdit()
        self.etyEntry = QtGui.QLineEdit()
        self.tagsEntry = QtGui.QLineEdit()
        self.transBox = QtGui.QTableWidget()
        self.transBox.setRowCount(2)
        headerLabels=['Language','Translation']
        self.transBox.setHorizontalHeaderLabels(headerLabels)
        self.paramEntries = [self.prefixEntry, self.nameEntry, self.lengthLabel, self.langEntry,self.posEntry, self.dateLabel, self.synEntry, self.etyEntry, self.tagsEntry, self.transBox ]
        for j in range(len(self.paramList)-1):
            if self.paramList[j] in self.wordDict.keys():
                self.paramEntries[j].setText(self.wordDict[self.paramList[j]])
        if 'translations' in self.wordDict:
            try:
                self.transBox.setRowCount(len(self.wordDict['translations']))
            except:
                self.transBox.setRowCount(len(self.wordDict['translations'].keys()))
                oldTD=self.wordDict['translations']
                newTL = []
                tl0=sorted(oldTD.keys())
                for keyitem in tl0:
                    newTL.append([keyitem, oldTD[keyitem]])
                self.wordDict['translations']=newTL
            for tnum, etrans in enumerate(self.wordDict['translations']):
                qtwi=QtGui.QTableWidgetItem(etrans[0])
                qtwj=QtGui.QTableWidgetItem(etrans[1])
                self.transBox.setItem(tnum, 0, qtwi)
                self.transBox.setItem(tnum, 1, qtwj)
        self.transBox.setMaximumWidth(400)
        for j in self.paramEntries:
            j.setMaximumWidth(400)
            
        self.saveChangesButton=QtGui.QPushButton('Save Changes')
        self.killTabButton=QtGui.QPushButton('Close Tab')        
        self.saveChangesButton.clicked.connect(self.saveChangesAction)
        self.killTabButton.clicked.connect(self.killTabAction)
        self.botButtons=[self.saveChangesButton, self.killTabButton]    


    def layoutWidgets(self):
        masterlayout=QtGui.QVBoxLayout()
        topGrid=QtGui.QGridLayout()
        bottomRow=QtGui.QHBoxLayout()
        for ppos, pLabel in enumerate(self.pLabelList):
            topGrid.addWidget(pLabel, ppos, 0)
        for epos, ewidget in enumerate(self.paramEntries):
            topGrid.addWidget(ewidget, epos, 1)
        for ebutton in self.botButtons:
            bottomRow.addWidget(ebutton)
            
        
        masterlayout.addLayout(topGrid)
        masterlayout.addLayout(bottomRow)
        self.setLayout(masterlayout)
        
        
    def saveChangesAction(self):
        pass
    def killTabAction(self):
        pass
    
    
class addMaster(QtGui.QWidget):
    def __init__(self):
        super(addMaster, self).__init__()
        
        self.createWidgets()
        self.layoutWidgets()
    def createWidgets(self):
        self.topLabel=QtGui.QLabel('Add a Word!')        
        
        self.preLabel=QtGui.QLabel("Prefix")
        self.nameLabel=QtGui.QLabel("Word")
        self.langLabel=QtGui.QLabel("Language")
        self.posLabel=QtGui.QLabel("Part of Speech")    
        self.synLabel=QtGui.QLabel("Synonym")    
        self.tagLabel=QtGui.QLabel("Tags")    
        
        self.preEntry=QtGui.QLineEdit('')
        self.preEntry.setMinimumWidth(50)
        self.nameEntry=QtGui.QLineEdit('')
        self.nameEntry.setMinimumWidth(150)
        langList=['afrikaans','czech','dutch','english', 'french', 'german' , 'greek', 'hungarian','hindi','italian', 'japanese','latin', 'portuguese','romanian','russian','spanish','turkish', 'ukranian']
        posList=['noun','verb','adjective','adverb','preposition','conjunction','pronoun', 'profanity', 'saying', 'salutation']        
        self.langEntry=QtGui.QComboBox()
        self.langEntry.addItems(langList)
        self.posEntry=QtGui.QComboBox()
        self.posEntry.addItems(posList)
        self.synEntry=QtGui.QLineEdit('')
        self.synEntry.setMinimumWidth(100)
        self.tagEntry=QtGui.QLineEdit('')
        self.tagEntry.setMinimumWidth(100)
               
               
        self.addButton=QtGui.QPushButton('Add Word')
        self.addButton.setMaximumWidth(100)
        self.clearButton=QtGui.QPushButton('Clear Form')
        self.clearButton.setMaximumWidth(100)               
        self.addButton.clicked.connect(self.addWord)
        self.clearButton.clicked.connect(self.clearForm)
        self.botLabel=QtGui.QLabel('Last word added: ')

    def layoutWidgets(self):
         self.labelRow=[self.preLabel,self.nameLabel,self.langLabel,self.posLabel,self.synLabel,self.tagLabel]
         self.entryRow=[self.preEntry,self.nameEntry,self.langEntry,self.posEntry,self.synEntry,self.tagEntry]
         self.buttonRow=[self.addButton, self.clearButton]
         slay = QtGui.QVBoxLayout()
         slay.addWidget(self.topLabel)

         ll=QtGui.QHBoxLayout()         
         for i in self.labelRow:
             ll.addWidget(i)
         slay.addLayout(ll)

         el=QtGui.QHBoxLayout()         
         for i in self.entryRow:
             el.addWidget(i)
         slay.addLayout(el)

         bl=QtGui.QHBoxLayout()         
         for i in self.buttonRow:
             bl.addWidget(i)
         slay.addLayout(bl)
         
         slay.addWidget(self.botLabel)
         self.setLayout(slay)
         self.setGeometry(200,200,600,350)
         self.show()
             
    def clearForm(self):
        self.preEntry.setText("")
        self.nameEntry.setText("")
        self.synEntry.setText("")
        self.tagEntry.setTExt("")
    def addWord(self):
        wordDict={}
        wordDict['prefix']=str(self.preEntry.text()).strip()
        wordDict['wordname']=str(self.nameEntry.text()).strip()
        wordDict['language']=str(self.langEntry.currentText()).strip()
        wordDict['pos']=str(self.posEntry.currentText()).strip()
        syntext =str(self.synEntry.text()).strip()
        if ',' in syntext:
            wordDict['synlist']=syntext.split(',')
        else:
            wordDict['synlist']=syntext.split(';')
        tagtext=str(self.tagEntry.text()).strip()
        if ',' in tagtext:
            wordDict['taglist']=tagtext.split(',')
        else:
            wordDict['taglist']=tagtext.split(';')
        maxlong=0
        for t in wordDict['taglist']:
            cc=0
            for tc in t:
                if tc.isalnum():
                    cc+=1
            if cc>0:
                maxlong=cc
                break
        if maxlong < 1:
            wordDict['taglist']=""
            
        retStat=wpsyfuncs.addWordFromDict(wordDict)
        if retStat>0:
            botText='Last word added: %s' % (wordDict['wordname'])
        else:
            botText='Error adding word: %s' % (wordDict['wordname'])
        self.botLabel.setText(botText)

class regexWidget(QtGui.QWidget):
    def __init__(self):
        super(regexWidget, self).__init__()
        #print 'regexWidget initialized'
        self.createWidgets()
        self.layoutWidgets()
        
    def createWidgets(self):
        self.welcomeLabel=QtGui.QLabel('Regex Syntax: Tcl on PostgreSQL')
        self.reList=[['^','string beginning'],["$","string end"],["[a,b,c]","any of a, b, c"],["[1-4]","1, 2, 3, or 4"],["[^0-5]","NOT 0-5"],["|","logical or"],["a*","0 or more occurrences of 'a'"],["a+","1 or more occurrences of 'a'"],["a?","0 or 1 occurrences of 'a'"],["a{3}","exactly 3 occurrences of 'a'"],["a{2,5}","between 2 and 5 occurrences of 'a'"],[".","any single character"],["\d","and digit"],["\s","space"],["\w","any alnum"],["\D","any nondigit"],["\m","WORD beginning"],["\M","WORD end"],["(ab.)","subexpression: treat as char"],["""\\2""","back-reference to second subexpression"]]
        self.reTable=QtGui.QTableWidget()
        self.reTable.setColumnCount(2)
        self.reTable.setRowCount(len(self.reList))
        for i,item in enumerate(self.reList):
            qtwi = QtGui.QTableWidgetItem(item[0])
            qtwj = QtGui.QTableWidgetItem(item[1])
            self.reTable.setItem(i,0,qtwi)
            self.reTable.setItem(i,1,qtwj)
        self.reTable.resizeColumnsToContents()
    def layoutWidgets(self):
        thelayout=QtGui.QVBoxLayout()
        thelayout.addWidget(self.welcomeLabel)
        thelayout.addWidget(self.reTable)
        self.setLayout(thelayout)
        self.setGeometry(300,150,400,600)
            
        
class welcomeBox(QtGui.QWidget):
    def __init__(self):
        super(welcomeBox, self).__init__()
        self.hiLabel=QtGui.QLabel('Welcome to PyWords!')
        self.searchButton=QtGui.QPushButton('Search Words')
        self.addButton=QtGui.QPushButton('Add Words')
        self.searchButton.clicked.connect(self.searchAction)
        self.addButton.clicked.connect(self.addAction)
        lay=QtGui.QVBoxLayout()
        lay.addWidget(self.hiLabel)        
        lay.addWidget(self.searchButton)
        lay.addWidget(self.addButton)
        self.setLayout(lay)
        self.setGeometry(300,300,200,200)
    def searchAction(self):
        self.qh=QHolder()
        self.qh.show()
    def addAction(self):
        self.ab=addMaster()
        self.ab.show()
            
        
def runWordQuery():
    app = QtGui.QApplication(sys.argv)
    wq = welcomeBox()
    #rect = QApplication.desktop().availableGeometry()
    #form.resize(int(rect.width() * 0.6), int(rect.height() * 0.9))
    wq.show()
    #app.exec_()   
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    runWordQuery() 