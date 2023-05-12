from account import AccountSberbank
from debit import DebitSberbank
from general import *
import interface_tk as interface
from tkinter.filedialog import askopenfilename


def df_setting():
    pd.set_option('display.max_rows', None)

    # Сброс ограничений на число столбцов
    pd.set_option('display.max_columns', None)

    # Сброс ограничений на количество символов в записи
    pd.set_option('display.max_colwidth', 20)

'''def new(list: list):
    tmp = None
    tmp = pd.concat([debit.operations[['date', 'category', 'cost']], account.operations[['date', 'category', 'cost']]],
                    ignore_index=True)

    tmp = tmp.sort_values(by='date', ascending=False)
    tmp.reset_index(drop=True, inplace=True)
    paint(get_category_from_df(tmp, type_operation='expenses'))'''


if __name__ == '__main__':

    # Вывод диагамм по выбранным картам
    df_setting()

    interface.show_test()



    '''
    # Отобразить данные о счете в консоли
    path = askopenfilename(initialdir='C:\\Users\\stars\\Downloads', filetypes=[('PDF', '*.pdf')]) 

    account = AccountSberbank() 
    account.set(path)
    print(f'Имя: {account.name},\n'
          f'Валюта: {account.currency},\n'
          f'Баланс: {account.balance},\n'
          f'Неснижаемый баланс: {account.irreducible_balance},\n'
          f'Ставка: {account.deposit_rate},\n'
          f'Срок: {account.deposit_term}'
          )
    print(account.operations)'''



    '''
    # Отобразить данные о дебетовой карте в консоли
    path = askopenfilename(initialdir='C:\\Users\\stars\\Downloads', filetypes=[('PDF', '*.pdf')])

    debit = DebitSberbank()
    debit.set(path)

    print(f'Имя: {debit.name},\n'
          f'Валюта: {debit.currency},\n'
          f'Баланс: {debit.balance}'
          )
    print(debit.operations)
    
    # Получение всех категорий карте
    print(debit.get_category())

    # Получение доходных категорий карте
    print(debit.get_category(type_operation="income"))

    # Получение расходных категорий карте
    print(debit.get_category(type_operation="expenses"))
    
    print(debit.operations.category.unique())'''
