# Holdi Board

Welcome to the **Holdi Board** repository! This application is a simulator built using Python and Streamlit, designed to simulate investment performance based on your individual profile and asset allocation. It provides a straightforward interface to interact with investment scenarios to help optimize your financial planning.

## Features

-   **Performance Simulation**: Simulate the potential performance of your investments based on various profiles and asset allocations (`app.py`) 
-   **Data Analysis**: Includes a Jupyter Notebook (`data_handling.ipynb`) to convert input from Excel Sheet to SQLite database 
-   **Local Database**: Utilize a SQLite database (`data/investment_data.db`) to store and manage simulation data.


## Installation

Follow these simple steps to get a local copy up and running:

1.  **Clone the repository**:  
    Open a terminal and enter the following command:
    
    `git clone https://github.com/alexkocev/holdi_board.git` 
    
    This command copies the project to your local machine.
    
2.  **Install Dependencies**:  
    Navigate into the project directory (`cd holdi_board`) and run:
    
    `pip install -r requirements.txt` 
    
    This installs the required Python packages specified in `requirements.txt`.
    

## Usage

To run the application:

1.  Activate the environment where Streamlit is installed. If it’s the global Python environment, you can skip this step.
    
2.  Launch the application by running:
    
    `streamlit run app.py` 
    
    This command starts the Streamlit server.
    
3.  Access the application by opening [http://localhost:8501](http://localhost:8501/) in your web browser.
    

By following these steps, you can quickly set up and start using the Holdi Board application locally.



## Deployment

The application is also hosted on Render and can be accessed through the following URL: [Holdi Board on Render](https://holdi-board.onrender.com/)
