"""
    .. module:: projectsgroup
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The ``projects`` api group of the CoreWeave client.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List

from automojo.restclient.coreweave.aspectscoreweave import (
    AspectsCoreweave, DEFAULT_COREWEAVE_ASPECTS
)
from automojo.restclient.coreweave.apigroups.groupsupport import collect_paged_items
from automojo.restclient.coreweave.model.coreweaveproject import CoreweaveProject
from automojo.restclient.coreweave.urlcompose import require_identifier


class ProjectsGroup:
    """
        The ``projects`` api group enumerates the projects of an
        organization.
    """

    def __init__(self, *, client: Any) -> None:
        """
            Initialize the api group.

            :param client: The owning :class:`CoreweaveClient`.

            :returns: ``None``.
        """
        self._client = client
        return

    def list(self, *, organization_id: str,
             aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> List[CoreweaveProject]:
        """
            Enumerate the projects scoped to an organization.

            :param organization_id: The owning organization identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`CoreweaveProject` records.

            :raises: :class:`SemanticError` when ``organization_id`` is
                empty or ``None``.
        """
        validated_org = require_identifier(name="organization_id",
                                           value=organization_id)

        def fetch_page(query_params: Dict[str, str]) -> Dict[str, Any]:
            page = self._client.request_json(
                method="GET",
                segments=("v1", "organizations", validated_org, "projects"),
                params=query_params,
                body=None,
                aspects=aspects)
            return page

        item_dicts = collect_paged_items(fetch_page=fetch_page)

        rtnval: List[CoreweaveProject] = []
        for item in item_dicts:
            record = CoreweaveProject.from_payload(payload=item)
            rtnval.append(record)

        return rtnval


__all__ = ["ProjectsGroup"]
