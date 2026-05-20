"""
    .. module:: sshkeysgroup
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The ``ssh-keys`` api group of the CoreWeave client.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List

from automojo.errors.exceptions import HttpNotFoundError

from automojo.restclient.coreweave.aspectscoreweave import (
    AspectsCoreweave, DEFAULT_COREWEAVE_ASPECTS
)
from automojo.restclient.coreweave.apigroups.groupsupport import collect_paged_items
from automojo.restclient.coreweave.model.coreweavesshkey import CoreweaveSshKey
from automojo.restclient.coreweave.urlcompose import require_identifier


class SshKeysGroup:
    """
        The ``ssh-keys`` api group registers and removes SSH public keys on a
        CoreWeave project. Registration is idempotent (read-before-create);
        deletion is idempotent (no-op on absent).
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
             aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> List[CoreweaveSshKey]:
        """
            Enumerate the SSH keys registered with the active project.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`CoreweaveSshKey` records.
        """
        def fetch_page(query_params: Dict[str, str]) -> Dict[str, Any]:
            page = self._client.request_json(method="GET",
                                             segments=("v1", "ssh-keys"),
                                             params=query_params,
                                             body=None,
                                             aspects=aspects)
            return page

        item_dicts = collect_paged_items(fetch_page=fetch_page)

        rtnval: List[CoreweaveSshKey] = []
        for item in item_dicts:
            record = CoreweaveSshKey.from_payload(payload=item)
            rtnval.append(record)

        return rtnval

    def register(self, *, name: str, public_key: str,
                 aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> CoreweaveSshKey:
        """
            Register an SSH public key with the active project.

            The call is idempotent: when a key with the same name already
            exists the existing record is returned without creating a
            duplicate.

            :param name: The key name.
            :param public_key: The SSH public-key material.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CoreweaveSshKey` record.

            :raises: :class:`SemanticError` when ``name`` is empty.
        """
        validated_name = require_identifier(name="name", value=name)

        existing_keys = self.list(aspects=aspects)
        for key in existing_keys:
            if key.name == validated_name:
                rtnval = key
                return rtnval

        body = {"name": validated_name, "public_key": public_key}

        payload = self._client.request_json(method="POST",
                                            segments=("v1", "ssh-keys"),
                                            params=None,
                                            body=body,
                                            aspects=aspects)

        rtnval = CoreweaveSshKey.from_payload(payload=payload)
        return rtnval

    def delete(self, *, key_id: str,
               aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> None:
        """
            Delete an SSH key. An unknown key id is treated as success
            (idempotent delete).

            :param key_id: The server-assigned key identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`SemanticError` when ``key_id`` is empty.
        """
        validated_id = require_identifier(name="key_id", value=key_id)

        try:
            self._client.request_json(method="DELETE",
                                      segments=("v1", "ssh-keys", validated_id),
                                      params=None,
                                      body=None,
                                      aspects=aspects)
        except HttpNotFoundError:
            # An unknown key id is treated as already removed.
            return

        return


__all__ = ["SshKeysGroup"]
