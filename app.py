import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import time
import matplotlib.image as mpimg
from utils import generate_network, initialize_states, sir_step, get_node_colors

# Set page to wide mode for better layout
st.set_page_config(layout="wide")

# Remove Streamlit header completely and reduce all top spacing
st.markdown("""
    <style>
        /* General background and text */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #222831;
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: linear-gradient(135deg, #00b4d8 0%, #48cae4 100%);
            color: #222831;
        }
        /* Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #ffaf7b 0%, #d76d77 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%);
            color: #fff;
        }
        /* Sliders */
        .stSlider>div>div>div {
            background: #e0e0e0;
        }
        .stSlider>div>div>div>div {
            background: #00b4d8;
        }
        /* Titles and headers */
        .stTitle, .stHeader, .stSubheader {
            color: #185a9d;
        }
        /* Info boxes */
        .stInfo {
            background: #caf0f8;
            color: #222831;
        }
        /* Chart background */
        .element-container .stPlotlyChart, .element-container .stAltairChart, .element-container .stVegaLiteChart {
            background: #f5f7fa !important;
        }
        /* Hide Streamlit header and main menu */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 0rem !important; margin-top: 0 !important;}
        .main .block-container {padding-top: 0rem !important; margin-top: 0 !important;}
        .css-18e3th9 {padding-top: 0rem !important; margin-top: 0 !important;}
        .css-1d391kg {padding-top: 0rem !important; margin-top: 0 !important;}
        .css-1v0mbdj {padding-top: 0rem !important; margin-top: 0 !important;}
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

# Sidebar controls
with st.sidebar:
    st.header("Simulation Parameters")
    n = st.slider("Population Size", 100, 2000, 500)
    k = st.slider("Avg. Degree (k)", 2, 20, 6)
    p = st.slider("Randomness (p)", 0.0, 1.0, 0.1)
    R0 = st.slider("R₀ (Reproduction Number)", 0.5, 5.0, 2.5)
    recovery_prob = st.slider("Recovery Probability", 0.01, 1.0, 0.1)
    quarantine_pct = st.slider("Quarantine %", 0.0, 1.0, 0.0)
    distancing_strength = st.slider("Social Distancing", 0.0, 1.0, 0.0)
    step_delay = st.slider("Step Delay (seconds)", 0.0, 2.0, value=0.05)
    show_edges = st.checkbox("Show Network Edges", value=False)

# Efficiently cache the network layout (pos) for a given graph
@st.cache_data(show_spinner=False)
def get_layout(_G):
    return nx.spring_layout(_G, seed=42)

# Create consistent layout structure for both auto and static visualization
col1, col2 = st.columns([1.4, 1])

# Create placeholders that will be used in both auto and static modes
with col1:
    st.title("Virus Spread Simulation (SIR Model)")
    graph_placeholder = st.empty()

with col2:
    # Manual controls in a vertical layout
    st.subheader("Simulation Controls")
    if st.button("Next Step", use_container_width=True):
        st.session_state.next_step = True
        st.session_state.auto_sim = False

    if st.button("Reset", use_container_width=True):
        st.session_state.G = generate_network(n, k, p)
        st.session_state.states = initialize_states(st.session_state.G)
        st.session_state.stats = {"step": [0], "infected": [1], "recovered": [0], "susceptible": [n-1]}
        st.session_state.pos = get_layout(st.session_state.G)
        st.session_state.auto_sim = False
        st.session_state.next_step = False

    if st.button("Start Auto Simulation", use_container_width=True):
        st.session_state.auto_sim = True
        st.session_state.next_step = False

    if st.button("Pause Simulation", use_container_width=True):
        st.session_state.auto_sim = False
        st.session_state.next_step = False

    # Statistics section
    st.markdown("### Statistics")
    days_placeholder = st.empty()
    chart_placeholder = st.empty()

# Initialize network if not exists
if st.session_state.G is None:
    st.session_state.G = generate_network(n, k, p)
    st.session_state.states = initialize_states(st.session_state.G)
    st.session_state.stats = {"step": [0], "infected": [1], "recovered": [0], "susceptible": [n-1]}
    st.session_state.pos = get_layout(st.session_state.G)

def update_stats(states, stats):
    infected = sum(1 for s in states.values() if s == 'I')
    recovered = sum(1 for s in states.values() if s == 'R')
    susceptible = sum(1 for s in states.values() if s == 'S')
    stats["step"].append(stats["step"][-1] + 1)
    stats["infected"].append(infected)
    stats["recovered"].append(recovered)
    stats["susceptible"].append(susceptible)

@st.cache_data(show_spinner=False)
def create_network_visualization(states, pos):
    fig, ax = plt.subplots(figsize=(8, 6))
    # Load and display the background image
    img = mpimg.imread('background.png')
    ax.imshow(img, extent=[-1.1, 1.1, -1.1, 1.1], aspect='auto')
    # For large graphs, skip edge drawing for performance
    draw_edges = show_edges and len(states) <= 1000
    nx.draw(
        st.session_state.G, pos,
        node_color=get_node_colors(states),
        node_size=20,
        ax=ax,
        with_labels=False,
        edge_color='grey' if draw_edges else 'none'
    )
    return fig

def update_visualization():
    # Update visualization using cached function
    fig = create_network_visualization(st.session_state.states, st.session_state.pos)
    graph_placeholder.pyplot(fig)
    plt.close(fig)
    
    # Update stats
    days_placeholder.info(f"Days passed: {st.session_state.stats['step'][-1]}")
    chart_placeholder.line_chart({
        "Infected": st.session_state.stats["infected"],
        "Recovered": st.session_state.stats["recovered"],
        "Susceptible": st.session_state.stats["susceptible"]
    }, color=["#FF6B6B", "#4ECDC4", "#45B7D1"])

# Auto simulation logic
if st.session_state.auto_sim:
    if any(s == 'I' for s in st.session_state.states.values()):
        st.session_state.states = sir_step(
            st.session_state.G, st.session_state.states, R0, recovery_prob, quarantine_pct, distancing_strength
        )
        update_stats(st.session_state.states, st.session_state.stats)
        update_visualization()
        if step_delay > 0:
            time.sleep(step_delay)
        st.rerun()
    else:
        st.session_state.auto_sim = False

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