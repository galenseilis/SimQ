import simpy
import numpy as np
from abc import ABC, abstractmethod

# Abstract base class for distributions
class Distribution(ABC):
    @abstractmethod
    def sample(self, queue):
        pass

# Exponential distribution class
class ExponentialDistribution(Distribution):
    def __init__(self, rate):
        self.rate = rate

    def sample(self, queue):
        return np.random.exponential(1 / self.rate)

# Normal distribution class
class NormalDistribution(Distribution):
    def __init__(self, mean, stddev):
        self.mean = mean
        self.stddev = stddev

    def sample(self, queue):
        return np.random.normal(self.mean, self.stddev)

# Queue class with its own routing logic and arrival process
class GGCQueue:
    def __init__(self, env, name, num_servers, service_time_dist, inter_arrival_dist, routing_strategy=None):
        self.env = env
        self.name = name
        self.server = simpy.Resource(env, capacity=num_servers)
        self.service_time_dist = service_time_dist  # Service time distribution
        self.inter_arrival_dist = inter_arrival_dist  # Inter-arrival time distribution
        self.routing_strategy = routing_strategy  # Routing function to decide next step
        self.waiting_times = []
        self.customers_served = 0

    def customer(self, customer_id, queue_system):
        arrival_time = self.env.now
        print(f"Customer {customer_id} arrived at {arrival_time:.2f} at queue {self.name}")

        # Request a server
        with self.server.request() as request:
            yield request

            wait_time = self.env.now - arrival_time
            self.waiting_times.append(wait_time)
            print(f"Customer {customer_id} started service after waiting {wait_time:.2f} at queue {self.name}")

            # Service time is sampled from the distribution
            service_time = self.service_time_dist.sample(self)
            yield self.env.timeout(service_time)

            print(f"Customer {customer_id} finished service after {service_time:.2f} at queue {self.name}")
            self.customers_served += 1

            # Decide the next action based on routing strategy
            if self.routing_strategy:
                yield self.env.process(self.routing_strategy(customer_id, self, queue_system))
            else:
                print(f"Customer {customer_id} leaves the system after {self.name}.")

    def generate_customers(self, queue_system):
        while True:
            # Generate customers for this queue based on its inter-arrival time distribution
            inter_arrival_time = self.inter_arrival_dist.sample(self)
            yield self.env.timeout(inter_arrival_time)

            # Get a new unique customer_id from the queue system
            customer_id = queue_system.get_next_customer_id()
            self.env.process(self.customer(customer_id, queue_system))

# Queue system manages multiple queues and tracks customer IDs
class QueueSystem:
    def __init__(self, env, queues):
        self.env = env
        self.queues = queues  # List of queues
        self.customer_id_counter = 0  # Centralized customer ID counter

    def start_customer_generation(self):
        # Start customer generation for each queue
        for queue in self.queues:
            self.env.process(queue.generate_customers(self))

    def get_next_customer_id(self):
        # Increment the customer ID counter and return the next unique ID
        self.customer_id_counter += 1
        return self.customer_id_counter

# Example routing strategies for individual queues

# After Queue 1, 50% chance to go to Queue 2, or leave the system
def queue1_routing(customer_id, current_queue, queue_system):
    if np.random.rand() < 0.5:
        print(f"Customer {customer_id} is routed from {current_queue.name} to Queue 2.")
        yield queue_system.env.process(queue_system.queues[1].customer(customer_id, queue_system))
    else:
        print(f"Customer {customer_id} leaves the system after {current_queue.name}.")

# After Queue 2, customer always leaves the system
def queue2_routing(customer_id, current_queue, queue_system):
    print(f"Customer {customer_id} leaves the system after {current_queue.name}.")

# Example usage with multiple queues and individual routing strategies
env = simpy.Environment()

# Define the queues with different service and arrival distributions, and routing strategies
queue1 = GGCQueue(
    env,
    name="Queue 1",
    num_servers=2,
    service_time_dist=ExponentialDistribution(rate=3.0),
    inter_arrival_dist=ExponentialDistribution(rate=2.0),
    routing_strategy=queue1_routing
)

queue2 = GGCQueue(
    env,
    name="Queue 2",
    num_servers=1,
    service_time_dist=NormalDistribution(mean=2.0, stddev=0.5),
    inter_arrival_dist=ExponentialDistribution(rate=1.5),  # Different arrival rate for Queue 2
    routing_strategy=queue2_routing
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

