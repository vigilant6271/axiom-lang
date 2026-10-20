import unittest
from axiom.adaptive import AdaptiveEngine
from axiom.auto_engine import AutoEngine


class EngineTests(unittest.TestCase):
    def test_ema(self):
        engine = AdaptiveEngine(alpha=0.5)
        self.assertAlmostEqual(engine.observe(10).baseline, 10)
        self.assertAlmostEqual(engine.observe(20).baseline, 15)

    def test_bounded_samples(self):
        engine = AdaptiveEngine(max_samples=3)
        for x in range(10):
            snap = engine.observe(x)
        self.assertEqual(snap.samples_seen, 3)

    def test_rejects_nonfinite(self):
        engine = AdaptiveEngine()
        with self.assertRaises(ValueError):
            engine.observe(float("nan"))

    def test_auto_engine_telemetry_opt_in(self):
        report = AutoEngine(telemetry=True).execute("print(7)", output=lambda _: None)
        self.assertEqual(report.results, [7])
        self.assertIsNotNone(report.adaptation)
        self.assertGreaterEqual(report.elapsed_seconds, 0)


if __name__ == "__main__":
    unittest.main()
