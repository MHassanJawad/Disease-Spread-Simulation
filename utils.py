# utils.py
import networkx as nx
import random

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