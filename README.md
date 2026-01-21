# bball_fanbot

## Overview

This project generates **college basketball matchup analyses** by synthesizing Reddit fan commentary from team-specific subreddits. Given a query such as:

```
Duke vs UNC
```

the system produces a structured breakdown of positional matchups (guards, forwards, centers), explicitly grounding claims in **fan perceptions, narratives, and recurring themes** rather than traditional box-score statistics.

The goal is not to predict outcomes, but to **capture how fans themselves understand strengths, weaknesses, and key battles** heading into a matchup.

---

## Motivation

Pre-game discussion in college basketball is often shaped by:

* Informal scouting reports from fans who watch every game
* Persistent narratives about player development, effort, and fit
* Concerns that do not always show up in statistics (depth, foul trouble, defensive versatility)

This project treats Reddit as a **crowdsourced qualitative scouting resource**, transforming unstructured discussion into a coherent, matchup-focused analysis.

---

## Core Functionality

* Accepts natural-language matchup queries (e.g., `Team A vs Team B`)
* Aggregates Reddit comments from each team’s fanbase
* Extracts player-level opinions, strengths, weaknesses, and concerns
* Organizes insights into **position-by-position matchup narratives**
* Explicitly attributes claims to fan sentiment (e.g., “UNC fans note…”, “Duke fans believe…”)

---

## Example Output

**Query**

```
Duke vs UNC
```

**Response (Excerpt)**

> **Guards: Seth Trimble vs Isaiah Evans**
> UNC fans credit Trimble for his defensive activity and athleticism, while Duke fans believe Evans has made major strides as a scorer, particularly from beyond the three-point line. This matchup may hinge on how effectively Trimble can disrupt Evans’ rhythm.
>
> **Forwards: Caleb Wilson vs Maliq Brown**
> UNC fans praise Wilson’s athleticism and mid-range scoring, but frequently note limitations in ball handling and perimeter shooting. Duke fans consistently describe Brown as an elite defender with strength, length, and versatility, suggesting he could significantly limit Wilson’s offensive impact.
>
> **Centers: Henri Veesar vs Cameron Boozer / Patrick Ngongba**
> UNC fans describe Veesar as a highly skilled finisher who is difficult to contain, even for similarly sized defenders. However, Duke fans often highlight Boozer’s ability to attack the rim and draw fouls, while UNC fans express concern about limited center depth if Veesar encounters foul trouble.

---

## Data Sources

* Reddit comments from team-specific college basketball subreddits
* Focus on discussion threads related to:

  * Games
  * Player performance
  * Rotations and depth
  * Matchup speculation

No proprietary or private data is used.

---

## Analysis Pipeline (High-Level)

1. **Query Parsing**
   Identify the two teams referenced in the user query.

2. **Comment Collection**
   Retrieve recent and relevant Reddit comments associated with each team.

3. **Player & Position Attribution**
   Associate comments with players and positions using name matching and contextual cues.

4. **Sentiment & Theme Extraction**
   Identify recurring opinions (e.g., defense, shooting, foul trouble, athleticism).

5. **Matchup Synthesis**
   Compare fan narratives across teams and generate a balanced, structured response.
