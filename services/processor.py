import pandas as pd


def main() -> None:
    from pprint import pprint
    import tkinter as tk
    from tkinter import filedialog
    from services.data_loader import load_data

    root = tk.Tk()
    root.withdraw()
    filename = filedialog.askopenfilename()
    root.destroy()

    data = load_data(filename, 'xlsx', index_col='index')

    test = adopt_arima(data['col1'])
    pprint(test)


# =========== Описательная статистика ==========
def describe(data: pd.DataFrame) -> dict:
    import statistics
    from services import preprocessor

    result = {}
    # Собираем готовую статистику
    result = data.describe().to_dict()

    # Обрабатываем каждую колонку для остальной статистики
    for col in data.columns:
        # Определяем медиану
        median = statistics.median(data[col].values)

        # Определяем моду
        moda = statistics.mode(data[col].values)

        # Определяем наибольшее отклонение
        variance = statistics.variance(data[col].values)

        # Определяем стационарность ряда
        if preprocessor.is_stationary(data[col].values):
            stationary = 'Стационарный'
        else:
            stationary = 'Нестационарный'

        # Обновляем словарь, относящийся к колонке
        new_val = result[col]

        # Дописываем туда посчитанное
        new_val.update({'median': median})
        new_val.update({'moda': moda})
        new_val.update({'variance': variance})
        new_val.update({'stationary': stationary})

        # Обновляем результирующий словарь.
        result.update({col: new_val})
    return result
# ==============================================


# ============= Линейная регрессия =============
def linear_regression(data: pd.Series, sample_len: int = 24, predict_depth: int = 12):
    # Подготовку набора данных перенес в nnet.py. Смысл тот-же, но функционал шире
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_absolute_error
    from services.nnet import prepare_dataset
    from bokeh.plotting import figure
    from bokeh.resources import INLINE
    from bokeh.embed import components
    from datetime import timedelta
    from pprint import pprint

    train_data = prepare_dataset(data, sample_len=sample_len)
    x_train = train_data['x'][:-10]
    x_test = train_data['x'][-10:]
    y_train = train_data['y'][:-10]
    y_test = train_data['y'][-10:]
    model = LinearRegression()
    model.fit(x_train, y_train)
    prediction = model.predict(x_test)
    mae = mean_absolute_error(prediction, y_test)

    fig = figure(title='Результат настройки модели', plot_width=1000, x_axis_type='datetime')
    axis_x = data.index
    interval = timedelta(days=31)
    axis_x_pred = [axis_x[-1] + interval]
    work_data = data[-sample_len:]
    prediction = model.predict(pd.DataFrame(work_data).transpose())
    work_data = work_data.append(pd.Series(prediction, index=[axis_x_pred[-1]]))
    work_data = work_data[-sample_len:]
    for i in range(predict_depth - 1):
        axis_x_pred.append(axis_x_pred[-1] + interval)
        prediction = model.predict(pd.DataFrame(work_data).transpose())
        work_data = work_data.append(pd.Series(prediction, index=[axis_x_pred[-1]]))
        work_data = work_data[-sample_len:]
    work_data = work_data[-predict_depth:]
    fig.line(axis_x, data.values, line_width=2, legend_label='Исходные данные')
    fig.line(axis_x_pred, work_data.values, line_width=4, line_color='green', legend_label='Прогноз')

    fig.legend.location = "top_left"

    script, div = components(fig)
    return {'js_res': INLINE.render_js(), 'css_res': INLINE.render_css(), 'script': script, 'div': div, 'model': model}
# ==============================================


# ============= ARIMA ==========================
def arima_regression(data: pd.Series, p: int = 0, d: int = 0, q: int = 0, test_len: int = 0) -> dict:
    from bokeh.plotting import figure
    from bokeh.resources import INLINE
    from bokeh.embed import components
    import statsmodels.api as sm
    import datetime

    fig = figure(title='Результат настройки модели', plot_width=1000, x_axis_type='datetime')
    if test_len > 0:
        axis_x = data.index[:(-1 * test_len)]
        axis_x_pred = data.index[(-1 * (test_len + 1)):]
        trn = data[(-1 * (test_len + 1)):]
        data = data[:(-1 * test_len)]
        fig.line(axis_x, data, line_width=2, legend_label='Исходные данные')
        fig.line(axis_x_pred, trn, line_width=4, line_color='yellow', legend_label='Тестовая выборка')
    else:
        axis_x = data.index
        axis_x_pred = axis_x.to_list()
        for r in range(11):
            axis_x_pred.append(axis_x_pred[-1] + datetime.timedelta(days=1))
        axis_x_pred = axis_x_pred[-12:]
        fig.line(axis_x, data, line_width=2, legend_label='Исходные данные')

    model = sm.tsa.arima.ARIMA(data, order=(p, d, q)).fit()

    pred = model.predict(start=len(axis_x), end=len(axis_x)+len(axis_x_pred)-1, typ='levels')
    fig.line(axis_x_pred, pred, line_width=4, line_color='green', legend_label='Прогноз')
    fig.legend.location = "top_left"

    script, div = components(fig)
    return {'js_res': INLINE.render_js(), 'css_res': INLINE.render_css(), 'script': script, 'div': div, 'model': model}


def adopt_arima(data: pd.Series) -> dict:
    import statsmodels.api as sm
    from services import preprocessor

    train = data[-6:]
    data = data[:-6]
    min_error = None
    current_model = None

    for p in range(1):
        for d in range(10):
            for q in range(10):
                model = sm.tsa.arima.ARIMA(data, order=(p, d, q)).fit()
                pred = model.predict(start=len(data.to_list()), end=len(data.to_list()) + 5, typ='levels')
                error = preprocessor.count_sko(train, pred)
                if (min_error is None) or (min_error > error):
                    min_error = error
                    current_model = {'p': p, 'd': d, 'q': q}

    current_model.update({'msqer': min_error})
    return current_model
# ==============================================


# ================= X 13 =======================
# def arima_regression(data: pd.Series, p: int = 0, d: int = 0, q: int = 0, test_len: int = 0) -> dict:
#     from bokeh.plotting import figure
#     from bokeh.resources import INLINE
#     from bokeh.embed import components
#     import statsmodels.api as sm
#     import datetime
#
#     fig = figure(title='Результат настройки модели', plot_width=1000, x_axis_type='datetime')
#     if test_len > 0:
#         axis_x = data.index[:(-1 * test_len)]
#         axis_x_pred = data.index[(-1 * (test_len + 1)):]
#         trn = data[(-1 * (test_len + 1)):]
#         data = data[:(-1 * test_len)]
#         fig.line(axis_x, data, line_width=2, legend_label='Исходные данные')
#         fig.line(axis_x_pred, trn, line_width=4, line_color='yellow', legend_label='Тестовая выборка')
#     else:
#         axis_x = data.index
#         axis_x_pred = axis_x.to_list()
#         for r in range(5):
#             axis_x_pred.append(axis_x_pred[-1] + datetime.timedelta(days=1))
#         axis_x_pred = axis_x_pred[-6:]
#         fig.line(axis_x, data, line_width=2, legend_label='Исходные данные')
#
#     model = sm.tsa.arima.x13(data).fit()
#
#     pred = model.predict(start=len(axis_x), end=len(axis_x)+len(axis_x_pred)-1, typ='levels')
#     fig.line(axis_x_pred, pred, line_width=4, line_color='green', legend_label='Прогноз')
#     fig.legend.location = "top_left"
#
#     script, div = components(fig)
#     return {'js_res': INLINE.render_js(), 'css_res': INLINE.render_css(), 'script': script, 'div': div, 'model': model}
# ==============================================

if __name__ == '__main__':
    main()
