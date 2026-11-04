# aoa-eval report

Gate variant: `current` — **PASS**

> 標註是 agent 的初始標註，尚未經人工複核（見 eval/README.md）。

## Primary metrics: is core? / is leaf?

兩個二元決策（全部標註檔案）：**core recall**＝真的 core 有多少被判成 core（優先，漏判代表敏感檔案走了較鬆的流程）；**leaf precision**＝判成 leaf 的有多少真的是 leaf（優先，誤判代表 AI 在不該放手的檔案上直接改）。core→leaf 必須是 0（gate）。kappa 是次要指標。

| repo | variant | n | **core recall** | core precision | **leaf precision** | leaf recall | **core→leaf** | kappa |
|---|---|---|---|---|---|---|---|---|
| flask | before | 34 | 0.600 (6/10) | 0.500 (6/12) | 0.917 (11/12) | 0.733 (11/15) | 0 | 0.379 |
| flask | hubs-only | 34 | 0.600 (6/10) | 0.600 (6/10) | 0.917 (11/12) | 0.733 (11/15) | 0 | 0.469 |
| flask | catalog-only | 34 | 0.600 (6/10) | 0.500 (6/12) | 0.917 (11/12) | 0.733 (11/15) | 0 | 0.379 |
| flask | all-barrels | 34 | 0.600 (6/10) | 0.600 (6/10) | 0.917 (11/12) | 0.733 (11/15) | 0 | 0.469 |
| flask | 2026.11-3 | 34 | 0.600 (6/10) | 0.600 (6/10) | 0.917 (11/12) | 0.733 (11/15) | 0 | 0.469 |
| flask | **current** | 34 | 0.600 (6/10) | 0.600 (6/10) | 0.917 (11/12) | 0.733 (11/15) | 0 | 0.469 |
| httpx | before | 31 | 0.778 (7/9) | 0.778 (7/9) | 1.000 (8/8) | 0.615 (8/13) | 0 | 0.571 |
| httpx | hubs-only | 31 | 0.778 (7/9) | 0.778 (7/9) | 1.000 (8/8) | 0.615 (8/13) | 0 | 0.571 |
| httpx | catalog-only | 31 | 0.778 (7/9) | 0.778 (7/9) | 1.000 (8/8) | 0.615 (8/13) | 0 | 0.571 |
| httpx | all-barrels | 31 | 0.778 (7/9) | 0.778 (7/9) | 1.000 (8/8) | 0.615 (8/13) | 0 | 0.571 |
| httpx | 2026.11-3 | 31 | 0.778 (7/9) | 0.778 (7/9) | 1.000 (8/8) | 0.615 (8/13) | 0 | 0.571 |
| httpx | **current** | 31 | 0.778 (7/9) | 0.778 (7/9) | 1.000 (8/8) | 0.615 (8/13) | 0 | 0.571 |
| zod | before | 63 | 0.769 (10/13) | 0.476 (10/21) | 0.952 (20/21) | 0.540 (20/37) | 0 | 0.405 |
| zod | hubs-only | 63 | 0.769 (10/13) | 0.476 (10/21) | 0.952 (20/21) | 0.540 (20/37) | 0 | 0.405 |
| zod | catalog-only | 63 | 0.923 (12/13) | 0.522 (12/23) | 0.950 (19/20) | 0.513 (19/37) | 0 | 0.387 |
| zod | all-barrels | 63 | 1.000 (13/13) | 0.542 (13/24) | 0.870 (20/23) | 0.540 (20/37) | 0 | 0.394 |
| zod | 2026.11-3 | 63 | 0.923 (12/13) | 0.522 (12/23) | 0.950 (19/20) | 0.513 (19/37) | 0 | 0.387 |
| zod | **current** | 63 | 0.923 (12/13) | 0.522 (12/23) | 0.950 (19/20) | 0.513 (19/37) | 0 | 0.387 |
| django | before | 75 | 0.889 (16/18) | 0.444 (16/36) | 0.870 (20/23) | 0.769 (20/26) | 0 | 0.459 |
| django | hubs-only | 75 | 0.778 (14/18) | 0.483 (14/29) | 0.870 (20/23) | 0.769 (20/26) | 0 | 0.486 |
| django | catalog-only | 75 | 0.889 (16/18) | 0.444 (16/36) | 0.870 (20/23) | 0.769 (20/26) | 0 | 0.459 |
| django | all-barrels | 75 | 0.778 (14/18) | 0.483 (14/29) | 0.870 (20/23) | 0.769 (20/26) | 0 | 0.486 |
| django | 2026.11-3 | 75 | 0.778 (14/18) | 0.483 (14/29) | 0.870 (20/23) | 0.769 (20/26) | 0 | 0.486 |
| django | **current** | 75 | 0.778 (14/18) | 0.483 (14/29) | 0.870 (20/23) | 0.769 (20/26) | 0 | 0.486 |

Misses on `current`:

- flask core missed (label core, predicted not core): `src/flask/config.py`, `src/flask/ctx.py`, `src/flask/globals.py`, `src/flask/helpers.py`
- flask false leaf (predicted leaf, label not leaf): `src/flask/views.py`
- httpx core missed (label core, predicted not core): `httpx/_models.py`, `httpx/_urlparse.py`
- zod core missed (label core, predicted not core): `packages/zod/src/v4/core/parse.ts`
- zod false leaf (predicted leaf, label not leaf): `packages/zod/src/locales/index.ts`
- django core missed (label core, predicted not core): `django/core/cache/backends/base.py`, `django/db/backends/utils.py`, `django/utils/tree.py`, `django/views/debug.py`
- django false leaf (predicted leaf, label not leaf): `django/contrib/contenttypes/apps.py`, `django/contrib/sitemaps/views.py`, `django/test/client.py`

## Secondary: agreement (kappa) and cost

| repo | variant | n (ranked) | kappa | weighted κ | kappa ranked | core→leaf | under | over | mean cost |
|---|---|---|---|---|---|---|---|---|---|
| flask | before | 34 (24) | 0.379 | 0.522 | 0.056 | 0 | 5 | 9 | 0.765 |
| flask | hubs-only | 34 (24) | 0.469 | 0.574 | 0.196 | 0 | 5 | 7 | 0.706 |
| flask | catalog-only | 34 (24) | 0.379 | 0.522 | 0.056 | 0 | 5 | 9 | 0.765 |
| flask | all-barrels | 34 (24) | 0.469 | 0.574 | 0.196 | 0 | 5 | 7 | 0.706 |
| flask | 2026.11-3 | 34 (24) | 0.469 | 0.574 | 0.196 | 0 | 5 | 7 | 0.706 |
| flask | current | 34 (24) | 0.469 | 0.574 | 0.196 | 0 | 5 | 7 | 0.706 |
| httpx | before | 31 (23) | 0.571 | 0.667 | 0.357 | 0 | 2 | 7 | 0.403 |
| httpx | hubs-only | 31 (23) | 0.571 | 0.667 | 0.357 | 0 | 2 | 7 | 0.403 |
| httpx | catalog-only | 31 (23) | 0.571 | 0.667 | 0.357 | 0 | 2 | 7 | 0.403 |
| httpx | all-barrels | 31 (23) | 0.571 | 0.667 | 0.357 | 0 | 2 | 7 | 0.403 |
| httpx | 2026.11-3 | 31 (23) | 0.571 | 0.667 | 0.357 | 0 | 2 | 7 | 0.403 |
| httpx | current | 31 (23) | 0.571 | 0.667 | 0.357 | 0 | 2 | 7 | 0.403 |
| zod | before | 63 (57) | 0.405 | 0.455 | 0.363 | 0 | 4 | 21 | 0.532 |
| zod | hubs-only | 63 (57) | 0.405 | 0.455 | 0.363 | 0 | 4 | 21 | 0.532 |
| zod | catalog-only | 63 (57) | 0.387 | 0.483 | 0.343 | 0 | 2 | 24 | 0.413 |
| zod | all-barrels | 63 (57) | 0.394 | 0.484 | 0.353 | 0 | 3 | 22 | 0.405 |
| zod | 2026.11-3 | 63 (57) | 0.387 | 0.483 | 0.343 | 0 | 2 | 24 | 0.413 |
| zod | current | 63 (57) | 0.387 | 0.483 | 0.343 | 0 | 2 | 24 | 0.413 |
| django | before | 75 (69) | 0.459 | 0.556 | 0.431 | 0 | 5 | 23 | 0.493 |
| django | hubs-only | 75 (69) | 0.486 | 0.577 | 0.460 | 0 | 7 | 19 | 0.533 |
| django | catalog-only | 75 (69) | 0.459 | 0.556 | 0.431 | 0 | 5 | 23 | 0.493 |
| django | all-barrels | 75 (69) | 0.486 | 0.577 | 0.460 | 0 | 7 | 19 | 0.533 |
| django | 2026.11-3 | 75 (69) | 0.486 | 0.577 | 0.460 | 0 | 7 | 19 | 0.533 |
| django | current | 75 (69) | 0.486 | 0.577 | 0.460 | 0 | 7 | 19 | 0.533 |

## Class counts

| repo | variant | rules | nodes | core | business | leaf | ranked core／business／leaf | high_risk |
|---|---|---|---|---|---|---|---|---|
| flask | before | 2026.11-4 | 83 | 12 | 10 | 61 | 12／10／2 | 11 |
| flask | hubs-only | 2026.11-4 | 83 | 10 | 12 | 61 | 10／12／2 | 7 |
| flask | catalog-only | 2026.11-4 | 83 | 12 | 10 | 61 | 12／10／2 | 11 |
| flask | all-barrels | 2026.11-4 | 83 | 10 | 12 | 61 | 10／12／2 | 7 |
| flask | 2026.11-3 | 2026.11-4 | 83 | 10 | 12 | 61 | 10／12／2 | 7 |
| flask | current | 2026.11-4 | 83 | 10 | 12 | 61 | 10／12／2 | 7 |
| httpx | before | 2026.11-4 | 60 | 9 | 14 | 37 | 9／14／0 | 2 |
| httpx | hubs-only | 2026.11-4 | 60 | 9 | 14 | 37 | 9／14／0 | 2 |
| httpx | catalog-only | 2026.11-4 | 60 | 9 | 14 | 37 | 9／14／0 | 2 |
| httpx | all-barrels | 2026.11-4 | 60 | 9 | 14 | 37 | 9／14／0 | 2 |
| httpx | 2026.11-3 | 2026.11-4 | 60 | 9 | 14 | 37 | 9／14／0 | 2 |
| httpx | current | 2026.11-4 | 60 | 9 | 14 | 37 | 9／14／0 | 2 |
| zod | before | 2026.11-4 | 522 | 26 | 105 | 391 | 26／105／52 | 2 |
| zod | hubs-only | 2026.11-4 | 522 | 26 | 105 | 391 | 26／105／52 | 2 |
| zod | catalog-only | 2026.11-4 | 522 | 32 | 99 | 391 | 32／99／52 | 2 |
| zod | all-barrels | 2026.11-4 | 522 | 31 | 93 | 398 | 31／93／59 | 2 |
| zod | 2026.11-3 | 2026.11-4 | 522 | 32 | 99 | 391 | 32／99／52 | 2 |
| zod | current | 2026.11-4 | 522 | 32 | 99 | 391 | 32／99／52 | 2 |
| django | before | 2026.11-4 | 2984 | 374 | 205 | 2405 | 374／205／356 | 244 |
| django | hubs-only | 2026.11-4 | 2984 | 277 | 302 | 2405 | 277／302／356 | 56 |
| django | catalog-only | 2026.11-4 | 2984 | 374 | 205 | 2405 | 374／205／356 | 244 |
| django | all-barrels | 2026.11-4 | 2984 | 255 | 324 | 2405 | 255／324／356 | 56 |
| django | 2026.11-3 | 2026.11-4 | 2984 | 277 | 302 | 2405 | 277／302／356 | 56 |
| django | current | 2026.11-4 | 2984 | 255 | 324 | 2405 | 255／324／356 | 56 |

## Determinism

| repo | graph identical | nodes identical |
|---|---|---|
| flask | True | True |
| httpx | True | True |
| zod | True | True |
| django | True | True |

## Stability (adjacent first-parent commits)

| repo | variant | commits | class churn | churn on untouched files | labelled files that flipped |
|---|---|---|---|---|---|
| flask | before | 5 | 0.0030 | 0.0031 | 1 |
| flask | hubs-only | 5 | 0.0030 | 0.0031 | 1 |
| flask | catalog-only | 5 | 0.0030 | 0.0031 | 1 |
| flask | all-barrels | 5 | 0.0030 | 0.0031 | 1 |
| flask | 2026.11-3 | 5 | 0.0030 | 0.0031 | 1 |
| flask | current | 5 | 0.0030 | 0.0031 | 1 |
| httpx | before | 5 | 0.0042 | 0.0042 | 1 |
| httpx | hubs-only | 5 | 0.0042 | 0.0042 | 1 |
| httpx | catalog-only | 5 | 0.0042 | 0.0042 | 1 |
| httpx | all-barrels | 5 | 0.0042 | 0.0042 | 1 |
| httpx | 2026.11-3 | 5 | 0.0042 | 0.0042 | 1 |
| httpx | current | 5 | 0.0042 | 0.0042 | 1 |
| zod | before | 5 | 0.0000 | 0.0000 | 0 |
| zod | hubs-only | 5 | 0.0000 | 0.0000 | 0 |
| zod | catalog-only | 5 | 0.0000 | 0.0000 | 0 |
| zod | all-barrels | 5 | 0.0000 | 0.0000 | 0 |
| zod | 2026.11-3 | 5 | 0.0000 | 0.0000 | 0 |
| zod | current | 5 | 0.0000 | 0.0000 | 0 |
| django | before | 5 | 0.0001 | 0.0001 | 0 |
| django | hubs-only | 5 | 0.0003 | 0.0003 | 0 |
| django | catalog-only | 5 | 0.0001 | 0.0001 | 0 |
| django | all-barrels | 5 | 0.0003 | 0.0003 | 0 |
| django | 2026.11-3 | 5 | 0.0003 | 0.0003 | 0 |
| django | current | 5 | 0.0003 | 0.0003 | 0 |

## Historical replay

在較舊的 commit 分類，數之後的 bug-fix commit 改到哪些檔案。lift = 該類被改到的比例 ÷ 全體比例。

| repo | variant | replay commit | bug-fix commits | touched／ranked | core lift | business lift | leaf lift |
|---|---|---|---|---|---|---|---|
| flask | before | `88a65bb374` | 14 | 3／24 | 2.000 | 0.000 | 0.000 |
| flask | hubs-only | `88a65bb374` | 14 | 3／24 | 1.600 | 0.667 | 0.000 |
| flask | catalog-only | `88a65bb374` | 14 | 3／24 | 2.000 | 0.000 | 0.000 |
| flask | all-barrels | `88a65bb374` | 14 | 3／24 | 1.600 | 0.667 | 0.000 |
| flask | 2026.11-3 | `88a65bb374` | 14 | 3／24 | 1.600 | 0.667 | 0.000 |
| flask | current | `88a65bb374` | 14 | 3／24 | 1.600 | 0.667 | 0.000 |
| httpx | before | `e70d0b08c9` | 3 | 2／23 | 2.300 | 0.000 | – |
| httpx | hubs-only | `e70d0b08c9` | 3 | 2／23 | 2.300 | 0.000 | – |
| httpx | catalog-only | `e70d0b08c9` | 3 | 2／23 | 2.300 | 0.000 | – |
| httpx | all-barrels | `e70d0b08c9` | 3 | 2／23 | 2.300 | 0.000 | – |
| httpx | 2026.11-3 | `e70d0b08c9` | 3 | 2／23 | 2.300 | 0.000 | – |
| httpx | current | `e70d0b08c9` | 3 | 2／23 | 2.300 | 0.000 | – |
| zod | before | `8d336c4d15` | 204 | 78／138 | 1.429 | 1.267 | 0.186 |
| zod | hubs-only | `8d336c4d15` | 204 | 78／138 | 1.429 | 1.267 | 0.186 |
| zod | catalog-only | `8d336c4d15` | 204 | 78／138 | 1.429 | 1.171 | 0.483 |
| zod | all-barrels | `8d336c4d15` | 204 | 78／138 | 1.497 | 1.145 | 0.483 |
| zod | 2026.11-3 | `8d336c4d15` | 204 | 78／138 | 1.429 | 1.171 | 0.483 |
| zod | current | `8d336c4d15` | 204 | 78／138 | 1.429 | 1.171 | 0.483 |
| django | before | `05ba1a9228` | 598 | 262／918 | 1.578 | 0.946 | 0.443 |
| django | hubs-only | `05ba1a9228` | 598 | 262／918 | 1.765 | 0.982 | 0.443 |
| django | catalog-only | `05ba1a9228` | 598 | 262／918 | 1.578 | 0.946 | 0.443 |
| django | all-barrels | `05ba1a9228` | 598 | 262／918 | 1.924 | 0.915 | 0.443 |
| django | 2026.11-3 | `05ba1a9228` | 598 | 262／918 | 1.765 | 0.982 | 0.443 |
| django | current | `05ba1a9228` | 598 | 262／918 | 1.924 | 0.915 | 0.443 |

## Per repo

### flask @ `49943b5a94`

**before** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 11 | 3 | 1 | 0.733 |
| business | 1 | 3 | 5 | 0.333 |
| core | 0 | 4 | 6 | 0.600 |
| precision | 0.917 | 0.300 | 0.500 | |

<details><summary>Disagreements (14)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `src/flask/config.py` | core | business | default | 50.0 | 21 |
| `src/flask/ctx.py` | core | business | default | 50.0 | 21 |
| `src/flask/globals.py` | core | business | default | 14.6 | 21 |
| `src/flask/helpers.py` | core | business | default | 77.1 | 21 |
| `src/flask/views.py` | business | leaf | score_low | 2.1 | 0 |
| `src/flask/debughelpers.py` | leaf | core | runtime_cycle | 29.2 | 21 |
| `src/flask/blueprints.py` | business | core | runtime_cycle | 50.0 | 21 |
| `src/flask/cli.py` | business | core | sensitive:crypto, sensitive:secrets, runtime_cycle | 85.4 | 21 |
| `src/flask/sansio/blueprints.py` | business | core | runtime_cycle | 50.0 | 21 |
| `src/flask/templating.py` | business | core | runtime_cycle | 29.2 | 21 |
| `src/flask/testing.py` | business | core | runtime_cycle | 81.2 | 21 |
| `src/flask/logging.py` | leaf | business | default | 29.2 | 21 |
| `src/flask/signals.py` | leaf | business | default | 62.5 | 22 |
| `src/flask/typing.py` | leaf | business | default | 62.5 | 22 |

</details>

**hubs-only** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 11 | 3 | 1 | 0.733 |
| business | 1 | 5 | 3 | 0.556 |
| core | 0 | 4 | 6 | 0.600 |
| precision | 0.917 | 0.417 | 0.600 | |

<details><summary>Disagreements (12)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `src/flask/config.py` | core | business | default | 50.0 | 21 |
| `src/flask/ctx.py` | core | business | default | 50.0 | 21 |
| `src/flask/globals.py` | core | business | default | 14.6 | 21 |
| `src/flask/helpers.py` | core | business | default | 77.1 | 21 |
| `src/flask/views.py` | business | leaf | score_low | 2.1 | 0 |
| `src/flask/debughelpers.py` | leaf | core | runtime_cycle | 29.2 | 21 |
| `src/flask/blueprints.py` | business | core | runtime_cycle | 50.0 | 21 |
| `src/flask/cli.py` | business | core | sensitive:crypto, sensitive:secrets, runtime_cycle | 85.4 | 21 |
| `src/flask/templating.py` | business | core | runtime_cycle | 29.2 | 21 |
| `src/flask/logging.py` | leaf | business | default | 29.2 | 21 |
| `src/flask/signals.py` | leaf | business | default | 62.5 | 22 |
| `src/flask/typing.py` | leaf | business | default | 62.5 | 22 |

</details>

**catalog-only** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 11 | 3 | 1 | 0.733 |
| business | 1 | 3 | 5 | 0.333 |
| core | 0 | 4 | 6 | 0.600 |
| precision | 0.917 | 0.300 | 0.500 | |

<details><summary>Disagreements (14)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `src/flask/config.py` | core | business | default | 50.0 | 21 |
| `src/flask/ctx.py` | core | business | default | 50.0 | 21 |
| `src/flask/globals.py` | core | business | default | 14.6 | 21 |
| `src/flask/helpers.py` | core | business | default | 77.1 | 21 |
| `src/flask/views.py` | business | leaf | score_low | 2.1 | 0 |
| `src/flask/debughelpers.py` | leaf | core | runtime_cycle | 29.2 | 21 |
| `src/flask/blueprints.py` | business | core | runtime_cycle | 50.0 | 21 |
| `src/flask/cli.py` | business | core | sensitive:crypto, sensitive:secrets, runtime_cycle | 85.4 | 21 |
| `src/flask/sansio/blueprints.py` | business | core | runtime_cycle | 50.0 | 21 |
| `src/flask/templating.py` | business | core | runtime_cycle | 29.2 | 21 |
| `src/flask/testing.py` | business | core | runtime_cycle | 81.2 | 21 |
| `src/flask/logging.py` | leaf | business | default | 29.2 | 21 |
| `src/flask/signals.py` | leaf | business | default | 62.5 | 22 |
| `src/flask/typing.py` | leaf | business | default | 62.5 | 22 |

</details>

**all-barrels** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 11 | 3 | 1 | 0.733 |
| business | 1 | 5 | 3 | 0.556 |
| core | 0 | 4 | 6 | 0.600 |
| precision | 0.917 | 0.417 | 0.600 | |

<details><summary>Disagreements (12)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `src/flask/config.py` | core | business | default | 50.0 | 21 |
| `src/flask/ctx.py` | core | business | default | 50.0 | 21 |
| `src/flask/globals.py` | core | business | default | 14.6 | 21 |
| `src/flask/helpers.py` | core | business | default | 77.1 | 21 |
| `src/flask/views.py` | business | leaf | score_low | 2.1 | 0 |
| `src/flask/debughelpers.py` | leaf | core | runtime_cycle | 29.2 | 21 |
| `src/flask/blueprints.py` | business | core | runtime_cycle | 50.0 | 21 |
| `src/flask/cli.py` | business | core | sensitive:crypto, sensitive:secrets, runtime_cycle | 85.4 | 21 |
| `src/flask/templating.py` | business | core | runtime_cycle | 29.2 | 21 |
| `src/flask/logging.py` | leaf | business | default | 29.2 | 21 |
| `src/flask/signals.py` | leaf | business | default | 62.5 | 22 |
| `src/flask/typing.py` | leaf | business | default | 62.5 | 22 |

</details>

**2026.11-3** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 11 | 3 | 1 | 0.733 |
| business | 1 | 5 | 3 | 0.556 |
| core | 0 | 4 | 6 | 0.600 |
| precision | 0.917 | 0.417 | 0.600 | |

<details><summary>Disagreements (12)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `src/flask/config.py` | core | business | default | 50.0 | 21 |
| `src/flask/ctx.py` | core | business | default | 50.0 | 21 |
| `src/flask/globals.py` | core | business | default | 14.6 | 21 |
| `src/flask/helpers.py` | core | business | default | 77.1 | 21 |
| `src/flask/views.py` | business | leaf | score_low | 2.1 | 0 |
| `src/flask/debughelpers.py` | leaf | core | runtime_cycle | 29.2 | 21 |
| `src/flask/blueprints.py` | business | core | runtime_cycle | 50.0 | 21 |
| `src/flask/cli.py` | business | core | sensitive:crypto, sensitive:secrets, runtime_cycle | 85.4 | 21 |
| `src/flask/templating.py` | business | core | runtime_cycle | 29.2 | 21 |
| `src/flask/logging.py` | leaf | business | default | 29.2 | 21 |
| `src/flask/signals.py` | leaf | business | default | 62.5 | 22 |
| `src/flask/typing.py` | leaf | business | default | 62.5 | 22 |

</details>

**current** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 11 | 3 | 1 | 0.733 |
| business | 1 | 5 | 3 | 0.556 |
| core | 0 | 4 | 6 | 0.600 |
| precision | 0.917 | 0.417 | 0.600 | |

<details><summary>Disagreements (12)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `src/flask/config.py` | core | business | default | 50.0 | 21 |
| `src/flask/ctx.py` | core | business | default | 50.0 | 21 |
| `src/flask/globals.py` | core | business | default | 14.6 | 21 |
| `src/flask/helpers.py` | core | business | default | 77.1 | 21 |
| `src/flask/views.py` | business | leaf | score_low | 2.1 | 0 |
| `src/flask/debughelpers.py` | leaf | core | runtime_cycle | 29.2 | 21 |
| `src/flask/blueprints.py` | business | core | runtime_cycle | 50.0 | 21 |
| `src/flask/cli.py` | business | core | sensitive:crypto, sensitive:secrets, runtime_cycle | 85.4 | 21 |
| `src/flask/templating.py` | business | core | runtime_cycle | 29.2 | 21 |
| `src/flask/logging.py` | leaf | business | default | 29.2 | 21 |
| `src/flask/signals.py` | leaf | business | default | 62.5 | 22 |
| `src/flask/typing.py` | leaf | business | default | 62.5 | 22 |

</details>

### httpx @ `b5addb64f0`

**before** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 8 | 5 | 0 | 0.615 |
| business | 0 | 7 | 2 | 0.778 |
| core | 0 | 2 | 7 | 0.778 |
| precision | 1.000 | 0.500 | 0.778 | |

<details><summary>Disagreements (9)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `httpx/_models.py` | core | business | default | 69.6 | 20 |
| `httpx/_urlparse.py` | core | business | default | 52.2 | 20 |
| `httpx/_api.py` | business | core | sensitive:crypto, sensitive:public_api | 15.2 | 5 |
| `httpx/_utils.py` | business | core | runtime_cycle | 52.2 | 20 |
| `httpx/__version__.py` | leaf | business | default | 34.8 | 6 |
| `httpx/_main.py` | leaf | business | default | 15.2 | 5 |
| `httpx/_transports/__init__.py` | leaf | business | default | 15.2 | 5 |
| `httpx/_transports/mock.py` | leaf | business | default | 34.8 | 6 |
| `httpx/_types.py` | leaf | business | default | 69.6 | 20 |

</details>

**hubs-only** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 8 | 5 | 0 | 0.615 |
| business | 0 | 7 | 2 | 0.778 |
| core | 0 | 2 | 7 | 0.778 |
| precision | 1.000 | 0.500 | 0.778 | |

<details><summary>Disagreements (9)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `httpx/_models.py` | core | business | default | 69.6 | 20 |
| `httpx/_urlparse.py` | core | business | default | 52.2 | 20 |
| `httpx/_api.py` | business | core | sensitive:crypto, sensitive:public_api | 15.2 | 5 |
| `httpx/_utils.py` | business | core | runtime_cycle | 52.2 | 20 |
| `httpx/__version__.py` | leaf | business | default | 34.8 | 6 |
| `httpx/_main.py` | leaf | business | default | 15.2 | 5 |
| `httpx/_transports/__init__.py` | leaf | business | default | 15.2 | 5 |
| `httpx/_transports/mock.py` | leaf | business | default | 34.8 | 6 |
| `httpx/_types.py` | leaf | business | default | 69.6 | 20 |

</details>

**catalog-only** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 8 | 5 | 0 | 0.615 |
| business | 0 | 7 | 2 | 0.778 |
| core | 0 | 2 | 7 | 0.778 |
| precision | 1.000 | 0.500 | 0.778 | |

<details><summary>Disagreements (9)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `httpx/_models.py` | core | business | default | 69.6 | 20 |
| `httpx/_urlparse.py` | core | business | default | 52.2 | 20 |
| `httpx/_api.py` | business | core | sensitive:crypto, sensitive:public_api | 15.2 | 5 |
| `httpx/_utils.py` | business | core | runtime_cycle | 52.2 | 20 |
| `httpx/__version__.py` | leaf | business | default | 34.8 | 6 |
| `httpx/_main.py` | leaf | business | default | 15.2 | 5 |
| `httpx/_transports/__init__.py` | leaf | business | default | 15.2 | 5 |
| `httpx/_transports/mock.py` | leaf | business | default | 34.8 | 6 |
| `httpx/_types.py` | leaf | business | default | 69.6 | 20 |

</details>

**all-barrels** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 8 | 5 | 0 | 0.615 |
| business | 0 | 7 | 2 | 0.778 |
| core | 0 | 2 | 7 | 0.778 |
| precision | 1.000 | 0.500 | 0.778 | |

<details><summary>Disagreements (9)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `httpx/_models.py` | core | business | default | 69.6 | 20 |
| `httpx/_urlparse.py` | core | business | default | 52.2 | 20 |
| `httpx/_api.py` | business | core | sensitive:crypto, sensitive:public_api | 15.2 | 5 |
| `httpx/_utils.py` | business | core | runtime_cycle | 52.2 | 20 |
| `httpx/__version__.py` | leaf | business | default | 34.8 | 6 |
| `httpx/_main.py` | leaf | business | default | 15.2 | 5 |
| `httpx/_transports/__init__.py` | leaf | business | default | 15.2 | 5 |
| `httpx/_transports/mock.py` | leaf | business | default | 34.8 | 6 |
| `httpx/_types.py` | leaf | business | default | 69.6 | 20 |

</details>

**2026.11-3** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 8 | 5 | 0 | 0.615 |
| business | 0 | 7 | 2 | 0.778 |
| core | 0 | 2 | 7 | 0.778 |
| precision | 1.000 | 0.500 | 0.778 | |

<details><summary>Disagreements (9)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `httpx/_models.py` | core | business | default | 69.6 | 20 |
| `httpx/_urlparse.py` | core | business | default | 52.2 | 20 |
| `httpx/_api.py` | business | core | sensitive:crypto, sensitive:public_api | 15.2 | 5 |
| `httpx/_utils.py` | business | core | runtime_cycle | 52.2 | 20 |
| `httpx/__version__.py` | leaf | business | default | 34.8 | 6 |
| `httpx/_main.py` | leaf | business | default | 15.2 | 5 |
| `httpx/_transports/__init__.py` | leaf | business | default | 15.2 | 5 |
| `httpx/_transports/mock.py` | leaf | business | default | 34.8 | 6 |
| `httpx/_types.py` | leaf | business | default | 69.6 | 20 |

</details>

**current** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 8 | 5 | 0 | 0.615 |
| business | 0 | 7 | 2 | 0.778 |
| core | 0 | 2 | 7 | 0.778 |
| precision | 1.000 | 0.500 | 0.778 | |

<details><summary>Disagreements (9)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `httpx/_models.py` | core | business | default | 69.6 | 20 |
| `httpx/_urlparse.py` | core | business | default | 52.2 | 20 |
| `httpx/_api.py` | business | core | sensitive:crypto, sensitive:public_api | 15.2 | 5 |
| `httpx/_utils.py` | business | core | runtime_cycle | 52.2 | 20 |
| `httpx/__version__.py` | leaf | business | default | 34.8 | 6 |
| `httpx/_main.py` | leaf | business | default | 15.2 | 5 |
| `httpx/_transports/__init__.py` | leaf | business | default | 15.2 | 5 |
| `httpx/_transports/mock.py` | leaf | business | default | 34.8 | 6 |
| `httpx/_types.py` | leaf | business | default | 69.6 | 20 |

</details>

### zod @ `2554b70c3d`

**before** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 20 | 10 | 7 | 0.540 |
| business | 1 | 8 | 4 | 0.615 |
| core | 0 | 3 | 10 | 0.769 |
| precision | 0.952 | 0.381 | 0.476 | |

<details><summary>Disagreements (25)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `packages/zod/src/v3/types.ts` | core | business | default | 55.5 | 10 |
| `packages/zod/src/v4/classic/external.ts` | core | business | default | 54.9 | 20 |
| `packages/zod/src/v4/core/parse.ts` | core | business | default | 53.3 | 134 |
| `packages/zod/src/locales/index.ts` | business | leaf | score_low | 1.9 | 1 |
| `packages/resolution/src/index.cts` | leaf | core | sensitive:public_api | 43.4 | 0 |
| `packages/resolution/src/index.ts` | leaf | core | sensitive:public_api | 42.1 | 0 |
| `packages/zod/src/v4/locales/da.ts` | leaf | core | score_top | 91.0 | 134 |
| `packages/zod/src/v4/locales/fr.ts` | leaf | core | score_boundary | 89.3 | 134 |
| `packages/zod/src/v4/locales/lt.ts` | leaf | core | score_top | 91.0 | 134 |
| `packages/zod/src/v4/locales/nn.ts` | leaf | core | score_top | 94.0 | 134 |
| `packages/zod/src/v4/locales/no.ts` | leaf | core | score_top | 91.0 | 134 |
| `packages/mini/src/index.ts` | business | core | sensitive:public_api | 40.2 | 5 |
| `packages/zod/src/v4/core/memoizer.ts` | business | core | score_top | 96.5 | 134 |
| `packages/zod/src/v4/core/to-json-schema.ts` | business | core | score_top | 97.5 | 134 |
| `packages/zod/src/v4/locales/en.ts` | business | core | score_top | 94.0 | 134 |
| `packages/zod/src/v4/core/versions.ts` | leaf | business | default | 57.1 | 136 |
| `packages/zod/src/v4/locales/ca.ts` | leaf | business | default | 78.1 | 134 |
| `packages/zod/src/v4/locales/ckb.ts` | leaf | business | default | 78.1 | 134 |
| `packages/zod/src/v4/locales/eo.ts` | leaf | business | default | 78.1 | 134 |
| `packages/zod/src/v4/locales/it.ts` | leaf | business | default | 78.1 | 134 |
| `packages/zod/src/v4/locales/ja.ts` | leaf | business | default | 78.1 | 134 |
| `packages/zod/src/v4/locales/km.ts` | leaf | business | default | 78.1 | 134 |
| `packages/zod/src/v4/locales/ro.ts` | leaf | business | default | 63.1 | 134 |
| `packages/zod/src/v4/mini/deep-partial.ts` | leaf | business | default | 45.6 | 17 |
| `scripts/compile-fuzz.ts` | leaf | business | default | 35.8 | 0 |

</details>

**hubs-only** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 20 | 10 | 7 | 0.540 |
| business | 1 | 8 | 4 | 0.615 |
| core | 0 | 3 | 10 | 0.769 |
| precision | 0.952 | 0.381 | 0.476 | |

<details><summary>Disagreements (25)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `packages/zod/src/v3/types.ts` | core | business | default | 55.5 | 10 |
| `packages/zod/src/v4/classic/external.ts` | core | business | default | 54.9 | 20 |
| `packages/zod/src/v4/core/parse.ts` | core | business | default | 53.3 | 134 |
| `packages/zod/src/locales/index.ts` | business | leaf | score_low | 1.9 | 1 |
| `packages/resolution/src/index.cts` | leaf | core | sensitive:public_api | 43.4 | 0 |
| `packages/resolution/src/index.ts` | leaf | core | sensitive:public_api | 42.1 | 0 |
| `packages/zod/src/v4/locales/da.ts` | leaf | core | score_top | 91.0 | 134 |
| `packages/zod/src/v4/locales/fr.ts` | leaf | core | score_boundary | 89.3 | 134 |
| `packages/zod/src/v4/locales/lt.ts` | leaf | core | score_top | 91.0 | 134 |
| `packages/zod/src/v4/locales/nn.ts` | leaf | core | score_top | 94.0 | 134 |
| `packages/zod/src/v4/locales/no.ts` | leaf | core | score_top | 91.0 | 134 |
| `packages/mini/src/index.ts` | business | core | sensitive:public_api | 40.2 | 5 |
| `packages/zod/src/v4/core/memoizer.ts` | business | core | score_top | 96.5 | 134 |
| `packages/zod/src/v4/core/to-json-schema.ts` | business | core | score_top | 97.5 | 134 |
| `packages/zod/src/v4/locales/en.ts` | business | core | score_top | 94.0 | 134 |
| `packages/zod/src/v4/core/versions.ts` | leaf | business | default | 57.1 | 136 |
| `packages/zod/src/v4/locales/ca.ts` | leaf | business | default | 78.1 | 134 |
| `packages/zod/src/v4/locales/ckb.ts` | leaf | business | default | 78.1 | 134 |
| `packages/zod/src/v4/locales/eo.ts` | leaf | business | default | 78.1 | 134 |
| `packages/zod/src/v4/locales/it.ts` | leaf | business | default | 78.1 | 134 |
| `packages/zod/src/v4/locales/ja.ts` | leaf | business | default | 78.1 | 134 |
| `packages/zod/src/v4/locales/km.ts` | leaf | business | default | 78.1 | 134 |
| `packages/zod/src/v4/locales/ro.ts` | leaf | business | default | 63.1 | 134 |
| `packages/zod/src/v4/mini/deep-partial.ts` | leaf | business | default | 45.6 | 17 |
| `scripts/compile-fuzz.ts` | leaf | business | default | 35.8 | 0 |

</details>

**catalog-only** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 19 | 13 | 5 | 0.513 |
| business | 1 | 6 | 6 | 0.462 |
| core | 0 | 1 | 12 | 0.923 |
| precision | 0.950 | 0.300 | 0.522 | |

<details><summary>Disagreements (26)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `packages/zod/src/v4/core/parse.ts` | core | business | default | 84.4 | 132 |
| `packages/zod/src/locales/index.ts` | business | leaf | score_low | 1.9 | 1 |
| `packages/resolution/src/index.cts` | leaf | core | sensitive:public_api | 48.4 | 0 |
| `packages/resolution/src/index.ts` | leaf | core | sensitive:public_api | 45.4 | 0 |
| `packages/zod/src/v4/core/versions.ts` | leaf | core | score_boundary | 88.8 | 134 |
| `packages/zod/src/v4/locales/fr.ts` | leaf | core | score_boundary | 88.2 | 2 |
| `packages/zod/src/v4/locales/km.ts` | leaf | core | score_top | 90.7 | 1 |
| `packages/mini/src/index.ts` | business | core | sensitive:public_api | 43.4 | 5 |
| `packages/zod/src/v4/core/doc.ts` | business | core | score_boundary | 89.9 | 133 |
| `packages/zod/src/v4/core/memoizer.ts` | business | core | score_top | 96.5 | 132 |
| `packages/zod/src/v4/core/to-json-schema.ts` | business | core | score_top | 97.5 | 132 |
| `packages/zod/src/v4/locales/en.ts` | business | core | score_top | 92.6 | 28 |
| `packages/zod/src/v4/locales/index.ts` | business | core | score_boundary | 87.2 | 134 |
| `packages/tsc/generate.ts` | leaf | business | default | 36.1 | 1 |
| `packages/zod/src/v4/locales/ca.ts` | leaf | business | default | 68.3 | 0 |
| `packages/zod/src/v4/locales/ckb.ts` | leaf | business | default | 68.3 | 0 |
| `packages/zod/src/v4/locales/da.ts` | leaf | business | default | 80.6 | 0 |
| `packages/zod/src/v4/locales/eo.ts` | leaf | business | default | 68.3 | 0 |
| `packages/zod/src/v4/locales/it.ts` | leaf | business | default | 68.3 | 0 |
| `packages/zod/src/v4/locales/ja.ts` | leaf | business | default | 68.3 | 0 |
| `packages/zod/src/v4/locales/lt.ts` | leaf | business | default | 80.6 | 0 |
| `packages/zod/src/v4/locales/nn.ts` | leaf | business | default | 83.3 | 0 |
| `packages/zod/src/v4/locales/no.ts` | leaf | business | default | 80.6 | 0 |
| `packages/zod/src/v4/locales/ro.ts` | leaf | business | default | 53.8 | 0 |
| `packages/zod/src/v4/mini/deep-partial.ts` | leaf | business | default | 50.5 | 17 |
| `scripts/compile-fuzz.ts` | leaf | business | default | 36.9 | 0 |

</details>

**all-barrels** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 20 | 11 | 6 | 0.540 |
| business | 3 | 5 | 5 | 0.385 |
| core | 0 | 0 | 13 | 1.000 |
| precision | 0.870 | 0.312 | 0.542 | |

<details><summary>Disagreements (25)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `packages/zod/src/locales/index.ts` | business | leaf | score_low | 2.5 | 1 |
| `packages/zod/src/v4/classic/coerce.ts` | business | leaf | score_low | 13.9 | 0 |
| `packages/zod/src/v4/mini/coerce.ts` | business | leaf | score_low | 13.9 | 0 |
| `packages/resolution/src/index.cts` | leaf | core | sensitive:public_api | 49.2 | 0 |
| `packages/resolution/src/index.ts` | leaf | core | sensitive:public_api | 45.9 | 0 |
| `packages/zod/src/v4/core/versions.ts` | leaf | core | score_top | 90.4 | 130 |
| `packages/zod/src/v4/locales/fr.ts` | leaf | core | score_boundary | 89.9 | 2 |
| `packages/zod/src/v4/locales/km.ts` | leaf | core | score_top | 92.9 | 1 |
| `packages/zod/src/v4/locales/nn.ts` | leaf | core | score_boundary | 86.1 | 0 |
| `packages/mini/src/index.ts` | business | core | sensitive:public_api | 44.5 | 5 |
| `packages/zod/src/v4/core/doc.ts` | business | core | score_top | 91.5 | 129 |
| `packages/zod/src/v4/core/memoizer.ts` | business | core | score_top | 94.3 | 3 |
| `packages/zod/src/v4/core/to-json-schema.ts` | business | core | score_top | 97.0 | 128 |
| `packages/zod/src/v4/locales/en.ts` | business | core | score_top | 95.4 | 7 |
| `packages/tsc/generate.ts` | leaf | business | default | 36.9 | 1 |
| `packages/zod/src/v4/locales/ca.ts` | leaf | business | default | 71.6 | 0 |
| `packages/zod/src/v4/locales/ckb.ts` | leaf | business | default | 71.6 | 0 |
| `packages/zod/src/v4/locales/da.ts` | leaf | business | default | 84.4 | 0 |
| `packages/zod/src/v4/locales/eo.ts` | leaf | business | default | 71.6 | 0 |
| `packages/zod/src/v4/locales/it.ts` | leaf | business | default | 71.6 | 0 |
| `packages/zod/src/v4/locales/ja.ts` | leaf | business | default | 71.6 | 0 |
| `packages/zod/src/v4/locales/lt.ts` | leaf | business | default | 84.4 | 0 |
| `packages/zod/src/v4/locales/no.ts` | leaf | business | default | 84.4 | 0 |
| `packages/zod/src/v4/locales/ro.ts` | leaf | business | default | 55.5 | 0 |
| `scripts/compile-fuzz.ts` | leaf | business | default | 38.0 | 0 |

</details>

**2026.11-3** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 19 | 13 | 5 | 0.513 |
| business | 1 | 6 | 6 | 0.462 |
| core | 0 | 1 | 12 | 0.923 |
| precision | 0.950 | 0.300 | 0.522 | |

<details><summary>Disagreements (26)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `packages/zod/src/v4/core/parse.ts` | core | business | default | 84.4 | 132 |
| `packages/zod/src/locales/index.ts` | business | leaf | score_low | 1.9 | 1 |
| `packages/resolution/src/index.cts` | leaf | core | sensitive:public_api | 48.4 | 0 |
| `packages/resolution/src/index.ts` | leaf | core | sensitive:public_api | 45.4 | 0 |
| `packages/zod/src/v4/core/versions.ts` | leaf | core | score_boundary | 88.8 | 134 |
| `packages/zod/src/v4/locales/fr.ts` | leaf | core | score_boundary | 88.2 | 2 |
| `packages/zod/src/v4/locales/km.ts` | leaf | core | score_top | 90.7 | 1 |
| `packages/mini/src/index.ts` | business | core | sensitive:public_api | 43.4 | 5 |
| `packages/zod/src/v4/core/doc.ts` | business | core | score_boundary | 89.9 | 133 |
| `packages/zod/src/v4/core/memoizer.ts` | business | core | score_top | 96.5 | 132 |
| `packages/zod/src/v4/core/to-json-schema.ts` | business | core | score_top | 97.5 | 132 |
| `packages/zod/src/v4/locales/en.ts` | business | core | score_top | 92.6 | 28 |
| `packages/zod/src/v4/locales/index.ts` | business | core | score_boundary | 87.2 | 134 |
| `packages/tsc/generate.ts` | leaf | business | default | 36.1 | 1 |
| `packages/zod/src/v4/locales/ca.ts` | leaf | business | default | 68.3 | 0 |
| `packages/zod/src/v4/locales/ckb.ts` | leaf | business | default | 68.3 | 0 |
| `packages/zod/src/v4/locales/da.ts` | leaf | business | default | 80.6 | 0 |
| `packages/zod/src/v4/locales/eo.ts` | leaf | business | default | 68.3 | 0 |
| `packages/zod/src/v4/locales/it.ts` | leaf | business | default | 68.3 | 0 |
| `packages/zod/src/v4/locales/ja.ts` | leaf | business | default | 68.3 | 0 |
| `packages/zod/src/v4/locales/lt.ts` | leaf | business | default | 80.6 | 0 |
| `packages/zod/src/v4/locales/nn.ts` | leaf | business | default | 83.3 | 0 |
| `packages/zod/src/v4/locales/no.ts` | leaf | business | default | 80.6 | 0 |
| `packages/zod/src/v4/locales/ro.ts` | leaf | business | default | 53.8 | 0 |
| `packages/zod/src/v4/mini/deep-partial.ts` | leaf | business | default | 50.5 | 17 |
| `scripts/compile-fuzz.ts` | leaf | business | default | 36.9 | 0 |

</details>

**current** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 19 | 13 | 5 | 0.513 |
| business | 1 | 6 | 6 | 0.462 |
| core | 0 | 1 | 12 | 0.923 |
| precision | 0.950 | 0.300 | 0.522 | |

<details><summary>Disagreements (26)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `packages/zod/src/v4/core/parse.ts` | core | business | default | 84.4 | 132 |
| `packages/zod/src/locales/index.ts` | business | leaf | score_low | 1.9 | 1 |
| `packages/resolution/src/index.cts` | leaf | core | sensitive:public_api | 48.4 | 0 |
| `packages/resolution/src/index.ts` | leaf | core | sensitive:public_api | 45.4 | 0 |
| `packages/zod/src/v4/core/versions.ts` | leaf | core | score_boundary | 88.8 | 134 |
| `packages/zod/src/v4/locales/fr.ts` | leaf | core | score_boundary | 88.2 | 2 |
| `packages/zod/src/v4/locales/km.ts` | leaf | core | score_top | 90.7 | 1 |
| `packages/mini/src/index.ts` | business | core | sensitive:public_api | 43.4 | 5 |
| `packages/zod/src/v4/core/doc.ts` | business | core | score_boundary | 89.9 | 133 |
| `packages/zod/src/v4/core/memoizer.ts` | business | core | score_top | 96.5 | 132 |
| `packages/zod/src/v4/core/to-json-schema.ts` | business | core | score_top | 97.5 | 132 |
| `packages/zod/src/v4/locales/en.ts` | business | core | score_top | 92.6 | 28 |
| `packages/zod/src/v4/locales/index.ts` | business | core | score_boundary | 87.2 | 134 |
| `packages/tsc/generate.ts` | leaf | business | default | 36.1 | 1 |
| `packages/zod/src/v4/locales/ca.ts` | leaf | business | default | 68.3 | 0 |
| `packages/zod/src/v4/locales/ckb.ts` | leaf | business | default | 68.3 | 0 |
| `packages/zod/src/v4/locales/da.ts` | leaf | business | default | 80.6 | 0 |
| `packages/zod/src/v4/locales/eo.ts` | leaf | business | default | 68.3 | 0 |
| `packages/zod/src/v4/locales/it.ts` | leaf | business | default | 68.3 | 0 |
| `packages/zod/src/v4/locales/ja.ts` | leaf | business | default | 68.3 | 0 |
| `packages/zod/src/v4/locales/lt.ts` | leaf | business | default | 80.6 | 0 |
| `packages/zod/src/v4/locales/nn.ts` | leaf | business | default | 83.3 | 0 |
| `packages/zod/src/v4/locales/no.ts` | leaf | business | default | 80.6 | 0 |
| `packages/zod/src/v4/locales/ro.ts` | leaf | business | default | 53.8 | 0 |
| `packages/zod/src/v4/mini/deep-partial.ts` | leaf | business | default | 50.5 | 17 |
| `scripts/compile-fuzz.ts` | leaf | business | default | 36.9 | 0 |

</details>

### django @ `308b6d6ac0`

**before** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 20 | 3 | 3 | 0.769 |
| business | 3 | 11 | 17 | 0.355 |
| core | 0 | 2 | 16 | 0.889 |
| precision | 0.870 | 0.688 | 0.444 | |

<details><summary>Disagreements (28)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `django/utils/tree.py` | core | business | default | 75.7 | 602 |
| `django/views/debug.py` | core | business | default | 69.5 | 13 |
| `django/contrib/contenttypes/apps.py` | business | leaf | score_low | 29.1 | 0 |
| `django/contrib/sitemaps/views.py` | business | leaf | score_low | 0.3 | 0 |
| `django/test/client.py` | business | leaf | test_file | – | 2 |
| `django/contrib/admin/decorators.py` | leaf | core | runtime_cycle | 86.3 | 25 |
| `django/contrib/gis/db/backends/postgis/models.py` | leaf | core | sensitive:db_schema | 56.9 | 2 |
| `django/urls/exceptions.py` | leaf | core | runtime_cycle | 81.3 | 601 |
| `django/contrib/admin/filters.py` | business | core | runtime_cycle | 58.3 | 25 |
| `django/contrib/admin/helpers.py` | business | core | runtime_cycle | 58.0 | 25 |
| `django/contrib/admin/views/main.py` | business | core | runtime_cycle | 87.9 | 25 |
| `django/contrib/flatpages/views.py` | business | core | runtime_cycle | 53.7 | 6 |
| `django/contrib/gis/forms/fields.py` | business | core | score_top | 90.6 | 32 |
| `django/contrib/gis/gdal/raster/source.py` | business | core | score_top | 99.2 | 63 |
| `django/contrib/gis/geos/point.py` | business | core | runtime_cycle | 78.1 | 62 |
| `django/contrib/gis/geos/prepared.py` | business | core | runtime_cycle | 78.1 | 62 |
| `django/contrib/postgres/fields/hstore.py` | business | core | runtime_cycle | 55.4 | 10 |
| `django/contrib/postgres/search.py` | business | core | runtime_cycle | 48.7 | 10 |
| `django/core/checks/__init__.py` | business | core | runtime_cycle | 85.0 | 601 |
| `django/core/mail/handler.py` | business | core | runtime_cycle | 96.1 | 601 |
| `django/db/backends/sqlite3/operations.py` | business | core | runtime_cycle | 94.8 | 6 |
| `django/tasks/base.py` | business | core | runtime_cycle | 76.8 | 6 |
| `django/utils/ipv6.py` | business | core | runtime_cycle | 70.8 | 601 |
| `django/utils/module_loading.py` | business | core | runtime_cycle | 94.2 | 601 |
| `django/utils/regex_helper.py` | business | core | runtime_cycle | 89.1 | 601 |
| `django/contrib/postgres/utils.py` | leaf | business | default | 64.9 | 14 |
| `django/core/management/color.py` | leaf | business | default | 61.8 | 602 |
| `scripts/tests.py` | leaf | business | default | 57.9 | 0 |

</details>

**hubs-only** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 20 | 4 | 2 | 0.769 |
| business | 3 | 15 | 13 | 0.484 |
| core | 0 | 4 | 14 | 0.778 |
| precision | 0.870 | 0.652 | 0.483 | |

<details><summary>Disagreements (26)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `django/core/cache/backends/base.py` | core | business | default | 70.8 | 601 |
| `django/db/backends/utils.py` | core | business | default | 63.3 | 601 |
| `django/utils/tree.py` | core | business | default | 75.7 | 602 |
| `django/views/debug.py` | core | business | default | 69.5 | 13 |
| `django/contrib/contenttypes/apps.py` | business | leaf | score_low | 29.1 | 0 |
| `django/contrib/sitemaps/views.py` | business | leaf | score_low | 0.3 | 0 |
| `django/test/client.py` | business | leaf | test_file | – | 2 |
| `django/contrib/admin/decorators.py` | leaf | core | runtime_cycle | 86.3 | 25 |
| `django/contrib/gis/db/backends/postgis/models.py` | leaf | core | sensitive:db_schema | 56.9 | 2 |
| `django/contrib/admin/filters.py` | business | core | runtime_cycle | 58.3 | 25 |
| `django/contrib/admin/helpers.py` | business | core | runtime_cycle | 58.0 | 25 |
| `django/contrib/admin/views/main.py` | business | core | runtime_cycle | 87.9 | 25 |
| `django/contrib/flatpages/views.py` | business | core | runtime_cycle | 53.7 | 6 |
| `django/contrib/gis/forms/fields.py` | business | core | score_top | 90.6 | 32 |
| `django/contrib/gis/gdal/raster/source.py` | business | core | score_top | 99.2 | 63 |
| `django/contrib/gis/geos/point.py` | business | core | runtime_cycle | 78.1 | 62 |
| `django/core/checks/__init__.py` | business | core | runtime_cycle | 85.0 | 601 |
| `django/core/mail/handler.py` | business | core | score_top | 96.1 | 601 |
| `django/db/backends/sqlite3/operations.py` | business | core | runtime_cycle | 94.8 | 6 |
| `django/tasks/base.py` | business | core | runtime_cycle | 76.8 | 6 |
| `django/utils/module_loading.py` | business | core | score_top | 94.2 | 601 |
| `django/utils/regex_helper.py` | business | core | runtime_cycle | 89.1 | 601 |
| `django/contrib/postgres/utils.py` | leaf | business | default | 64.9 | 14 |
| `django/core/management/color.py` | leaf | business | default | 61.8 | 602 |
| `django/urls/exceptions.py` | leaf | business | default | 81.3 | 601 |
| `scripts/tests.py` | leaf | business | default | 57.9 | 0 |

</details>

**catalog-only** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 20 | 3 | 3 | 0.769 |
| business | 3 | 11 | 17 | 0.355 |
| core | 0 | 2 | 16 | 0.889 |
| precision | 0.870 | 0.688 | 0.444 | |

<details><summary>Disagreements (28)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `django/utils/tree.py` | core | business | default | 75.7 | 602 |
| `django/views/debug.py` | core | business | default | 69.5 | 13 |
| `django/contrib/contenttypes/apps.py` | business | leaf | score_low | 29.1 | 0 |
| `django/contrib/sitemaps/views.py` | business | leaf | score_low | 0.3 | 0 |
| `django/test/client.py` | business | leaf | test_file | – | 2 |
| `django/contrib/admin/decorators.py` | leaf | core | runtime_cycle | 86.3 | 25 |
| `django/contrib/gis/db/backends/postgis/models.py` | leaf | core | sensitive:db_schema | 56.9 | 2 |
| `django/urls/exceptions.py` | leaf | core | runtime_cycle | 81.3 | 601 |
| `django/contrib/admin/filters.py` | business | core | runtime_cycle | 58.3 | 25 |
| `django/contrib/admin/helpers.py` | business | core | runtime_cycle | 58.0 | 25 |
| `django/contrib/admin/views/main.py` | business | core | runtime_cycle | 87.9 | 25 |
| `django/contrib/flatpages/views.py` | business | core | runtime_cycle | 53.7 | 6 |
| `django/contrib/gis/forms/fields.py` | business | core | score_top | 90.6 | 32 |
| `django/contrib/gis/gdal/raster/source.py` | business | core | score_top | 99.2 | 63 |
| `django/contrib/gis/geos/point.py` | business | core | runtime_cycle | 78.1 | 62 |
| `django/contrib/gis/geos/prepared.py` | business | core | runtime_cycle | 78.1 | 62 |
| `django/contrib/postgres/fields/hstore.py` | business | core | runtime_cycle | 55.4 | 10 |
| `django/contrib/postgres/search.py` | business | core | runtime_cycle | 48.7 | 10 |
| `django/core/checks/__init__.py` | business | core | runtime_cycle | 85.0 | 601 |
| `django/core/mail/handler.py` | business | core | runtime_cycle | 96.1 | 601 |
| `django/db/backends/sqlite3/operations.py` | business | core | runtime_cycle | 94.8 | 6 |
| `django/tasks/base.py` | business | core | runtime_cycle | 76.8 | 6 |
| `django/utils/ipv6.py` | business | core | runtime_cycle | 70.8 | 601 |
| `django/utils/module_loading.py` | business | core | runtime_cycle | 94.2 | 601 |
| `django/utils/regex_helper.py` | business | core | runtime_cycle | 89.1 | 601 |
| `django/contrib/postgres/utils.py` | leaf | business | default | 64.9 | 14 |
| `django/core/management/color.py` | leaf | business | default | 61.8 | 602 |
| `scripts/tests.py` | leaf | business | default | 57.9 | 0 |

</details>

**all-barrels** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 20 | 4 | 2 | 0.769 |
| business | 3 | 15 | 13 | 0.484 |
| core | 0 | 4 | 14 | 0.778 |
| precision | 0.870 | 0.652 | 0.483 | |

<details><summary>Disagreements (26)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `django/core/cache/backends/base.py` | core | business | default | 70.8 | 601 |
| `django/db/backends/utils.py` | core | business | default | 63.3 | 601 |
| `django/utils/tree.py` | core | business | default | 75.7 | 602 |
| `django/views/debug.py` | core | business | default | 69.5 | 13 |
| `django/contrib/contenttypes/apps.py` | business | leaf | score_low | 29.1 | 0 |
| `django/contrib/sitemaps/views.py` | business | leaf | score_low | 0.3 | 0 |
| `django/test/client.py` | business | leaf | test_file | – | 2 |
| `django/contrib/admin/decorators.py` | leaf | core | runtime_cycle | 86.3 | 25 |
| `django/contrib/gis/db/backends/postgis/models.py` | leaf | core | sensitive:db_schema | 56.9 | 2 |
| `django/contrib/admin/filters.py` | business | core | runtime_cycle | 58.3 | 25 |
| `django/contrib/admin/helpers.py` | business | core | runtime_cycle | 58.0 | 25 |
| `django/contrib/admin/views/main.py` | business | core | runtime_cycle | 87.9 | 25 |
| `django/contrib/flatpages/views.py` | business | core | runtime_cycle | 53.7 | 6 |
| `django/contrib/gis/forms/fields.py` | business | core | score_top | 90.6 | 32 |
| `django/contrib/gis/gdal/raster/source.py` | business | core | score_top | 99.2 | 63 |
| `django/contrib/gis/geos/point.py` | business | core | runtime_cycle | 78.1 | 62 |
| `django/core/checks/__init__.py` | business | core | runtime_cycle | 85.0 | 601 |
| `django/core/mail/handler.py` | business | core | score_top | 96.1 | 601 |
| `django/db/backends/sqlite3/operations.py` | business | core | runtime_cycle | 94.8 | 6 |
| `django/tasks/base.py` | business | core | runtime_cycle | 76.8 | 6 |
| `django/utils/module_loading.py` | business | core | score_top | 94.2 | 601 |
| `django/utils/regex_helper.py` | business | core | runtime_cycle | 89.1 | 601 |
| `django/contrib/postgres/utils.py` | leaf | business | default | 64.9 | 14 |
| `django/core/management/color.py` | leaf | business | default | 61.8 | 602 |
| `django/urls/exceptions.py` | leaf | business | default | 81.3 | 601 |
| `scripts/tests.py` | leaf | business | default | 57.9 | 0 |

</details>

**2026.11-3** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 20 | 4 | 2 | 0.769 |
| business | 3 | 15 | 13 | 0.484 |
| core | 0 | 4 | 14 | 0.778 |
| precision | 0.870 | 0.652 | 0.483 | |

<details><summary>Disagreements (26)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `django/core/cache/backends/base.py` | core | business | default | 70.8 | 601 |
| `django/db/backends/utils.py` | core | business | default | 63.3 | 601 |
| `django/utils/tree.py` | core | business | default | 75.7 | 602 |
| `django/views/debug.py` | core | business | default | 69.5 | 13 |
| `django/contrib/contenttypes/apps.py` | business | leaf | score_low | 29.1 | 0 |
| `django/contrib/sitemaps/views.py` | business | leaf | score_low | 0.3 | 0 |
| `django/test/client.py` | business | leaf | test_file | – | 2 |
| `django/contrib/admin/decorators.py` | leaf | core | runtime_cycle | 86.3 | 25 |
| `django/contrib/gis/db/backends/postgis/models.py` | leaf | core | sensitive:db_schema | 56.9 | 2 |
| `django/contrib/admin/filters.py` | business | core | runtime_cycle | 58.3 | 25 |
| `django/contrib/admin/helpers.py` | business | core | runtime_cycle | 58.0 | 25 |
| `django/contrib/admin/views/main.py` | business | core | runtime_cycle | 87.9 | 25 |
| `django/contrib/flatpages/views.py` | business | core | runtime_cycle | 53.7 | 6 |
| `django/contrib/gis/forms/fields.py` | business | core | score_top | 90.6 | 32 |
| `django/contrib/gis/gdal/raster/source.py` | business | core | score_top | 99.2 | 63 |
| `django/contrib/gis/geos/point.py` | business | core | runtime_cycle | 78.1 | 62 |
| `django/core/checks/__init__.py` | business | core | runtime_cycle | 85.0 | 601 |
| `django/core/mail/handler.py` | business | core | score_top | 96.1 | 601 |
| `django/db/backends/sqlite3/operations.py` | business | core | runtime_cycle | 94.8 | 6 |
| `django/tasks/base.py` | business | core | runtime_cycle | 76.8 | 6 |
| `django/utils/module_loading.py` | business | core | score_top | 94.2 | 601 |
| `django/utils/regex_helper.py` | business | core | runtime_cycle | 89.1 | 601 |
| `django/contrib/postgres/utils.py` | leaf | business | default | 64.9 | 14 |
| `django/core/management/color.py` | leaf | business | default | 61.8 | 602 |
| `django/urls/exceptions.py` | leaf | business | default | 81.3 | 601 |
| `scripts/tests.py` | leaf | business | default | 57.9 | 0 |

</details>

**current** — confusion（列 = 標註，欄 = 預測）

| label \ pred | leaf | business | core | recall |
|---|---|---|---|---|
| leaf | 20 | 4 | 2 | 0.769 |
| business | 3 | 15 | 13 | 0.484 |
| core | 0 | 4 | 14 | 0.778 |
| precision | 0.870 | 0.652 | 0.483 | |

<details><summary>Disagreements (26)</summary>

| path | label | pred | rules | pct | prod blast |
|---|---|---|---|---|---|
| `django/core/cache/backends/base.py` | core | business | default | 70.8 | 601 |
| `django/db/backends/utils.py` | core | business | default | 63.3 | 601 |
| `django/utils/tree.py` | core | business | default | 75.7 | 602 |
| `django/views/debug.py` | core | business | default | 69.5 | 13 |
| `django/contrib/contenttypes/apps.py` | business | leaf | score_low | 29.1 | 0 |
| `django/contrib/sitemaps/views.py` | business | leaf | score_low | 0.3 | 0 |
| `django/test/client.py` | business | leaf | test_file | – | 2 |
| `django/contrib/admin/decorators.py` | leaf | core | runtime_cycle | 86.3 | 25 |
| `django/contrib/gis/db/backends/postgis/models.py` | leaf | core | sensitive:db_schema | 56.9 | 2 |
| `django/contrib/admin/filters.py` | business | core | runtime_cycle | 58.3 | 25 |
| `django/contrib/admin/helpers.py` | business | core | runtime_cycle | 58.0 | 25 |
| `django/contrib/admin/views/main.py` | business | core | runtime_cycle | 87.9 | 25 |
| `django/contrib/flatpages/views.py` | business | core | runtime_cycle | 53.7 | 6 |
| `django/contrib/gis/forms/fields.py` | business | core | score_top | 90.6 | 32 |
| `django/contrib/gis/gdal/raster/source.py` | business | core | score_top | 99.2 | 63 |
| `django/contrib/gis/geos/point.py` | business | core | runtime_cycle | 78.1 | 62 |
| `django/core/checks/__init__.py` | business | core | runtime_cycle | 85.0 | 601 |
| `django/core/mail/handler.py` | business | core | score_top | 96.1 | 601 |
| `django/db/backends/sqlite3/operations.py` | business | core | runtime_cycle | 94.8 | 6 |
| `django/tasks/base.py` | business | core | runtime_cycle | 76.8 | 6 |
| `django/utils/module_loading.py` | business | core | score_top | 94.2 | 601 |
| `django/utils/regex_helper.py` | business | core | runtime_cycle | 89.1 | 601 |
| `django/contrib/postgres/utils.py` | leaf | business | default | 64.9 | 14 |
| `django/core/management/color.py` | leaf | business | default | 61.8 | 602 |
| `django/urls/exceptions.py` | leaf | business | default | 81.3 | 601 |
| `scripts/tests.py` | leaf | business | default | 57.9 | 0 |

</details>
