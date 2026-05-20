"""
    .. module:: kubeconfigsgroup
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The ``kubeconfigs`` api group of the CoreWeave client. This
        group implements the §7 decision: CoreWeave mints a kubeconfig; the
        client returns it; it never speaks the Kubernetes API.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import os

from typing import Any

from automojo.restclient.coreweave.aspectscoreweave import (
    AspectsCoreweave, DEFAULT_COREWEAVE_ASPECTS
)
from automojo.restclient.coreweave.exceptions.coreweaveerrors import (
    CoreweaveKubeconfigError
)
from automojo.restclient.coreweave.model.coreweavekubeconfig import (
    CoreweaveKubeconfig
)
from automojo.restclient.coreweave.urlcompose import require_identifier


class KubeconfigsGroup:
    """
        The ``kubeconfigs`` api group exchanges the API credential for a
        scoped kubeconfig for a CKS cluster.

        This group never invokes a Kubernetes API endpoint. It POSTs to the
        CoreWeave control plane's kubeconfig-issuance endpoint and returns
        the minted material as a :class:`CoreweaveKubeconfig` record.
    """

    def __init__(self, *, client: Any) -> None:
        """
            Initialize the api group.

            :param client: The owning :class:`CoreweaveClient`.

            :returns: ``None``.
        """
        self._client = client
        return

    def issue(self, *, cluster_id: str,
              aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> CoreweaveKubeconfig:
        """
            Issue a scoped kubeconfig for a CKS cluster.

            :param cluster_id: The cluster to issue a kubeconfig for.
            :param aspects: Behaviour control for the call. The requested
                TTL is taken from ``aspects.kubeconfig_ttl_seconds``.

            :returns: A :class:`CoreweaveKubeconfig` carrying the YAML
                payload, expiry, and API-server URL.

            :raises: :class:`SemanticError` when ``cluster_id`` is empty.
            :raises: :class:`CoreweaveKubeconfigError` when the issued
                kubeconfig is malformed or missing required fields.
        """
        validated_cluster = require_identifier(name="cluster_id",
                                                value=cluster_id)

        body = {"ttl_seconds": aspects.kubeconfig_ttl_seconds}

        payload = self._client.request_json(
            method="POST",
            segments=("v1", "clusters", validated_cluster, "kubeconfig"),
            params=None,
            body=body,
            aspects=aspects)

        kubeconfig = CoreweaveKubeconfig.from_payload(payload=payload,
                                                      cluster_id=validated_cluster)

        if kubeconfig.yaml_payload is None or len(kubeconfig.yaml_payload) == 0:
            err_msg_lines = ["The issued kubeconfig is missing its YAML payload."]
            err_msg_lines.append("CLUSTER: {}".format(validated_cluster))
            err_msg = os.linesep.join(err_msg_lines)
            raise CoreweaveKubeconfigError(err_msg)

        if kubeconfig.api_endpoint is None or len(kubeconfig.api_endpoint) == 0:
            err_msg_lines = ["The issued kubeconfig is missing the API endpoint."]
            err_msg_lines.append("CLUSTER: {}".format(validated_cluster))
            err_msg = os.linesep.join(err_msg_lines)
            raise CoreweaveKubeconfigError(err_msg)

        rtnval = kubeconfig
        return rtnval


__all__ = ["KubeconfigsGroup"]
