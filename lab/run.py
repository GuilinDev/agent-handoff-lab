"""Run a traceable five-role fixture on the actual AgentWorld server.

Scripted policy is explicitly labelled; LLM policy uses the same actions and verifier.
"""
import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from .engine import Engine
from .evaluate import evaluate, RECIPES, TARGETS, verified_craft

ROOT = Path(__file__).resolve().parents[1]
ROLES = ["iron", "coal", "wood", "smelter", "smith"]
LABELS = {"iron": "Iron supplier", "coal": "Coal supplier", "wood": "Wood courier", "smelter": "Smelter", "smith": "Smith"}
POSITIONS = {"iron": (87, 33), "coal": (91, 33), "wood": (89, 36), "smelter": (87, 36), "smith": (91, 36)}
INITIAL = {"iron": {"ironore": 10}, "coal": {"coal": 10}, "wood": {"logs": 2}, "smelter": {}, "smith": {"hilt2": 1}}


def load_env():
    file = ROOT / ".env"
    if file.exists():
        for line in file.read_text(encoding="utf-8-sig").splitlines():
            if line.strip() and not line.lstrip().startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".pending")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)


def action(name, **args):
    return {"action": name, "args": args}


class ScriptedPolicy:
    """Fixed policy for instrumentation and intervention smoke tests, not AI."""
    def __init__(self):
        self.sent = set()
        self.tried_shortage = False
        self.requested = False

    def decide(self, role, observation, messages):
        inv = observation["inventory"]
        if role in ("iron", "coal", "wood"):
            item, target = {"iron": ("ironore", "smelter"), "coal": ("coal", "smelter"), "wood": ("logs", "smith")}[role]
            if role not in self.sent:
                self.sent.add(role)
                return action("transfer", target=target, item=item, count=inv[item])
            if role == "coal" and inv.get("coal", 0) and any(m["sender"] == "smelter" and "coal" in m["message"].lower() for m in messages):
                return action("transfer", target="smelter", item="coal", count=inv["coal"])
            return action("wait", reason="My handoff is complete" if not inv.get(item, 0) else "Holding reserve; waiting for a request")
        if role == "smelter":
            if inv.get("ironbar", 0):
                return action("transfer", target="smith", item="ironbar", count=inv["ironbar"])
            if not inv.get("ironore", 0):
                return action("wait", reason="All ore has been processed")
            if inv.get("coal", 0) < 5:
                if not self.tried_shortage:
                    self.tried_shortage = True
                    return action("craft", item="ironbar", count=5)
                if not self.requested:
                    self.requested = True
                    return action("chat", target="coal", message="Need 5 more coal to finish the second batch. Please transfer your reserve to smelter.")
                return action("wait", reason="Blocked: need 5 coal for the next batch")
            return action("craft", item="ironbar", count=5)
        for item in TARGETS:
            if not inv.get(item, 0) and all(inv.get(k, 0) >= v for k, v in RECIPES[item].items()):
                return action("craft", item=item, count=1)
        return action("wait", reason="Waiting for the next verified iron-bar delivery")


TOOLS = [
    {"type": "function", "function": {"name": "transfer", "description": "Transfer your available inventory to another role. Read actual delivered count in the response.", "parameters": {"type": "object", "properties": {"target": {"type": "string", "enum": ROLES}, "item": {"type": "string", "enum": ["ironore", "coal", "logs", "ironbar", "hilt2"]}, "count": {"type": "integer", "minimum": 1}}, "required": ["target", "item", "count"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "craft", "description": "Craft using your role's skill, consuming inventory. Smelter: ironbar. Smith: pickaxe, axe, sword2.", "parameters": {"type": "object", "properties": {"item": {"type": "string", "enum": list(RECIPES)}, "count": {"type": "integer", "enum": [1, 5, 10]}}, "required": ["item", "count"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "chat", "description": "Send a concise coordination message. The recipient receives it when the message is delivered.", "parameters": {"type": "object", "properties": {"target": {"type": "string", "enum": ROLES + ["all"]}, "message": {"type": "string"}}, "required": ["target", "message"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "wait", "description": "Wait one turn if no useful action is available.", "parameters": {"type": "object", "properties": {"reason": {"type": "string"}}, "required": ["reason"], "additionalProperties": False}}},
]


class LLMPolicy:
    def __init__(self):
        self.key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if os.environ.get("LLM_PROVIDER", "openai-compatible") != "openai-compatible":
            raise ValueError("v0.1 supports OpenAI-compatible tool-calling APIs only")
        self.model = os.environ.get("LLM_MODEL")
        self.base = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        if not self.key or not self.model:
            raise ValueError("LLM mode requires LLM_API_KEY and LLM_MODEL in the local .env file")
        self.history = {role: [] for role in ROLES}
        self.usage = {"input_tokens": 0, "output_tokens": 0, "requests": 0}

    def decide(self, role, observation, messages):
        prompt = (f"You are {LABELS[role]} in a five-agent team. Complete 1 NEW pickaxe, 1 NEW axe, 1 NEW sword2. "
                  f"Roles: {LABELS}. Recipes: {RECIPES}. Your role id is {role}. "
                  "The environment prepositions agents and supplies materials. You have only your own inventory, public recipes, "
                  "delivered messages and your own past tool results. Coordinate concrete handoffs. A delivery may be partial. "
                  "Check actual state and responses. Do not claim completion until the items are made. "
                  "Smelter alone can smelt; smith alone can craft final equipment. Use exactly one tool each turn. "
                  "Prefer useful actions; avoid repeating unchanged messages. No need to explain hidden reasoning.")
        payload = {"model": self.model, "messages": [{"role": "system", "content": prompt},
            *self.history[role][-24:], {"role": "user", "content": json.dumps({"observation": observation, "delivered_messages": messages[-12:]})}],
            "tools": TOOLS, "tool_choice": "required", "parallel_tool_calls": False}
        req = Request(self.base + "/chat/completions", data=json.dumps(payload).encode(),
                      headers={"Content-Type": "application/json", "Authorization": "Bearer " + self.key})
        try:
            with urlopen(req, timeout=120) as response:
                result = json.load(response)
        except HTTPError as error:
            # Provider payloads can echo request details: keep them out of public logs.
            raise RuntimeError(f"LLM request failed with HTTP {error.code}") from None
        calls = result["choices"][0]["message"].get("tool_calls", [])
        if len(calls) != 1:
            raise RuntimeError("Model must return exactly one tool call")
        function = calls[0]["function"]
        arguments = json.loads(function["arguments"])
        usage = result.get("usage", {})
        self.usage["input_tokens"] += usage.get("prompt_tokens", 0)
        self.usage["output_tokens"] += usage.get("completion_tokens", 0)
        self.usage["requests"] += 1
        return action(function["name"], **arguments)

    def record(self, role, chosen, result):
        self.history[role].append({"role": "user", "content": json.dumps({"your_previous_action": chosen, "observed_result": result})})


def run_one(mode, condition, max_rounds=18, pace=0):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_id = f"{stamp}-{mode}-{condition}"
    policy = ScriptedPolicy() if mode == "scripted" else LLMPolicy()
    engine = Engine(os.environ.get("AGENTWORLD_URL", "http://127.0.0.1:7031"))
    run = {"schema_version": 1, "id": run_id, "mode": mode, "condition": condition,
           "started_at": datetime.now(timezone.utc).isoformat(), "status": "setting-up", "round": 0,
           "model": getattr(policy, "model", None), "events": [], "messages": [], "usage": {},
           "roles": LABELS, "upstream": json.loads((ROOT / "upstream.lock.json").read_text()),
           "fixture": {"initial_inventory": INITIAL, "smithing_level": 45, "prepositioned": True,
                       "first_coal_delivery_cap": 5 if condition != "normal" else None,
                       "request_delay_rounds": 3 if condition == "delayed-request" else 0,
                       "decision_order": ROLES, "max_rounds": max_rounds,
                       "notes": "Scripted is a fixed rule policy, never LLM autonomy. Skill 45 removes smelting randomness. No gathering or long-distance navigation in v0.1."}}
    output = ROOT / "artifacts/runs" / (run_id + ".json")
    live = ROOT / ".runtime/live.json"
    save_json(live, run)
    coal_intervened = False
    begun = time.monotonic()
    try:
        for role in ROLES:
            # Stable local users permit a browser observer to find the party.
            engine.login(role, "lab_" + role)
            engine.post(role, "teleport", x=POSITIONS[role][0], y=POSITIONS[role][1], withAnimation=False)
            engine.set_inventory(role, INITIAL[role])
            for skill in ["smithing", "mining", "lumberjacking"]:
                level = 45 if ((skill == "smithing" and role in ("smelter", "smith")) or (skill == "mining" and role in ("iron", "coal")) or (skill == "lumberjacking" and role == "wood")) else 1
                # Upstream's lowering path resets XP to zero instead of the target.
                # Explicit reset then raise makes the fixture independent of login defaults.
                engine.post(role, "setSkillLevel", skill=skill, level=1)
                result = engine.post(role, "setSkillLevel", skill=skill, level=level)
                if result.get("status") != "success":
                    raise RuntimeError(f"Cannot set {role} skill {skill}")
        run["initial"] = engine.snapshot()
        run["status"] = "running"
        save_json(live, run)
        for round_number in range(1, max_rounds + 1):
            run["round"] = round_number
            for message in run["messages"]:
                if not message.get("delivered") and message["deliver_at"] <= round_number:
                    engine.post(message["sender"], "chat", message=message["message"], **{"global": True})
                    message["delivered"] = True
            for role in ROLES:
                before = engine.snapshot()
                visible = [m for m in run["messages"] if m.get("delivered") and m["target"] in (role, "all")]
                chosen = policy.decide(role, before[role], visible)
                name, args = chosen["action"], chosen["args"]
                event = {"id": len(run["events"]) + 1, "round": round_number, "actor": role,
                         "action": name, "args": args, "elapsed_s": round(time.monotonic() - begun, 3), "before": before}
                result = {"status": "success", "message": "Waited one turn"}
                if name == "transfer":
                    target, item, count = args.get("target"), args.get("item"), args.get("count")
                    if target not in ROLES or target == role or item not in {"ironore", "coal", "logs", "ironbar", "hilt2"} or type(count) is not int or not 1 <= count <= 30:
                        result = {"status": "error", "message": "Invalid handoff arguments"}
                    else:
                        actual = count
                        if condition != "normal" and role == "coal" and item == "coal" and not coal_intervened:
                            actual = min(count, 5)
                            coal_intervened = True
                            event["intervention"] = "First coal handoff capped at 5; remaining coal stays with supplier"
                        result = engine.transfer(role, target, item, actual)
                elif name == "craft":
                    item, count = args.get("item"), args.get("count")
                    allowed = ["ironbar"] if role == "smelter" else list(TARGETS) if role == "smith" else []
                    if item not in allowed or type(count) is not int or count not in (1, 5, 10):
                        result = {"status": "error", "message": "Recipe or count unavailable to this role"}
                    else:
                        result = engine.craft(role, item, count)
                elif name == "chat":
                    target, text = args.get("target"), args.get("message")
                    if target not in ROLES + ["all"] or not isinstance(text, str) or not 1 <= len(text) <= 1000:
                        result = {"status": "error", "message": "Invalid message"}
                    else:
                        delay = 3 if condition == "delayed-request" and role == "smelter" and target in ("coal", "all") else 0
                        message = {"sender": role, "target": target, "message": text, "sent_at": round_number,
                                   "deliver_at": round_number + delay, "delivered": delay == 0, "event_id": event["id"]}
                        run["messages"].append(message)
                        if delay == 0:
                            engine.post(role, "chat", message=text, **{"global": True})
                        else:
                            event["intervention"] = f"Coordination message delayed by {delay} rounds"
                        result = {"status": "success", "message": "Message accepted for delivery"}
                elif name != "wait":
                    result = {"status": "error", "message": "Unknown action"}
                event["result"] = result
                event["after"] = engine.snapshot()
                event["verified_crafted"] = verified_craft(event) if name == "craft" and args.get("item") in RECIPES else 0
                if name == "craft" and result.get("status") == "success":
                    result["verified_crafted"] = event["verified_crafted"]
                    if not event["verified_crafted"]:
                        result["status"] = "error"
                        result["message"] = "API reported success but inventory did not verify a crafted item"
                run["events"].append(event)
                if mode == "llm":
                    policy.record(role, chosen, result)
                    run["usage"] = policy.usage
                run["final"] = event["after"]
                run["evaluation"] = evaluate(run)
                save_json(live, run)
                if pace:
                    time.sleep(pace)
                if run["evaluation"]["passed"]:
                    break
            if run.get("evaluation", {}).get("passed"):
                break
        run["status"] = "passed" if evaluate(run)["passed"] else "failed"
    except Exception as error:
        run["status"] = "error"
        run["error"] = f"{type(error).__name__}: {error}"
    finally:
        run["duration_s"] = round(time.monotonic() - begun, 3)
        run["evaluation"] = evaluate(run)
        save_json(output, run)
        save_json(live, run)
        engine.close()
    print(json.dumps({"id": run_id, "status": run["status"], "evaluation": run["evaluation"], "error": run.get("error")}))
    return run


def main():
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["scripted", "llm"], default="scripted")
    parser.add_argument("--condition", choices=["normal", "partial-delivery", "delayed-request"], default="normal")
    parser.add_argument("--max-rounds", type=int, default=18)
    parser.add_argument("--pace", type=float, default=0)
    parser.add_argument("--suite", action="store_true")
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    if not 1 <= args.repeats <= 20 or not 1 <= args.max_rounds <= 50 or not 0 <= args.pace <= 10:
        parser.error("Use 1-20 repeats, 1-50 rounds and 0-10 seconds pace")
    # OS-backed exclusive lock is automatically released on process exit/crash.
    lock_path = ROOT / ".runtime/runner.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock = lock_path.open("a+b")
    lock.seek(0)
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        parser.exit(1, "Another lab experiment is running; wait for it to finish.\n")
    if args.suite:
        runs = []
        for repetition in range(args.repeats):
            for condition in ["normal", "partial-delivery", "delayed-request"]:
                run = run_one(args.mode, condition, args.max_rounds, args.pace)
                runs.append({"id": run["id"], "condition": condition, "repetition": repetition + 1, "status": run["status"], **run["evaluation"]})
                if run["status"] == "error":
                    raise SystemExit("Suite stopped on infrastructure error; inspect the saved trace")
        save_json(ROOT / "artifacts/suite.json", {"mode": args.mode, "repeats": args.repeats, "runs": runs,
            "interpretation": "Fixed-policy repetitions validate instrumentation; they do not estimate LLM capability." if args.mode == "scripted" else "Exploratory repeated runs, not a benchmark-wide estimate."})
    else:
        run = run_one(args.mode, args.condition, args.max_rounds, args.pace)
        if run["status"] == "error":
            raise SystemExit(1)


if __name__ == "__main__":
    main()
