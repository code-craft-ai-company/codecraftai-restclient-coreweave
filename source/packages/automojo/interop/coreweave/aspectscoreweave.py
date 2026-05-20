"""
    .. module:: aspectscoreweave
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that contains the :class:`AspectsCoreweave` class used
        to control the behaviour of CoreWeave control-plane REST calls.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Optional, Tuple

import logging

from requests import Session

from automojo.restclient.base.aspectsrest import (
    ActionPattern, AspectsRest, LoggingPattern,
    DEFAULT_COMPLETION_TIMEOUT, DEFAULT_COMPLETION_INTERVAL,
    DEFAULT_CONNECTION_TIMEOUT, DEFAULT_INACTIVITY_TIMEOUT,
    DEFAULT_MONITOR_DELAY, DEFAULT_RETRY_LOGGING_INTERVAL,
    DEFAULT_LOGGING_PATTERN, DEFAULT_MUST_CONNECT,
    DEFAULT_ALLOWED_ERROR_CODES, DEFAULT_ALLOWED_CONNECTION_EXCEPTIONS
)


DEFAULT_KUBECONFIG_TTL_SECONDS = 3600

DEFAULT_OPERATION_POLL_INTERVAL_SECONDS = 5
DEFAULT_OPERATION_POLL_TIMEOUT_SECONDS = 600


class AspectsCoreweave(AspectsRest):
    """
        :class:`AspectsCoreweave` extends :class:`AspectsRest` with the
        CoreWeave-specific behaviour knobs — the default TTL requested when
        minting a kubeconfig and the polling cadence used to drive
        long-running-operation waits.

        The standard REST aspects are untouched; the extra fields are
        assigned after the parent class freezes itself and the object is
        re-frozen so the aspects remain immutable. No behaviour-modifying
        decorators are used.
    """

    def __init__(self, *, action_pattern: ActionPattern = ActionPattern.SINGLE_CALL,
                 completion_timeout: float = DEFAULT_COMPLETION_TIMEOUT,
                 completion_interval: float = DEFAULT_COMPLETION_INTERVAL,
                 connection_timeout: float = DEFAULT_CONNECTION_TIMEOUT,
                 inactivity_timeout: float = DEFAULT_INACTIVITY_TIMEOUT,
                 monitor_delay: float = DEFAULT_MONITOR_DELAY,
                 logging_pattern: LoggingPattern = DEFAULT_LOGGING_PATTERN,
                 retry_logging_interval: int = DEFAULT_RETRY_LOGGING_INTERVAL,
                 allowed_error_codes: Tuple[int, ...] = DEFAULT_ALLOWED_ERROR_CODES,
                 allowed_connection_exceptions: Tuple[BaseException, ...] = DEFAULT_ALLOWED_CONNECTION_EXCEPTIONS,
                 must_connect: bool = DEFAULT_MUST_CONNECT,
                 logger: Optional[logging.Logger] = None,
                 session: Optional[Session] = None,
                 kubeconfig_ttl_seconds: int = DEFAULT_KUBECONFIG_TTL_SECONDS,
                 operation_poll_interval_seconds: int = DEFAULT_OPERATION_POLL_INTERVAL_SECONDS,
                 operation_poll_timeout_seconds: int = DEFAULT_OPERATION_POLL_TIMEOUT_SECONDS) -> None:
        """
            Initialize a set of CoreWeave REST call aspects.

            :param action_pattern: Default action pattern for calls.
            :param completion_timeout: Time in seconds to wait for completion.
            :param completion_interval: Polling interval when waiting.
            :param connection_timeout: Timeout for establishing connections.
            :param inactivity_timeout: Timeout for inactivity in seconds.
            :param monitor_delay: Delay before monitoring begins.
            :param logging_pattern: Pattern used for call logging.
            :param retry_logging_interval: Interval for retry log messages.
            :param allowed_error_codes: HTTP status codes considered success.
            :param allowed_connection_exceptions: Exceptions allowed during
                connect.
            :param must_connect: Whether a connection must be established.
            :param logger: Logger to use for messages.
            :param session: Requests session to reuse.
            :param kubeconfig_ttl_seconds: Default TTL requested when minting
                a kubeconfig.
            :param operation_poll_interval_seconds: Interval between polls
                when waiting on a long-running operation.
            :param operation_poll_timeout_seconds: Maximum time to wait for a
                long-running operation to reach a terminal state.

            :returns: ``None``.
        """
        super().__init__(action_pattern=action_pattern,
                         completion_timeout=completion_timeout,
                         completion_interval=completion_interval,
                         connection_timeout=connection_timeout,
                         inactivity_timeout=inactivity_timeout,
                         monitor_delay=monitor_delay,
                         logging_pattern=logging_pattern,
                         retry_logging_interval=retry_logging_interval,
                         allowed_error_codes=allowed_error_codes,
                         allowed_connection_exceptions=allowed_connection_exceptions,
                         must_connect=must_connect,
                         logger=logger,
                         session=session)

        # The parent class freezes after __init__; flip the flag, assign the
        # extra attributes, and re-freeze so the aspects stay immutable.
        object.__setattr__(self, "__frozen__", False)
        self.kubeconfig_ttl_seconds = kubeconfig_ttl_seconds
        self.operation_poll_interval_seconds = operation_poll_interval_seconds
        self.operation_poll_timeout_seconds = operation_poll_timeout_seconds
        object.__setattr__(self, "__frozen__", True)
        return


DEFAULT_COREWEAVE_ASPECTS = AspectsCoreweave()


__all__ = ["AspectsCoreweave", "DEFAULT_COREWEAVE_ASPECTS"]
