import unittest
from tradelink.generator import generate
from tradelink.detections import detect
from tradelink.report import report_markdown


class TestDetections(unittest.TestCase):
    def test_full_attack_detected(self):
        events = generate()
        alerts = detect(events)
        self.assertEqual({a['rule_id'] for a in alerts},
                         {'TL-001', 'TL-002', 'TL-003', 'TL-004', 'TL-005'})
        self.assertEqual(len(alerts), 5)

    def test_deterministic_fixture(self):
        self.assertEqual(generate(), generate())

    def test_baseline_without_attack_has_no_alerts(self):
        benign = [e for e in generate() if e['source']['ip'] != '203.0.113.77']
        self.assertEqual(detect(benign), [])

    def test_failed_attempts_below_threshold(self):
        ev = [e for e in generate() if e['event']['action'] == 'login_failure'][:4]
        self.assertEqual(detect(ev), [])

    def test_report_has_caveats(self):
        events = generate()
        report = report_markdown(events, detect(events))
        self.assertIn('synthetic', report.lower())
        self.assertIn('403 responses demonstrate blocked access', report)
        self.assertIn('TL-IR-001', report)


if __name__ == '__main__':
    unittest.main()
