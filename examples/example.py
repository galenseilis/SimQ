import simpy

from simq.dists import Exponential, Normal
from simq.core import GGCQueue, QueueSystem
# Example routing strategies for individual queues


# After Queue 1, 50% chance to go to Queue 2, or leave the system
def queue1_routing(customer_id, current_queue, queue_system):
    if np.random.rand() < 0.5:
        queue_system.event_log.append(
            f"Customer {customer_id} is routed from {current_queue.name} to Queue 2."
        )
        yield queue_system.env.process(
            queue_system.queues[1].customer(customer_id, queue_system)
        )
    else:
        queue_system.event_log.append(
            f"Customer {customer_id} leaves the system after {current_queue.name}."
        )


# After Queue 2, customer always leaves the system
def queue2_routing(customer_id, current_queue, queue_system):
    queue_system.event_log.append(
        f"Customer {customer_id} leaves the system after {current_queue.name}."
    )


# Example usage with multiple queues and individual routing strategies
env = simpy.Environment()

# Define the queues with different service and arrival distributions, and routing strategies
queue1 = GGCQueue(
    env,
    name="Queue 1",
    num_servers=2,
    service_time_dist=Exponential(rate=3.0),
    inter_arrival_dist=Exponential(rate=2.0),
    routing_strategy=queue1_routing,
)

queue2 = GGCQueue(
    env,
    name="Queue 2",
    num_servers=1,
    service_time_dist=Normal(mean=2.0, stddev=0.5),
    inter_arrival_dist=Exponential(rate=1.5),  # Different arrival rate for Queue 2
    routing_strategy=queue2_routing,
)

# Define a queue system with multiple queues
system = QueueSystem(env, [queue1, queue2])

# Start customer generation for all queues
system.start_customer_generation()

# Run the simulation
simulation_time = 30.0
env.run(until=simulation_time)

# Results: Average waiting time per queue
for queue in system.queues:
    if queue.waiting_times:
        avg_wait_time = np.mean(queue.waiting_times)
        print(f"\nAverage waiting time at {queue.name}: {avg_wait_time:.2f}")
    else:
        print(f"\nNo customers waited at {queue.name}.")
    print(f"Customers served at {queue.name}: {queue.customers_served}")
