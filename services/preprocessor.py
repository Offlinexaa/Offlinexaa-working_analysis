import pandas as pd
import copy


# ============ Удаление дубликатов =================
# Адаптер к стандартной функции pandas
def deduplicate(data: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates from data frame.
    Duplicates must be with indexes"""
    return data.drop_duplicates()
# ==================================================


# ====================== Преобразование в период-к-периоду ====================
def reshape_to_period_over_period(
    data: pd.DataFrame,
    column: str
) -> pd.DataFrame:
    data_in = copy.deepcopy(data)
    data_pop = data_in.to_dict('series')
    first = True
    old_v = 0
    for k, v in data_pop[column].items():
        if first:
            old_v = v
            data_pop[column].update({k: 100.0})
            first = False
        else:
            data_pop[column].update({k: 100 + 100*(v - old_v)/old_v})
            old_v = v
    return pd.DataFrame(data_pop)
# =============================================================================


# ============== Нормализация ряда ====================
# TODO: Разобраться с проблемами при индексации по
#  времени - ряд превращается в прямую y=1
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
# Обобщённый тест Дикки-Фуллера на наличие единичных корней
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
def get_base_column(
    data: pd.DataFrame,
    column_name: str,
    mode: str = 'abs'
) -> list:
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
    for column_name in data.columns:
        data[column_name] = get_base_column(data, column_name, mode)
    return data
# ============================================================


# ============ Расчет среднеквадратичной ошибки =============
def count_single_sko(a: float, b: float) -> float:
    if a > b:
        return abs(a - b)
    else:
        return abs(b - a)


def count_sko(a: pd.Series, b: pd.Series) -> float:
    if len(a.to_list()) != len(b.to_list()):
        raise IndexError("Серии разной длинны")
    length = len(a.to_list())
    result = 0
    for x in range(length):
        result += count_single_sko(a[x], b[x])
    return result/length
# ===========================================================


# =========== Процедура отладки, в релизе не нужна ===============
def main() -> None:
    pass


if __name__ == '__main__':
    main()
