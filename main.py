import re
import time
import pandas as pd
from datetime import datetime, timedelta
from typing import List

import fitz

class DebitSberbank:

    def __int__(self):
        self.name_card = ''
        self.currency = ''
        self.balance = 0.0
        self.balance_date = None
        self.pre_balance = 0.0
        self.pre_balance_date = None
        self.operations = None

    def set(self, path: str):
        card = extract_text_from_pdf(path)

        self.name_card = self.find_name(card)
        self.currency = self.find_currency(card)
        self.balance, self.pre_balance = self.find_balance(card)
        self.balance_date, self.pre_balance_date = self.find_balance_date(card)
        self.operations = self.find_operations(card)

        self.verification()

    def add(self, path_new_doc: str):
        card = extract_text_from_pdf(path_new_doc)
        if self.card_matching(card):
            if self.change_date_and_balance(card):
                new_operations = self.find_operations(card)

                self.operations = pd.concat([self.operations, new_operations], ignore_index=True)
                self.operations.drop_duplicates(keep='first', inplace=True)
                self.operations.sort_values(by='date', ascending=False)
                self.operations.reset_index(drop=True , inplace=True)

                self.verification()

        pass

    def card_matching(self, card: str) -> bool:

        new_name_card = self.find_name(card)
        new_currency = self.find_currency(card)

        if self.name_card != new_name_card and self.currency != new_currency:
            print('Different cards')
            return False

        return True
        pass

    def change_date_and_balance(self, card: str) -> bool:
        '''
        case1: Добавление информации перед серединой известного нам интервала.
        case2: Добавление информации после середины известного нам интервала.
        :param card:
        :return:
        '''

        new_balance, new_pre_balance = self.find_balance(card)
        new_balance_date, new_pre_balance_date = self.find_balance_date(card)

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

    def find_name(self, line: str):
        """
        Sample:
        MIR •••• 9999
        """
        try:
            pattern = r'(MIR|Visa|MasterCard|Maestro)(\s\w+)?\s(•{4})\s(\d{4})'
            res = re.search(pattern, line)

            if res:
                name_card = res.group()
                return name_card
            #print(name_card)
            else:
                raise print('Имя карты не определено', res)
        except:
            print('Error in find_name')
            raise
        pass

    def find_currency(self, line: str):
        """
        Sample:
        Валюта
        РУБЛЬ РФ
        """
        try:
            pattern = r'{}\n[\S ]+'.format(self.name_card)
            res = re.search(pattern, line)

            if res:
                currency = res.group()
                currency = currency[len(self.name_card) + 1:]
                return currency
                #print(currency)
            else:
                raise print('Error: currency not found', res)
        except:
            print('Error in find_balance')
        pass

    def find_balance(self, line: str):
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
                #print(balance, pre_balance)
            else:
                raise print(f'Error: balance not found')
        except:
            print('Error in find_balance', res_pre_balance, res_balance)
        pass

    def find_balance_date(self, line: str):
        try:
            pattern = r'ОСТАТОК НА \d{2}\.\d{2}\.\d{4}\nОСТАТОК НА \d{2}\.\d{2}\.\d{4}'
            res = re.search(pattern, line)
            #print(res)

            if res:
                balance_date = res.group()

                pre_balance_date = balance_date[11:21]
                balance_date = balance_date[-10:]

                pre_balance_date = self.convert_to_datetime(pre_balance_date)
                balance_date = self.convert_to_datetime(balance_date)

                return balance_date, pre_balance_date
                #print(balance_date, pre_balance_date)
            else:
                raise print('Error: balance_date not found', res)
        except:
            print("Error in find_balance_date")

    def find_operations(self, line: str):
        general_information = list()

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

            date_transaction = list()
            date_processing = list()
            code_transaction = list()
            category = list()
            description = list()
            cost = list()

            for item in general_information:
                item = item.split('\n')
                date_transaction.append(self.convert_to_datetime(item[0], item[1]))
                date_processing.append(self.convert_to_datetime(item[2]))
                code_transaction.append(int(item[3]))
                category.append(item[4])
                description.append(item[5])
                cost.append(convert_to_float(item[6], is_operation=True))
            operations = pd.DataFrame(
                {'date': date_transaction, 'date_processing': date_processing, 'code_transaction': code_transaction, 'category': category, 'description': description, 'cost': cost})
            #(operations)
            return operations
        except:
            print("Error in find_operations", item)
            raise
        pass

    def verification(self):
        try:

            difference = self.balance - self.pre_balance
            print(difference, self.balance, self.pre_balance, self.operations['cost'].sum())
            if abs(difference - self.operations['cost'].sum()) > 0.1:
                raise print('Error some operations were not read correctly')
        except:
            raise
        pass

    def convert_to_datetime(self, date: str, time='', utc=0) -> datetime:
        """
        utc=0 == utc+3  ->  time of Moscow
        :param time: '15.03.2023\n12:56'
        :return: datetime.datetime(2023, 3, 15, 12, 56)
        """
        try:
            if time != '':
                return datetime.strptime(date + time, '%d.%m.%Y%H:%M') + timedelta(hours=utc)
            else:
                return datetime.strptime(date, '%d.%m.%Y') + timedelta(hours=utc)

        except Exception:
            raise print('Error in convert_to_datetime:', date, time)


def convert_to_float(line: str, is_operation=False) -> float:
    try:

        if is_operation:
            if line.count('+') == 0:
                line = '-' + line

        line = line.replace('\xa0', '')
        line = line.replace(' ', '')
        res = float(line.replace(',', '.'))
        if not res:
            raise
        return res
    except:
        error(f'Error in conversation from str to float: {line}')

def extract_text_from_pdf(path: str) -> str:
    try:
        text = ''
        with fitz.open(path) as doc:
            for num, page in enumerate(doc.pages()):
                text += page.getText()

        return text
    except:
        print('PDF-file is not readable')
        raise

def error(line: str):
    print('Error' + line)


if __name__ == '__main__':
    path = 'C:\\Users\\stars\\Downloads\\Документ-2023-03-23-232902.pdf'
    path2 = 'C:\\Users\\stars\\Downloads\\Документ-2023-03-23-232807.pdf'
    pd.set_option('display.max_rows', None)

    # Сброс ограничений на число столбцов
    pd.set_option('display.max_columns', None)

    # Сброс ограничений на количество символов в записи
    pd.set_option('display.max_colwidth', 20)

    start = time.time()
    debit = DebitSberbank()
    debit.set(path)
    end = time.time()
    print('Имя:', debit.name_card)
    print('Валюта:', debit.currency)
    print('Начальный баланс:', debit.pre_balance)
    print('Баланс:', debit.balance)
    print('Начальная дата:', debit.pre_balance_date)
    print('Дата:', debit.balance_date)
    #print(debit.operations)

    debit_test = DebitSberbank()
    debit_test.set('C:\\Users\\stars\\Downloads\\Документ-2023-03-24-000859.pdf')
    print('Имя:', debit_test.name_card)
    print('Валюта:', debit_test.currency)
    print('Начальный баланс:', debit_test.pre_balance)
    print('Баланс:', debit_test.balance)
    print('Начальная дата:', debit_test.pre_balance_date)
    print('Дата:', debit_test.balance_date)
    print(debit_test.operations)


    debit.add(path2)
    #print(debit.operations)

    print('time:', format(end-start))
