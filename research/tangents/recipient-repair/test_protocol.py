"""Synthetic protocol fixtures and rejected-event atomicity checks."""
import json
import unittest
from pathlib import Path
from protocol import Message, Model, ProtocolError, run_case

CASES = json.loads((Path(__file__).parent / 'TRACE-CASES.json').read_text())['cases']


class SyntheticTraceCases(unittest.TestCase):
    def test_explicitly_synthetic(self):
        self.assertGreaterEqual(len(CASES), 12)
        self.assertTrue(all(c['fictional'] is True for c in CASES))
        self.assertEqual(len({c['id'] for c in CASES}), len(CASES))

    def test_every_declared_case(self):
        for c in CASES:
            with self.subTest(c['id']):
                if 'error' in c['expected']:
                    with self.assertRaises(ProtocolError) as result:
                        run_case(c)
                    self.assertEqual(result.exception.code, c['expected']['error'])
                else:
                    state = run_case(c)
                    for key, expected in c['expected'].items():
                        self.assertEqual(state[key], expected, f"{c['id']}:{key}")

    def test_failed_transition_is_atomic(self):
        for c in CASES:
            if 'error' not in c['expected']:
                continue
            with self.subTest(c['id']):
                model = Model(Message(**c['message']))
                for event in c['events'][:-1]:
                    model.apply(event)
                before = model.snapshot()
                before_now = model.now
                before_pending = dict(model.pending)
                with self.assertRaises(ProtocolError):
                    model.apply(c['events'][-1])
                self.assertEqual(model.snapshot(), before)
                self.assertEqual(model.now, before_now)
                self.assertEqual(model.pending, before_pending)

    def test_no_implicit_comprehension_or_resolution(self):
        for c in CASES:
            if 'error' in c['expected']:
                continue
            with self.subTest(c['id']):
                output = run_case(c)
                ops = {e['op'] for e in c['events']}
                if 'interpret' not in ops:
                    self.assertEqual(output['interpretation'], 'unknown')
                if 'resolve' not in ops:
                    self.assertEqual(output['resolution'], 'unverified')
                if 'ack' not in ops:
                    self.assertFalse(output['acknowledged'])
                if 'action' not in ops:
                    self.assertEqual(output['action'], 'not_reported')

    def test_bad_message_boundaries(self):
        base = CASES[0]['message']
        for invalid in (
            dict(expires_at=0), dict(state_version=True),
            dict(latest_safe_action=101), dict(fallback_available='yes')
        ):
            with self.subTest(invalid):
                with self.assertRaises(ProtocolError):
                    Message(**dict(base, **invalid))

    def test_per_version_cap_cannot_be_bypassed_by_id_reuse(self):
        model = Model(Message(**CASES[0]['message']))
        for event in next(c for c in CASES if c['id'] == 'two_bounded_repairs')['events']:
            model.apply(event)
        event = next(c for c in CASES if c['id'] == 'duplicate_request_id_rejected')['events'][-1]
        with self.assertRaisesRegex(ProtocolError, 'duplicate_request_id'):
            model.apply(dict(event, at=7))


if __name__ == '__main__':
    unittest.main()
