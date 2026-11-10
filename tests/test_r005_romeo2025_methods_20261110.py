"""R005 Romeo 2025 source-boundary fail-closed regression tests."""
import json
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "research/sources/auditory/romeo2025-methods-2026-11-10" / "OBSERVATIONS.json"

def validate(d):
    assert d["issue"] == 5 and d["downstream_issue"] == 6
    assert d["manifestation"]["doi"] == "10.1145/3711938"
    assert d["cross_publication"]["doi"].lower() == "10.1109/ro-man57019.2023.10309631"
    assert d["manifestation"]["doi"] != d["cross_publication"]["doi"]
    assert d["frozen_publication_cutoff"] == "2026-10-04"
    assert d["observer"]["kind"] == "AI_agent" and d["observer"]["independent_human_review"] is False
    assert d["manifestation"]["source_pdf_bytes_retained"] is False
    assert d["manifestation"]["original_sha256_verified"] is False
    assert d["manifestation"]["page_images_verified"] is False
    assert d["manifestation"]["audio_heard"] is False
    assert d["manifestation"]["original_supplement_downloaded"] is False
    assert d["http_response_timestamp_utc"] is None
    ps = d["procedural_observations"]
    assert len(ps) == 2 and {x["code"] for x in ps} == {"PILOT-ONLINE-2025", "MAZE-INPERSON-2025"}
    assert {x["author_reported_recruited_n"] for x in ps} == {50, 60}
    assert all(x["independent_sample_admitted"] is False for x in ps)
    c = d["cross_publication"]
    assert c["participant_nonoverlap_proven"] is False
    assert c["stimulus_nonoverlap_proven"] is False
    assert c["identical_experiments_claimed"] is False
    a = d["admission_boundary"]
    assert all(a[k] == 0 for k in ("canonical_scr_added","canonical_study_added","canonical_experiment_added","canonical_sample_added","new_search_hits_added"))
    assert a["full_text_screening_adjudicated_by_r005"] is False
    assert a["no_study_sample_sum"] is True
    assert all(x["response_bytes_hashed"] is False for x in d["tool_observations"])
    assert len(d["existing_discovery_refs"]) >= 2
    return True

class TestRomeo2025Boundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(P.read_text(encoding="utf-8"))

    def mutate(self, keys, value):
        d = json.loads(json.dumps(self.ledger))
        target = d
        for k in keys[:-1]:
            target = target[k]
        target[keys[-1]] = value
        with self.assertRaises(AssertionError):
            validate(d)

    def test_valid_record(self): self.assertTrue(validate(self.ledger))
    def test_wrong_doi(self): self.mutate(["manifestation","doi"], "10.1109/ro-man57019.2023.10309631")
    def test_falsified_human(self): self.mutate(["observer","independent_human_review"], True)
    def test_fabricated_hash(self): self.mutate(["manifestation","original_sha256_verified"], True)
    def test_fabricated_pdf_bytes(self): self.mutate(["manifestation","source_pdf_bytes_retained"], True)
    def test_fabricated_images(self): self.mutate(["manifestation","page_images_verified"], True)
    def test_fabricated_audio(self): self.mutate(["manifestation","audio_heard"], True)
    def test_fabricated_supplement(self): self.mutate(["manifestation","original_supplement_downloaded"], True)
    def test_invalid_participant_identity(self): self.mutate(["cross_publication","participant_nonoverlap_proven"], True)
    def test_invalid_stimulus_identity(self): self.mutate(["cross_publication","stimulus_nonoverlap_proven"], True)
    def test_invalid_sample_admission(self): self.mutate(["procedural_observations",0,"independent_sample_admitted"], True)
    def test_invalid_experiment_admission(self): self.mutate(["admission_boundary","canonical_experiment_added"], 1)
    def test_invalid_scr_admission(self): self.mutate(["admission_boundary","canonical_scr_added"], 1)
    def test_faked_api_hash(self): self.mutate(["tool_observations",0,"response_bytes_hashed"], True)
    def test_changed_cutoff(self): self.mutate(["frozen_publication_cutoff"], "2026-11-10")

if __name__ == "__main__":
    unittest.main()
