#!/bin/bash

# Start the Jupyter Notebook in the background
jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root &

# Start the Streamlit app in the foreground
streamlit run ./src/app.py