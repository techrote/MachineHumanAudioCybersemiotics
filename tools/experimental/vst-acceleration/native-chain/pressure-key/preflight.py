"""Verify and extract the three original, exact Windows packages for SDK replay."""
import argparse
import importlib.util
import json
from pathlib import Path

PINS = (
    (15268476929,'9cc02bb443694bb9e38eef3083322876af242a8166ba71a0385904c08ca5dffc','25ca01e644c4389078f0e7d7d8446f99e588fa9f','MHACOrbitLantern','24C15B793B8C4F4B98275F233EE969C4','0.5.0','ed4e8d1e79334a76e5d53ac4c96de9a226d025a5913c65478015a125968de1db'),
    (15268772488,'205cf432490c8b3f3c578f405c1d073d3894f32ac1498224097ff7a7daabadc2','6665b5475e87384f8f36862f0adbb879ecfaf3ec','MHACHarmonicMemoryBank','AE00577BADF94D9C8F2FB9D04991475C','0.4.0','c38a604e520788fcc9c5e000f2c96c3f3cb7263e76c6b5255a1503543283ef2e'),
    (15248002499,'369ec7afe0163626fd4d13c06f469984547e04f5f0b5fe52de3c4f3a45295217','b5f509eb5c857dc6e411a7718bdc40dfa09bb0ad','MHACPalimpsestShuttle','58F3C28ABA5142D1AF75DF83173B962E','0.2.0','fe2caece775dcf76b65fcc24082e284c96b487580d16652581e3973d9df5e59b'),
)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ('orbit','bank','shuttle','out'):
        parser.add_argument('--'+arg, type=Path, required=True)
    a = parser.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    report = dict(status='started', packages=[])
    def persist():
        (a.out/'packages.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    try:
        spec = importlib.util.spec_from_file_location('prior',Path(__file__).resolve().parent.parent/'constellation-chain'/'constellation_host.py')
        prior = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(prior)
        for path,pin in zip((a.orbit,a.bank,a.shuttle),PINS):
            _,row = prior.extract(path,pin,a.out/'modules')
            prior.require(not row['metadata_mismatch'],'module/class version mismatch')
            report['packages'].append(row)
            persist()
        report['status']='pass'
        print('PRESSURE_KEY_PACKAGES_PASS packages=3')
    except Exception as exc:
        report.update(status='fail',error=str(exc))
        raise
    finally:
        persist()

if __name__ == '__main__':
    main()
