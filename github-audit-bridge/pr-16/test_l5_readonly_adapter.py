import json
import unittest

from source.freqtrade_console import l5_readonly_adapter as adapter


def walk_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_keys(item)


class L5ReadonlyAdapterTest(unittest.TestCase):
    def test_backtest_cockpit_schema_is_readonly_and_macd_named(self):
        payload = adapter.get_l5_backtest_cockpit(limit=48)

        self.assertTrue(payload["readonly"])
        self.assertIn("macd_signals", payload)
        self.assertNotIn("ma" + "ce_signals", payload)
        self.assertIn("source_status", payload)
        self.assertIn("fallback_sources", payload)
        self.assertIn("module_status", payload)
        self.assertIsInstance(payload["candles"], list)
        self.assertIsInstance(payload["backtest_summary"], dict)
        if payload["macd_signals"]:
            signal = payload["macd_signals"][0]
            self.assertEqual(signal["pair"], payload["pair"])
            self.assertEqual(signal["timeframe"], payload["timeframe"])

    def test_strategy_evolution_schema_is_fallback_safe(self):
        payload = adapter.get_l5_strategy_evolution()

        self.assertTrue(payload["readonly"])
        self.assertIn("strategies", payload)
        self.assertIn("strategy_scores", payload)
        self.assertIn("evolution_timeline", payload)
        self.assertIn("next_recommendations", payload)
        self.assertIn("source_status", payload)
        self.assertIn("module_status", payload)

    def test_readiness_and_guard_status_are_display_only(self):
        readiness = adapter.get_l5_readiness()
        guard = adapter.get_l5_guard_status()

        self.assertTrue(readiness["readonly"])
        self.assertTrue(readiness["readonly_mode"])
        self.assertTrue(guard["readonly"])
        self.assertEqual(guard["mutation_policy"], "default deny")

    def test_responses_do_not_expose_sensitive_field_names(self):
        payloads = [
            adapter.get_l5_readiness(),
            adapter.get_l5_backtest_cockpit(limit=16),
            adapter.get_l5_strategy_evolution(),
            adapter.get_l5_data_sources(),
            adapter.get_l5_guard_status(),
        ]
        forbidden = {
            "tok" + "en",
            "cook" + "ie",
            "auth" + "orization",
            "api" + "_key",
            "pass" + "word",
        }

        for payload in payloads:
            lowered = json.dumps(payload, ensure_ascii=False).lower()
            self.assertNotIn("ma" + "ce", lowered)
            for key in walk_keys(payload):
                self.assertNotIn(key.lower(), forbidden)


if __name__ == "__main__":
    unittest.main()
