"""
    .. module:: coreweavenodepool
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Hand-authored :class:`CoreweaveNodePool` data model.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict


class CoreweaveNodePool:
    """
        Typed record describing a node pool inside a CoreWeave CKS cluster.
    """

    def __init__(self, *, id: str, cluster_id: str, name: str,
                 gpu_model: str, gpus_per_node: int, node_count: int,
                 interconnect: str) -> None:
        """
            Initialize a :class:`CoreweaveNodePool`.

            :param id: The server-assigned node-pool identifier.
            :param cluster_id: The owning cluster identifier.
            :param name: The node-pool name.
            :param gpu_model: The GPU model offered by the pool (for example
                ``H100_SXM``). An empty string indicates a CPU-only pool.
            :param gpus_per_node: GPU count per node in the pool.
            :param node_count: The number of nodes in the pool.
            :param interconnect: The interconnect topology label
                (for example ``INFINIBAND_NDR`` or ``ETHERNET``).

            :returns: ``None``.
        """
        self.id = id
        self.cluster_id = cluster_id
        self.name = name
        self.gpu_model = gpu_model
        self.gpus_per_node = gpus_per_node
        self.node_count = node_count
        self.interconnect = interconnect
        return

    @classmethod
    def from_payload(cls, *, payload: Dict[str, Any]) -> "CoreweaveNodePool":
        """
            Build a :class:`CoreweaveNodePool` from an API payload dict.

            :param payload: The decoded API object.

            :returns: A populated :class:`CoreweaveNodePool`.
        """
        pool_id = payload.get("id", "")
        cluster_id = payload.get("cluster_id", "")
        name = payload.get("name", "")
        gpu_model = payload.get("gpu_model", "")
        gpus_per_node = payload.get("gpus_per_node", 0)
        node_count = payload.get("node_count", 0)
        interconnect = payload.get("interconnect", "ETHERNET")

        rtnval = cls(id=pool_id, cluster_id=cluster_id, name=name,
                     gpu_model=gpu_model, gpus_per_node=gpus_per_node,
                     node_count=node_count, interconnect=interconnect)
        return rtnval


__all__ = ["CoreweaveNodePool"]
