# Greek Vase & Myth Banner

## Proposed Folder/File Changes

- `src/greek_vase_assets.py`: cache schema, seed assets, license validation, daily selection, WhatsApp caption helper.
- `src/website_publisher.py`: adds `greek_vase_banner` to `public_notifications/latest.json`.
- `index.html`: renders the daily vase banner.
- `styles.css`: responsive ancient-style banner styling with dark overlay.
- `tests/test_kazaalkis.py`: license, selection, payload, and caption tests.
- Runtime cache: `E:\AI\KazaAlkis\data\greek_vase_daily_assets.json`.

## Implementation Plan

1. Maintain a local verified cache of vase assets.
2. Accept only assets with explicit `Public Domain`, `CC0`, or commercial-use Open Access rights.
3. Select one unused asset per date.
4. Mark selected asset with `last_used_date` and `usage_status`.
5. Reset usage cycle only when all verified assets have been used.
6. Include selected asset in website JSON as `greek_vase_banner`.
7. Render image, title, date, description, rights, and source link on the homepage.
8. Use fallback copy when no valid image exists.

## JSON Schema

```json
{
  "id": "string",
  "title": "string",
  "object_type": "string",
  "date": "string",
  "culture": "string",
  "period": "string",
  "museum": "string",
  "source_url": "string",
  "image_url": "string",
  "license": "Public Domain | CC0 | Open Access with commercial reuse allowed",
  "license_verified": true,
  "attribution_required": false,
  "attribution_text": "string",
  "myth_keywords": ["string"],
  "original_description": "string",
  "llm_rephrased_description": "string",
  "last_used_date": "YYYY-MM-DD | null",
  "usage_status": "available | used | rejected | fallback"
}
```

## Daily Scheduler Logic

1. Website publishing calls `WebsitePublisher.publish(date)`.
2. Publisher calls `GreekVaseAssetManager.select_daily_asset(date)`.
3. If today already has an asset, reuse it.
4. Otherwise choose from verified unused assets.
5. If all are used, reset the valid asset pool.
6. Save the selected asset usage to `greek_vase_daily_assets.json`.
7. Write the selected banner into `public_notifications/latest.json`.

## License Validation Logic

An asset is valid only when:

- `license` is one of:
  - `Public Domain`
  - `CC0`
  - `Open Access with commercial reuse allowed`
- `license_verified` is `true`
- `image_url` and `source_url` are present
- `usage_status` is not `rejected`

Rejected:

- Unknown copyright
- Editorial use only
- Non-commercial only
- No derivatives
- Missing rights metadata

## Example Vase Asset Entry

```json
{
  "id": "met-251345",
  "title": "Terracotta hydria (water jar)",
  "object_type": "Hydria",
  "date": "ca. 530-520 BCE",
  "culture": "Greek, Attic",
  "period": "Archaic",
  "museum": "The Metropolitan Museum of Art",
  "source_url": "https://www.metmuseum.org/art/collection/search/251345",
  "image_url": "https://images.metmuseum.org/CRDImages/gr/original/DP115342.jpg",
  "license": "Public Domain",
  "license_verified": true,
  "attribution_required": false,
  "attribution_text": "The Metropolitan Museum of Art, Rogers Fund, 1923",
  "myth_keywords": ["Triton", "sea travel", "water", "heroes"],
  "original_description": "Attic terracotta hydria; Met metadata tags include Triton.",
  "llm_rephrased_description": "A hydria was made for water, so a scene associated with Triton feels especially alive...",
  "last_used_date": "2026-06-03",
  "usage_status": "used"
}
```

## Webpage Banner HTML/CSS/JS

The homepage includes:

- `#vase-banner`
- `#vase-image`
- `#vase-title`
- `#vase-meta`
- `#vase-story-title`
- `#vase-description`
- `#vase-rights`
- `#vase-link`

The JavaScript reads `payload.greek_vase_banner` from `public_notifications/latest.json`.

## WhatsApp Daily Message Format

```text
🏺 Greek Vase & Myth: Terracotta hydria (water jar)
A hydria was made for water, so a scene associated with Triton feels especially alive...
Source: The Metropolitan Museum of Art | Public Domain
Read more: https://www.metmuseum.org/art/collection/search/251345
```

## Testing Checklist

- Valid public-domain assets pass validation.
- Unknown or unsupported licenses fail validation.
- A daily selected vase is reused for the same date.
- Consecutive days do not repeat while unused assets exist.
- `public_notifications/latest.json` includes `greek_vase_banner`.
- Homepage renders image, title, metadata, description, rights, and source link.
- Fallback banner appears if no valid asset is available.
- Mobile layout remains readable.
