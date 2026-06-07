# Design

## Overview

`CoreweaveClient` is a `RestClientBase` subclass that talks to the CoreWeave
control-plane REST API. Its responsibility is the cloud-shaped surface
(organizations, projects, clusters, node pools, accelerator SKUs, kubeconfig
issuance, SSH keys, object-storage namespaces, tagging, long-running
operations) — *not* the Kubernetes-shaped surface, which is delegated to
`codecraftai-interop-kubernetes` via the kubeconfig this client mints.

All calls accept `aspects: AspectsRest = DEFAULT_COREWEAVE_ASPECTS` so
retry/backoff/timeout/logging are caller-driven. Credentials are typed
(`CoreweaveApiCredential`). The client never imports anything from the
Kubernetes SDK.

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│  codecraftai-provisioning / venues / coreweave            │
│  (WorkloadProvisioner lifecycle)                       │
└──────────┬─────────────────────────────┬───────────────┘
           │ cloud-shaped ops             │ kubeconfig
           ▼                              ▼
┌────────────────────────────┐  ┌─────────────────────────┐
│  CoreweaveClient           │  │ codecraftai-interop-       │
│  (this package)            │  │   kubernetes            │
│  ─ RestClientBase          │  │ (downstream consumer)   │
│  ─ AspectsRest on every op │  └─────────────────────────┘
└──────────┬─────────────────┘
           │ HTTPS, token auth
           ▼
┌────────────────────────────────────────────────────────┐
│  api.coreweave.com  (REST control plane)               │
└────────────────────────────────────────────────────────┘
```

---

## Data Model

`model/`:
- `coreweaveorganization.py` — `CoreweaveOrganization(id, slug, name, tags)`
- `coreweaveproject.py` — `CoreweaveProject(id, organization_id, slug, region_defaults)`
- `coreweavecluster.py` — `CoreweaveCluster(id, project_id, name, region, k8s_version, api_endpoint, status)`
- `coreweavenodepool.py` — `CoreweaveNodePool(id, cluster_id, gpu_model, gpus_per_node, node_count, interconnect)`
- `coreweaveacceleratorsku.py` — `CoreweaveAcceleratorSku(name, gpu_model, memory_gb, available_regions)`
- `coreweavekubeconfig.py` — `CoreweaveKubeconfig(yaml_payload, expires_at, api_endpoint, cluster_id)`
- `coreweavesshkey.py` — `CoreweaveSshKey(id, name, fingerprint)`
- `coreweaveobjectnamespace.py` — `CoreweaveObjectNamespace(id, name, region, endpoint_url)`
- `coreweaveoperationresult.py` — `CoreweaveOperationResult(operation_id, status, resource_ref, detail)`
- `coreweavetaskhandle.py` — `CoreweaveTaskHandle(ITaskHandle)`

Exceptions (`exceptions/`):
- `CoreweaveAuthenticationError`
- `CoreweaveKubeconfigError`
- `CoreweaveAcceleratorNotAvailableError`
- `CoreweaveTaggingNotSupportedError`

---

## Module Layout

```
source/packages/ccai/restclient/coreweave/
├── __init__.py
├── coreweaveclient.py
├── aspectscoreweave.py            # DEFAULT_COREWEAVE_ASPECTS
├── apigroups/
│   ├── organizationsgroup.py
│   ├── projectsgroup.py
│   ├── clustersgroup.py
│   ├── nodepoolsgroup.py
│   ├── acceleratorsgroup.py
│   ├── kubeconfigsgroup.py
│   ├── sshkeysgroup.py
│   ├── objectnamespacesgroup.py
│   ├── tagsgroup.py
│   └── operationsgroup.py
├── model/
└── exceptions/
```

---

## See Also

- `codecraftai-restclient-base/specs/restapigroup-enhancements/` — `RestApiGroup` shape this client builds on.
- `codecraftai-interop-kubernetes/specs/kubernetes-client/` — downstream consumer of the issued kubeconfig.
- `codecraftai-provisioning/specs/venue-coreweave/` — provisioner that composes this client.
- `codecraftai-credentials/specs/coreweave-credentials/` — credential type accepted on construction.

---

## Testing Strategy

Example-based tests (unittest) cover:
- Construction with a valid/invalid credential.
- Successful and failing kubeconfig issuance.
- Idempotent SSH-key registration and idempotent object-namespace creation.
- Reclassification of HTTP 401/403/404 into typed exceptions.

Property-based tests (hypothesis) are **required** for:
1. **Paging cursor traversal.** For any sequence of mock pages with arbitrary
   cursor tokens, `list_*` must return the concatenated union exactly once,
   in order, with no item dropped or duplicated.
2. **URL composition.** For any tuple of identifier strings, the composed URL
   must be a deterministic function of inputs; each segment is independently
   percent-encoded; empty/`None` identifiers raise `SemanticError`.
3. **Idempotent retry semantics.** For any retry budget and any sequence of
   transient failures within budget, the operation produces the same result as
   a single successful call; outside budget, the final exception bubbles unchanged.
4. **Task-handle waiting.** For any monotonic status progression mock, `wait`
   terminates on the first terminal status and never reports a status not
   present in the input stream.

All tests use a mock transport; no live CoreWeave API is required for unit runs.
A separate `multihost` tier may add live-API smoke tests later.
