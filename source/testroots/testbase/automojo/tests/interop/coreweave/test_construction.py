"""
    .. module:: test_construction
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Tests for :class:`CoreweaveClient` construction and
                   credential validation.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import pytest

from automojo.errors.exceptions import ConfigurationError

from automojo.credentials.basiccredential import BasicCredential
from automojo.credentials.coreweaveapicredential import CoreweaveApiCredential

from automojo.interop.coreweave.coreweaveclient import CoreweaveClient
from automojo.interop.coreweave.apigroups.organizationsgroup import (
    OrganizationsGroup
)
from automojo.interop.coreweave.apigroups.kubeconfigsgroup import (
    KubeconfigsGroup
)

from automojo.tests.interop.coreweave.testsupport import (
    TEST_ORG, TEST_PROJECT, make_client, make_credential
)


def test_construct_with_valid_credential():
    """
        Constructing with a valid credential succeeds and binds every api
        group.
    """
    client = make_client()

    assert client.organization_id == TEST_ORG
    assert client.project_id == TEST_PROJECT
    assert isinstance(client.organizations, OrganizationsGroup) is True
    assert isinstance(client.kubeconfigs, KubeconfigsGroup) is True
    return


def test_construct_resolves_org_from_credential():
    """
        When ``organization_id`` is omitted the credential's value is used.
    """
    client = CoreweaveClient(credential=make_credential(),
                             project_id=TEST_PROJECT)

    assert client.organization_id == TEST_ORG
    return


def test_construct_with_wrong_credential_raises():
    """
        Constructing with a non-CoreWeave credential raises
        :class:`ConfigurationError`.
    """
    wrong = BasicCredential(identifier="basic", categories=["basic"],
                            username="u", password="p")

    with pytest.raises(ConfigurationError):
        CoreweaveClient(credential=wrong, organization_id=TEST_ORG,
                        project_id=TEST_PROJECT)
    return


def test_construct_missing_organization_raises():
    """
        Constructing without an organization scope raises
        :class:`ConfigurationError` before any HTTP call.
    """
    cred = CoreweaveApiCredential(identifier="cw", categories=["hpc-venue"],
                                  token="tok", organization_id=None)

    with pytest.raises(ConfigurationError):
        CoreweaveClient(credential=cred, project_id=TEST_PROJECT)
    return


def test_construct_missing_project_raises():
    """
        Constructing without a project scope raises
        :class:`ConfigurationError`.
    """
    with pytest.raises(ConfigurationError):
        CoreweaveClient(credential=make_credential(),
                        organization_id=TEST_ORG, project_id="")
    return
