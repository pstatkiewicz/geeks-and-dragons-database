from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
import matplotlib.pyplot as plt
import numpy as np
import mysql.connector
import requests
import datetime

DATE = datetime.date.today()
root = "C:\\Users\\Patryk\\pwr\\"

class view(FloatLayout):


    def __init__(self, **kwargs):

        super(view, self).__init__(**kwargs)

        self.add_widget(Label(text = "Podaj NIP/REGON odbiorcy",
                              font_name = "Arial",
                              font_size = "20",
                              size_hint = (.3, .065),
                              pos = (25, 550)))
        
        self.data = TextInput(size_hint = (.3, .065),
                             pos = (280, 550),
                             font_name = "Arial",
                             font_size = "20",
                             halign = 'center',
                             multiline = False,
                             write_tab = True)
        
        self.add_widget(self.data)

        self.add_widget(Label(text = "Naciścnij, po czym chcesz wyszukać",
                              font_name = "Arial",
                              font_size = "20",
                              size_hint = (.3, .065),
                              pos = (60, 500)))
        
        self.legend1 = ToggleButton(text = 'REGON',
                                   group = 'data',
                                   size_hint = (.1, .065),
                                   pos = (350, 500))
        self.add_widget(self.legend1)

        self.legend11 = ToggleButton(text = 'NIP',
                                   group = 'data',
                                   size_hint = (.1, .065),
                                   pos = (430, 500),
                                   state = 'down')
        self.add_widget(self.legend11)

        self.add_widget(Label(text = "Podaj indeks transakcji",
                              font_name = "Arial",
                              font_size = "20",
                              size_hint = (.3, .065),
                              pos = (0, 450)))
        
        self.ID = TextInput(size_hint = (.3, .065),
                             pos = (240, 450),
                             font_name = "Arial",
                             font_size = "20",
                             halign = 'center',
                             multiline = False,
                             write_tab = True)
        self.add_widget(self.ID)
        
        self.add_widget(Label(text = "Naciścnij, po czym chcesz wyszukać",
                              font_name = "Arial",
                              font_size = "20",
                              size_hint = (.3, .065),
                              pos = (60, 400)))
        
        self.legend2 = ToggleButton(text = 'wypożyczenia',
                                   group = 'sklep',
                                   size_hint = (.15, .065),
                                   pos = (360, 400))
        self.add_widget(self.legend2)

        self.legend22 = ToggleButton(text = 'sprzedaże',
                                   group = 'sklep',
                                   size_hint = (.15, .065),
                                   pos = (480, 400),
                                   state = 'down')
        self.add_widget(self.legend22)

        self.check = Button(text = "Sprawdź", 
                            background_color = "yellow",
                            size_hint = (.1, .075),
                            pos = (470, 150),
                            font_name = "Arial",
                            font_size = "20",
                            halign = 'center')
        self.check.bind(on_press = self.checking)
        self.add_widget(self.check)

        self.error = Label(text = "", 
                            disabled = True, 
                            color = "red",
                            size_hint = (.3, .1),
                            pos = (300, 300),
                            font_name = "Arial",
                            font_size = "20")
        self.add_widget(self.error)

        self.create = Button(text = "Stwórz",
                           background_color = "cyan",
                           size_hint = (.7, .1),
                           pos = (150, 75),
                           font_name = "Arial",
                           font_size = "20",
                           halign = 'center',
                           disabled = True)
        self.create.bind(on_press = self.creating)
        self.add_widget(self.create)


    def checking(self, instance):

        data = self.data.text
        id = self.ID.text
        self.error.text = ""

        if self.legend2.state == 'normal':
            table = 'sprzedaże'
        else:
            table = 'wypożyczenia'
        
        l1 = 0
        l2 = 0

        try:

            with open(f"{root}baza.txt", "r", encoding = "utf-8") as file1: 
                base = file1.readlines()
            
            with open(f"{root}faktura.txt", "r", encoding = "utf-8") as file2: 
                test = file2.readlines()

            if self.legend1.state == 'normal':
                for i in range(len(base)):
                    if base == []:
                        break
                    base_pom = eval(base[i])
                    if data == str(base_pom['result']['subject']['nip']):
                        l1 = 1
                        break
            else:
                for i in range(len(base)):
                    if base == []:
                        break
                    base_pom = eval(base[i])
                    if data == str(base_pom['result']['subject']['regon']):
                        l1 = 1
                        break
        
        except FileNotFoundError:
            l2 = 1
            self.error.text = "Brak pliku do zapisu."
        
        if id == "":

            l2 = 1
            self.error.text = "Pole 'indeks' jest puste."

        try:

            int(id)
        
        except ValueError:

            l2 = 1
            self.error.text = "Pole 'indeks' zawiera niedozwolone znaki. Wymagane tylko cyfry."

        if l2 == 0:

            try:

                mydb = mysql.connector.connect(
                    host = "giniewicz.it",
                    user = "team13",
                    password = "te@mie",
                    port = "3306",
                    database = "team13")
                
                my_cursor = mydb.cursor()
                query_id = f"""SELECT id FROM {table}
                            WHERE id = {id}"""
                my_cursor.execute(query_id)
                if my_cursor.fetchone() is None:
                    self.error.text = "Źle wprowadzony numer indeksu."
                    l2 = 1

                if self.legend1.state == 'normal':
                    response = requests.get(f"https://wl-api.mf.gov.pl/api/search/nip/{data}?date={DATE}")
                else:
                    response = requests.get(f"https://wl-api.mf.gov.pl/api/search/regon/{data}?date={DATE}")

                for key, value in response.json().items():
                    if key == "message":
                        if response.json()['message'] == "Pole 'NIP' zawiera niedozwolone znaki. Wymagane tylko cyfry.":
                            self.error.text = response.json()['message'] 
                            l2 = 1
                            break
                        elif response.json()['message'] == "Pole 'NIP' ma nieprawidłową długość. Wymagane 10 znaków.":
                            self.error.text = response.json()['message'] 
                            l2 = 1
                            break
                        elif response.json()['message'] == "Pole 'NIP' nie może być puste.":
                            self.error.text = response.json()['message'] 
                            l2 = 1
                            break
                        elif response.json()['message'] == 'Nieprawidłowy NIP.':
                            self.error.text = response.json()['message'] 
                            l2 = 1
                            break
                        elif response.json()['message'] == "Pole 'REGON' ma nieprawidłową długość. Wymagane 9 lub 14 znaków.":
                            self.error.text = response.json()['message']
                            l2 = 1
                            break
                        elif response.json()['message'] == "Pole 'REGON' nie może być puste.":
                            self.error.text = response.json()['message'] 
                            l2 = 1
                            break
                        elif response.json()['message'] == "Pole 'REGON' zawiera niedozwolone znaki. Wymagane tylko cyfry.":
                            self.error.text = response.json()['message']
                            l2 = 1
                            break
                        elif response.json()['message'] == 'Nieprawidłowy REGON.':
                            self.error.text = response.json()['message'] 
                            l2 = 1
                            break

                if l2 == 0:
                    if response.json()['result']['subject'] == None:
                        if self.legend1.state == 'normal':
                            self.error.text = "NIP jest niezarejestrowany"
                        else:
                            self.error.text = "REGON jest niezarejestrowany"
                        l2 = 1
                
                if l2 == 0 and l1 == 0:
                    with open("baza.txt", "r", encoding = "utf-8") as file1: 
                        file1.write(f'{str(response.json())}\n')

            except mysql.connector.InterfaceError:

                self.error.text = "Brak dostępu do internetu."
                l2 = 1

        if l2 == 0:
            self.create.disabled = False
            self.check.disabled = True
            self.data.disabled = True
            self.legend1.disabled = True
            self.legend11.disabled = True
            self.ID.disabled = True
            self.legend2.disabled = True
            self.legend22.disabled = True

    def creating(self, instance):

        data = self.data.text
        id = self.ID.text
        self.error.text = ""
        l = 0

        if self.legend2.state == 'normal':
            table = 'sprzedaże'
        else:
            table = 'wypożyczenia'

        try:

            mydb = mysql.connector.connect(
                host = "giniewicz.it",
                user = "team13",
                password = "te@mie",
                port = "3306",
                database = "team13")
                
            my_cursor = mydb.cursor()
            query_id = f"""SELECT {table}.id, `nazwa gry`, kwota FROM {table}
                            INNER JOIN gry ON {table}.id_gry = gry.id
                            WHERE {table}.id = {id}"""
            my_cursor.execute(query_id)
            facture = my_cursor.fetchall()
            if self.legend2.state == 'normal':
                name = f'{facture[0][0]}/1/{DATE}'
            else:
                name = f'{facture[0][0]}/2/{DATE}'

            if self.legend1.state == 'normal':
                response = requests.get(f"https://wl-api.mf.gov.pl/api/search/nip/{data}?date={DATE}")
            else:
                response = requests.get(f"https://wl-api.mf.gov.pl/api/search/regon/{data}?date={DATE}")

            if response.json()['result']['subject']['workingAddress'] == None:
                address = response.json()['result']['subject']['residenceAddress']
            else:
                address = response.json()['result']['subject']['workingAddress']

        except mysql.connector.InterfaceError:

            self.error.text = "Brak dostępu do internetu."
            self.create.disabled = True
            self.check.disabled = False
        
        with open(f"{root}faktura.txt", "r", encoding = "utf-8") as file1: 
            base = file1.readlines()
            
        for i in base:
            d = eval(i)
            if d[0][:-10] == name[:-10]:
                self.error.text = "Faktura na ten produkt jest już wystawiona."
                l = 1

        if l == 0:
            result = [name, response.json()['result']['subject']['name'],
                    response.json()['result']['subject']['nip'], address,
                    facture[0][1], float(facture[0][2])]
                
            with open(f"{root}faktura.txt", "a", encoding = "utf-8") as file1:
                file1.write(f'\n{result}')
            
            self.data.disabled = False
            self.legend11.disabled = False
            self.legend1.disabled = False

        self.legend22.disabled = False
        self.legend2.disabled = False        
        self.ID.disabled = False
        self.create.disabled = True
        self.check.disabled = False

class FunctionApp(App):

    def build(self):

        return view()
    
if __name__ == '__main__':
    FunctionApp().run()