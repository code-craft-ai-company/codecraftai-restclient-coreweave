"""
    .. module:: testsupport
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Shared fixtures and helpers for the CoreWeave client
                   tests — all HTTP traffic is mocked via ``requests-mock``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from automojo.credentials.coreweaveapicredential import CoreweaveApiCredential

from automojo.interop.coreweave.coreweaveclient import CoreweaveClient


TEST_HOST = "api.coreweave.test"
TEST_ORG = "org-0001"
TEST_PROJECT = "proj-0001"

BASE = "https://{}".format(TEST_HOST)


def make_credential() -> CoreweaveApiCredential:
    """
        Build a valid :class:`CoreweaveApiCredential` for tests.

        :returns: A :class:`CoreweaveApiCredential` with the ``hpc-venue``
            category.
    """
    rtnval = CoreweaveApiCredential(identifier="coreweave-test",
                                    categories=["hpc-venue"],
                                    token="cw-token-0001",
                                    organization_id=TEST_ORG)
    return rtnval


def make_client() -> CoreweaveClient:
    """
        Build a :class:`CoreweaveClient` bound to the test host, org, and
        project.

        :returns: A configured :class:`CoreweaveClient`.
    """
    rtnval = CoreweaveClient(credential=make_credential(),
                             organization_id=TEST_ORG,
                             project_id=TEST_PROJECT,
                             host=TEST_HOST)
    return rtnval


def sample_kubeconfig_yaml(*, server: str = "https://k8s.coreweave.test:6443") -> str:
    """
        Build a minimal but valid kubeconfig YAML payload.

        :param server: The API-server URL to embed.

        :returns: A kubeconfig YAML string.
    """
    lines = [
        "apiVersion: v1",
        "kind: Config",
        "clusters:",
        "- name: cks",
        "  cluster:",
        "    server: {}".format(server),
        "contexts:",
        "- name: cks",
        "  context:",
        "    cluster: cks",
        "    user: cks",
        "current-context: cks",
        "users:",
        "- name: cks",
        "  user:",
        "    token: kube-token-0001",
    ]
    rtnval = "\n".join(lines)
    return rtnval
