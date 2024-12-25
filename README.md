# Hospital Resource Allocation Simulation (Using Multi-Agent System)

This project is a multi-agent simulation system built using the Mesa framework. It models hospital resource allocation to patients based on their medical needs and hospital resource capacity.

## Features

### 🤖 Agent Types
- ResourceCoordinatorAgent
    - Central agent managing resource allocation.
    - Develops allocation strategies considering patient severity, hospital capacity, and resource efficiency.
    - Negotiates resource allocation by evaluating hospital bids for patients.
    - Coordinates global resource transfers for load balancing.

- HospitalAgent
    - Represents hospitals with specific specializations and resources.
    - Evaluates patients for admission using a score based on specialization match and resource efficiency.
    - Allocates resources to patients and manages internal resource replenishment.
 
- PatientAgent
    - Represents patients with dynamic medical needs based on severity (low, medium, high).
    - Generates medical needs stochastically.
    - Sends messages to the ResourceCoordinatorAgent to request resources.
 
### 🖼️ Visualization
- Hospitals are represented as blue circles, with size indicating available resources.
- Patients are represented as red circles, with size indicating the severity of their medical needs.
- Includes real-time charts and message logs for monitoring the simulation.

![image](https://github.com/user-attachments/assets/6f2d6000-4051-47c3-9775-bc9909784596)

### 📈 Performance Monitoring
- Resource Allocation Efficiency Chart: Tracks how effectively resources are allocated.
- Total Unmet Needs Chart: Displays the total unmet needs of patients over time.
![image](https://github.com/user-attachments/assets/bee62807-3464-4547-b1a0-0baab20d5b79)


### 🎚️ Interactive Parameters
- Adjust the number of hospitals and patients.
- Set the initial hospital resource levels.

## Installation
### Clone the repository:
```
git clone https://github.com/your-username/hospital-resource-allocation.git
cd hospital-resource-allocation
```

### Install dependencies:
```
pip install -r requirements.txt
```

## Running the Simulation
### Start the server:
```
python server.py
```
### Open the web browser and navigate to http://localhost:8530.

## Requirements
- Python 3.8+
- Mesa 2.1.4
- NumPy 1.22.4
- Matplotlib 3.7.1
