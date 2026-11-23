# MHAC-X008 — execution evidence and exact qualification checkpoint

**23 November 2026 UTC.** Issue [#193](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/193). Scoped branch: mhac-x008/echo-one-witness. The GitHub main SHA observed during reconciliation before edits was **3791929a376ef32e586e50f20c58ba76625fd10f**. Main can change while parallel research continues.

## Source, scope and tool record

AGENTS, RAG, the programme, runbook, repository README and open PR/issue roster were read from live GitHub. This expedition was differentiated from T015's multi-alarm independence, R006's study identity and X004's lexical archaeology. The three public primary/publisher sources and reading extents are given precisely in SOURCES.md. One GPT-6 assistant performed the research, authored code, sound and tests, and self-critiqued; no independent human reviewer or participant was involved.

A local Git clone was attempted but failed due to network DNS resolving github.com. Work was built and tested in a standalone local Python working directory then published through the connected GitHub repository interface; **local tests are not a full local clone's repo-wide validation**. No shared manifests, frozen protocol, accepted claims, R005/R006 identity data or other agents' branches were changed.

## Local execution actually observed

Python standard library commands:

~~~sh
python -m unittest discover -s tests -p 'test_x008_echo_one_witness.py' -q
python research/expeditions/echo-one-witness/echo_lab.py --out generated
~~~

Actual focused unittest output: **19 tests, all OK**, in approximately 2.7–3.0 seconds. An independent iterative closure comparator checked all 2^6 = **64 forward-edge DAGs** on four vertices, with all **15 nonempty output subsets** each = **960 root sets**, and agreed with the recursive DAG oracle. Tests cover refusal of malformed IDs, duplicate sources, duplicate edges, cyclic and self-cyclic provenance, missing parents, partial/untraced ancestry, opposing source polarity, probability bounds, and reproducible waveform structure. Mechanical local success is not scientific validation.

The generator actually wrote: echo.json; independent.json; mixed.json; untraced.json; opposing.json; message_lineage.csv; echo-1-root.wav; eight-independent-roots.wav; RECEIPT.json.

## Synthetic numerical results

| Fictional world | Outward reports | Known unique observation roots | Defective message-count posterior | Root-level posterior under explicitly assumed independence |
| --- | ---: | ---: | ---: | ---: |
| echo | 8 | 1 | 0.9999847414437646 | 0.8 |
| independent | 8 | 8 | 0.9999847414437646 | 0.9999847414437646 |
| mixed | 8 | 2 | 0.9999847414437646 | 0.9411764705882353 |
| untraced | 8 | 1 plus untraced | 0.9999847414437646 | null / refused |
| opposing | 8; one negative | 2 | 0.9997559189650964 | 0.49999999999999994 |

The prior is 0.5; P(positive | H)=0.8; P(positive | not H)=0.2. These are **invented demonstration parameters**. The root-level toy conditions on source observations being independent under both H and not-H, an assumption the provenance graph **does not** establish and cannot certify from IDs. The untraced case abstains from an unsupported root-based posterior.

## Original audio and file provenance

Both original 7.5-second WAV files contain **180,000 samples at 24,000 Hz, 16-bit mono**. The first **5.5 seconds of PCM are exactly byte-identical**; thereafter a one-pulse vs eight-pulse constructed witness-count convention causes different PCM. A listener has not been asked to interpret either sound.

**SHA-256 of generated files, computed in the local execution:**

| File | SHA-256 |
| --- | --- |
| echo-1-root.wav | edad1dcfd9e828c5ec2251ed4eb249adfc2039eacd370669d50f6b0ee674ae4a |
| eight-independent-roots.wav | 44e90399f61779cd060c488c092e6f00668692b5bda7ae86f723fedc4c08b0b0 |
| echo.json | 2d1e338f08b1927c3d5910c8506ef47f77689b0a1852e71b3dacd7f32c49a5f3 |
| independent.json | cbba21281df260fcbf9560f991f34334b7319e0ada013b7cc83cd39a6f7567a5 |
| mixed.json | 546586049ceb8121dd04023fe96d09deda1f5ed4514187eaa523d321c5477929 |
| untraced.json | c6325a83aa00a275998147a0c2b2f8a514a589424ae688998674277ac253b842 |
| opposing.json | 6c9d3639f038d67a10958d6dd5e83b8f13f386477191f8b9671c6b1c76fd7dc4 |
| message_lineage.csv | 8e6abc06a227e62f086d82d1f900b32a7838fa24c3f69a7ed7f2abd28579d715 |

Regenerate with the published Python file to confirm those local hashes; the generator's RECEIPT.json is the authority for any machine-run, not a copied documentation row. Byte-identical PCM does not establish equivalent human experience or a valid semantic codebook.

## GitHub Actions, review and completion gate

**Do not infer hosted CI status from these local tests or from prior MHAC workflow runs.** The exact final PR head must be inspected after publication: required unittest suite, structural validator, deterministic fixture check, legacy status distinction and mergeability. Any later commit invalidates earlier head-level acceptance. Independent scientific/source review and any required owner decision are separate; an all-green mechanical workflow alone does not make the conceptual interpretation true.

Issue #193 remains open and PR should remain Draft until these checks, source limitations, independent review and any necessary authorization have been addressed. No primary-source research corpus promotion, real hardware, real listeners, external correspondence or production TTS were undertaken.
