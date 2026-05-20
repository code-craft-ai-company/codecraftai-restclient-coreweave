"""
    .. module:: coreweaveclient
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that contains :class:`CoreweaveClient`, the typed,
        aspect-driven REST client for the CoreWeave control-plane API.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import json
import os

from typing import Any, Dict, Optional, Tuple

from requests import Response, Session

from automojo.errors.exceptions import (
    ConfigurationError, HttpForbiddenError, HttpUnAuthorizedError
)

from automojo.credentials.basecredential import BaseCredential
from automojo.credentials.coreweaveapicredential import CoreweaveApiCredential

from automojo.restclient.base.restclientbase import RestClientBase

from automojo.interop.coreweave.aspectscoreweave import (
    AspectsCoreweave, DEFAULT_COREWEAVE_ASPECTS
)
from automojo.interop.coreweave.apigroups.groupsupport import safe_json
from automojo.interop.coreweave.apigroups.organizationsgroup import (
    OrganizationsGroup
)
from automojo.interop.coreweave.apigroups.projectsgroup import ProjectsGroup
from automojo.interop.coreweave.apigroups.clustersgroup import ClustersGroup
from automojo.interop.coreweave.apigroups.nodepoolsgroup import NodePoolsGroup
from automojo.interop.coreweave.apigroups.acceleratorsgroup import (
    AcceleratorsGroup
)
from automojo.interop.coreweave.apigroups.kubeconfigsgroup import (
    KubeconfigsGroup
)
from automojo.interop.coreweave.apigroups.sshkeysgroup import SshKeysGroup
from automojo.interop.coreweave.apigroups.objectnamespacesgroup import (
    ObjectNamespacesGroup
)
from automojo.interop.coreweave.apigroups.tagsgroup import TagsGroup
from automojo.interop.coreweave.apigroups.operationsgroup import OperationsGroup
from automojo.interop.coreweave.exceptions.coreweaveerrors import (
    CoreweaveAuthenticationError
)
from automojo.interop.coreweave.model.coreweavekubeconfig import (
    CoreweaveKubeconfig
)
from automojo.interop.coreweave.model.coreweavetaskhandle import (
    CoreweaveTaskHandle
)
from automojo.interop.coreweave.urlcompose import compose_leaf


COREWEAVE_API_HOST = "api.coreweave.com"

# HTTP statuses considered a successful read/write on the CoreWeave API.
_SUCCESS_STATUSES = (200, 201, 202, 204)


class CoreweaveClient(RestClientBase):
    """
        :class:`CoreweaveClient` is the typed, aspect-driven REST client for
        the CoreWeave control-plane API. It is built on
        :class:`RestClientBase` and authenticates with a typed
        :class:`CoreweaveApiCredential`.

        CoreWeave is Kubernetes-native. This client is deliberately bounded
        to the *cloud-shaped* surface that lives outside the Kubernetes API:
        organizations, projects, clusters, node pools, accelerator SKUs,
        kubeconfig issuance, SSH keys, object-storage namespaces, tagging,
        and long-running operations. The §7 architectural decision is hard:
        this client mints a kubeconfig and *returns it*; it never speaks the
        Kubernetes API. Downstream, ``automojo-interop-kubernetes`` consumes
        the kubeconfig.

        The surface is exposed through nine api groups
        (:attr:`organizations`, :attr:`projects`, :attr:`clusters`,
        :attr:`node_pools`, :attr:`accelerators`, :attr:`kubeconfigs`,
        :attr:`ssh_keys`, :attr:`object_namespaces`, :attr:`tags`,
        :attr:`operations`). Every behaviour-bearing call accepts an
        ``aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS`` named-only
        parameter; no behaviour-modifying decorators are used.
    """

    def __init__(self, *, credential: BaseCredential,
                 organization_id: Optional[str] = None,
                 project_id: Optional[str] = None,
                 host: str = COREWEAVE_API_HOST,
                 aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> None:
        """
            Initialize the CoreWeave REST client.

            :param credential: A :class:`CoreweaveApiCredential`.
            :param organization_id: The CoreWeave organization scope. When
                omitted the credential's ``organization_id`` is used.
            :param project_id: The CoreWeave project scope.
            :param host: Override host name for the REST endpoint.
            :param aspects: Default :class:`AspectsCoreweave` applied when a
                call omits an explicit aspects argument.

            :returns: ``None``.

            :raises: :class:`ConfigurationError` when the credential is not a
                :class:`CoreweaveApiCredential` or the organization scope
                cannot be resolved.
        """
        if not isinstance(credential, CoreweaveApiCredential):
            err_msg_lines = ["CoreweaveClient requires a CoreweaveApiCredential."]
            err_msg_lines.append("EXPECTED: CoreweaveApiCredential")
            err_msg_lines.append("FOUND: {}".format(type(credential).__name__))
            err_msg = os.linesep.join(err_msg_lines)
            raise ConfigurationError(err_msg)

        resolved_organization = organization_id
        if resolved_organization is None:
            resolved_organization = credential.organization_id

        if resolved_organization is None or len(resolved_organization) == 0:
            err_msg_lines = ["The CoreweaveClient requires an organization scope."]
            err_msg_lines.append("Provide 'organization_id' or set it on the "
                                 "CoreweaveApiCredential.")
            err_msg = os.linesep.join(err_msg_lines)
            raise ConfigurationError(err_msg)

        if project_id is None or len(project_id) == 0:
            err_msg_lines = ["The CoreweaveClient requires a project scope."]
            err_msg_lines.append("Provide a non-empty 'project_id'.")
            err_msg = os.linesep.join(err_msg_lines)
            raise ConfigurationError(err_msg)

        super().__init__(host=host, credential=credential, aspects=aspects)

        self._organization_id = resolved_organization
        self._project_id = project_id
        self._token = credential.token

        self._organizations = OrganizationsGroup(client=self)
        self._projects = ProjectsGroup(client=self)
        self._clusters = ClustersGroup(client=self)
        self._node_pools = NodePoolsGroup(client=self)
        self._accelerators = AcceleratorsGroup(client=self)
        self._kubeconfigs = KubeconfigsGroup(client=self)
        self._ssh_keys = SshKeysGroup(client=self)
        self._object_namespaces = ObjectNamespacesGroup(client=self)
        self._tags = TagsGroup(client=self)
        self._operations = OperationsGroup(client=self)
        return

    @property
    def organization_id(self) -> str:
        """
            The CoreWeave organization scope this client targets.

            :returns: The organization identifier string.
        """
        rtnval = self._organization_id
        return rtnval

    @property
    def project_id(self) -> str:
        """
            The CoreWeave project scope this client targets.

            :returns: The project identifier string.
        """
        rtnval = self._project_id
        return rtnval

    @property
    def organizations(self) -> OrganizationsGroup:
        """
            The ``organizations`` api group.

            :returns: The :class:`OrganizationsGroup` instance.
        """
        rtnval = self._organizations
        return rtnval

    @property
    def projects(self) -> ProjectsGroup:
        """
            The ``projects`` api group.

            :returns: The :class:`ProjectsGroup` instance.
        """
        rtnval = self._projects
        return rtnval

    @property
    def clusters(self) -> ClustersGroup:
        """
            The ``clusters`` api group.

            :returns: The :class:`ClustersGroup` instance.
        """
        rtnval = self._clusters
        return rtnval

    @property
    def node_pools(self) -> NodePoolsGroup:
        """
            The ``node-pools`` api group.

            :returns: The :class:`NodePoolsGroup` instance.
        """
        rtnval = self._node_pools
        return rtnval

    @property
    def accelerators(self) -> AcceleratorsGroup:
        """
            The ``accelerators`` api group.

            :returns: The :class:`AcceleratorsGroup` instance.
        """
        rtnval = self._accelerators
        return rtnval

    @property
    def kubeconfigs(self) -> KubeconfigsGroup:
        """
            The ``kubeconfigs`` api group.

            :returns: The :class:`KubeconfigsGroup` instance.
        """
        rtnval = self._kubeconfigs
        return rtnval

    @property
    def ssh_keys(self) -> SshKeysGroup:
        """
            The ``ssh-keys`` api group.

            :returns: The :class:`SshKeysGroup` instance.
        """
        rtnval = self._ssh_keys
        return rtnval

    @property
    def object_namespaces(self) -> ObjectNamespacesGroup:
        """
            The ``object-namespaces`` api group.

            :returns: The :class:`ObjectNamespacesGroup` instance.
        """
        rtnval = self._object_namespaces
        return rtnval

    @property
    def tags(self) -> TagsGroup:
        """
            The ``tags`` api group.

            :returns: The :class:`TagsGroup` instance.
        """
        rtnval = self._tags
        return rtnval

    @property
    def operations(self) -> OperationsGroup:
        """
            The ``operations`` api group.

            :returns: The :class:`OperationsGroup` instance.
        """
        rtnval = self._operations
        return rtnval

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate(self) -> None:
        """
            Build the authenticated :class:`Session` for the client.

            CoreWeave uses bearer-token authentication; the credential's API
            token is attached as an ``Authorization: Bearer`` header. No
            login round-trip is required.

            :returns: ``None``.
        """
        session = Session()
        session.verify = self._verify_certificate
        session.headers.update({
            "Authorization": "Bearer {}".format(self._token),
            "Accept": "application/json",
            "X-CoreWeave-Organization": self._organization_id,
            "X-CoreWeave-Project": self._project_id,
        })

        self._session = session
        return

    # ------------------------------------------------------------------
    # Transport
    # ------------------------------------------------------------------

    def request_json(self, *, method: str, segments: Tuple[str, ...],
                     params: Optional[Dict[str, str]],
                     body: Optional[Dict[str, Any]],
                     aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> Dict[str, Any]:
        """
            Issue a single CoreWeave control-plane call and decode the JSON
            response body.

            HTTP 401 / 403 are reclassified into
            :class:`CoreweaveAuthenticationError` carrying the request URL
            and response detail. All other behaviour (retry, timeout,
            logging) flows through :class:`RestClientBase` per ``aspects``.

            :param method: The HTTP method to invoke.
            :param segments: The ordered path segments composed into the
                request leaf. Each must be a non-empty string.
            :param params: Optional query-string parameters.
            :param body: Optional request body serialized as JSON.
            :param aspects: Behaviour control for the call.

            :returns: The decoded JSON object, or an empty dict for an empty
                body.

            :raises: :class:`SemanticError` when a path segment is empty.
            :raises: :class:`CoreweaveAuthenticationError` on HTTP 401 / 403.
        """
        leaf = compose_leaf(segments=segments)

        body_bytes: Optional[bytes] = None
        headers: Dict[str, str] = {}
        if body is not None:
            body_bytes = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        try:
            response: Response = self.perform_call(
                leaf=leaf,
                method=method,
                params=params,
                body=body_bytes,
                exp_status=list(_SUCCESS_STATUSES),
                headers=headers,
                context_msg="CoreWeave API call",
                aspects=aspects)
        except (HttpForbiddenError, HttpUnAuthorizedError) as auth_error:
            err_msg_lines = ["The CoreWeave control plane rejected the request."]
            err_msg_lines.append("METHOD: {}".format(method))
            err_msg_lines.append("URL: {}".format(self._format_call_url(leaf)))
            err_msg_lines.append("DETAIL:")
            err_msg_lines.append(str(auth_error))
            err_msg = os.linesep.join(err_msg_lines)
            raise CoreweaveAuthenticationError(err_msg) from auth_error

        decoded = safe_json(response=response)
        rtnval = decoded
        return rtnval

    # ------------------------------------------------------------------
    # Convenience surface
    # ------------------------------------------------------------------

    def mint_kubeconfig(self, *, cluster_id: str,
                        aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> CoreweaveKubeconfig:
        """
            Mint a scoped kubeconfig for a CKS cluster.

            This is the §7.6 "mint kubeconfig, then drive Kubernetes" entry
            point used by ``automojo-provisioning/venues/coreweave/``. The
            returned :class:`CoreweaveKubeconfig` is handed to a
            ``KubernetesClient``; this client never speaks the Kubernetes
            API itself.

            :param cluster_id: The cluster to mint a kubeconfig for.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CoreweaveKubeconfig` record.

            :raises: :class:`CoreweaveKubeconfigError` when the issued
                kubeconfig is malformed.
        """
        rtnval = self._kubeconfigs.issue(cluster_id=cluster_id, aspects=aspects)
        return rtnval

    def task_handle(self, *, operation_id: str,
                    aspects: AspectsCoreweave = DEFAULT_COREWEAVE_ASPECTS) -> CoreweaveTaskHandle:
        """
            Build a :class:`CoreweaveTaskHandle` for a long-running
            operation id.

            :param operation_id: The operation identifier (typically taken
                from a 202-Accepted response).
            :param aspects: The CoreWeave aspects supplying the poll cadence.

            :returns: A :class:`CoreweaveTaskHandle` implementing
                :class:`ITaskHandle`.
        """
        rtnval = CoreweaveTaskHandle(operation_id=operation_id,
                                     operations_group=self._operations,
                                     client_aspects=aspects)
        return rtnval


__all__ = ["CoreweaveClient", "COREWEAVE_API_HOST"]
