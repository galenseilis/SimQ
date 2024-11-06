"""Routing functions and related utilities related to routing."""

from collections.abc import Generator
from typing import Any
from .core import Node, Network

# TODO: Routing class?


def leave_router(customer_id: int, node: Node, network: Network) -> None:
    """Route to leave the network."""
    network.log(
        {
            "customer": customer_id,
            "action": "routing",
            "node": node.name,
            "destination": "exit",
        }
    )


# TODO: Implement probability distribution option.
# TODO: Develop and import discrete uniform probability distribution for simdist.
def probability_router(
    customer_id: int, node: Node, network: Network, probs: list[str]
) -> Generator[Any, Any, Any] | None: ...



