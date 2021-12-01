import pandas as pd
import copy

# =========== Процедура отладки, в релизе не нужна ===============
def main() -> None:
    import pprint
    import tkinter as tk
    from tkinter import filedialog
    from services.data_loader import load_data

    root = tk.Tk()
    root.withdraw()
    filename = filedialog.askopenfilename()
    root.destroy()

    data = load_data(filename, 'xlsx', index_col='index')
    new_data = df_to_base(data)

# ===============================================================


# ============ Удаление дубликатов =================
# Адаптер к стандартной функции pandas
def deduplicate(data: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates from data frame.
    Duplicates must be with indexes"""
    return data.drop_duplicates()
# ==================================================


# ====================== Преобразование в период-к-периоду ========================
def reshape_to_period_over_period(data: pd.DataFrame, column: str) -> pd.DataFrame:
    data_in = copy.deepcopy(data)
    data_pop = data_in.to_dict('series')
    first = True
    old_v = 0
    for k, v in data_pop[column].items():
        if first == True:
            old_v = v
            data_pop[column].update({k: 100.0})
            first = False
        else:
            data_pop[column].update({k: 100 + 100*(v - old_v)/old_v})
            old_v = v
    return pd.DataFrame(data_pop)
# =================================================================================


# ============== Нормализация ряда ====================
# TODO: Разобраться с проблемами при индексации по
#  времени - ряд превращается в прямую y=1
#  UPD 11.10.2020: Требуется альтернативная библиотека.
#  Создан форк с исправлением бага, но в мейн он не добавлен.
def auto_normalize(data: pd.DataFrame, col_name: str = None) -> pd.DataFrame:
    from sklearn import preprocessing

    if (col_name is None) or (col_name == 'Все'):
        x = data.to_numpy()
    else:
        x = data[col_name].to_numpy()
    normalizer = preprocessing.Normalizer()
    x_normalized = normalizer.fit_transform(x)
    return pd.DataFrame(x_normalized)
# =====================================================


# ============== Определение стационарности ряда =============
# Обощённый тест Дикки-Фуллера на наличие единичных корней
def is_stationary(data: pd.DataFrame) -> bool:
    from statsmodels import api as sm

    describe = sm.tsa.adfuller(data)
    if describe[0] > describe[4]['5%']:
        return False
    else:
        return True
# ============================================================


# =============== Разность со сдвигом ========================
def differ_x(data: pd.DataFrame, lag: int) -> pd.DataFrame:
    return data.diff(periods=lag).dropna()
# ============================================================


# ======== Пересчет столбца в базисный показатель ============
def get_base_column(data: pd.DataFrame, column_name: str, mode: str ='abs') -> list:
    col = data[column_name]
    new_col = []
    first = True
    for value in col:
        if first:
            new_col.append(value)
            # new_col.append(100)
            first = False
        elif mode == 'abs':
            new_col.append(new_col[-1]*value/100)
        elif mode == 'add':
            new_col.append(new_col[-1]+value)
    return new_col
# ============================================================


# ========= Пересчет датафрейма в базисный вариант ===========
def df_to_base(data: pd.DataFrame, mode: str = 'abs') -> pd.DataFrame:
    # from pprint import pprint
    for column_name in data.columns:
        # ======= debug ======
        # print('working on: ' + column_name)
        # ====================
        data[column_name] = get_base_column(data, column_name, mode)
        #data.rename(columns={column_name: column_name+'_base'}, inplace= True)
    # ======= debug ======
    # pprint(data.head(5))
    # pprint(data.tail(5))
    # ====================
    return data
#============================================================


# ============ Расчет среднеквадратичной ошибки =============
def count_single_sko(a: float, b: float) -> float:
    import math
    # a = abs(a)
    # b = abs(b)
    if a > b:
        return abs(a - b)
    else:
        return abs(b - a)


def count_sko(a: pd.Series, b: pd.Series) -> float:
    # print('Length A = ' + str(len(a.to_list())))
    # print('Length B = ' + str(len(b.to_list())))
    if len(a.to_list()) != len(b.to_list()):
        raise IndexError("Серии разной длинны")
    length = len(a.to_list())
    result = 0
    for x in range(length):
        result += count_single_sko(a[x], b[x])
    return result/length
# ===========================================================


if __name__ == '__main__':
    main()
