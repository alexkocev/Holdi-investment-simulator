import streamlit as st
import numpy as np
import plotly.graph_objs as go
import sqlite3
import pandas as pd


def get_asset_data():
    """
    Connect to DataBase with assets, return and allocation
    """
    conn = sqlite3.connect('data/investment_data.db')
    df = pd.read_sql_query("SELECT * FROM assets_return_allocation", conn)
    conn.close()
    return df
assets_data = get_asset_data()


def generate_asset_allocation(df, age, investor_profile='Profil Équilibré'):
    """
    Build a dictionary with assets and their allocation according to age and investor profile
    """
    # Define age category based on the given age
    if 20 <= age <= 24:
        age_col = '20 à 24 ans'
    elif 25 <= age <= 29:
        age_col = '25 à 29 ans'
    elif 30 <= age <= 34:
        age_col = '30 à 34 ans'
    elif 35 <= age <= 39:
        age_col = '35 à 39 ans'
    elif 40 <= age <= 44:
        age_col = '40 à 44 ans'
    elif 45 <= age <= 49:
        age_col = '45 à 49 ans'
    elif 50 <= age <= 54:
        age_col = '50 à 54 ans'
    elif 55 <= age <= 59:
        age_col = '55 à 59 ans'
    elif 60 <= age <= 64:
        age_col = '60 à 64 ans'
    else:
        age_col = '65 ans et +'

    df['Profil Equilibré'] = df[age_col]
    
    if investor_profile == 'Profil Prudent':
        df['Profil Prudent_'] = df['Profil Equilibré'] + df['Profil Prudent']
        asset_allocation = dict(zip(df['FONDS PROPOSÉS A TERME'], df['Profil Prudent_'].round(2)))

    elif investor_profile == 'Profil Dynamique':
        df['Profil Dynamique_'] = df['Profil Equilibré'] + df['Profil Dynamique']
        asset_allocation = dict(zip(df['FONDS PROPOSÉS A TERME'], df['Profil Dynamique_'].round(2)))

    else :
        asset_allocation = dict(zip(df['FONDS PROPOSÉS A TERME'], df['Profil Equilibré'].round(2)))

    return asset_allocation



def generate_asset_return(df):
    """
    Generate a dictionary with assets : returns
    """
    asset_return = df.set_index('FONDS PROPOSÉS A TERME')['Taux'].to_dict()
    return asset_return


def calculate_weighted_annual_return(asset_return, custom_asset_allocation):
    # Initialize the weighted return
    weighted_annual_return = 0
    # Calculate the weighted return
    for asset, allocation in custom_asset_allocation.items():
        if asset in asset_return:
            # Add the product of allocation and return to the weighted return
            weighted_annual_return += allocation * asset_return[asset]
        else:
            # Optionally handle assets not found in the return dictionary
            raise KeyError(f"Return data for {asset} not found")
    
    return weighted_annual_return



def simulate_investment(years, monthly_amount, weighted_annual_return, initial_amount, inflation_rate, withdrawal_rate, years_until_withdrawal):

    # Adjust for inflation
    effective_annual_return = (weighted_annual_return * 100)

    # List of [0,1,2,3,...] years
    timeline = np.arange(years + 1)

    # Initialize arrays
    initial_amount_array = np.zeros(years) # This array will remain constant with the initial amount
    invested_array = np.zeros(years)  # To store cumulative invested amounts
    earnings_array = np.zeros(years)  # To store earnings at the end of each year

    # Initialize total amount with the initial investment
    total_value = initial_amount
    


    # Convert annual return to monthly return
    monthly_return = (1 + (effective_annual_return/100)) ** (1/12) - 1

    # Loop over years
    for y in range(years):
        # Initialize total amount for withdraw
        last_year_withdraw_amount = 0

        ##############################
        #### initial_amount_array ####
        ##############################
        initial_amount_array[y] = initial_amount

        ##############################
        ####### invested_array #######
        ##############################
        if y == 0:
            # Only the montlhy amount are invested in the first year
            invested_array[y] = monthly_amount * 12
        else:
            # Add this year's investments to last year's total investments
            invested_array[y] = invested_array[y-1] + monthly_amount * 12 * (1 + (inflation_rate / 100))
     



        ##############################
        ####### earnings_array #######
        ##############################
        # Loop over months
        for m in range(12):
            # Apply monthly return to the total amount at the start of the month
            total_value *= 1 + monthly_return

            # Add the monthly investment at the end of the month
            total_value += monthly_amount * (1 + (inflation_rate / 100))

            # Remove withdraws at the end of the month
            if y >= years_until_withdrawal:
                total_value *= 1 - (withdrawal_rate / 100 / 12)
                last_year_withdraw_amount += total_value * withdrawal_rate / 100 / 12

        earnings_array[y] = total_value - (initial_amount_array[y] + invested_array[y])


    return timeline, initial_amount_array, invested_array, earnings_array, last_year_withdraw_amount










def page_simulator():
    st.header("Créer votre objectif d'investissement")



    ##############################
    ###### PROFILE #############
    ##############################
    with st.form("profile_form"):
        st.subheader("Votre profil")
        col1, col2 = st.columns(2)

        with col1:      
            input_salary = st.number_input(
                "Votre salaire mensuel NET", 
                min_value=0, 
                value=st.session_state.salary,
                help="Entrez le montant de votre salaire net mensuel.",
                key="salary_input" 
            )  
            input_age = st.number_input(
                "Votre âge", 
                min_value=0, 
                value=st.session_state.age,
                help="Entrez votre âge.",
                key="age_input" 
            )

        with col2:
            input_investment_perc = st.number_input(
                "Votre taux d'épargne (%)", 
                min_value=0, 
                value=st.session_state.investment_perc,
                help="Indiquez quel pourcentage de votre salaire vous épargnez.",
                key="investment_perc_input" 
            )      
            status = st.selectbox(
                "Quel est votre statut ?",
                ['Personne physique', 'Personne morale'],
                help="Sélectionnez 'Personne physique' si vous êtes un individu, ou 'Personne morale' si vous représentez une entreprise ou une entité juridique."
            )   

        # Custom CSS to adjust the button placement
        st.markdown("""
        <style>
        div.stButton > button {
            display: block;
            margin: 2vh auto 20px;  # Vertical spacing and center alignment
        }
        </style>""", unsafe_allow_html=True)

        submitted = st.form_submit_button("Enregistrer votre profil")
        if submitted:
            st.session_state.salary = input_salary
            st.session_state.age = input_age
            st.session_state.investment_perc = input_investment_perc
            
            st.session_state.initial_amount = int(st.session_state.salary * (st.session_state.investment_perc / 100))
            st.session_state.withdrawal_rate = 0
            st.session_state.inflation_rate = 2
            st.session_state.monthly_amount = int(st.session_state.salary * (st.session_state.investment_perc / 100))
            st.session_state.years_until_withdrawal = 5
            st.session_state.years = 60 - st.session_state.age
            
            st.success("Profil et paramètres mis à jour !")



    ##############################
    ###### PARAMETERS ############
    ##############################
    with st.form("parameter_form"):
        st.subheader("Vos paramètres")
        col1, col2 = st.columns(2)
        with col1:
            input_initial_amount = st.number_input(
                "Montant initial", 
                min_value=0, 
                value=st.session_state.initial_amount,
                #value= int(st.session_state.salary * (st.session_state.investment_perc / 100)),
                help="Indiquez le montant initial que vous investissez en une seule fois au début.",
                key="initial_amount_input" 
            )

            input_withdrawal_rate = st.number_input(
                "Taux de prélèvement (%)", 
                min_value=0, 
                value=st.session_state.withdrawal_rate,
                #value=0,
                help="Le pourcentage du portefeuille que vous prévoyez de retirer chaque année.",
                key="withdrawal_rate_input" 
            )
            input_inflation_rate = st.number_input(
                "Inflation (%)", 
                min_value=0, 
                value=st.session_state.inflation_rate,
                #value=2,
                help="Le taux d'inflation annuel estimé, qui représente l'augmentation prévue des salaires et par conséquent du montant que vous pouvez investir.",
                key="inflation_rate_input" 
            )

        with col2:
            input_monthly_amount = st.number_input(
                "Montant à placer par mois", 
                min_value=0, 
                value=st.session_state.monthly_amount,
                #value= int(st.session_state.salary * (st.session_state.investment_perc / 100)),
                help="Indiquez le montant que vous comptez investir chaque mois.",
                key="monthly_amount_input" 
            )
            input_years_until_withdrawal = st.number_input(
                "Années avant le début des prélèvements", 
                min_value=0,  # Assuming withdrawal could start immediately
                value=st.session_state.years_until_withdrawal,
                #value= 5,  # Default to 10 years, adjust as necessary
                help="Indiquez le nombre d'années après le début de l'investissement avant de commencer les prélèvements.",
                key="years_until_withdrawal_input" 
            )

        input_years = st.slider(
            "Nombre d'années de placement", 
            min_value=3, 
            max_value=50, 
            value=st.session_state.years,
            #value=60 - st.session_state.age,
            help="La durée totale pendant laquelle vous prévoyez de maintenir l'investissement.",
            key="years_input" 
        )

        submitted = st.form_submit_button("Enregistrer vos paramètres")
        if submitted:
            st.session_state.initial_amount = input_initial_amount
            st.session_state.withdrawal_rate = input_withdrawal_rate
            st.session_state.inflation_rate = input_inflation_rate
            st.session_state.years_until_withdrawal = input_years_until_withdrawal
            st.session_state.years = input_years
            st.success("Paramètres mis à jour !")



    # Align buttons horizontally for investment profile
    cols = st.columns(3)
    options = ["Profil Prudent", "Profil Équilibré", "Profil Dynamique"]
    if 'investor_profile' not in st.session_state:
        st.session_state.investor_profile = "Profil Équilibré"  # Default selection

    def update_selection(option):
        st.session_state.investor_profile = option
        
    for i, option in enumerate(options):
        with cols[i]:
            # Button with unique key and disabled state to show selection
            st.button(option, on_click=update_selection, args=(option,),
                    key=f'button{i+1}',
                    disabled=st.session_state.investor_profile == option)



    ##############################
    ###### PORTFOLIO #############
    ##############################
    with st.form("portfolio_form"):
        st.subheader("Répartition par actif")
        
        generated_asset_allocation = generate_asset_allocation(assets_data, st.session_state.age, st.session_state.investor_profile)         
        # Create columns for asset inputs
        col1, col2 = st.columns(2)
        columns = [col1, col2]

        # Create editable inputs for each asset, distributed across two columns
        custom_asset_allocation = {}
        for i, (asset, allocation) in enumerate(generated_asset_allocation.items()):
            with columns[i % 2]:  # Alternate placement between col1 and col2
                # Convert allocation to percentage and adjust input to handle percentages
                percentage_allocation = allocation * 100
                custom_asset_allocation[asset] = st.number_input(
                    f"{asset} (%)", value=percentage_allocation, format="%.2f", step=0.01
                ) / 100.0  # Convert back to fraction on submission

        # Custom CSS to adjust the button placement
        st.markdown("""
        <style>
        div.stButton > button {
            display: block;
            margin: 2vh auto 20px;  # Reduced vertical positioning
        }
        </style>""", unsafe_allow_html=True)

        submitted = st.form_submit_button("Enregistrer votre portefeuille")
        if submitted:
            st.session_state.custom_asset_allocation = custom_asset_allocation  # Save to session state
            st.success("Portefeuille mis à jour !")

    
    #################################
    #### Show the Annual Return #####
    #################################
    asset_return = generate_asset_return(assets_data)
    weighted_annual_return = calculate_weighted_annual_return(asset_return, custom_asset_allocation)

    # Using columns to align label and value horizontally
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.write('')
        # Using markdown to add styling for center alignment and bold, larger text within the column
        st.markdown(f"""
        <div style='text-align: center;'>
            <span style='font-size: 24px;'>Rendement annuel estimé</span> 
            <span style='font-size: 28px; font-weight: bold;'>{weighted_annual_return:.2%}</span>
        </div>
        """, unsafe_allow_html=True)


    st.title("")
    timeline, initial_amount_array, invested_array, earnings_array, last_year_withdraw_amount = simulate_investment(st.session_state.years, st.session_state.monthly_amount, weighted_annual_return, st.session_state.initial_amount, st.session_state.inflation_rate, st.session_state.withdrawal_rate, st.session_state.years_until_withdrawal)
    
    fig = go.Figure()

    # Custom function to format numbers with space as thousand separator
    def format_number(num):
        return "{:,.0f}".format(num).replace(',', ' ')
    # Adding trace to the figure
    fig.add_trace(go.Scatter(x=timeline, y=initial_amount_array, fill='tonexty',
                            mode='lines', name='Montant Initial',
                            hovertemplate='%{text}',
                            text=[format_number(y) for y in (initial_amount_array)]))  # Using formatted hover texts
    fig.add_trace(go.Scatter(x=timeline, y=initial_amount_array + invested_array, fill='tonexty',
                            mode='lines', name='Montant Investi',
                            hovertemplate='%{text}',
                            text=[format_number(y) for y in (initial_amount_array + invested_array)]))  # Using formatted hover texts
    fig.add_trace(go.Scatter(x=timeline, y=initial_amount_array + invested_array + earnings_array, fill='tonexty',
                            mode='lines', name='Gains - Prélèvements',
                            hovertemplate='%{text}',
                            text=[format_number(y) for y in (initial_amount_array + invested_array + earnings_array)]))  # Using formatted hover texts


    fig.update_layout(
        title='Projection d\'Investissement selon le Profil',
        xaxis_title='Années',
        yaxis_title='Valeur du Portefeuille',
        template="plotly_white",
        legend=dict(
                    orientation="h",  # Horizontal layout for the legend
                    xanchor="center",  # Anchor the legend's x-axis to center
                    yanchor="bottom",  # Anchor the legend's y-axis to bottom
                    x=0.5,  # Center the legend horizontally
                    y=-0.3,  # Position the legend below the x-axis
                    traceorder="normal",
                    font=dict(
                        family="sans-serif",
                        size=12,
                        color="white"
                    )
                )
    )
    st.plotly_chart(fig, use_container_width=True)

    # Calculate the values
    future_value = st.session_state.initial_amount + invested_array[-1] + earnings_array[-1]  # Total value at the end of the simulation
    capital_gain = earnings_array[-1]  # Total earnings
    invested_and_initial_value = st.session_state.initial_amount + invested_array[-1]  # If there's no taxes or fees separate from withdrawals
    monthly_income = last_year_withdraw_amount / 12  # If monthly income is defined as average annual withdrawal


    # Create columns to display this information
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<h2 style='text-align: center; font-size: medium;'>Valeur future</h2><p style='text-align: center; font-size: medium;'>{future_value:,.0f} €</p>".replace(',', ' '), unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h2 style='text-align: center; font-size: medium;'>Dont plus-value</h2><p style='text-align: center; font-size: medium;'>{capital_gain:,.0f} €</p>".replace(',', ' '), unsafe_allow_html=True)
    with col3:
        st.markdown(f"<h2 style='text-align: center; font-size: medium;'>Montant investi</h2><p style='text-align: center; font-size: medium;'>{invested_and_initial_value:,.0f} €</p>".replace(',', ' '), unsafe_allow_html=True)
    with col4:
        st.markdown(f"<h2 style='text-align: center; font-size: medium;'>Revenu mensuel</h2><p style='text-align: center; font-size: medium;'>{monthly_income:,.0f} €</p>".replace(',', ' '), unsafe_allow_html=True)

    st.title("")









def page_portfolio():
    st.header("Votre portfeuille")

    if 'custom_asset_allocation' in st.session_state:
        st.subheader("Répartition actuelle de votre portefeuille")
        # Create a dataframe from the session state data for nicer display
        allocations = pd.DataFrame(list(st.session_state.custom_asset_allocation.items()), columns=['Actif', 'Allocation'])
        allocations['Allocation'] = (allocations['Allocation'] * 100).round(2).astype(str) + '%'  # Convert to percentage string for display
        # Use st.write with HTML to remove index
        st.write(allocations.to_html(index=False), unsafe_allow_html=True)
    else:
        st.write("Aucune information de portefeuille disponible. Veuillez configurer votre portefeuille sur la page 'Objectif d'investissement'.")



def page_admin():
    st.header("Admin")
    st.write(assets_data)



def main():
    # Initialize session state variables
    if 'salary' not in st.session_state:
        st.session_state.salary = 2500
    if 'age' not in st.session_state:
        st.session_state.age = 30
    if 'investment_perc' not in st.session_state:
        st.session_state.investment_perc = 17

    if 'initial_amount' not in st.session_state:
        st.session_state.initial_amount = int(st.session_state.salary * (st.session_state.investment_perc / 100))
    if 'withdrawal_rate' not in st.session_state:
        st.session_state.withdrawal_rate = 0
    if 'inflation_rate' not in st.session_state:
        st.session_state.inflation_rate = 2
    if 'monthly_amount' not in st.session_state:
        st.session_state.monthly_amount = int(st.session_state.salary * (st.session_state.investment_perc / 100))
    if 'years_until_withdrawal' not in st.session_state:
        st.session_state.years_until_withdrawal = 5
    if 'years' not in st.session_state:
        st.session_state.years = 60 - st.session_state.age

    # Set page title and favicon
    st.set_page_config(
        page_title='HOLDi', 
        page_icon='✨', 
        #layout='wide'
        )
    
    st.header('HOLDi', divider='rainbow')

    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # Footer with enhanced CSS for full coverage, including sidebar
    footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        height: 50px; /* Set the height of the footer */
        background-color: grey;
        color: white;
        text-align: center;
        line-height: 50px; /* Use the same as height for vertical alignment */
        z-index: 9999; /* Ensures it stays on top */
    }

    /* Ensure the sidebar doesn't overlap the footer */
    div[data-testid="stSidebar"] {
        z-index: 1; /* Ensure sidebar is below the footer */
        bottom: 50px; /* Raise the bottom of the sidebar to make room for the footer */
    }

    /* Additional CSS to ensure content doesn't get hidden under the footer */
    div.block-container {
        padding-bottom: 60px; /* Add padding to make sure content doesn't get hidden under the footer */
    }
    </style>
    <div class="footer">
        <p>Made by HOLDi - 2024</p>
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)


    choice = st.sidebar.radio("", ["📊 Objectif d'investissement", "💰 Portefeuille", "🔧 Admin"])
    if choice == "📊 Objectif d'investissement":
        page_simulator()
    elif choice == "💰 Portefeuille":
        page_portfolio()
    elif choice == "🔧 Admin":
        page_admin()




if __name__ == "__main__":
    main()



