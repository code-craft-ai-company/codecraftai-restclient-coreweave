"""
    .. module:: organizationsgroup
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The ``organizations`` api group of the CoreWeave client.

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
from automojo.restclient.coreweave.model.coreweaveorganization import (
    CoreweaveOrganization
)


class OrganizationsGroup:
    """
        The ``organizations`` api group enumerates the organizations the
        supplied credential can see.
    """

    def __init__(self, *, client: Any) -> None:
        """
            Initialize the api group.

            :param client: The owning :class:`CoreweaveClient`.

            :returns: ``None``.
        """
        self._client = client
        return

    def list(self, *,
             aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> List[CoreweaveOrganization]:
        """
            Enumerate the organizations visible to the credential.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`CoreweaveOrganization` records.
        """
        def fetch_page(query_params: Dict[str, str]) -> Dict[str, Any]:
            page = self._client.request_json(method="GET",
                                             segments=("v1", "organizations"),
                                             params=query_params,
                                             body=None,
                                             aspects=aspects)
            return page

        item_dicts = collect_paged_items(fetch_page=fetch_page)

        rtnval: List[CoreweaveOrganization] = []
        for item in item_dicts:
            record = CoreweaveOrganization.from_payload(payload=item)
            rtnval.append(record)

        return rtnval


__all__ = ["OrganizationsGroup"]
