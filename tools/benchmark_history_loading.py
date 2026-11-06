"""Measure the current offline snapshot loader against one immutable local base.

Run this same script in the before/after checkouts with PYTHONPATH=. to compare
snapshot hashes and Git-process counts. Timing is descriptive, not a CI threshold.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
from pathlib import Path
import platform
import subprocess
import time
from unittest.mock import patch

from tools.record_io import dumps
from tools import records


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path.cwd())
    parser.add_argument('--ref',required=True,help='Full pre-fetched immutable commit SHA')
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    original=subprocess.run;calls=0
    def counted(*a,**kw):
        nonlocal calls
        calls+=1
        return original(*a,**kw)
    with patch.object(records.subprocess,'run',side_effect=counted):
        start=time.perf_counter();snapshot=records.snapshot_from_git(args.root,args.ref)
        elapsed=time.perf_counter()-start
    report={
        'artifact_kind':'offline_history_loader_measurement',
        'measured_at':datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),
        'base':args.ref,'elapsed_seconds':elapsed,'git_processes':calls,
        'record_count':len(snapshot['records']),
        'snapshot_sha256':hashlib.sha256(dumps(snapshot).encode()).hexdigest(),
        'loader_source_sha256':hashlib.sha256(Path(records.__file__).read_bytes()).hexdigest(),
        'python':platform.python_version(),
        'git':subprocess.check_output(['git','--version'],text=True).strip(),
        'limitations':'Single local elapsed-time observation; caches and concurrent load uncontrolled. No scientific acceptance or CI timing threshold.'}
    text=dumps(report)
    if args.report:args.report.write_text(text,encoding='utf-8')
    print(text,end='')


if __name__=='__main__':main()
