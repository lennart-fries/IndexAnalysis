import pandas as pd
import numpy as np

import yfinance as yf


def standardize_to_100(series):
    first_value = series.dropna().iloc[0]
    return series / first_value * 100


def collect_yfin_data():
    indices = {"^GSPC": "S&P 500",
           "^IXIC": "NASDAQ",
           "^DJI": "Dow Jones"}

    df = pd.DataFrame()

    for i, name in indices.items():
        data = yf.Ticker(i)
        history = data.history(period="max", interval="1mo")
        close = history['Close']
        df[name] = close

    df.index = pd.to_datetime(df.index)
    df.to_csv("../data/230822_Misc-Indices-Monthly.csv")


def get_indices_data(produce_csv=False):
  msci_indices, other_indices = preprocess_indices_data()
  indices_dataset = concatenate_indices_data(msci_indices, other_indices)

  if produce_csv:
    indices_dataset.to_csv('data/indices_data_processed.csv')

  return indices_dataset


def preprocess_indices_data():
  msci_indices = pd.read_excel("data/230822_MSCI-Data-Monthly.xls", skiprows=6, skipfooter=19, index_col=0)
  msci_indices.index = (x.strftime('%Y-%m') for x in pd.to_datetime(msci_indices.index))
  msci_indices.sort_index(inplace=True)

  for col in msci_indices.columns:
    if msci_indices[col].dtype == 'object':
        msci_indices[col] = msci_indices[col].str.replace(',', '').astype(float)

  msci_indices["ACWI IMI IMI (Large+Mid+Small Cap)"] = standardize_to_100(msci_indices["ACWI IMI IMI (Large+Mid+Small Cap)"])

  other_indices = pd.read_csv("data/230822_Misc-Indices-Monthly.csv", index_col = 0)
  other_indices.index = [x.strftime('%Y-%m') for x in pd.to_datetime(other_indices.index)]
  other_indices = other_indices.apply(standardize_to_100)

  return msci_indices, other_indices


def concatenate_indices_data(*dfs):
  concatenated_data = pd.concat(dfs, axis=1, copy=False)

  column_names = {
    'ACWI IMI IMI (Large+Mid+Small Cap)': 'ACWI IMI',
    'ACWI Standard (Large+Mid Cap)': 'ACWI',
    'WORLD Standard (Large+Mid Cap)': 'World',
    'EUROPE Standard (Large+Mid Cap)': 'Europe',
    'NORTH AMERICA Standard (Large+Mid Cap)': 'North America',
    'EM (EMERGING MARKETS) Standard (Large+Mid Cap)': 'Emerging Markets'
  }

  concatenated_data.rename(columns=column_names, inplace=True)

  return concatenated_data


def add_custom_index(indices_data, weight_industrial_markets = 0.7, weight_emerging_markets = 0.3, initial_value=100):
  indices_data.index = pd.to_datetime(indices_data.index)
  monthly_percentage_change = indices_data.pct_change()

  custom_index = pd.concat([monthly_percentage_change["World"], monthly_percentage_change["Emerging Markets"]], axis=1).replace(0,np.nan).dropna()
  custom_index['Composite Returns'] = custom_index["World"] * weight_industrial_markets + custom_index["Emerging Markets"] * weight_emerging_markets
  custom_index['Composite Value'] = (custom_index['Composite Returns']+1).cumprod() * initial_value

  custom_index_name = f'{np.round(weight_industrial_markets*100):.0f}/{np.round(weight_emerging_markets*100):.0f}'

  indices_data.loc['1987-12', custom_index_name] = initial_value
  indices_data.loc['1988-01':, custom_index_name] = custom_index['Composite Value']
  indices_data.index = (x.strftime('%Y-%m') for x in pd.to_datetime(indices_data.index))

  return indices_data