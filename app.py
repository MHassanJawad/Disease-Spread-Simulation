import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import time
from utils import generate_network, initialize_states, sir_step, get_node_colors

# Set page to wide mode for better layout
st.set_page_config(layout="wide")

<<<<<<< Updated upstream
st.title("Virus Spread Simulation (SIR Model)")

# Sidebar controls
=======
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

# Sidebar controls - Moved to top
>>>>>>> Stashed changes
with st.sidebar:
    st.header("Simulation Parameters")
    n = st.slider("Population Size", 100, 2000, 500)
    k = st.slider("Avg. Degree (k)", 2, 20, 6)
    p = st.slider("Randomness (p)", 0.0, 1.0, 0.1)
    R0 = st.slider("R₀ (Reproduction Number)", 0.5, 5.0, 2.5)
    recovery_prob = st.slider("Recovery Probability", 0.01, 1.0, 0.1)
    quarantine_pct = st.slider("Quarantine %", 0.0, 1.0, 0.0)
    distancing_strength = st.slider("Social Distancing", 0.0, 1.0, 0.0)
    step_delay = st.slider("Step Delay (seconds)", 0.1, 2.0, 0.5)
    show_edges = st.checkbox("Show Network Edges", value=True)

<<<<<<< Updated upstream
# Session state initialization
if "G" not in st.session_state:
=======
# Create consistent layout structure for both auto and static visualization
col1, col2 = st.columns([1.4, 1])

# Create placeholders that will be used in both auto and static modes
with col1:
    st.title("Virus Spread Simulation (SIR Model)")
    graph_placeholder = st.empty()

with col2:
    # Manual controls in a vertical layout
    st.subheader("Simulation Controls")
    next_step_button = st.button("Next Step", use_container_width=True)
    reset_button = st.button("Reset", use_container_width=True)
    auto_sim_button = st.button("Start Auto Simulation", use_container_width=True)
    pause_button = st.button("Pause Simulation", use_container_width=True)

    # Statistics section
    st.markdown("### Statistics")
    days_placeholder = st.empty()
    chart_placeholder = st.empty()

# Initialize network if not exists
if st.session_state.G is None:
>>>>>>> Stashed changes
    st.session_state.G = generate_network(n, k, p)
    st.session_state.states = initialize_states(st.session_state.G)
    st.session_state.stats = {"step": [0], "infected": [1], "recovered": [0], "susceptible": [n-1]}
    st.session_state.auto_sim = False
    st.session_state.next_step = False

def update_stats(states, stats):
    infected = sum(1 for s in states.values() if s == 'I')
    recovered = sum(1 for s in states.values() if s == 'R')
    susceptible = sum(1 for s in states.values() if s == 'S')
    stats["step"].append(stats["step"][-1] + 1)
    stats["infected"].append(infected)
    stats["recovered"].append(recovered)
    stats["susceptible"].append(susceptible)

# Manual controls in a more organized layout
st.subheader("Simulation Controls")
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Next Step", use_container_width=True):
        st.session_state.next_step = True
        st.session_state.auto_sim = False  # Pause auto if manual step

with col2:
    if st.button("Reset", use_container_width=True):
        st.session_state.G = generate_network(n, k, p)
        st.session_state.states = initialize_states(st.session_state.G)
        st.session_state.stats = {"step": [0], "infected": [1], "recovered": [0], "susceptible": [n-1]}
        st.session_state.auto_sim = False
        st.session_state.next_step = False

with col3:
    if st.button("Start Auto Simulation", use_container_width=True):
        st.session_state.auto_sim = True
        st.session_state.next_step = False

with col4:
    if st.button("Pause Simulation", use_container_width=True):
        st.session_state.auto_sim = False
        st.session_state.next_step = False

# Create consistent layout structure for both auto and static visualization
st.markdown("### Network Visualization and Statistics")
col1, col2 = st.columns([1.4, 1])

# Create placeholders that will be used in both auto and static modes
with col1:
    graph_placeholder = st.empty()
with col2:
    days_placeholder = st.empty()
    chart_placeholder = st.empty()

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
<<<<<<< Updated upstream
=======
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
>>>>>>> Stashed changes
    graph_placeholder.pyplot(fig)
    plt.close(fig)  # Close the figure to prevent memory leaks
    
    # Update stats in the same placeholders
    days_placeholder.info(f"Days passed: {st.session_state.stats['step'][-1]}")
    chart_placeholder.line_chart({
        "Infected": st.session_state.stats["infected"],
        "Recovered": st.session_state.stats["recovered"],
        "Susceptible": st.session_state.stats["susceptible"]
    }, color=["#ff0000", "#0000ff", "#00ff00"])  # Red, Blue, Green
<<<<<<< Updated upstream
=======

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
    # Clear the visualization and force rerun
    graph_placeholder.empty()
    chart_placeholder.empty()
    days_placeholder.empty()
    st.rerun()

if auto_sim_button:
    st.session_state.auto_sim = True
    st.session_state.next_step = False

if pause_button:
    st.session_state.auto_sim = False
    st.session_state.next_step = False
>>>>>>> Stashed changes

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

# Next step logic - using same pattern as auto simulation
if st.session_state.next_step:
    if any(s == 'I' for s in st.session_state.states.values()):
        # Update states
        st.session_state.states = sir_step(
            st.session_state.G, st.session_state.states, R0, recovery_prob, quarantine_pct, distancing_strength
        )
        update_stats(st.session_state.states, st.session_state.stats)
        update_visualization()
        time.sleep(step_delay)  # Add small delay for consistency
        st.session_state.next_step = False
    else:
        st.session_state.next_step = False

# Static visualization (only shown when not in auto simulation or next step)
if not st.session_state.auto_sim and not st.session_state.next_step:
    update_visualization()