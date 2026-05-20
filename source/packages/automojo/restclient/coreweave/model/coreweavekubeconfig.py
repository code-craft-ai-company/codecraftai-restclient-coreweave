"""
    .. module:: coreweavekubeconfig
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Hand-authored :class:`CoreweaveKubeconfig` data model.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Optional


class CoreweaveKubeconfig:
    """
        Typed record describing a kubeconfig minted by the CoreWeave
        control plane for a CKS cluster.

        The CoreWeave client deliberately stops at this boundary — it mints
        the kubeconfig and hands it off. All Kubernetes-API traffic is the
        responsibility of ``automojo-interop-kubernetes``.
    """

    def __init__(self, *, yaml_payload: str, expires_at: Optional[str],
                 api_endpoint: str, cluster_id: str,
                 config_dict: Optional[Dict[str, Any]] = None) -> None:
        """
            Initialize a :class:`CoreweaveKubeconfig`.

            :param yaml_payload: The raw kubeconfig YAML text.
            :param expires_at: The ISO-8601 expiry timestamp, or ``None``.
            :param api_endpoint: The Kubernetes API-server URL.
            :param cluster_id: The cluster this kubeconfig targets.
            :param config_dict: Optional already-parsed kubeconfig dict. When
                ``None`` it is parsed lazily from ``yaml_payload`` by
                :meth:`as_dict`.

            :returns: ``None``.
        """
        self.yaml_payload = yaml_payload
        self.expires_at = expires_at
        self.api_endpoint = api_endpoint
        self.cluster_id = cluster_id
        self.config_dict = config_dict
        return

    def as_dict(self) -> Dict[str, Any]:
        """
            Return the kubeconfig as a parsed dictionary suitable for
            handing to ``KubernetesClient(kubeconfig_dict=...)``.

            :returns: The parsed kubeconfig dictionary.
        """
        if self.config_dict is not None:
            rtnval = self.config_dict
            return rtnval

        import yaml

        parsed = yaml.safe_load(self.yaml_payload)
        self.config_dict = parsed

        rtnval = self.config_dict
        return rtnval

    @classmethod
    def from_payload(cls, *, payload: Dict[str, Any],
                     cluster_id: str) -> "CoreweaveKubeconfig":
        """
            Build a :class:`CoreweaveKubeconfig` from an API payload dict.

            :param payload: The decoded API object.
            :param cluster_id: The cluster identifier the kubeconfig was
                requested for.

            :returns: A populated :class:`CoreweaveKubeconfig`.
        """
        yaml_payload = payload.get("kubeconfig", "")
        expires_at = payload.get("expires_at", None)
        api_endpoint = payload.get("api_endpoint", "")

        rtnval = cls(yaml_payload=yaml_payload, expires_at=expires_at,
                     api_endpoint=api_endpoint, cluster_id=cluster_id)
        return rtnval


__all__ = ["CoreweaveKubeconfig"]
