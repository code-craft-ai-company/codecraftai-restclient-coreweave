# Implementation Plan — CoreWeave Client

## Package Skeleton

- [x] 1. Create `source/packages/automojo/interop/coreweave/` package tree with `apigroups/`, `model/`, `exceptions/` subpackages.
- [x] 2. Add `aspectscoreweave.py` defining `DEFAULT_COREWEAVE_ASPECTS`.

## Client Core

- [x] 3. Implement `CoreweaveClient(RestClientBase)` with credential validation and `_authenticate` override.
- [x] 4. Implement URL composition helper with per-segment percent-encoding and empty/`None` rejection.
- [x] 5. Implement HTTP error reclassification into `CoreweaveAuthenticationError` and related typed exceptions.

## Data Model

- [x] 6. Implement model dataclasses for organization, project, cluster, node pool, accelerator SKU, kubeconfig, SSH key, object namespace, operation result.
- [x] 7. Implement `CoreweaveTaskHandle` against `ITaskHandle`.

## API Groups

- [x] 8. Implement `OrganizationsGroup.list(aspects)`.
- [x] 9. Implement `ProjectsGroup.list(organization_id, aspects)`.
- [x] 10. Implement `ClustersGroup.list(project_id, aspects)` and `.get(cluster_id, aspects)`.
- [x] 11. Implement `NodePoolsGroup.list(cluster_id, aspects)`.
- [x] 12. Implement `AcceleratorsGroup.list_skus(project_id, aspects)`.
- [x] 13. Implement `KubeconfigsGroup.issue(cluster_id, aspects)` returning `CoreweaveKubeconfig`.
- [x] 14. Implement `SshKeysGroup.register(name, public_key, aspects)` with idempotent read-before-create and `.delete(key_id, aspects)` as idempotent no-op on absent.
- [x] 15. Implement `ObjectNamespacesGroup.create(name, region, aspects)` with idempotent read-before-create and `.list(project_id, aspects)`.
- [x] 16. Implement `TagsGroup.apply(resource_type, resource_id, tags, aspects)` with translation from neutral tag list.
- [x] 17. Implement `OperationsGroup.get(operation_id, aspects)` consumed by `CoreweaveTaskHandle.wait`.

## Paging

- [x] 18. Implement transparent cursor traversal in every `list_*` method.

## Tests — Example-Based

- [x] 19. Construction tests covering valid credential, missing org/project slug.
- [x] 20. Kubeconfig issuance success and failure tests.
- [x] 21. Idempotency tests for SSH-key register and object-namespace create.
- [x] 22. HTTP-error reclassification tests.

## Tests — Property-Based (hypothesis)

- [x] 23. Paging-cursor traversal totality: union over arbitrary page sequences equals expected concatenation.
- [x] 24. URL-composition determinism + per-segment encoding + empty/`None` rejection.
- [x] 25. Idempotent-retry equivalence within budget; bubble-through outside budget.
- [x] 26. `CoreweaveTaskHandle.wait` terminal-state correctness against arbitrary monotonic mock streams.

## Integration

- [ ] 27. Smoke-test fixture for live CoreWeave API (gated by env var), `multihost` tier.
