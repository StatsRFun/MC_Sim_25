
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import pandas as pd

st.title("Monte Carlo Portfolio Simulation - Enhanced Version")
st.write("""
This app simulates possible portfolio growth paths using Monte Carlo methods.
Features:
- Real-time trial counter and balance display in separate boxes.
- Chart displayed first with a thick black mean line and ±1.5 SD wedge.
- Deep green lines for other paths outside the ±1.5 SD range.
- Fast Mode toggle for bulk calculation or Animated Mode for trial-by-trial visualization.
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
fast_mode = st.sidebar.checkbox("Fast Mode (No animation)", value=False)

run_simulation = st.button("Run Simulation")

if run_simulation:
    final_balances = []
    yearly_balances = []
    total_initial = initial_stocks + initial_bonds + initial_cash

    chart_placeholder = st.empty()
    col1, col2 = st.columns(2)
    trial_box = col1.empty()
    balance_box = col2.empty()

    if fast_mode:
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
        all_paths = np.array(yearly_balances)
        mean_vals = all_paths.mean(axis=0)
        sd_vals = all_paths.std(axis=0)
        fig, ax = plt.subplots(figsize=(7,4))
        ax.plot(range(years+1), mean_vals, color='black', linewidth=5, label='Mean')
        ax.fill_between(range(years+1), mean_vals-1.5*sd_vals, mean_vals+1.5*sd_vals, color='black', alpha=0.2, label='±1.5 SD')
        for p in all_paths:
            if any((p > mean_vals+1.5*sd_vals) | (p < mean_vals-1.5*sd_vals)):
                ax.plot(range(years+1), p, color='green', alpha=0.2)
        ax.set_title('Portfolio Growth with ±1.5 SD Wedge')
        ax.set_xlabel('Years')
        ax.set_ylabel('Balance')
        ax.legend()
        chart_placeholder.pyplot(fig)
        trial_box.metric("Trials Completed", simulations)
        balance_box.metric("Last Balance", f"${final_balances[-1]:,.2f}")

    else:
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
            trial_box.metric("Current Trial", sim+1)
            balance_box.metric("Final Balance", f"${path[-1]:,.2f}")
            all_paths = np.array(yearly_balances)
            mean_vals = all_paths.mean(axis=0)
            sd_vals = all_paths.std(axis=0)
            fig, ax = plt.subplots(figsize=(7,4))
            ax.plot(range(years+1), mean_vals, color='darkgrey', linewidth=12, label='Mean')
            ax.fill_between(range(years+1), mean_vals-1.5*sd_vals, mean_vals+1.5*sd_vals, color='black', alpha=0.2, label='±2 SD')
            for p in all_paths:
                if any((p > mean_vals+1.5*sd_vals) | (p < mean_vals-1.5*sd_vals)):
                    ax.plot(range(years+1), p, color='green', alpha=0.2)
            ax.set_title(f'Real-time Portfolio Growth (Trial {sim+1})')
            ax.set_xlabel('Years')
            ax.set_ylabel('Balance')
            ax.legend()
            chart_placeholder.pyplot(fig)
            time.sleep(0.05)

    final_balances = np.array(final_balances)
    fig2, ax2 = plt.subplots(figsize=(8,5))
    ax2.hist(final_balances, bins=30, edgecolor='black')
    ax2.set_title("Distribution of Final Balances")
    ax2.set_xlabel("Final Balance")
    ax2.set_ylabel("Frequency")
    st.pyplot(fig2)

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
