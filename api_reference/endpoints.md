# Rattle API — Endpoint Reference

Auto-generated from the OpenAPI spec. Do not edit manually.
Run `python3 tools/fetch_api_docs.py` to refresh.

**API version**: 1.0.0
**Base URL**: /

## API Keys

- `GET /api/v1/api-keys` — List API keys
- `POST /api/v1/api-keys` — Create an API key
  - Request body: `ApiKeyCreateRequest`
- `GET /api/v1/api-keys/usage` — Get API key usage statistics
- `DELETE /api/v1/api-keys/{id}` — Revoke an API key
- `GET /api/v1/api-keys/{id}` — Get an API key
- `DELETE /api/v1/api-keys/{id}/permanent` — Permanently delete an API key
- `POST /api/v1/api-keys/{id}/rotate` — Rotate an API key

## Analytics

- `GET /api/v1/analytics/option-selections` — List option selection facts
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `from` (query) — Start date (ISO 8601, e.g. 2026-01-01)
  - `to` (query) — End date (ISO 8601, e.g. 2026-03-31)
  - `product_id` (query) — Filter by product ID
- `GET /api/v1/analytics/part-usage` — List part usage facts
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `from` (query) — Start date (ISO 8601, e.g. 2026-01-01)
  - `to` (query) — End date (ISO 8601, e.g. 2026-03-31)
  - `product_id` (query) — Filter by product ID
- `GET /api/v1/analytics/pipeline` — List pipeline snapshots
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `from` (query) — Start date (ISO 8601, e.g. 2026-01-01)
  - `to` (query) — End date (ISO 8601, e.g. 2026-03-31)
- `GET /api/v1/analytics/quotes` — List quote analytics
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `from` (query) — Start date (ISO 8601, e.g. 2026-01-01)
  - `to` (query) — End date (ISO 8601, e.g. 2026-03-31)

## Area Groups

- `GET /api/v1/area-groups` — List area groups
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `product_id` (query) — Filter by product
- `POST /api/v1/area-groups` — Create an area group
- `DELETE /api/v1/area-groups/{id}` — Delete an area group
- `GET /api/v1/area-groups/{id}` — Get an area group
- `PATCH /api/v1/area-groups/{id}` — Partially update an area group
- `PUT /api/v1/area-groups/{id}` — Update an area group
- `GET /api/v1/area-groups/{id}/areas` — List areas in an area group

## Areas

- `GET /api/v1/areas` — List areas
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `product_id` (query) — Filter by product
  - `search` (query) — Filter by name (case-insensitive partial match)
- `POST /api/v1/areas` — Create an area
  - Request body: `AreaCreateRequest`
- `GET /api/v1/areas/library` — List library areas
- `GET /api/v1/areas/{areaId}/options` — List area options
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
- `GET /api/v1/areas/{areaId}/price-overrides` — List area price overrides
- `POST /api/v1/areas/{areaId}/price-overrides` — Create area price override
- `POST /api/v1/areas/{areaId}/price-overrides/replace` — Replace all area price overrides
- `DELETE /api/v1/areas/{areaId}/price-overrides/{overrideId}` — Delete area price override
- `PATCH /api/v1/areas/{areaId}/price-overrides/{overrideId}` — Partially update area price override
- `PUT /api/v1/areas/{areaId}/price-overrides/{overrideId}` — Update area price override
- `DELETE /api/v1/areas/{id}` — Delete an area
- `GET /api/v1/areas/{id}` — Get an area
- `PATCH /api/v1/areas/{id}` — Partially update an area
  - Request body: `AreaUpdateRequest`
- `PUT /api/v1/areas/{id}` — Update an area
  - Request body: `AreaUpdateRequest`
- `DELETE /api/v1/areas/{id}/content` — Delete area rich content
  - `language` (query) — Language code to delete (omit for all)
- `GET /api/v1/areas/{id}/content` — Get area rich content
  - `language` (query) — Language code (e.g. 'DE', 'EN')
- `PUT /api/v1/areas/{id}/content` — Update area rich content
  - Request body: `AreaContentUpdateRequest`
- `POST /api/v1/areas/{id}/content/images` — Upload content image
- `GET /api/v1/areas/{id}/groups` — List groups in an area

## Attributes

- `GET /api/v1/attributes` — List technical attributes
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
- `POST /api/v1/attributes` — Create an attribute
  - Request body: `AttributeCreateRequest`
- `DELETE /api/v1/attributes/values/{id}` — Delete an attribute value
- `PATCH /api/v1/attributes/values/{id}` — Partially update an attribute value
- `PUT /api/v1/attributes/values/{id}` — Update an attribute value
- `DELETE /api/v1/attributes/{id}` — Delete an attribute
- `GET /api/v1/attributes/{id}` — Get an attribute
- `PATCH /api/v1/attributes/{id}` — Partially update an attribute
  - Request body: `AttributeUpdateRequest`
- `PUT /api/v1/attributes/{id}` — Update an attribute
  - Request body: `AttributeUpdateRequest`
- `GET /api/v1/attributes/{id}/values` — List attribute values
  - `element_type` (query) — Filter: product, area, option
  - `element_id` (query) — Filter by element ID
- `POST /api/v1/attributes/{id}/values` — Create an attribute value

## Baselines

- `GET /api/v1/baselines` — List baselines
  - `product_id` (query (required)) — Product ID (required)
- `POST /api/v1/baselines` — Create a baseline
  - Request body: `BaselineCreateRequest`
- `DELETE /api/v1/baselines/{id}` — Delete a baseline
- `GET /api/v1/baselines/{id}` — Get a baseline

## Batch

- `POST /api/v1/areas/batch` — Batch areas operations
  - Request body: `ResourceBatchRequest`
- `POST /api/v1/batch` — Universal batch operations
  - Request body: `UniversalBatchRequest`
- `POST /api/v1/bom/batch` — Batch bom operations
  - Request body: `ResourceBatchRequest`
- `POST /api/v1/customers/batch` — Batch customers operations
  - Request body: `ResourceBatchRequest`
- `POST /api/v1/groups/batch` — Batch groups operations
  - Request body: `ResourceBatchRequest`
- `POST /api/v1/options/batch` — Batch options operations
  - Request body: `ResourceBatchRequest`
- `POST /api/v1/parts/batch` — Batch parts operations
  - Request body: `ResourceBatchRequest`
- `POST /api/v1/products/batch` — Batch products operations
  - Request body: `ResourceBatchRequest`

## Branches

- `GET /api/v1/branches` — List branches
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
- `POST /api/v1/branches` — Create branch
  - Request body: `BranchCreateRequest`
- `DELETE /api/v1/branches/{branchId}` — Delete branch
- `GET /api/v1/branches/{branchId}` — Get branch

## Catalog Filters

- `GET /api/v1/catalog-filters` — List catalog filter dimensions
- `POST /api/v1/catalog-filters` — Create a catalog filter dimension
  - Request body: `CatalogFilterDimensionCreateRequest`
- `POST /api/v1/catalog-filters/reorder` — Reorder catalog filter dimensions
  - Request body: `CatalogFilterReorderRequest`
- `DELETE /api/v1/catalog-filters/{id}` — Delete a catalog filter dimension
- `GET /api/v1/catalog-filters/{id}` — Get a catalog filter dimension
- `PUT /api/v1/catalog-filters/{id}` — Update a catalog filter dimension
  - Request body: `CatalogFilterDimensionUpdateRequest`
- `POST /api/v1/catalog-filters/{id}/values` — Add a value to a catalog filter dimension
  - Request body: `CatalogFilterValueCreateRequest`
- `POST /api/v1/catalog-filters/{id}/values/reorder` — Reorder values within a dimension
  - Request body: `CatalogFilterValueReorderRequest`
- `DELETE /api/v1/catalog-filters/{id}/values/{valueId}` — Delete a catalog filter value
- `PUT /api/v1/catalog-filters/{id}/values/{valueId}` — Update a catalog filter value
  - Request body: `CatalogFilterValueUpdateRequest`

## Change Orders

- `DELETE /api/v1/change-orders/{ecoId}` — Delete change order
- `GET /api/v1/change-orders/{ecoId}` — Get change order
- `PATCH /api/v1/change-orders/{ecoId}` — Partially update change order
  - Request body: `ChangeOrderUpdateRequest`
- `PUT /api/v1/change-orders/{ecoId}` — Update change order
  - Request body: `ChangeOrderUpdateRequest`
- `GET /api/v1/change-orders/{ecoId}/approvals` — List change approvals
- `POST /api/v1/change-orders/{ecoId}/approvals` — Create change approval
  - Request body: `ApprovalCreateRequest`
- `PATCH /api/v1/change-orders/{ecoId}/approvals/{approvalId}` — Partially update change approval
  - Request body: `ApprovalUpdateRequest`
- `PUT /api/v1/change-orders/{ecoId}/approvals/{approvalId}` — Update change approval
  - Request body: `ApprovalUpdateRequest`
- `GET /api/v1/change-orders/{ecoId}/impacts` — List change impacts
- `POST /api/v1/change-orders/{ecoId}/impacts` — Create change impact
  - Request body: `ChangeImpactCreateRequest`
- `DELETE /api/v1/change-orders/{ecoId}/impacts/{impactId}` — Delete change impact
- `PATCH /api/v1/change-orders/{ecoId}/impacts/{impactId}` — Partially update change impact
  - Request body: `ChangeImpactUpdateRequest`
- `PUT /api/v1/change-orders/{ecoId}/impacts/{impactId}` — Update change impact
  - Request body: `ChangeImpactUpdateRequest`

## Change Requests

- `GET /api/v1/change-requests` — List change requests
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `state` (query) — Filter by state (Open, Review, Approved, Rejected)
- `POST /api/v1/change-requests` — Create change request
  - Request body: `ChangeRequestCreateRequest`
- `DELETE /api/v1/change-requests/{ecrId}` — Delete change request
- `GET /api/v1/change-requests/{ecrId}` — Get change request
- `PATCH /api/v1/change-requests/{ecrId}` — Partially update change request
  - Request body: `ChangeRequestUpdateRequest`
- `PUT /api/v1/change-requests/{ecrId}` — Update change request
  - Request body: `ChangeRequestUpdateRequest`
- `GET /api/v1/change-requests/{ecrId}/orders` — List change orders for request
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
- `POST /api/v1/change-requests/{ecrId}/orders` — Create change order
  - Request body: `ChangeOrderCreateRequest`

## Company

- `GET /api/v1/company` — Get company settings
- `PATCH /api/v1/company` — Partially update company settings
  - Request body: `CompanySettingsUpdateRequest`
- `PUT /api/v1/company` — Update company settings
  - Request body: `CompanySettingsUpdateRequest`
- `GET /api/v1/company/configurator-settings` — Get configurator settings
- `PATCH /api/v1/company/configurator-settings` — Partially update configurator settings
- `PUT /api/v1/company/configurator-settings` — Update configurator settings
- `GET /api/v1/company/connector-settings` — Get connector settings
- `PATCH /api/v1/company/connector-settings` — Partially update connector settings
- `PUT /api/v1/company/connector-settings` — Update connector settings
- `GET /api/v1/company/contacts` — List company contacts
- `POST /api/v1/company/contacts` — Create a company contact
- `DELETE /api/v1/company/contacts/{id}` — Delete a company contact
- `PATCH /api/v1/company/contacts/{id}` — Partially update a company contact
- `PUT /api/v1/company/contacts/{id}` — Update a company contact

## Configurations

- `GET /api/v1/configurations` — List saved configurations
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `product_id` (query) — Filter by product
- `POST /api/v1/configurations/calculate` — Calculate a configuration
  - Request body: `ConfigurationCalculateRequest`
- `GET /api/v1/configurations/states/by-code/{code}` — Get configuration state by code
- `GET /api/v1/configurations/states/by-code/{code}/parts` — Get configured parts (BOM)
  - `limit` (query) — Max parts per page (default 200, max 500)
  - `offset` (query) — Number of parts to skip
- `GET /api/v1/configurations/states/by-code/{code}/selections` — Get enriched selected options
- `GET /api/v1/configurations/states/{hash}` — Get configuration state by hash
- `GET /api/v1/configurations/{id}` — Get a saved configuration
- `POST /api/v1/configurations/{id}/finalize` — Finalize a configuration

## Connectors

- `GET /api/v1/connectors` — List connectors
- `POST /api/v1/connectors` — Create a connector
  - Request body: `ConnectorCreateRequest`
- `DELETE /api/v1/connectors/endpoints/{id}` — Delete a connector endpoint
- `GET /api/v1/connectors/jobs` — List connector jobs
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `status` (query) — Filter by status
- `GET /api/v1/connectors/jobs/{id}` — Get a connector job
- `POST /api/v1/connectors/jobs/{id}/replay` — Replay a connector job
- `GET /api/v1/connectors/jobs/{jobId}/logs` — List job logs
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
- `DELETE /api/v1/connectors/tasks/{id}` — Delete a connector task
- `GET /api/v1/connectors/tasks/{id}` — Get a connector task
- `POST /api/v1/connectors/tasks/{id}/run` — Run a connector task
- `GET /api/v1/connectors/triggers` — List connector triggers
- `POST /api/v1/connectors/triggers` — Create a connector trigger
- `DELETE /api/v1/connectors/triggers/{id}` — Delete a connector trigger
- `PUT /api/v1/connectors/triggers/{id}` — Update a connector trigger
- `DELETE /api/v1/connectors/{id}` — Delete a connector
- `GET /api/v1/connectors/{id}` — Get a connector
- `PATCH /api/v1/connectors/{id}` — Partially update a connector
  - Request body: `ConnectorUpdateRequest`
- `PUT /api/v1/connectors/{id}` — Update a connector
  - Request body: `ConnectorUpdateRequest`
- `GET /api/v1/connectors/{id}/endpoints` — List connector endpoints
- `POST /api/v1/connectors/{id}/endpoints` — Create a connector endpoint
  - Request body: `EndpointCreateRequest`
- `GET /api/v1/connectors/{id}/tasks` — List connector tasks
- `POST /api/v1/connectors/{id}/tasks` — Create a connector task
  - Request body: `TaskCreateRequest`

## Constraints

- `GET /api/v1/constraints` — List option-level forbidden combinations
  - `product_id` (query (required)) — Product ID
- `POST /api/v1/constraints` — Replace option-level forbidden combinations
- `GET /api/v1/constraints/area` — List area-level forbidden combinations
  - `product_id` (query (required)) — Product ID
- `POST /api/v1/constraints/area` — Replace area-level forbidden combinations
- `POST /api/v1/constraints/check` — Check if a combination is forbidden
  - Request body: `ConstraintCheckRequest`
- `GET /api/v1/constraints/rules` — List constraint rules
  - `product_id` (query) — Filter by product
  - `area_id` (query) — Filter by area
- `POST /api/v1/constraints/rules` — Create a constraint rule
  - Request body: `ForbiddenRuleCreateRequest`
- `DELETE /api/v1/constraints/rules/{id}` — Delete a constraint rule
- `GET /api/v1/constraints/rules/{id}` — Get a constraint rule
- `PATCH /api/v1/constraints/rules/{id}` — Partially update a constraint rule
  - Request body: `ForbiddenRuleUpdateRequest`
- `PUT /api/v1/constraints/rules/{id}` — Update a constraint rule
  - Request body: `ForbiddenRuleUpdateRequest`

## Customer Links

- `GET /api/v1/customer-links` — List customer links
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `product_id` (query) — Filter by product
- `POST /api/v1/customer-links` — Create a customer link
- `DELETE /api/v1/customer-links/{id}` — Delete a customer link
- `GET /api/v1/customer-links/{id}` — Get a customer link
- `PATCH /api/v1/customer-links/{id}` — Partially update a customer link
- `PUT /api/v1/customer-links/{id}` — Update a customer link

## Customers

- `GET /api/v1/customers` — List customers
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `search` (query) — Filter by organization, email, or ID (case-insensitive)
  - `country` (query) — Filter by address country
- `POST /api/v1/customers` — Create a customer
  - Request body: `CustomerCreateRequest`
- `GET /api/v1/customers/search` — Search customers
  - `q` (query (required)) — Search query (min 2 chars)
- `GET /api/v1/customers/{customerId}/configurations` — List customer configurations
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
- `GET /api/v1/customers/{customerId}/opportunities` — List customer opportunities
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
- `GET /api/v1/customers/{customerId}/quotes` — List customer quotes
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
- `DELETE /api/v1/customers/{id}` — Delete a customer
- `GET /api/v1/customers/{id}` — Get a customer
- `PATCH /api/v1/customers/{id}` — Partially update a customer
  - Request body: `CustomerUpdateRequest`
- `PUT /api/v1/customers/{id}` — Update a customer
  - Request body: `CustomerUpdateRequest`
- `GET /api/v1/customers/{id}/contacts` — List contacts for a customer
- `POST /api/v1/customers/{id}/contacts` — Add a contact to a customer
  - Request body: `ContactCreateRequest`
- `DELETE /api/v1/customers/{id}/contacts/{contact_id}` — Remove a contact
- `PUT /api/v1/customers/{id}/contacts/{contact_id}` — Update a contact
  - Request body: `ContactUpdateRequest`

## Documents

- `GET /api/v1/documents/content-blocks` — List content blocks
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `product_id` (query) — Filter by product
  - `directory_id` (query) — Filter by directory
  - `tag` (query) — Filter by tag
  - `search` (query) — Search by title or key
  - `is_active` (query) — Filter by active status
- `POST /api/v1/documents/content-blocks` — Create a content block
  - Request body: `ContentBlockCreateRequest`
- `POST /api/v1/documents/content-blocks/batch` — Batch content block operations
  - Request body: `ResourceBatchRequest`
- `DELETE /api/v1/documents/content-blocks/images` — Delete EditorJS image by URL
- `POST /api/v1/documents/content-blocks/images` — Upload EditorJS image
- `DELETE /api/v1/documents/content-blocks/{id}` — Delete a content block
- `GET /api/v1/documents/content-blocks/{id}` — Get a content block with locales
- `PUT /api/v1/documents/content-blocks/{id}` — Update a content block
  - Request body: `ContentBlockUpdateRequest`
- `GET /api/v1/documents/content-blocks/{id}/locales` — List content block locales
- `POST /api/v1/documents/content-blocks/{id}/locales` — Create or upsert a content block locale
  - Request body: `ContentBlockLocaleCreateRequest`
- `DELETE /api/v1/documents/content-blocks/{id}/locales/{locale_id}` — Delete a content block locale
- `GET /api/v1/documents/content-blocks/{id}/locales/{locale_id}` — Get a content block locale
- `PUT /api/v1/documents/content-blocks/{id}/locales/{locale_id}` — Update a content block locale
  - Request body: `ContentBlockLocaleUpdateRequest`
- `POST /api/v1/documents/content-blocks/{id}/locales/{locale_id}/translate` — Translate locale to target language
  - Request body: `TranslateRequest`
- `POST /api/v1/documents/content-blocks/{id}/set-version` — Set current version
- `GET /api/v1/documents/content-directories` — List content directories (tree)
- `POST /api/v1/documents/content-directories` — Create a content directory
  - Request body: `ContentDirectoryCreateRequest`
- `DELETE /api/v1/documents/content-directories/{id}` — Delete a content directory
- `GET /api/v1/documents/content-directories/{id}` — Get a content directory
- `PUT /api/v1/documents/content-directories/{id}` — Update a content directory
  - Request body: `ContentDirectoryUpdateRequest`
- `GET /api/v1/documents/instances` — List document instances
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `template_id` (query) — Filter by template
  - `quote_id` (query) — Filter by quote
  - `context_type` (query) — Filter by context type
- `POST /api/v1/documents/instances` — Create a document instance (enriched)
  - Request body: `InstanceCreateRequest`
- `DELETE /api/v1/documents/instances/{id}` — Delete a document instance
- `GET /api/v1/documents/instances/{id}` — Get a document instance
- `POST /api/v1/documents/instances/{id}/attachments` — Create instance attachment
  - Request body: `InstanceAttachmentCreateRequest`
- `DELETE /api/v1/documents/instances/{id}/attachments/{att_id}` — Delete instance attachment
- `PUT /api/v1/documents/instances/{id}/attachments/{att_id}` — Update instance attachment
  - Request body: `InstanceAttachmentUpdateRequest`
- `GET /api/v1/documents/instances/{id}/blocks` — List instance blocks (tree)
  - `include_attachments` (query) — Include attachment data
- `DELETE /api/v1/documents/instances/{id}/blocks/{block_id}` — Delete an instance block
- `GET /api/v1/documents/instances/{id}/blocks/{block_id}` — Get an instance block
- `PUT /api/v1/documents/instances/{id}/blocks/{block_id}` — Update an instance block
  - Request body: `InstanceBlockUpdateRequest`
- `GET /api/v1/documents/instances/{id}/public-links` — List public links
- `DELETE /api/v1/documents/instances/{id}/public-links/{link_id}` — Delete a public link
- `GET /api/v1/documents/instances/{id}/public-links/{link_id}` — Get a public link
- `POST /api/v1/documents/instances/{id}/publish` — Publish document instance
  - Request body: `PublishRequest`
- `GET /api/v1/documents/templates` — List document templates
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `doc_type` (query) — Filter by type
  - `product_id` (query) — Filter by product
- `POST /api/v1/documents/templates` — Create a document template
  - Request body: `DocumentTemplateCreateRequest`
- `DELETE /api/v1/documents/templates/{id}` — Delete a document template
- `GET /api/v1/documents/templates/{id}` — Get a document template
- `PATCH /api/v1/documents/templates/{id}` — Partially update a document template
  - Request body: `DocumentTemplateUpdateRequest`
- `PUT /api/v1/documents/templates/{id}` — Update a document template
  - Request body: `DocumentTemplateUpdateRequest`
- `POST /api/v1/documents/templates/{id}/clone` — Deep clone a template
  - Request body: `CloneRequest`
- `GET /api/v1/documents/templates/{id}/structure` — Get template structure tree
  - `language` (query) — Resolve titles for this language
- `POST /api/v1/documents/templates/{id}/structure/batch` — Batch structure operations
  - Request body: `ResourceBatchRequest`
- `POST /api/v1/documents/templates/{id}/structure/blocks` — Create a structure block
  - Request body: `StructureBlockCreateRequest`
- `DELETE /api/v1/documents/templates/{id}/structure/blocks/{block_id}` — Delete a structure block (cascade)
- `GET /api/v1/documents/templates/{id}/structure/blocks/{block_id}` — Get a structure block
- `PUT /api/v1/documents/templates/{id}/structure/blocks/{block_id}` — Update a structure block
  - Request body: `StructureBlockUpdateRequest`
- `GET /api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments` — List block attachments
- `POST /api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments` — Attach content block
  - Request body: `AttachmentCreateRequest`
- `POST /api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments/reorder` — Reorder attachments
  - Request body: `ReorderRequest`
- `DELETE /api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments/{att_id}` — Remove an attachment
- `GET /api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments/{att_id}` — Get an attachment
- `PUT /api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments/{att_id}` — Update an attachment
  - Request body: `AttachmentUpdateRequest`
- `GET /api/v1/documents/templates/{id}/structure/blocks/{block_id}/locales` — List structure block locales
- `DELETE /api/v1/documents/templates/{id}/structure/blocks/{block_id}/locales/{lang}` — Delete structure block locale
- `PUT /api/v1/documents/templates/{id}/structure/blocks/{block_id}/locales/{lang}` — Upsert structure block locale title
  - Request body: `StructureBlockLocaleUpsertRequest`
- `POST /api/v1/documents/templates/{id}/structure/blocks/{block_id}/move` — Move block to new parent
  - Request body: `MoveRequest`
- `POST /api/v1/documents/templates/{id}/structure/reorder` — Reorder structure blocks
  - Request body: `ReorderRequest`
- `POST /api/v1/documents/templates/{id}/translate` — Translate entire template
  - Request body: `TemplateTranslateRequest`
- `POST /api/v1/documents/templates/{id}/variants` — Create an inheritance variant
  - Request body: `VariantCreateRequest`

## Export

- `GET /api/v1/customers/export` — Export customers (NDJSON)
  - `updated_after` (query) — ISO 8601 timestamp for incremental sync
- `GET /api/v1/parts/export` — Export parts (NDJSON)
  - `updated_after` (query) — ISO 8601 timestamp for incremental sync
- `GET /api/v1/products/export` — Export products (NDJSON)
  - `updated_after` (query) — ISO 8601 timestamp for incremental sync

## Groups

- `GET /api/v1/groups` — List groups
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `search` (query) — Filter by name (case-insensitive partial match)
  - `area_id` (query) — Filter by area assignment
- `POST /api/v1/groups` — Create a group
  - Request body: `GroupCreateRequest`
- `DELETE /api/v1/groups/{id}` — Delete a group
- `GET /api/v1/groups/{id}` — Get a group
- `PATCH /api/v1/groups/{id}` — Partially update a group
  - Request body: `GroupUpdateRequest`
- `PUT /api/v1/groups/{id}` — Update a group
  - Request body: `GroupUpdateRequest`
- `GET /api/v1/groups/{id}/areas` — List areas linked to a group
- `POST /api/v1/groups/{id}/areas` — Link a group to areas
  - Request body: `GroupAreaLinkRequest`
- `DELETE /api/v1/groups/{id}/areas/{area_id}` — Unlink a group from an area
- `POST /api/v1/groups/{id}/duplicate` — Duplicate a group
- `GET /api/v1/groups/{id}/options` — List options in a group

## Health

- `GET /api/v1/health` — Health check

## Images

- `DELETE /api/v1/areas/{areaId}/image` — Delete area image
- `POST /api/v1/areas/{areaId}/image` — Upload area image
  - Request: multipart file upload
- `DELETE /api/v1/options/{optionId}/image` — Delete option image
- `POST /api/v1/options/{optionId}/image` — Upload option image
  - Request: multipart file upload
- `DELETE /api/v1/options/{optionId}/image/areas/{areaId}` — Delete option area override image
- `POST /api/v1/options/{optionId}/image/areas/{areaId}` — Upload option area override image
  - Request: multipart file upload
- `DELETE /api/v1/products/{productId}/background` — Delete product background
- `POST /api/v1/products/{productId}/background` — Upload product background
  - Request: multipart file upload
- `GET /api/v1/products/{productId}/gallery` — List gallery images
- `POST /api/v1/products/{productId}/gallery` — Upload gallery image
  - Request: multipart file upload
- `POST /api/v1/products/{productId}/gallery/reorder` — Reorder gallery images
  - Request body: `GalleryReorderRequest`
- `DELETE /api/v1/products/{productId}/gallery/{imageId}` — Delete gallery image
- `GET /api/v1/products/{productId}/gallery/{imageId}` — Get gallery image
- `PUT /api/v1/products/{productId}/gallery/{imageId}` — Replace gallery image
  - Request: multipart file upload
- `DELETE /api/v1/products/{productId}/image` — Delete product image
- `POST /api/v1/products/{productId}/image` — Upload product image
  - Request: multipart file upload

## Inbound Webhooks

- `POST /api/v1/inbound/connectors/tasks/{id}/trigger` — Trigger a connector task
- `POST /api/v1/inbound/customers` — Upsert an inbound customer
- `POST /api/v1/inbound/customers/batch` — Batch upsert inbound customers
- `POST /api/v1/inbound/events` — Send an inbound event
- `POST /api/v1/inbound/opportunities` — Create an inbound opportunity
- `POST /api/v1/inbound/parts/batch` — Batch upsert inbound parts
- `POST /api/v1/inbound/triggers/{suffix}` — Fire a webhook trigger by path

## Item Revisions

- `GET /api/v1/parts/{partId}/revisions` — List revisions for a part
- `POST /api/v1/parts/{partId}/revisions` — Create a revision
  - Request body: `ItemRevisionCreateRequest`
- `DELETE /api/v1/parts/{partId}/revisions/{revisionId}` — Delete a draft revision
- `GET /api/v1/parts/{partId}/revisions/{revisionId}` — Get a revision
- `PUT /api/v1/parts/{partId}/revisions/{revisionId}` — Update a draft revision
  - Request body: `ItemRevisionUpdateRequest`
- `POST /api/v1/parts/{partId}/revisions/{revisionId}/obsolete` — Obsolete a revision
- `POST /api/v1/parts/{partId}/revisions/{revisionId}/release` — Release a revision

## Languages

- `GET /api/v1/languages` — List languages
- `POST /api/v1/languages` — Create a language
  - Request body: `LanguageCreateRequest`
- `POST /api/v1/languages/reorder` — Reorder languages
  - Request body: `LanguageReorderRequest`
- `DELETE /api/v1/languages/{id}` — Delete a language
- `GET /api/v1/languages/{id}` — Get a language
- `PATCH /api/v1/languages/{id}` — Partially update a language
  - Request body: `LanguageUpdateRequest`
- `PUT /api/v1/languages/{id}` — Update a language
  - Request body: `LanguageUpdateRequest`

## Offer Sections

- `GET /api/v1/products/{productId}/offer-sections` — List offer sections
- `POST /api/v1/products/{productId}/offer-sections` — Create offer section
  - Request body: `OfferSectionCreateRequest`
- `POST /api/v1/products/{productId}/offer-sections/reorder` — Reorder offer sections
  - Request body: `OfferSectionReorderRequest`
- `DELETE /api/v1/products/{productId}/offer-sections/{sectionId}` — Delete offer section
- `GET /api/v1/products/{productId}/offer-sections/{sectionId}` — Get offer section
- `PATCH /api/v1/products/{productId}/offer-sections/{sectionId}` — Partially update offer section
  - Request body: `OfferSectionUpdateRequest`
- `PUT /api/v1/products/{productId}/offer-sections/{sectionId}` — Update offer section
  - Request body: `OfferSectionUpdateRequest`
- `GET /api/v1/products/{productId}/offer-sections/{sectionId}/content` — List offer section content
  - `language` (query) — Filter by language code
- `PUT /api/v1/products/{productId}/offer-sections/{sectionId}/content` — Upsert offer section content
  - Request body: `OfferSectionContentUpsertRequest`
- `DELETE /api/v1/products/{productId}/offer-sections/{sectionId}/content/{contentId}` — Delete offer section content

## Opportunities

- `GET /api/v1/opportunities` — List opportunities
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `stage` (query) — Filter by stage
  - `customer_id` (query) — Filter by customer
  - `search` (query) — Search by name
- `POST /api/v1/opportunities` — Create an opportunity
  - Request body: `OpportunityCreateRequest`
- `DELETE /api/v1/opportunities/{id}` — Delete an opportunity
- `GET /api/v1/opportunities/{id}` — Get an opportunity
- `PATCH /api/v1/opportunities/{id}` — Partially update an opportunity
  - Request body: `OpportunityUpdateRequest`
- `PUT /api/v1/opportunities/{id}` — Update an opportunity
  - Request body: `OpportunityUpdateRequest`
- `GET /api/v1/opportunities/{id}/quotes` — List quotes for an opportunity

## Options

- `GET /api/v1/options` — List options
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `group_id` (query) — Filter by group
  - `search` (query) — Filter by name (case-insensitive partial match)
- `POST /api/v1/options` — Create an option
  - Request body: `OptionCreateRequest`
- `DELETE /api/v1/options/{id}` — Delete an option
- `GET /api/v1/options/{id}` — Get an option
- `PATCH /api/v1/options/{id}` — Partially update an option
  - Request body: `OptionUpdateRequest`
- `PUT /api/v1/options/{id}` — Update an option
  - Request body: `OptionUpdateRequest`
- `GET /api/v1/options/{id}/effective` — Get effective price for an option
  - `price_list_id` (query) — Price list ID
  - `area_id` (query) — Area ID
- `GET /api/v1/options/{optionId}/advanced-prices` — List advanced prices
- `POST /api/v1/options/{optionId}/advanced-prices` — Create an advanced price
- `DELETE /api/v1/options/{optionId}/advanced-prices/{priceId}` — Delete an advanced price
- `PATCH /api/v1/options/{optionId}/advanced-prices/{priceId}` — Partially update an advanced price
- `PUT /api/v1/options/{optionId}/advanced-prices/{priceId}` — Update an advanced price
- `GET /api/v1/options/{optionId}/area-config` — Get area-specific config for an option
  - `area_id` (query (required)) — Area ID
- `PUT /api/v1/options/{optionId}/area-config` — Set area-specific config for an option
  - `area_id` (query (required)) — Area ID

## Part Documents

- `GET /api/v1/part-documents` — List part documents
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `doc_type` (query) — Filter by doc type (CAD, Drawing, Spec, Manual, Other)
  - `lifecycle_state` (query) — Filter by lifecycle state
  - `search` (query) — Search by document number
- `POST /api/v1/part-documents` — Create a part document
  - Request body: `PartDocumentCreateRequest`
- `DELETE /api/v1/part-documents/{id}` — Delete a part document
- `GET /api/v1/part-documents/{id}` — Get a part document
- `PATCH /api/v1/part-documents/{id}` — Partially update a part document
  - Request body: `PartDocumentUpdateRequest`
- `PUT /api/v1/part-documents/{id}` — Update a part document
  - Request body: `PartDocumentUpdateRequest`
- `GET /api/v1/parts/{partId}/document-links` — List document links for a part
- `POST /api/v1/parts/{partId}/document-links` — Create a document link for a part
  - Request body: `PartDocumentLinkCreateRequest`
- `DELETE /api/v1/parts/{partId}/document-links/{linkId}` — Remove a document link
- `GET /api/v1/parts/{partId}/revisions/{revisionId}/document-links` — List document links for a revision
- `POST /api/v1/parts/{partId}/revisions/{revisionId}/document-links` — Create a document link for a revision
  - Request body: `PartDocumentLinkCreateRequest`

## Parts

- `GET /api/v1/parts` — List parts
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `status` (query) — Filter by lifecycle status
  - `part_type` (query) — Filter by part type
  - `search` (query) — Search by number or name
- `POST /api/v1/parts` — Create a part
  - Request body: `PartCreateRequest`
- `DELETE /api/v1/parts/bom/{id}` — Delete a BOM item
- `PATCH /api/v1/parts/bom/{id}` — Partially update a BOM item
  - Request body: `BomItemUpdateRequest`
- `PUT /api/v1/parts/bom/{id}` — Update a BOM item
  - Request body: `BomItemUpdateRequest`
- `GET /api/v1/parts/groups` — List part groups
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
- `POST /api/v1/parts/groups` — Create part group
  - Request body: `PartGroupCreateRequest`
- `DELETE /api/v1/parts/groups/{groupId}` — Delete part group
- `GET /api/v1/parts/groups/{groupId}` — Get part group
- `PATCH /api/v1/parts/groups/{groupId}` — Partially update part group
  - Request body: `PartGroupUpdateRequest`
- `PUT /api/v1/parts/groups/{groupId}` — Update part group
  - Request body: `PartGroupUpdateRequest`
- `DELETE /api/v1/parts/placements/{id}` — Delete a part placement
- `PATCH /api/v1/parts/placements/{id}` — Partially update a part placement
  - Request body: `PartPlacementUpdateRequest`
- `PUT /api/v1/parts/placements/{id}` — Update a part placement
  - Request body: `PartPlacementUpdateRequest`
- `DELETE /api/v1/parts/{id}` — Delete a part
- `GET /api/v1/parts/{id}` — Get a part
- `PATCH /api/v1/parts/{id}` — Partially update a part
  - Request body: `PartUpdateRequest`
- `PUT /api/v1/parts/{id}` — Update a part
  - Request body: `PartUpdateRequest`
- `GET /api/v1/parts/{id}/bom` — List BOM children
- `POST /api/v1/parts/{id}/bom` — Add a BOM child
  - Request body: `BomItemCreateRequest`
- `GET /api/v1/parts/{id}/bom/flat` — Get flattened BOM
  - `max_depth` (query) — Maximum traversal depth
- `GET /api/v1/parts/{id}/bom/tree` — Get multi-level BOM tree
  - `max_depth` (query) — Maximum traversal depth
  - `max_nodes` (query) — Maximum number of nodes to return
- `POST /api/v1/parts/{id}/bom/validate` — Validate BOM integrity
- `GET /api/v1/parts/{id}/placements` — List part placements
- `POST /api/v1/parts/{id}/placements` — Create a part placement
  - Request body: `PartPlacementCreateRequest`
- `GET /api/v1/parts/{id}/where-used` — Find where a part is used
- `GET /api/v1/parts/{partId}/changelog` — List part changelog
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)

## Price Lists

- `GET /api/v1/price-lists` — List price lists
- `POST /api/v1/price-lists` — Create a price list
  - Request body: `PriceListCreateRequest`
- `POST /api/v1/price-lists/reorder` — Reorder price lists
  - Request body: `PriceListReorderRequest`
- `DELETE /api/v1/price-lists/{id}` — Delete a price list
- `GET /api/v1/price-lists/{id}` — Get a price list
- `PATCH /api/v1/price-lists/{id}` — Partially update a price list
  - Request body: `PriceListUpdateRequest`
- `PUT /api/v1/price-lists/{id}` — Update a price list
  - Request body: `PriceListUpdateRequest`
- `GET /api/v1/price-lists/{priceListId}/overrides` — List price list overrides
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)

## Price Overrides

- `GET /api/v1/options/{optionId}/price-overrides` — List price overrides for an option
- `POST /api/v1/options/{optionId}/price-overrides` — Create a price override
  - Request body: `PriceOverrideCreateRequest`
- `POST /api/v1/options/{optionId}/price-overrides/replace` — Replace all price overrides
  - Request body: `PriceOverrideReplaceRequest`
- `DELETE /api/v1/options/{optionId}/price-overrides/{overrideId}` — Delete a price override
- `PATCH /api/v1/options/{optionId}/price-overrides/{overrideId}` — Partially update a price override
  - Request body: `PriceOverrideUpdateRequest`
- `PUT /api/v1/options/{optionId}/price-overrides/{overrideId}` — Update a price override
  - Request body: `PriceOverrideUpdateRequest`

## Product Media

- `GET /api/v1/products/{productId}/models` — List 3D model links
- `POST /api/v1/products/{productId}/models` — Create 3D model link
  - Request body: `ModelLinkCreateRequest`
- `POST /api/v1/products/{productId}/models/reorder` — Reorder 3D model links
  - Request body: `ModelLinkReorderRequest`
- `DELETE /api/v1/products/{productId}/models/{modelId}` — Delete 3D model link
- `PUT /api/v1/products/{productId}/models/{modelId}` — Update 3D model link
  - Request body: `ModelLinkUpdateRequest`
- `GET /api/v1/products/{productId}/videos` — List video links
- `POST /api/v1/products/{productId}/videos` — Create video link
  - Request body: `VideoLinkCreateRequest`
- `POST /api/v1/products/{productId}/videos/reorder` — Reorder video links
  - Request body: `VideoLinkReorderRequest`
- `DELETE /api/v1/products/{productId}/videos/{videoId}` — Delete video link
- `PUT /api/v1/products/{productId}/videos/{videoId}` — Update video link
  - Request body: `VideoLinkUpdateRequest`

## Products

- `GET /api/v1/products` — List products
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `search` (query) — Filter by name (case-insensitive partial match)
  - `status` (query) — Filter: `active` (default), `inactive`, or `all`
- `POST /api/v1/products` — Create a product
  - Request body: `ProductCreateRequest`
- `POST /api/v1/products/reorder` — Reorder products
  - Request body: `ProductReorderRequest`
- `DELETE /api/v1/products/{id}` — Delete a product
- `GET /api/v1/products/{id}` — Get a product
  - `expand` (query) — Comma-separated list of expansions: `areas`, `gallery`
- `PATCH /api/v1/products/{id}` — Partially update a product
  - Request body: `ProductUpdateRequest`
- `PUT /api/v1/products/{id}` — Update a product
  - Request body: `ProductUpdateRequest`
- `GET /api/v1/products/{productId}/areas` — List assigned areas
- `POST /api/v1/products/{productId}/areas` — Assign an area to a product
- `POST /api/v1/products/{productId}/areas/reorder` — Reorder product areas
- `POST /api/v1/products/{productId}/areas/replace` — Replace all product area assignments
- `DELETE /api/v1/products/{productId}/areas/{areaId}` — Remove area from product
- `GET /api/v1/products/{productId}/configurations` — List product configurations
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
- `GET /api/v1/products/{productId}/price-overrides` — List product price overrides
- `POST /api/v1/products/{productId}/price-overrides` — Create product price override
  - Request body: `ProductPriceOverrideCreateRequest`
- `POST /api/v1/products/{productId}/price-overrides/replace` — Replace all product price overrides
  - Request body: `ProductPriceOverrideReplaceRequest`
- `DELETE /api/v1/products/{productId}/price-overrides/{overrideId}` — Delete product price override
- `PATCH /api/v1/products/{productId}/price-overrides/{overrideId}` — Partially update product price override
  - Request body: `ProductPriceOverrideUpdateRequest`
- `PUT /api/v1/products/{productId}/price-overrides/{overrideId}` — Update product price override
  - Request body: `ProductPriceOverrideUpdateRequest`
- `GET /api/v1/products/{productId}/pricing-presets` — List pricing presets
- `POST /api/v1/products/{productId}/pricing-presets` — Create pricing preset
  - Request body: `PricingPresetCreateRequest`
- `POST /api/v1/products/{productId}/pricing-presets/reorder` — Reorder pricing presets
  - Request body: `PricingPresetReorderRequest`
- `DELETE /api/v1/products/{productId}/pricing-presets/{presetId}` — Delete pricing preset
- `PATCH /api/v1/products/{productId}/pricing-presets/{presetId}` — Partially update pricing preset
  - Request body: `PricingPresetUpdateRequest`
- `PUT /api/v1/products/{productId}/pricing-presets/{presetId}` — Update pricing preset
  - Request body: `PricingPresetUpdateRequest`

## Pull Requests

- `GET /api/v1/branches/{branchId}/pull-requests` — List pull requests
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
- `POST /api/v1/branches/{branchId}/pull-requests` — Create pull request
  - Request body: `PullRequestCreateRequest`
- `GET /api/v1/pull-requests/{prId}` — Get pull request
- `PATCH /api/v1/pull-requests/{prId}` — Partially update pull request
  - Request body: `PullRequestUpdateRequest`
- `PUT /api/v1/pull-requests/{prId}` — Update pull request
  - Request body: `PullRequestUpdateRequest`

## Quotes

- `GET /api/v1/quotes` — List quotes
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
  - `status` (query) — Filter by status
  - `opportunity_id` (query) — Filter by opportunity
- `POST /api/v1/quotes` — Create a quote
  - Request body: `QuoteCreateRequest`
- `DELETE /api/v1/quotes/{id}` — Delete a quote
- `GET /api/v1/quotes/{id}` — Get a quote
- `PATCH /api/v1/quotes/{id}` — Partially update a quote
  - Request body: `QuoteUpdateRequest`
- `PUT /api/v1/quotes/{id}` — Update a quote
  - Request body: `QuoteUpdateRequest`
- `GET /api/v1/quotes/{id}/line-items` — List line items
- `POST /api/v1/quotes/{id}/line-items` — Add a line item
  - Request body: `LineItemCreateRequest`
- `DELETE /api/v1/quotes/{id}/line-items/{item_id}` — Remove a line item
- `PATCH /api/v1/quotes/{id}/line-items/{item_id}` — Partially update a line item
  - Request body: `LineItemUpdateRequest`
- `PUT /api/v1/quotes/{id}/line-items/{item_id}` — Update a line item
  - Request body: `LineItemUpdateRequest`
- `POST /api/v1/quotes/{id}/revise` — Create a new revision
- `GET /api/v1/quotes/{id}/revisions` — List quote revisions
- `PUT /api/v1/quotes/{id}/status` — Update quote status
  - Request body: `QuoteStatusUpdateRequest`
- `GET /api/v1/quotes/{quoteId}/contacts` — List quote contacts
- `POST /api/v1/quotes/{quoteId}/contacts` — Add contact to quote
  - Request body: `QuoteContactAddRequest`
- `DELETE /api/v1/quotes/{quoteId}/contacts/{contactId}` — Remove contact from quote
- `GET /api/v1/quotes/{quoteId}/details` — Get quote details
- `PATCH /api/v1/quotes/{quoteId}/details` — Partially update quote details
  - Request body: `QuoteDetailsUpsertRequest`
- `PUT /api/v1/quotes/{quoteId}/details` — Upsert quote details
  - Request body: `QuoteDetailsUpsertRequest`

## Translations

- `GET /api/v1/translations` — List translations
  - `entity_type` (query) — Entity type (product, area, group, option)
  - `entity_id` (query) — Entity ID
  - `language` (query) — Language code
- `PUT /api/v1/translations` — Upsert translations
- `GET /api/v1/translations/dictionary` — List dictionary entries
- `POST /api/v1/translations/dictionary` — Create or update a dictionary entry

## Webhooks

- `GET /api/v1/webhooks` — List webhook subscriptions
- `POST /api/v1/webhooks` — Create a webhook subscription
  - Request body: `WebhookCreateRequest`
- `GET /api/v1/webhooks/deliveries/{id}` — Get delivery detail
- `GET /api/v1/webhooks/events` — List available webhook events
- `DELETE /api/v1/webhooks/{id}` — Delete a webhook subscription
- `GET /api/v1/webhooks/{id}` — Get a webhook subscription
- `PATCH /api/v1/webhooks/{id}` — Partially update a webhook subscription
  - Request body: `WebhookUpdateRequest`
- `PUT /api/v1/webhooks/{id}` — Update a webhook subscription
  - Request body: `WebhookUpdateRequest`
- `GET /api/v1/webhooks/{id}/deliveries` — List delivery attempts
  - `cursor` (query) — Opaque cursor for the next page
  - `limit` (query) — Items per page (server enforces configured maximum)
- `POST /api/v1/webhooks/{id}/rotate-secret` — Rotate webhook signing secret
- `POST /api/v1/webhooks/{id}/test` — Send a test event

---
**Total: 441 endpoints across 38 resource groups**
