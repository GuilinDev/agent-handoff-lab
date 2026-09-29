"""Minimal local AgentWorld client. Credentials are never written into trajectories."""
import json
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError


class Engine:
    def __init__(self, url="http://127.0.0.1:7031"):
        self.url = url.rstrip("/")
        self.tokens = {}
        self.users = {}

    def request(self, endpoint, data=None, query=""):
        payload = None if data is None else json.dumps(data).encode()
        req = Request(self.url + "/ai/" + endpoint + query, data=payload,
                      headers={"Content-Type": "application/json"})
        try:
            with urlopen(req, timeout=25) as response:
                return json.load(response)
        except HTTPError as error:
            return json.loads(error.read())

    def post(self, role, endpoint, **data):
        return self.request(endpoint, {"token": self.tokens[role], **data})

    def login(self, role, username):
        result = self.request("login", {"username": username, "password": "local-lab-only", "force": True})
        if result.get("status") != "success":
            raise RuntimeError(f"Cannot create role {role}: {result.get('message')}")
        self.tokens[role] = result["token"]
        self.users[role] = username

    def observe(self, role):
        result = self.request("observe", query=f"?token={self.tokens[role]}&radius=12")
        if result.get("status") != "success":
            raise RuntimeError(f"Cannot observe {role}: {result.get('message')}")
        inventory = {}
        for item in result.get("inventory", {}).get("items", []):
            key = item.get("key")
            if key:
                inventory[key] = inventory.get(key, 0) + item.get("count", 0)
        player = result.get("playerStatus", {})
        return {"inventory": inventory, "hp": player.get("hitPoints"),
                "location": result.get("location", {}), "username": self.users[role]}

    def snapshot(self):
        return {role: self.observe(role) for role in self.tokens}

    def set_inventory(self, role, items):
        result = self.post(role, "setInventory", items=[{"key": key, "count": count} for key, count in items.items() if count > 0], clearFirst=True)
        if result.get("status") != "success" or result.get("results", {}).get("failedItems"):
            raise RuntimeError(f"Inventory update failed for {role}")
        if self.observe(role)["inventory"] != {k: v for k, v in items.items() if v > 0}:
            raise RuntimeError(f"Inventory verification failed for {role}")

    def transfer(self, role, target, item, count):
        """Serialized two-inventory handoff with read-back and compensation.

        The upstream engine exposes setInventory, not an atomic trade endpoint.
        An ambiguous transport failure aborts the run; it is never silently retried.
        """
        before = self.observe(role)["inventory"]
        recipient = self.observe(target)["inventory"]
        if count < 1 or before.get(item, 0) < count:
            return {"status": "error", "message": "Insufficient inventory for handoff"}
        sender_after = dict(before)
        sender_after[item] -= count
        recipient_after = dict(recipient)
        recipient_after[item] = recipient_after.get(item, 0) + count
        try:
            self.set_inventory(role, sender_after)
            self.set_inventory(target, recipient_after)
        except Exception:
            self.set_inventory(role, before)
            self.set_inventory(target, recipient)
            raise
        return {"status": "success", "message": f"Delivered {count} {item} to {target}", "verified_count": count}

    def craft(self, role, item, count):
        # Cooldown is enforced by the engine; near its boundary a real failure
        # may add a retry/round. Keep that failure in the evidence.
        time.sleep(0.55)
        return self.post(role, "craft", type="Smelting" if item == "ironbar" else "Smithing", itemKey=item, count=count)

    def close(self):
        for role in list(self.tokens):
            try:
                self.post(role, "logout")
            except Exception:
                pass
