import simpy
import random
import numpy as np

class MMcQueue:
    def __init__(self, env, arrival_rate, service_rate, num_servers):
        self.env = env
        self.server = simpy.Resource(env, capacity=num_servers)
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
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

            # Service time follows an exponential distribution
            service_time = random.expovariate(self.service_rate)
            yield self.env.timeout(service_time)
            print(f"Customer {customer_id} finished service after {service_time:.2f}")

    def generate_customers(self):
        customer_id = 0
        while True:
            # Inter-arrival time follows an exponential distribution
            inter_arrival_time = random.expovariate(self.arrival_rate)
            yield self.env.timeout(inter_arrival_time)
            customer_id += 1
            self.env.process(self.customer(customer_id))

# Parameters
arrival_rate = 2.0      # Average arrivals per time unit
service_rate = 3.0      # Average service rate per server
num_servers = 3         # Number of servers
simulation_time = 20.0  # Total simulation time

# Setup and run the simulation
env = simpy.Environment()
queue = MMcQueue(env, arrival_rate, service_rate, num_servers)
env.process(queue.generate_customers())
env.run(until=simulation_time)

# Results: Average waiting time
if queue.waiting_times:
    avg_wait_time = np.mean(queue.waiting_times)
    print(f"\nAverage waiting time: {avg_wait_time:.2f}")
else:
    print("\nNo customers waited.")

