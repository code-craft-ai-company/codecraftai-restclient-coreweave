"""
    .. module:: coreweavesshkey
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Hand-authored :class:`CoreweaveSshKey` data model.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict


class CoreweaveSshKey:
    """
        Typed record describing an SSH public key registered with a
        CoreWeave project.
    """

    def __init__(self, *, id: str, name: str, fingerprint: str) -> None:
        """
            Initialize a :class:`CoreweaveSshKey`.

            :param id: The server-assigned key identifier.
            :param name: The key name.
            :param fingerprint: The key fingerprint.

            :returns: ``None``.
        """
        self.id = id
        self.name = name
        self.fingerprint = fingerprint
        return

    @classmethod
    def from_payload(cls, *, payload: Dict[str, Any]) -> "CoreweaveSshKey":
        """
            Build a :class:`CoreweaveSshKey` from an API payload dict.

            :param payload: The decoded API object.

            :returns: A populated :class:`CoreweaveSshKey`.
        """
        key_id = payload.get("id", "")
        name = payload.get("name", "")
        fingerprint = payload.get("fingerprint", "")

        rtnval = cls(id=key_id, name=name, fingerprint=fingerprint)
        return rtnval


__all__ = ["CoreweaveSshKey"]
