import numpy as np

def block_bootstrap(returns, investments, investment_interval, block_size=12, n_years=30, n_iterations=10000, initial_investment=1000, value_table=False, continue_investing=0.0, return_timeseries=False):
    """
    Bootstraps the given returns data using block sampling to estimate the distribution of final investment values.

    Parameters:
    - returns: Array-like of monthly returns.
    - investments: Array-like of investment amounts.
    - investment_interval: String indicating the frequency of investments ("M" for monthly, "Q" for quarterly, "Y" for yearly, "YM" for yearly values given that are to be invested monthly for each year).
    - block_size: Integer indicating the size of each block for bootstrapping.
    - n_years: Number of years for the simulation.
    - n_iterations: Number of bootstrap iterations.
    - initial_investment: Initial investment amount.
    - value_table: Boolean indicating whether to return all final values from the bootstrap iterations.
    - continue_investing: Multiplier for investments after the investments array is exhausted.
    - return_timeseries: Boolean indicating whether to return the time series data for each iteration.

    Returns:
    Dictionary containing:
    - Mean, median, and standard deviation of final values.
    - Confidence intervals for final values.
    - Mean, median, and standard deviation of yearly returns.
    - (Optional) All final values from the bootstrap iterations.
    - (Optional) Time series data for each iteration.
    """
    np.random.seed(42)

    n_months = n_years * 12
    final_values = []
    yearly_returns_list = []
    timeseries_data = []

    for _ in range(n_iterations):
        sampled_returns = []

        for _ in range(n_months // block_size):
            start_idx = np.random.randint(0, len(returns) - block_size + 1)
            sampled_return = returns[start_idx:start_idx+block_size]
            sampled_returns.extend(sampled_return)

        # Apply investments based on the investment_interval
        total_value = initial_investment
        values = [total_value]
        for i, monthly_return in enumerate(sampled_returns):
            if investment_interval == "M":
                investment_amount = investments[min(i, len(investments)-1)]
            elif investment_interval == "Q" and i % 3 == 0:
                investment_amount = investments[min(i//3, len(investments)-1)]
            elif investment_interval == "Y" and i % 12 == 0:
                investment_amount = investments[min(i//12, len(investments)-1)]
            elif investment_interval == "YM":
                investment_amount = investments[min(i//12, len(investments)-1)]
            else:
                investment_amount = 0  # No investment for this month
            
            if continue_investing and i >= len(investments):
                investment_amount = investments[-1] * continue_investing

            total_value += investment_amount
            total_value *= (1 + monthly_return)
            values.append(total_value)

        final_values.append(values[-1])
        if return_timeseries:
            timeseries_data.append(values)

        # Calculate yearly returns for the bootstrapped sample
        yearly_returns = [(np.array(sampled_returns[i:i+12]) + 1).prod() - 1 for i in range(0, len(sampled_returns), 12)]
        yearly_returns_list.extend(yearly_returns)

    # Calculate statistics for final values
    mean_final_value = np.mean(final_values)
    median_final_value = np.median(final_values)
    std_final_value = np.std(final_values)

    # Confidence intervals for final values
    ci_68 = (np.percentile(final_values, 16), np.percentile(final_values, 84))
    ci_95 = (np.percentile(final_values, 2.5), np.percentile(final_values, 97.5))
    ci_997 = (np.percentile(final_values, 0.15), np.percentile(final_values, 99.85))

    # Calculate statistics for yearly returns
    mean_yearly_return = np.mean(yearly_returns_list) * 100 
    median_yearly_return = np.median(yearly_returns_list) * 100
    std_yearly_return = np.std(yearly_returns_list) * 100 

    results = {
        'Mean Final Value': mean_final_value,
        'Median Final Value': median_final_value,
        'Std. Dev. Final Value': std_final_value,
        '68% CI Final Value': ci_68,
        '95% CI Final Value': ci_95,
        '99.7% CI Final Value': ci_997,
        'Mean Yearly Return (%)': mean_yearly_return,
        'Median Yearly Return (%)': median_yearly_return,
        'Std. Dev. Yearly Return (%)': std_yearly_return
    }

    if value_table:
        results['Final Values Table'] = final_values

    if return_timeseries:
        results['Time Series Data'] = timeseries_data

    return results