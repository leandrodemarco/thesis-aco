#!/usr/bin/python
# -*- coding: utf-8 -*-

from Tkinter import *
from ttk import Style
import tkMessageBox
import scipy.stats
from CspAco import runAlgorithm, runExperiment
from statFuns import pValuePoisson, generatePoissonSample, twoSamplePValue, \
                     pValueBinnedPoisson
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
        
        # Seleccionar si usamos modelo completo o reducido
        modelLabel = Label(self, text="Modelo")
        modelLabel.place(x=25, y=25)
        
        self.vModel = IntVar()
        completeModel = Radiobutton(self, text="Completo", variable = self.vModel, value=1)
        reducedModel = Radiobutton(self, text="Reducido", variable = self.vModel, value=2)
        self.vModel.set(2)
        
        completeModel.place(x=85, y=25)
        reducedModel.place(x=180, y=25)
        
        # Seleccionar escenario
        scenaryLabel = Label(self, text="Escenario")
        scenaryLabel.place(x=25, y=50)
        
        self.vScenary = IntVar()
        scen1Bt = Radiobutton(self, text="1", variable=self.vScenary, value=1)
        scen2Bt = Radiobutton(self, text="2", variable=self.vScenary, value=2)
        self.vScenary.set(2)
        
        scen1Bt.place(x=85,y=50)
        scen2Bt.place(x=120, y=50)
        
        # Seleccionar número de hormigas
        nAntsLabel = Label(self, text="Nº de hormigas por ciclo: ")
        nAntsLabel.place(x=25, y=80)
        
        self.vNants = StringVar()
        nAntsEntry = Entry(self, textvariable=self.vNants, width=4)
        self.vNants.set("10")
        nAntsEntry.place(x=185, y=80)
        
        # Seleccionar numero maximo de ciclos
        nCyclesLabel = Label(self, text="Nº máximo de ciclos: ")
        nCyclesLabel.place(x=25, y=110)
        
        self.vNcycles = StringVar()
        nCyclesEntry = Entry(self, textvariable=self.vNcycles, width=4)
        self.vNcycles.set("10")
        nCyclesEntry.place(x=185, y=110)
        
        # Seleccionar tasa de evaporación, tau_min y tau_max
        evapRateLabel = Label(self, text="Tasa de evaporación: ")
        evapRateLabel.place(x=25, y=175)
                
        self.vEvaporationRate = StringVar()
        evapRateEntry = Entry(self, textvariable=self.vEvaporationRate, \
                              width=5)
        self.vEvaporationRate.set("0.15")
        evapRateEntry.place(x=185, y=175)
        
        tauMinLabel = Label(self, text="tau_min: ")
        tauMinLabel.place(x=240, y=175)
        self.vTauMin = StringVar()
        tauMinEntry = Entry(self, textvariable=self.vTauMin, width=5)
        self.vTauMin.set("0.05")
        tauMinEntry.place(x=300, y=175)
        
        tauMaxLabel = Label(self, text="tau_max: ")
        tauMaxLabel.place(x=355, y=175)
        self.vTauMax = StringVar()
        tauMaxEntry = Entry(self, textvariable=self.vTauMax, width=5)
        self.vTauMax.set("15")
        tauMaxEntry.place(x=415, y=175)
        
        # Seleccionar función costo a utilizar
        costFunctionLabel = Label(self, text="Función costo: ")
        costFunctionLabel.place(x=25, y=210)
        
        self.vCostFunction = IntVar()
        linearCostBt = Radiobutton(self, text="Lineal", \
                                   variable=self.vCostFunction, value=1)
        expCostBt = Radiobutton(self, text="Exponencial", \
                                   variable=self.vCostFunction, value=2)
        pozoCostBt = Radiobutton(self, text="Pozo", \
                                   variable=self.vCostFunction, value=3)
        pozo45CostBt = Radiobutton(self, text="Pozo 45", \
                                   variable=self.vCostFunction, value=4)
        exp2CostBt = Radiobutton(self, text="Exp 2", \
                                 variable=self.vCostFunction, value=5)
        LCostBt = Radiobutton(self, text="L-costo", \
                              variable=self.vCostFunction, value=6)
                                   
        linearCostBt.place(x=115, y=210)
        expCostBt.place(x=185, y=210)
        pozoCostBt.place(x=285, y=210)
        pozo45CostBt.place(x=340, y=210)
        exp2CostBt.place(x=415, y=210)
        LCostBt.place(x=480, y=210)
        
        
        self.vCostFunction.set(2)
        
        # Seleccionar sigma para funcion costo
        costSigmaLabel = Label(self, text="Sigma: ")
        costSigmaLabel.place(x=25, y=245)
        
        self.vCostSigma = StringVar()
        costSigmaEntry = Entry(self, textvariable=self.vCostSigma, width=5)
        self.vCostSigma.set("0.05")
        costSigmaEntry.place(x=185, y=245)
        
        # Seleccionar a, factor de modificación ¿de qué?
        aFactorLabel = Label(self, text="a: ")
        aFactorLabel.place(x=25, y=280)
        
        self.vaFactor = StringVar()
        aFactorEntry = Entry(self, textvariable=self.vaFactor, width=3)
        self.vaFactor.set("4")
        aFactorEntry.place(x=185, y=280)
        
        # Correr algoritmo
        runButton = Button(self, text="Ejecutar", command=self.runProgram)
        runButton.place(x=250, y=350)
        
        # -------------- FIT EXPERIMENT ------------------------------
        sampleLabel = Label(self, text="M: ")
        sampleLabel.place(x=170, y=460)
        
        self.vRuns = StringVar()
        expRunsEntry = Entry(self, textvariable=self.vRuns, width=5)
        self.vRuns.set("50")
        expRunsEntry.place(x=192, y=460)
        
        experimentButton = Button(self, text="Experimento", \
                                  command=self._runExperiment)
        experimentButton.place(x=170, y=425)
        
        twoSampleButton = Button(self, text="Dos muestras", 
                                 command=self.runTwoSample)
        twoSampleButton.place(x=290, y=425)

    def validateInt(self, stringVar):
        strValue = stringVar.get()
        valToRet = None
        try:
            valToRet = int(strValue)
        except:
            alert = tkMessageBox.showerror("Error!", "El nro de \
            hormigas debe ser enteros")
            
        return valToRet
        
    def validateFloat(self, stringVar):
        strValue = stringVar.get()
        valToRet = None
        try:
            valToRet = float(strValue)
        except:
            alert = tkMessageBox.showerror("Error!", "La evaporación"\
            "tau_min, tau_max y sigma deben ser decimales separados con .")

        return valToRet

    def validateInput(self):
        nAnts = self.validateInt(self.vNants)
        numCycles = self.validateInt(self.vNcycles)
        evapRate = self.validateFloat(self.vEvaporationRate)
        tauMin = self.validateFloat(self.vTauMin)
        tauMax = self.validateFloat(self.vTauMax)
        costSigma = self.validateFloat(self.vCostSigma)
        errFactor = self.validateFloat(self.vaFactor)

        allVars = (nAnts, evapRate, tauMin, tauMax, \
                  costSigma, numCycles, errFactor)
        allOk = all(var != None for var in allVars)
    
        if allOk:
            return allVars
        else:
            return None

    def runProgram(self):
        validInput = self.validateInput()
        if validInput != None:
            # Obtener data de la UI
            useCompleteModel = self.vModel.get() == 1
            useScenario1 = self.vScenary.get() == 1
            costFunction = self.vCostFunction.get()                
            
            nAnts, evapRate, tauMin, tauMax, \
            costSigma, numCycles, errorScale = validInput
            
            res = runAlgorithm(useCompleteModel, useScenario1, nAnts, \
                        evapRate, tauMin, tauMax, costSigma, numCycles,\
                        errorScale, costFunction)
            
            return res
            
    def generateSampleTest(self):
        nRuns = self.validateInt(self.vRuns)
                
        if nRuns != None:
            sampleTest = {}
            for i in range(0, nRuns):
                res = self.runProgram()
                # Guardar nro de soluciones encontradas para ver si fitea con
                # una Bin(n,p)
                try:
                    sampleTest[res[3]] += 1
                except:
                    sampleTest[res[3]] = 1
            
            return sampleTest, res[2]
        else:
            alert = tkMessageBox.showerror("Error!", "El número de"\
                "muestras debe ser entero")            
            
    def _runExperiment(self):
        sampleTest, numPaths = self.generateSampleTest()
                
        nAnts = self.validateInt(self.vNants)
        numCycles = self.validateInt(self.vNcycles)
        totalAnts = nAnts * numCycles
        
        numSols = 171. if self.vScenary.get() != 1 else 333.
        prob = numSols / numPaths            
        
        print prob
        print sampleTest
        # Los valores de cada corrida van entre 0 y totalAnts
        # Hacemos el test de chisq
        lam = totalAnts*prob
        print "Running poisson chi-test for lambda = ", lam
        #p_val, T = pValuePoisson(sampleTest, int(lam)+3, lam)
        p_val, T = pValueBinnedPoisson(sampleTest, [(0,0)] ,lam)
            
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
        w = 600
        h = 500

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
