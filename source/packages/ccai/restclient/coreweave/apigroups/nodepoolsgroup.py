"""
    .. module:: nodepoolsgroup
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The ``node-pools`` api group of the CoreWeave client.

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
from ccai.restclient.coreweave.model.coreweavenodepool import CoreweaveNodePool
from ccai.restclient.coreweave.urlcompose import require_identifier


class NodePoolsGroup:
    """
        The ``node-pools`` api group enumerates the node pools (including
        accelerator pools) of a CKS cluster.
    """

    def __init__(self, *, client: Any) -> None:
        """
            Initialize the api group.

            :param client: The owning :class:`CoreweaveClient`.

            :returns: ``None``.
        """
        self._client = client
        return

    def list(self, *, cluster_id: str,
             aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> List[CoreweaveNodePool]:
        """
            Enumerate the node pools of a CKS cluster.

            :param cluster_id: The owning cluster identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`CoreweaveNodePool` records.

            :raises: :class:`SemanticError` when ``cluster_id`` is empty or
                ``None``.
        """
        validated_cluster = require_identifier(name="cluster_id",
                                                value=cluster_id)

        def fetch_page(query_params: Dict[str, str]) -> Dict[str, Any]:
            page = self._client.request_json(
                method="GET",
                segments=("v1", "clusters", validated_cluster, "node-pools"),
                params=query_params,
                body=None,
                aspects=aspects)
            return page

        item_dicts = collect_paged_items(fetch_page=fetch_page)

        rtnval: List[CoreweaveNodePool] = []
        for item in item_dicts:
            record = CoreweaveNodePool.from_payload(payload=item)
            rtnval.append(record)

        return rtnval


__all__ = ["NodePoolsGroup"]
