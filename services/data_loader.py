import pandas as pd
import os
from flask import session
import statsmodels.tsa.arima.model as sm
import urllib.request


def main() -> None:
    pass    # TODO: добавить отладчик и проверку работоспособности


def load_workfile() -> pd.DataFrame:
    return load_data(session['workfile']+'.json', 'json')


def load_basefile() -> pd.DataFrame:
    return load_data(session['workfile']+'_basis.json', 'json')


def load_data(file_name: str, file_type: str, index_col: str = None) -> pd.DataFrame:
    # TODO Проверить формат csv (у json проблемы с переиндексированием по дефолту)
    # Нагуглил костыль - используется scipy 2.1.13
    file_path = os.path.abspath(file_name)          # Получем полный путь к файлу
    if not os.path.exists(file_path):               # Если такого файла нет
        raise IOError('File is not existed')        # вызываем исключение по этому поводу
    if file_type == 'csv':                          # В зависимости от указанного формата
        return pd.read_csv(file_path, index_col=index_col).dropna() #.to_json()     # считываем файлы разной функцией из
    elif file_type == 'xlsx':                       # модуля pandas
        return pd.read_excel(file_path, index_col=index_col, engine='openpyxl').dropna() #.to_json()
    elif file_type == 'json':
        return pd.read_json(file_path).dropna() #.to_json()


def url_load(url: str, filepath: str) -> pd.DataFrame:
    urllib.request.urlretrieve(url, filepath)
    data = pd.read_excel(filepath, skiprows=2, engine='openpyxl')
    data_t = data.T.dropna(axis='columns')
    colnames = next(data_t.iterrows())[1]
    data_t = data_t.drop(data_t.index[0])
    data_t = data_t.rename(columns=colnames)
    data_t.index.names = ['index']
    return data_t


def load_model(file_name: str = '') -> sm.ARIMAResults:
    if file_name == '':
        file_name = os.path.join(os.getcwd(), 'static', 'models', str(session['uid']) + '_model.mdl')
    model = sm.ARIMAResults.load(file_name)
    return model


def show_open_dialog(title: str = 'Открыть файл', filetypes=(('Все файлы', '*.*'),)) -> str:
    import tkinter as tk
    import tkinter.filedialog as filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    result = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.attributes('-topmost', False)
    root.destroy()
    return result

if __name__ == '__main__':
    main()