"""Модуль, отвечающий за загрузку данных."""
import pandas as pd
import os
from flask import session
import statsmodels.tsa.arima.model as sm
import urllib.request


def load_workfile(postfix: str = '') -> pd.DataFrame:
    """Функция загрузки текущего рабочего файла."""
    return load_data(session['workfile'] + postfix + '.json', 'json')


def load_basefile() -> pd.DataFrame:
    """Функция загрузки базисны данных."""
    return load_workfile('_basis')


def load_data(
    file_name: str,
    file_type: str,
    index_col: str = None
) -> pd.DataFrame:
    """
    Общая функция загрузки данных.
    Читает файл в объект pandas.DataFrame, удаляя из набора столбцы,
    содержащие NaN или None. В табличных файлах индексы должны содержаться
    в столбце index_col.
    Поддерживает форматы: *.csv, *.xlsx, *.json.
    """
    file_path = os.path.abspath(file_name)
    if not os.path.exists(file_path):
        raise IOError('File is not existed')
    if file_type == 'csv':
        return pd.read_csv(
            file_path,
            index_col=index_col
        ).dropna()
    elif file_type == 'xlsx':
        return pd.read_excel(
            file_path,
            index_col=index_col,
            engine='openpyxl'
        ).dropna()
    elif file_type == 'json':
        return pd.read_json(file_path).dropna()


def url_load(url: str, filepath: str) -> pd.DataFrame:
    """
    Функция загрузки по URL.
    Загружает и преобразует к пригодному для обработки виду файлы
    типовых сводных публичных отчётов по региональной экономической
    ситуации центрального аппарата.
    """
    urllib.request.urlretrieve(url, filepath)
    data = pd.read_excel(filepath, skiprows=2, engine='openpyxl')
    data_t = data.T.dropna(axis='columns')
    colnames = next(data_t.iterrows())[1]
    data_t = data_t.drop(data_t.index[0])
    data_t = data_t.rename(columns=colnames)
    data_t.index.names = ['index']
    return data_t


def load_model(file_name: str = '') -> sm.ARIMAResults:
    """Функция загрузки модели ARIMA."""
    if file_name == '':
        file_name = os.path.join(
            os.getcwd(),
            'static',
            'models',
            str(session['uid']) + '_model.mdl'
        )
    model = sm.ARIMAResults.load(file_name)
    return model


def show_open_dialog(
    title: str = 'Открыть файл',
    filetypes=(('Все файлы', '*.*'),)
) -> str:
    """Функция показывает диалог выбора файля для загрузки."""
    import tkinter as tk
    import tkinter.filedialog as filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    result = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.attributes('-topmost', False)
    root.destroy()
    return result


def main():
    pass


if __name__ == '__main__':
    main()
