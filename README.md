# SimQ

Queueing network tool based on SimPy.

# Installation

```bash
pip install SimQ
```

# Example

The following is a simple example of using SimQ to simulate a single-node queueing system.

```python
import simpy
from simdist import dists
from simq.core import Network, Node

SIMULATION_TIME: float = 30.0

def leave(customer_id: int, current_queue: Node, queue_system: Network) -> None:
    queue_system.log(
        {
            "customer": customer_id,
            "action": "routing",
            "node": current_queue.name,
            "destination": "exit",
        }
    )


env = simpy.Environment()

queue = Node(
    env,
    name="Queue 2",
    num_servers=1,
    service_time_dist=dists.Gamma(5, 5),
    inter_arrival_dist=dists.Gamma(1, 2),
    routing_strategy=leave,
)

system = Network(env, [queue])

system.start_customer_generation()

_ = env.run(until=SIMULATION_TIME)

for entry in system.event_log:
    print(entry)
```
