# Rattle REST API Reference

> Comprehensive reference for AI agents. All ~500 operations across ~276 endpoints.

## Overview

- **Base URL**: `https://www.rattleapp.de/api/v1` (configurable via `RATTLE_BASE_URL` env var)
- **Authentication**: Bearer token -- `Authorization: Bearer rk_live_...`
- **Content-Type**: `application/json` (except image uploads: `multipart/form-data`)

## Using with RattleClient

The `RattleClient` in `rattle_api/client.py` provides a thin wrapper. Paths are relative (without `/api/v1` prefix):

```python
from rattle_api.client import RattleClient
client = RattleClient("acme")

# GET /api/v1/products?per_page=100
products = client.list_all("products", per_page=100)

# POST /api/v1/products
client.post("products", json={"name": "Widget", "base_price": "99.00"})

# PATCH /api/v1/products/42
client.patch("products/42", json={"description": "Updated"})

# DELETE /api/v1/products/42
client.delete("products/42")

# Upload image (multipart/form-data)
client.upload_image("options/301/image", "/path/to/image.jpg")
```

## Response Envelope

Single resource:
```json
{"data": {"id": 42, "name": "..."}}
```

Paginated list:
```json
{"data": [...], "meta": {"limit": 25, "has_next": true, "next_cursor": "eyJ...", "total_count": 42}}
```

Use `client.list_all()` to auto-paginate through all pages.

## Errors (RFC 9457)

```json
{"type": "/problems/not-found", "title": "Not Found", "status": 404, "detail": "...", "request_id": "req_..."}
```

Validation errors (422) include an `errors` array with per-field details.

## Pagination

Cursor-based. Parameters: `cursor` (opaque string), `limit` (default 25, max 100).
Some endpoints are NOT paginated and return `{data: [...]}` without meta -- noted per endpoint.

## Image Uploads

Use `multipart/form-data` with field name `file`. Accepted types: JPEG, PNG, WebP, GIF. Max 10MB.

---

## Quick Reference Table

| Tag | Method | Path | Summary |
|-----|--------|------|---------|
| Products | GET | `/api/v1/products` | List products |
| Products | POST | `/api/v1/products` | Create a product |
| Products | GET | `/api/v1/products/{id}` | Get a product |
| Products | PUT | `/api/v1/products/{id}` | Update a product |
| Products | PATCH | `/api/v1/products/{id}` | Partially update a product |
| Products | DELETE | `/api/v1/products/{id}` | Delete a product |
| Products | POST | `/api/v1/products/reorder` | Reorder products |
| Products | GET | `/api/v1/products/{productId}/areas` | List assigned areas |
| Products | POST | `/api/v1/products/{productId}/areas` | Assign an area to a product |
| Products | DELETE | `/api/v1/products/{productId}/areas/{areaId}` | Remove area from product |
| Products | POST | `/api/v1/products/{productId}/areas/reorder` | Reorder product areas |
| Products | POST | `/api/v1/products/{productId}/areas/replace` | Replace all product area assignments |
| Products | GET | `/api/v1/products/{productId}/price-overrides` | List product price overrides |
| Products | POST | `/api/v1/products/{productId}/price-overrides` | Create product price override |
| Products | PUT | `/api/v1/products/{productId}/price-overrides/{overrideId}` | Update product price override |
| Products | PATCH | `/api/v1/products/{productId}/price-overrides/{overrideId}` | Partially update product price override |
| Products | DELETE | `/api/v1/products/{productId}/price-overrides/{overrideId}` | Delete product price override |
| Products | POST | `/api/v1/products/{productId}/price-overrides/replace` | Replace all product price overrides |
| Products | GET | `/api/v1/products/{productId}/pricing-presets` | List pricing presets |
| Products | POST | `/api/v1/products/{productId}/pricing-presets` | Create pricing preset |
| Products | PUT | `/api/v1/products/{productId}/pricing-presets/{presetId}` | Update pricing preset |
| Products | PATCH | `/api/v1/products/{productId}/pricing-presets/{presetId}` | Partially update pricing preset |
| Products | DELETE | `/api/v1/products/{productId}/pricing-presets/{presetId}` | Delete pricing preset |
| Products | POST | `/api/v1/products/{productId}/pricing-presets/reorder` | Reorder pricing presets |
| Products | GET | `/api/v1/products/{productId}/configurations` | List product configurations |
| Images | POST | `/api/v1/products/{productId}/image` | Upload product image |
| Images | DELETE | `/api/v1/products/{productId}/image` | Delete product image |
| Images | POST | `/api/v1/products/{productId}/background` | Upload product background |
| Images | DELETE | `/api/v1/products/{productId}/background` | Delete product background |
| Images | GET | `/api/v1/products/{productId}/gallery` | List gallery images |
| Images | POST | `/api/v1/products/{productId}/gallery` | Upload gallery image |
| Images | POST | `/api/v1/products/{productId}/gallery/reorder` | Reorder gallery images |
| Images | GET | `/api/v1/products/{productId}/gallery/{imageId}` | Get gallery image |
| Images | PUT | `/api/v1/products/{productId}/gallery/{imageId}` | Replace gallery image |
| Images | DELETE | `/api/v1/products/{productId}/gallery/{imageId}` | Delete gallery image |
| Images | POST | `/api/v1/areas/{areaId}/image` | Upload area image |
| Images | DELETE | `/api/v1/areas/{areaId}/image` | Delete area image |
| Images | POST | `/api/v1/options/{optionId}/image` | Upload option image |
| Images | DELETE | `/api/v1/options/{optionId}/image` | Delete option image |
| Images | POST | `/api/v1/options/{optionId}/image/areas/{areaId}` | Upload option area override image |
| Images | DELETE | `/api/v1/options/{optionId}/image/areas/{areaId}` | Delete option area override image |
| Areas | GET | `/api/v1/areas` | List areas |
| Areas | POST | `/api/v1/areas` | Create an area |
| Areas | GET | `/api/v1/areas/{id}` | Get an area |
| Areas | PUT | `/api/v1/areas/{id}` | Update an area |
| Areas | PATCH | `/api/v1/areas/{id}` | Partially update an area |
| Areas | DELETE | `/api/v1/areas/{id}` | Delete an area |
| Areas | GET | `/api/v1/areas/library` | List library areas |
| Areas | GET | `/api/v1/areas/{id}/groups` | List groups in an area |
| Areas | GET | `/api/v1/areas/{id}/content` | Get area rich content |
| Areas | PUT | `/api/v1/areas/{id}/content` | Update area rich content |
| Areas | DELETE | `/api/v1/areas/{id}/content` | Delete area rich content |
| Areas | POST | `/api/v1/areas/{id}/content/images` | Upload content image |
| Areas | GET | `/api/v1/areas/{areaId}/price-overrides` | List area price overrides |
| Areas | POST | `/api/v1/areas/{areaId}/price-overrides` | Create area price override |
| Areas | PUT | `/api/v1/areas/{areaId}/price-overrides/{overrideId}` | Update area price override |
| Areas | PATCH | `/api/v1/areas/{areaId}/price-overrides/{overrideId}` | Partially update area price override |
| Areas | DELETE | `/api/v1/areas/{areaId}/price-overrides/{overrideId}` | Delete area price override |
| Areas | POST | `/api/v1/areas/{areaId}/price-overrides/replace` | Replace all area price overrides |
| Areas | GET | `/api/v1/areas/{areaId}/options` | List area options |
| Area Groups | GET | `/api/v1/area-groups` | List area groups |
| Area Groups | POST | `/api/v1/area-groups` | Create an area group |
| Area Groups | GET | `/api/v1/area-groups/{id}` | Get an area group |
| Area Groups | PUT | `/api/v1/area-groups/{id}` | Update an area group |
| Area Groups | PATCH | `/api/v1/area-groups/{id}` | Partially update an area group |
| Area Groups | DELETE | `/api/v1/area-groups/{id}` | Delete an area group |
| Area Groups | GET | `/api/v1/area-groups/{id}/areas` | List areas in an area group |
| Groups | GET | `/api/v1/groups` | List groups |
| Groups | POST | `/api/v1/groups` | Create a group |
| Groups | GET | `/api/v1/groups/{id}` | Get a group |
| Groups | PUT | `/api/v1/groups/{id}` | Update a group |
| Groups | PATCH | `/api/v1/groups/{id}` | Partially update a group |
| Groups | DELETE | `/api/v1/groups/{id}` | Delete a group |
| Groups | POST | `/api/v1/groups/{id}/duplicate` | Duplicate a group |
| Groups | GET | `/api/v1/groups/{id}/options` | List options in a group |
| Groups | GET | `/api/v1/groups/{id}/areas` | List areas linked to a group |
| Groups | POST | `/api/v1/groups/{id}/areas` | Link a group to areas |
| Groups | DELETE | `/api/v1/groups/{id}/areas/{area_id}` | Unlink a group from an area |
| Options | GET | `/api/v1/options` | List options |
| Options | POST | `/api/v1/options` | Create an option |
| Options | GET | `/api/v1/options/{id}` | Get an option |
| Options | PUT | `/api/v1/options/{id}` | Update an option |
| Options | PATCH | `/api/v1/options/{id}` | Partially update an option |
| Options | DELETE | `/api/v1/options/{id}` | Delete an option |
| Options | GET | `/api/v1/options/{id}/effective` | Get effective price for an option |
| Options | GET | `/api/v1/options/{optionId}/advanced-prices` | List advanced prices |
| Options | POST | `/api/v1/options/{optionId}/advanced-prices` | Create an advanced price |
| Options | PUT | `/api/v1/options/{optionId}/advanced-prices/{priceId}` | Update an advanced price |
| Options | PATCH | `/api/v1/options/{optionId}/advanced-prices/{priceId}` | Partially update an advanced price |
| Options | DELETE | `/api/v1/options/{optionId}/advanced-prices/{priceId}` | Delete an advanced price |
| Options | GET | `/api/v1/options/{optionId}/area-config` | Get area-specific config for an option |
| Options | PUT | `/api/v1/options/{optionId}/area-config` | Set area-specific config for an option |
| Price Overrides | GET | `/api/v1/options/{optionId}/price-overrides` | List price overrides for an option |
| Price Overrides | POST | `/api/v1/options/{optionId}/price-overrides` | Create a price override |
| Price Overrides | PUT | `/api/v1/options/{optionId}/price-overrides/{overrideId}` | Update a price override |
| Price Overrides | PATCH | `/api/v1/options/{optionId}/price-overrides/{overrideId}` | Partially update a price override |
| Price Overrides | DELETE | `/api/v1/options/{optionId}/price-overrides/{overrideId}` | Delete a price override |
| Price Overrides | POST | `/api/v1/options/{optionId}/price-overrides/replace` | Replace all price overrides |
| Price Lists | GET | `/api/v1/price-lists` | List price lists |
| Price Lists | POST | `/api/v1/price-lists` | Create a price list |
| Price Lists | GET | `/api/v1/price-lists/{id}` | Get a price list |
| Price Lists | PUT | `/api/v1/price-lists/{id}` | Update a price list |
| Price Lists | PATCH | `/api/v1/price-lists/{id}` | Partially update a price list |
| Price Lists | DELETE | `/api/v1/price-lists/{id}` | Delete a price list |
| Price Lists | POST | `/api/v1/price-lists/reorder` | Reorder price lists |
| Price Lists | GET | `/api/v1/price-lists/{priceListId}/overrides` | List price list overrides |
| Catalog Filters | GET | `/api/v1/catalog-filters` | List catalog filter dimensions |
| Catalog Filters | POST | `/api/v1/catalog-filters` | Create a catalog filter dimension |
| Catalog Filters | GET | `/api/v1/catalog-filters/{id}` | Get a catalog filter dimension |
| Catalog Filters | PUT | `/api/v1/catalog-filters/{id}` | Update a catalog filter dimension |
| Catalog Filters | DELETE | `/api/v1/catalog-filters/{id}` | Delete a catalog filter dimension |
| Catalog Filters | POST | `/api/v1/catalog-filters/reorder` | Reorder catalog filter dimensions |
| Catalog Filters | POST | `/api/v1/catalog-filters/{id}/values` | Add a value to a dimension |
| Catalog Filters | PUT | `/api/v1/catalog-filters/{id}/values/{valueId}` | Update a catalog filter value |
| Catalog Filters | DELETE | `/api/v1/catalog-filters/{id}/values/{valueId}` | Delete a catalog filter value |
| Catalog Filters | POST | `/api/v1/catalog-filters/{id}/values/reorder` | Reorder values within a dimension |
| Customers | GET | `/api/v1/customers` | List customers |
| Customers | POST | `/api/v1/customers` | Create a customer |
| Customers | GET | `/api/v1/customers/search` | Search customers |
| Customers | GET | `/api/v1/customers/{id}` | Get a customer |
| Customers | PUT | `/api/v1/customers/{id}` | Update a customer |
| Customers | PATCH | `/api/v1/customers/{id}` | Partially update a customer |
| Customers | DELETE | `/api/v1/customers/{id}` | Delete a customer |
| Customers | GET | `/api/v1/customers/{id}/contacts` | List contacts for a customer |
| Customers | POST | `/api/v1/customers/{id}/contacts` | Add a contact to a customer |
| Customers | PUT | `/api/v1/customers/{id}/contacts/{contact_id}` | Update a contact |
| Customers | DELETE | `/api/v1/customers/{id}/contacts/{contact_id}` | Remove a contact |
| Customers | GET | `/api/v1/customers/{customerId}/quotes` | List customer quotes |
| Customers | GET | `/api/v1/customers/{customerId}/opportunities` | List customer opportunities |
| Customers | GET | `/api/v1/customers/{customerId}/configurations` | List customer configurations |
| Languages | GET | `/api/v1/languages` | List languages |
| Languages | POST | `/api/v1/languages` | Create a language |
| Languages | GET | `/api/v1/languages/{id}` | Get a language |
| Languages | PUT | `/api/v1/languages/{id}` | Update a language |
| Languages | PATCH | `/api/v1/languages/{id}` | Partially update a language |
| Languages | DELETE | `/api/v1/languages/{id}` | Delete a language |
| Languages | POST | `/api/v1/languages/reorder` | Reorder languages |
| Constraints | GET | `/api/v1/constraints` | List option-level forbidden combinations |
| Constraints | POST | `/api/v1/constraints` | Replace option-level forbidden combinations |
| Constraints | GET | `/api/v1/constraints/area` | List area-level forbidden combinations |
| Constraints | POST | `/api/v1/constraints/area` | Replace area-level forbidden combinations |
| Constraints | POST | `/api/v1/constraints/check` | Check if a combination is forbidden |
| Constraints | GET | `/api/v1/constraints/rules` | List constraint rules |
| Constraints | POST | `/api/v1/constraints/rules` | Create a constraint rule |
| Constraints | GET | `/api/v1/constraints/rules/{id}` | Get a constraint rule |
| Constraints | PUT | `/api/v1/constraints/rules/{id}` | Update a constraint rule |
| Constraints | PATCH | `/api/v1/constraints/rules/{id}` | Partially update a constraint rule |
| Constraints | DELETE | `/api/v1/constraints/rules/{id}` | Delete a constraint rule |
| Attributes | GET | `/api/v1/attributes` | List technical attributes |
| Attributes | POST | `/api/v1/attributes` | Create an attribute |
| Attributes | GET | `/api/v1/attributes/{id}` | Get an attribute |
| Attributes | PUT | `/api/v1/attributes/{id}` | Update an attribute |
| Attributes | PATCH | `/api/v1/attributes/{id}` | Partially update an attribute |
| Attributes | DELETE | `/api/v1/attributes/{id}` | Delete an attribute |
| Attributes | GET | `/api/v1/attributes/{id}/values` | List attribute values |
| Attributes | POST | `/api/v1/attributes/{id}/values` | Create an attribute value |
| Attributes | PUT | `/api/v1/attributes/values/{id}` | Update an attribute value |
| Attributes | PATCH | `/api/v1/attributes/values/{id}` | Partially update an attribute value |
| Attributes | DELETE | `/api/v1/attributes/values/{id}` | Delete an attribute value |
| Configurations | GET | `/api/v1/configurations` | List saved configurations |
| Configurations | POST | `/api/v1/configurations/calculate` | Calculate a configuration |
| Configurations | GET | `/api/v1/configurations/states/{hash}` | Get configuration state by hash |
| Configurations | GET | `/api/v1/configurations/states/by-code/{code}` | Get configuration state by code |
| Configurations | GET | `/api/v1/configurations/states/by-code/{code}/selections` | Get enriched selected options |
| Configurations | GET | `/api/v1/configurations/states/by-code/{code}/parts` | Get configured parts (BOM) |
| Configurations | GET | `/api/v1/configurations/{id}` | Get a saved configuration |
| Configurations | POST | `/api/v1/configurations/{id}/finalize` | Finalize a configuration |
| Opportunities | GET | `/api/v1/opportunities` | List opportunities |
| Opportunities | POST | `/api/v1/opportunities` | Create an opportunity |
| Opportunities | GET | `/api/v1/opportunities/{id}` | Get an opportunity |
| Opportunities | PUT | `/api/v1/opportunities/{id}` | Update an opportunity |
| Opportunities | PATCH | `/api/v1/opportunities/{id}` | Partially update an opportunity |
| Opportunities | DELETE | `/api/v1/opportunities/{id}` | Delete an opportunity |
| Opportunities | GET | `/api/v1/opportunities/{id}/quotes` | List quotes for an opportunity |
| Quotes | GET | `/api/v1/quotes` | List quotes |
| Quotes | POST | `/api/v1/quotes` | Create a quote |
| Quotes | GET | `/api/v1/quotes/{id}` | Get a quote |
| Quotes | PUT | `/api/v1/quotes/{id}` | Update a quote |
| Quotes | PATCH | `/api/v1/quotes/{id}` | Partially update a quote |
| Quotes | DELETE | `/api/v1/quotes/{id}` | Delete a quote |
| Quotes | PUT | `/api/v1/quotes/{id}/status` | Update quote status |
| Quotes | POST | `/api/v1/quotes/{id}/revise` | Create a new revision |
| Quotes | GET | `/api/v1/quotes/{id}/revisions` | List quote revisions |
| Quotes | GET | `/api/v1/quotes/{id}/line-items` | List line items |
| Quotes | POST | `/api/v1/quotes/{id}/line-items` | Add a line item |
| Quotes | PUT | `/api/v1/quotes/{id}/line-items/{item_id}` | Update a line item |
| Quotes | PATCH | `/api/v1/quotes/{id}/line-items/{item_id}` | Partially update a line item |
| Quotes | DELETE | `/api/v1/quotes/{id}/line-items/{item_id}` | Remove a line item |
| Quotes | GET | `/api/v1/quotes/{quoteId}/details` | Get quote details |
| Quotes | PUT | `/api/v1/quotes/{quoteId}/details` | Upsert quote details |
| Quotes | PATCH | `/api/v1/quotes/{quoteId}/details` | Partially update quote details |
| Quotes | GET | `/api/v1/quotes/{quoteId}/contacts` | List quote contacts |
| Quotes | POST | `/api/v1/quotes/{quoteId}/contacts` | Add contact to quote |
| Quotes | DELETE | `/api/v1/quotes/{quoteId}/contacts/{contactId}` | Remove contact from quote |
| Documents | GET | `/api/v1/documents/templates` | List document templates |
| Documents | POST | `/api/v1/documents/templates` | Create a document template |
| Documents | GET | `/api/v1/documents/templates/{id}` | Get a document template |
| Documents | PUT | `/api/v1/documents/templates/{id}` | Update a document template |
| Documents | PATCH | `/api/v1/documents/templates/{id}` | Partially update a document template |
| Documents | DELETE | `/api/v1/documents/templates/{id}` | Delete a document template |
| Documents | POST | `/api/v1/documents/templates/{id}/clone` | Deep clone a template |
| Documents | POST | `/api/v1/documents/templates/{id}/variants` | Create an inheritance variant |
| Documents | POST | `/api/v1/documents/templates/{id}/translate` | Translate entire template |
| Documents | GET | `/api/v1/documents/templates/{id}/structure` | Get template structure tree |
| Documents | POST | `/api/v1/documents/templates/{id}/structure/blocks` | Create a structure block |
| Documents | GET | `/api/v1/documents/templates/{id}/structure/blocks/{block_id}` | Get a structure block |
| Documents | PUT | `/api/v1/documents/templates/{id}/structure/blocks/{block_id}` | Update a structure block |
| Documents | DELETE | `/api/v1/documents/templates/{id}/structure/blocks/{block_id}` | Delete a structure block (cascade) |
| Documents | POST | `/api/v1/documents/templates/{id}/structure/reorder` | Reorder structure blocks |
| Documents | POST | `/api/v1/documents/templates/{id}/structure/blocks/{block_id}/move` | Move block to new parent |
| Documents | GET | `/api/v1/documents/templates/{id}/structure/blocks/{block_id}/locales` | List structure block locales |
| Documents | PUT | `/api/v1/documents/templates/{id}/structure/blocks/{block_id}/locales/{lang}` | Upsert structure block locale title |
| Documents | DELETE | `/api/v1/documents/templates/{id}/structure/blocks/{block_id}/locales/{lang}` | Delete structure block locale |
| Documents | GET | `/api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments` | List block attachments |
| Documents | POST | `/api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments` | Attach content block |
| Documents | GET | `/api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments/{att_id}` | Get an attachment |
| Documents | PUT | `/api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments/{att_id}` | Update an attachment |
| Documents | DELETE | `/api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments/{att_id}` | Remove an attachment |
| Documents | POST | `/api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments/reorder` | Reorder attachments |
| Documents | POST | `/api/v1/documents/templates/{id}/structure/batch` | Batch structure operations |
| Documents | GET | `/api/v1/documents/content-blocks` | List content blocks |
| Documents | POST | `/api/v1/documents/content-blocks` | Create a content block |
| Documents | GET | `/api/v1/documents/content-blocks/{id}` | Get a content block with locales |
| Documents | PUT | `/api/v1/documents/content-blocks/{id}` | Update a content block |
| Documents | DELETE | `/api/v1/documents/content-blocks/{id}` | Delete a content block |
| Documents | POST | `/api/v1/documents/content-blocks/{id}/set-version` | Set current version |
| Documents | GET | `/api/v1/documents/content-blocks/{id}/locales` | List content block locales |
| Documents | POST | `/api/v1/documents/content-blocks/{id}/locales` | Create or upsert a content block locale |
| Documents | GET | `/api/v1/documents/content-blocks/{id}/locales/{locale_id}` | Get a content block locale |
| Documents | PUT | `/api/v1/documents/content-blocks/{id}/locales/{locale_id}` | Update a content block locale |
| Documents | DELETE | `/api/v1/documents/content-blocks/{id}/locales/{locale_id}` | Delete a content block locale |
| Documents | POST | `/api/v1/documents/content-blocks/{id}/locales/{locale_id}/translate` | Translate locale to target language |
| Documents | POST | `/api/v1/documents/content-blocks/images` | Upload EditorJS image |
| Documents | DELETE | `/api/v1/documents/content-blocks/images` | Delete EditorJS image by URL |
| Documents | POST | `/api/v1/documents/content-blocks/batch` | Batch content block operations |
| Documents | GET | `/api/v1/documents/content-directories` | List content directories (tree) |
| Documents | POST | `/api/v1/documents/content-directories` | Create a content directory |
| Documents | GET | `/api/v1/documents/content-directories/{id}` | Get a content directory |
| Documents | PUT | `/api/v1/documents/content-directories/{id}` | Update a content directory |
| Documents | DELETE | `/api/v1/documents/content-directories/{id}` | Delete a content directory |
| Documents | GET | `/api/v1/documents/instances` | List document instances |
| Documents | POST | `/api/v1/documents/instances` | Create a document instance (enriched) |
| Documents | GET | `/api/v1/documents/instances/{id}` | Get a document instance |
| Documents | DELETE | `/api/v1/documents/instances/{id}` | Delete a document instance |
| Documents | GET | `/api/v1/documents/instances/{id}/blocks` | List instance blocks (tree) |
| Documents | GET | `/api/v1/documents/instances/{id}/blocks/{block_id}` | Get an instance block |
| Documents | PUT | `/api/v1/documents/instances/{id}/blocks/{block_id}` | Update an instance block |
| Documents | DELETE | `/api/v1/documents/instances/{id}/blocks/{block_id}` | Delete an instance block |
| Documents | POST | `/api/v1/documents/instances/{id}/attachments` | Create instance attachment |
| Documents | PUT | `/api/v1/documents/instances/{id}/attachments/{att_id}` | Update instance attachment |
| Documents | DELETE | `/api/v1/documents/instances/{id}/attachments/{att_id}` | Delete instance attachment |
| Documents | POST | `/api/v1/documents/instances/{id}/publish` | Publish document instance |
| Documents | GET | `/api/v1/documents/instances/{id}/public-links` | List public links |
| Documents | GET | `/api/v1/documents/instances/{id}/public-links/{link_id}` | Get a public link |
| Documents | DELETE | `/api/v1/documents/instances/{id}/public-links/{link_id}` | Delete a public link |
| Offer Sections | GET | `/api/v1/products/{productId}/offer-sections` | List offer sections |
| Offer Sections | POST | `/api/v1/products/{productId}/offer-sections` | Create offer section |
| Offer Sections | GET | `/api/v1/products/{productId}/offer-sections/{sectionId}` | Get offer section |
| Offer Sections | PUT | `/api/v1/products/{productId}/offer-sections/{sectionId}` | Update offer section |
| Offer Sections | PATCH | `/api/v1/products/{productId}/offer-sections/{sectionId}` | Partially update offer section |
| Offer Sections | DELETE | `/api/v1/products/{productId}/offer-sections/{sectionId}` | Delete offer section |
| Offer Sections | POST | `/api/v1/products/{productId}/offer-sections/reorder` | Reorder offer sections |
| Offer Sections | GET | `/api/v1/products/{productId}/offer-sections/{sectionId}/content` | List offer section content |
| Offer Sections | PUT | `/api/v1/products/{productId}/offer-sections/{sectionId}/content` | Upsert offer section content |
| Offer Sections | DELETE | `/api/v1/products/{productId}/offer-sections/{sectionId}/content/{contentId}` | Delete offer section content |
| Product Media | GET | `/api/v1/products/{productId}/videos` | List video links |
| Product Media | POST | `/api/v1/products/{productId}/videos` | Create video link |
| Product Media | PUT | `/api/v1/products/{productId}/videos/{videoId}` | Update video link |
| Product Media | DELETE | `/api/v1/products/{productId}/videos/{videoId}` | Delete video link |
| Product Media | POST | `/api/v1/products/{productId}/videos/reorder` | Reorder video links |
| Product Media | GET | `/api/v1/products/{productId}/models` | List 3D model links |
| Product Media | POST | `/api/v1/products/{productId}/models` | Create 3D model link |
| Product Media | PUT | `/api/v1/products/{productId}/models/{modelId}` | Update 3D model link |
| Product Media | DELETE | `/api/v1/products/{productId}/models/{modelId}` | Delete 3D model link |
| Product Media | POST | `/api/v1/products/{productId}/models/reorder` | Reorder 3D model links |
| Translations | GET | `/api/v1/translations` | List translations |
| Translations | PUT | `/api/v1/translations` | Upsert translations |
| Translations | GET | `/api/v1/translations/dictionary` | List dictionary entries |
| Translations | POST | `/api/v1/translations/dictionary` | Create or update a dictionary entry |
| Webhooks | GET | `/api/v1/webhooks` | List webhook subscriptions |
| Webhooks | POST | `/api/v1/webhooks` | Create a webhook subscription |
| Webhooks | GET | `/api/v1/webhooks/{id}` | Get a webhook subscription |
| Webhooks | PUT | `/api/v1/webhooks/{id}` | Update a webhook subscription |
| Webhooks | PATCH | `/api/v1/webhooks/{id}` | Partially update a webhook subscription |
| Webhooks | DELETE | `/api/v1/webhooks/{id}` | Delete a webhook subscription |
| Webhooks | POST | `/api/v1/webhooks/{id}/test` | Send a test event |
| Webhooks | POST | `/api/v1/webhooks/{id}/rotate-secret` | Rotate webhook signing secret |
| Webhooks | GET | `/api/v1/webhooks/{id}/deliveries` | List delivery attempts |
| Webhooks | GET | `/api/v1/webhooks/deliveries/{id}` | Get delivery detail |
| Webhooks | GET | `/api/v1/webhooks/events` | List available webhook events |
| Inbound Webhooks | POST | `/api/v1/inbound/events` | Send an inbound event |
| Inbound Webhooks | POST | `/api/v1/inbound/customers` | Upsert an inbound customer |
| Inbound Webhooks | POST | `/api/v1/inbound/customers/batch` | Batch upsert inbound customers |
| Inbound Webhooks | POST | `/api/v1/inbound/opportunities` | Create an inbound opportunity |
| Inbound Webhooks | POST | `/api/v1/inbound/parts/batch` | Batch upsert inbound parts |
| Inbound Webhooks | POST | `/api/v1/inbound/connectors/tasks/{id}/trigger` | Trigger a connector task |
| Inbound Webhooks | POST | `/api/v1/inbound/triggers/{suffix}` | Fire a webhook trigger by path |
| API Keys | GET | `/api/v1/api-keys` | List API keys |
| API Keys | POST | `/api/v1/api-keys` | Create an API key (session auth) |
| API Keys | GET | `/api/v1/api-keys/{id}` | Get an API key |
| API Keys | DELETE | `/api/v1/api-keys/{id}` | Revoke an API key (session auth) |
| API Keys | DELETE | `/api/v1/api-keys/{id}/permanent` | Permanently delete an API key (session auth) |
| API Keys | POST | `/api/v1/api-keys/{id}/rotate` | Rotate an API key (session auth) |
| API Keys | GET | `/api/v1/api-keys/usage` | Get API key usage statistics |
| Connectors | GET | `/api/v1/connectors` | List connectors |
| Connectors | POST | `/api/v1/connectors` | Create a connector |
| Connectors | GET | `/api/v1/connectors/{id}` | Get a connector |
| Connectors | PUT | `/api/v1/connectors/{id}` | Update a connector |
| Connectors | PATCH | `/api/v1/connectors/{id}` | Partially update a connector |
| Connectors | DELETE | `/api/v1/connectors/{id}` | Delete a connector |
| Connectors | GET | `/api/v1/connectors/{id}/endpoints` | List connector endpoints |
| Connectors | POST | `/api/v1/connectors/{id}/endpoints` | Create a connector endpoint |
| Connectors | DELETE | `/api/v1/connectors/endpoints/{id}` | Delete a connector endpoint |
| Connectors | GET | `/api/v1/connectors/{id}/tasks` | List connector tasks |
| Connectors | POST | `/api/v1/connectors/{id}/tasks` | Create a connector task |
| Connectors | GET | `/api/v1/connectors/tasks/{id}` | Get a connector task |
| Connectors | DELETE | `/api/v1/connectors/tasks/{id}` | Delete a connector task |
| Connectors | POST | `/api/v1/connectors/tasks/{id}/run` | Run a connector task |
| Connectors | GET | `/api/v1/connectors/triggers` | List connector triggers |
| Connectors | POST | `/api/v1/connectors/triggers` | Create a connector trigger |
| Connectors | PUT | `/api/v1/connectors/triggers/{id}` | Update a connector trigger |
| Connectors | DELETE | `/api/v1/connectors/triggers/{id}` | Delete a connector trigger |
| Connectors | GET | `/api/v1/connectors/jobs` | List connector jobs |
| Connectors | GET | `/api/v1/connectors/jobs/{id}` | Get a connector job |
| Connectors | POST | `/api/v1/connectors/jobs/{id}/replay` | Replay a connector job |
| Connectors | GET | `/api/v1/connectors/jobs/{jobId}/logs` | List job logs |
| Company | GET | `/api/v1/company` | Get company settings |
| Company | PUT | `/api/v1/company` | Update company settings |
| Company | PATCH | `/api/v1/company` | Partially update company settings |
| Company | GET | `/api/v1/company/configurator-settings` | Get configurator settings |
| Company | PUT | `/api/v1/company/configurator-settings` | Update configurator settings |
| Company | PATCH | `/api/v1/company/configurator-settings` | Partially update configurator settings |
| Company | GET | `/api/v1/company/connector-settings` | Get connector settings |
| Company | PUT | `/api/v1/company/connector-settings` | Update connector settings |
| Company | PATCH | `/api/v1/company/connector-settings` | Partially update connector settings |
| Company | GET | `/api/v1/company/contacts` | List company contacts |
| Company | POST | `/api/v1/company/contacts` | Create a company contact |
| Company | PUT | `/api/v1/company/contacts/{id}` | Update a company contact |
| Company | PATCH | `/api/v1/company/contacts/{id}` | Partially update a company contact |
| Company | DELETE | `/api/v1/company/contacts/{id}` | Delete a company contact |
| Parts | GET | `/api/v1/parts` | List parts |
| Parts | POST | `/api/v1/parts` | Create a part |
| Parts | GET | `/api/v1/parts/{id}` | Get a part |
| Parts | PUT | `/api/v1/parts/{id}` | Update a part |
| Parts | PATCH | `/api/v1/parts/{id}` | Partially update a part |
| Parts | DELETE | `/api/v1/parts/{id}` | Delete a part |
| Parts | GET | `/api/v1/parts/{id}/placements` | List part placements |
| Parts | POST | `/api/v1/parts/{id}/placements` | Create a part placement |
| Parts | PUT | `/api/v1/parts/placements/{id}` | Update a part placement |
| Parts | PATCH | `/api/v1/parts/placements/{id}` | Partially update a part placement |
| Parts | DELETE | `/api/v1/parts/placements/{id}` | Delete a part placement |
| Parts | GET | `/api/v1/parts/{id}/bom` | List BOM children |
| Parts | POST | `/api/v1/parts/{id}/bom` | Add a BOM child |
| Parts | PUT | `/api/v1/parts/bom/{id}` | Update a BOM item |
| Parts | PATCH | `/api/v1/parts/bom/{id}` | Partially update a BOM item |
| Parts | DELETE | `/api/v1/parts/bom/{id}` | Delete a BOM item |
| Parts | GET | `/api/v1/parts/{id}/bom/tree` | Get multi-level BOM tree |
| Parts | GET | `/api/v1/parts/{id}/bom/flat` | Get flattened BOM |
| Parts | GET | `/api/v1/parts/{id}/where-used` | Find where a part is used |
| Parts | POST | `/api/v1/parts/{id}/bom/validate` | Validate BOM integrity |
| Parts | GET | `/api/v1/parts/groups` | List part groups |
| Parts | POST | `/api/v1/parts/groups` | Create part group |
| Parts | GET | `/api/v1/parts/groups/{groupId}` | Get part group |
| Parts | PUT | `/api/v1/parts/groups/{groupId}` | Update part group |
| Parts | PATCH | `/api/v1/parts/groups/{groupId}` | Partially update part group |
| Parts | DELETE | `/api/v1/parts/groups/{groupId}` | Delete part group |
| Parts | GET | `/api/v1/parts/{partId}/changelog` | List part changelog |
| Item Revisions | GET | `/api/v1/parts/{partId}/revisions` | List revisions for a part |
| Item Revisions | POST | `/api/v1/parts/{partId}/revisions` | Create a revision |
| Item Revisions | GET | `/api/v1/parts/{partId}/revisions/{revisionId}` | Get a revision |
| Item Revisions | PUT | `/api/v1/parts/{partId}/revisions/{revisionId}` | Update a draft revision |
| Item Revisions | DELETE | `/api/v1/parts/{partId}/revisions/{revisionId}` | Delete a draft revision |
| Item Revisions | POST | `/api/v1/parts/{partId}/revisions/{revisionId}/release` | Release a revision |
| Item Revisions | POST | `/api/v1/parts/{partId}/revisions/{revisionId}/obsolete` | Obsolete a revision |
| Part Documents | GET | `/api/v1/part-documents` | List part documents |
| Part Documents | POST | `/api/v1/part-documents` | Create a part document |
| Part Documents | GET | `/api/v1/part-documents/{id}` | Get a part document |
| Part Documents | PUT | `/api/v1/part-documents/{id}` | Update a part document |
| Part Documents | PATCH | `/api/v1/part-documents/{id}` | Partially update a part document |
| Part Documents | DELETE | `/api/v1/part-documents/{id}` | Delete a part document |
| Part Documents | GET | `/api/v1/parts/{partId}/document-links` | List document links for a part |
| Part Documents | POST | `/api/v1/parts/{partId}/document-links` | Create a document link for a part |
| Part Documents | DELETE | `/api/v1/parts/{partId}/document-links/{linkId}` | Remove a document link |
| Part Documents | GET | `/api/v1/parts/{partId}/revisions/{revisionId}/document-links` | List document links for a revision |
| Part Documents | POST | `/api/v1/parts/{partId}/revisions/{revisionId}/document-links` | Create a document link for a revision |
| Part Documents | GET | `/api/v1/part-documents/{id}/cad-files` | List CAD files for a document |
| Part Documents | POST | `/api/v1/part-documents/{id}/cad-files` | Upload a CAD file |
| Part Documents | GET | `/api/v1/part-documents/{id}/cad-files/{fileId}` | Get a CAD file |
| Part Documents | DELETE | `/api/v1/part-documents/{id}/cad-files/{fileId}` | Delete a CAD file |
| Part Documents | GET | `/api/v1/part-documents/{id}/derivatives` | List derivatives for a document |
| Part Documents | POST | `/api/v1/part-documents/{id}/derivatives` | Request a derivative |
| Part Documents | GET | `/api/v1/part-documents/{id}/derivatives/{derivId}` | Get a derivative |
| Part Documents | DELETE | `/api/v1/part-documents/{id}/derivatives/{derivId}` | Delete a derivative |
| Baselines | GET | `/api/v1/baselines` | List baselines |
| Baselines | POST | `/api/v1/baselines` | Create a baseline |
| Baselines | GET | `/api/v1/baselines/{id}` | Get a baseline |
| Baselines | DELETE | `/api/v1/baselines/{id}` | Delete a baseline |
| Batch | POST | `/api/v1/batch` | Universal batch operations |
| Batch | POST | `/api/v1/parts/batch` | Batch parts operations |
| Batch | POST | `/api/v1/products/batch` | Batch products operations |
| Batch | POST | `/api/v1/options/batch` | Batch options operations |
| Batch | POST | `/api/v1/groups/batch` | Batch groups operations |
| Batch | POST | `/api/v1/areas/batch` | Batch areas operations |
| Batch | POST | `/api/v1/customers/batch` | Batch customers operations |
| Batch | POST | `/api/v1/bom/batch` | Batch BOM operations |
| Export | GET | `/api/v1/products/export` | Export products (NDJSON) |
| Export | GET | `/api/v1/customers/export` | Export customers (NDJSON) |
| Export | GET | `/api/v1/parts/export` | Export parts (NDJSON) |
| Customer Links | GET | `/api/v1/customer-links` | List customer links |
| Customer Links | POST | `/api/v1/customer-links` | Create a customer link |
| Customer Links | GET | `/api/v1/customer-links/{id}` | Get a customer link |
| Customer Links | PUT | `/api/v1/customer-links/{id}` | Update a customer link |
| Customer Links | PATCH | `/api/v1/customer-links/{id}` | Partially update a customer link |
| Customer Links | DELETE | `/api/v1/customer-links/{id}` | Delete a customer link |
| Branches | GET | `/api/v1/branches` | List branches |
| Branches | POST | `/api/v1/branches` | Create branch |
| Branches | GET | `/api/v1/branches/{branchId}` | Get branch |
| Branches | DELETE | `/api/v1/branches/{branchId}` | Delete branch |
| Pull Requests | GET | `/api/v1/branches/{branchId}/pull-requests` | List pull requests |
| Pull Requests | POST | `/api/v1/branches/{branchId}/pull-requests` | Create pull request |
| Pull Requests | GET | `/api/v1/pull-requests/{prId}` | Get pull request |
| Pull Requests | PUT | `/api/v1/pull-requests/{prId}` | Update pull request |
| Pull Requests | PATCH | `/api/v1/pull-requests/{prId}` | Partially update pull request |
| Change Requests | GET | `/api/v1/change-requests` | List change requests |
| Change Requests | POST | `/api/v1/change-requests` | Create change request |
| Change Requests | GET | `/api/v1/change-requests/{ecrId}` | Get change request |
| Change Requests | PUT | `/api/v1/change-requests/{ecrId}` | Update change request |
| Change Requests | PATCH | `/api/v1/change-requests/{ecrId}` | Partially update change request |
| Change Requests | DELETE | `/api/v1/change-requests/{ecrId}` | Delete change request |
| Change Requests | GET | `/api/v1/change-requests/{ecrId}/orders` | List change orders for request |
| Change Requests | POST | `/api/v1/change-requests/{ecrId}/orders` | Create change order |
| Change Orders | GET | `/api/v1/change-orders/{ecoId}` | Get change order |
| Change Orders | PUT | `/api/v1/change-orders/{ecoId}` | Update change order |
| Change Orders | PATCH | `/api/v1/change-orders/{ecoId}` | Partially update change order |
| Change Orders | DELETE | `/api/v1/change-orders/{ecoId}` | Delete change order |
| Change Orders | GET | `/api/v1/change-orders/{ecoId}/impacts` | List change impacts |
| Change Orders | POST | `/api/v1/change-orders/{ecoId}/impacts` | Create change impact |
| Change Orders | PUT | `/api/v1/change-orders/{ecoId}/impacts/{impactId}` | Update change impact |
| Change Orders | PATCH | `/api/v1/change-orders/{ecoId}/impacts/{impactId}` | Partially update change impact |
| Change Orders | DELETE | `/api/v1/change-orders/{ecoId}/impacts/{impactId}` | Delete change impact |
| Change Orders | GET | `/api/v1/change-orders/{ecoId}/approvals` | List change approvals |
| Change Orders | POST | `/api/v1/change-orders/{ecoId}/approvals` | Create change approval |
| Change Orders | PUT | `/api/v1/change-orders/{ecoId}/approvals/{approvalId}` | Update change approval |
| Change Orders | PATCH | `/api/v1/change-orders/{ecoId}/approvals/{approvalId}` | Partially update change approval |
| Roles | GET | `/api/v1/roles` | List roles |
| Roles | POST | `/api/v1/roles` | Create a custom role |
| Roles | GET | `/api/v1/roles/{id}` | Get a role |
| Roles | PUT | `/api/v1/roles/{id}` | Update a role |
| Roles | PATCH | `/api/v1/roles/{id}` | Partially update a role |
| Roles | DELETE | `/api/v1/roles/{id}` | Delete a custom role |
| Roles | GET | `/api/v1/users/{userId}/roles` | List user's role assignments |
| Roles | POST | `/api/v1/users/{userId}/roles` | Assign a role to a user |
| Roles | DELETE | `/api/v1/users/{userId}/roles/{roleId}` | Remove a role assignment |
| Permissions | GET | `/api/v1/permissions` | List all available permissions |
| Permissions | GET | `/api/v1/users/{userId}/permissions` | Get effective permissions for a user |
| Permissions | GET | `/api/v1/me/permissions` | Get caller's own permissions |
| Teams | GET | `/api/v1/teams` | List teams |
| Teams | POST | `/api/v1/teams` | Create a team |
| Teams | GET | `/api/v1/teams/{id}` | Get a team |
| Teams | PUT | `/api/v1/teams/{id}` | Update a team |
| Teams | PATCH | `/api/v1/teams/{id}` | Partially update a team |
| Teams | DELETE | `/api/v1/teams/{id}` | Delete a team |
| Teams | POST | `/api/v1/teams/{id}/members` | Add a team member |
| Teams | DELETE | `/api/v1/teams/{id}/members/{userId}` | Remove a team member |
| Territories | GET | `/api/v1/territories` | List territories |
| Territories | POST | `/api/v1/territories` | Create a territory |
| Territories | GET | `/api/v1/territories/{id}` | Get a territory |
| Territories | PUT | `/api/v1/territories/{id}` | Update a territory |
| Territories | PATCH | `/api/v1/territories/{id}` | Partially update a territory |
| Territories | DELETE | `/api/v1/territories/{id}` | Delete a territory |
| Territories | POST | `/api/v1/territories/{id}/users` | Assign a user to a territory |
| Territories | DELETE | `/api/v1/territories/{id}/users/{userId}` | Remove a user from a territory |
| Data Access Policies | GET | `/api/v1/data-access-policies` | List data access policies |
| Data Access Policies | POST | `/api/v1/data-access-policies` | Create a data access policy |
| Data Access Policies | GET | `/api/v1/data-access-policies/{id}` | Get a data access policy |
| Data Access Policies | PUT | `/api/v1/data-access-policies/{id}` | Update a data access policy |
| Data Access Policies | PATCH | `/api/v1/data-access-policies/{id}` | Partially update a data access policy |
| Data Access Policies | DELETE | `/api/v1/data-access-policies/{id}` | Delete a data access policy |
| Data Access Policies | POST | `/api/v1/data-access-policies/{id}/assignments` | Assign a policy to a role or user |
| Data Access Policies | DELETE | `/api/v1/data-access-policies/{id}/assignments/{assignmentId}` | Remove a policy assignment |
| Permission Bundles | GET | `/api/v1/permission-bundles` | List permission bundles |
| Permission Bundles | POST | `/api/v1/permission-bundles` | Create a permission bundle |
| Permission Bundles | GET | `/api/v1/permission-bundles/{id}` | Get a permission bundle |
| Permission Bundles | PUT | `/api/v1/permission-bundles/{id}` | Update a permission bundle |
| Permission Bundles | DELETE | `/api/v1/permission-bundles/{id}` | Delete a permission bundle |
| Role Templates | GET | `/api/v1/role-templates` | List role templates |
| Role Templates | POST | `/api/v1/role-templates` | Create a role template |
| Role Templates | GET | `/api/v1/role-templates/{id}` | Get a role template |
| Role Templates | PUT | `/api/v1/role-templates/{id}` | Update a role template |
| Role Templates | DELETE | `/api/v1/role-templates/{id}` | Delete a role template |
| User Attributes | GET | `/api/v1/users/{id}/attributes` | List user attributes |
| User Attributes | POST | `/api/v1/users/{id}/attributes` | Create a user attribute |
| User Attributes | GET | `/api/v1/users/{id}/attributes/{attrId}` | Get a user attribute |
| User Attributes | PUT | `/api/v1/users/{id}/attributes/{attrId}` | Update a user attribute |
| User Attributes | DELETE | `/api/v1/users/{id}/attributes/{attrId}` | Delete a user attribute |
| Users | GET | `/api/v1/users` | List users |
| Users | GET | `/api/v1/users/{id}` | Get a user |
| Invitations | GET | `/api/v1/invitations` | List invitations |
| Invitations | POST | `/api/v1/invitations` | Create an invitation |
| Invitations | GET | `/api/v1/invitations/{id}` | Get an invitation |
| Invitations | DELETE | `/api/v1/invitations/{id}` | Revoke an invitation |
| Approval Workflows | GET | `/api/v1/approval-rules` | List approval rules |
| Approval Workflows | POST | `/api/v1/approval-rules` | Create an approval rule |
| Approval Workflows | GET | `/api/v1/approval-rules/{id}` | Get an approval rule |
| Approval Workflows | PUT | `/api/v1/approval-rules/{id}` | Update an approval rule |
| Approval Workflows | PATCH | `/api/v1/approval-rules/{id}` | Partially update an approval rule |
| Approval Workflows | DELETE | `/api/v1/approval-rules/{id}` | Delete an approval rule |
| Approval Workflows | GET | `/api/v1/approvals` | List approval requests |
| Approval Workflows | GET | `/api/v1/approvals/pending` | List pending approvals for current user |
| Approval Workflows | POST | `/api/v1/approvals/{id}/action` | Approve or reject an approval request |
| Analytics | GET | `/api/v1/analytics/pipeline` | List pipeline snapshots |
| Analytics | GET | `/api/v1/analytics/quotes` | List quote analytics |
| Analytics | GET | `/api/v1/analytics/option-selections` | List option selection facts |
| Analytics | GET | `/api/v1/analytics/part-usage` | List part usage facts |
| AI Usage | GET | `/api/v1/ai-usage/wallet` | Get AI token wallet |
| AI Usage | GET | `/api/v1/ai-usage/ledger` | List AI usage ledger entries |
| AI Usage | GET | `/api/v1/ai-usage/periods` | List AI usage periods |
| Resource Tags | GET | `/api/v1/resource-tags` | List resource tags |
| Resource Tags | POST | `/api/v1/resource-tags` | Create a resource tag |
| Resource Tags | GET | `/api/v1/resource-tags/{id}` | Get a resource tag |
| Resource Tags | PUT | `/api/v1/resource-tags/{id}` | Update a resource tag |
| Resource Tags | DELETE | `/api/v1/resource-tags/{id}` | Delete a resource tag |
| Health | GET | `/api/v1/health` | Health check |

---

## Products

### List products
`GET /api/v1/products` | `listProducts`

Returns a paginated list of products for your company. Use `search` to filter by name and `status` to filter by lifecycle state.

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| cursor | string | No | Opaque cursor for the next page |
| limit | integer | No | Items per page (default 25, max 100) |
| search | string | No | Filter by name (case-insensitive partial match) |
| status | string | No | Filter: `active` (default), `inactive`, or `all` |

**Response:** Paginated list of `ProductResponse`

<details><summary>Example response</summary>

```json
{
  "data": [
    {
      "id": 42,
      "name": "Premium Window System",
      "description": "Triple-glazed window with configurable frame material and color.",
      "base_price": "1250.00",
      "currency": "EUR",
      "language": "EN",
      "is_active": true,
      "order_index": 0,
      "image_url": "https://cdn.example.com/uploads/42/product_42_1710000000000_abc123.jpg",
      "background_url": "https://cdn.example.com/uploads/42/product_bg_42_1710000000000_def456.jpg",
      "gallery_count": 3,
      "public_token": "pk_abc123def456",
      "integration_metadata": {"erp_id": "PRD-001", "sync_source": "SAP"},
      "catalog_meta": {"filters": {"1": [3, 5]}, "tags": ["triple-glazed", "premium"], "badges": ["featured"], "specs_summary": "Max 2400mm width, U-value 0.7", "sort_priority": 0},
      "options_version": 5,
      "constraints_version": 2,
      "areas_version": 3,
      "parts_version": 1,
      "pricing_version": 4,
      "created_at": "2025-09-15T08:30:00Z",
      "updated_at": "2026-01-20T14:15:00Z",
      "links": {
        "self": {"href": "/api/v1/products/42"},
        "areas": {"href": "/api/v1/areas?product_id=42"},
        "gallery": {"href": "/api/v1/products/42/gallery"},
        "image": {"href": "/api/v1/products/42/image"}
      }
    }
  ],
  "meta": {"limit": 25, "has_next": false, "next_cursor": null, "total_count": 1}
}
```
</details>

### Create a product
`POST /api/v1/products` | `createProduct`

Create a new product in your catalog. Returns the created product with a `Location` header pointing to the new resource.

**Request Body:** `ProductCreateRequest`

<details><summary>Example request</summary>

```json
{
  "name": "Premium Window System",
  "description": "Triple-glazed window with configurable frame material and color.",
  "base_price": "1250.00",
  "language": "EN",
  "integration_metadata": {"erp_id": "PRD-001"},
  "catalog_meta": {"filters": {"1": [3]}, "tags": ["triple-glazed"], "badges": ["new"]}
}
```
</details>

**Response:** `201 Created` with `ProductResponse`

### Get a product
`GET /api/v1/products/{id}` | `getProduct`

Retrieve a single product by ID. Use `expand` to inline related resources. Supported expansions: `areas`, `areas.groups`, `areas.groups.options`, `gallery`.

**Path Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | integer | Yes | Resource ID |

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| expand | string | No | Comma-separated list of expansions: `areas`, `gallery` |

**Response:** Single `ProductResponse`

### Update a product
`PUT /api/v1/products/{id}` | `updateProduct`

**Request Body:** `ProductUpdateRequest`

<details><summary>Example request</summary>

```json
{
  "name": "Premium Window System v2",
  "base_price": "1350.00",
  "is_active": true,
  "integration_metadata": {"erp_id": "PRD-001", "sync_source": "SAP"},
  "catalog_meta": {"filters": {"1": [3, 5]}, "tags": ["triple-glazed", "premium"], "badges": ["featured"], "specs_summary": "Max 2400mm width, U-value 0.7", "sort_priority": 0}
}
```
</details>

### Partially update a product
`PATCH /api/v1/products/{id}` | `patchProduct`

Same body as PUT but all fields optional. Only provided fields are changed.

### Delete a product
`DELETE /api/v1/products/{id}` | `deleteProduct`

**Response:** `204 No Content`

### Reorder products
`POST /api/v1/products/reorder` | `reorderProducts`

<details><summary>Example request</summary>

```json
{"order": [3, 1, 2, 5, 4]}
```
</details>

### List assigned areas
`GET /api/v1/products/{productId}/areas` | `listProductAreas`

List all areas assigned to this product with their assignment metadata (area_id, area_name, order_index, enabled). **Not paginated.**

**Response:** `{data: [ProductAreaResponse, ...]}`

### Assign an area to a product
`POST /api/v1/products/{productId}/areas` | `assignProductArea`

**Request Body:**
```json
{"area_id": 101, "order_index": 0, "enabled": true}
```

### Remove area from product
`DELETE /api/v1/products/{productId}/areas/{areaId}` | `removeProductArea`

### Reorder product areas
`POST /api/v1/products/{productId}/areas/reorder` | `reorderProductAreas`

**Request Body:**
```json
{"order": [103, 101, 102]}
```

### Replace all product area assignments
`POST /api/v1/products/{productId}/areas/replace` | `replaceProductAreas`

**Request Body:**
```json
{
  "areas": [
    {"area_id": 101, "order_index": 0, "enabled": true},
    {"area_id": 102, "order_index": 1, "enabled": true}
  ]
}
```

### List product price overrides
`GET /api/v1/products/{productId}/price-overrides` | `listProductPriceOverrides`

List all price-list overrides for a product's base price. **Not paginated.**

<details><summary>Example response</summary>

```json
{
  "data": [
    {"id": 1, "product_id": 42, "price_list_id": 10, "override_price": "1100.00"}
  ]
}
```
</details>

### Create product price override
`POST /api/v1/products/{productId}/price-overrides` | `createProductPriceOverride`

<details><summary>Example request</summary>

```json
{"price_list_id": 10, "override_price": "1100.00"}
```
</details>

### Update product price override
`PUT /api/v1/products/{productId}/price-overrides/{overrideId}` | `updateProductPriceOverride`

### Partially update product price override
`PATCH /api/v1/products/{productId}/price-overrides/{overrideId}` | `patchProductPriceOverride`

### Delete product price override
`DELETE /api/v1/products/{productId}/price-overrides/{overrideId}` | `deleteProductPriceOverride`

### Replace all product price overrides
`POST /api/v1/products/{productId}/price-overrides/replace` | `replaceProductPriceOverrides`

<details><summary>Example request</summary>

```json
{
  "overrides": [
    {"price_list_id": 10, "override_price": "1100.00"},
    {"price_list_id": 11, "override_price": "1300.00"}
  ]
}
```
</details>

### List pricing presets
`GET /api/v1/products/{productId}/pricing-presets` | `listPricingPresets`

List pricing adjustment presets (surcharges, discounts, fees) for a product. **Not paginated.**

<details><summary>Example response</summary>

```json
{
  "data": [
    {
      "id": 5, "product_id": 42, "key": "assembly_fee", "label": "Assembly Fee",
      "category": "surcharge", "amount_type": "fixed", "value": "150.00",
      "taxable": true, "default_on": true, "sort_index": 0,
      "created_at": "2026-02-01T10:00:00Z", "updated_at": "2026-02-15T16:45:00Z"
    }
  ]
}
```
</details>

### Create pricing preset
`POST /api/v1/products/{productId}/pricing-presets` | `createPricingPreset`

<details><summary>Example request</summary>

```json
{
  "key": "assembly_fee", "label": "Assembly Fee",
  "category": "surcharge", "amount_type": "fixed", "value": "150.00",
  "taxable": true, "default_on": true
}
```
</details>

### Update / Partially update / Delete pricing preset
`PUT /api/v1/products/{productId}/pricing-presets/{presetId}` | `updatePricingPreset`
`PATCH /api/v1/products/{productId}/pricing-presets/{presetId}` | `patchPricingPreset`
`DELETE /api/v1/products/{productId}/pricing-presets/{presetId}` | `deletePricingPreset`

### Reorder pricing presets
`POST /api/v1/products/{productId}/pricing-presets/reorder` | `reorderPricingPresets`

### List product configurations
`GET /api/v1/products/{productId}/configurations` | `listProductConfigurations`

Paginated list of all configurations created for a product.

---

## Images

All image endpoints use `multipart/form-data` with a `file` field for uploads.

### Upload product image
`POST /api/v1/products/{productId}/image` | `uploadProductImage`

### Delete product image
`DELETE /api/v1/products/{productId}/image` | `deleteProductImage`

### Upload product background
`POST /api/v1/products/{productId}/background` | `uploadProductBackground`

### Delete product background
`DELETE /api/v1/products/{productId}/background` | `deleteProductBackground`

### List gallery images
`GET /api/v1/products/{productId}/gallery` | `listGalleryImages`

Returns gallery images ordered by position. **Not paginated.**

### Upload gallery image
`POST /api/v1/products/{productId}/gallery` | `uploadGalleryImage`

Upload a new gallery image (max 10 per product).

### Reorder gallery images
`POST /api/v1/products/{productId}/gallery/reorder` | `reorderGalleryImages`

**Request Body:** `GalleryReorderRequest`
```json
{"order": [3, 1, 2]}
```

### Get gallery image
`GET /api/v1/products/{productId}/gallery/{imageId}` | `getGalleryImage`

### Replace gallery image
`PUT /api/v1/products/{productId}/gallery/{imageId}` | `replaceGalleryImage`

Replace the file for a gallery image, preserving its ID and order position.

### Delete gallery image
`DELETE /api/v1/products/{productId}/gallery/{imageId}` | `deleteGalleryImage`

### Upload area image
`POST /api/v1/areas/{areaId}/image` | `uploadAreaImage`

### Delete area image
`DELETE /api/v1/areas/{areaId}/image` | `deleteAreaImage`

### Upload option image
`POST /api/v1/options/{optionId}/image` | `uploadOptionImage`

Upload or replace the option's base image.

### Delete option image
`DELETE /api/v1/options/{optionId}/image` | `deleteOptionImage`

### Upload option area override image
`POST /api/v1/options/{optionId}/image/areas/{areaId}` | `uploadOptionAreaImage`

Upload or replace an area-specific image override for the option.

### Delete option area override image
`DELETE /api/v1/options/{optionId}/image/areas/{areaId}` | `deleteOptionAreaImage`

---

## Areas

### List areas
`GET /api/v1/areas` | `listAreas`

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| cursor | string | No | Opaque cursor for next page |
| limit | integer | No | Items per page (default 25) |
| product_id | integer | No | Filter by product |
| search | string | No | Filter by name (case-insensitive partial match) |

**Response:** Paginated list of `AreaResponse`

<details><summary>Example response item</summary>

```json
{
  "id": 101,
  "name": "Frame Material",
  "description": "Select the frame material for your window.",
  "price": "0.00",
  "language": "EN",
  "order_index": 0,
  "allow_disable": false,
  "image_url": null,
  "area_group_id": null,
  "created_at": "2025-09-15T08:30:00Z",
  "updated_at": "2026-01-20T14:15:00Z",
  "links": {
    "self": {"href": "/api/v1/areas/101"},
    "option_groups": {"href": "/api/v1/areas/101/groups"},
    "area_group": null,
    "image": {"href": "/api/v1/areas/101/image"},
    "content": {"href": "/api/v1/areas/101/content"}
  }
}
```
</details>

### Create an area
`POST /api/v1/areas` | `createArea`

<details><summary>Example request</summary>

```json
{
  "name": "Frame Material",
  "description": "Select the frame material for your window.",
  "product_id": 42,
  "language": "EN"
}
```
</details>

### Get / Update / Partially update / Delete an area
`GET /api/v1/areas/{id}` | `getArea`
`PUT /api/v1/areas/{id}` | `updateArea`
`PATCH /api/v1/areas/{id}` | `patchArea`
`DELETE /api/v1/areas/{id}` | `deleteArea`

### List library areas
`GET /api/v1/areas/library` | `listLibraryAreas`

List areas not assigned to any product. **Not paginated.**

### List groups in an area
`GET /api/v1/areas/{id}/groups` | `listAreaGroups`

Returns groups linked to this area. **Not paginated.**

### Get area rich content
`GET /api/v1/areas/{id}/content` | `getAreaContent`

Returns EditorJS rich content blocks for an area. Supports all block types: header, paragraph, list, table, image, quote, delimiter, warning, embed, code, safety_notice, hp_statement.

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| language | string | No | Language code (e.g. 'DE', 'EN') |

<details><summary>Example response</summary>

```json
{
  "data": {
    "area_id": 101,
    "language": "EN",
    "enabled": true,
    "blocks": [
      {"type": "header", "data": {"text": "Frame Material Overview", "level": 2}},
      {"type": "paragraph", "data": {"text": "Our premium frames are crafted from the finest materials."}},
      {"type": "list", "data": {"style": "unordered", "items": ["Aluminum", "Wood", "PVC"]}}
    ],
    "links": {
      "self": {"href": "/api/v1/areas/101/content?language=EN"},
      "area": {"href": "/api/v1/areas/101"},
      "upload_image": {"href": "/api/v1/areas/101/content/images"}
    }
  }
}
```
</details>

### Update area rich content
`PUT /api/v1/areas/{id}/content` | `updateAreaContent`

### Delete area rich content
`DELETE /api/v1/areas/{id}/content` | `deleteAreaContent`

Pass `language` query param to delete a specific language; omit to delete all content.

### Upload content image
`POST /api/v1/areas/{id}/content/images` | `uploadAreaContentImage`

Upload an image for use in EditorJS content blocks. Returns the URL to use in an image block's `data.file.url`.

### List / Create / Update / Delete area price overrides
`GET /api/v1/areas/{areaId}/price-overrides` | `listAreaPriceOverrides` -- **Not paginated.**
`POST /api/v1/areas/{areaId}/price-overrides` | `createAreaPriceOverride`
`PUT /api/v1/areas/{areaId}/price-overrides/{overrideId}` | `updateAreaPriceOverride`
`PATCH /api/v1/areas/{areaId}/price-overrides/{overrideId}` | `patchAreaPriceOverride`
`DELETE /api/v1/areas/{areaId}/price-overrides/{overrideId}` | `deleteAreaPriceOverride`

### Replace all area price overrides
`POST /api/v1/areas/{areaId}/price-overrides/replace` | `replaceAreaPriceOverrides`

### List area options
`GET /api/v1/areas/{areaId}/options` | `listAreaOptions`

List all options available in an area (across all groups assigned to it). Paginated.

---

## Area Groups

### List / Create / Get / Update / Delete area groups
`GET /api/v1/area-groups` | `listAreaGroupResources` -- Paginated, filter by `product_id`.
`POST /api/v1/area-groups` | `createAreaGroup` -- Required: `name`, `product_id`.
`GET /api/v1/area-groups/{id}` | `getAreaGroup`
`PUT /api/v1/area-groups/{id}` | `updateAreaGroup`
`PATCH /api/v1/area-groups/{id}` | `patchAreaGroup`
`DELETE /api/v1/area-groups/{id}` | `deleteAreaGroup`

### List areas in an area group
`GET /api/v1/area-groups/{id}/areas` | `listAreaGroupAreas` -- **Not paginated.**

---

## Groups

### List groups
`GET /api/v1/groups` | `listGroups`

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| cursor | string | No | Opaque cursor for next page |
| limit | integer | No | Items per page (default 25) |
| search | string | No | Filter by name (case-insensitive partial match) |
| area_id | integer | No | Filter by area assignment |

<details><summary>Example response item</summary>

```json
{
  "id": 201,
  "name": "Wood Type",
  "description": "Choose from our selection of premium woods.",
  "key": "wood_type",
  "is_multi": false,
  "order_index": 0,
  "language": "EN",
  "area_ids": [101, 102],
  "links": {
    "self": {"href": "/api/v1/groups/201"},
    "options": {"href": "/api/v1/groups/201/options"},
    "areas": {"href": "/api/v1/groups/201/areas"}
  }
}
```
</details>

### Create a group
`POST /api/v1/groups` | `createGroup`

<details><summary>Example request</summary>

```json
{
  "name": "Wood Type",
  "description": "Choose from our selection of premium woods.",
  "key": "wood_type",
  "is_multi": false,
  "area_id": 101
}
```
</details>

### Get / Update / Partially update / Delete a group
`GET /api/v1/groups/{id}` | `getGroup`
`PUT /api/v1/groups/{id}` | `updateGroup`
`PATCH /api/v1/groups/{id}` | `patchGroup`
`DELETE /api/v1/groups/{id}` | `deleteGroup`

### Duplicate a group
`POST /api/v1/groups/{id}/duplicate` | `duplicateGroup`

Deep-copy the group including all options.

### List options in a group
`GET /api/v1/groups/{id}/options` | `listGroupOptions` -- **Not paginated.**

### List areas linked to a group
`GET /api/v1/groups/{id}/areas` | `listGroupAreas` -- **Not paginated.**

### Link a group to areas
`POST /api/v1/groups/{id}/areas` | `linkGroupAreas`

Already-linked areas are silently skipped (idempotent).

```json
{"area_ids": [101, 102, 103]}
```

### Unlink a group from an area
`DELETE /api/v1/groups/{id}/areas/{area_id}` | `unlinkGroupArea`

Removes the group-area association and cleans up area-specific data (OptionAreaConfig, OptionPriceOverride, OptionAdvancedPrice rows).

---

## Options

### List / Create / Get / Update / Delete options
`GET /api/v1/options` | `listOptions` -- Paginated. Filter by `group_id`, `search`.
`POST /api/v1/options` | `createOption`
`GET /api/v1/options/{id}` | `getOption`
`PUT /api/v1/options/{id}` | `updateOption`
`PATCH /api/v1/options/{id}` | `patchOption`
`DELETE /api/v1/options/{id}` | `deleteOption`

<details><summary>Example OptionResponse</summary>

```json
{
  "id": 301,
  "name": "Oak",
  "description": "Solid European oak, FSC certified.",
  "price": "85.00",
  "key": "oak",
  "order_index": 0,
  "recommended": true,
  "is_numbered": false,
  "number_min": null,
  "number_max": null,
  "number_step": null,
  "number_unit": "",
  "image_url": "/static/uploads/options/oak-texture.jpg",
  "language": "EN",
  "group_id": 201,
  "price_scalings": {"10": 0.95, "50": 0.90},
  "created_at": "2025-09-15T08:30:00Z",
  "updated_at": "2026-01-20T14:15:00Z",
  "links": {"self": {"href": "/api/v1/options/301"}}
}
```
</details>

### Get effective price for an option
`GET /api/v1/options/{id}/effective` | `getEffectivePrice`

Returns the effective price considering overrides.

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| price_list_id | integer | No | Price list ID |
| area_id | integer | No | Area ID |

### List / Create / Update / Delete advanced prices
`GET /api/v1/options/{optionId}/advanced-prices` | `listAdvancedPrices` -- **Not paginated.**
`POST /api/v1/options/{optionId}/advanced-prices` | `createAdvancedPrice`
`PUT /api/v1/options/{optionId}/advanced-prices/{priceId}` | `updateAdvancedPrice`
`PATCH /api/v1/options/{optionId}/advanced-prices/{priceId}` | `patchAdvancedPrice`
`DELETE /api/v1/options/{optionId}/advanced-prices/{priceId}` | `deleteAdvancedPrice`

### Get / Set area-specific config for an option
`GET /api/v1/options/{optionId}/area-config?area_id=101` | `getOptionAreaConfig`
`PUT /api/v1/options/{optionId}/area-config?area_id=101` | `setOptionAreaConfig`

Override price, key, numbering, description, or recommended flag per area.

---

## Price Overrides

Option-level price overrides for specific price lists and/or areas.

### List / Create price overrides
`GET /api/v1/options/{optionId}/price-overrides` | `listPriceOverrides`
`POST /api/v1/options/{optionId}/price-overrides` | `createPriceOverride`

### Update / Delete price overrides
`PUT /api/v1/options/{optionId}/price-overrides/{overrideId}` | `updatePriceOverride`
`PATCH /api/v1/options/{optionId}/price-overrides/{overrideId}` | `patchPriceOverride`
`DELETE /api/v1/options/{optionId}/price-overrides/{overrideId}` | `deletePriceOverride`

### Replace all price overrides
`POST /api/v1/options/{optionId}/price-overrides/replace` | `replacePriceOverrides`

Delete all existing overrides and replace with the provided set.

---

## Price Lists

### List / Create / Get / Update / Delete price lists
`GET /api/v1/price-lists` | `listPriceLists`
`POST /api/v1/price-lists` | `createPriceList`
`GET /api/v1/price-lists/{id}` | `getPriceList`
`PUT /api/v1/price-lists/{id}` | `updatePriceList`
`PATCH /api/v1/price-lists/{id}` | `patchPriceList`
`DELETE /api/v1/price-lists/{id}` | `deletePriceList`

<details><summary>Example PriceListResponse</summary>

```json
{
  "id": 10,
  "name": "EU Retail 2026",
  "description": "Standard retail pricing for European markets.",
  "order_index": 0,
  "is_base": true,
  "currency": "EUR",
  "created_at": "2025-09-15T08:30:00Z",
  "updated_at": "2026-01-20T14:15:00Z",
  "links": {"self": {"href": "/api/v1/price-lists/10"}}
}
```
</details>

### Reorder price lists
`POST /api/v1/price-lists/reorder` | `reorderPriceLists`

### List price list overrides
`GET /api/v1/price-lists/{priceListId}/overrides` | `listPriceListOverrides`

List all option price overrides for a given price list. Paginated.

---

## Catalog Filters

### List catalog filter dimensions
`GET /api/v1/catalog-filters` | `listCatalogFilters` -- **Not paginated.**

Returns all catalog filter dimensions with their values.

<details><summary>Example response</summary>

```json
{
  "data": [
    {
      "id": 1,
      "label": "Product Line",
      "slug": "product-line",
      "order_index": 0,
      "display_type": "pills",
      "is_visible": true,
      "multi_select": false,
      "values": [
        {"id": 10, "label": "Entry", "slug": "entry", "order_index": 0, "color": null},
        {"id": 11, "label": "Pro", "slug": "pro", "order_index": 1, "color": "#0066FF"}
      ],
      "links": {
        "self": {"href": "/api/v1/catalog-filters/1"},
        "values": {"href": "/api/v1/catalog-filters/1/values"}
      }
    }
  ]
}
```
</details>

### Create / Get / Update / Delete catalog filter dimensions
`POST /api/v1/catalog-filters` | `createCatalogFilter` -- Maximum 5 per company.
`GET /api/v1/catalog-filters/{id}` | `getCatalogFilter`
`PUT /api/v1/catalog-filters/{id}` | `updateCatalogFilter`
`DELETE /api/v1/catalog-filters/{id}` | `deleteCatalogFilter`

### Reorder catalog filter dimensions
`POST /api/v1/catalog-filters/reorder` | `reorderCatalogFilters`

### Add / Update / Delete / Reorder filter values
`POST /api/v1/catalog-filters/{id}/values` | `createCatalogFilterValue` -- Maximum 30 per dimension.
`PUT /api/v1/catalog-filters/{id}/values/{valueId}` | `updateCatalogFilterValue`
`DELETE /api/v1/catalog-filters/{id}/values/{valueId}` | `deleteCatalogFilterValue`
`POST /api/v1/catalog-filters/{id}/values/reorder` | `reorderCatalogFilterValues`

---

## Customers

### List / Create / Get / Update / Delete customers
`GET /api/v1/customers` | `listCustomers` -- Filter by `search`, `country`.
`POST /api/v1/customers` | `createCustomer`
`GET /api/v1/customers/{id}` | `getCustomer`
`PUT /api/v1/customers/{id}` | `updateCustomer`
`PATCH /api/v1/customers/{id}` | `patchCustomer`
`DELETE /api/v1/customers/{id}` | `deleteCustomer`

<details><summary>Example CustomerResponse</summary>

```json
{
  "id": 500,
  "customer_id": "CUST-2026-0042",
  "organization": "Acme Windows GmbH",
  "email": "procurement@acme-windows.de",
  "phone": "+49 30 12345678",
  "address_street": "Fensterstr. 12",
  "address_zip": "10115",
  "address_city": "Berlin",
  "address_country": "Germany",
  "integration_metadata": {"crm_id": "SF-ACC-00042", "erp_code": "K10042"},
  "secret_key": "sk_cust_abc123def456",
  "contacts": [
    {"id": 1, "first_name": "Anna", "last_name": "Schmidt", "email": "a.schmidt@acme-windows.de", "phone": "+49 30 12345679", "position": "Procurement Manager"}
  ],
  "links": {"self": {"href": "/api/v1/customers/500"}, "contacts": {"href": "/api/v1/customers/500/contacts"}}
}
```
</details>

### Search customers
`GET /api/v1/customers/search` | `searchCustomers`

Quick search across organization, email, and customer ID. Returns up to 50 results. **Not paginated.**

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| q | string | Yes | Search query (min 2 chars) |

### List / Add / Update / Remove contacts
`GET /api/v1/customers/{id}/contacts` | `listContacts` -- **Not paginated.**
`POST /api/v1/customers/{id}/contacts` | `createContact`
`PUT /api/v1/customers/{id}/contacts/{contact_id}` | `updateContact`
`DELETE /api/v1/customers/{id}/contacts/{contact_id}` | `deleteContact`

### Customer cross-references
`GET /api/v1/customers/{customerId}/quotes` | `listCustomerQuotes` -- Paginated.
`GET /api/v1/customers/{customerId}/opportunities` | `listCustomerOpportunities` -- Paginated.
`GET /api/v1/customers/{customerId}/configurations` | `listCustomerConfigurations` -- Paginated.

---

## Languages

### CRUD + Reorder
`GET /api/v1/languages` | `listLanguages`
`POST /api/v1/languages` | `createLanguage`
`GET /api/v1/languages/{id}` | `getLanguage`
`PUT /api/v1/languages/{id}` | `updateLanguage`
`PATCH /api/v1/languages/{id}` | `patchLanguage`
`DELETE /api/v1/languages/{id}` | `deleteLanguage`
`POST /api/v1/languages/reorder` | `reorderLanguages`

<details><summary>Example LanguageResponse</summary>

```json
{"id": 1, "code": "EN", "name": "English", "is_base": true, "order_index": 0, "links": {"self": {"href": "/api/v1/languages/1"}}}
```
</details>

---

## Constraints

### List option-level forbidden combinations
`GET /api/v1/constraints?product_id=42` | `listConstraints`

Returns all pair-level forbidden combinations for a product. These prevent two specific options from being selected together.

### Replace option-level forbidden combinations
`POST /api/v1/constraints` | `replaceConstraints`

Atomically replaces all option-level forbidden combinations for a product. Include the `X-Constraints-Version` header for optimistic concurrency control.

### List / Replace area-level forbidden combinations
`GET /api/v1/constraints/area?product_id=42` | `listAreaConstraints`
`POST /api/v1/constraints/area` | `replaceAreaConstraints`

### Check if a combination is forbidden
`POST /api/v1/constraints/check` | `checkConstraint`

<details><summary>Example request / response</summary>

```json
// Request
{"product_id": 42, "option_id1": 301, "option_id2": 305}

// Response
{"data": {"forbidden": true, "pair_conflict": true, "rule_conflict": false}}
```
</details>

### List / Create / Get / Update / Delete constraint rules
`GET /api/v1/constraints/rules` | `listConstraintRules` -- Filter by `product_id`, `area_id`.
`POST /api/v1/constraints/rules` | `createConstraintRule`
`GET /api/v1/constraints/rules/{id}` | `getConstraintRule`
`PUT /api/v1/constraints/rules/{id}` | `updateConstraintRule`
`PATCH /api/v1/constraints/rules/{id}` | `patchConstraintRule`
`DELETE /api/v1/constraints/rules/{id}` | `deleteConstraintRule`

<details><summary>Example ForbiddenRuleResponse</summary>

```json
{
  "id": 10,
  "product_id": 42,
  "area_id": 101,
  "description": "Oak frame incompatible with plastic glazing beads",
  "rule_json": [{"if": {"option_selected": 301}, "then": {"forbid_options": [410, 411]}}],
  "links": {"self": {"href": "/api/v1/constraints/rules/10"}}
}
```
</details>

---

## Attributes

### CRUD for attributes and values
`GET /api/v1/attributes` | `listAttributes` -- Paginated.
`POST /api/v1/attributes` | `createAttribute`
`GET /api/v1/attributes/{id}` | `getAttribute`
`PUT /api/v1/attributes/{id}` | `updateAttribute`
`PATCH /api/v1/attributes/{id}` | `patchAttribute`
`DELETE /api/v1/attributes/{id}` | `deleteAttribute`

### Attribute values
`GET /api/v1/attributes/{id}/values` | `listAttributeValues` -- Filter by `element_type` (product/area/option) and `element_id`.
`POST /api/v1/attributes/{id}/values` | `createAttributeValue`
`PUT /api/v1/attributes/values/{id}` | `updateAttributeValue`
`PATCH /api/v1/attributes/values/{id}` | `patchAttributeValue`
`DELETE /api/v1/attributes/values/{id}` | `deleteAttributeValue`

---

## Configurations

### List saved configurations
`GET /api/v1/configurations` | `listConfigurations` -- Filter by `product_id`.

### Calculate a configuration
`POST /api/v1/configurations/calculate` | `calculateConfiguration`

Resolve constraints, compute pricing, and return a configuration state.

<details><summary>Example request</summary>

```json
{
  "product_id": 42,
  "selected_options": {"101": [301], "102": [350, 351]},
  "option_amounts": {"350": 3},
  "disabled_areas": [],
  "enabled_areas": [101, 102],
  "price_list_id": 10,
  "validate_config": true
}
```
</details>

### Get configuration state by hash
`GET /api/v1/configurations/states/{hash}` | `getConfigurationState`

### Get configuration state by code
`GET /api/v1/configurations/states/by-code/{code}` | `getConfigurationStateByCode`

Supports ETag/If-None-Match conditional caching. States are immutable.

### Get enriched selected options
`GET /api/v1/configurations/states/by-code/{code}/selections` | `getConfigurationSelections`

Returns each selected option enriched with group name, option name, price, quantity, and wishlist status.

### Get configured parts (BOM)
`GET /api/v1/configurations/states/by-code/{code}/parts` | `getConfigurationParts`

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| limit | integer | No | Max parts per page (default 200, max 500) |
| offset | integer | No | Number of parts to skip |

### Get a saved configuration
`GET /api/v1/configurations/{id}` | `getConfiguration`

### Finalize a configuration
`POST /api/v1/configurations/{id}/finalize` | `finalizeConfiguration`

Lock the configuration so it cannot be modified.

---

## Opportunities

### CRUD
`GET /api/v1/opportunities` | `listOpportunities` -- Filter by `stage`, `customer_id`, `search`.
`POST /api/v1/opportunities` | `createOpportunity`
`GET /api/v1/opportunities/{id}` | `getOpportunity`
`PUT /api/v1/opportunities/{id}` | `updateOpportunity`
`PATCH /api/v1/opportunities/{id}` | `patchOpportunity`
`DELETE /api/v1/opportunities/{id}` | `deleteOpportunity`

<details><summary>Example OpportunityResponse</summary>

```json
{
  "id": 600,
  "opportunity_number": "OPP-2026-0015",
  "name": "Acme HQ Renovation -- Windows",
  "description": "Full window replacement for the Acme headquarters building.",
  "stage": "drafting",
  "status": "open",
  "probability": 40,
  "expected_amount": 48500.00,
  "expected_close_date": "2026-06-30",
  "customer_id": 500,
  "customer_name": "Acme Windows GmbH",
  "owner_contact_id": 1,
  "primary_quote_id": 700,
  "quote_count": 2,
  "integration_metadata": {"crm_deal_id": "DEAL-2026-015"},
  "links": {"self": {"href": "/api/v1/opportunities/600"}, "quotes": {"href": "/api/v1/opportunities/600/quotes"}}
}
```
</details>

### List quotes for an opportunity
`GET /api/v1/opportunities/{id}/quotes` | `listOpportunityQuotes` -- **Not paginated.**

---

## Quotes

### CRUD
`GET /api/v1/quotes` | `listQuotes` -- Filter by `status`, `opportunity_id`.
`POST /api/v1/quotes` | `createQuote` -- If no opportunity_id is given but customer_id is provided, an opportunity is auto-created.
`GET /api/v1/quotes/{id}` | `getQuote`
`PUT /api/v1/quotes/{id}` | `updateQuote`
`PATCH /api/v1/quotes/{id}` | `patchQuote`
`DELETE /api/v1/quotes/{id}` | `deleteQuote`

<details><summary>Example QuoteResponse</summary>

```json
{
  "id": 700,
  "quote_number": "QUO-2026-0042",
  "version_number": 1,
  "status": "draft",
  "is_primary": true,
  "opportunity_id": 600,
  "customer_id": 500,
  "customer_name": "Acme Windows GmbH",
  "currency": "EUR",
  "price_list_id": 10,
  "price_list_name": "EU Retail 2026",
  "total_amount": "48500.00",
  "discount_percent": "5.00",
  "discount_amount": "2425.00",
  "tax_amount": "8754.25",
  "final_amount": "54829.25",
  "valid_from": "2026-02-01",
  "valid_until": "2026-04-30",
  "notes": "Includes installation and 5-year warranty.",
  "line_item_count": 3,
  "links": {"self": {"href": "/api/v1/quotes/700"}, "line_items": {"href": "/api/v1/quotes/700/line-items"}}
}
```
</details>

### Update quote status
`PUT /api/v1/quotes/{id}/status` | `updateQuoteStatus`

```json
{"status": "approved"}
```

### Create a new revision
`POST /api/v1/quotes/{id}/revise` | `reviseQuote`

Creates a new version of this quote, incrementing the version number.

### List quote revisions
`GET /api/v1/quotes/{id}/revisions` | `listQuoteRevisions`

### Line items
`GET /api/v1/quotes/{id}/line-items` | `listLineItems`
`POST /api/v1/quotes/{id}/line-items` | `createLineItem`
`PUT /api/v1/quotes/{id}/line-items/{item_id}` | `updateLineItem`
`PATCH /api/v1/quotes/{id}/line-items/{item_id}` | `patchLineItem`
`DELETE /api/v1/quotes/{id}/line-items/{item_id}` | `deleteLineItem`

### Quote details (extended)
`GET /api/v1/quotes/{quoteId}/details` | `getQuoteDetails`
`PUT /api/v1/quotes/{quoteId}/details` | `upsertQuoteDetails`
`PATCH /api/v1/quotes/{quoteId}/details` | `patchQuoteDetails`

Extended details: payment terms, shipping method, shipping cost, internal notes, custom fields.

### Quote contacts
`GET /api/v1/quotes/{quoteId}/contacts` | `listQuoteContacts` -- **Not paginated.**
`POST /api/v1/quotes/{quoteId}/contacts` | `addQuoteContact`
`DELETE /api/v1/quotes/{quoteId}/contacts/{contactId}` | `removeQuoteContact`

---

## Documents

### Templates CRUD
`GET /api/v1/documents/templates` | `listDocumentTemplates` -- Filter by `doc_type`, `product_id`.
`POST /api/v1/documents/templates` | `createDocumentTemplate`
`GET /api/v1/documents/templates/{id}` | `getDocumentTemplate`
`PUT /api/v1/documents/templates/{id}` | `updateDocumentTemplate`
`PATCH /api/v1/documents/templates/{id}` | `patchDocumentTemplate`
`DELETE /api/v1/documents/templates/{id}` | `deleteDocumentTemplate`

### Clone a template
`POST /api/v1/documents/templates/{id}/clone` | `cloneTemplate`

Deep copy including structure blocks, locale titles, and content block attachments.

### Create an inheritance variant
`POST /api/v1/documents/templates/{id}/variants` | `createVariant`

Modes: **link** (read-only mirror), **extend** (inherits + auto-syncs, allows additions), **fork** (independent deep copy).

### Translate entire template
`POST /api/v1/documents/templates/{id}/translate` | `translateTemplate`

Translates all structure block titles and attached content block locales to the target language via DeepL.

### Template structure
`GET /api/v1/documents/templates/{id}/structure` | `getStructureTree` -- **Not paginated.** Pass `?language=DE` for locale-specific titles.
`POST /api/v1/documents/templates/{id}/structure/blocks` | `createStructureBlock`
`GET /api/v1/documents/templates/{id}/structure/blocks/{block_id}` | `getStructureBlock`
`PUT /api/v1/documents/templates/{id}/structure/blocks/{block_id}` | `updateStructureBlock`
`DELETE /api/v1/documents/templates/{id}/structure/blocks/{block_id}` | `deleteStructureBlock` -- Cascade deletes children, locales, attachments.
`POST /api/v1/documents/templates/{id}/structure/reorder` | `reorderStructureBlocks`
`POST /api/v1/documents/templates/{id}/structure/blocks/{block_id}/move` | `moveStructureBlock`

### Structure block locales
`GET /api/v1/documents/templates/{id}/structure/blocks/{block_id}/locales` | `listStructureBlockLocales`
`PUT /api/v1/documents/templates/{id}/structure/blocks/{block_id}/locales/{lang}` | `upsertStructureBlockLocale`
`DELETE /api/v1/documents/templates/{id}/structure/blocks/{block_id}/locales/{lang}` | `deleteStructureBlockLocale`

### Structure block attachments
`GET /api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments` | `listStructureAttachments`
`POST /api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments` | `createStructureAttachment`
`GET /api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments/{att_id}` | `getStructureAttachment`
`PUT /api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments/{att_id}` | `updateStructureAttachment`
`DELETE /api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments/{att_id}` | `deleteStructureAttachment`
`POST /api/v1/documents/templates/{id}/structure/blocks/{block_id}/attachments/reorder` | `reorderStructureAttachments`

### Structure batch operations
`POST /api/v1/documents/templates/{id}/structure/batch` | `batchStructureOperations`

### Content blocks
`GET /api/v1/documents/content-blocks` | `listContentBlocks` -- Paginated. Filter by `product_id`, `directory_id`, `tag`, `search`, `is_active`.
`POST /api/v1/documents/content-blocks` | `createContentBlock`
`GET /api/v1/documents/content-blocks/{id}` | `getContentBlock`
`PUT /api/v1/documents/content-blocks/{id}` | `updateContentBlock`
`DELETE /api/v1/documents/content-blocks/{id}` | `deleteContentBlock`
`POST /api/v1/documents/content-blocks/{id}/set-version` | `setContentBlockVersion`

### Content block locales
`GET /api/v1/documents/content-blocks/{id}/locales` | `listContentBlockLocales` -- **Not paginated.**
`POST /api/v1/documents/content-blocks/{id}/locales` | `createContentBlockLocale` -- Upsert behavior.
`GET /api/v1/documents/content-blocks/{id}/locales/{locale_id}` | `getContentBlockLocale`
`PUT /api/v1/documents/content-blocks/{id}/locales/{locale_id}` | `updateContentBlockLocale`
`DELETE /api/v1/documents/content-blocks/{id}/locales/{locale_id}` | `deleteContentBlockLocale`
`POST /api/v1/documents/content-blocks/{id}/locales/{locale_id}/translate` | `translateContentBlockLocale`

### Content block images
`POST /api/v1/documents/content-blocks/images` | `uploadEditorJsImage`
`DELETE /api/v1/documents/content-blocks/images` | `deleteEditorJsImage`

### Content block batch
`POST /api/v1/documents/content-blocks/batch` | `batchContentBlocks` -- Up to 100 operations. Returns 207 on partial failures.

### Content directories
`GET /api/v1/documents/content-directories` | `listContentDirectories` -- **Not paginated.** Returns nested tree.
`POST /api/v1/documents/content-directories` | `createContentDirectory`
`GET /api/v1/documents/content-directories/{id}` | `getContentDirectory`
`PUT /api/v1/documents/content-directories/{id}` | `updateContentDirectory`
`DELETE /api/v1/documents/content-directories/{id}` | `deleteContentDirectory`

### Document instances
`GET /api/v1/documents/instances` | `listDocumentInstances` -- Filter by `template_id`, `quote_id`, `context_type`.
`POST /api/v1/documents/instances` | `createDocumentInstance`
`GET /api/v1/documents/instances/{id}` | `getDocumentInstance`
`DELETE /api/v1/documents/instances/{id}` | `deleteDocumentInstance`

### Instance blocks
`GET /api/v1/documents/instances/{id}/blocks` | `listInstanceBlocks` -- **Not paginated.**
`GET /api/v1/documents/instances/{id}/blocks/{block_id}` | `getInstanceBlock`
`PUT /api/v1/documents/instances/{id}/blocks/{block_id}` | `updateInstanceBlock`
`DELETE /api/v1/documents/instances/{id}/blocks/{block_id}` | `deleteInstanceBlock`

### Instance attachments
`POST /api/v1/documents/instances/{id}/attachments` | `createInstanceAttachment`
`PUT /api/v1/documents/instances/{id}/attachments/{att_id}` | `updateInstanceAttachment`
`DELETE /api/v1/documents/instances/{id}/attachments/{att_id}` | `deleteInstanceAttachment`

### Publish document instance
`POST /api/v1/documents/instances/{id}/publish` | `publishInstance`

Render the instance as HTML, PDF, or Markdown. Optionally create a public link.

### Public links
`GET /api/v1/documents/instances/{id}/public-links` | `listPublicLinks` -- **Not paginated.**
`GET /api/v1/documents/instances/{id}/public-links/{link_id}` | `getPublicLink`
`DELETE /api/v1/documents/instances/{id}/public-links/{link_id}` | `deletePublicLink`

---

## Offer Sections

### CRUD + Reorder + Content
`GET /api/v1/products/{productId}/offer-sections` | `listOfferSections` -- **Not paginated.**
`POST /api/v1/products/{productId}/offer-sections` | `createOfferSection`
`GET /api/v1/products/{productId}/offer-sections/{sectionId}` | `getOfferSection`
`PUT /api/v1/products/{productId}/offer-sections/{sectionId}` | `updateOfferSection`
`PATCH /api/v1/products/{productId}/offer-sections/{sectionId}` | `patchOfferSection`
`DELETE /api/v1/products/{productId}/offer-sections/{sectionId}` | `deleteOfferSection`
`POST /api/v1/products/{productId}/offer-sections/reorder` | `reorderOfferSections`

### Offer section content
`GET /api/v1/products/{productId}/offer-sections/{sectionId}/content` | `listOfferSectionContent` -- Filter by `language`.
`PUT /api/v1/products/{productId}/offer-sections/{sectionId}/content` | `upsertOfferSectionContent`
`DELETE /api/v1/products/{productId}/offer-sections/{sectionId}/content/{contentId}` | `deleteOfferSectionContent`

---

## Product Media

### Video links
`GET /api/v1/products/{productId}/videos` | `listVideoLinks` -- **Not paginated.** Max 20.
`POST /api/v1/products/{productId}/videos` | `createVideoLink`
`PUT /api/v1/products/{productId}/videos/{videoId}` | `updateVideoLink`
`DELETE /api/v1/products/{productId}/videos/{videoId}` | `deleteVideoLink`
`POST /api/v1/products/{productId}/videos/reorder` | `reorderVideoLinks`

### 3D model links
`GET /api/v1/products/{productId}/models` | `listModelLinks` -- **Not paginated.** Max 20.
`POST /api/v1/products/{productId}/models` | `createModelLink`
`PUT /api/v1/products/{productId}/models/{modelId}` | `updateModelLink`
`DELETE /api/v1/products/{productId}/models/{modelId}` | `deleteModelLink`
`POST /api/v1/products/{productId}/models/reorder` | `reorderModelLinks`

---

## Translations

### List translations
`GET /api/v1/translations` | `listTranslations` -- **Not paginated.**

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| entity_type | string | No | Entity type (product, area, group, option) |
| entity_id | integer | No | Entity ID |
| language | string | No | Language code |

### Upsert translations
`PUT /api/v1/translations` | `upsertTranslations`

Create or update translations in bulk.

### Dictionary
`GET /api/v1/translations/dictionary` | `listDictionaryEntries` -- **Not paginated.**
`POST /api/v1/translations/dictionary` | `upsertDictionaryEntry`

---

## Webhooks

### CRUD
`GET /api/v1/webhooks` | `listWebhooks`
`POST /api/v1/webhooks` | `createWebhook`
`GET /api/v1/webhooks/{id}` | `getWebhook`
`PUT /api/v1/webhooks/{id}` | `updateWebhook`
`PATCH /api/v1/webhooks/{id}` | `patchWebhook`
`DELETE /api/v1/webhooks/{id}` | `deleteWebhook`

<details><summary>Example WebhookSubscriptionResponse</summary>

```json
{
  "id": 5,
  "name": "Quote notifications",
  "url": "https://integrations.acme-windows.de/webhooks/rattleapp",
  "events": ["quote.created", "quote.status_changed"],
  "is_active": true,
  "created_at": "2026-01-05T08:00:00Z",
  "links": {"self": {"href": "/api/v1/webhooks/5"}, "deliveries": {"href": "/api/v1/webhooks/5/deliveries"}}
}
```
</details>

### Send a test event
`POST /api/v1/webhooks/{id}/test` | `testWebhook`

### Rotate webhook signing secret
`POST /api/v1/webhooks/{id}/rotate-secret` | `rotateWebhookSecret`

### List delivery attempts
`GET /api/v1/webhooks/{id}/deliveries` | `listWebhookDeliveries` -- Paginated.

### Get delivery detail
`GET /api/v1/webhooks/deliveries/{id}` | `getWebhookDelivery`

### List available webhook events
`GET /api/v1/webhooks/events` | `listWebhookEvents` -- **Not paginated.**

Returns the catalog of all event types available for webhook subscriptions.

---

## Inbound Webhooks

### Send an inbound event
`POST /api/v1/inbound/events` | `sendInboundEvent`

```json
{"event_type": "order.placed", "data": {...}, "idempotency_key": "unique-key"}
```

### Upsert an inbound customer
`POST /api/v1/inbound/customers` | `upsertInboundCustomer`

Create or update a customer from an external system. Required: `external_id`.

### Batch upsert inbound customers
`POST /api/v1/inbound/customers/batch` | `batchUpsertInboundCustomers`

### Create an inbound opportunity
`POST /api/v1/inbound/opportunities` | `createInboundOpportunity`

Create an opportunity with optional configuration and quote from an external system.

### Batch upsert inbound parts
`POST /api/v1/inbound/parts/batch` | `batchUpsertInboundParts`

### Trigger a connector task
`POST /api/v1/inbound/connectors/tasks/{id}/trigger` | `triggerInboundConnectorTask`

### Fire a webhook trigger by path
`POST /api/v1/inbound/triggers/{suffix}` | `fireWebhookTrigger`

External systems POST to this endpoint to trigger a connector task by its configured path suffix.

---

## API Keys

> API key creation, rotation, revocation, and permanent deletion require **session authentication** (not Bearer token).

### List API keys
`GET /api/v1/api-keys` | `listApiKeys`

### Create an API key
`POST /api/v1/api-keys` | `createApiKey` -- **Session auth only.**

The plaintext key is returned only once.

<details><summary>Example response</summary>

```json
{
  "data": {
    "id": 3,
    "name": "CI/CD Pipeline",
    "key": "rk_example_key_placeholder",
    "key_prefix": "rk_live_abc1",
    "scopes": ["products:read", "products:write", "prices:read"],
    "expires_at": null,
    "created_at": "2025-11-01T10:00:00Z",
    "links": {"self": {"href": "/api/v1/api-keys/3"}}
  }
}
```
</details>

### Get an API key
`GET /api/v1/api-keys/{id}` | `getApiKey`

### Revoke an API key
`DELETE /api/v1/api-keys/{id}` | `revokeApiKey` -- **Session auth only.** Soft-revoke: deactivates but keeps record.

### Permanently delete an API key
`DELETE /api/v1/api-keys/{id}/permanent` | `deleteApiKeyPermanent` -- **Session auth only.** Hard-delete: cannot be undone.

### Rotate an API key
`POST /api/v1/api-keys/{id}/rotate` | `rotateApiKey` -- **Session auth only.** Revokes current and issues new.

### Get API key usage statistics
`GET /api/v1/api-keys/usage` | `getApiKeyUsage`

---

## Connectors

### CRUD
`GET /api/v1/connectors` | `listConnectors`
`POST /api/v1/connectors` | `createConnector`
`GET /api/v1/connectors/{id}` | `getConnector`
`PUT /api/v1/connectors/{id}` | `updateConnector`
`PATCH /api/v1/connectors/{id}` | `patchConnector`
`DELETE /api/v1/connectors/{id}` | `deleteConnector`

### Endpoints
`GET /api/v1/connectors/{id}/endpoints` | `listConnectorEndpoints`
`POST /api/v1/connectors/{id}/endpoints` | `createConnectorEndpoint`
`DELETE /api/v1/connectors/endpoints/{id}` | `deleteConnectorEndpoint`

### Tasks
`GET /api/v1/connectors/{id}/tasks` | `listConnectorTasks`
`POST /api/v1/connectors/{id}/tasks` | `createConnectorTask`
`GET /api/v1/connectors/tasks/{id}` | `getConnectorTask`
`DELETE /api/v1/connectors/tasks/{id}` | `deleteConnectorTask`
`POST /api/v1/connectors/tasks/{id}/run` | `runConnectorTask` -- Returns `202 Accepted`.

### Triggers
`GET /api/v1/connectors/triggers` | `listConnectorTriggers` -- **Not paginated.**
`POST /api/v1/connectors/triggers` | `createConnectorTrigger`
`PUT /api/v1/connectors/triggers/{id}` | `updateConnectorTrigger`
`DELETE /api/v1/connectors/triggers/{id}` | `deleteConnectorTrigger`

### Jobs
`GET /api/v1/connectors/jobs` | `listConnectorJobs` -- Paginated. Filter by `status`.
`GET /api/v1/connectors/jobs/{id}` | `getConnectorJob`
`POST /api/v1/connectors/jobs/{id}/replay` | `replayConnectorJob` -- Re-execute using original input context.
`GET /api/v1/connectors/jobs/{jobId}/logs` | `listConnectorJobLogs` -- Paginated.

---

## Company

### Settings
`GET /api/v1/company` | `getCompanySettings`
`PUT /api/v1/company` | `updateCompanySettings`
`PATCH /api/v1/company` | `patchCompanySettings`

### Configurator settings
`GET /api/v1/company/configurator-settings` | `getConfiguratorSettings`
`PUT /api/v1/company/configurator-settings` | `updateConfiguratorSettings`
`PATCH /api/v1/company/configurator-settings` | `patchConfiguratorSettings`

### Connector settings
`GET /api/v1/company/connector-settings` | `getConnectorSettings`
`PUT /api/v1/company/connector-settings` | `updateConnectorSettings`
`PATCH /api/v1/company/connector-settings` | `patchConnectorSettings`

### Company contacts
`GET /api/v1/company/contacts` | `listCompanyContacts` -- **Not paginated.**
`POST /api/v1/company/contacts` | `createCompanyContact` -- Required: `name`.
`PUT /api/v1/company/contacts/{id}` | `updateCompanyContact`
`PATCH /api/v1/company/contacts/{id}` | `patchCompanyContact`
`DELETE /api/v1/company/contacts/{id}` | `deleteCompanyContact`

---

## Parts

### CRUD
`GET /api/v1/parts` | `listParts` -- Filter by `status`, `part_type`, `search`.
`POST /api/v1/parts` | `createPart`
`GET /api/v1/parts/{id}` | `getPart`
`PUT /api/v1/parts/{id}` | `updatePart`
`PATCH /api/v1/parts/{id}` | `patchPart`
`DELETE /api/v1/parts/{id}` | `deletePart`

<details><summary>Example PartResponse</summary>

```json
{
  "id": 1500,
  "part_number": "FRM-OAK-001",
  "part_name": "Oak Frame Profile 80mm",
  "part_cost": 4200,
  "part_type": "manufactured",
  "part_description": "80mm oak frame profile, pre-treated.",
  "make_or_buy": "make",
  "commodity_code": "4418.10",
  "weight": 3.2,
  "weight_unit": "kg",
  "status": "active",
  "custom_fields": {"lead_time_days": 14},
  "integration_metadata": {"erp_part_id": "ERP-P-1500"},
  "image_url": "https://cdn.example.com/uploads/42/part_1500_abc123.jpg",
  "links": {"self": {"href": "/api/v1/parts/1500"}, "bom": {"href": "/api/v1/parts/1500/bom"}, "placements": {"href": "/api/v1/parts/1500/placements"}, "document_links": {"href": "/api/v1/parts/1500/document-links"}}
}
```
</details>

### Placements
`GET /api/v1/parts/{id}/placements` | `listPartPlacements`
`POST /api/v1/parts/{id}/placements` | `createPartPlacement`
`PUT /api/v1/parts/placements/{id}` | `updatePartPlacement`
`PATCH /api/v1/parts/placements/{id}` | `patchPartPlacement`
`DELETE /api/v1/parts/placements/{id}` | `deletePartPlacement`

### BOM (Bill of Materials)
`GET /api/v1/parts/{id}/bom` | `listBomChildren`
`POST /api/v1/parts/{id}/bom` | `createBomItem`
`PUT /api/v1/parts/bom/{id}` | `updateBomItem`
`PATCH /api/v1/parts/bom/{id}` | `patchBomItem`
`DELETE /api/v1/parts/bom/{id}` | `deleteBomItem`

### BOM tree / flat / where-used / validate
`GET /api/v1/parts/{id}/bom/tree` | `getBomTree` -- Recursive tree with cycle detection. Params: `max_depth` (default 20), `max_nodes` (default 5000).
`GET /api/v1/parts/{id}/bom/flat` | `getBomFlat` -- Flat list with level indicators.
`GET /api/v1/parts/{id}/where-used` | `getWhereUsed` -- Reverse BOM lookup.
`POST /api/v1/parts/{id}/bom/validate` | `validateBom` -- Check for cycles, missing children, duplicates.

### Part groups
`GET /api/v1/parts/groups` | `listPartGroups` -- Paginated.
`POST /api/v1/parts/groups` | `createPartGroup`
`GET /api/v1/parts/groups/{groupId}` | `getPartGroup`
`PUT /api/v1/parts/groups/{groupId}` | `updatePartGroup`
`PATCH /api/v1/parts/groups/{groupId}` | `patchPartGroup`
`DELETE /api/v1/parts/groups/{groupId}` | `deletePartGroup`

### Part changelog
`GET /api/v1/parts/{partId}/changelog` | `listPartChangelog` -- Paginated.

---

## Item Revisions

### CRUD + lifecycle
`GET /api/v1/parts/{partId}/revisions` | `listItemRevisions`
`POST /api/v1/parts/{partId}/revisions` | `createItemRevision`
`GET /api/v1/parts/{partId}/revisions/{revisionId}` | `getItemRevision`
`PUT /api/v1/parts/{partId}/revisions/{revisionId}` | `updateItemRevision` -- Only Draft or Review revisions.
`DELETE /api/v1/parts/{partId}/revisions/{revisionId}` | `deleteItemRevision` -- Only Draft or Review revisions.

### Release a revision
`POST /api/v1/parts/{partId}/revisions/{revisionId}/release` | `releaseItemRevision`

Transitions to Released state. Obsoletes the previous released revision for the same part.

### Obsolete a revision
`POST /api/v1/parts/{partId}/revisions/{revisionId}/obsolete` | `obsoleteItemRevision`

Marks a Released revision as Obsolete.

---

## Part Documents

### CRUD
`GET /api/v1/part-documents` | `listPartDocuments` -- Filter by `doc_type`, `lifecycle_state`, `search`.
`POST /api/v1/part-documents` | `createPartDocument`
`GET /api/v1/part-documents/{id}` | `getPartDocument`
`PUT /api/v1/part-documents/{id}` | `updatePartDocument`
`PATCH /api/v1/part-documents/{id}` | `patchPartDocument`
`DELETE /api/v1/part-documents/{id}` | `deletePartDocument`

### Document links (part-level)
`GET /api/v1/parts/{partId}/document-links` | `listPartDocumentLinks`
`POST /api/v1/parts/{partId}/document-links` | `createPartDocumentLink`
`DELETE /api/v1/parts/{partId}/document-links/{linkId}` | `deletePartDocumentLink`

### Document links (revision-level)
`GET /api/v1/parts/{partId}/revisions/{revisionId}/document-links` | `listRevisionDocumentLinks`
`POST /api/v1/parts/{partId}/revisions/{revisionId}/document-links` | `createRevisionDocumentLink`

### CAD files
`GET /api/v1/part-documents/{id}/cad-files` | `listCadFiles` -- **Not paginated.**
`POST /api/v1/part-documents/{id}/cad-files` | `createCadFile` -- Multipart upload.
`GET /api/v1/part-documents/{id}/cad-files/{fileId}` | `getCadFile`
`DELETE /api/v1/part-documents/{id}/cad-files/{fileId}` | `deleteCadFile`

### Derivatives
`GET /api/v1/part-documents/{id}/derivatives` | `listDerivatives` -- **Not paginated.**
`POST /api/v1/part-documents/{id}/derivatives` | `createDerivative` -- Request generation (thumbnail, preview, stl, pdf).
`GET /api/v1/part-documents/{id}/derivatives/{derivId}` | `getDerivative`
`DELETE /api/v1/part-documents/{id}/derivatives/{derivId}` | `deleteDerivative`

---

## Baselines

`GET /api/v1/baselines?product_id=42` | `listBaselines` -- `product_id` required.
`POST /api/v1/baselines` | `createBaseline`
`GET /api/v1/baselines/{id}` | `getBaseline`
`DELETE /api/v1/baselines/{id}` | `deleteBaseline`

<details><summary>Example BaselineResponse</summary>

```json
{
  "id": 30,
  "product_id": 42,
  "name": "v2.1 Release Baseline",
  "note": "Frozen before summer pricing update.",
  "item_count": 47,
  "created_at": "2026-02-01T00:00:00Z",
  "links": {"self": {"href": "/api/v1/baselines/30"}}
}
```
</details>

---

## Batch

### Universal batch operations
`POST /api/v1/batch` | `universalBatch`

Execute multiple operations across different resource types in a single request. Max 100 operations. Returns 200 if all succeed, 207 if any fail.

### Per-resource batch
`POST /api/v1/parts/batch` | `batchParts`
`POST /api/v1/products/batch` | `batchProducts`
`POST /api/v1/options/batch` | `batchOptions`
`POST /api/v1/groups/batch` | `batchGroups`
`POST /api/v1/areas/batch` | `batchAreas`
`POST /api/v1/customers/batch` | `batchCustomers`
`POST /api/v1/bom/batch` | `batchBom`

All support create/update/delete/upsert operations, up to 100 per request.

---

## Export

All export endpoints stream NDJSON (one JSON object per line). Use `updated_after` for incremental sync.

`GET /api/v1/products/export` | `exportProducts`
`GET /api/v1/customers/export` | `exportCustomers`
`GET /api/v1/parts/export` | `exportParts`

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| updated_after | string | No | ISO 8601 timestamp for incremental sync |

---

## Customer Links

`GET /api/v1/customer-links` | `listCustomerLinks` -- Paginated. Filter by `product_id`.
`POST /api/v1/customer-links` | `createCustomerLink` -- Required: `name`, `product_id`.
`GET /api/v1/customer-links/{id}` | `getCustomerLink`
`PUT /api/v1/customer-links/{id}` | `updateCustomerLink`
`PATCH /api/v1/customer-links/{id}` | `patchCustomerLink`
`DELETE /api/v1/customer-links/{id}` | `deleteCustomerLink`

---

## Branches

`GET /api/v1/branches` | `listBranches` -- Paginated. Scope: `parts:read`.
`POST /api/v1/branches` | `createBranch`
`GET /api/v1/branches/{branchId}` | `getBranch`
`DELETE /api/v1/branches/{branchId}` | `deleteBranch`

---

## Pull Requests

`GET /api/v1/branches/{branchId}/pull-requests` | `listPullRequests` -- Paginated.
`POST /api/v1/branches/{branchId}/pull-requests` | `createPullRequest`
`GET /api/v1/pull-requests/{prId}` | `getPullRequest`
`PUT /api/v1/pull-requests/{prId}` | `updatePullRequest`
`PATCH /api/v1/pull-requests/{prId}` | `patchPullRequest`

---

## Change Requests

`GET /api/v1/change-requests` | `listChangeRequests` -- Filter by `state` (Open, Review, Approved, Rejected).
`POST /api/v1/change-requests` | `createChangeRequest`
`GET /api/v1/change-requests/{ecrId}` | `getChangeRequest`
`PUT /api/v1/change-requests/{ecrId}` | `updateChangeRequest`
`PATCH /api/v1/change-requests/{ecrId}` | `patchChangeRequest`
`DELETE /api/v1/change-requests/{ecrId}` | `deleteChangeRequest`

### Change orders under a request
`GET /api/v1/change-requests/{ecrId}/orders` | `listChangeOrdersForRequest` -- Paginated.
`POST /api/v1/change-requests/{ecrId}/orders` | `createChangeOrder`

---

## Change Orders

`GET /api/v1/change-orders/{ecoId}` | `getChangeOrder`
`PUT /api/v1/change-orders/{ecoId}` | `updateChangeOrder`
`PATCH /api/v1/change-orders/{ecoId}` | `patchChangeOrder`
`DELETE /api/v1/change-orders/{ecoId}` | `deleteChangeOrder`

### Impacts
`GET /api/v1/change-orders/{ecoId}/impacts` | `listChangeImpacts` -- **Not paginated.**
`POST /api/v1/change-orders/{ecoId}/impacts` | `createChangeImpact`
`PUT /api/v1/change-orders/{ecoId}/impacts/{impactId}` | `updateChangeImpact`
`PATCH /api/v1/change-orders/{ecoId}/impacts/{impactId}` | `patchChangeImpact`
`DELETE /api/v1/change-orders/{ecoId}/impacts/{impactId}` | `deleteChangeImpact`

### Approvals
`GET /api/v1/change-orders/{ecoId}/approvals` | `listChangeApprovals` -- **Not paginated.**
`POST /api/v1/change-orders/{ecoId}/approvals` | `createChangeApproval`
`PUT /api/v1/change-orders/{ecoId}/approvals/{approvalId}` | `updateChangeApproval`
`PATCH /api/v1/change-orders/{ecoId}/approvals/{approvalId}` | `patchChangeApproval`

---

## Roles

`GET /api/v1/roles` | `listRoles` -- Paginated. Filter by `include_inactive`.
`POST /api/v1/roles` | `createRole`
`GET /api/v1/roles/{id}` | `getRole`
`PUT /api/v1/roles/{id}` | `updateRole`
`PATCH /api/v1/roles/{id}` | `patchRole`
`DELETE /api/v1/roles/{id}` | `deleteRole` -- Soft-delete. System roles cannot be deleted.

### User role assignments
`GET /api/v1/users/{userId}/roles` | `listUserRoles` -- **Not paginated.**
`POST /api/v1/users/{userId}/roles` | `assignUserRole`
`DELETE /api/v1/users/{userId}/roles/{roleId}` | `removeUserRole`

<details><summary>Example RoleResponse</summary>

```json
{
  "id": 2, "name": "editor", "display_name": "Editor",
  "description": "Can edit all business data; no access to user management or billing",
  "is_system": true, "is_active": true,
  "permissions": ["quote.view", "quote.create", "quote.edit", "product.view", "product.edit"],
  "default_data_scope": "all",
  "created_at": "2026-03-01T10:00:00Z"
}
```
</details>

---

## Permissions

### List all available permissions
`GET /api/v1/permissions` | `listPermissions` -- **Not paginated.**

### Get effective permissions for a user
`GET /api/v1/users/{userId}/permissions` | `getUserPermissions`

### Get caller's own permissions
`GET /api/v1/me/permissions` | `getMyPermissions`

---

## Teams

`GET /api/v1/teams` | `listTeams` -- Paginated. Filter by `include_inactive`.
`POST /api/v1/teams` | `createTeam`
`GET /api/v1/teams/{id}` | `getTeam`
`PUT /api/v1/teams/{id}` | `updateTeam`
`PATCH /api/v1/teams/{id}` | `patchTeam`
`DELETE /api/v1/teams/{id}` | `deleteTeam`

### Members
`POST /api/v1/teams/{id}/members` | `addTeamMember`
`DELETE /api/v1/teams/{id}/members/{userId}` | `removeTeamMember`

---

## Territories

`GET /api/v1/territories` | `listTerritories` -- Paginated. Filter by `include_inactive`.
`POST /api/v1/territories` | `createTerritory`
`GET /api/v1/territories/{id}` | `getTerritory`
`PUT /api/v1/territories/{id}` | `updateTerritory`
`PATCH /api/v1/territories/{id}` | `patchTerritory`
`DELETE /api/v1/territories/{id}` | `deleteTerritory`

### User assignments
`POST /api/v1/territories/{id}/users` | `assignTerritoryUser`
`DELETE /api/v1/territories/{id}/users/{userId}` | `removeTerritoryUser`

---

## Data Access Policies

ABAC policies for row-level data filtering. Policies define subject, resource, and context conditions.

`GET /api/v1/data-access-policies` | `listDataAccessPolicies` -- Paginated. Filter by `resource_type`, `include_inactive`.
`POST /api/v1/data-access-policies` | `createDataAccessPolicy`
`GET /api/v1/data-access-policies/{id}` | `getDataAccessPolicy`
`PUT /api/v1/data-access-policies/{id}` | `updateDataAccessPolicy`
`PATCH /api/v1/data-access-policies/{id}` | `patchDataAccessPolicy`
`DELETE /api/v1/data-access-policies/{id}` | `deleteDataAccessPolicy`

### Assignments
`POST /api/v1/data-access-policies/{id}/assignments` | `createPolicyAssignment` -- Assign to role or user.
`DELETE /api/v1/data-access-policies/{id}/assignments/{assignmentId}` | `deletePolicyAssignment`

<details><summary>Example DataAccessPolicyResponse</summary>

```json
{
  "id": 1, "name": "Editor team access",
  "description": "Editors can see their own and team data",
  "resource_type": "quote", "effect": "allow", "priority": 100,
  "is_active": true,
  "subject_conditions": {
    "match_type": "all",
    "conditions": [
      {"attribute": "role_names", "operator": "contains", "value": "editor"}
    ]
  },
  "resource_conditions": {
    "match_type": "any",
    "conditions": [
      {"attribute": "owner_id", "operator": "eq", "value": "$user.user_id"},
      {"attribute": "owner_id", "operator": "in", "value": "$user.team_member_ids"}
    ]
  },
  "context_conditions": null,
  "assignments": [{"id": 1, "role_id": 2, "user_id": null, "assigned_at": "2026-03-01T10:00:00Z"}]
}
```
</details>

---

## Permission Bundles

`GET /api/v1/permission-bundles` | `listPermissionBundles` -- Paginated.
`POST /api/v1/permission-bundles` | `createPermissionBundle`
`GET /api/v1/permission-bundles/{id}` | `getPermissionBundle`
`PUT /api/v1/permission-bundles/{id}` | `updatePermissionBundle`
`DELETE /api/v1/permission-bundles/{id}` | `deletePermissionBundle` -- System bundles cannot be deleted.

---

## Role Templates

`GET /api/v1/role-templates` | `listRoleTemplates` -- Paginated.
`POST /api/v1/role-templates` | `createRoleTemplate`
`GET /api/v1/role-templates/{id}` | `getRoleTemplate`
`PUT /api/v1/role-templates/{id}` | `updateRoleTemplate`
`DELETE /api/v1/role-templates/{id}` | `deleteRoleTemplate` -- System templates cannot be deleted.

---

## User Attributes

Custom attributes for users, used for ABAC policy evaluation.

`GET /api/v1/users/{id}/attributes` | `listUserAttributes` -- **Not paginated.**
`POST /api/v1/users/{id}/attributes` | `createUserAttribute`
`GET /api/v1/users/{id}/attributes/{attrId}` | `getUserAttribute`
`PUT /api/v1/users/{id}/attributes/{attrId}` | `updateUserAttribute`
`DELETE /api/v1/users/{id}/attributes/{attrId}` | `deleteUserAttribute`

---

## Users

`GET /api/v1/users` | `listUsers` -- Paginated. Filter by `search`, `is_active`.
`GET /api/v1/users/{id}` | `getUser` -- Returns user with role assignments.

---

## Invitations

`GET /api/v1/invitations` | `listInvitations` -- Paginated.
`POST /api/v1/invitations` | `createInvitation` -- Invite by email.
`GET /api/v1/invitations/{id}` | `getInvitation`
`DELETE /api/v1/invitations/{id}` | `deleteInvitation` -- Revoke.

---

## Approval Workflows

### Rules
`GET /api/v1/approval-rules` | `listApprovalRules` -- **Not paginated.** Filter by `entity_type`.
`POST /api/v1/approval-rules` | `createApprovalRule`
`GET /api/v1/approval-rules/{id}` | `getApprovalRule`
`PUT /api/v1/approval-rules/{id}` | `updateApprovalRule`
`PATCH /api/v1/approval-rules/{id}` | `patchApprovalRule`
`DELETE /api/v1/approval-rules/{id}` | `deleteApprovalRule`

<details><summary>Example ApprovalRuleResponse</summary>

```json
{
  "id": 1, "name": "High-value quote approval",
  "description": "Quotes above 50k require manager approval",
  "entity_type": "quote", "is_active": true, "priority": 100,
  "conditions": [{"type": "quote_amount_gte", "value": 50000}],
  "condition_logic": "AND",
  "approval_type": "sequential",
  "approver_config": [{"user_id": 5, "role": "manager"}],
  "escalation_enabled": true, "escalation_timeout_hours": 48
}
```
</details>

### Requests and actions
`GET /api/v1/approvals` | `listApprovalRequests` -- Offset-based pagination (`limit`, `offset`). Filter by `status`, `entity_type`.
`GET /api/v1/approvals/pending` | `listPendingApprovals` -- Approvals pending for current user. **Not paginated.**
`POST /api/v1/approvals/{id}/action` | `actionApprovalRequest` -- Approve, reject, or request changes.

```json
{"action": "approve", "comment": "Looks good, approved."}
```

---

## Analytics

All analytics endpoints require scope `analytics:read`.

### Pipeline snapshots
`GET /api/v1/analytics/pipeline` | `listPipelineSnapshots` -- Paginated. Filter by `from`, `to`.

### Quote analytics
`GET /api/v1/analytics/quotes` | `listQuoteAnalytics` -- Paginated. Filter by `from`, `to`.

### Option selection facts
`GET /api/v1/analytics/option-selections` | `listOptionSelectionFacts` -- Paginated. Filter by `from`, `to`, `product_id`.

### Part usage facts
`GET /api/v1/analytics/part-usage` | `listPartUsageFacts` -- Paginated. Filter by `from`, `to`, `product_id`.

---

## AI Usage

### Get AI token wallet
`GET /api/v1/ai-usage/wallet` | `getAiWallet`

### List AI usage ledger entries
`GET /api/v1/ai-usage/ledger` | `listAiLedger` -- Paginated. Filter by `task_type`, `provider`.

### List AI usage periods
`GET /api/v1/ai-usage/periods` | `listAiUsagePeriods` -- **Not paginated.** Filter by `period_type`.

---

## Resource Tags

`GET /api/v1/resource-tags` | `listResourceTags` -- Paginated. Filter by `resource_type`, `resource_id`, `tag_name`.
`POST /api/v1/resource-tags` | `createResourceTag`
`GET /api/v1/resource-tags/{id}` | `getResourceTag`
`PUT /api/v1/resource-tags/{id}` | `updateResourceTag`
`DELETE /api/v1/resource-tags/{id}` | `deleteResourceTag`

---

## Health

### Health check
`GET /api/v1/health` | `healthCheck`

No authentication required. Returns system health status with database and Redis checks.

```json
{"status": "ok", "version": "1.0.0", "checks": {"database": "ok", "redis": "ok"}}
```

Returns `503` when unhealthy.

---

## Schema Reference

All request/response schemas with example JSON.

<details><summary>ProductResponse</summary>

```json
{
  "id": 42,
  "name": "Premium Window System",
  "description": "Triple-glazed window with configurable frame material and color.",
  "base_price": "1250.00",
  "currency": "EUR",
  "language": "EN",
  "is_active": true,
  "order_index": 0,
  "image_url": "https://cdn.example.com/uploads/42/product_42_1710000000000_abc123.jpg",
  "background_url": "https://cdn.example.com/uploads/42/product_bg_42_1710000000000_def456.jpg",
  "gallery_count": 3,
  "public_token": "pk_abc123def456",
  "integration_metadata": {"erp_id": "PRD-001", "sync_source": "SAP"},
  "catalog_meta": {"filters": {"1": [3, 5]}, "tags": ["triple-glazed", "premium"], "badges": ["featured"], "specs_summary": "Max 2400mm width, U-value 0.7", "sort_priority": 0},
  "options_version": 5,
  "constraints_version": 2,
  "areas_version": 3,
  "parts_version": 1,
  "pricing_version": 4,
  "created_at": "2025-09-15T08:30:00Z",
  "updated_at": "2026-01-20T14:15:00Z",
  "links": {"self": {"href": "/api/v1/products/42"}, "areas": {"href": "/api/v1/areas?product_id=42"}, "gallery": {"href": "/api/v1/products/42/gallery"}, "image": {"href": "/api/v1/products/42/image"}}
}
```
</details>

<details><summary>ProductCreateRequest</summary>

```json
{
  "name": "Premium Window System",
  "description": "Triple-glazed window with configurable frame material and color.",
  "base_price": "1250.00",
  "language": "EN",
  "integration_metadata": {"erp_id": "PRD-001"},
  "catalog_meta": {"filters": {"1": [3]}, "tags": ["triple-glazed"], "badges": ["new"]}
}
```
</details>

<details><summary>ProductUpdateRequest</summary>

```json
{
  "name": "Premium Window System v2",
  "base_price": "1350.00",
  "is_active": true,
  "integration_metadata": {"erp_id": "PRD-001", "sync_source": "SAP"},
  "catalog_meta": {"filters": {"1": [3, 5]}, "tags": ["triple-glazed", "premium"], "badges": ["featured"], "specs_summary": "Max 2400mm width, U-value 0.7", "sort_priority": 0}
}
```
</details>

<details><summary>AreaResponse</summary>

```json
{
  "id": 101,
  "name": "Frame Material",
  "description": "Select the frame material for your window.",
  "price": "0.00",
  "language": "EN",
  "order_index": 0,
  "allow_disable": false,
  "image_url": null,
  "area_group_id": null,
  "created_at": "2025-09-15T08:30:00Z",
  "updated_at": "2026-01-20T14:15:00Z",
  "links": {"self": {"href": "/api/v1/areas/101"}, "option_groups": {"href": "/api/v1/areas/101/groups"}, "image": {"href": "/api/v1/areas/101/image"}, "content": {"href": "/api/v1/areas/101/content"}}
}
```
</details>

<details><summary>GroupResponse</summary>

```json
{
  "id": 201,
  "name": "Wood Type",
  "description": "Choose from our selection of premium woods.",
  "key": "wood_type",
  "is_multi": false,
  "order_index": 0,
  "language": "EN",
  "area_ids": [101, 102],
  "links": {"self": {"href": "/api/v1/groups/201"}, "options": {"href": "/api/v1/groups/201/options"}, "areas": {"href": "/api/v1/groups/201/areas"}}
}
```
</details>

<details><summary>OptionResponse</summary>

```json
{
  "id": 301,
  "name": "Oak",
  "description": "Solid European oak, FSC certified.",
  "price": "85.00",
  "key": "oak",
  "order_index": 0,
  "recommended": true,
  "is_numbered": false,
  "number_min": null, "number_max": null, "number_step": null, "number_unit": "",
  "image_url": "/static/uploads/options/oak-texture.jpg",
  "language": "EN",
  "group_id": 201,
  "price_scalings": {"10": 0.95, "50": 0.90},
  "created_at": "2025-09-15T08:30:00Z",
  "updated_at": "2026-01-20T14:15:00Z",
  "links": {"self": {"href": "/api/v1/options/301"}}
}
```
</details>

<details><summary>CustomerResponse</summary>

```json
{
  "id": 500,
  "customer_id": "CUST-2026-0042",
  "organization": "Acme Windows GmbH",
  "email": "procurement@acme-windows.de",
  "phone": "+49 30 12345678",
  "address_street": "Fensterstr. 12",
  "address_zip": "10115",
  "address_city": "Berlin",
  "address_country": "Germany",
  "integration_metadata": {"crm_id": "SF-ACC-00042", "erp_code": "K10042"},
  "secret_key": "sk_cust_abc123def456",
  "contacts": [
    {"id": 1, "first_name": "Anna", "last_name": "Schmidt", "email": "a.schmidt@acme-windows.de", "phone": "+49 30 12345679", "position": "Procurement Manager"}
  ],
  "links": {"self": {"href": "/api/v1/customers/500"}, "contacts": {"href": "/api/v1/customers/500/contacts"}}
}
```
</details>

<details><summary>ConfigurationResponse</summary>

```json
{
  "id": 800,
  "config_token": "ct_9f8e7d6c5b4a3210",
  "display_code": "CFG-2026-0042",
  "product_id": 42,
  "customer_id": 500,
  "price_list_id": 10,
  "is_finalized": false,
  "configuration_state_hash": "sha256_abc123def456",
  "opportunity_id": 600,
  "integration_metadata": {"external_ref": "EXT-CFG-001"},
  "offer_language": "DE",
  "created_at": "2026-02-01T10:00:00Z",
  "updated_at": "2026-02-15T16:45:00Z",
  "links": {"self": {"href": "/api/v1/configurations/800"}, "product": {"href": "/api/v1/products/42"}}
}
```
</details>

<details><summary>ConfigurationCalculateRequest</summary>

```json
{
  "product_id": 42,
  "selected_options": {"101": [301], "102": [350, 351]},
  "option_amounts": {"350": 3},
  "disabled_areas": [],
  "enabled_areas": [101, 102],
  "price_list_id": 10,
  "validate_config": true
}
```
</details>

<details><summary>OpportunityResponse</summary>

```json
{
  "id": 600,
  "opportunity_number": "OPP-2026-0015",
  "name": "Acme HQ Renovation",
  "stage": "drafting",
  "status": "open",
  "probability": 40,
  "expected_amount": 48500.00,
  "expected_close_date": "2026-06-30",
  "customer_id": 500,
  "customer_name": "Acme Windows GmbH",
  "primary_quote_id": 700,
  "quote_count": 2,
  "integration_metadata": {"crm_deal_id": "DEAL-2026-015"},
  "links": {"self": {"href": "/api/v1/opportunities/600"}, "quotes": {"href": "/api/v1/opportunities/600/quotes"}}
}
```
</details>

<details><summary>QuoteResponse</summary>

```json
{
  "id": 700,
  "quote_number": "QUO-2026-0042",
  "version_number": 1,
  "status": "draft",
  "is_primary": true,
  "opportunity_id": 600,
  "customer_id": 500,
  "currency": "EUR",
  "total_amount": "48500.00",
  "discount_percent": "5.00",
  "final_amount": "54829.25",
  "valid_from": "2026-02-01",
  "valid_until": "2026-04-30",
  "line_item_count": 3,
  "links": {"self": {"href": "/api/v1/quotes/700"}, "line_items": {"href": "/api/v1/quotes/700/line-items"}}
}
```
</details>

<details><summary>QuoteLineItemResponse</summary>

```json
{
  "id": 1001,
  "position": 1,
  "product_id": 42,
  "product_name": "Premium Window System",
  "configuration_code": "CFG-2026-0042",
  "quantity": 12,
  "unit_price": "2485.00",
  "discount_percent": "5.00",
  "line_total": "28329.00",
  "notes": "Ground floor -- east facade",
  "integration_metadata": {"erp_line_id": "ERP-LI-001"}
}
```
</details>

<details><summary>DocumentTemplateResponse</summary>

```json
{
  "id": 20,
  "name": "Standard Offer Template",
  "doc_type": "offer",
  "status": "published",
  "version": 3,
  "is_published": true,
  "product_id": 42,
  "origin_template_id": null,
  "inheritance_mode": "standalone",
  "links": {
    "self": {"href": "/api/v1/documents/templates/20"},
    "structure": {"href": "/api/v1/documents/templates/20/structure"},
    "clone": {"href": "/api/v1/documents/templates/20/clone"},
    "variants": {"href": "/api/v1/documents/templates/20/variants"},
    "translate": {"href": "/api/v1/documents/templates/20/translate"}
  }
}
```
</details>

<details><summary>WebhookSubscriptionResponse</summary>

```json
{
  "id": 5,
  "name": "Quote notifications",
  "url": "https://integrations.acme-windows.de/webhooks/rattleapp",
  "events": ["quote.created", "quote.status_changed"],
  "is_active": true,
  "created_at": "2026-01-05T08:00:00Z",
  "links": {"self": {"href": "/api/v1/webhooks/5"}, "deliveries": {"href": "/api/v1/webhooks/5/deliveries"}}
}
```
</details>

<details><summary>ConnectorResponse</summary>

```json
{
  "id": 8,
  "name": "SAP ERP Connector",
  "connector_type": "generic_http",
  "base_url": "https://sap.acme-windows.de/api",
  "verify_tls": true,
  "settings": {"timeout": 30},
  "auth_type": "basic",
  "has_secret": true,
  "endpoint_count": 3,
  "task_count": 2,
  "links": {"self": {"href": "/api/v1/connectors/8"}, "endpoints": {"href": "/api/v1/connectors/8/endpoints"}}
}
```
</details>

<details><summary>PartResponse</summary>

```json
{
  "id": 1500,
  "part_number": "FRM-OAK-001",
  "part_name": "Oak Frame Profile 80mm",
  "part_cost": 4200,
  "part_type": "manufactured",
  "part_description": "80mm oak frame profile, pre-treated.",
  "make_or_buy": "make",
  "commodity_code": "4418.10",
  "weight": 3.2,
  "weight_unit": "kg",
  "status": "active",
  "custom_fields": {"lead_time_days": 14},
  "integration_metadata": {"erp_part_id": "ERP-P-1500"},
  "links": {"self": {"href": "/api/v1/parts/1500"}, "bom": {"href": "/api/v1/parts/1500/bom"}, "placements": {"href": "/api/v1/parts/1500/placements"}}
}
```
</details>

<details><summary>BomItemResponse</summary>

```json
{
  "id": 70,
  "parent_part_id": 1500,
  "child_part_id": 1501,
  "child_part_number": "RAW-OAK-BLANK",
  "child_part_name": "Oak Blank 100x80x2400mm",
  "quantity": 1.0,
  "uom": "pcs",
  "scrap_percent": 5.0,
  "order_index": 0,
  "alt_group": null,
  "priority": 0,
  "effective_from": "2025-01-01",
  "effective_to": null,
  "note": "Grade A only",
  "usage_subclauses": [{"option_id": 301, "factor": 1.0}],
  "option_scalings": {"301": 1.0},
  "ghost_part": false,
  "part_group_id": null
}
```
</details>

<details><summary>CompanySettingsResponse</summary>

```json
{
  "id": 1,
  "company_name": "Acme Windows GmbH",
  "default_language": "EN",
  "config_code_prefix": "CFG",
  "company_url": "https://acme-windows.rattleapp.de",
  "custom_domain": "configurator.acme-windows.de",
  "custom_domain_verified": true
}
```
</details>

<details><summary>PriceListResponse</summary>

```json
{
  "id": 10,
  "name": "EU Retail 2026",
  "description": "Standard retail pricing for European markets.",
  "order_index": 0,
  "is_base": true,
  "currency": "EUR",
  "created_at": "2025-09-15T08:30:00Z",
  "updated_at": "2026-01-20T14:15:00Z",
  "links": {"self": {"href": "/api/v1/price-lists/10"}}
}
```
</details>

<details><summary>LanguageResponse</summary>

```json
{"id": 1, "code": "EN", "name": "English", "is_base": true, "order_index": 0, "links": {"self": {"href": "/api/v1/languages/1"}}}
```
</details>

<details><summary>AttributeResponse</summary>

```json
{
  "id": 50,
  "name": "U-Value (W/m2K)",
  "attr_type": "range",
  "values": [
    {"id": 1, "product_id": null, "area_id": null, "option_id": 301, "number_value": null, "range_min": 0.7, "range_max": 1.1, "bool_value": null, "text_value": null}
  ],
  "links": {"self": {"href": "/api/v1/attributes/50"}, "values": {"href": "/api/v1/attributes/50/values"}}
}
```
</details>

<details><summary>ApiKeyResponse</summary>

```json
{
  "id": 3,
  "name": "CI/CD Pipeline",
  "key_prefix": "rk_live_abc1",
  "scopes": ["products:read", "products:write", "prices:read"],
  "is_active": true,
  "last_used_at": "2026-02-22T18:45:00Z",
  "expires_at": null,
  "created_at": "2025-11-01T10:00:00Z",
  "links": {"self": {"href": "/api/v1/api-keys/3"}}
}
```
</details>

<details><summary>BaselineResponse</summary>

```json
{
  "id": 30,
  "product_id": 42,
  "name": "v2.1 Release Baseline",
  "note": "Frozen before summer pricing update.",
  "item_count": 47,
  "created_at": "2026-02-01T00:00:00Z",
  "links": {"self": {"href": "/api/v1/baselines/30"}}
}
```
</details>

<details><summary>BranchResponse</summary>

```json
{
  "id": 1, "company_id": 1, "name": "feature/oak-frame-update",
  "description": "Update oak frame pricing and BOM", "state": "open",
  "created_by": 5, "created_at": "2026-02-20T10:00:00Z",
  "links": {"self": {"href": "/api/v1/branches/1"}, "pull_requests": {"href": "/api/v1/branches/1/pull-requests"}}
}
```
</details>

<details><summary>ChangeRequestResponse</summary>

```json
{
  "id": 1, "title": "Replace oak supplier",
  "description": "Switch from Supplier A to Supplier B",
  "state": "Open", "created_by": 5, "order_count": 2
}
```
</details>

<details><summary>ChangeOrderResponse</summary>

```json
{
  "id": 1, "ecr_id": 1, "state": "Draft",
  "note": "Phase 1: Update BOM for oak frames",
  "created_by": 5, "impact_count": 3
}
```
</details>

<details><summary>RoleResponse</summary>

```json
{
  "id": 2, "name": "editor", "display_name": "Editor",
  "description": "Can edit all business data",
  "is_system": true, "is_active": true,
  "permissions": ["quote.view", "quote.create", "quote.edit", "product.view", "product.edit"],
  "default_data_scope": "all"
}
```
</details>

<details><summary>TeamResponse</summary>

```json
{
  "id": 1, "name": "EMEA Sales", "description": "European sales team",
  "is_active": true, "member_count": 5, "members": []
}
```
</details>

<details><summary>TerritoryResponse</summary>

```json
{
  "id": 1, "name": "Europe", "code": "EMEA",
  "description": "Europe, Middle East and Africa",
  "is_active": true, "parent_id": null, "assigned_users": []
}
```
</details>

<details><summary>DataAccessPolicyResponse</summary>

```json
{
  "id": 1, "name": "Editor team access",
  "resource_type": "quote", "effect": "allow", "priority": 100, "is_active": true,
  "subject_conditions": {"match_type": "all", "conditions": [{"attribute": "role_names", "operator": "contains", "value": "editor"}]},
  "resource_conditions": {"match_type": "any", "conditions": [{"attribute": "owner_id", "operator": "eq", "value": "$user.user_id"}]},
  "assignments": [{"id": 1, "role_id": 2, "user_id": null}]
}
```
</details>

<details><summary>ApprovalRuleResponse</summary>

```json
{
  "id": 1, "name": "High-value quote approval",
  "entity_type": "quote", "is_active": true, "priority": 100,
  "conditions": [{"type": "quote_amount_gte", "value": 50000}],
  "approval_type": "sequential",
  "approver_config": [{"user_id": 5, "role": "manager"}],
  "escalation_enabled": true, "escalation_timeout_hours": 48
}
```
</details>

<details><summary>AiWalletResponse</summary>

```json
{"id": 1, "balance": 50000, "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-03-20T12:00:00Z"}
```
</details>

<details><summary>AiLedgerEntryResponse</summary>

```json
{
  "id": 100, "delta": -1200, "balance_after": 48800,
  "task_type": "rewrite", "provider": "openai",
  "input_tokens": 800, "output_tokens": 400,
  "model_used": "gpt-5", "user_cost_usd": "0.024",
  "created_at": "2026-03-20T14:30:00Z"
}
```
</details>

<details><summary>ResourceTagResponse</summary>

```json
{
  "id": 1, "resource_type": "product", "resource_id": 42,
  "tag_name": "category", "tag_value": "premium",
  "created_at": "2026-03-01T10:00:00Z"
}
```
</details>

<details><summary>PermissionBundleResponse</summary>

```json
{
  "id": 1, "name": "cpq_viewer", "display_name": "CPQ Viewer",
  "description": "Read-only access to CPQ resources",
  "permissions": ["quote.view", "opportunity.view", "product.view"],
  "is_system": false
}
```
</details>

<details><summary>RoleTemplateResponse</summary>

```json
{
  "id": 1, "name": "regional_sales_mgr", "display_name": "Regional Sales Manager",
  "description": "Template for regional sales managers",
  "permissions": ["quote.view", "quote.create", "quote.edit", "quote.approve", "opportunity.view", "opportunity.manage"],
  "approval_limits": {"quote_amount": 100000},
  "default_data_scope": "territory", "is_system": false
}
```
</details>

<details><summary>UserAttributeResponse</summary>

```json
{
  "id": 1, "user_id": 42,
  "attribute_name": "department", "attribute_value": "engineering",
  "created_at": "2026-03-01T10:00:00Z", "updated_at": "2026-03-15T09:00:00Z"
}
```
</details>

<details><summary>ProblemDetails (error envelope)</summary>

```json
{
  "type": "/problems/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "The requested resource was not found.",
  "instance": "/api/v1/products/999",
  "request_id": "req_a1b2c3d4e5f6g7h8",
  "errors": [
    {"field": "name", "message": "Field required", "code": "missing"}
  ]
}
```
</details>

<details><summary>PaginationMeta</summary>

```json
{
  "limit": 25,
  "has_next": true,
  "next_cursor": "eyJhZnRlcl9pZCI6MjV9",
  "total_count": 42
}
```
</details>
