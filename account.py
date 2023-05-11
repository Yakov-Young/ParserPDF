import re
import pandas as pd

from general import *

class AccountSberbank:
    def __init__(self):
        self.name = ''
        self.deposit_rate = 0.0
        self.irreducible_balance = 0.0
        self.currency = ''
        self.balance = 0.0
        self.date = None
        self.pre_date = None
        self.deposit_term = None
        self.operations = None

    def set(self, path: str):
        account = extract_text_from_pdf(path)

        pattern = r'Сформировано в СберБанк Онлайн за период[\s\S]+ИТОГО ПО ОПЕРАЦИЯМ ЗА ПЕРИОД'
        data_for_info = re.search(pattern, account).group()

        self.name = self.__set_name(data_for_info)
        self.deposit_rate = self.__set_deposit_rate(data_for_info)
        self.irreducible_balance = self.__set_irreducible_balance(data_for_info)
        self.currency = self.__set_currency(data_for_info)
        self.deposit_term = self.__set_deposit_term(data_for_info)
        self.date, self.pre_date = self.__set_dates(data_for_info)
        self.operations = self.__set_operations(account)
        self.balance = self.__set_balance()

        self.__verification()

    def add(self, path_new_doc: str):
        new_account = extract_text_from_pdf(path_new_doc)

        if self.__account_matching(new_account):
            if self.__check_date(new_account):
                new_operations = self.__set_operations(new_account)

                self.operations = pd.concat([self.operations, new_operations], ignore_index=True)
                self.operations.drop_duplicates(keep='first', inplace=True)
                self.operations.sort_values(by='date', ascending=False)
                self.operations.reset_index(drop=True, inplace=True)

                self.balance = self.__set_balance()
                self.__verification()
                return

        print('Карты не совпадают')
        pass

    def __account_matching(self, new_account) -> bool:

        new_name = self.__set_name(new_account)
        new_currency = self.__set_currency(new_account)

        if self.name != new_name or self.currency != new_currency:
            print('Different account')
            return False

        return True

    def __check_date(self, new_account):
        new_date, new_pre_date = self.__set_dates(new_account)

        delta_days_case1 = (self.pre_date - new_date).days
        delta_days_case2 = (new_pre_date - self.date).days

        if delta_days_case1 > -1 and new_date <= self.date:
            self.pre_date = new_pre_date

        elif delta_days_case2 > -1 and new_date <= self.date:
            self.date = new_date

        elif delta_days_case1 < -1 and delta_days_case2 < -1:
            print("Data already entered")
        else:
            print('Time gap')
            return False

        return True

    def __set_name(self, line: str) -> str:
        try:

            start_index = line.find('Тип вклада\n') + len('Тип вклада\n')
            end_index = line.find('\nСтавка по вкладу')

            type_account = line[start_index:end_index].replace('\n', ' ')

            start_index = line.find('Номер счёта\n') + len('Номер счёта\n')
            end_index = line.find('\nДата заключения')

            number_account = line[start_index:end_index]

            name = type_account + ' •••• ' + number_account[-4:]

            #print(name)
            return name
        except:
            print('error in set_name', line)
            raise

    def __set_deposit_rate(self, line: str) -> float:
        try:
            pattern = r'[\d,]+%'
            res = re.search(pattern, line).group()

            rate = convert_to_float(res[:-1])

            #print(rate)
            return rate
        except:
            #print('error in set_deposit_rate', line)
            raise

    def __set_irreducible_balance(self, line: str) -> float:
        try:
            start_index = line.find('Неснижаемый\nостаток') + len('Неснижаемый\nостаток')
            line = line[start_index:]

            pattern = r'[0-9, \xa0]+'
            res = re.search(pattern, line).group()

            irreducible_balance = convert_to_float(res)

            #print(convert_to_float(res))
            return irreducible_balance

        except:
            print('error in set_irreducible_balance', line)
            raise

    def __set_currency(self, line: str) -> str:
        try:
            start_index = line.find('Валюта') + len('Валюта\n')
            end_index = line.find('\nНеснижаемый\nостаток')

            currency = line[start_index:end_index]

            #print(currency)
            return currency

        except:
            print('error in set_currency', line)
            raise

    def __set_deposit_term(self, line: str):
        try:
            start_index = line.find('Срок вклада\n') + len('Срок вклада\n')
            end_index = line.find('\nУсловия вклада')

            term = line[start_index: end_index]

            if term == 'Бессрочный':
                return term

            term = convert_to_datetime(term)

            #print(term)
            return term
        except:
            print("error in set_currency", line)
            raise

    def __set_operations(self, line: str):
        try:
            pattern = r'\d\d.\d\d.\d\d\d\d\n\S+\nк\/с \d+\n№ [\d-]+\n\d+\n[\S\xa0]+\n[\S\xa0]+'
            general_information = re.findall(pattern, line)

            if len(general_information) == 0:
                print('В данной выписке отсутствуют операции')
                raise

            date_transaction = list()
            category = list()
            number = list()
            cost = list()
            balance = list()

            for item in general_information:
                item = item.split('\n')
                date_transaction.append(convert_to_datetime(item[0]))
                category.append(item[1])
                number.append(item[3])
                cost.append(convert_to_float(item[5]))
                balance.append(convert_to_float(item[6]))
            operations = pd.DataFrame(
                {'date': date_transaction, 'category': category, 'number': number, 'cost': cost, 'balance': balance})
            # print(operations)
            return operations


        except:
            print('error in set_operations', line)
            raise

    def __set_balance(self) -> float:
        try:
            index = self.operations['date'].idxmax()

            series = self.operations.iloc[index]

            #print(series['balance'])
            return series['balance']
        except:
            print('error in set_balance_and_balance_date')
            raise

    def __verification(self):
        try:
            first_balance = self.operations.iloc[[-1]]['balance'].values[0]
            last_balance = self.operations.iloc[[0]]['balance'].values[0]
            total_cost = round(self.operations['cost'].sum(), 4)

            if first_balance + last_balance - total_cost > 0.1:
                raise
        except:
            print('Ошибка в распознавании документа')

        pass

    def __set_dates(self, line: str):
        try:
            start_index = line.find('Сформировано в СберБанк Онлайн за период') + len('Сформировано в СберБанк Онлайн за период ')
            end_index = start_index + 23

            dates = line[start_index:end_index]

            pre_date = convert_to_datetime(dates[:10])
            date = convert_to_datetime(dates[-10:])

            #print(date, pre_date)
            return date, pre_date
        except:
            print('error in set_date', line)
            raise

    def get_category(self, type_operation='all'):
        category_name = self.operations.category.unique()
        category = {}

        for item in category_name:
            costs_by_category = self.operations[(self.operations['category'] == item)]['cost']
            total_costs_by_category = costs_by_category.sum()
            if type_operation == 'expenses':
                tmp = {item: costs_by_category[(costs_by_category < 0)].sum()}
            elif type_operation == 'income':
                tmp = {item: costs_by_category[(costs_by_category > 0)].sum()}
            elif type_operation == 'all':
                tmp = {item: costs_by_category.sum()}
            else:
                print('Неизветсное значение параметра \"type_operation\"')
                return

            category.update(tmp)
        if type_operation != 'all':
            category = {key: val for key, val in category.items() if val != 0}
        #print(category)

        return category

    def get_text(self):
        text = f'Валюта: {self.currency}\n' \
               f'Ставка: {self.deposit_rate}\n' \
               f'Баланс на {self.date}: {self.balance}'

        return text
