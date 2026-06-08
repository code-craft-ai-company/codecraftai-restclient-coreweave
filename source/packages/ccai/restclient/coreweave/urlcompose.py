"""
    .. module:: urlcompose
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Total, unambiguous URL-path composition for the CoreWeave
        client. Each identifier segment is independently percent-encoded;
        an empty or ``None`` segment is rejected with :class:`SemanticError`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import os

from typing import Optional, Tuple
from urllib.parse import quote

from ccai.errors.exceptions import SemanticError


def compose_leaf(*, segments: Tuple[str, ...]) -> str:
    """
        Compose an API leaf path from a tuple of path segments.

        Every segment is percent-encoded independently so that an embedded
        ``/`` inside an identifier cannot silently create extra path
        components. The composed leaf is a deterministic function of the
        supplied segments.

        :param segments: The ordered path segments. Each must be a non-empty
            string.

        :returns: The composed leaf path beginning with ``/``.

        :raises: :class:`SemanticError` when any segment is empty or
            ``None``.
    """
    if segments is None:
        raise SemanticError("'segments' must be a tuple of path segments.")

    if len(segments) == 0:
        raise SemanticError("'segments' must contain at least one segment.")

    encoded_parts = []
    for index in range(0, len(segments)):
        segment = segments[index]

        if segment is None:
            err_msg_lines = ["A URL path segment was None."]
            err_msg_lines.append("SEGMENT INDEX: {}".format(index))
            err_msg_lines.append("SEGMENTS: {}".format(segments))
            err_msg = os.linesep.join(err_msg_lines)
            raise SemanticError(err_msg)

        if len(segment) == 0:
            err_msg_lines = ["A URL path segment was empty."]
            err_msg_lines.append("SEGMENT INDEX: {}".format(index))
            err_msg_lines.append("SEGMENTS: {}".format(segments))
            err_msg = os.linesep.join(err_msg_lines)
            raise SemanticError(err_msg)

        encoded = quote(segment, safe="")
        encoded_parts.append(encoded)

    rtnval = "/" + "/".join(encoded_parts)
    return rtnval


def require_identifier(*, name: str, value: Optional[str]) -> str:
    """
        Validate that a single identifier argument is a non-empty string.

        :param name: The argument name (for error messages).
        :param value: The identifier value to validate.

        :returns: The validated identifier value.

        :raises: :class:`SemanticError` when the identifier is empty or
            ``None``.
    """
    if value is None:
        raise SemanticError("'{}' must be a non-empty identifier.".format(name))

    if len(value) == 0:
        raise SemanticError("'{}' must be a non-empty identifier.".format(name))

    rtnval = value
    return rtnval


__all__ = ["compose_leaf", "require_identifier"]
