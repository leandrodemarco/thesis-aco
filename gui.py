#!/usr/bin/python
# -*- coding: utf-8 -*-

from Tkinter import *
from ttk import Style
import tkMessageBox
from CspAco import runAlgorithm
#from ttk import Frame, Button, Label, Style


class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent
        
        self.initUI()
        self.centerWindow()
        
        self.running = False
    
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
        
        # Seleccionar modo elitista o no
        self.vElitist = IntVar()
        self.vElitist.set(1)
        elitistButton = Checkbutton(self, text="Modo elitista", \
            variable=self.vElitist, onvalue=1, offvalue=0, command=self.onElitist)
        elitistButton.place(x=20, y=140)
        
        self.vNumElitists = StringVar()
        self.numElitistsEntry = Entry(self, textvariable=self.vNumElitists, \
                                      width=4)
        self.vNumElitists.set("10")
        self.numElitistsEntry.place(x=185, y=140)
        
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
        
        # Seleccionar sigma para funcion costo
        costSigmaLabel = Label(self, text="Sigma: ")
        costSigmaLabel.place(x=25, y=210)
        
        self.vCostSigma = StringVar()
        costSigmaEntry = Entry(self, textvariable=self.vCostSigma, width=5)
        self.vCostSigma.set("0.05")
        costSigmaEntry.place(x=185, y=210)
        
        # Seleccionar a, factor de modificación ¿de qué?
        aFactorLabel = Label(self, text="a: ")
        aFactorLabel.place(x=25, y=245)
        
        self.vaFactor = StringVar()
        aFactorEntry = Entry(self, textvariable=self.vaFactor, width=3)
        self.vaFactor.set("4")
        aFactorEntry.place(x=185, y=245)
        
        # Correr algoritmo
        runButton = Button(self, text="Ejecutar", command=self.runProgram)
        runButton.place(x=250, y=350)
        
    def onElitist(self):
        isElitist = self.vElitist.get() == 1
        if not isElitist:
            self.numElitistsEntry.place_forget()
        else:
            self.numElitistsEntry.place(x=140, y=75)

    def validateInt(self, stringVar):
        strValue = stringVar.get()
        valToRet = None
        try:
            valToRet = int(strValue)
        except:
            alert = tkMessageBox.showerror("Error!", "El nro de \
            hormigas y las consideradas en modo elitista deben ser enteros")
            
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
        numElitists = self.validateInt(self.vNumElitists)
        numCycles = self.validateInt(self.vNcycles)
        evapRate = self.validateFloat(self.vEvaporationRate)
        tauMin = self.validateFloat(self.vTauMin)
        tauMax = self.validateFloat(self.vTauMax)
        costSigma = self.validateFloat(self.vCostSigma)

        allVars = (nAnts, numElitists, evapRate, tauMin, tauMax, \
                  costSigma, numCycles)
        allOk = all(var != None for var in allVars)
    
        if allOk:
            return allVars
        else:
            return None

    def runProgram(self):
        if not self.running:
            self.running = True
            validInput = self.validateInput()
            if validInput != None:
                # Obtener data de la UI
                useCompleteModel = self.vModel.get() == 1
                useScenario1 = self.vScenary.get() == 1
                beElitist = self.vElitist.get() == 1
                
                nAnts, numElitists, evapRate, tauMin, tauMax, \
                costSigma, numCycles = validInput
                
                runAlgorithm(useCompleteModel, useScenario1, beElitist,\
                numElitists, nAnts, evapRate, tauMin, tauMax, \
                costSigma, numCycles)
            else:
                self.running = False
        
    def centerWindow(self):
        w = 600
        h = 400

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
