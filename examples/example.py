import simpy
from collections.abc import Generator
from typing import Any
from simdist import dists
from simq.core import Node, Network


# Some chance of going to Queue 2 after Queue 1, else leave the system.
def queue1_routing(
    customer_id: int, current_queue: Node, queue_system: Network
) -> Generator[Any, Any, Any] | None:
    if dists.Gamma(1, 1).sample() < 0.5:
        queue_system.log(
            {
                "customer": customer_id,
                "action": "routing",
                "node": current_queue.name,
                "destination": 1,
            }
        )
        yield queue_system.env.process(
            queue_system.nodes[1].service(customer_id, queue_system)
        )
    else:
        queue_system.log(
            {
                "customer": customer_id,
                "action": "routing",
                "node": current_queue.name,
                "destination": "exit",
            }
        )


# After Queue 2, customer always leaves the system
def queue2_routing(customer_id: int, current_queue: Node, queue_system: Network):
    queue_system.log(
        {
            "customer": customer_id,
            "action": "routing",
            "node": current_queue.name,
            "destination": "exit",
        }
    )


# Example usage with multiple queues and individual routing strategies
env = simpy.Environment()

# Define the queues with different service and arrival distributions, and routing strategies
queue1 = Node(
    env,
    name="Queue 1",
    num_servers=2,
    service_time_dist=dists.Gamma(1, 1),
    inter_arrival_dist=dists.Gamma(1, 1),
    routing_strategy=queue1_routing,
)

queue2 = Node(
    env,
    name="Queue 2",
    num_servers=1,
    service_time_dist=dists.Gamma(5, 5),
    inter_arrival_dist=dists.Gamma(1, 1),  # Different arrival rate for Queue 2
    routing_strategy=queue2_routing,
)

# Define a queue system with multiple queues
system = Network(env, [queue1, queue2])

# Start customer generation for all queues
system.start_customer_generation()

# Run the simulation
simulation_time: float = 30.0
_ = env.run(until=simulation_time)

for entry in system.event_log:
    print(entry)
