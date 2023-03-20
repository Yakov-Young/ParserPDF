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
        self.pre_balance = ''
        self.balance = 0.0

    def set(self, line: str):
        self.name_card = self.set_name(line)
        self.currency = self.set_currency(line)
        self.balance = self.set_balance(line)
        self.operations = self.set_operations(line)

    def set_name(self, line: str):
        """
        Sample:
        MIR •••• 9999
        """
        pattern = r'(MIR|Visa|MasterCard|Maestro)(\s\w+)?\s(•{4})\s(\d{4})'
        res = re.search(pattern, line)
        if res:
            print(res.group())
            return res.group()
        else:
            raise print('Имя карты не определено')
        pass

    def set_currency(self, line: str):
        """
        Sample:
        Валюта
        РУБЛЬ РФ
        """
        try:
            pattern = r'{}\n[\S ]+'.format(self.name_card)
            res = re.search(pattern, line)

            res = res.group()
            res = res[len(self.name_card) + 1:]
            print(res)
            return res

        except:
            raise print('Валюта не определена', res)
        pass

    def set_balance(self, line: str) -> float:
        pattern = r'ВСЕГО ПОПОЛНЕНИЙ\n[\S\xa0]+\n[\S\xa0]+'
        res = re.search(pattern, line).group()

        if res:
            pattern = r'[0-9, \xa0]+$'
            res = re.search(pattern, res)

        if res:
            res = res.group()
            temp = convert_to_float(res)
            print(temp)
            return temp
        else:
            raise print(f'Баланс не определен')
        pass

    def set_operations(self, line: str):
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
        pattern = r'\d{2}\.\d{2}\.\d{4}\n\d{2}:\d{2}\n\d{2}\.\d{2}\.\d{4}\n\d{6}\n[\S \(\+\)]+\n[ \S]+\n[\S\xa0]+'
        general_information = re.findall(pattern, line)


        date_transaction = list()
        date_processing = list()
        code_transaction = list()
        category = list()
        description = list()
        cost = list()

        for i in general_information:
            item = i.split('\n')
            date_transaction.append(self.convert_to_datetime(item[0], item[1]))
            date_processing.append(self.convert_to_datetime(item[2]))
            code_transaction.append(int(item[3]))
            category.append(item[4])
            description.append(item[5])
            cost.append(convert_to_float(item[6], is_operation=True))
        operations = pd.DataFrame(
            {'date': date_transaction, 'date_processing': date_processing, 'code_transaction': code_transaction, 'category': category, 'description': description, 'cost': cost})
        print(operations)
        return operations
        pass

    def convert_to_datetime(self, date: str, time=None, utc=0) -> datetime:
        """
        utf=0 == utc+3  ->  Время Москвы
        :param time: '15.03.2023\n12:56'
        :return: datetime.datetime(2023, 3, 15, 12, 56)
        """
        try:
            if time:
                return datetime.strptime(date + time, '%d.%m.%Y%H:%M') + timedelta(hours=utc)
            else:
                return datetime.strptime(date, '%d.%m.%Y') + timedelta(hours=utc)

        except Exception:
            raise print('Error in convert_to_datetime', date, time)


def convert_to_float(line: str, is_operation=False) -> float:
    try:

        if is_operation:
            if line.count('+') == 0:
                line = '-' + line

        line = line.replace('\xa0', '')
        line = line.replace(' ', '')
        res = float(line.replace(',', '.'))

        return res
    except:
        error(f'Error in conversation from str to float: {line}')

def extract_text_from_pdf(path: str) -> str:
    text = ''
    with fitz.open(path) as doc:
        for num, page in enumerate(doc.pages()):
            text += page.getText()

    return text

def error(line: str):
    print('Erroe' + line)


if __name__ == '__main__':
    path2 = 'C:\\Users\\stars\\Downloads\\Документ-2023-03-19-000142.pdf'

    start = time.time()
    a = extract_text_from_pdf(path2)
    print(a)
    debit = DebitSberbank()
    debit.set(a)
    end = time.time()
    print(format(end-start))
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
