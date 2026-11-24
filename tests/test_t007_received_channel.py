"""Synthetic-only MHAC #41 adversarial replay; never claims listener outcomes."""
import json
import sys
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / 'research' / 'tangents' / 'received-channel'
sys.path.insert(0, str(MODULE))
import model
import generate


class ReceivedChannelCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = model.load('CUES.json')
        cls.cues = {c['id']:c for c in cls.config['cues']}
        cls.transforms = {t['id']:t for t in model.load('TRANSFORMS.json')['transforms']}
        cls.results = model.run_all()

    def record(self, transform, cue):
        return self.results['runs'][transform][cue]

    def feat(self, transform, cue, key):
        return self.record(transform,cue)['features'][key]

    def test_all_25_adversarial_cases(self):
        cases=model.load('CASES.json')['cases']
        self.assertGreaterEqual(len(cases), 16)
        self.assertEqual(len(cases),len({c['id'] for c in cases}))
        for c in cases:
            with self.subTest(case=c['id']):
                kind=c['test']; t=c.get('transform'); cue=c.get('cue'); a=c.get('left'); b=c.get('right')
                if kind=='truth_invariant':
                    self.assertEqual(self.record(t,cue)['metadata'],
                        {k:self.cues[cue][k] for k in model.SEMANTIC_FIELDS})
                elif kind=='repeatable':
                    raw=model.synthesis(self.cues[cue],8000,800)
                    y,_=model.apply(raw,self.transforms[t],8000)
                    self.assertEqual(model.waveform_sha(y),self.record(t,cue)['waveform_sha256'])
                elif kind=='gain_normalized':
                    for field in ('pulse_groups_proxy','active_frame_fraction','crest_factor','high_low_projection_db','interaural_level_db'):
                        x,y=self.feat('identity',cue,field),self.feat(t,cue,field)
                        if x is None or y is None:
                            self.assertIsNone(x); self.assertIsNone(y)
                        else: self.assertAlmostEqual(x,y,places=4)
                elif kind=='spatial_collapse':
                    self.assertIsNone(self.feat(t,a,'interaural_level_db'))
                    self.assertIsNone(self.feat(t,b,'interaural_level_db'))
                    self.assertEqual(self.record(t,a)['waveform_sha256'],self.record(t,b)['waveform_sha256'])
                    self.assertIsNone(self.results['pairwise'][t][a+'|'+b]['interaural_level_db'])
                elif kind=='spatial_separated':
                    self.assertGreater(self.feat(t,a,'interaural_level_db'),10)
                    self.assertLess(self.feat(t,b,'interaural_level_db'),-10)
                    self.assertGreater(self.results['pairwise'][t][a+'|'+b]['interaural_level_db'],20)
                elif kind=='mute_collapse':
                    self.assertEqual(self.record(t,a)['waveform_sha256'],self.record(t,b)['waveform_sha256'])
                    self.assertEqual(self.feat(t,a,'rms'),0)
                elif kind in ('mute_undefined','no_silent_zero_ild'):
                    for field in ('interaural_level_db','active_frame_fraction','high_low_projection_db'):
                        self.assertIsNone(self.feat(t,cue,field))
                elif kind=='spectral_separation':
                    self.assertLess(self.feat(t,a,'high_low_projection_db'),-100)
                    self.assertGreater(self.feat(t,b,'high_low_projection_db'),100)
                elif kind=='lowpass_high_attenuation':
                    gain_low=self.feat(t,a,'rms')/self.feat('identity',a,'rms')
                    gain_high=self.feat(t,b,'rms')/self.feat('identity',b,'rms')
                    self.assertGreater(gain_low,gain_high)
                elif kind=='reflection_tail':
                    self.assertGreater(self.feat(t,cue,'active_frame_fraction'),self.feat('identity',cue,'active_frame_fraction'))
                elif kind=='masker_tail':
                    self.assertEqual(self.feat('identity',cue,'tail_rms'),0)
                    self.assertGreater(self.feat(t,cue,'tail_rms'),0)
                elif kind=='nonmonotonic_gate':
                    self.assertLess(self.feat(t,cue,'tail_rms'),self.feat('identity',cue,'tail_rms'))
                    self.assertLess(self.feat(t,cue,'pulse_groups_proxy'),self.feat('identity',cue,'pulse_groups_proxy'))
                elif kind=='compression_peak':
                    self.assertLess(self.feat(t,cue,'peak'),self.feat('identity',cue,'peak'))
                elif kind=='compression_distinct':
                    self.assertNotEqual(self.feat(t,cue,'rms'),self.feat('fast_compression',cue,'rms'))
                elif kind=='unknown_transform_error':
                    raw=model.synthesis(self.cues[cue],8000,800)
                    with self.assertRaises(ValueError):
                        model.apply(raw,{'kind':'imaginary_hearing_aid'},8000)
                elif kind=='pulse_divergence':
                    self.assertNotEqual(self.feat(t,a,'pulse_groups_proxy'),self.feat(t,b,'pulse_groups_proxy'))
                elif kind=='rank_reversal':
                    key=c['axis']
                    def signed_gap(transform):
                        anchor=self.feat(transform,cue,key)
                        return abs(anchor-self.feat(transform,a,key))-abs(anchor-self.feat(transform,b,key))
                    self.assertLess(signed_gap('identity')*signed_gap(t),0)
                elif kind=='cross_axis_non_equivalence':
                    diff=self.results['pairwise'][t][a+'|'+b]
                    self.assertEqual(diff['pulse_groups_proxy'],0)
                    self.assertGreater(diff['interaural_level_db'],20)
                else: self.fail('Unrecognized case kind: '+kind)

    def test_generated_tables_match(self):
        generate.generate(check=True)

    def test_fictional_semantics_not_encoded_by_waveform(self):
        c=self.cues['P_FAST'].copy()
        before=model.waveform_sha(model.synthesis(c,8000,800))
        c.update(source_id='other-source',truth_status='contrary-hypothetical',action_id='do-nothing')
        after=model.waveform_sha(model.synthesis(c,8000,800))
        self.assertEqual(before,after)

    def test_invalid_cue_or_transform_is_not_silently_accepted(self):
        raw=model.synthesis(self.cues['P_FAST'],8000,800)
        with self.assertRaises(ValueError):
            model.apply(raw,{'kind':'medical_device'},8000)
        with self.assertRaises(KeyError):
            model.synthesis({'kind':'continuous'},8000,800)

    def test_fixture_invariants(self):
        self.assertEqual(len(self.cues),10)
        self.assertEqual(len(self.transforms),10)
        self.assertEqual(self.config['synthesis_seed'],0)
        self.assertEqual(self.config['sample_rate_hz'],8000)
        self.assertEqual(self.config['duration_ms'],800)
        for cue in self.cues.values():
            self.assertEqual(cue['truth_status'],'hypothetical')

    def test_pairs_have_undefined_not_zero_for_missing_spatial_axis(self):
        pair=self.results['pairwise']['mono']['S_LEFT|S_RIGHT']
        self.assertIsNone(pair['interaural_level_db'])
        self.assertEqual(pair['pulse_groups_proxy'],0)


if __name__=='__main__':
    unittest.main()
