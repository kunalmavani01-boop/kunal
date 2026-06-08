# Prompt Library Scouting

Date: 2026-06-04

## Why this exists

The current beta library is too compressed.

What we verified in the app today:

- Visible library flows: `9`
- Local prompt templates: `36`
- Open-source prompts bundled right now: `126`
- Open-source prompts over-classified as `General Prompt Repair Pack`: `68`

So the real problem is not only prompt count.
It is:

1. shallow category taxonomy
2. weak reclassification of imported prompts
3. too much fallback into general buckets

## Manager verdict

Do not keep patching the UI on top of a weak taxonomy.

The product needs:

1. better source scouting
2. richer category tree
3. structured ingestion metadata
4. prompt ranking per category
5. later, optional hybrid RAG behind the scenes

## Scouted public sources

### 1. Promptly World
Source: [https://promptlyworld.com/](https://promptlyworld.com/)

Observed positioning:

- `250+ expert prompts`
- `15 categories`

Observed categories and patterns:

- Marketing & Growth
- Software Development
- Design & Visual
- Business & Strategy
- Writing & Content
- Education & Coaching
- HR & People
- Legal & Compliance
- Data & Analytics
- Sales & Negotiation
- Product Management
- AI & Automation
- Personal Productivity
- Social Media & Creator
- Customer Success

Useful takeaway:

- strong business-facing taxonomy
- categories are profession-first, not model-first

### 2. AISnips
Source: [https://aisnips.org/](https://aisnips.org/)

Observed positioning:

- `1355+ curated prompts`

Observed categories and patterns:

- Business
- Coding
- Design
- Education
- Finance
- Food
- Gaming
- Health
- Lifestyle
- Marketing
- Productivity
- Social Media
- Travel
- Writing

Useful takeaway:

- broader consumer + creator taxonomy
- useful for long-tail categories later
- good example of high-volume category browsing

### 3. Prompt Bible
Source: [https://www.promptbible.io/](https://www.promptbible.io/)

Observed positioning:

- `12,732 AI prompts`
- `21 prompt categories`

Observed categories and patterns:

- Coding & Dev
- Marketing & Ads
- Design & Creative
- Business Strategy
- Writing & Copy
- Social Media
- Content Creation
- Productivity
- E-Commerce
- Finance
- SEO & Content
- Customer Support
- Legal & HR
- Real Estate
- Education
- Image Generation
- Sales
- Platform Content
- Prompt Builders
- Content Writing
- Character Generation

Useful takeaway:

- richer operational taxonomy
- separate buckets for SEO, sales, support, ecommerce
- useful for category expansion

### 4. PromptPortal
Sources:

- [https://promptportal.io/](https://promptportal.io/)
- [https://promptportal.io/categories](https://promptportal.io/categories)

Observed positioning:

- prompt discovery by category, model, and keyword

Useful takeaway:

- category-first plus model filters is a sensible long-term pattern
- but for MVP, category-first only is cleaner

### 5. GitHub open-source prompt libraries

Observed candidates:

- [f/awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts)
- [RISE-UNIBAS/prompt-library](https://github.com/RISE-UNIBAS/prompt-library)
- [convertscout/awesome-ai-prompts](https://github.com/convertscout/awesome-ai-prompts)
- [MrXie23/PromptLibrary](https://github.com/MrXie23/PromptLibrary)
- [harish-garg/gemini-cli-prompt-library](https://github.com/harish-garg/gemini-cli-prompt-library)

Useful takeaway:

- GitHub is the best near-term open source source base
- repositories vary a lot in structure and quality
- metadata normalization is required before import

## Recommended MVP category expansion

Current visible category count is too small.

Recommended next visible taxonomy:

1. MVP Building
2. Product Strategy
3. Validation & Research
4. Website & Landing Pages
5. Messaging & Positioning
6. Sales & Outreach
7. Proposals & Client Work
8. Content & SEO
9. Social Media & Creator
10. Study & Learning
11. Research Summaries
12. Coding Help
13. Debugging & Fixes
14. APIs & Architecture
15. Story & Screenplay
16. Character & Scene Writing
17. Productivity & Planning
18. Decision Making
19. Prompt Repair
20. General Use

This is the right next visible level for the app.

## Recommended hidden metadata schema

Each prompt should carry:

- `id`
- `title`
- `summary`
- `prompt_text`
- `source_label`
- `source_url`
- `origin`
- `primary_category`
- `secondary_category`
- `pack`
- `subcategory`
- `domain`
- `interest`
- `keywords`
- `model_fit`
- `prompt_type`
- `token_profile`
- `quality_score`
- `license_note`

## Ingestion strategy

### Phase 1

Do not scrape full libraries blindly.

Collect:

- source metadata
- public category maps
- public sample prompt structures
- prompt titles and short summaries where appropriate
- only reusable prompt text where licensing and exposure make sense

### Phase 2

Normalize imported entries into our schema:

- infer categories
- infer subcategories
- infer pack affinity
- infer model fit
- infer token profile
- de-duplicate by title + body similarity

### Phase 3

Rank per category:

- top 5 default
- expand to 10
- local curated prompts preferred first
- open-source prompts used as enrichment

## Hybrid RAG note

Not for immediate MVP rollout.

But backend should be prepared for:

1. local curated prompt store
2. larger external prompt corpus later
3. metadata filter first
4. retrieval second
5. reranking third

That is the correct hybrid architecture.

## Immediate next engineering work

1. Expand the app taxonomy from `9` flows to the richer structure above
2. Reclassify the current `126` open-source prompts against that taxonomy
3. Reduce the current overuse of `General Prompt Repair Pack`
4. Add source-quality ranking
5. Only then add more repositories

## Alignment check

This document assumes:

- local-first MVP remains the visible product
- hybrid RAG stays backend-ready, not frontend-visible yet
- library stays unified for the user
- prompt source labels matter internally more than visually

