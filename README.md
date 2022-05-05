# working_analysis

Инструмент визуализации и анализа данных. 

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
https://github.com/Offlinexaa/working_analysis.git
```

```
cd working_analysis
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip setuptools
```

```
pip install -r requirements.txt
```

Запустить проект:

```
python3 main.py
```

### Требования

Python 3.5 или выше

Google chrome 86 или выше

### Применяемые технологии

Пользовательский интерфейс: Flask, jinja2, Bootstrap (4.6), Tkinter

Обработка данных: Scikit-learn, Statsmodels, Pandas, Numpy

Визуализация данных: Matplotlib, Bokeh

### Планы по доработке

- Приведение к стандарту по PEP8
- Добавить строки документации
- Вынести во внешний модуль компановку графиков для Bokeh
- Заменить реализацию append_to_excel в модуле data_saver на свою

# Примечание

Опубликована часть инструмента, на которую получено разрешение работодателя.
