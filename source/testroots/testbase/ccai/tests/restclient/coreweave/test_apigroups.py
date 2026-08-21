"""
    .. module:: test_apigroups
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Tests for the CoreWeave api groups — URL composition,
                   parsing, idempotency, and HTTP-error reclassification.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from ccai import testbase


import requests_mock as rm_module

from ccai.errors.exceptions import SemanticError

from ccai.restclient.coreweave.exceptions.coreweaveerrors import (
    CoreweaveAuthenticationError,
    CoreweaveKubeconfigError,
    CoreweaveAcceleratorNotAvailableError,
    CoreweaveTaggingNotSupportedError,
)
from ccai.restclient.coreweave.model.coreweavecluster import CoreweaveCluster
from ccai.restclient.coreweave.model.coreweavekubeconfig import (
    CoreweaveKubeconfig
)

from .testsupport import (
    BASE, TEST_PROJECT, make_client, sample_kubeconfig_yaml
)


def test_list_organizations_parses_records():
    """
        ``organizations.list`` parses every entry into a record.
    """
    client = make_client()
    body = {"items": [{"id": "o1", "slug": "alpha", "name": "Alpha"},
                      {"id": "o2", "slug": "beta", "name": "Beta"}]}
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/organizations".format(BASE), json=body)
        orgs = client.organizations.list()

    assert len(orgs) == 2
    assert orgs[0].slug == "alpha"
    return


def test_list_clusters_url_and_parsing():
    """
        ``clusters.list`` composes the project-scoped URL and parses records.
    """
    client = make_client()
    body = {"items": [{"id": "c1", "project_id": TEST_PROJECT, "name": "ck",
                       "region": "us-east", "k8s_version": "1.30",
                       "api_endpoint": "https://k.test", "status": "ready"}]}
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/projects/{}/clusters".format(BASE, TEST_PROJECT),
                 json=body)
        clusters = client.clusters.list(project_id=TEST_PROJECT)
        assert mock.last_request.path == "/v1/projects/{}/clusters".format(
            TEST_PROJECT)

    assert len(clusters) == 1
    assert isinstance(clusters[0], CoreweaveCluster) is True
    assert clusters[0].region == "us-east"
    return


def test_list_clusters_empty_project_raises_semantic_error():
    """
        An empty identifier raises :class:`SemanticError` before any HTTP.
    """
    client = make_client()
    with testbase.raises(SemanticError):
        client.clusters.list(project_id="")
    return


def test_issue_kubeconfig_returns_record():
    """
        ``kubeconfigs.issue`` POSTs and returns a populated record.
    """
    client = make_client()
    body = {"kubeconfig": sample_kubeconfig_yaml(),
            "expires_at": "2099-01-01T00:00:00Z",
            "api_endpoint": "https://k8s.coreweave.test:6443"}
    with rm_module.Mocker() as mock:
        mock.post("{}/v1/clusters/c1/kubeconfig".format(BASE), json=body)
        kubeconfig = client.kubeconfigs.issue(cluster_id="c1")
        assert mock.last_request.method == "POST"

    assert isinstance(kubeconfig, CoreweaveKubeconfig) is True
    assert kubeconfig.cluster_id == "c1"
    parsed = kubeconfig.as_dict()
    assert parsed["kind"] == "Config"
    return


def test_issue_kubeconfig_missing_payload_raises():
    """
        A kubeconfig response missing the YAML payload raises
        :class:`CoreweaveKubeconfigError`.
    """
    client = make_client()
    body = {"kubeconfig": "", "api_endpoint": "https://k.test"}
    with rm_module.Mocker() as mock:
        mock.post("{}/v1/clusters/c1/kubeconfig".format(BASE), json=body)
        with testbase.raises(CoreweaveKubeconfigError):
            client.kubeconfigs.issue(cluster_id="c1")
    return


def test_mint_kubeconfig_does_not_call_kubernetes_api():
    """
        ``mint_kubeconfig`` issues exactly one POST to the CoreWeave control
        plane and never touches a Kubernetes endpoint.
    """
    client = make_client()
    body = {"kubeconfig": sample_kubeconfig_yaml(),
            "api_endpoint": "https://k8s.coreweave.test:6443"}
    with rm_module.Mocker() as mock:
        mock.post("{}/v1/clusters/c9/kubeconfig".format(BASE), json=body)
        client.mint_kubeconfig(cluster_id="c9")
        assert mock.call_count == 1
        assert "coreweave.test" in mock.last_request.url
    return


def test_http_401_reclassified_as_authentication_error():
    """
        An HTTP 401 is reclassified into
        :class:`CoreweaveAuthenticationError`.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/organizations".format(BASE), status_code=401,
                 json={"detail": "bad token"})
        with testbase.raises(CoreweaveAuthenticationError):
            client.organizations.list()
    return


def test_http_403_reclassified_as_authentication_error():
    """
        An HTTP 403 is reclassified into
        :class:`CoreweaveAuthenticationError`.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/organizations".format(BASE), status_code=403,
                 json={"detail": "forbidden"})
        with testbase.raises(CoreweaveAuthenticationError):
            client.organizations.list()
    return


def test_register_ssh_key_is_idempotent():
    """
        ``ssh_keys.register`` returns the existing record when a key with the
        same name already exists, without POSTing.
    """
    client = make_client()
    existing = {"items": [{"id": "k1", "name": "deploy",
                           "fingerprint": "ab:cd"}]}
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/ssh-keys".format(BASE), json=existing)
        post_marker = mock.post("{}/v1/ssh-keys".format(BASE),
                                json={"id": "k2", "name": "deploy"})
        key = client.ssh_keys.register(name="deploy", public_key="ssh-rsa AAA")

    assert key.id == "k1"
    assert post_marker.called is False
    return


def test_register_ssh_key_creates_when_absent():
    """
        ``ssh_keys.register`` POSTs a new key when none with the name exists.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/ssh-keys".format(BASE), json={"items": []})
        mock.post("{}/v1/ssh-keys".format(BASE),
                  json={"id": "k9", "name": "deploy",
                        "fingerprint": "ee:ff"})
        key = client.ssh_keys.register(name="deploy", public_key="ssh-rsa AAA")

    assert key.id == "k9"
    return


def test_delete_ssh_key_absent_is_noop():
    """
        ``ssh_keys.delete`` treats an unknown key id as success.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.delete("{}/v1/ssh-keys/unknown".format(BASE), status_code=404,
                    json={"detail": "not found"})
        client.ssh_keys.delete(key_id="unknown")
    return


def test_create_object_namespace_is_idempotent():
    """
        ``object_namespaces.create`` returns an existing namespace matching
        name + region instead of creating a duplicate.
    """
    client = make_client()
    existing = {"items": [{"id": "n1", "name": "datasets",
                           "region": "us-east",
                           "endpoint_url": "https://s3.test"}]}
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/projects/{}/object-namespaces".format(BASE,
                 TEST_PROJECT), json=existing)
        post_marker = mock.post(
            "{}/v1/projects/{}/object-namespaces".format(BASE, TEST_PROJECT),
            json={"id": "n2"})
        namespace = client.object_namespaces.create(
            project_id=TEST_PROJECT, name="datasets", region="us-east")

    assert namespace.id == "n1"
    assert post_marker.called is False
    return


def test_require_sku_absent_raises():
    """
        ``accelerators.require_sku`` raises when the SKU is not in catalog.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/projects/{}/accelerator-skus".format(BASE,
                 TEST_PROJECT),
                 json={"items": [{"name": "H100_SXM", "gpu_model": "H100"}]})
        with testbase.raises(CoreweaveAcceleratorNotAvailableError):
            client.accelerators.require_sku(project_id=TEST_PROJECT,
                                            sku_name="B200")
    return


def test_apply_tags_unsupported_resource_raises():
    """
        ``tags.apply`` raises :class:`CoreweaveTaggingNotSupportedError` for
        an untaggable resource type.
    """
    client = make_client()
    with testbase.raises(CoreweaveTaggingNotSupportedError):
        client.tags.apply(resource_type="node-pools", resource_id="np1",
                          tags=[{"env": "prod"}])
    return


def test_apply_tags_supported_resource_patches():
    """
        ``tags.apply`` PATCHes a taggable resource with the flattened tags.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        marker = mock.patch("{}/v1/clusters/c1/tags".format(BASE), json={})
        client.tags.apply(resource_type="clusters", resource_id="c1",
                          tags=[{"env": "prod"}, {"team": "ml"}])
        assert marker.called is True
        sent = marker.last_request.json()
        assert sent["tags"] == {"env": "prod", "team": "ml"}
    return
