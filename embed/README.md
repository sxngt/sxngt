# Embedding the mjlab contributor card elsewhere

The workflow publishes three things to `assets/` every day:

| file | use |
|---|---|
| `mjlab-card-light.svg`, `mjlab-card-dark.svg` | self-contained image (OG image inlined, ~1 MB) |
| `mjlab-card.json` | data only (~500 B) — for native rendering |

Public URLs (jsDelivr caches for ~7 days and sends CORS headers; raw.githubusercontent is uncached but has no CORS for JSON):

```
https://cdn.jsdelivr.net/gh/sxngt/sxngt@main/assets/mjlab-card-light.svg
https://cdn.jsdelivr.net/gh/sxngt/sxngt@main/assets/mjlab-card-dark.svg
https://cdn.jsdelivr.net/gh/sxngt/sxngt@main/assets/mjlab-card.json
```

Purge the CDN cache after a refresh with `https://purge.jsdelivr.net/gh/sxngt/sxngt@main/assets/mjlab-card.json`.

## Blog / plain HTML

```html
<a href="https://github.com/mujocolab/mjlab/pulls?q=is%3Apr+is%3Amerged+author%3Asxngt">
  <img src="https://cdn.jsdelivr.net/gh/sxngt/sxngt@main/assets/mjlab-card-light.svg" alt="mjlab contributor card" width="480">
</a>
```

## React / Next.js (TSX)

Copy `ContributorCard.tsx` into your project.

```tsx
import ContributorCard from "@/components/ContributorCard";

<ContributorCard />                          // fetches the JSON, follows system theme
<ContributorCard theme="light" showImage={false} />   // compact
```

Static (SSR / SSG, no client fetch):

```tsx
const data = await fetch("https://cdn.jsdelivr.net/gh/sxngt/sxngt@main/assets/mjlab-card.json").then(r => r.json());
<ContributorCard data={data} />
```
