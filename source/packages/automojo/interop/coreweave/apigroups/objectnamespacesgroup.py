"""
    .. module:: objectnamespacesgroup
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The ``object-namespaces`` api group of the CoreWeave client.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List

from automojo.interop.coreweave.aspectscoreweave import (
    AspectsCoreweave, DEFAULT_COREWEAVE_ASPECTS
)
from automojo.interop.coreweave.apigroups.groupsupport import collect_paged_items
from automojo.interop.coreweave.model.coreweaveobjectnamespace import (
    CoreweaveObjectNamespace
)
from automojo.interop.coreweave.urlcompose import require_identifier


class ObjectNamespacesGroup:
    """
        The ``object-namespaces`` api group creates and lists CoreWeave
        object-storage namespaces. Creation is idempotent
        (read-before-create on name + region).
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
             aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> List[CoreweaveObjectNamespace]:
        """
            Enumerate the object-storage namespaces of a project.

            :param project_id: The owning project identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`CoreweaveObjectNamespace` records.

            :raises: :class:`SemanticError` when ``project_id`` is empty.
        """
        validated_project = require_identifier(name="project_id",
                                                value=project_id)

        def fetch_page(query_params: Dict[str, str]) -> Dict[str, Any]:
            page = self._client.request_json(
                method="GET",
                segments=("v1", "projects", validated_project,
                          "object-namespaces"),
                params=query_params,
                body=None,
                aspects=aspects)
            return page

        item_dicts = collect_paged_items(fetch_page=fetch_page)

        rtnval: List[CoreweaveObjectNamespace] = []
        for item in item_dicts:
            record = CoreweaveObjectNamespace.from_payload(payload=item)
            rtnval.append(record)

        return rtnval

    def create(self, *, project_id: str, name: str, region: str,
               aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> CoreweaveObjectNamespace:
        """
            Create an object-storage namespace.

            The call is idempotent: when a namespace with the same name in
            the same region already exists the existing record is returned.

            :param project_id: The owning project identifier.
            :param name: The namespace name.
            :param region: The region the namespace should live in.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CoreweaveObjectNamespace` record.

            :raises: :class:`SemanticError` when ``project_id`` or ``name``
                is empty.
        """
        validated_project = require_identifier(name="project_id",
                                                value=project_id)
        validated_name = require_identifier(name="name", value=name)

        existing = self.list(project_id=validated_project, aspects=aspects)
        for namespace in existing:
            if namespace.name == validated_name and namespace.region == region:
                rtnval = namespace
                return rtnval

        body = {"name": validated_name, "region": region}

        payload = self._client.request_json(
            method="POST",
            segments=("v1", "projects", validated_project, "object-namespaces"),
            params=None,
            body=body,
            aspects=aspects)

        rtnval = CoreweaveObjectNamespace.from_payload(payload=payload)
        return rtnval


__all__ = ["ObjectNamespacesGroup"]
