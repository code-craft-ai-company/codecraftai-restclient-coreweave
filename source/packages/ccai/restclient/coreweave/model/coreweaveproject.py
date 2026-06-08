"""
    .. module:: coreweaveproject
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Hand-authored :class:`CoreweaveProject` data model.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, Optional


class CoreweaveProject:
    """
        Typed record describing a CoreWeave project.
    """

    def __init__(self, *, id: str, organization_id: str, slug: str,
                 region_defaults: Optional[Dict[str, Any]] = None) -> None:
        """
            Initialize a :class:`CoreweaveProject`.

            :param id: The server-assigned project identifier.
            :param organization_id: The owning organization identifier.
            :param slug: The project slug.
            :param region_defaults: Optional default-region settings dict.

            :returns: ``None``.
        """
        self.id = id
        self.organization_id = organization_id
        self.slug = slug
        self.region_defaults = region_defaults if region_defaults is not None else {}
        return

    @classmethod
    def from_payload(cls, *, payload: Dict[str, Any]) -> "CoreweaveProject":
        """
            Build a :class:`CoreweaveProject` from an API payload dict.

            :param payload: The decoded API object.

            :returns: A populated :class:`CoreweaveProject`.
        """
        project_id = payload.get("id", "")
        organization_id = payload.get("organization_id", "")
        slug = payload.get("slug", "")
        region_defaults = payload.get("region_defaults", None)

        rtnval = cls(id=project_id, organization_id=organization_id,
                     slug=slug, region_defaults=region_defaults)
        return rtnval


__all__ = ["CoreweaveProject"]
