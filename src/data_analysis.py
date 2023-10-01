import pandas as pd
import numpy as np

def get_CAGR(indices_data, index_age, initial_value=100):
  CAGR = ((indices_data.iloc[-1] / initial_value) ** (1/index_age) - 1) * 100

  return CAGR


def get_annualized_averages(monthly_percentage_change):
  annualized_returns = monthly_percentage_change.mean() * 12 * 100
  annualized_volatility = monthly_percentage_change.std() * (12 ** 0.5) * 100

  return annualized_returns, annualized_volatility


def get_maximum_drawdown(indices_data):
  rolling_max = indices_data.cummax()
  drawdown = (indices_data - rolling_max) / rolling_max
  maximum_drawdown = np.abs(drawdown.min()*100)

  return maximum_drawdown


def get_sharpe_ratio(monthly_percentage_change, risk_free_rate=0.0):
  sharpe_ratio = (monthly_percentage_change.mean() - risk_free_rate) / monthly_percentage_change.std()
  return sharpe_ratio


def calculate_KPI(indices_data):
  monthly_percentage_change = indices_data.pct_change()
  index_age = indices_data.apply(lambda col: len(col.dropna())).div(12)
  cagr = get_CAGR(indices_data, index_age)
  average_returns, average_volatility = get_annualized_averages(monthly_percentage_change)
  max_drawdown = get_maximum_drawdown(indices_data)
  sharpe_ratio = get_sharpe_ratio(monthly_percentage_change)
  indicators = pd.concat([index_age, cagr, average_returns, average_volatility,
                      max_drawdown, sharpe_ratio],
                    keys=['Index Age', 'CAGR (%)', 'Mean (%)', 'Volatility (%)',
                            'Max Drawdown (%)', "Sharpe Ratio"], axis=1)
  indicators = indicators.applymap(lambda x: round(x, 2) if not pd.isna(x) else x)
  
  return indicators


def perform_data_backtest(indices_data, years=20):
    # Calculate the number of periods based on data frequency (assuming data is monthly)
    periods = years * 12

    # Calculate rolling CAGR for each investment
    rolling_CAGR = ((indices_data.shift(-periods) / indices_data) ** (1/years) - 1) * 100

    # Determine best, worst, and average CAGR
    best_case = rolling_CAGR.max()
    worst_case = rolling_CAGR.min()
    average_case = rolling_CAGR.mean()

    # Combine results into a DataFrame
    results = pd.DataFrame({
        'Best Case CAGR (%)': best_case,
        'Average Case CAGR (%)': average_case,
        'Worst Case CAGR (%)': worst_case
    })

    return results