import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import time
import pandas as pd
from utils import generate_network, initialize_states, sir_step, get_node_colors

# Set page to wide mode for better layout
st.set_page_config(layout="wide")

# Remove Streamlit header completely and reduce all top spacing
st.markdown("""
    <style>
        #MainMenu {display: none !important;}
        header {display: none !important;}
        .stDeployButton {display: none !important;}
        .stApp > header {display: none !important;}
        .stApp > footer {display: none !important;}
        .block-container {padding-top: 0rem !important;}
        .main .block-container {padding-top: 0rem !important;}
        .css-18e3th9 {padding-top: 0rem !important;}
        .css-1d391kg {padding-top: 0rem !important;}
        .css-1v0mbdj {padding-top: 0rem !important;}
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.G = None
    st.session_state.states = None
    st.session_state.stats = None
    st.session_state.auto_sim = False
    st.session_state.next_step = False
    st.session_state.pos = None
    st.session_state.fig = None
    st.session_state.total_infected = 1  # Initial infected count
    st.session_state.new_infections = 0  # New infections today
    st.session_state.daily_stats = []  # Daily statistics history
    st.session_state.view_as_percentage = False  # Flag to toggle percentage view

# Sidebar controls - Moved to top
with st.sidebar:
    st.header("Simulation Parameters")
    n = st.slider("Population Size", 100, 2000, 500)
    k = st.slider("Avg. Degree (k)", 2, 20, 6)
    p = st.slider("Randomness (p)", 0.0, 1.0, 0.1)
    R0 = st.slider("R₀ (Reproduction Number)", 0.5, 5.0, 2.5)
    recovery_prob = st.slider("Recovery Probability", 0.01, 1.0, 0.1)
    quarantine_pct = st.slider("Quarantine %", 0.0, 1.0, 0.0)
    distancing_strength = st.slider("Social Distancing", 0.0, 1.0, 0.0)
    step_delay = st.slider("Step Delay (seconds)", 0.0, 2.0, 0.1)
    show_edges = st.checkbox("Show Network Edges", value=False)

# Page title
st.title("Virus Spread Simulation (SIR Model)")

st.subheader("Simulation Controls")
control_cols = st.columns(4)  # Divide into 4 equal columns

# Place controls in horizontal arrangement
with control_cols[0]:
    next_step_button = st.button("Next Step", use_container_width=True)

with control_cols[1]:
    reset_button = st.button("Reset", use_container_width=True)

with control_cols[2]:
    auto_sim_button = st.button("Start Auto Simulation", use_container_width=True)

with control_cols[3]:
    pause_button = st.button("Pause Simulation", use_container_width=True)

# Create main display area with two columns for graphs
col1, col2 = st.columns([1.4, 1])

# Left column for network visualization
with col1:
    graph_placeholder = st.empty()

# Right column for statistics
with col2:
    st.subheader("Statistics")
    days_placeholder = st.empty()
    chart_placeholder = st.empty()

# History section at bottom spanning full width
st.subheader("Simulation History")
percentage_toggle = st.checkbox("View as percentages", value=st.session_state.view_as_percentage)
st.session_state.view_as_percentage = percentage_toggle
history_container = st.empty()

# Initialize network if not exists
if st.session_state.G is None:
    st.session_state.G = generate_network(n, k, p)
    st.session_state.states = initialize_states(st.session_state.G)
    st.session_state.stats = {"step": [0], "infected": [1], "recovered": [0], "susceptible": [n-1]}
    st.session_state.pos = nx.spring_layout(st.session_state.G, seed=42)
    st.session_state.total_infected = 1
    st.session_state.new_infections = 0
    st.session_state.daily_stats = [{"Day": 0, "Susceptible": n-1, "Infected": 1, "Recovered": 0, "Quarantined": 0, "New Infections": 0, "Total Infected": 1}]

def update_stats(states, stats):
    infected = sum(1 for s in states.values() if s == 'I')
    recovered = sum(1 for s in states.values() if s == 'R')
    susceptible = sum(1 for s in states.values() if s == 'S')
    quarantined = sum(1 for s in states.values() if s == 'Q')
    
    # Calculate new infections (only count increases)
    prev_infected = stats["infected"][-1] if stats["infected"] else 0
    prev_recovered = stats["recovered"][-1] if stats["recovered"] else 0
    current_total = infected + recovered
    prev_total = prev_infected + prev_recovered
    new_infections = max(0, current_total - prev_total)
    
    # Update total infected count
    st.session_state.total_infected += new_infections
    st.session_state.new_infections = new_infections
    
    # Update stats
    stats["step"].append(stats["step"][-1] + 1)
    stats["infected"].append(infected)
    stats["recovered"].append(recovered)
    stats["susceptible"].append(susceptible)
    
    # Add to daily stats history
    day = stats["step"][-1]
    st.session_state.daily_stats.append({
        "Day": day,
        "Susceptible": susceptible,
        "Infected": infected,
        "Recovered": recovered,
        "Quarantined": quarantined,
        "New Infections": new_infections,
        "Total Infected": st.session_state.total_infected
    })

@st.cache_data
def create_network_visualization(states, pos):
    fig, ax = plt.subplots(figsize=(8, 6))
    nx.draw(
        st.session_state.G, pos,
        node_color=get_node_colors(states),
        node_size=20,
        ax=ax,
        with_labels=False,
        edge_color='none'
    )
    return fig

def update_visualization():
    # Update visualization in the same placeholder
    pos = nx.spring_layout(st.session_state.G, seed=42)
    fig, ax = plt.subplots(figsize=(8, 6))
    nx.draw(
        st.session_state.G, pos,
        node_color=get_node_colors(st.session_state.states),
        node_size=20, 
        ax=ax, 
        with_labels=False,
        edge_color='gray' if show_edges else 'none'  # Hide edges if show_edges is False
    )
    graph_placeholder.pyplot(fig)
    plt.close(fig)  # Close the figure to prevent memory leaks
    
    # Update stats in the same placeholders
    days_placeholder.info(f" Days passed: {st.session_state.stats['step'][-1]} |  New infections: {st.session_state.new_infections}  |  Total infected: {st.session_state.total_infected}")
    chart_placeholder.line_chart({
        "Infected": st.session_state.stats["infected"],
        "Recovered": st.session_state.stats["recovered"],
        "Susceptible": st.session_state.stats["susceptible"]
    }, color=["#ff0000", "#0000ff", "#00ff00"])  # Red, Blue, Green
    
    # Create dataframe from daily stats for history table
    df = pd.DataFrame(st.session_state.daily_stats)
    
    # Calculate population size
    population_size = n
    
    # Convert to percentages if selected
    if st.session_state.view_as_percentage:
        for col in ["Susceptible", "Infected", "Recovered", "Quarantined"]:
            df[col] = (df[col] / population_size * 100).round(2).astype(str) + '%'
        df["Total Infected"] = (df["Total Infected"] / population_size * 100).round(2).astype(str) + '%'
        df["New Infections"] = (df["New Infections"] / population_size * 100).round(2).astype(str) + '%'
    
    # Display the data with full width
    history_container.dataframe(df, use_container_width=True, height=300)

# Handle button clicks after all placeholders are defined
if next_step_button:
    st.session_state.next_step = True
    st.session_state.auto_sim = False

if reset_button:
    st.session_state.G = generate_network(n, k, p)
    st.session_state.states = initialize_states(st.session_state.G)
    st.session_state.stats = {"step": [0], "infected": [1], "recovered": [0], "susceptible": [n-1]}
    st.session_state.pos = nx.spring_layout(st.session_state.G, seed=42)
    st.session_state.auto_sim = False
    st.session_state.next_step = False
    st.session_state.total_infected = 1
    st.session_state.new_infections = 0
    st.session_state.daily_stats = [{"Day": 0, "Susceptible": n-1, "Infected": 1, "Recovered": 0, "Quarantined": 0, "New Infections": 0, "Total Infected": 1}]
    # Clear the visualization and force rerun
    graph_placeholder.empty()
    chart_placeholder.empty()
    days_placeholder.empty()
    history_container.empty()
    st.rerun()

if auto_sim_button:
    st.session_state.auto_sim = True
    st.session_state.next_step = False

if pause_button:
    st.session_state.auto_sim = False
    st.session_state.next_step = False

# Auto simulation logic
if st.session_state.auto_sim:
    while any(s == 'I' for s in st.session_state.states.values()):
        # Update states
        st.session_state.states = sir_step(
            st.session_state.G, st.session_state.states, R0, recovery_prob, quarantine_pct, distancing_strength
        )
        update_stats(st.session_state.states, st.session_state.stats)
        update_visualization()
        time.sleep(step_delay)
    
    st.session_state.auto_sim = False
    st.rerun()

# Next step logic
if st.session_state.next_step:
    if any(s == 'I' for s in st.session_state.states.values()):
        st.session_state.states = sir_step(
            st.session_state.G, st.session_state.states, R0, recovery_prob, quarantine_pct, distancing_strength
        )
        update_stats(st.session_state.states, st.session_state.stats)
        update_visualization()
        if step_delay > 0:
            time.sleep(step_delay)
        st.session_state.next_step = False
    else:
        st.session_state.next_step = False

# Static visualization
if not st.session_state.auto_sim and not st.session_state.next_step:
    update_visualization()