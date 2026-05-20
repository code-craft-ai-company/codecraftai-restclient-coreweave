"""
    .. module:: operationsgroup
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The ``operations`` api group of the CoreWeave client.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any

from automojo.interop.coreweave.aspectscoreweave import (
    AspectsCoreweave, DEFAULT_COREWEAVE_ASPECTS
)
from automojo.interop.coreweave.model.coreweaveoperationresult import (
    CoreweaveOperationResult
)
from automojo.interop.coreweave.urlcompose import require_identifier


class OperationsGroup:
    """
        The ``operations`` api group reads the status of long-running
        CoreWeave control-plane operations. It backs
        :class:`CoreweaveTaskHandle.wait`.
    """

    def __init__(self, *, client: Any) -> None:
        """
            Initialize the api group.

            :param client: The owning :class:`CoreweaveClient`.

            :returns: ``None``.
        """
        self._client = client
        return

    def get(self, *, operation_id: str,
            aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> CoreweaveOperationResult:
        """
            Read the status of a long-running operation.

            :param operation_id: The operation identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CoreweaveOperationResult`.

            :raises: :class:`SemanticError` when ``operation_id`` is empty.
        """
        validated_operation = require_identifier(name="operation_id",
                                                  value=operation_id)

        payload = self._client.request_json(
            method="GET",
            segments=("v1", "operations", validated_operation),
            params=None,
            body=None,
            aspects=aspects)

        rtnval = CoreweaveOperationResult.from_payload(payload=payload)
        return rtnval


__all__ = ["OperationsGroup"]
