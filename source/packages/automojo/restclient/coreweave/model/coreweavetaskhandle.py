"""
    .. module:: coreweavetaskhandle
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: :class:`CoreweaveTaskHandle` — an :class:`ITaskHandle`
        implementation for CoreWeave long-running operations.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import os
import time

from typing import Any

from automojo.aspects.aspects import Aspects

from automojo.interfaces.itaskhandle import TaskResult, TaskState

from automojo.restclient.coreweave.aspectscoreweave import (
    AspectsCoreweave, DEFAULT_COREWEAVE_ASPECTS
)
from automojo.restclient.coreweave.model.coreweaveoperationresult import (
    CoreweaveOperationResult
)


_STATE_BY_STATUS = {
    "pending": TaskState.PENDING,
    "queued": TaskState.PENDING,
    "running": TaskState.RUNNING,
    "in_progress": TaskState.RUNNING,
    "succeeded": TaskState.SUCCEEDED,
    "failed": TaskState.FAILED,
    "cancelled": TaskState.CANCELLED,
}


class CoreweaveTaskHandle:
    """
        Synchronous-poll handle on a CoreWeave long-running operation.

        Implements the :class:`automojo.interfaces.itaskhandle.ITaskHandle`
        protocol. The poll loop is driven by the CoreWeave-specific aspects
        (``operation_poll_interval_seconds`` /
        ``operation_poll_timeout_seconds``); a generic :class:`Aspects` is
        accepted on :meth:`wait` to satisfy the protocol surface.
    """

    def __init__(self, *, operation_id: str, operations_group: Any,
                 client_aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> None:
        """
            Initialize a :class:`CoreweaveTaskHandle`.

            :param operation_id: The CoreWeave operation identifier.
            :param operations_group: The :class:`OperationsGroup` used to
                poll operation status.
            :param client_aspects: The CoreWeave aspects supplying the poll
                cadence.

            :returns: ``None``.
        """
        self._operation_id = operation_id
        self._operations_group = operations_group
        self._client_aspects = client_aspects
        self._last_result: CoreweaveOperationResult = CoreweaveOperationResult(
            operation_id=operation_id, status="pending")
        return

    def task_id(self) -> str:
        """
            Return the CoreWeave operation identifier.

            :returns: The operation identifier string.
        """
        rtnval = self._operation_id
        return rtnval

    def is_done(self) -> bool:
        """
            Report whether the last observed operation status is terminal.

            :returns: ``True`` when the operation has reached a terminal
                state.
        """
        rtnval = self._last_result.is_terminal()
        return rtnval

    def cancel(self, *, aspects: Aspects) -> None:
        """
            Request cancellation. The CoreWeave control plane has no
            operation-cancellation endpoint, so this is unsupported.

            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: ``NotImplementedError`` always.
        """
        raise NotImplementedError(
            "CoreWeave operations do not support cancellation.")

    def wait(self, *, aspects: Aspects) -> TaskResult:
        """
            Block until the operation reaches a terminal state or the poll
            timeout elapses.

            The poll cadence is taken from the CoreWeave aspects supplied at
            construction; the generic ``aspects`` argument satisfies the
            :class:`ITaskHandle` protocol.

            :param aspects: Behaviour control for the call.

            :returns: A terminal :class:`TaskResult`.

            :raises: ``TimeoutError`` when the poll timeout elapses without
                a terminal status.
        """
        poll_interval = self._client_aspects.operation_poll_interval_seconds
        poll_timeout = self._client_aspects.operation_poll_timeout_seconds

        start_time = time.time()

        while True:
            result = self._operations_group.get(
                operation_id=self._operation_id,
                aspects=self._client_aspects)
            self._last_result = result

            if result.is_terminal():
                terminal = self._to_task_result(result=result)
                return terminal

            elapsed = time.time() - start_time
            if elapsed >= poll_timeout:
                err_msg_lines = ["Timed out waiting for a CoreWeave operation."]
                err_msg_lines.append("OPERATION: {}".format(self._operation_id))
                err_msg_lines.append("LAST STATUS: {}".format(result.status))
                err_msg = os.linesep.join(err_msg_lines)
                raise TimeoutError(err_msg)

            time.sleep(poll_interval)

    def _to_task_result(self, *,
                        result: CoreweaveOperationResult) -> TaskResult:
        """
            Adapt a :class:`CoreweaveOperationResult` into a typed
            :class:`TaskResult`.

            :param result: The operation result to adapt.

            :returns: A populated :class:`TaskResult`.
        """
        normalized = result.status.lower()
        state = _STATE_BY_STATUS.get(normalized, TaskState.RUNNING)

        error_value = None
        if state == TaskState.FAILED:
            error_value = result.detail

        payload = None
        if result.resource_ref is not None:
            payload = {"resource_ref": result.resource_ref}

        rtnval = TaskResult(task_id=self._operation_id, state=state,
                            progress=0, error=error_value, payload=payload)
        return rtnval


__all__ = ["CoreweaveTaskHandle"]
