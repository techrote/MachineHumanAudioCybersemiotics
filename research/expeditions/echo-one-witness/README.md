# MHAC-X008 — The Echo of One Witness

**[Expedition issue #193](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/193)** · Original critical synthesis, finite proof, typed synthetic ancestry experiment and original PCM sonification.

> Eight audible messages are not necessarily eight independent observations.

This project asks what happens when one source is repeated across a research corpus, agent reports or machine utterances, and the repeated outputs begin to look like independent corroboration. It is not an allegation that MHAC has in fact committed source laundering, a real listener study, an accepted Track E/G result, or a request for a production alarm subsystem.

## Artifact inventory

| Artifact | Purpose |
| --- | --- |
| [THEORY.md](THEORY.md) | Proof of output-level provenance aliasing, source vs message cardinality, Bayesian counterexample, direct opposing cases, Brier subtraction |
| [SOURCES.md](SOURCES.md) | Actual publisher/organization reading extent, provenance and limitations |
| [ADVERSARIAL.md](ADVERSARIAL.md) | Eighteen targeted objections and refusal conditions |
| [TRANSFER.md](TRANSFER.md) | Proposed opt-in provenance envelope and the cheaper no-corroboration alternative |
| [AFTERWORD.md](AFTERWORD.md) | Fictional original philosophical afterword, explicitly not evidence |
| [echo_lab.py](echo_lab.py) | Standard-library declared provenance DAG and cycle guards, likelihood toy, exact generated WAV/JSON/CSV receipts |
| [tests/test_x008_echo_one_witness.py](../../../tests/test_x008_echo_one_witness.py) | 19 local tests, including 960 exhaustive small-DAG ancestry comparisons and reproducible PCM structure |
| [EVIDENCE.md](EVIDENCE.md) | Executed commands, observed results, hashes, CI/review status and limits |

## Reproduce

Python 3.11 or newer, standard library only. From the repository root:

~~~sh
python -m unittest discover -s tests -p 'test_x008_echo_one_witness.py' -v
python research/expeditions/echo-one-witness/echo_lab.py --out build/mhac-x008
~~~

The second command creates **disposable** generated material in build/mhac-x008:

- Five fictional scenario JSONs (echo, independent, mixed, untraced and opposing).
- A CSV showing each message's declared transitive observation roots.
- Two 7.5-second original PCM16 mono WAV files at 24 kHz. Their first 5.5 seconds are precisely byte-identical: eight outward sonic reports in each. Only afterward is the made-up root-count code different (one pulse vs eight).
- RECEIPT.json containing SHA-256 digests and the equality assertion.

The program is a *toy accounting and sound instrument*, not an authenticated provenance pipeline, human-validated codebook or sensor calibration.

## Nonduplication and source boundaries

[T015 #58 / PR #59](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/59) already tests false corroboration and suppression for concurrent alarms; **this expedition does not reimplement those policies**. [R006 #6](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/6) owns actual study/publication/sample identities, and [X004 #184](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/184) studies lexical sediment; neither is modified here. Our new axis is a claim's **transitive declared evidential ancestry**, which cannot be inferred from lexical similarity, number of messages or root IDs alone.

A **negative result is acceptable**: simply declining unsupported claims of “independent confirmation” may be better than narrating lineage to a person under an audio deadline. No human gate was opened or silently bypassed. There are no production voice-engine, participant recruitment, real device, source-rights, core registry or protocol changes.

## Most important caution

**Different root IDs do not prove conditional statistical independence.** Without a credible model of the joint observation process, counting unique roots is an audit aid only. See [THEORY.md](THEORY.md) and [ADVERSARIAL.md](ADVERSARIAL.md) before citing the probability numbers as evidence.
