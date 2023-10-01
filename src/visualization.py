import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.graph_objects as go

def draw_correlation_matrix(indices_data):
  monthly_percentage_change = indices_data.pct_change()
  correlation_matrix = monthly_percentage_change.corr()
  mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))

  plt.figure(figsize=(10, 8))
  sns.heatmap(correlation_matrix, annot=True, cmap='crest',
              square=True, linewidths=.5, cbar_kws={"shrink": .75}, mask=mask)
  plt.title('Correlation Matrix of Indices')
  plt.show()

def draw_time_series(indices_data):
  categories = {
        'All-World': ['ACWI IMI', 'ACWI', '70/30'],
        'Regions': ['World', 'Emerging Markets', 'North America', 'Europe'],
        'Sectors': ['S&P 500', 'NASDAQ', 'Dow Jones']
    }

  fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(20, 6))
  color_palette = sns.color_palette("pastel")

  for ax, (category, indices) in zip(axes, categories.items()):
    # Use a subset of the color palette for each category
    colors = color_palette[:len(indices)]

    # Plot all indices in the current category at once
    indices_data[indices].plot(ax=ax, color=colors)

    # Set the y-axis to log scale
    ax.set_yscale("log")

    # Set title for the subplot
    ax.set_title(category)
    ax.set_ylabel("Index Value (Log Scale)")
    ax.legend()

  # Adjust layout
  plt.tight_layout()
  plt.show()

def draw_bootstrap_distribution(bootstrap_results):
  sns.kdeplot(bootstrap_results['Final Values Table'], fill=True)
  plt.axvline(bootstrap_results['Mean Final Value'], color='r', linestyle='--', label='Mean')
  plt.axvline(bootstrap_results['Median Final Value'], color='g', linestyle='--', label='Median')

  plt.axvline(bootstrap_results['68% CI Final Value'][0], color='b', linestyle='--', label='68% CI')
  plt.axvline(bootstrap_results['68% CI Final Value'][1], color='b', linestyle='--')
  plt.axvline(bootstrap_results['95% CI Final Value'][0], color='y', linestyle='--', label='95% CI')
  plt.axvline(bootstrap_results['95% CI Final Value'][1], color='y', linestyle='--')

  plt.legend()
  plt.title('Bootstrap Distribution of Final Values')
  plt.show()


def draw_bootstrap_timeseries(bootstrap_results, start_year):
    # Extract the time series data
    timeseries_data = np.array(bootstrap_results['Time Series Data'])

    # Calculate statistics for each month
    mean_values = timeseries_data.mean(axis=0)
    ci_68_lower = np.percentile(timeseries_data, 16, axis=0)
    ci_68_upper = np.percentile(timeseries_data, 84, axis=0)
    ci_95_lower = np.percentile(timeseries_data, 2.5, axis=0)
    ci_95_upper = np.percentile(timeseries_data, 97.5, axis=0)
    ci_997_lower = np.percentile(timeseries_data, 0.15, axis=0)
    ci_997_upper = np.percentile(timeseries_data, 99.85, axis=0)

    # Plotting
    plt.figure(figsize=(14, 8))

    # Plot mean line
    plt.plot(mean_values, label='Mean Value', color='blue')

    # Shade the confidence intervals
    plt.fill_between(range(len(mean_values)), ci_68_lower, ci_68_upper, color='blue', alpha=0.3, label='68% CI')
    plt.fill_between(range(len(mean_values)), ci_95_lower, ci_95_upper, color='blue', alpha=0.2, label='95% CI')

    # Plot the 99.7% CI with dashed lines
    plt.plot(ci_997_lower, ':', color='blue', alpha=0.5, label='99.7% CI')
    plt.plot(ci_997_upper, ':', color='blue', alpha=0.5)

    # Adjust x-axis to show years
    total_years = len(mean_values) // 12
    plt.xticks(np.arange(0, len(mean_values), 12), labels=[str(start_year + i) for i in range(total_years + 1)])

    plt.title('Bootstrap Time Series Analysis')
    plt.xlabel('Years')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def draw_interactive_timeseries(bootstrap_results, start_year=2023, extreme_bounds=False):
    """
    Plots the time series of bootstrapped results using Plotly.

    Parameters:
    - bootstrap_results: Dictionary containing the results from the block_bootstrap function.
    - start_year: The starting year for the x-axis.
    - extreme_bounds: Boolean indicating whether to show the extreme bounds.
    """
    timeseries = bootstrap_results['Time Series Data']
    num_months = len(timeseries[0])
    years = [start_year + i/12 for i in range(num_months)]

    # Calculate y-values
    mean_values = np.mean(timeseries, axis=0)
    p84 = np.percentile(timeseries, 84, axis=0)
    p16 = np.percentile(timeseries, 16, axis=0)
    p975 = np.percentile(timeseries, 97.5, axis=0)
    p25 = np.percentile(timeseries, 2.5, axis=0)
    p9985 = np.percentile(timeseries, 99.85, axis=0)
    p0015 = np.percentile(timeseries, 0.15, axis=0)

    fig = go.Figure()

    # Extreme bounds 230, 57, 70, 0.1
    if extreme_bounds:
        fig.add_trace(go.Scatter(x=years, y=p9985, fill=None, mode='lines', line_color='rgba(255, 195, 0, 0.3)', name='99.7% CI', legendgroup='99.7% CI', hoverinfo='y'))
        fig.add_trace(go.Scatter(x=years, y=p0015, fill='tonexty', fillcolor='rgba(255, 195, 0, 0.3)', mode='lines', line_color='rgba(255, 195, 0, 0.3)', showlegend=False, legendgroup='99.7% CI', hoverinfo='y'))

    # 95% CI
    fig.add_trace(go.Scatter(x=years, y=p975, fill=None, mode='lines', line_color='rgba(0, 187, 249, 0.5)', name='95% CI', legendgroup='95% CI', hoverinfo='y'))
    fig.add_trace(go.Scatter(x=years, y=p25, fill='tonexty', fillcolor='rgba(0, 187, 249, 0.5)', mode='lines', line_color='rgba(0, 187, 249, 0.5)', showlegend=False, legendgroup='95% CI', hoverinfo='y'))

    # 68% CI
    fig.add_trace(go.Scatter(x=years, y=p84, fill=None, mode='lines', line_color='rgba(42, 157, 143, 0.7)', name='68% CI', legendgroup='68% CI', hoverinfo='y'))
    fig.add_trace(go.Scatter(x=years, y=p16, fill='tonexty', fillcolor='rgba(42, 157, 143, 0.7)', mode='lines', line_color='rgba(42, 157, 106, 0.7)', showlegend=False, legendgroup='68% CI', hoverinfo='y'))

    # Mean
    fig.add_trace(go.Scatter(x=years, y=mean_values, mode='lines', name='Mean', line=dict(dash='dot', color='black', width=2.5), hoverinfo='y'))

    

    fig.update_layout(title='Bootstrapped Investment Over Time', xaxis_title='Year', yaxis_title='Value')
    
    return fig
