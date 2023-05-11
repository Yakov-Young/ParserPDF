from datetime import datetime, timedelta

import fitz
import pandas as pd
import matplotlib.pyplot as plt

def convert_to_datetime(date: str, time='', utc=0) -> datetime:
    """
    :param utc: utc=0 == utc+3  ->  time of Moscow
    :param date: '15.03.2023'
    :param time: '12:56'
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
        if not res and res != 0:
            raise
        return res
    except:
        raise print('Error in conversation from str to float', line)


def extract_text_from_pdf(path: str) -> str:
    try:
        text = ''
        with fitz.open(path) as doc:
            for num, page in enumerate(doc.pages()):
                text += page.getText()

        return text
    except:
        raise print('PDF-file is not readable')

def get_category_from_df(data: pd.DataFrame, type_operation='all'):
    category_name = data.category.unique()
    category = {}

    for item in category_name:
        costs_by_category = data[(data['category'] == item)]['cost']
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

def paint(data, title='Круговая диаграмма'):
    data = {k: v for k, v in sorted(data.items(), key=lambda item: item[1])}

    values = list(data.values())
    data_names = data.keys()

    if sum(data.values()) < 0:
        values = [v * -1 for v in values if v < 0]

    total = sum(values)

    labels = [f'{name} ({val / total:.1%})' for name, val in zip(data_names, values)]

    fig1, ax1 = plt.subplots()
    ax1.pie(values)
    ax1.legend(loc=4, bbox_to_anchor=(0.35, 0.50), labels=labels, title=title)
    plt.show()