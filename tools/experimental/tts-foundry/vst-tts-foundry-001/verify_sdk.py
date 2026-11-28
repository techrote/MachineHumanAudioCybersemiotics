#!/usr/bin/env python3
import pathlib, subprocess, sys
ROOT='9fad9770f2ae8542ab1a548a68c1ad1ac690abe0'
PINS={'base':'3d2e82f8e6bff59c1d8b7a27491a29c2286b5206','cmake':'de6e54eeaaab35b7145f5c32c279b5e892146e04','doc':'6d4737c9e70750056e731d88d49aa06eefc8a1a4','pluginterfaces':'31d6eeba6daaa3e2a8bfbe3e7a90ca0b7fbfbc1c','public.sdk':'a3911a4615dabbfdfd9d181ee26b05c70c289a95','tutorials':'33b73dfbb87f3fde3bce8c0a10cae934dc66ad34','vstgui4':'76823bdbe286e4bdb9f79ab8986af5ce7202336c'}
def git(path,*args):return subprocess.check_output(['git','-C',str(path),*args],text=True).strip()
root=pathlib.Path(sys.argv[1]).resolve()
assert git(root,'rev-parse','HEAD')==ROOT
for name,sha in PINS.items():assert git(root/name,'rev-parse','HEAD')==sha,(name,git(root/name,'rev-parse','HEAD'))
assert not git(root,'status','--porcelain','--untracked-files=all','--ignore-submodules=none')
print('VST3 SDK 3.8.0 build 66 provenance PASS')
