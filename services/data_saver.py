import pandas
import os
from flask import session
import statsmodels.tsa.arima.model as sm

def main():
    pass # TODO: добавить отладчик и проверку работоспособности


def init_save_path():
    filepath = os.path.join(os.getcwd(), 'static', 'current_data', str(session['uid']))
    session['workfile'] = filepath


# Данные сохраняем в JSON. Так исключается проблема с движком openpyxl.
# TODO: нужна функция экспорта в формат excel после смены движка. Желательно новый (xlsx).
def save_data(data: pandas.DataFrame, postfix: str = ''):
    data.to_json(session['workfile'] + postfix + '.json')
    # data.to_excel(session['workfile'], engine='openpyxl')


def save_to_excel(data: pandas.DataFrame, filepath: str = 'unnamed.xlsx'):
    data.to_excel(filepath)


def save_model(model: sm.ARIMAResults, filepath: str = ''):
    if filepath == '':
        filepath = os.path.join(os.getcwd(), 'static', 'models', str(session['uid']) + '_model.mdl')
    model.save(filepath)


def show_save_dialog(title: str = 'Сохранить файл', filetypes=(('Все файлы', '*.*'),)) -> str:
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    result = filedialog.asksaveasfilename(title=title, filetypes=filetypes)
    root.attributes('-topmost', False)
    root.destroy()
    return result
