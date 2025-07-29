
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

st.title("Monte Carlo Portfolio Simulation with Live Animation")
st.write("""
This app simulates possible portfolio growth paths using Monte Carlo methods.
Adjust the parameters below and click **Run Simulation** to see results.
""")

# Sidebar parameters
initial_stocks = st.sidebar.number_input("Initial Stocks ($)", 10000, 1000000, 250000, step=5000)
initial_bonds = st.sidebar.number_input("Initial Bonds ($)", 10000, 1000000, 125000, step=5000)
initial_cash = st.sidebar.number_input("Initial Cash ($)", 10000, 1000000, 125000, step=5000)
years = st.sidebar.slider("Years", 1, 50, 10)
simulations = st.sidebar.slider("Number of Simulations", 10, 1000, 100, step=10)
stock_mean = st.sidebar.slider("Stock Mean Return (%)", -10.0, 20.0, 8.0, step=0.1) / 100
stock_std = st.sidebar.slider("Stock Std Dev (%)", 0.0, 50.0, 20.0, step=0.1) / 100
bonds_min = st.sidebar.slider("Bonds Min Return (%)", -10.0, 10.0, -3.0, step=0.1) / 100
bonds_mode = st.sidebar.slider("Bonds Most Likely Return (%)", -5.0, 15.0, 5.0, step=0.1) / 100
bonds_max = st.sidebar.slider("Bonds Max Return (%)", 0.0, 20.0, 12.0, step=0.1) / 100
cash_min = st.sidebar.slider("Cash Min Return (%)", 0.0, 5.0, 1.0, step=0.1) / 100
cash_max = st.sidebar.slider("Cash Max Return (%)", 0.0, 10.0, 3.0, step=0.1) / 100

run_simulation = st.button("Run Simulation")

if run_simulation:
    final_balances = []
    yearly_balances = []
    total_initial = initial_stocks + initial_bonds + initial_cash

    # Placeholder for live chart
    chart_placeholder = st.empty()
    
    for sim in range(simulations):
        stocks = initial_stocks
        bonds = initial_bonds
        cash = initial_cash
        path = [stocks + bonds + cash]
        for _ in range(years):
            stocks *= (1 + np.random.normal(stock_mean, stock_std))
            bonds *= (1 + np.random.triangular(bonds_min, bonds_mode, bonds_max))
            cash *= (1 + np.random.uniform(cash_min, cash_max))
            path.append(stocks + bonds + cash)
        final_balances.append(path[-1])
        yearly_balances.append(path)
        
        # Live line plot update
        fig_live, ax_live = plt.subplots(figsize=(6,4))
        for p in yearly_balances[-10:]:
            ax_live.plot(range(years+1), p, alpha=0.5)
        ax_live.set_title(f"Live Simulation Progress: {sim+1}/{simulations} Trials")
        ax_live.set_xlabel("Years")
        ax_live.set_ylabel("Portfolio Balance")
        chart_placeholder.pyplot(fig_live)
        time.sleep(0.05)

    final_balances = np.array(final_balances)
    yearly_balances = np.array(yearly_balances)

    # Histogram
    fig2, ax2 = plt.subplots(figsize=(8,5))
    ax2.hist(final_balances, bins=30, edgecolor='black')
    ax2.set_title("Distribution of Final Balances")
    ax2.set_xlabel("Final Balance")
    ax2.set_ylabel("Frequency")
    st.pyplot(fig2)

    # Summary Stats
    mean_balance = np.mean(final_balances)
    std_balance = np.std(final_balances)
    min_balance = np.min(final_balances)
    max_balance = np.max(final_balances)
    avg_annual_return = (mean_balance / total_initial)**(1/years) - 1
    coef_variation = std_balance / mean_balance

    st.subheader("Simulation Summary")
    st.write(f"**Mean Final Balance:** ${mean_balance:,.2f}")
    st.write(f"**Standard Deviation:** ${std_balance:,.2f}")
    st.write(f"**Minimum Balance:** ${min_balance:,.2f}")
    st.write(f"**Maximum Balance:** ${max_balance:,.2f}")
    st.write(f"**Average Annual Return:** {avg_annual_return*100:.2f}%")
    st.write(f"**Coefficient of Variation:** {coef_variation:.2f}")

    st.subheader("Probability of Exceeding Thresholds")
    thresholds = np.arange(500000, 4000000, 250000)
    prob_data = {"Threshold": thresholds, "Probability (%)": [(final_balances >= t).mean()*100 for t in thresholds]}
    st.dataframe(prob_data)
