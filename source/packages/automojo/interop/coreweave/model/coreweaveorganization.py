"""
    .. module:: coreweaveorganization
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Hand-authored :class:`CoreweaveOrganization` data model.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional


class CoreweaveOrganization:
    """
        Typed record describing a CoreWeave organization.
    """

    def __init__(self, *, id: str, slug: str, name: str,
                 tags: Optional[List[Dict[str, str]]] = None) -> None:
        """
            Initialize a :class:`CoreweaveOrganization`.

            :param id: The server-assigned organization identifier.
            :param slug: The organization slug.
            :param name: The human-readable organization name.
            :param tags: Optional neutral tag list.

            :returns: ``None``.
        """
        self.id = id
        self.slug = slug
        self.name = name
        self.tags = tags if tags is not None else []
        return

    @classmethod
    def from_payload(cls, *, payload: Dict[str, Any]) -> "CoreweaveOrganization":
        """
            Build a :class:`CoreweaveOrganization` from an API payload dict.

            :param payload: The decoded API object.

            :returns: A populated :class:`CoreweaveOrganization`.
        """
        org_id = payload.get("id", "")
        slug = payload.get("slug", "")
        name = payload.get("name", "")
        tags = payload.get("tags", None)

        rtnval = cls(id=org_id, slug=slug, name=name, tags=tags)
        return rtnval


__all__ = ["CoreweaveOrganization"]
