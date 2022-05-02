import pandas as pd
from pprint import pprint
from sklearn.metrics import mean_absolute_error
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import ARDRegression, HuberRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.exceptions import ConvergenceWarning


def prepare_dataset(data: pd.Series, sample_len: int = 24) -> dict:
    """Разбивает ряд формата """
    data = data.to_list()
    length = len(data)
    past_days = []
    past_column = []
    current_day = []
    for day in range(sample_len, length):
        past_slice = list(data[(day - sample_len):day])
        past_days.append(past_slice)
        current_day.append(data[day])
    for i in range(sample_len):
        past_column.append(f'past_{i}')
    learn_samples = pd.DataFrame(past_days, columns=past_column)
    target_values = pd.Series(current_day, name='target')
    data = {
        'x': learn_samples,
        'y': target_values,
        'sample_len': sample_len,
    }
    return data


def get_best_model(learn_samples: pd.DataFrame, target_vales: pd.Series):
    """
    Обучает и тестирует модели на предоставленных наборах данных.
    Возвращает модель с наимеьшим значением абсолютной ошибки в
    тестовой выборке.
    """
    models = init_models_pool()
    x_train = learn_samples[:-10]
    x_test = learn_samples[-10:]
    y_train = target_vales[:-10]
    y_test = target_vales[-10:]
    best_model = ''
    best_mae = None
    for model in models:
        try:
            model.fit(x_train, y_train)
        except ConvergenceWarning:
            continue
        prediction = model.predict(x_test)
        mae = mean_absolute_error(prediction, y_test)
        if best_mae is None or mae < best_mae:
            best_mae = mae
            best_model = model
    return [best_model, round(best_mae*100, 3)]


def init_models_pool() -> list:
    """Инициализация моделей нейронных сетей и других методов
    машинного обучения."""
    mlp_model0 = MLPRegressor()
    mlp_model1 = MLPRegressor(
        max_iter=1000,
        hidden_layer_sizes=(200, 200, 200)
    )
    ard_model0 = ARDRegression()
    ard_model1 = ARDRegression(n_iter=1000)
    ada_model = AdaBoostRegressor(n_estimators=150)
    hub_model = HuberRegressor(epsilon=1.05, max_iter=2000)
    return [mlp_model0, mlp_model1,
            ard_model0, ard_model1,
            ada_model,
            hub_model]


def predict(
    data: pd.Series,
    model,
    sample_len: int = 24,
    depth: int = 12
) -> list:
    """
    Мысль: возвращаем список вместе с прогнозными значениями,
    после чего собираем из него Series с добавлением оси Х в
    качестве индексов.
    """
    data_list = data.to_list()
    for i in range(depth):
        past_column = []
        for j in range(sample_len):
            past_column.append(f'past_{j}')
        current = pd.DataFrame(
            data_list[-sample_len:],
            index=past_column
        ).transpose()
        prediction = model.predict(current)
        data_list.append(round(*prediction, 3))
    return data_list[-depth:]


def main():
    import data_loader

    file = data_loader.show_open_dialog()
    data = data_loader.load_data(file, 'xlsx', 'index')
    series = data['Все товары и услуги']
    train_data = prepare_dataset(series)
    model = get_best_model(train_data['x'], train_data['y'])
    pprint(model)
    result = predict(series, model)
    pprint(result)


if __name__ == '__main__':
    main()
