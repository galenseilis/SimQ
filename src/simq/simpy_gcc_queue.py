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

# GGCQueue class with dependency-injected distribution objects
class GGCQueue:
    def __init__(self, env, num_servers, inter_arrival_dist, service_time_dist):
        self.env = env
        self.server = simpy.Resource(env, capacity=num_servers)
        self.inter_arrival_dist = inter_arrival_dist  # Inter-arrival distribution object
        self.service_time_dist = service_time_dist  # Service time distribution object
        self.waiting_times = []

    def customer(self, customer_id):
        arrival_time = self.env.now
        print(f"Customer {customer_id} arrived at {arrival_time:.2f}")

        # Request a server
        with self.server.request() as request:
            # Wait for the server to become available
            yield request

            wait_time = self.env.now - arrival_time
            self.waiting_times.append(wait_time)
            print(f"Customer {customer_id} started service after waiting {wait_time:.2f}")

            # Service time is sampled from the distribution class
            service_time = self.service_time_dist.sample(self)
            yield self.env.timeout(service_time)
            print(f"Customer {customer_id} finished service after {service_time:.2f}")

    def generate_customers(self):
        customer_id = 0
        while True:
            # Inter-arrival time is sampled from the distribution class
            inter_arrival_time = self.inter_arrival_dist.sample(self)
            yield self.env.timeout(inter_arrival_time)
            customer_id += 1
            self.env.process(self.customer(customer_id))

# Example usage with distribution classes
num_servers = 3         # Number of servers
simulation_time = 20.0  # Total simulation time

# Setup the environment
env = simpy.Environment()

# Define the distributions
inter_arrival_dist = ExponentialDistribution(rate=2.0)  # Average of 2 arrivals per time unit
service_time_dist = ExponentialDistribution(rate=3.0)   # Average service rate of 3 per time unit

# Setup the queue with injected distribution objects
queue = GGCQueue(env, num_servers, inter_arrival_dist, service_time_dist)
env.process(queue.generate_customers())
env.run(until=simulation_time)

# Results: Average waiting time
if queue.waiting_times:
    avg_wait_time = np.mean(queue.waiting_times)
    print(f"\nAverage waiting time: {avg_wait_time:.2f}")
else:
    print("\nNo customers waited.")

