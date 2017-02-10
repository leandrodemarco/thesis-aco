#!/usr/bin/python
# -*- coding: utf-8 -*-

from Tkinter import *
from ttk import Style
import tkMessageBox
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
        
        # Seleccionar modo elitista o no
        self.vElitist = IntVar()
        self.vElitist.set(1)
        elitistButton = Checkbutton(self, text="Modo elitista", variable=self.vElitist, onvalue=1, offvalue=0)
        elitistButton.place(x=20, y=75)
        
        # Seleccionar tasa de evaporación
        evapRateLabel = Label(self, text="Tasa de evaporación: ")
        evapRateLabel.place(x=25, y=100)
                
        self.vEvaporationRate = StringVar()
        evapRateEntry = Entry(self, textvariable=self.vEvaporationRate)
        self.vEvaporationRate.set("0.15")
        evapRateEntry.place(x=175, y=100)
        
        # Seleccionar sigma para funcion costo
        costSigmaLabel = Label(self, text="Sigma: ")
        costSigmaLabel.place(x=25, y=125)
        
        self.vCostSigma = StringVar()
        costSigmaEntry = Entry(self, textvariable=self.vCostSigma)
        self.vCostSigma.set("0.05")
        costSigmaEntry.place(x=100, y=125)
        
        # Correr algoritmo
        runButton = Button(self, text="Ejecutar", command=self.runAlgorithm)
        runButton.place(x=250, y=350)

    def runAlgorithm(self):
        # Obtener data de la UI
        useCompleteModel = self.vModel.get() == 1
        useScenario1 = self.vScenary.get() == 1
        beElitist = self.vElitist.get() == 1
        evapRateStr = self.vEvaporationRate.get()
        sigmaCostStr = self.vCostSigma.get()
        evapRate = 0.
        sigmaCost = 0.
        try:
            evapRate = float(evapRateStr)
            sigmaCost = float(sigmaCostStr)
        except:
            alert = tkMessageBox.showerror("Error!", \
            "La evaporación y sigma deben ser decimales separados con .")
            return
            
        
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
