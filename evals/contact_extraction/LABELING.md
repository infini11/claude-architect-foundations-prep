# Labeling policy: contact extraction

How to write `expected` in `cases.json`. Always from the point of view of **our company receiving the email**.

## Fields

- `name`, `email`, `company`: the **sender's**, never the recipient's or someone mentioned. `null` when not explicitly stated (no guessing from an email domain).
- `urgent`: `true` only with an explicit deadline or a stated consequence (cancellation, escalation). Angry tone alone is not urgent.

## `intent`

| Value | Meaning |
|---|---|
| `purchase` | commercial opportunity: the sender wants to **buy** from us, or **responds to our request for proposal / tender** |
| `support` | the sender needs help using our products, services or portals (customer or not), without blame |
| `complaint` | unhappy customer: blame, repeated issue, threat |
| `other` | everything else: job applications, unsolicited cold outreach, partnerships, newsletters |

## Tags

`tags[0]` = expected `intent` (used to group scores), `tags[1]` = difficulty (`easy` / `hard`).
