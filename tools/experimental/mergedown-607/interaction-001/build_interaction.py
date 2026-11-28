"""#607: reconstruct frozen synthetic evidence, retain raw platform outputs.
Run with Python 3.13.5; no external dependencies or source changes.
"""
import hashlib, json, pathlib, shutil, subprocess, sys

FILES = {
    'delayed-status-baseline.wav': '2d6758ba0df07d1df9afdafca0d683f8279002903fb03806221ac74c0ec17134',
    'delayed-status-bound-priority.wav': 'c9a4e27da0decd73bb4b19dafac62f99a1f5e54a78142ecbf0cb7eb08ddeb42c',
    'forward-restored-baseline.wav': '2b6d916f4a16cba654b78c4b24f3ed20463e0eef4138f7b8aea0f41e805bd70e',
    'forward-restored-bound-priority.wav': '2ace16cb2f5b2461cd510a6c41b01ca4834adf8d15d86524d4fa3e2eb131288b',
    'index.html': '04115249c50185a1cb574621adc4ae870a102ed3b476f0293c5591ae3ee02157',
    'receipt.json': '8d1db0bfb48c9d473967842f140b1cda899f84716339651132dc64546571a60d',
}
MANIFEST = 'e619850702050f6cc61091dd350244a67615bfec058ddd7c50540bd1a8f8e505'
AUDIT = '25b3bfeb6e22adcc6237fe3ac155af014b52a68d3cb8d1bfc168f811ebdfaec2'
SOURCES = ('deadline-clarification.py', 'live-clarification.py', 'uncertainty-repair.py', 'check_interaction.py', 'test_check_interaction.py')
def sha(b): return hashlib.sha256(b).hexdigest()
def need(ok, why):
    if not ok: raise ValueError(why)
def canonicalize(raw, dest):
    need({p.name for p in raw.iterdir()} == set(FILES) | {'manifest.json'}, 'raw inventory')
    m = json.loads((raw/'manifest.json').read_bytes())
    need(set(m) == set(FILES), 'raw manifest inventory')
    data = {}; changed = []
    for n,h in FILES.items():
        b = (raw/n).read_bytes(); need(sha(b)==m[n], 'raw hash: '+n)
        c = b.replace(b'\r\n', b'\n') if n.endswith(('.html','.json')) else b
        need(sha(c)==h, 'frozen hash: '+n); data[n]=c
        if c!=b: changed.append(n)
    mb = (json.dumps(FILES,sort_keys=True)+'\n').encode()
    need(sha(mb)==MANIFEST, 'canonical manifest hash')
    # Verify the raw manifest serialization too, not just its mapping.
    need((raw/'manifest.json').read_bytes().replace(b'\r\n',b'\n')==(json.dumps(m,sort_keys=True)+'\n').encode(), 'raw manifest serialization')
    dest.mkdir()
    for n,b in data.items(): (dest/n).write_bytes(b)
    (dest/'manifest.json').write_bytes(mb)
    return changed

def main(source, out):
    need(sys.version_info[:3]==(3,13,5), 'reference Python 3.13.5 required')
    out.mkdir(parents=True)
    package=out/'laboratory'; package.mkdir()
    for n in SOURCES: shutil.copyfile(source/n,package/n)
    readme = source/'README.md'
    if not readme.exists(): readme=source/'README-consolidation.md'
    shutil.copyfile(readme,package/'README.md')
    raw=out/'raw-run1'
    subprocess.run([sys.executable,'-B',str(package/'deadline-clarification.py'),str(raw)],check=True,cwd=package)
    changed=canonicalize(raw,package/'run1')
    audit=subprocess.check_output([sys.executable,'-B','check_interaction.py','.'],cwd=package).replace(b'\r\n',b'\n')
    need(sha(audit)==AUDIT,'independent audit hash'); (package/'audit.json').write_bytes(audit)
    subprocess.run([sys.executable,'-B','-m','unittest','-v','test_check_interaction.py'],check=True,cwd=package)
    receipt={'schema':'mhac.interaction-rebuild/1','platform':sys.platform,'python':sys.version.split()[0],'canonical_files':7,'raw_text_normalized':changed,'audit_sha256':sha(audit)}
    (out/'rebuild-receipt.json').write_bytes((json.dumps(receipt,sort_keys=True,indent=2)+'\n').encode())
    print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__': main(pathlib.Path(sys.argv[1]).resolve(),pathlib.Path(sys.argv[2]).resolve())
