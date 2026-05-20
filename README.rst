=========================================
Automation Mojo Interop - CoreWeave
=========================================

The ``automojo-restclient-coreweave`` package is the venue-specific REST client for
CoreWeave's control-plane API. CoreWeave is a GPU-first cloud whose primary workload
surface is Kubernetes (CKS), with bare-metal and Slurm-on-Kubernetes (Sunk) overlays.
This client authenticates against the CoreWeave control plane, exchanges an organization
API token for a scoped ``kubeconfig``, and enumerates the cloud-level resources that sit
outside the Kubernetes API; all workload-shaped operations are delegated to
``automojo-interop-kubernetes``.

Highlights
==========

- ``CoreweaveClient`` — a ``RestClientBase`` subclass that authenticates against the CoreWeave control plane and mints a scoped ``kubeconfig``.
- Cloud-level resource enumeration — organizations, projects, clusters, node pools, and accelerator inventories that live outside the Kubernetes API.
- Hard architectural boundary — this package never speaks the Kubernetes API directly; Kubernetes-shaped work is delegated to ``automojo-interop-kubernetes``.
- Aspects-driven transport — every behaviour-bearing call accepts ``aspects: AspectsRest = DEFAULT_COREWEAVE_ASPECTS``; credentials enter as typed ``CoreweaveApiCredential`` instances from ``automojo-credentials``.

Repository Structure
====================

- ``development/`` - Runtime environment scripts.
- ``repository-setup/`` - Repository homing and setup scripts.
- ``source/packages/automojo/restclient/coreweave/`` - Package source code.
- ``source/testroots/testbase/automojo/tests/restclient/coreweave/`` - TestBase test roots.
- ``specs/`` - Requirements, design, and task documentation (Kiro-style).
- ``userguide/`` - Standards, conventions, and documentation.

Environment Setup
=================

When working in a Codex container:

.. code-block:: bash

   ./development/setup-agent-container

For local development:

.. code-block:: bash

   ./repository-setup/rehome-repository
   ./development/setup-environment

Running Tests
=============

.. code-block:: bash

   source .venv/bin/activate
   PYTHONPATH=source/packages:source/testroots/testbase python -m pytest source/testroots -q

Standards and Conventions
=========================

- Naming conventions: ``userguide/10-02-naming-conventions.rst``
- Code organization: ``userguide/10-01-code-organization.rst``
- Coding standards: ``userguide/10-00-coding-standards.rst``

Additional Resources
====================

- User guide entry point: ``userguide/userguide.rst``
