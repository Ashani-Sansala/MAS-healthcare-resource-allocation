import mesa
import numpy as np
import random
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class Message:
    """
    Represents a communication message between agents
    """
    def __init__(self, sender, recipient, content, message_type):
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.message_type = message_type
        self.timestamp = datetime.now()

class MessageManager:
    """
    Centralized message management system
    """
    def __init__(self):
        self.message_log = []
    
    def send_message(self, message):
        """
        Log and process sent messages
        """
        self.message_log.append(message)
        logging.info(f"MESSAGE: From {message.sender} to {message.recipient} "
                     f"[{message.message_type}]: {message.content}\n")
    
    def get_messages_for_agent(self, agent):
        """
        Retrieve messages for a specific agent
        """
        return [msg for msg in self.message_log if msg.recipient == agent]

class ResourceAllocationEnvironment(mesa.Model):
    """
    Multi-Agent Healthcare Resource Allocation Environment
    
    Simulates dynamic resource allocation across hospitals and patients
    with intelligent agent interactions and optimization strategies.
    """
    
    def __init__(self, num_hospitals=5, num_patients=50, initial_resources=1000):
        super().__init__()

        # Add grid for visualization
        self.grid = mesa.space.MultiGrid(10, 10, True)
        
        # Simulation Configuration
        self.num_hospitals = num_hospitals
        self.num_patients = num_patients
        self.initial_resources = initial_resources
        
        # Global Message Manager
        self.global_message_manager = MessageManager()
        
        # Agent Collections
        self.hospitals = []
        self.patients = []
        self.resource_coordinator = None
        
        # Data Collection Setup
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Total Unmet Needs": "total_unmet_needs",
                "Resource Allocation Efficiency": "resource_allocation_efficiency"
            },
            agent_reporters={
                "Hospital Resources": lambda a: a.current_resources if isinstance(a, HospitalAgent) else None,
                "Patient Unmet Needs": lambda a: a.unmet_needs if isinstance(a, PatientAgent) else None
            }
        )
        
        # Scheduling
        self.schedule = mesa.time.RandomActivation(self)
        
        # Setup Simulation Agents
        self.setup_resource_coordinator()
        self.setup_hospitals()
        self.setup_patients()
        
        # Performance Metrics
        self.total_unmet_needs = 0
        self.resource_allocation_efficiency = 0.0

        # Place agents on grid
        for agent in self.hospitals + self.patients:
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))
    
    def setup_resource_coordinator(self):
        """Initialize the central resource coordination agent"""
        self.resource_coordinator = ResourceCoordinatorAgent(
            unique_id=self.next_id(), 
            model=self
        )
        self.schedule.add(self.resource_coordinator)
    
    def setup_hospitals(self):
        """Create specialized hospital agents"""
        for i in range(self.num_hospitals):
            hospital = HospitalAgent(
                unique_id=self.next_id(),
                model=self,
                specialization=self.get_hospital_specialization(),
                initial_resources=self.initial_resources
            )

            self.hospitals.append(hospital)
            self.schedule.add(hospital)
    
    def setup_patients(self):
        """Generate patient agents with varying medical needs"""
        for i in range(self.num_patients):
            patient = PatientAgent(
                unique_id=self.next_id(),
                model=self,
                severity=random.choice(['low', 'medium', 'high'])
            )
            self.patients.append(patient)
            self.schedule.add(patient)
    
    def get_hospital_specialization(self):
        """Assign random hospital specializations"""
        specializations = [
            'emergency', 'intensive_care', 'general', 
            'pediatric', 'surgical'
        ]
        return random.choice(specializations)
    
    def negotiate_resource_allocation(self, patient, required_resources):
        """
        Centralized resource negotiation and allocation strategy
        
        Steps:
        1. Broadcast patient needs
        2. Collect hospital bids
        3. Allocate resources through coordinator
        """
        bids = []
        for hospital in self.hospitals:
            bid = hospital.evaluate_patient_admission(patient, required_resources)
            if bid is not None:
                bids.append((hospital, bid))
        
        return self.resource_coordinator.allocate_resources(patient, bids)
    
    def step(self):
        """
        Simulate one time step of resource allocation
        
        Workflow:
        1. Generate patient medical needs
        2. Process hospital resources
        3. Coordinate global resource allocation
        4. Collect performance data
        """
        # Patient medical needs generation
        for patient in self.patients:
            patient.generate_medical_needs()
        
        # Hospital resource processing
        for hospital in self.hospitals:
            hospital.process_resources()
        
        # Global resource coordination
        self.resource_coordinator.coordinate_global_resources()
        
        # Update system-level performance metrics
        self.update_performance_metrics()
        
        # Advance simulation schedule
        self.schedule.step()
        
        # Collect data for visualization and analysis
        self.datacollector.collect(self)
        
        # Log simulation progress
        logger.info(f"Simulation Step: Unmet Needs = {self.total_unmet_needs}, "
                    f"Allocation Efficiency = {self.resource_allocation_efficiency:.2%}")
    
    def update_performance_metrics(self):
        """Calculate and update system-wide performance indicators"""
        unmet_needs = sum(patient.unmet_needs for patient in self.patients)
        total_resources = sum(hospital.current_resources for hospital in self.hospitals)
        
        self.total_unmet_needs = unmet_needs
        self.resource_allocation_efficiency = (
            (total_resources - unmet_needs) / (total_resources + 1)
        )

class ResourceCoordinatorAgent(mesa.Agent):
    """Central agent for coordinating resource allocation strategies"""
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.global_strategy = self.develop_allocation_strategy()
        self.message_manager = MessageManager()
    
    def develop_allocation_strategy(self):
        """
        Create a multi-objective optimization strategy
        
        Priority factors:
        1. Patient severity
        2. Hospital capacity
        3. Resource efficiency
        """
        return {
            'priority_factors': {
                'patient_severity': 0.4,
                'hospital_capacity': 0.3,
                'resource_efficiency': 0.3
            }
        }
    
    def allocate_resources(self, patient, hospital_bids):
        """
        Enhanced resource allocation with explicit messaging
        """
        if not hospital_bids:
            # Send a broadcast message about resource unavailability
            message = Message(
                sender=self,
                recipient="BROADCAST",
                content=f"No hospitals available for patient {patient.unique_id}",
                message_type="RESOURCE_UNAVAILABLE"
            )
            self.message_manager.send_message(message)
            logger.warning(f"No hospitals available for patient {patient.unique_id}")
            return None

        # Sort bids and prepare messages
        sorted_bids = sorted(
            hospital_bids,
            key=lambda x: self.evaluate_bid(x[0], x[1], patient),
            reverse=True
        )

        # Log the negotiation process
        for i, (hospital, bid_value) in enumerate(sorted_bids):
            logger.info(f"Negotiation Step {i+1}: Hospital {hospital.unique_id} bid value = {bid_value}")

        # Select best hospital and create allocation message
        best_hospital, bid_value = sorted_bids[0]
        allocation_message = Message(
            sender=self,
            recipient=best_hospital,
            content={
                'patient_id': patient.unique_id,
                'required_resources': patient.medical_needs,
                'bid_value': bid_value
            },
            message_type="RESOURCE_ALLOCATION"
        )

        # Send allocation message
        self.message_manager.send_message(allocation_message)
        logger.info(f"Allocation Decision: Patient {patient.unique_id} assigned to Hospital {best_hospital.unique_id}")

        # Actual resource allocation
        allocation_success = best_hospital.allocate_resources(patient, bid_value)

        # Send confirmation/rejection message
        result_message = Message(
            sender=self,
            recipient=patient,
            content={
                'allocation_status': allocation_success,
                'hospital_id': best_hospital.unique_id
            },
            message_type="ALLOCATION_RESULT"
        )
        self.message_manager.send_message(result_message)

        return allocation_success
    
    def evaluate_bid(self, hospital, bid_value, patient):
        """
        Comprehensive bid evaluation using multiple factors
        
        Scoring considers:
        - Patient severity
        - Hospital capacity
        - Resource efficiency
        """
        strategy = self.global_strategy['priority_factors']
        
        score = (
            strategy['patient_severity'] * self.severity_score(patient) +
            strategy['hospital_capacity'] * self.capacity_score(hospital) +
            strategy['resource_efficiency'] * bid_value
        )
        
        return score
    
    def severity_score(self, patient):
        """Convert patient severity to numerical score"""
        severity_map = {'low': 0.2, 'medium': 0.5, 'high': 1.0}
        return severity_map.get(patient.severity, 0.5)
    
    def capacity_score(self, hospital):
        """Evaluate hospital capacity utilization"""
        return min(hospital.current_resources / hospital.initial_resources, 1.0)
    
    def coordinate_global_resources(self):
        """
        Periodic global resource rebalancing
        
        Strategies:
        - Inter-hospital resource transfer
        - Load balancing
        """
        hospitals = self.model.hospitals
        
        # Simple load balancing: transfer from high-capacity to low-capacity hospitals
        high_capacity_hospitals = sorted(
            [h for h in hospitals if h.current_resources > h.initial_resources * 1.2], 
            key=lambda x: x.current_resources, 
            reverse=True
        )
        
        low_capacity_hospitals = sorted(
            [h for h in hospitals if h.current_resources < h.initial_resources * 0.8], 
            key=lambda x: x.current_resources
        )
        
        for source in high_capacity_hospitals:
            for target in low_capacity_hospitals:
                transfer_amount = min(
                    source.current_resources * 0.1,  # 10% of source resources
                    target.initial_resources * 0.2 - target.current_resources  # Needed to reach 80% capacity
                )
                
                if transfer_amount > 0:
                    # Create resource transfer message
                    transfer_message = Message(
                        sender=source,
                        recipient=target,
                        content={
                            'transfer_amount': transfer_amount,
                            'source_hospital': source.unique_id,
                            'target_hospital': target.unique_id
                        },
                        message_type="RESOURCE_TRANSFER"
                    )
                    self.message_manager.send_message(transfer_message)
                    
                    source.current_resources -= transfer_amount
                    target.current_resources += transfer_amount
                    
                    logger.info(f"Resource Transfer: {source.unique_id} -> {target.unique_id}: {transfer_amount}")

class HospitalAgent(mesa.Agent):
    """Agent representing a hospital with intelligent resource management"""
    
    def __init__(self, unique_id, model, specialization, initial_resources):
        super().__init__(unique_id, model)
        
        self.specialization = specialization
        self.initial_resources = initial_resources
        self.current_resources = initial_resources
        
        # Dynamic admission policy
        self.admission_policy = self.develop_admission_policy()
        
        # Message tracking
        self.received_messages = []
    
    def develop_admission_policy(self):
        """Create context-aware admission strategy"""
        return {
            'specialization_weight': 0.4,
            'resource_efficiency_weight': 0.6
        }
    
    def evaluate_patient_admission(self, patient, required_resources):
        """
        Enhanced admission evaluation with messaging
        """
        # Create and send a bid message
        bid_message = Message(
            sender=self,
            recipient=self.model.resource_coordinator,
            content={
                'patient_id': patient.unique_id,
                'required_resources': required_resources,
                'hospital_specialization': self.specialization
            },
            message_type="ADMISSION_BID"
        )
        self.model.resource_coordinator.message_manager.send_message(bid_message)
        logger.info(f"Hospital {self.unique_id} submitted a bid for patient {patient.unique_id}")

        # Existing admission logic
        if self.current_resources < required_resources:
            logger.info(f"Hospital {self.unique_id} rejected patient {patient.unique_id} due to insufficient resources")
            return None

        match_score = self.calculate_admission_score(patient, required_resources)
        admission_threshold = 0.5

        if match_score > admission_threshold:
            logger.info(f"Hospital {self.unique_id} accepted patient {patient.unique_id} with a score of {match_score:.2f}")
        else:
            logger.info(f"Hospital {self.unique_id} rejected patient {patient.unique_id} with a score of {match_score:.2f}")

        return match_score if match_score > admission_threshold else None
    
    def calculate_admission_score(self, patient, required_resources):
        """
        Multi-factor admission scoring mechanism
        
        Evaluation dimensions:
        1. Specialization compatibility
        2. Resource utilization efficiency
        """
        policy = self.admission_policy
        
        # Specialization match scoring
        specialization_match = 1.0 if self.matches_specialization(patient) else 0.3
        
        # Resource efficiency calculation
        resource_efficiency = 1 - (required_resources / self.current_resources)
        
        # Weighted score computation
        score = (
            policy['specialization_weight'] * specialization_match +
            policy['resource_efficiency_weight'] * resource_efficiency
        )
        
        return score
    
    def matches_specialization(self, patient):
        """
        Determine specialization compatibility
        
        Future enhancement: More sophisticated matching logic
        """
        return True  # Placeholder compatibility check
    
    def allocate_resources(self, patient, allocation_score):
        """
        Resource allocation to patient with score-based decision
        
        Returns allocation success status
        """
        required_resources = patient.medical_needs
        
        if self.current_resources >= required_resources:
            self.current_resources -= required_resources
            
            # Create allocation confirmation message
            allocation_message = Message(
                sender=self,
                recipient=patient,
                content={
                    'allocated_resources': required_resources,
                    'hospital_id': self.unique_id
                },
                message_type="RESOURCE_ALLOCATED"
            )
            self.model.resource_coordinator.message_manager.send_message(allocation_message)
            
            return True
        
        return False
    
    def process_resources(self):
        """
        Periodic resource management and optimization
        
        Strategies:
        - Gradual resource replenishment
        - Capacity growth limit
        """
        max_growth_factor = 1.5
        replenishment_rate = 1.1
        
        self.current_resources = min(
            self.current_resources * replenishment_rate,
            self.initial_resources * max_growth_factor
        )

class PatientAgent(mesa.Agent):
    """Agent representing a patient with dynamic medical needs"""
    
    def __init__(self, unique_id, model, severity):
        super().__init__(unique_id, model)
        
        self.severity = severity
        self.medical_needs = 0
        self.unmet_needs = 0
        self.received_messages = []
    
    def generate_medical_needs(self):
        """
        Stochastic medical resource requirement generation
        
        Needs vary based on patient severity:
        - Low: Minor interventions
        - Medium: Moderate treatments
        - High: Intensive care requirements
        """
        severity_resource_ranges = {
            'low': (5, 20),
            'medium': (20, 100),
            'high': (100, 200)
        }
        
        min_need, max_need = severity_resource_ranges.get(self.severity, (10, 50))
        self.medical_needs = random.randint(min_need, max_need)

        # Create and send a medical needs message
        needs_message = Message(
            sender=self,
            recipient=self.model.resource_coordinator,
            content={
                'medical_needs': self.medical_needs,
                'patient_severity': self.severity
            },
            message_type="MEDICAL_NEEDS"
        )
        self.model.resource_coordinator.message_manager.send_message(needs_message)
        
        # Attempt resource allocation
        allocation_result = self.model.negotiate_resource_allocation(
            self, 
            self.medical_needs
        )
        
        # Track unmet medical needs
        self.unmet_needs = self.medical_needs if not allocation_result else 0

def run_healthcare_simulation(num_hospitals=5, num_patients=50, simulation_steps=10):
    """
    Execute healthcare resource allocation simulation
    
    Configurable parameters:
    - Number of hospitals
    - Number of patients
    - Simulation duration
    """
    model = ResourceAllocationEnvironment(
        num_hospitals=num_hospitals, 
        num_patients=num_patients, 
        initial_resources=1000
    )
    
    # Run simulation for specified steps
    for _ in range(simulation_steps):
        model.step()
    
    # Print simulation results
    logger.info(f"Simulation Completed")
    logger.info(f"Total Unmet Needs: {model.total_unmet_needs}")
    logger.info(f"Resource Allocation Efficiency: {model.resource_allocation_efficiency:.2%}")
    
    return model

# Main execution
if __name__ == "__main__":
    run_healthcare_simulation()