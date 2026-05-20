"""
    .. module:: coreweaveobjectnamespace
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Hand-authored :class:`CoreweaveObjectNamespace` data model.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict


class CoreweaveObjectNamespace:
    """
        Typed record describing a CoreWeave object-storage namespace.
    """

    def __init__(self, *, id: str, name: str, region: str,
                 endpoint_url: str) -> None:
        """
            Initialize a :class:`CoreweaveObjectNamespace`.

            :param id: The server-assigned namespace identifier.
            :param name: The namespace name.
            :param region: The region the namespace lives in.
            :param endpoint_url: The S3-compatible endpoint URL.

            :returns: ``None``.
        """
        self.id = id
        self.name = name
        self.region = region
        self.endpoint_url = endpoint_url
        return

    @classmethod
    def from_payload(cls, *, payload: Dict[str, Any]) -> "CoreweaveObjectNamespace":
        """
            Build a :class:`CoreweaveObjectNamespace` from an API payload dict.

            :param payload: The decoded API object.

            :returns: A populated :class:`CoreweaveObjectNamespace`.
        """
        namespace_id = payload.get("id", "")
        name = payload.get("name", "")
        region = payload.get("region", "")
        endpoint_url = payload.get("endpoint_url", "")

        rtnval = cls(id=namespace_id, name=name, region=region,
                     endpoint_url=endpoint_url)
        return rtnval


__all__ = ["CoreweaveObjectNamespace"]
