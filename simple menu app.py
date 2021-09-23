#Author: Yutung
#Tab Control for Diner

#import libraries 
from tkinter import *
from tkinter import ttk 
import re

#some constants 
FOOD_TYPE_0 = 'Entree'
FOOD_TYPE_1 = 'Side Dish'
FOOD_TYPE_2 = 'Drink'
FOOD_TYPE_3 = 'Dessert'

#create a main class 
class TabControlEngine():
    
    #constructor 
    def __init__(self, tkWindow, dinerName):
        
        #lets create a new window on creation of this engine
        self.master = tkWindow
        self.master.title(dinerName)
        self.master.geometry("600x700")

        #initialize some menu dictionary
        self.menuItems = {}
        self.checkedMenuItems = {}
        self.checkBoxLib = {}

        #add the tab control 
        self.addTabControl()

        #add the list box
        self.addTreeViewControl()

        #add label frame
        self.addLabelFrameControl()

        #parse the data
        self.parseXmlFileData()

    #adding tab control
    def addTabControl(self):
        self.tabControl = ttk.Notebook(self.master, width=300, height=300)
        self.tabControl.grid(row=0, column=0)

    #adding tabs
    def addTabToControl(self, typeName):

        #convert the type
        if (typeName == '0'):
            typeName = FOOD_TYPE_0
        elif (typeName == '1'):
            typeName = FOOD_TYPE_1
        elif (typeName == '2'):
            typeName = FOOD_TYPE_2
        elif (typeName == '3'):
            typeName = FOOD_TYPE_3

        newTab = ttk.Frame(self.tabControl, padding=50)

        #create a frame in a frame
        topLeft = ttk.Frame(newTab, width=50, height=200)
        topLeft.pack(side=LEFT)
        topRight = ttk.Frame(newTab, width=200, height=200)
        topRight.pack(side=RIGHT)

        #add the listbox
        #border and highlight to 0 to remove any border
        listBox = Listbox(topRight, 
                          height=0, 
                          width=50, 
                          background="#EEEEEE", 
                          borderwidth=0, 
                          highlightthickness=0, 
                          font=('Veranda', 13), 
                          selectmode="multiple")
        listBox.bind("<<ListboxSelect>>", self.selectionOnListBox)

        #add the check boxes
        for foodItem in self.menuItems[typeName]:
            checkBox = Checkbutton(topLeft, variable=foodItem.getChecked(), borderwidth=0, command=self.handleCheckBox)
            checkBox.pack(padx=0, pady=0)

            #store all the checkbox so we can match with the listbox 
            try:
                self.checkBoxLib[typeName][foodItem.getName()] = checkBox
            except:
                self.checkBoxLib[typeName] = {}
                self.checkBoxLib[typeName][foodItem.getName()] = checkBox

            listBox.insert("end", foodItem.getName())
            listBox.pack()

        self.tabControl.add(newTab, text=typeName)

    #handle listbox select
    def selectionOnListBox(self, event):
        
        #every time the list box is selected
        # find the typeName 
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            data = event.widget.get(index)
            #find the typeName of the data
            foundTypeName = ''
            for typeName in self.checkBoxLib:
                for checkBoxItem in self.checkBoxLib[typeName]:
                    if (data == checkBoxItem):
                        foundTypeName = typeName
                        break

            #first let us deselect all from same tab
            for eachItem in self.checkBoxLib[foundTypeName]:
                self.checkBoxLib[foundTypeName][eachItem].deselect()
                self.handleCheckBox()

            #select again
            for selected in range(len(selection)):
                index = selection[selected]
                data = event.widget.get(index)
                self.checkBoxLib[foundTypeName][data].select()
                self.handleCheckBox()
            
        
    #adding the list box control
    def addTreeViewControl(self):

        #create a tree view with default columns 
        self.treeView = ttk.Treeview(self.master, height=300, column=(1, 2), show='headings')
        self.treeView.grid(row=1, column=0)
        self.treeView.column(1, anchor=CENTER, width=200)
        self.treeView.heading(1, text="Menu Item", anchor=W)
        self.treeView.column(2, anchor=CENTER, width=100)
        self.treeView.heading(2, text="Price", anchor=W)

    #handle the checkbox action
    def handleCheckBox(self):

        #to make it easy just clear the table every time
        for i in self.treeView.get_children():
            self.treeView.delete(i)

        #clear the total
        self.changeTotalPrice(0)

        runningTotal = 0

        #we need to iterate over all the menu items and see what was checked
        counter = 0
        for foodType in self.menuItems:
            for foodItem in self.menuItems[foodType]:
                if (foodItem.getChecked().get() == 1):
                    self.treeView.insert(parent='',index=counter, iid=counter, values=(foodItem.getName(), foodItem.getPrice()))
                    counter += 1

                    #everytime something is insert lets count the total
                    runningTotal += float(foodItem.getPrice())
                    self.changeTotalPrice(runningTotal)

    #add items to the treeview
    def addItemToTreeView(self, item, price):

        #add item
        self.treeView.insert(parent='', index=len(self.checkedMenuItems), values={item, price})

        #track items in a dict
        self.checkedMenuItems[item] = price

    #remove items from treeview
    def removeItemFromTreeView(self, item):
        self.checkedMenuItems.pop(item)

    #add label frame
    def addLabelFrameControl(self):
        self.labelFrame = ttk.LabelFrame(self.master, text='Pay The Amount', width=300, height=300)
        self.labelFrame.grid(row=0, column=1)

        #add some fields to the label frame 
        totalLabel = ttk.Label(self.labelFrame, text='Total:')
        totalLabel.place(x=50, y=40, anchor=W)
        self.totalText = Text(self.labelFrame, state=NORMAL, height=1, width=20, background="#EEEEEE")

        #set the default to 0
        self.totalText.insert(END, '${:.2f}'.format(0))
        self.totalText.place(x=90, y=30)

        #add the Tax
        taxLabel = ttk.Label(self.labelFrame, text='Tax:')
        taxLabel.place(x=50, y=80, anchor=W)
        self.taxText = Text(self.labelFrame, state=NORMAL, height=1, width=20, background="#EEEEEE")

        #set the default to 0
        self.taxText.insert(END, '${:.2f}'.format(0))
        self.taxText.place(x=90, y=70)

    #change total text
    def changeTotalPrice(self, price):
        #calculate the tax
        calcTax = price * 0.0825
        totalPrice = price + calcTax

        self.totalText.delete('1.0', END)
        self.totalText.insert(END, '${:.2f}'.format(totalPrice))

        self.taxText.delete('1.0', END)
        self.taxText.insert(END, '${:.2f}'.format(calcTax))

    #handle xml file
    def parseXmlFileData(self):

        #parse the menu items 
        self.readMenuData('Restaurants.xml')

        #now that the file is parsed, create the tabs
        for foodType in self.menuItems:
            self.addTabToControl(foodType)

    #read the data
    def readMenuData(self, path):

        #first open the file
        file = open(path)

        #define the regex patterns
        itemRegex = '\<Item\>(.*)\<\/item\>'
        priceRegex = '\<Price\>(.*)\<\/Price\>'
        typeRegex = '\<Menu\>(.*)\<\/Menu\>'

        #go through each line in the file
        for line in file:

            #every time we see Product 
            itemPattern = re.compile(itemRegex)
            foundItem = itemPattern.findall(line)
            if (len(foundItem) > 0):
                itemName = foundItem[0]
        
            #every time we see a Type
            typePattern = re.compile(typeRegex)
            foundType = typePattern.findall(line)
            if (len(foundType) > 0):
                typeName = foundType[0]

            #every time we see Price we add a new product
            pricePattern = re.compile(priceRegex)
            foundPrice = pricePattern.findall(line)
            if (len(foundPrice) > 0):
                price = foundPrice[0]

                #convert the type
                if (typeName == '0'):
                    typeName = FOOD_TYPE_0
                elif (typeName == '1'):
                    typeName = FOOD_TYPE_1
                elif (typeName == '2'):
                    typeName = FOOD_TYPE_2
                elif (typeName == '3'):
                    typeName = FOOD_TYPE_3

                newProduct = MenuItem(itemName, typeName, price)

                try:
                    self.menuItems[typeName].append(newProduct)
                except:
                    self.menuItems[typeName] = []
                    self.menuItems[typeName].append(newProduct)


#food item class
class MenuItem():

    #constructor 
    def __init__(self, name, foodType, price):
        self.name = name
        self.type = foodType
        self.price = price
        self.checked = IntVar()

    #get name
    def getName(self):
        return self.name

    #get type 
    def getType(self):
        return self.type

    #get price 
    def getPrice(self):
        return self.price
    
    #get checked
    def getChecked(self):
        return self.checked

#initialize the window
window = Tk()
tControl = TabControlEngine(window, "Yutung's Diner")
window.mainloop()