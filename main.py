from account import AccountSberbank
from debit import DebitSberbank
from general import *
import interface_tk as interface

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
    df_setting()

    interface.show()

    '''path = 'C:\\Users\\stars\\Downloads\\Документ-2023-05-08-191903.pdf'

    account = AccountSberbank()
    account.set(path)

    path = 'C:\\Users\\stars\\Downloads\\Документ-2023-03-19-000142.pdf'

    debit = DebitSberbank()
    debit.set(path)'''

    '''expenses = debit.get_category(type_operation="expenses")  #Получение диаграмм по доходам и расходам
    paint(expenses, 'Расходы')

    income = debit.get_category(type_operation="income")
    paint(income, 'Доходы')'''

    #print(account.get_category())
    #print(account.get_category(type_operation="income"))
    #print(account.get_category(type_operation="expenses"))
    #print(account.operations.category.unique())
