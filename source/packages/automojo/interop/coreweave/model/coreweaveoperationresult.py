"""
    .. module:: coreweaveoperationresult
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Hand-authored :class:`CoreweaveOperationResult` data model.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Optional


TERMINAL_STATUSES = ("succeeded", "failed", "cancelled")


class CoreweaveOperationResult:
    """
        Typed record describing the status of a long-running CoreWeave
        control-plane operation.
    """

    def __init__(self, *, operation_id: str, status: str,
                 resource_ref: Optional[str] = None,
                 detail: Optional[str] = None) -> None:
        """
            Initialize a :class:`CoreweaveOperationResult`.

            :param operation_id: The server-assigned operation identifier.
            :param status: The operation status string.
            :param resource_ref: Optional reference to the operated resource.
            :param detail: Optional detail / error message.

            :returns: ``None``.
        """
        self.operation_id = operation_id
        self.status = status
        self.resource_ref = resource_ref
        self.detail = detail
        return

    def is_terminal(self) -> bool:
        """
            Report whether the operation has reached a terminal status.

            :returns: ``True`` when the status is terminal.
        """
        normalized = self.status.lower()
        rtnval = normalized in TERMINAL_STATUSES
        return rtnval

    @classmethod
    def from_payload(cls, *, payload: Dict[str, Any]) -> "CoreweaveOperationResult":
        """
            Build a :class:`CoreweaveOperationResult` from an API payload.

            :param payload: The decoded API object.

            :returns: A populated :class:`CoreweaveOperationResult`.
        """
        operation_id = payload.get("operation_id", "")
        if operation_id == "":
            operation_id = payload.get("id", "")
        status = payload.get("status", "")
        resource_ref = payload.get("resource_ref", None)
        detail = payload.get("detail", None)

        rtnval = cls(operation_id=operation_id, status=status,
                     resource_ref=resource_ref, detail=detail)
        return rtnval


__all__ = ["CoreweaveOperationResult", "TERMINAL_STATUSES"]
