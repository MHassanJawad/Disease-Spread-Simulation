# utils.py
import networkx as nx
import random
import plotly.graph_objects as go

def generate_network(n, k, p):
    return nx.watts_strogatz_graph(n, k, p)

def initialize_states(G, initial_infected=1):
    states = {node: 'S' for node in G.nodes()}
    infected = random.sample(list(G.nodes()), initial_infected)
    for node in infected:
        states[node] = 'I'
    return states

def sir_step(G, states, R0, recovery_prob, quarantine_pct, distancing_strength):
    new_states = states.copy()
    avg_degree = sum(dict(G.degree()).values()) / G.number_of_nodes()
    p_infection = (R0 / avg_degree) * (1 - distancing_strength)
    infected_nodes = [n for n, s in states.items() if s == 'I']
    susceptible_nodes = [n for n, s in states.items() if s == 'S']
    quarantined = set(random.sample(infected_nodes, int(len(infected_nodes) * quarantine_pct)))
    for node in infected_nodes:
        if node in quarantined:
            new_states[node] = 'Q'
            continue
        for neighbor in G.neighbors(node):
            if states[neighbor] == 'S' and random.random() < p_infection:
                new_states[neighbor] = 'I'
        if random.random() < recovery_prob:
            new_states[node] = 'R'
    return new_states

def get_node_colors(states):
    color_map = {'S': 'green', 'I': 'red', 'R': 'blue', 'Q': 'grey'}
    return [color_map[states[n]] for n in states]

def create_network_plotly(G, states):
    pos = nx.spring_layout(G, seed=42)
    
    # Create edge trace
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    # Create node trace
    node_x = []
    node_y = []
    node_colors = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_colors.append(states[node])

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            size=10,
            color=[{'S': 'green', 'I': 'red', 'R': 'blue', 'Q': 'grey'}[c] for c in node_colors],
            line_width=2))

    # Create figure with larger size
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20,l=20,r=20,t=20),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       height=600,
                       width=800)
                   )
    
    return fig

def create_line_chart(stats):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=stats['step'],
        y=stats['Infected'],
        name='Infected',
        line=dict(color='red')
    ))
    
    fig.add_trace(go.Scatter(
        x=stats['step'],
        y=stats['Recovered'],
        name='Recovered',
        line=dict(color='blue')
    ))
    
    fig.add_trace(go.Scatter(
        x=stats['step'],
        y=stats['Susceptible'],
        name='Susceptible',
        line=dict(color='green')
    ))
    
    fig.update_layout(
        title='Infection Spread Over Time',
        xaxis_title='Days',
        yaxis_title='Number of People',
        hovermode='x unified',
        height=600,
        width=600,
        margin=dict(b=20,l=20,r=20,t=40)
    )
    
    return fig