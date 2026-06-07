"""
    .. module:: coreweaveerrors
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Typed exceptions raised by the CoreWeave control-plane client.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


class CoreweaveError(Exception):
    """
        Base class for every typed error raised by the CoreWeave client.
    """


class CoreweaveAuthenticationError(CoreweaveError):
    """
        Raised when the CoreWeave control plane rejects the supplied API
        token (HTTP 401 / 403). Carries the request URL and the response
        detail so failure reports point at the offending call.
    """


class CoreweaveKubeconfigError(CoreweaveError):
    """
        Raised when an issued kubeconfig is expired, malformed, or missing
        a required field.
    """


class CoreweaveAcceleratorNotAvailableError(CoreweaveError):
    """
        Raised when a requested accelerator SKU is not present in the
        venue catalog for the target project.
    """


class CoreweaveTaggingNotSupportedError(CoreweaveError):
    """
        Raised when a tagging request targets a resource type that the
        CoreWeave control plane does not support tags on.
    """


__all__ = [
    "CoreweaveError",
    "CoreweaveAuthenticationError",
    "CoreweaveKubeconfigError",
    "CoreweaveAcceleratorNotAvailableError",
    "CoreweaveTaggingNotSupportedError",
]
