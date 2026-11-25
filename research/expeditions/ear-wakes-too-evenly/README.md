# The Ear That Wakes Too Evenly

25 November 2026 — expedition #604. Synthetic mathematics, engineering hypothesis and original symbolic sound art. Noncanonical; no frozen-protocol amendment, production claim or participant evidence. Authored and self-checked by one ChatGPT agent; no independent human review or claim of mathematical priority.

## The anomaly

A machine emits four consecutive one-slot pulses in every six-slot cycle, then rests for two slots. Its receiver has four listening opportunities per cycle, but the relative integer phase is unknown and fixed. Two receivers use listening sets A={0,1,3,4} and B={1,3,4,5}. A is balanced: its gaps are 1,2,1,2. B is uneven: its gaps are 2,1,1,2. Both guarantee two successful receptions per cycle, the greatest possible minimum. Nevertheless A has a worst inter-reception gap of five slots and B only four. The apparently more even ear has the worse deadline.

| Phase t | A hits relative to transmit window | B hits | A cyclic gap | B cyclic gap |
|---:|---|---|---:|---:|
| 0 | 0,1,3 | 1,3 | 3 | 4 |
| 1 | 0,2,3 | 0,2,3 | 3 | 3 |
| 2 | 1,2 | 1,2,3 | 5 | 4 |
| 3 | 0,1,3 | 0,1,2 | 3 | 4 |
| 4 | 0,2,3 | 0,1,3 | 3 | 3 |
| 5 | 1,2 | 0,2 | 5 | 4 |

An opportunity to receive is not the same thing as an actual receipt; the count of actual receipts is not the maximum time between them. An evenly distributed availability schedule can interact badly with another agent's unavailable interval.

## Source encounters and scope

* Sangil Choi, Wooksik Lee, Teukseob Song and Jong-Hoon Youn (2015), [Block Design-Based Asynchronous Neighbor Discovery Protocol for Wireless Sensor Networks](https://doi.org/10.1155/2015/951652), Journal of Sensors, article 951652. Publisher HTML read: abstract, introduction, §2, §3 opening, §3.1 definitions 1–2, §3.2 opening definitions; §4.4 worst-case latency discussion also retrieved. The source studies binary sleep/awake schedules and simultaneous availability, and uses block designs for bounded discovery latency. Its symmetric/multinetwork problems and reported performance are not our proof or measured acoustic results.
* S. Chen, R. Morillo, Y. Qin, A. Russell, R. Jin, B. Wang and S. Vasudevan (2020), [Asynchronous Neighbor Discovery on Duty-Cycled Mobile Devices: Models and Schedules](https://doi.org/10.1109/TWC.2020.2990764), IEEE Transactions on Wireless Communications 19(8), 5204–5217. [Institutional abstract](https://scholarlyworks.adelphi.edu/esploro/outputs/journalArticle/Asynchronous-Neighbor-Discovery-on-Duty-Cycled-Mobile/991004359586506266) read, not full text. The authors explicitly distinguish discrete and continuous schedules and report advantages of the latter in their model. This is a contrary constraint against extrapolating our integer-slot theorem into actual hardware.
* S. Masih Ayat, S. Majid Ayat and Meysam Ghahramani (2020), [The independence number of circulant triangle-free graphs](https://doi.org/10.3934/math.2020242), AIMS Mathematics 5(4), 3741–3750. Publisher metadata and abstract read only. A discovery lead for graph-independence optimization, not a premise of the exact special cases below; their triangle-free restriction need not hold for our graphs.

Access date 25 November 2026; agent-mediated web reading, no restricted source bytes retained. The mathematical arguments below are self-contained elementary constructions. These source encounters are not comprehensive novelty or evidence screening. The existing #294 investigates allocation of phase correction and reachable meeting times; #540 studies exclusive voice allocation and contiguous non-sounding windows. Their issue bodies, comments and expedition reports were inspected. This expedition fixes phase and optimizes one-way reception, not convergence or human rest.

## Formal contract and sharp count theorem

Let N>=2, 1<=a<=N, and B a subset of the cyclic group Z_N of size b (0<=b<=N). Transmitter is active in slots A=[0,a-1] each period. Receiver is active at i when i+t belongs to B modulo N, with an unknown fixed phase t. The hit set is H_t=A intersect (B-t). A hit is an ideal instantaneous receipt; no collisions, physical packet length, interference, gain error, drift, switching cost or acknowledgement delay are modeled.

Summing |H_t| over all N phases counts every active transmitter slot against all b receiver slots exactly once. Thus min_t |H_t| <= floor(ab/N). For the mechanical mask whose bit at i is floor((i+1)b/N)-floor(ib/N), extended periodically, every length-a circular window has count floor(ab/N) or ceil(ab/N) by telescoping. Therefore the exact optimum over listening masks is floor(ab/N), including b=0. With at most e periodic erasures of hits, at least one receipt per period for all phases is possible exactly when ab>=N(e+1). For e>=a this is impossible. The count result assumes a contiguous transmitter window. For A={0,1,3} in Z_6 and b=2, A-A contains all residues, so the two translates used to cover phases overlap. Since they have total size six, they cannot cover all six phases. All fifteen receiver pairs fail despite ab=N; the JavaScript census checks this.

## Deadline certificates: a hypergraph hidden in the off-window

Define G_e(B) as the worst cyclic inter-reception gap over all phases and all periodic deletion patterns of at most e distinct hits per period, with infinity if a phase can be completely erased. Equivalently, for 1<=G<=N, G_e<=G exactly when every cyclic G-slot window, at every phase, contains at least e+1 original hits. Necessity: delete all hits of a failing window, repeat each period; sufficiency: every such window still has a hit. The same guarantee holds under a rolling budget of at most e erased hit occurrences in every N consecutive slots; periodic attacks still attain the bound. An aligned disjoint-period budget alone is weaker (see limits). A gap of G means every G consecutive slots contains a hit, not a continuous-time physical latency guarantee.

For fixed phase with k>e ordered hits h_0<...<h_{k-1}, extend h_{j+k}=h_j+N. Its worst gap is max_j(h_{j+e+1}-h_j): remove the e intervening hits, or observe that any consecutive survivors skip at most e. If k<=e the result is infinite. This supplies a direct executable oracle.

Let G=N-a+s with 1<=s<=a. Every G-window overlaps A in at least s slots. Define the s-element shapes

    Q_u = [0,u-1] union [a-(s-u),a-1],  u=0,...,s,

with empty intervals omitted. They are exactly the minimum-overlap intersections obtained by taking a G-window containing the transmitter's entire off interval and u active slots on one side, s-u on the other. When a=N, they are ordinary circular intervals. Any larger intersection is either contiguous or a prefix-plus-suffix of A. In the first case it contains a translate of a consecutive s-slot shape; in the second it contains a Q_u by choosing u appropriately. Unknown receiver phase permits all translations in either case. Thus:

    G_e(B) <= N-a+s
    iff every translate of every Q_u contains at least e+1 points of B.

This is an exact hypergraph covering certificate. It avoids searching individual deletion patterns, and the shapes can be tested by bit rotations. The equivalent holes contract, C=Z_N minus B, is at most s-e-1 holes in each translated Q_u. If s<=e, even full listening fails. If s=e+1, all translated minimum shapes must be fully listened to; their union covers Z_N. Therefore the physical-blackout lower bound G_e>=N-a+e+1 is attained precisely by b=N, provided e<a. For e>=a no finite guarantee is possible.

For the zero-erasure extended census only, the maximum over phases of the wrap gap N-(last-first) already dominates internal gaps. Indeed if some consecutive receiver positions have circular separation d, start a transmitter window immediately after the earlier receiver position. If d>a the window is empty; otherwise its first hit is d-1 slots after its start, and its wrap gap is at least N-a+d. This dominates d. Every internal hit gap is one of these receiver gaps. Hence maximizing wrap gaps over all phases is exact; this supports the C++ bitboard acceleration, not an assumption of balanced gaps.

## One extra slot of latency becomes graph independence

Take s=e+2<=a: the receiver permits exactly one slot of slack beyond the full-listening optimum. The hypergraph rule becomes at most one hole per shape. Pairs of slots co-occurring in a Q_u have positive clockwise separation in

    F = {1,...,s-1} union {a-s+1,...,a-1}.

Proof: within either contiguous part the separation is at most s-1; across the two end parts, the minimum separation is a-s+1 and the maximum a-1. All such distances occur, using the contiguous or split shapes. Conversely no other distances occur before reducing modulo N. With all translations the holes must be independent in the circulant graph on Z_N with undirected edges at differences plus/minus F. The exact minimum listening budget is therefore N-alpha(graph), where alpha is its independence number. This reformulates a deadline specification into a graph compiler. No efficiency claim is made for arbitrary graph instances.

The first interval of forbidden separations forces cyclic gaps between holes to be at least s. Hence at most floor(N/s) holes. If s divides both N and a, holes at every s-th position attain the bound: no forbidden difference is a multiple of s. If s divides N but not a, and one attempts N/s holes, every gap must be exactly s. The second forbidden interval contains a multiple of s, contradicting independence. The listening budget must strictly exceed N-N/s. Thus arithmetic compatibility matters even at identical duty ratios.

Two sharp families at e=0:

* a=3 (N>=3): forbidden distances 1 and 2. Every hole gap is at least 3, so alpha=floor(N/3). Equally spaced holes with gaps 3 except a final remainder attain it. Minimum b=N-floor(N/3) at G=N-1.
* a=4 (N>=4): forbidden distances 1 and 3. For even N, all holes in one parity class attain alpha=N/2. For odd N, floor(N/2) holes would force all gaps 2 except a single gap 3, which is forbidden. The attainable optimum is (N-3)/2: arrange gaps 2 except one gap 5 (for N=5, a single hole). No directed distance 3 can arise from these gaps. Minimum b=N-(N-3)/2 for odd N, or N/2 for even N, at G=N-2. This is the exact parity-dependent duty budget.

For N=6,a=4, absolute optimum G=3 would require listening continuously. At b=4, an uneven mask achieves G=4, proving its optimum. The balanced mask gives G=5, despite count optimality. This falsifies the tempting conjecture that mechanical masks minimize latency whenever they maximize guaranteed overlap.

## Computation and unresolved conjecture

Run the standard-library native Python laboratory with assertions enabled:

    python laboratory.py > execution.json

The program enumerates every marked listening mask for N=2..11, all transmitter interval lengths, every phase, e=0..min(2,a-1). It compares the explicit consecutive-survivor oracle to the hypergraph rule, checks graph independence and density theorems, and separately enumerates literal deletion subsets for N<=7. It also renders and reads back the original PCM. Python 3.13.5, two runs with byte-identical JSON and WAV hashes. 40,960 mask/window profiles; 110,604 fault certificates; 98,332 graph certificates; 3,852 explicit-deletion checks; 570 duty-budget profiles; 32 mechanical-mask latency failures. The native source and corrected receipt were checked against exact Git blob hashes.

Run the independent-method JS (same author):

    node crosscheck.cjs

It uses forward scanning of every possible window start, phase and length, rather than computing consecutive-hit gaps or minimum shapes. Tested in the tool's JS runtime across N=2..10: 18,432 profiles, 49,164 fault checks, 43,036 graph checks, 438 budget profiles, 20 balanced failures, 15 failed noncontiguous receiver pairs. No assertion failures. The native count of balanced failures through ten agrees (1+2+3+5+9=20). No claim of independent peer review.

The C++ extension uses the proved zero-erasure wrap-gap reduction and bitboards, compiled and run locally:

    g++ -O3 joint.cpp -o joint
    ./joint > joint-execution.txt

All N=2..20, all masks, interval lengths and phases (with safe early exit on a zero-hit phase): 39,845,888 mask/window profiles and 3,078 budget profiles. It found 416 budgets in which the mechanical mask is not latency optimal, but **zero** budgets where no mask simultaneously attains optimal guaranteed count and optimal worst gap. This suggests the separate conjecture that a jointly optimal mask always exists. It is not proved. We explicitly distinguish failure of one canonical construction from an inherent tradeoff between objectives. The extension's balanced-failure counts agree with the other programs over their overlap. The zero-failure observation is finite evidence, not a general theorem.

Receipts: execution.json, crosscheck-execution.json, joint-execution.txt. Infinity is represented in program outputs by sentinel N+1. All enumerations are deterministic synthetic calculations, not empirical reliability statistics.

## Original score: The Window Organ

Four 3-second stereo PCM16 files are generated locally by laboratory.py (8 kHz; four repetitions of six slots, each 125 ms). Left channel is the fixed transmitter voice (360 Hz); right is actual model receipts (600 Hz); each pulse uses a squared-sine envelope and the same peak coefficient. Balanced-phase-2 vs uneven-phase-2 expose the 5 vs 4 gap; balanced-phase-0 vs uneven-phase-0 reverse the local ordering (3 vs 4). The transmitter channel is sample-identical in all four; the different number of right-channel pulses is intentional. Equal availability count is not equal received energy, and the renderer makes no claims about perceived loudness. The score is a synthetic symbolic sonification, not acoustic packet acquisition or a calibrated psychophysical stimulus.

An original interactive musical proposal: one performer controls a contiguous emission aperture; another chooses the receiver's wake pattern with fixed budget; a third turns a hidden phase dial and deletes receipt opportunities. Audition requested and actually received notes separately. A display should distinguish minimum count, worst gap and the phase attaining each. The musical constraint is to keep the duty budget fixed while shortening the longest absence of a reply. A silence could represent sleep, a failed opportunity, or genuine absence of an emission; the ordinary mono sound does not resolve these causal alternatives. The complete live instrument is not implemented.

## Limits, contrary cases and exaptation

This is an ideal one-way slot model; no acknowledgment, contention or payload decoding. If phase can change arbitrarily at every slot and B is not full, an adversary can always align a receiver hole with the currently active transmitter. Equal nominal periods alone do not secure the fixed-phase guarantee. An aligned-period deletion budget can also break the rolling-window latency theorem: with N=6 and hits at slots 1,3, erase time 3 in one cycle and time 7 in the next. One erasure per aligned cycle is satisfied, yet surviving times 1 and 9 have gap 8, larger than the periodic one-erasure bound 6. For such a contract one must analyze cross-boundary erasures rather than transplant the formula.

Conventional duty-cycle scheduling and combinatorics explain the mathematical anomaly without an extra cybersemiotic explanatory mechanism. The design hypothesis is that an explicit machine interface could report *availability*, *actual reception*, *guaranteed receipt count* and *maximum unacknowledged interval* separately. It could be tested first in an offline synthetic packet simulator with clock drift, jitter, packet duration and transition costs, comparing mechanical masks, optimized masks, an always-on baseline and ordinary scheduling. A later human study would need separate authorization and measure interpretation and task performance; a machine listening slot is not a human attentional state. It is not established that any cue is universally meaningful or that it reduces affect or cognitive load.

Fictional afterword: a clerk opens four shutters every six beats. He has arranged them as evenly as possible. His apprentice moves one shutter next to another, leaving a larger silence elsewhere. The messages arrive with a shorter longest wait. The clerk's ledger is correct; its measure of equality was simply not a measure of waiting.

## Checkpoint

Base main 495a98ca12bae467a507031f04931aa4254b1866; issue #604 created and empty comments fetched; fresh branch mhac-604/ear-wakes-too-evenly. Read AGENTS, README, RAG, programme, runbook, integrity, validation and research workspace. Inspected 100 recent open issues, 100 open PR search results, 362 branch entries across pages (live inventory may change), and targeted searches for difference sets, cross-correlation, rendezvous, asynchronous scheduling, cyclic shifts, turn-taking and related topics. Previous expedition #601 exact-head workflow 45678768419 succeeded. No shared manifest or other active branch modified. Git native checkout failed DNS; standalone native tests were executed, full repo tests not run locally. Draft for integration and independent critique; no scientific acceptance, protocol promotion, human or hardware validation. Review and exact-head CI remain required; use Refs, not Closes.
