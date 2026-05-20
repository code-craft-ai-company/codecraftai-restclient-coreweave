"""
    .. module:: tagsgroup
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The ``tags`` api group of the CoreWeave client.

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
from automojo.interop.coreweave.exceptions.coreweaveerrors import (
    CoreweaveTaggingNotSupportedError
)
from automojo.interop.coreweave.urlcompose import require_identifier


# Resource types the CoreWeave control plane supports tagging on.
TAGGABLE_RESOURCE_TYPES = ("clusters", "projects", "object-namespaces")


class TagsGroup:
    """
        The ``tags`` api group attaches neutral key/value tags to cloud
        resources.
    """

    def __init__(self, *, client: Any) -> None:
        """
            Initialize the api group.

            :param client: The owning :class:`CoreweaveClient`.

            :returns: ``None``.
        """
        self._client = client
        return

    def apply(self, *, resource_type: str, resource_id: str,
              tags: List[Dict[str, str]],
              aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> None:
        """
            Apply a neutral tag set to a cloud resource.

            The neutral tag form — a list of single-entry dicts — is
            translated to CoreWeave's flat tagging payload internally.

            :param resource_type: The resource type (for example
                ``clusters``).
            :param resource_id: The resource identifier.
            :param tags: The neutral tag list (single-entry dicts).
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`SemanticError` when ``resource_type`` or
                ``resource_id`` is empty.
            :raises: :class:`CoreweaveTaggingNotSupportedError` when the
                resource type does not support tagging.
        """
        validated_type = require_identifier(name="resource_type",
                                             value=resource_type)
        validated_id = require_identifier(name="resource_id",
                                          value=resource_id)

        if validated_type not in TAGGABLE_RESOURCE_TYPES:
            err_msg_lines = ["The resource type does not support tagging."]
            err_msg_lines.append("RESOURCE TYPE: {}".format(validated_type))
            err_msg_lines.append("SUPPORTED: ({})".format(
                len(TAGGABLE_RESOURCE_TYPES)))
            for entry in TAGGABLE_RESOURCE_TYPES:
                err_msg_lines.append("    {}".format(entry))
            err_msg = os.linesep.join(err_msg_lines)
            raise CoreweaveTaggingNotSupportedError(err_msg)

        flat_tags: Dict[str, str] = {}
        for entry in tags:
            for key, value in entry.items():
                flat_tags[key] = value

        body = {"tags": flat_tags}

        self._client.request_json(
            method="PATCH",
            segments=("v1", validated_type, validated_id, "tags"),
            params=None,
            body=body,
            aspects=aspects)

        return


__all__ = ["TagsGroup", "TAGGABLE_RESOURCE_TYPES"]
