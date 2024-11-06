"""Single-queue simulation example."""

COMMENT_SECTIONS = """
```yaml
contents:
    - 0. Imports
    - 1. Configuration
    - 2. Define Routing Functions
    - 3. Intitialize Simulation
    - 4. Intialize Queue
    - 5. Initialize Network
    - 6. Register Customer Generation Processes
    - 7. Run Simulation
    - 8. Access Event Log
```
"""

##############
# $0 IMPORTS #
##############

import simpy
from simdist import dists

from simq.core import Network, Node

####################
# $1 CONFIGURATION #
####################

__all__ = []
SIMULATION_TIME: float = 30.0

###############################
# $2 DEFINE ROUTING FUNCTIONS #
###############################


def leave(customer_id: int, current_queue: Node, queue_system: Network) -> None:
    """Leave simulation.

    Args:
        customer_id (int): The identifier of a customer.
        current_queue (Node): The node that the customer is leaving.
        queue_system (Network): The network that contains all the nodes.
    """
    queue_system.log(
        {
            "customer": customer_id,
            "action": "routing",
            "node": current_queue.name,
            "destination": "exit",
        }
    )


############################
# $3 INITIALIZE SIMULATION #
############################

env = simpy.Environment()

#######################
# $4 INITIALIZE QUEUE #
#######################

queue = Node(
    env,
    name="Queue 2",
    num_servers=1,
    service_time_dist=dists.Gamma(5, 5),
    inter_arrival_dist=dists.Gamma(1, 2),
    routing_strategy=leave,
)

#########################
# $5 INITIALIZE NETWORK #
#########################

system = Network(env, [queue])

#############################################
# $6 REGISTER CUSTOMER GENERATION PROCESSES #
#############################################

system.start_customer_generation()

#####################
# $7 RUN SIMULATION #
#####################

_ = env.run(until=SIMULATION_TIME)

#######################
# $8 ACCESS EVENT LOG #
#######################

for entry in system.event_log:
    print(entry)
