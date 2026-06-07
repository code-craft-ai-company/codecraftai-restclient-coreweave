# Requirements

## Introduction

The `coreweave-client` feature provides a REST client for the CoreWeave
control-plane API. CoreWeave is Kubernetes-native; this client is therefore
small and bounded — its responsibility is the *cloud-shaped* surface that
exists outside the Kubernetes API: organization/project enumeration, cluster
lookup, node-pool and accelerator inventory, kubeconfig issuance, and
object-storage namespace management. All Kubernetes-shaped work (jobs,
deployments, PVCs, services) is delegated to `codecraftai-interop-kubernetes`
via the kubeconfig this client produces.

The client is built on `RestClientBase` from `codecraftai-restclient-base`.
Authentication uses a typed `CoreweaveApiCredential` from
`codecraftai-credentials`. Every behaviour-bearing call accepts a typed
`aspects: AspectsRest = DEFAULT_COREWEAVE_ASPECTS` parameter so callers
control retry, timeout, and logging policy externally. The client never
speaks the Kubernetes API directly.

This client is consumed by `codecraftai-provisioning/venues/coreweave/` to
implement the `WorkloadProvisioner` lifecycle against CoreWeave Cloud and
Sunk-on-CKS workloads.

---

## Requirements

### Requirement 1: Authenticate Against the CoreWeave API

**User Story:** As a venue provisioner, I want to authenticate against the
CoreWeave control plane using a typed credential so that all subsequent
operations are scoped to the correct organization and project.

#### Acceptance Criteria

1. WHEN the caller constructs a `CoreweaveClient` with a `CoreweaveApiCredential`
   THE SYSTEM SHALL configure `RestClientBase` with the credential's API token,
   organization slug, and project slug.
2. WHEN the credential is missing the organization or project slug THE SYSTEM
   SHALL raise `ConfigurationError` before any HTTP call is issued.
3. WHEN an API call returns HTTP 401 or 403 THE SYSTEM SHALL reclassify the
   `RestClientBase` exception into a `CoreweaveAuthenticationError` containing
   the request URL and response detail.

### Requirement 2: List Organizations, Projects, and Clusters

**User Story:** As a provisioner, I want to enumerate organizations, projects,
and clusters so that I can map a neutral `CloudVenue` reference to a concrete
CoreWeave target.

#### Acceptance Criteria

1. WHEN the caller invokes `list_organizations(aspects)` THE SYSTEM SHALL
   return a list of `CoreweaveOrganization` records.
2. WHEN the caller invokes `list_projects(organization_id, aspects)` THE
   SYSTEM SHALL return a list of `CoreweaveProject` records scoped to that
   organization.
3. WHEN the caller invokes `list_clusters(project_id, aspects)` THE SYSTEM
   SHALL return a list of `CoreweaveCluster` records including region, k8s
   version, and reachable API endpoint.
4. WHEN any list endpoint returns a paging cursor THE SYSTEM SHALL transparently
   follow the cursor until exhausted and return a single concatenated list.

### Requirement 3: Issue a Kubeconfig for a Cluster

**User Story:** As a provisioner, I want to exchange the API credential for a
scoped kubeconfig so that downstream Kubernetes-shaped work runs through
`codecraftai-interop-kubernetes`.

#### Acceptance Criteria

1. WHEN the caller invokes `issue_kubeconfig(cluster_id, aspects)` THE SYSTEM
   SHALL POST to the cluster's kubeconfig-issuance endpoint and return a
   `CoreweaveKubeconfig` record containing the YAML payload, expiration, and
   the cluster's API server URL.
2. WHEN the issued kubeconfig is expired or missing required fields THE SYSTEM
   SHALL raise `CoreweaveKubeconfigError`.
3. THE SYSTEM SHALL NOT invoke any Kubernetes API endpoint as part of this call.

### Requirement 4: Enumerate Node Pools and Accelerator Inventory

**User Story:** As a provisioner planning a GPU workload, I want to read node-pool
and accelerator inventory so that I can validate a `CloudAcceleratorSpec` against
real available capacity before submitting work.

#### Acceptance Criteria

1. WHEN the caller invokes `list_node_pools(cluster_id, aspects)` THE SYSTEM
   SHALL return `CoreweaveNodePool` records carrying the GPU model, count
   per node, and interconnect topology.
2. WHEN the caller invokes `list_accelerator_skus(project_id, aspects)` THE
   SYSTEM SHALL return the venue's catalog of GPU SKUs.
3. WHEN a requested SKU is absent from the catalog THE SYSTEM SHALL raise
   `CoreweaveAcceleratorNotAvailableError` with the SKU name and project id.

### Requirement 5: Manage SSH Keys and API Credentials Plumbing

**User Story:** As a provisioner bootstrapping a host, I want to register an
SSH public key with the project so that emitted nodes accept the provisioner's
key without extra setup.

#### Acceptance Criteria

1. WHEN the caller invokes `register_ssh_key(name, public_key, aspects)` THE
   SYSTEM SHALL POST the key and return a `CoreweaveSshKey` record with the
   server-assigned id.
2. WHEN a key with the same name already exists THE SYSTEM SHALL return the
   existing record without creating a duplicate (idempotent registration).
3. WHEN the caller invokes `delete_ssh_key(key_id, aspects)` THE SYSTEM
   SHALL DELETE the key and return `None`. WHEN the key id is unknown the
   call SHALL succeed as a no-op (idempotent delete).

### Requirement 6: Manage Object-Storage Namespaces

**User Story:** As a provisioner staging dataset buckets, I want to create and
list object-storage namespaces so that bucket lifecycle is governed by the
same idempotent plan/apply pipeline as compute.

#### Acceptance Criteria

1. WHEN the caller invokes `create_object_namespace(name, region, aspects)`
   THE SYSTEM SHALL POST the request and return a `CoreweaveObjectNamespace`
   record.
2. WHEN a namespace with the same name in the same region already exists
   THE SYSTEM SHALL return the existing record (read-before-create).
3. WHEN the caller invokes `list_object_namespaces(project_id, aspects)`
   THE SYSTEM SHALL return all namespaces and SHALL follow paging cursors.

### Requirement 7: Apply Tags to Cloud Resources

**User Story:** As a provisioner, I want to attach neutral key/value tags so
that resources can be grouped across venues by the same labels used elsewhere.

#### Acceptance Criteria

1. WHEN the caller invokes `apply_tags(resource_type, resource_id, tags, aspects)`
   THE SYSTEM SHALL PATCH the resource with the supplied tag set.
2. THE SYSTEM SHALL accept tags as a `List[Dict[str, str]]` matching the
   neutral provisioning model and translate to CoreWeave's tagging payload
   shape internally.
3. WHEN the resource type does not support tagging THE SYSTEM SHALL raise
   `CoreweaveTaggingNotSupportedError` with the resource type.

### Requirement 8: Track Long-Running Operations

**User Story:** As a provisioner, I want async operations to return a typed
task handle so that the lifecycle pipeline can `wait()` on them with
caller-controlled aspects.

#### Acceptance Criteria

1. WHEN an API call returns a 202 Accepted with an operation id THE SYSTEM
   SHALL return a `CoreweaveTaskHandle` implementing `ITaskHandle`.
2. WHEN the caller invokes `handle.wait(aspects)` THE SYSTEM SHALL poll the
   operation status endpoint at the interval and timeout dictated by aspects
   and SHALL return the final `CoreweaveOperationResult` on completion.
3. WHEN the timeout in aspects elapses THE SYSTEM SHALL raise
   `TimeoutError` with the operation id and last observed status.

### Requirement 9: URL Composition for Nested Resources

**User Story:** As a maintainer, I want nested-resource URL composition to be
total and unambiguous so that path-segment encoding cannot silently produce
malformed requests.

#### Acceptance Criteria

1. WHEN any client method composes a URL containing identifiers THE SYSTEM
   SHALL percent-encode each path segment independently.
2. WHEN any identifier is empty or `None` THE SYSTEM SHALL raise
   `SemanticError` before issuing the request.
3. THE SYSTEM SHALL never collapse repeated `/` characters silently;
   the composed URL is a deterministic function of `(base, segments)`.

### Requirement 10: Aspects on Every Behaviour-Bearing Call

**User Story:** As a caller, I want consistent control over retries, timeouts,
backoff, and logging so that I never have to reach into the client to
modify behaviour.

#### Acceptance Criteria

1. THE SYSTEM SHALL accept `aspects: AspectsRest = DEFAULT_COREWEAVE_ASPECTS`
   as a named-only parameter on every method that performs I/O.
2. THE SYSTEM SHALL never apply behaviour-modifying decorators such as `@retry`.
3. WHEN a transient HTTP error occurs THE SYSTEM SHALL retry per `aspects`
   policy and SHALL surface the final error unchanged if the budget is exhausted.
