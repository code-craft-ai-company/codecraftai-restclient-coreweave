"""
    .. module:: clustersgroup
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The ``clusters`` api group of the CoreWeave client.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List

from ccai.restclient.coreweave.aspectscoreweave import (
    AspectsCoreweave, DEFAULT_COREWEAVE_ASPECTS
)
from ccai.restclient.coreweave.apigroups.groupsupport import collect_paged_items
from ccai.restclient.coreweave.model.coreweavecluster import CoreweaveCluster
from ccai.restclient.coreweave.urlcompose import require_identifier


class ClustersGroup:
    """
        The ``clusters`` api group enumerates and reads CoreWeave Kubernetes
        Service (CKS) clusters.
    """

    def __init__(self, *, client: Any) -> None:
        """
            Initialize the api group.

            :param client: The owning :class:`CoreweaveClient`.

            :returns: ``None``.
        """
        self._client = client
        return

    def list(self, *, project_id: str,
             aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> List[CoreweaveCluster]:
        """
            Enumerate the CKS clusters of a project.

            :param project_id: The owning project identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`CoreweaveCluster` records.

            :raises: :class:`SemanticError` when ``project_id`` is empty or
                ``None``.
        """
        validated_project = require_identifier(name="project_id",
                                                value=project_id)

        def fetch_page(query_params: Dict[str, str]) -> Dict[str, Any]:
            page = self._client.request_json(
                method="GET",
                segments=("v1", "projects", validated_project, "clusters"),
                params=query_params,
                body=None,
                aspects=aspects)
            return page

        item_dicts = collect_paged_items(fetch_page=fetch_page)

        rtnval: List[CoreweaveCluster] = []
        for item in item_dicts:
            record = CoreweaveCluster.from_payload(payload=item)
            rtnval.append(record)

        return rtnval

    def get(self, *, cluster_id: str,
            aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> CoreweaveCluster:
        """
            Read a single CKS cluster by identifier.

            :param cluster_id: The cluster identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CoreweaveCluster` record.

            :raises: :class:`SemanticError` when ``cluster_id`` is empty or
                ``None``.
        """
        validated_cluster = require_identifier(name="cluster_id",
                                                value=cluster_id)

        payload = self._client.request_json(
            method="GET",
            segments=("v1", "clusters", validated_cluster),
            params=None,
            body=None,
            aspects=aspects)

        rtnval = CoreweaveCluster.from_payload(payload=payload)
        return rtnval


__all__ = ["ClustersGroup"]
