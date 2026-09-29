"""State-based outcome verification, separate from agent self-reports."""
TARGETS = {"pickaxe": 1, "axe": 1, "sword2": 1}
RECIPES = {
    "ironbar": {"ironore": 1, "coal": 1},
    "pickaxe": {"ironbar": 5, "logs": 1},
    "axe": {"ironbar": 3, "logs": 1},
    "sword2": {"ironbar": 2, "hilt2": 1},
}


def verified_craft(event):
    if event.get("action") != "craft":
        return 0
    role, item = event["actor"], event["args"]["item"]
    before = event["before"][role]["inventory"]
    after = event["after"][role]["inventory"]
    made = after.get(item, 0) - before.get(item, 0)
    if made <= 0 or event.get("result", {}).get("status") != "success":
        return 0
    for material, quantity in RECIPES[item].items():
        if before.get(material, 0) - after.get(material, 0) < made * quantity:
            return 0
    return made


def evaluate(run):
    produced = dict.fromkeys(TARGETS, 0)
    failed = waits = transfers = verified_transfers = 0
    for event in run.get("events", []):
        if event.get("action") == "craft" and event["args"].get("item") in produced:
            produced[event["args"]["item"]] += verified_craft(event)
        if event.get("result", {}).get("status") == "error":
            failed += 1
        waits += event.get("action") == "wait"
        if event.get("action") == "transfer":
            transfers += 1
            a, target = event["actor"], event["args"].get("target")
            item = event["args"].get("item")
            if target not in event["before"] or target not in event["after"] or not isinstance(item, str) or event.get("result", {}).get("status") != "success":
                continue
            source_delta = event["before"][a]["inventory"].get(item, 0) - event["after"][a]["inventory"].get(item, 0)
            target_delta = event["after"][target]["inventory"].get(item, 0) - event["before"][target]["inventory"].get(item, 0)
            verified_transfers += source_delta > 0 and source_delta == target_delta
    final = run.get("final") or (run["events"][-1]["after"] if run.get("events") else {})
    inventory = {item: sum(state["inventory"].get(item, 0) for state in final.values()) for item in TARGETS}
    alive = len(final) == 5 and all(isinstance(state.get("hp"), (int, float)) and state["hp"] > 0 for state in final.values())
    passed = alive and all(produced[item] >= needed and inventory[item] >= needed for item, needed in TARGETS.items())
    return {"passed": passed, "newly_crafted": produced, "final_items": inventory, "all_alive": alive,
            "rounds": run.get("round", 0), "actions": len(run.get("events", [])),
            "failed_actions": failed, "wait_actions": waits, "verified_transfers": verified_transfers,
            "transfer_attempts": transfers, "tokens": run.get("usage", {}),
            "scope": "Task 46 inspired fixture; not official benchmark SR or CCE"}
