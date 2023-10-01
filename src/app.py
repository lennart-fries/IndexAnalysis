import streamlit as st
import pandas as pd
from bootstrap import block_bootstrap
from visualization import draw_interactive_timeseries

def fill_array(recurring_investment, interval_selection, investment_period, dynamic_plan):
        # Calculate the number of investments per year based on the interval
        investments_per_year = {'Monthly': 12, 'Quarterly': 4, 'Yearly': 1}
        investments_per_year = investments_per_year[interval_selection]

        # Initialize the investment array with the initial investment
        investment_array = []

        # Fill the investment array based on the investment period and interval
        for year in range(investment_period):
            # Apply the dynamic plan to the recurring investment once at the start of each year
            if year > 0:
                recurring_investment += recurring_investment * dynamic_plan
            for _ in range(investments_per_year):
                # Append the adjusted recurring investment to the investment array for each interval in the year
                investment_array.append(recurring_investment)

        return investment_array

def generate_array(input_list):
    # Initialize an empty list to store the values
    values_list = []
    
    # Iterate over each pair in the input_list
    for inputs in input_list:
        # Extract the years and amount from the pair
        years = inputs['years']
        amount = inputs['amount']
        
        # Append the amount to the values_list 12 * years times
        values_list.extend([amount] * (12 * years))
    
    # Return the generated values_list
    return values_list

def are_conditions_met(input_list):
    # Check if the input_list has more than one value pair
    if len(input_list) <= 1:
        return False
    
    # Iterate over each pair in the input_list
    for inputs in input_list:
        # Check the conditions for each pair
        if inputs['years'] < 1 or inputs['amount'] < 50:
            return False  # Return False if any pair does not meet the conditions
    
    # Return True if all pairs meet the conditions
    return True

# Initialize the session state variables if they don't exist
if 'input_list' not in st.session_state:
    st.session_state.input_list = [{'years': 1, 'amount': 1}]

if 'expander_open' not in st.session_state:
    st.session_state.expander_open = True

pct_returns = pd.read_csv('../data/Processed-Returns.csv')

st.set_page_config(
    page_title="Portfolio Forecast",
    page_icon="../tori.png",
)

def main():
    col1, col2 = st.columns([1, 9]) 

    # In the first column, display the title
    with col1:
        st.image('../tori.png', width=72)

    # In the second column, display the image
    with col2:
        color_hex = "#9CF8E8"  # Replace with your desired color
        st.markdown(f'<h1 style="color: {color_hex};">Portfolio Forecasting</h1>', unsafe_allow_html=True)        
    
    start_year = st.number_input('Year', value=2023, format='%d')
    
    index_options = {'MSCI World': 'World', 'MSCI ACWI': 'ACWI', '70/30-Strategie': '70/30', 'S&P 500': 'S&P 500'}
    index_selection = st.selectbox('Index', options=list(index_options.keys()))
    index = index_options[index_selection]
    # Number Input for Initial Investment
    initial_investment = st.number_input('Initial Investment', min_value=0, step=100, format='%d')
    
    # Slider with Input Field for Recurring Investment
    recurring_investment = st.slider('Recurring Investment', min_value=100, max_value=5000, value=100, step=50)
    
    # Dropdown for Interval Selection
    interval_options = {'Monthly': 'M', 'Quarterly': 'Q', 'Yearly': 'Y'}
    interval_selection = st.selectbox('Investment Interval', options=list(interval_options.keys()))
    interval = interval_options[interval_selection]
    
    # Slider for Investment Period
    investment_period = st.slider('Investment Duration in Years', min_value=5, max_value=50, value=10, step=1)   
    
    # Advanced Button with Hidden Tab for Advanced Utilities
    with st.expander('Advanced'):
        # Dynamic Input Field for % of Increase
        dynamic_plan = st.slider('Dynamization of Savings Rate in %', min_value=0.0, value=0.0, max_value=10.0, step=0.5) / 100
        # Slider for Growth Time
        investment_horizon = st.slider('Investment Horizon in Years', min_value=investment_period, max_value=100, value=investment_period, step=1)
        # Toggle Switch for Continue Investing
        continue_investing = st.slider('Continued Investment after Investment Duration in %', min_value=0, max_value=100, step=5, value=0) / 100
    
    with st.expander('Custom Investment Value'):
        st.warning('This is for a custom recurring investment value. Needs to be in a decimal format!')
        strategy_amount = st.number_input('Custom Amount', value=0, min_value=0, format='%d')
    
    with st.expander('Complex Strategy', expanded=st.session_state.expander_open):
        st.warning('This is for complex strategy involving multiple year intervals of greatly differing investment values that can not be properly displayed through dynamization... Beware that dynamization will not be applied for this strategy variant!')
        st.error('Currently this only works with monthly investment intervals, meaning one year stands for 12 individual investments, sorry for the inconvenience for everybody who prefers differing periodization.')
        st.info('For input you are required to specifiy the amount of years your investment will run, by using Add new line and inputing a value then pressing ENTER you open the new line. '+ 
                'Using the new line you can input another interval of investment. To be calculated you need to have at least two intervals of 1 or more years and 50 or more EUR of recurring investments.')
        

        for idx, inputs in enumerate(st.session_state.input_list):
            col1, col2, _ = st.columns([1, 1, 0.1])  # Create columns for each input field
            with col1:
                inputs['years'] = st.number_input(f'Years {idx+1}', min_value=1, max_value=10, value=inputs['years'], key=f'years_{idx}')
            with col2:
                inputs['amount'] = st.number_input(f'Amount {idx+1}', min_value=1, max_value=100000, value=inputs['amount'], key=f'amount_{idx}')

        # Create a button to add a new line of input fields
        if st.button('Add new line'):
            st.session_state.input_list.append({'years': 1, 'amount': 1})  # Append default values to the input list

    extreme = st.checkbox('Show outer extremes (99,97% of values)', value=False)

    if st.button('Conduct Bootstrap and Visualize Results'):
        st.success('Calculating... This can take a few seconds.')
        if strategy_amount >= 1:
            investment_array = fill_array(strategy_amount, interval_selection, investment_period, dynamic_plan)
        elif are_conditions_met(st.session_state.input_list):
            investment_array = generate_array(st.session_state.input_list)
            interval = 'M'
        else:
            investment_array = fill_array(recurring_investment, interval_selection, investment_period, dynamic_plan)
        
        bootstrap_results = block_bootstrap(returns=pct_returns[index].dropna().values, initial_investment=initial_investment, investments=investment_array, investment_interval=interval, n_years=investment_horizon, continue_investing=continue_investing, value_table=True, return_timeseries=True)
        st.plotly_chart(draw_interactive_timeseries(bootstrap_results, start_year, extreme))
        

if __name__ == '__main__':
    main()