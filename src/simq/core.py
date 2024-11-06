from __future__ import annotations

from collections.abc import Generator
from typing import Any, Callable, Self

import simpy

from simdist import dists


class Node:
    def __init__(
        self,
        env: simpy.Environment,
        name: str,
        num_servers: int,
        service_time_dist: dists.Distribution,
        inter_arrival_dist: dists.Distribution,
        routing_strategy: Callable[[int, Self, Network], Generator[Any, Any, Any] | None] | None = None,
    ):
        self.env: simpy.Environment = env
        self.name: str = name
        self.server: simpy.Resource = simpy.Resource(env, capacity=num_servers)
        self.service_time_dist: dists.Distribution = service_time_dist
        self.inter_arrival_dist: dists.Distribution = inter_arrival_dist
        # FIX: routing_strategy type annotation.
        self.routing_strategy: (
            Callable[[int, Self, Network], Generator[Any, Any, Any] | None] | None
        ) = routing_strategy

    def _log_arrival(self, customer_id: int, network: Network) -> None:
        """Log the arrival of a customer at the node."""
        arrival_time: float = self.env.now
        arrival_log_entry: dict[str, Any] = {
            "customer": customer_id,
            "action": "arrival",
            "node": self.name,
            "time": arrival_time,
        }

        network.log(arrival_log_entry)

    def _log_service_start(self, customer_id: int, network: Network) -> None:
        """Log the start of a customer's service."""
        log_entry = {
            "customer": customer_id,
            "action": "service_start",
            "node": self.name,
            "time": self.env.now,
        }
        network.log(log_entry)

    def _log_service_finish(self, customer_id: int, network: Network) -> None:
        """Log the completion of serving a customer."""
        log_entry = {
            "customer": customer_id,
            "action": "service_finish",
            "node": self.name,
            "time": self.env.now,
        }
        network.log(log_entry)

    def _log_customer_leaving(self, customer_id: int, network: Network) -> None:
        log_entry: dict[str, Any] = {
            "customer": customer_id,
            "action": "leave_system",
            "node": self.name,
            "time": self.env.now,
        }
        network.log(log_entry)

    # TODO: Refactor for different processes to be separate methods.
    # WARN: Not convinced that `Generator[Any, Any, Any]` is the most specific type we could use.
    def service(self, customer_id: int, network: Network) -> Generator[Any, Any, Any]:
        """Service a customer."""
        self._log_arrival(customer_id, network)

        # Request a server
        with self.server.request() as request:
            yield request

            self._log_service_start(customer_id, network)

            # Service time is sampled from the distribution
            service_time: float = self.service_time_dist.sample({"node": self})
            yield self.env.timeout(delay=service_time)

            # Decide the next action based on routing strategy
            if self.routing_strategy:
                route_event = self.routing_strategy(customer_id, self, network)
                if route_event is not None:
                    yield self.env.process(route_event)
            else:
                self._log_customer_leaving(customer_id, network)

    def generate_customers(self, network: Network) -> Generator[Any, Any, Any]:
        """Generate customers for this queue based on its inter-arrival time distribution."""

        while True:
            inter_arrival_time: float = self.inter_arrival_dist.sample({"node": self})
            yield self.env.timeout(inter_arrival_time)

            # Get a new unique customer_id from the queue system
            customer_id: int = network.get_next_customer_id()
            _ = self.env.process(self.service(customer_id, network))


class Network:
    """Network system manages multiple nodes and tracks customer IDs"""

    def __init__(self, env: simpy.Environment, nodes: list[Node]):
        self.env: simpy.Environment = env
        self.nodes: list[Node] = nodes
        self.customer_id_counter: int = 0
        self.event_log: list[dict[str, Any]] = []

    def start_customer_generation(self) -> None:
        """Start customer generation for each queue"""
        for node in self.nodes:
            _ = self.env.process(node.generate_customers(self))

    def get_next_customer_id(self) -> int:
        """Increment the customer ID counter and return the next unique ID"""
        self.customer_id_counter += 1
        return self.customer_id_counter

    def log(self, log_entry: dict[str, Any]) -> None:
        self.event_log.append(log_entry)
