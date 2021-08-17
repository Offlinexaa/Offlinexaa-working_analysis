import pandas as pd
from services import data_loader
from pprint import pprint
from urllib import request


def main():
    url = 'http://cbr.ru/vfs/regions/infl/infl_94.xlsx'
    dest = 'getfile.xlsx'
    bin_data = request.urlretrieve(url=url, filename=dest)

    data = pd.read_excel(dest, skiprows=2, engine='openpyxl')
    data_t = data.T.dropna(axis='columns')
    colnames = next(data_t.iterrows())[1]
    pprint(colnames.to_dict())
    pprint(data_t.head(5))

    data_t = data_t.drop(data_t.index[0])
    data_t = data_t.rename(columns=colnames)
    pprint(data_t.head(5))


if __name__ == '__main__':
    main()