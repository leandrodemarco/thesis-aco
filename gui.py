#!/usr/bin/python
# -*- coding: utf-8 -*-

from Tkinter import *
from ttk import Style
import tkMessageBox
import scipy.stats
from CspAco import runAlgorithm, runExperiment
from statFuns import pValuePoisson, generatePoissonSample, twoSamplePValue, \
                     pValueBinnedPoisson
import csv
#from ttk import Frame, Button, Label, Style

    
class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent
        
        self.initUI()
        self.centerWindow()
    
    def initUI(self):
      
        self.parent.title("Hormigas")
        self.pack(fill=BOTH, expand=1)
        
        self.style = Style()
        self.style.theme_use("default")
        
        # Seleccionar escenario
        scenaryLabel = Label(self, text="Escenario")
        scenaryLabel.place(x=25, y=25)
        
        self.vScenary = IntVar()
        scen1Bt = Radiobutton(self, text="1", variable=self.vScenary, value=1)
        scen2Bt = Radiobutton(self, text="2", variable=self.vScenary, value=2)
        self.vScenary.set(2)
        
        scen1Bt.place(x=95,y=25)
        scen2Bt.place(x=130, y=25)
        
        # Seleccionar número de hormigas
        nAntsLabel = Label(self, text="Nº de hormigas por ciclo: ")
        nAntsLabel.place(x=25, y=55)
        
        self.vNants = StringVar()
        nAntsEntry = Entry(self, textvariable=self.vNants, width=4)
        self.vNants.set("10")
        nAntsEntry.place(x=200, y=55)
        
        # Seleccionar numero maximo de ciclos
        nCyclesLabel = Label(self, text="Nº máximo de ciclos: ")
        nCyclesLabel.place(x=25, y=95)
        
        self.vNcycles = StringVar()
        nCyclesEntry = Entry(self, textvariable=self.vNcycles, width=4)
        self.vNcycles.set("10")
        nCyclesEntry.place(x=200, y=95)
        
        
        r1_label = Label(self, text="R1: ")
        r1_label.place(x=25, y=135)
        self.vaR1 = StringVar()
        R1_entry = Entry(self, textvariable=self.vaR1, width = 6)
        self.vaR1.set("")
        R1_entry.place(x=200, y=135)
        
        # Correr algoritmo
        runButton = Button(self, text="Ejecutar", command=self.execute_pressed)
        runButton.place(x=250, y=170)
        
        # -------------- FIT EXPERIMENT ------------------------------
        sampleLabel = Label(self, text="M: ")
        sampleLabel.place(x=170, y=230)
        
        self.vRuns = StringVar()
        expRunsEntry = Entry(self, textvariable=self.vRuns, width=5)
        self.vRuns.set("50")
        expRunsEntry.place(x=192, y=230)
        
        experimentButton = Button(self, text="Experimento", \
                                  command=self._runExperiment)
        experimentButton.place(x=170, y=200)
        
        twoSampleButton = Button(self, text="Dos muestras", 
                                 command=self.runTwoSample)
        twoSampleButton.place(x=290, y=200)

    def validateInt(self, stringVar):
        strValue = stringVar.get()
        valToRet = None
        try:
            valToRet = int(strValue)
        except:
            tkMessageBox.showerror("Error!", "El nro de hormigas debe ser \
                                   entero")
            
        return valToRet
    
    def getR1Value(self):
        strValue = self.vaR1.get()
        try:
            r1 = float(strValue)
            return r1
        except:
            return None

    def validateInput(self):
        nAnts = self.validateInt(self.vNants)
        numCycles = self.validateInt(self.vNcycles)

        allVars = (nAnts, numCycles)
        allOk = all(var != None for var in allVars)
    
        if allOk:
            return allVars
        else:
            return None
        
    def execute_pressed(self):
        self.runProgram(True)

    def runProgram(self, should_break = False):
        validInput = self.validateInput()
        if validInput != None:
            # Obtener data de la UI
            useScenario1 = self.vScenary.get() == 1
            nAnts, numCycles = validInput
            r1 = self.getR1Value()
            res = runAlgorithm(useScenario1, nAnts, numCycles, r1, should_break)
            
            return res
            
    def generateSampleTest(self):
        nRuns = self.validateInt(self.vRuns)
                
        if nRuns != None:
            csv_file = open('sample_test.csv', 'w+')
            csv_header = ['Sols halladas', 'Total paths']
            writer = csv.writer(csv_file)
            sampleTest = {}
            for i in range(0, nRuns):
                res = self.runProgram()
                num_paths = res[2]
                num_all_sols_found = res[3]
                
                # Guardar nro de soluciones encontradas para ver si fitea con
                # una Bin(n,p)
                try:
                    sampleTest[num_all_sols_found] += 1
                except:
                    sampleTest[num_all_sols_found] = 1
            
            writer.writerows([csv_header, [str(sampleTest), num_paths]])
            return sampleTest, num_paths
        else:
            msg = "El número de muestras debe ser entero"
            tkMessageBox.showerror("Error!", msg)            
            
    def _runExperiment(self):
        sampleTest, numPaths = self.generateSampleTest()
                
        nAnts = self.validateInt(self.vNants)
        numCycles = self.validateInt(self.vNcycles)
        totalAnts = nAnts * numCycles
        
        numSols = 171. if self.vScenary.get() != 1 else 333.
        prob = numSols / numPaths            
        
        print prob
        # Los valores de cada corrida van entre 0 y totalAnts
        # Hacemos el test de chisq
        lam = totalAnts*prob
        print "Running poisson chi-test for lambda = ", lam
        #p_val, T = pValuePoisson(sampleTest, int(lam)+3, lam)
        p_val, T = pValueBinnedPoisson(sampleTest, [(0,0), (1,1)] ,lam)
            
        print "T-statistic: ", T
        print "p-val: ", p_val
                
    def runTwoSample(self):
        sampleTest, numPaths = self.generateSampleTest()
        
        numSols = 171. if self.vScenary.get() != 1 else 333.
        
        nAnts = self.validateInt(self.vNants)
        numCycles = self.validateInt(self.vNcycles)
        totalAnts = nAnts * numCycles
        
        lam = totalAnts * (numSols/numPaths)
        
        nRuns = self.validateInt(self.vRuns)
        poissonSample = generatePoissonSample(lam, nRuns)
        
        sampleTestList = []
        
        for observedVal in sampleTest.keys():
            for i in range(0, sampleTest[observedVal]):
                sampleTestList.append(observedVal)
        
        print sampleTestList, poissonSample
        raw_input()        
        
        pVal = twoSamplePValue(sampleTestList, poissonSample)
        print pVal
        
    def centerWindow(self):
        w = 500
        h = 300

        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        
        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))
        

def main():
  
    root = Tk()
    root.geometry("1200x800+300+300")
    app = Example(root)
    root.mainloop()  


if __name__ == '__main__':
    main()
