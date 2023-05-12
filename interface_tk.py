import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.ttk import Combobox
from general import *
from debit import DebitSberbank
from account import  AccountSberbank

def show_test():
    global entities, root
    entities = list()

    root = tk.Tk()
    root.geometry('400x200')

    btn1 = tk.Button(text='Счет\вклад - Сбербанк', command=click_button_account)
    btn2 = tk.Button(text='Дебетовая карта - Сбербанк', command=click_button_debit)
    btn3 = tk.Button(text='Далее', command=continnue)
    lbl = tk.Label(text='Добавление карт/счетов')

    btn1.place(height=30, width=170, x=25, y=30)
    btn2.place(height=30, width=170, x=205, y=30)
    btn3.place(height=30, width=170, x=110, y=75)
    lbl.pack()

    root.mainloop()
def click_button_account():
    global entities

    path = askopenfilename(initialdir='C:\\Users\\stars\\Downloads', filetypes=[('PDF', '*.pdf')])

    if path != '':
        account = AccountSberbank()
        account.set(path)

        entities.append(account)
    pass


def click_button_debit():
    global entities

    path = askopenfilename(initialdir='C:\\Users\\stars\\Downloads', filetypes=[('PDF', '*.pdf')])

    if path != '':
        debit = DebitSberbank()
        debit.set(path)

        entities.append(debit)
    pass


def show_continnue():
    ind = name.index(combo.get())
    entity = entities[ind]

    lbl_data['text'] = entity.get_text()

def show_diagram_expenses():
    ind = name.index(combo.get())
    entity = entities[ind]

    income = entity.get_category(type_operation="expenses")
    paint(income, 'Расходы')

def show_diagram_income():
    ind = name.index(combo.get())
    entity = entities[ind]

    income = entity.get_category(type_operation="income")
    paint(income, 'Доходы')


def continnue():
    global combo, lbl_data, name

    newWindow = tk.Toplevel(root)
    newWindow.geometry('400x400')

    name = [entities[i].name for i in range(len(entities))]

    lbl_data = tk.Label(newWindow, justify=tk.LEFT)
    combo = Combobox(newWindow, width=200, values=name)
    btn_select = tk.Button(newWindow, text='Выбрать', command=show_continnue)
    btn_income = tk.Button(newWindow, text='Диаграмма доходов', command=show_diagram_income)
    btn_expenses = tk.Button(newWindow, text='Диаграмма расходов', command=show_diagram_expenses)

    combo.pack()
    btn_select.pack(anchor=tk.NE, padx=5, pady=5)
    btn_income.pack(anchor=tk.NE, padx=5, pady=5)
    btn_expenses.pack(anchor=tk.NE, padx=5, pady=5)
    lbl_data.pack(anchor=tk.NW, padx=5, pady=5)