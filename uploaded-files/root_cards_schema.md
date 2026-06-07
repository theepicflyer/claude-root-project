# Root Card Database Schema
 
**File:** `root_cards.json` — 361 cards, all expansions. Top-level object: { game, source, total_cards, cards }. The 361 card objects are in the `cards` array.
 
## Fields
 
| Field | Type | Notes |
|---|---|---|
| `id` | string | e.g. `"ROOT-50"` |
| `numeric_id` | number | Integer ID, use for sorting |
| `name` | string | Card name |
| `text` | string\|null | Rules text; null if not entered in source |
| `image` | string | Leder Card Library asset name |
| `suit` | string\|null | `"Fox"`, `"Rabbit"`, `"Mouse"`, `"Bird"`, `"Frog"`, or null. Source uses both `"Bunny"` and `"Rabbit"` — both normalized to `"Rabbit"` here |
| `deck` | string\|null | `"Standard Deck"`, `"Exiles & Partisans Deck"`, `"Squires & Disciples Deck"`, or null |
| `craftable` | boolean | Has a craft cost |
| `category` | string | See below |
| `expansion` | string | See below |
| `set` | string | Usually mirrors `expansion`; kept for display. 2 known exceptions (ROOT-167, ROOT-170): prefer `expansion` |
| `source_file` | string | Raw source filename |
| `tags` | string[] | Freeform, unnormalized; treat as hints not controlled vocabulary |
 
## category values
 
`ambush` · `dominance` · `craft_card` — deck cards  
`eyrie_leader` · `vagabond_role` · `quest` · `duchy_minister` · `mood` · `homeland_captain` · `homeland_frog` · `mechanical_marquise` · `faction_card` — faction-specific  
`hireling` · `clockwork_trait` · `clockwork_bot` · `clockwork_reference` · `advanced_setup` · `landmark` — supplementary  
`learn_to_play` · `clarification` — reference only
 
## expansion values
 
`Base Game` · `Exiles & Partisans Deck` · `Squires & Disciples Deck` · `Riverfolk Expansion` · `Underworld Expansion` · `Marauders Expansion` · `Homeland Expansion` · `Vagabond Pack` · `Clockwork Expansion` · `Landmarks`
 
## Query examples

```python
import json
data = json.load(open("root_cards.json"))
cards = data["cards"]  # top-level is an envelope — cards live here
fox_crafts = [c for c in cards if c["suit"] == "Fox" and c["craftable"]]
```

```bash
# jq: all Bird suit cards
jq '.cards[] | select(.suit == "Bird")' root_cards.json
```

## Notes
 
- `text: null` is common for role cards, quests, landmarks, and Clockwork cards — text lives in the Law of Root
- ROOT-13 (Faithful Retainer) is the only `faction_card`; it belongs to Keepers in Iron
- Frog suit belongs to the Lilypad Diaspora (Homeland Expansion)

