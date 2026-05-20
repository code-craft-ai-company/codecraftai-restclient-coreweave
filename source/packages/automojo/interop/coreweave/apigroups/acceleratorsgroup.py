"""
    .. module:: acceleratorsgroup
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The ``accelerators`` api group of the CoreWeave client.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import os

from typing import Any, Dict, List

from automojo.interop.coreweave.aspectscoreweave import (
    AspectsCoreweave, DEFAULT_COREWEAVE_ASPECTS
)
from automojo.interop.coreweave.apigroups.groupsupport import collect_paged_items
from automojo.interop.coreweave.exceptions.coreweaveerrors import (
    CoreweaveAcceleratorNotAvailableError
)
from automojo.interop.coreweave.model.coreweaveacceleratorsku import (
    CoreweaveAcceleratorSku
)
from automojo.interop.coreweave.urlcompose import require_identifier


class AcceleratorsGroup:
    """
        The ``accelerators`` api group enumerates the GPU SKU catalog of a
        CoreWeave project.
    """

    def __init__(self, *, client: Any) -> None:
        """
            Initialize the api group.

            :param client: The owning :class:`CoreweaveClient`.

            :returns: ``None``.
        """
        self._client = client
        return

    def list_skus(self, *, project_id: str,
                  aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> List[CoreweaveAcceleratorSku]:
        """
            Enumerate the GPU SKU catalog of a project.

            :param project_id: The owning project identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`CoreweaveAcceleratorSku` records.

            :raises: :class:`SemanticError` when ``project_id`` is empty or
                ``None``.
        """
        validated_project = require_identifier(name="project_id",
                                                value=project_id)

        def fetch_page(query_params: Dict[str, str]) -> Dict[str, Any]:
            page = self._client.request_json(
                method="GET",
                segments=("v1", "projects", validated_project,
                          "accelerator-skus"),
                params=query_params,
                body=None,
                aspects=aspects)
            return page

        item_dicts = collect_paged_items(fetch_page=fetch_page)

        rtnval: List[CoreweaveAcceleratorSku] = []
        for item in item_dicts:
            record = CoreweaveAcceleratorSku.from_payload(payload=item)
            rtnval.append(record)

        return rtnval

    def require_sku(self, *, project_id: str, sku_name: str,
                    aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> CoreweaveAcceleratorSku:
        """
            Resolve a single SKU by name, failing loudly when absent.

            :param project_id: The owning project identifier.
            :param sku_name: The catalog SKU name to resolve.
            :param aspects: Behaviour control for the call.

            :returns: The matching :class:`CoreweaveAcceleratorSku`.

            :raises: :class:`CoreweaveAcceleratorNotAvailableError` when the
                SKU is not present in the project catalog.
        """
        catalog = self.list_skus(project_id=project_id, aspects=aspects)

        for sku in catalog:
            if sku.name == sku_name:
                rtnval = sku
                return rtnval

        err_msg_lines = ["The requested accelerator SKU is not available."]
        err_msg_lines.append("SKU: {}".format(sku_name))
        err_msg_lines.append("PROJECT: {}".format(project_id))
        err_msg_lines.append("CATALOG: ({})".format(len(catalog)))
        for sku in catalog:
            err_msg_lines.append("    {}".format(sku.name))
        err_msg = os.linesep.join(err_msg_lines)
        raise CoreweaveAcceleratorNotAvailableError(err_msg)


__all__ = ["AcceleratorsGroup"]
