# Public Website Assets

Store public website images here so GitHub Pages can publish them.

Recommended structure:

- `assets/banners/` for hero/header images.
- `assets/backgrounds/` for page background images.
- `assets/icons/` for small symbols or decorative images.

Example CSS usage:

```css
:root {
  --hero-bg: url("assets/banners/kazaalkis-hero.jpg");
  --page-bg: url("assets/backgrounds/parchment.jpg");
}
```

Only put public-safe images here. Do not store private contacts, generated drafts,
Meta credentials, internal planning files, or copyrighted images without permission.
