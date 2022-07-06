from turtle import onclick
from typing import Container
from attr import validate
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.uix.screenmanager import NoTransition, ScreenManager, Screen, SlideTransition
from kivy.lang import Builder
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.actionbar import ActionBar,ActionBarException,ActionButton,ActionItem
from kivy.uix.dropdown import DropDown
from kivy.storage.jsonstore import JsonStore
from kivy.properties import ObjectProperty
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown
from kivy.metrics import dp
from kivy.uix.popup import Popup
import re
from kivy.uix.checkbox import CheckBox
import json

from requests import delete


Config.set('graphics', 'resizable', True)
Builder.load_file('ShoppingListDesign.kv')

class SimpleShoppingListApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        return sm

class HomeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)


class ScrollViewMain(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class ItemList(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        items = JsonStore("SimpleShoppingListApp/itemdata.json")
        for item in items:
            info = items.get(item)['info']
            self.add_widget(item_container(item,info[0],info[1],info[2]))
    
    def addNewItem(self):
        NewItemAnswer = NewItemPopUp(caller=self)
        NewItemAnswer.open()
    
    def getStats(self):
        Stats = statsPopUp(caller=self)
        Stats.open()

class statsPopUp(Popup):
    def __init__(self,caller, **kwargs):
        super().__init__(**kwargs)
        self.caller = caller
        self.title = "shopping info"
        self.size_hint = (0.5,0.65)
        
        stats = [0,0]
        #total cost and total for currently bought
        for item in self.caller.children:
            stats[0] += float(item.info[3])*int(item.info[2])
            if item.children[0].active:
                stats[1] += float(item.info[3])*int(item.info[2])

        Grid = GridLayout(cols=1,rows=2,size_hint=(1,1))
        Grid.add_widget(Label(text=f"total cost: £{stats[0]:.2f}"))
        Grid.add_widget(Label(text=f"currently bought: £{stats[1]:.2f}"))
        self.add_widget(Grid)

class NewItemPopUp(Popup):
    def __init__(self,caller, **kwargs):
        super(NewItemPopUp, self).__init__(**kwargs)
        self.caller = caller


    def add(self,newItem,shop,amnt,price):
        stored_data = JsonStore("SimpleShoppingListApp/itemdata.json")
        if not stored_data.exists(newItem.text.lower()) and self.validateItem(amnt.text,price.text):
            stored_data.put(newItem.text.lower(),info=[shop.text,amnt.text,price.text])
            self.caller.add_widget(item_container(newItem.text,shop.text,amnt.text,price.text))
            self.dismiss()
    
    def validateItem(self,amnt,price):
        if not amnt.isdigit():
            return False
        if re.match("(\d+\.\d{2}$)",price) == None and not price.isdigit():
            return False
        return True

class item_container(GridLayout):
    def __init__(self,name,shop,amount,price):
        super().__init__()
        self.cols= 5
        self.rows= 1
        self.id = name.lower()
        self.size_hint= (1,None)
        self.height = dp(70)
        self.info = [name,shop,amount,price]
        btn = Button(text=name, size_hint=(0.5,1), background_color=[0,0,0,0])
        btn.bind(on_release= self.editItem)
        self.add_widget(btn)
        self.add_widget(Label(text=shop,size_hint=(0.5,1)))
        self.add_widget(Label(text=amount,size_hint=(0.5,1)))
        self.add_widget(Label(text=f"£{float(price)*int(amount):.2f}",size_hint=(0.5,1)))
        self.add_widget(CheckBox(active=False,size_hint=(0.5,1)))

    def editItem(self,event):
        EditItemAnswer = EditItemPopUp(caller=self)
        EditItemAnswer.open()

class EditItemPopUp(Popup):
    def __init__(self,caller, **kwargs):
        self.caller = caller
        super(EditItemPopUp, self).__init__(**kwargs)

    def delete(self):
        itemid = self.caller.id
        item_data = JsonStore("SimpleShoppingListApp/itemdata.json")
        item_data.delete(itemid)
        self.caller.parent.remove_widget(self.caller)
        self.dismiss()

    def edit(self):
        info = self.caller.info
        itemlist = self.caller.parent
        self.delete()
        NewItemAnswer = NewItemPopUp(caller=itemlist)
        NewItemAnswer.open()
        
SimpleShoppingListApp().run()