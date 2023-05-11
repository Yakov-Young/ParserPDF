import re
import pandas as pd

from general import *


class DebitSberbank:
    def __int__(self):
        self.name = ''
        self.currency = ''
        self.balance = 0.0
        self.balance_date = None
        self.pre_balance = 0.0
        self.pre_balance_date = None
        self.operations = None

    def set(self, path: str):
        card = extract_text_from_pdf(path)

        self.name = self.__set_name(card)
        self.currency = self.__set_currency(card)
        self.balance, self.pre_balance = self.__set_balance(card)
        self.balance_date, self.pre_balance_date = self.__set_balance_date(card)
        self.operations = self.__set_operations(card)

        self.__verification()

    def add(self, path_new_doc: str):
        new_card = extract_text_from_pdf(path_new_doc)

        if self.__card_matching(new_card):
            if self.__change_date_and_balance(new_card):
                new_operations = self.__set_operations(new_card)

                self.operations = pd.concat([self.operations, new_operations], ignore_index=True)
                self.operations.drop_duplicates(keep='first', inplace=True)
                self.operations = self.operations.sort_values(by='date', ascending=False)
                self.operations.reset_index(drop=True, inplace=True)

                self.__verification()
                return

        print('Карты не совпадают')

    def __card_matching(self, card: str) -> bool:

        new_name = self.__set_name(card)
        new_currency = self.__set_currency(card)

        if self.name != new_name or self.currency != new_currency:
            print('Different cards')
            return False

        return True

    def __change_date_and_balance(self, card: str) -> bool:
        '''
        case1: Добавление информации перед серединой известного нам интервала.
        case2: Добавление информации после середины известного нам интервала.
        case3: Добавление информации внутри известного нам интервала.
        case4: Добавление информации вне известного нам интервала.
        :param card:
        :return:
        '''

        new_balance, new_pre_balance = self.__set_balance(card)
        new_balance_date, new_pre_balance_date = self.__set_balance_date(card)

        delta_days_case1 = (self.pre_balance_date - new_balance_date).days
        delta_days_case2 = (new_pre_balance_date - self.balance_date).days

        if delta_days_case1 > -1 and new_balance_date <= self.balance_date:
            self.pre_balance_date = new_pre_balance_date
            self.pre_balance = new_pre_balance
        elif delta_days_case2 > -1 and new_balance_date <= self.pre_balance_date:
            self.balance_date = new_balance_date
            self.balance = new_balance
        elif delta_days_case1 < -1 and delta_days_case2 < -1:
            print("Data already entered")
        else:
            print('Time gap')
            return False

        return True
        pass

    def __set_name(self, line: str):
        """
        Sample:
        MIR •••• 9999
        """
        try:
            pattern = r'(MIR|Visa|MasterCard|Maestro)(\s\w+)?\s(•{4})\s(\d{4})'
            res = re.search(pattern, line)

            if res:
                name = res.group()
                return name
            # print(name)
            else:
                raise print('Имя карты не определено', res)
        except:
            print('Error in set_name', line)
            raise

    def __set_currency(self, line: str):
        """
        Sample:
        Валюта
        РУБЛЬ РФ
        """
        try:
            pattern = r'{}\n[\S ]+'.format(self.name)
            res = re.search(pattern, line)

            if res:
                currency = res.group()
                currency = currency[len(self.name) + 1:]
                return currency
                # print(currency)
            else:
                raise print('Error: currency not found', res)
        except:

            print('Error in set_balance', line)
            raise

    def __set_balance(self, line: str):
        try:
            pattern = r'ВСЕГО ПОПОЛНЕНИЙ\n[\S\xa0]+\n[\S\xa0]+'
            res = re.search(pattern, line)

            if res:
                res = res.group()

                pattern = r'[0-9, \xa0]+$'
                res_balance = re.search(pattern, res)

                pattern = r'\n[0-9, \xa0]+\n'
                res_pre_balance = re.search(pattern, res)

            if res_balance and res_pre_balance:
                balance = res_balance.group()
                balance = convert_to_float(balance)

                pre_balance = res_pre_balance.group()[:-1]
                pre_balance = convert_to_float(pre_balance)

                return balance, pre_balance
                # print(balance, pre_balance)
            else:
                raise print(f'Error: balance not found', res)
        except:
            print('Error in set_balance', line)
            raise

    def __set_balance_date(self, line: str):
        try:
            pattern = r'ОСТАТОК НА \d{2}\.\d{2}\.\d{4}\nОСТАТОК НА \d{2}\.\d{2}\.\d{4}'
            res = re.search(pattern, line)
            # print(res)

            if res:
                balance_date = res.group()

                pre_balance_date = balance_date[11:21]
                balance_date = balance_date[-10:]

                pre_balance_date = convert_to_datetime(pre_balance_date)
                balance_date = convert_to_datetime(balance_date)

                return balance_date, pre_balance_date
                # print(balance_date, pre_balance_date)
            else:
                raise print('Error: balance_date not found', res)
        except:
            print("Error in set_balance_date", line)
            raise

    def __set_operations(self, line: str):
        """Format:
            07.12.2022               #date
            11:26                    #time
            07.12.2022               #date_processing
            282541                   #code_transaction
            Супермаркеты             #category
            YARCHE                   #description
            200,96                   #cost
        """
        try:
            pattern = r'\d{2}\.\d{2}\.\d{4}\n\d{2}:\d{2}\n\d{2}\.\d{2}\.\d{4}\n\d{6}\n[\S \(\+\)]+\n[ \S]+\n[\S\xa0]+'
            general_information = re.findall(pattern, line)

            if len(general_information) == 0:
                print('В данной выписке отсутствуют операции')
                raise

            date_transaction = list()
            date_processing = list()
            code_transaction = list()
            category = list()
            description = list()
            cost = list()

            for item in general_information:
                item = item.split('\n')
                date_transaction.append(convert_to_datetime(item[0], item[1]))
                date_processing.append(convert_to_datetime(item[2]))
                code_transaction.append(int(item[3]))
                category.append(item[4])
                description.append(item[5])
                cost.append(convert_to_float(item[6], is_operation=True))
            operations = pd.DataFrame(
                {'date': date_transaction, 'date_processing': date_processing, 'code_transaction': code_transaction,
                 'category': category, 'description': description, 'cost': cost})
            # print(operations)
            return operations

        except:
            print("Error in set_operations", line)
            raise

    def __verification(self):
        try:
            difference = self.balance - self.pre_balance

            if abs(difference - self.operations['cost'].sum()) > 0.1:
                raise

        except:
            print('Error some operations were not read correctly')
            raise
        pass

    def get_category(self, type_operation='all'):
        category_name = self.operations.category.unique()
        category = {}

        for item in category_name:
            costs_by_category = self.operations[(self.operations['category'] == item)]['cost']
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
        category = {key: val for key, val in category.items() if val != 0}
        #print(category)

        return category

    def get_text(self):
        text = f'Валюта: {self.currency}\n' \
               f'Баланс на {self.balance_date}: {self.balance}'
        return text