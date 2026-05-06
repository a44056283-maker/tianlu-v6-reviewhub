from pathlib import Path
import unittest


L5_HTML = Path("source/freqtrade_console/static/tabs/l5-evolution.html")
CONSOLE_SERVER = Path("source/freqtrade_console/console_server.py")


class L5WebUIStaticTest(unittest.TestCase):
    def test_l5_page_uses_macd_term_only(self):
        html = L5_HTML.read_text(encoding="utf-8")

        self.assertIn("MACD", html)
        self.assertNotIn("MA" + "CE", html)
        self.assertNotIn("ma" + "ce", html)

    def test_l5_page_uses_get_only_aggregation_endpoints(self):
        html = L5_HTML.read_text(encoding="utf-8")

        for endpoint in (
            "/api/l5/readiness",
            "/api/l5/backtest-cockpit",
            "/api/l5/strategy-evolution",
            "/api/l5/data-sources",
            "/api/l5/guard-status",
        ):
            self.assertIn(endpoint, html)
        self.assertIn("method:'GET'", html)
        self.assertIn("URLSearchParams", html)
        self.assertIn("data-timeframe", html)
        self.assertNotIn("method:'POST'", html)
        self.assertNotIn('method:"POST"', html)

    def test_l5_page_has_no_known_trade_mutation_terms(self):
        html = L5_HTML.read_text(encoding="utf-8").lower()

        for term in ("forceenter", "forceexit", "autopilot/start", "autopilot/stop"):
            self.assertNotIn(term, html)

    def test_l5_routes_are_declared_get_only(self):
        source = CONSOLE_SERVER.read_text(encoding="utf-8")

        for endpoint in (
            '/api/l5/readiness',
            '/api/l5/backtest-cockpit',
            '/api/l5/strategy-evolution',
            '/api/l5/data-sources',
            '/api/l5/guard-status',
        ):
            marker = f'@app.route("{endpoint}", methods=["GET"])'
            self.assertIn(marker, source)


if __name__ == "__main__":
    unittest.main()
