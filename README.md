# Virus Spread Simulation (SIR Model)

An interactive web application that simulates the spread of a virus through a network using the SIR (Susceptible-Infected-Recovered) model. The simulation visualizes how a virus spreads through a population network and shows the progression of infection over time.

## Features

- Interactive network visualization of virus spread
- Real-time statistics and infection curves
- Adjustable simulation parameters:
  - Population size
  - Network connectivity
  - Virus reproduction number (R₀)
  - Recovery probability
  - Quarantine percentage
  - Social distancing measures
- Manual step-by-step simulation
- Auto simulation mode
- Smooth visualization updates

## Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/virus-spread-simulation.git
cd virus-spread-simulation
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
streamlit run app.py
```

## Usage

1. Adjust the simulation parameters in the sidebar:

   - Population Size: Number of individuals in the network
   - Avg. Degree (k): Average number of connections per individual
   - Randomness (p): Probability of random connections
   - R₀: Basic reproduction number of the virus
   - Recovery Probability: Chance of recovery per day
   - Quarantine %: Percentage of infected individuals quarantined
   - Social Distancing: Strength of social distancing measures
   - Step Delay: Time between updates in auto simulation

2. Use the control buttons:
   - Next Step: Progress simulation one step at a time
   - Reset: Start a new simulation
   - Start Auto Simulation: Run simulation automatically
   - Pause Simulation: Stop the auto simulation

## Visualization

- Network Graph: Shows the spread of infection through the network
  - Green nodes: Susceptible individuals
  - Red nodes: Infected individuals
  - Blue nodes: Recovered individuals
- Line Chart: Shows the progression of infection over time
  - Green line: Number of susceptible individuals
  - Red line: Number of infected individuals
  - Blue line: Number of recovered individuals

## Dependencies

- streamlit==1.32.0
- networkx==3.2.1
- matplotlib==3.8.3

## License

This project is licensed under the MIT License - see the LICENSE file for details.
