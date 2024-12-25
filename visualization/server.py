import sys
import os
import mesa
import numpy as np

from mesa.visualization.modules import TextElement
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.resource_allocation_model import ResourceAllocationEnvironment, HospitalAgent, PatientAgent

def agent_portrayal(agent):
    """
    Define visual representation for different agent types
    
    Color and size coding:
    - Hospitals: Blue circles
    - Patients: Red circles
    - Size varies based on resources/needs
    """
    portrayal = {
        "Shape": "circle", 
        "Filled": "true",
        "Layer": 0,
        "r": 0.5  # Default radius
    }
    
    if isinstance(agent, HospitalAgent):
        portrayal["Color"] = "blue"
        # Adjust hospital circle size based on current resources
        portrayal["r"] = min(0.5 + (agent.current_resources / 1000), 1.0)
        portrayal["Text"] = f"Hospital {agent.unique_id}\nResources: {agent.current_resources:.0f}"
    
    elif isinstance(agent, PatientAgent):
        portrayal["Color"] = "red"
        # Adjust patient circle size based on medical needs
        portrayal["r"] = min(0.3 + (agent.medical_needs / 500), 0.7)
        portrayal["Text"] = f"Patient {agent.unique_id}\nNeeds: {agent.medical_needs:.0f}"
    
    return portrayal

# Create Grid Visualization
grid = mesa.visualization.CanvasGrid(
    agent_portrayal, 
    grid_width=10,     # Grid dimensions
    grid_height=10,    # Grid dimensions
    canvas_width=500,  # Pixel width
    canvas_height=500  # Pixel height
)

# Performance Charts
charts = [
    # Resource Allocation Efficiency Chart
    mesa.visualization.ChartModule([
        {"Label": "Resource Allocation Efficiency", "Color": "Green"}
    ]),
    
    # Total Unmet Needs Chart
    mesa.visualization.ChartModule([
        {"Label": "Total Unmet Needs", "Color": "Red"}
    ])
]

# Message Log Visualization
class MessageLogVisualization(mesa.visualization.TextElement):
    """Visualization element for displaying the message log"""
    def __init__(self):
        pass

    def portrayal(self, model):
        return "\n".join(
            [f"{msg.timestamp} - {msg.sender} -> {msg.recipient}: {msg.content}" for msg in model.global_message_manager.message_log[-10:]]
        )

    def render(self, model):
        return self.portrayal(model)

message_log = MessageLogVisualization()

# Simulation Parameters Slider
model_params = {
    "num_hospitals": mesa.visualization.Slider(
        "Number of Hospitals", 
        25, 1, 100, 1
    ),
    "num_patients": mesa.visualization.Slider(
        "Number of Patients", 
        60, 10, 100, 5
    ),
    "initial_resources": mesa.visualization.Slider(
        "Initial Hospital Resources", 
        1900, 500, 2400, 100
    )
}

class LegendModule(mesa.visualization.TextElement):
    """Custom legend to explain agent representations"""
    def __init__(self):
        pass

    def render(self, model):
        return (
            "🔵 - <b>HOSPITALS: </b>"
            "Circle size indicates resource capacity<br>"
            "🔴 - <b>PATIENTS: </b>"
            "Circle size indicates medical condition severity<br>"
        )

# Add this line to server creation before launching
legend = LegendModule()

# Modify the server creation line to include legend
server = mesa.visualization.ModularServer(
    ResourceAllocationEnvironment,
    [legend, grid, message_log] + charts,
    "Healthcare Resource Allocation Simulation",
    model_params
)

# Set server port
server.port = 8530

if __name__ == "__main__":
    server.launch()