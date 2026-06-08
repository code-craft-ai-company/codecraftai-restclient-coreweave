"""
    .. module:: coreweavecluster
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Hand-authored :class:`CoreweaveCluster` data model.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict


class CoreweaveCluster:
    """
        Typed record describing a CoreWeave Kubernetes Service (CKS) cluster.
    """

    def __init__(self, *, id: str, project_id: str, name: str, region: str,
                 k8s_version: str, api_endpoint: str, status: str) -> None:
        """
            Initialize a :class:`CoreweaveCluster`.

            :param id: The server-assigned cluster identifier.
            :param project_id: The owning project identifier.
            :param name: The cluster name.
            :param region: The CoreWeave region the cluster lives in.
            :param k8s_version: The Kubernetes version of the cluster.
            :param api_endpoint: The reachable Kubernetes API-server URL.
            :param status: The cluster lifecycle status string.

            :returns: ``None``.
        """
        self.id = id
        self.project_id = project_id
        self.name = name
        self.region = region
        self.k8s_version = k8s_version
        self.api_endpoint = api_endpoint
        self.status = status
        return

    @classmethod
    def from_payload(cls, *, payload: Dict[str, Any]) -> "CoreweaveCluster":
        """
            Build a :class:`CoreweaveCluster` from an API payload dict.

            :param payload: The decoded API object.

            :returns: A populated :class:`CoreweaveCluster`.
        """
        cluster_id = payload.get("id", "")
        project_id = payload.get("project_id", "")
        name = payload.get("name", "")
        region = payload.get("region", "")
        k8s_version = payload.get("k8s_version", "")
        api_endpoint = payload.get("api_endpoint", "")
        status = payload.get("status", "")

        rtnval = cls(id=cluster_id, project_id=project_id, name=name,
                     region=region, k8s_version=k8s_version,
                     api_endpoint=api_endpoint, status=status)
        return rtnval


__all__ = ["CoreweaveCluster"]
