# What this experiment measures

## Origin and scope

The user-provided Chinese walkthrough shows a local scripted AgentWorld production chain with prepositioned characters and supplied inventory. We recreate that class of demo and add evaluation instrumentation. The upstream reference is Task 46, `data_v0.1_multi/v1.3_benchmark/task_46_mining_expedition.yaml`, pinned to commit `df5237da96a3ef00f602950baa362d14d3a618fe` in [openagents-org/agentworld](https://github.com/openagents-org/agentworld).

This repository is independently authored on top of AgentWorld. It does not claim full benchmark replication. AgentWorld's collaboration metric and this project's intervention measurements are different; we do not report our score as CCE.

## Fixture

Five fixed roles take one action per round in the order iron, coal, wood, smelter, smith. Initial materials: iron supplier 10 iron ore; coal supplier 10 coal; wood courier 2 logs; smith 1 heavy-sword hilt. No target output is initially present. Characters are placed together, gathering is omitted, and relevant crafting skills are set to 45. Other default character properties come from upstream AI login. Characters must remain alive.

Recipes are taken from the engine: iron bar = 1 iron ore + 1 coal; pickaxe = 5 bars + 1 log; axe = 3 bars + 1 log; heavy sword = 2 bars + 1 hilt. Smelting is exposed under the API's Smelting category but uses the upstream Smithing skill calculation. Setup resets the skill to 1 before raising it because the upstream lowering path otherwise resets XP without reaching the requested intermediate level.

Actions available to both policies are `transfer`, `craft`, `chat`, and `wait`. Transfer is a harness-provided primitive implemented with the engine's administrative inventory setters, serialized source/recipient readbacks, and compensating restoration on failure. It is not an atomic game trade, and no transport retries silently mint resources. Crafting uses the real `/ai/craft` endpoint; missing materials and cooldowns are real engine responses.

## Interventions

1. **Normal**: deliver the requested coal; messages reach recipients immediately.
2. **Partial delivery**: cap the first coal handoff at 5 units. The remaining 5 stay with the supplier, and the returned delivered count is truthful. Subsequent transfers work normally.
3. **Delayed request**: apply the same cap, and delay smelter-to-coal (or smelter-to-all) coordination messages by 3 rounds. Other messages are unchanged.

The fixed baseline supplier transfers the reserve after receiving the smelter's request. This explicitly programmed dependency makes it suitable for checking that the intervention and trace instrumentation work. It is **not** evidence that a model discovered a coordination strategy. With LLM mode, decisions would come from the configured model under the same action vocabulary and verifier.

Messages reach the role's private policy inbox at the recorded delivery round. When released, they are also shown as public game chat for the observer; the public display is not the policy's observation channel. Inventory updates are traced around every serialized action, so before/after attribution is simple within this local fixture.

## Verification and metrics

A target counts as newly crafted only when the craft action reports success, the actor's target inventory increases, and recipe materials decrease by at least the required amounts. Final success also requires all three outputs to exist and all five actors to be alive. A self-reported completion, a preloaded tool, or an API success with no state change cannot pass.

We record rounds, attempted actions, waits, failed actions, verified transfers, and model token usage when available. Round count depends on the fixed decision order, engine timing, and stopping rule. It is not latency or token cost. The run ends on verified completion or a maximum round count; infrastructure failures are labelled `error`, rather than task failures.

## Results and nuisance effects

The archived suite has 5 normal, 5 partial-delivery and 5 delayed-request runs, executed in interleaved condition order. Means are 5.0, 7.2, and 9.0 rounds, with 15/15 verified completions. Each fixed policy is identical across repeats, but the engine's real-time crafting cooldown can affect outcomes. Run `20260929T030826581691Z-scripted-partial-delivery` required 8 rounds because the smith encountered `Crafting is on cooldown`, in addition to the expected missing-coal failure. No failed event was removed from that run.

Two preliminary setup attempts are preserved locally under ignored `artifacts/private/`; one was before server readiness and one exposed the skill-reset issue. They preceded the recorded suite and are not included as experimental repetitions. The archive also contains one initial successful smoke run and a separate paced recording run; the comparison table uses only the 15 run IDs listed in `suite.json`.

These repetitions validate a small harness, not statistical generalization. We deliberately show the cooldown variation instead of attributing every extra round to communication. Engine timing is a nuisance variable to control or stratify in future work.

## Explainability claim

The dependency graph represents material requirements. The inventory deltas and delivered messages expose what happened, and the interventions let us test selected dependencies within this fixture. They do not reveal hidden reasoning, prove a model's intentions, or identify the unique cause of an arbitrary failure. Model-generated explanations would be a separate, potentially unreliable data source.

The motivating hypothesis is that team evaluation should measure verified handoffs, recovery behavior, and coordination costs alongside final outcomes. v0.1 is an instrument for exploring that hypothesis.

## Next experiment

Run multiple LLM policies with the same fixture, recorded model versions, bounded rounds, and token accounting. Add an explicit acknowledgement protocol as a controlled condition. Compare outcome, failed actions, recovery time after disruption, and token cost. Counterbalance decision order and control the cooldown nuisance. Keep unsuccessful trajectories, report variability, and distinguish behavioral observability from internal interpretability.
