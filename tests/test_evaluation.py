import copy
import unittest
from lab.evaluate import evaluate, verified_craft


def state(inventory=None):
    return {role: {"inventory": copy.deepcopy(inventory or {}), "hp": 100} for role in ["iron", "coal", "wood", "smelter", "smith"]}


class OutcomeEvidenceTests(unittest.TestCase):
    def test_invalid_model_target_is_a_failed_attempt_not_a_verifier_crash(self):
        event = {"actor": "coal", "action": "transfer", "args": {"target": "missing", "item": "coal"}, "result": {"status": "error"}, "before": state(), "after": state()}
        result = evaluate({"events": [event]})
        self.assertEqual(result["failed_actions"], 1)
        self.assertEqual(result["verified_transfers"], 0)

    def test_initial_tools_and_final_inventory_do_not_count_as_new_crafts(self):
        run = {"final": state({"pickaxe": 1, "axe": 1, "sword2": 1}), "events": []}
        result = evaluate(run)
        self.assertFalse(result["passed"])
        self.assertEqual(result["newly_crafted"], {"pickaxe": 0, "axe": 0, "sword2": 0})

    def test_api_success_without_inventory_change_is_not_evidence(self):
        event = {"actor": "smith", "action": "craft", "args": {"item": "pickaxe"}, "result": {"status": "success"}, "before": state(), "after": state()}
        self.assertEqual(verified_craft(event), 0)

    def test_spawned_output_without_material_consumption_is_rejected(self):
        event = {"actor": "smith", "action": "craft", "args": {"item": "pickaxe"}, "result": {"status": "success"}, "before": state(), "after": state()}
        event["after"]["smith"]["inventory"] = {"pickaxe": 1}
        self.assertEqual(verified_craft(event), 0)

    def test_real_recipe_delta_is_accepted(self):
        event = {"actor": "smith", "action": "craft", "args": {"item": "pickaxe"}, "result": {"status": "success"}, "before": state(), "after": state()}
        event["before"]["smith"]["inventory"] = {"ironbar": 5, "logs": 1}
        event["after"]["smith"]["inventory"] = {"pickaxe": 1}
        self.assertEqual(verified_craft(event), 1)

    def test_handoff_needs_matching_sender_and_recipient_deltas(self):
        event = {"actor": "iron", "action": "transfer", "args": {"target": "smelter", "item": "ironore", "count": 5}, "result": {"status": "success"}, "before": state(), "after": state()}
        event["before"]["iron"]["inventory"] = {"ironore": 5}
        event["after"]["smelter"]["inventory"] = {"ironore": 4}
        self.assertEqual(evaluate({"events": [event]})["verified_transfers"], 0)


if __name__ == "__main__":
    unittest.main()
