# Computational material for When Laws Collide

Repository: https://github.com/pstanica/TFF-SUMO-ProjectsFiles

Keep the files together in one directory. The Python scripts use Python 3.9
or later and the standard library. Run them without Python's -O option,
because their verification checks use assertions.

## Files and their purpose

| File | Purpose |
| --- | --- |
| ModalVFest.tex | Manuscript with repository references and measurements matched to the included logs. |
| naval_binary.tff | Three-world binary-topic instance. |
| naval_operations_scenario.tff | Scenario input with 46 active axioms and active Q4 conjecture. |
| naval_operations_corrected.tff | Finite guarded maximal-agreement instance with 44 axioms and a twelve-part conjecture. |
| verify_policy.py | Checks 18,282 policy classifications over 242 strict orders on one to four authorities and the explicit binary naval interpretation. |
| check_supplied_tff.py | Evaluates the scenario axioms in the two Q4 witnesses and an inactive-source example, then checks all finite policy axioms and its conjecture. Keep this script. It is also imported by two other scripts. |
| check_vampire_log.py | Matches the logged conjecture and 26 used input axioms to the finite TFF input, checks the recorded proof endpoint, and reads the scenario timeout statistics. |
| convert_original_to_smt2.py | Generates the unrestricted SMT-LIB scenario translation with the active conjecture negated. |
| naval_operations_original.smt2 | Generated scenario translation. |
| make_q4_witness.py | Generates the fixed finite Q4 countermodel check from the parsed scenario axioms. |
| naval_q4_countermodel_check.smt2 | Grounded axioms and negated Q4 with 318 fixed Boolean predicate values. |
| vampire_corrected.log | Recorded Theorem result and proof for the finite policy input, 175.412 seconds and 217 MB. |
| vampire_scenario_original.log | Recorded scenario saturation timeout, 1,000 seconds and 1,422 MB. The log contains no embedded input or conjecture. |
| z3_original.log | Recorded unknown result for quantified scenario search, 600.55 seconds and 993.48 MB. |
| z3_countermodel.log | Recorded sat result for the fixed finite witness check, 0.01 seconds and 18.51 MB. |
| Verification.txt | Results of the checks performed when assembling this package. |
| SHA256SUMS | Digests of the other packaged files. |

## Run the Python checks

```sh
python3 verify_policy.py
python3 check_supplied_tff.py
python3 check_vampire_log.py
```

The TFF evaluator supports the fragment in these inputs. It is not a general
TFF parser or theorem prover. The Vampire log checker verifies input
correspondence and the recorded endpoint, not the validity of every proof
inference. The finite policy interpretation check and the policy enumeration
supplement the manuscript's proofs.

## Regenerate the SMT-LIB inputs

```sh
python3 convert_original_to_smt2.py naval_operations_scenario.tff regenerated_scenario.smt2
python3 make_q4_witness.py
```

The first command should reproduce naval_operations_original.smt2 byte for
byte. The second writes naval_q4_countermodel_check.smt2 and should reproduce
the included file byte for byte. These checks were performed for this package.
The scripts retain the existing filenames so that the generators, inputs,
and logs can be matched directly.

## Optional solver runs

With Z3 installed:

```sh
z3 naval_q4_countermodel_check.smt2
z3 naval_operations_original.smt2
```

The fixed witness check should return sat. The quantified problem sets a
600-second timeout and may return unknown. A successful witness check verifies
a specified finite model rather than searching all models. Solver versions,
hardware, and execution settings affect runtimes.

With the user's Vampire executable installed:

```sh
vampire-main -t 1000 naval_binary.tff
vampire-main -t 1000 naval_operations_corrected.tff
vampire-main -t 1000 naval_operations_scenario.tff
```

These are suggested fresh commands. The full commands and hardware for the
archived runs were not recorded. The Vampire logs identify version 5.0.0,
release commit b56c5534b. The Z3 logs do not identify a solver version.
A scenario timeout establishes neither Q4 nor its negation. The two explicit
models checked by check_supplied_tff.py establish non-entailment in both
directions. The scenario Vampire log does not itself certify which input was
used, so its filename attribution must not be treated as an input certificate.

## Build the manuscript

```sh
pdflatex ModalVFest.tex
pdflatex ModalVFest.tex
```

The source requires a LaTeX installation with the packages declared in its
preamble. Generated PDF and LaTeX build intermediates are not included.

## Limits of the available material

The separate Q1-Q4 per-query proof outputs and exact execution commands are
not present in the supplied package. The six frame-test input files and proof
outputs are also absent. Their table entries remain explicitly reported
observations in the manuscript and cannot be reproduced from this package.
No files have been invented to stand in for those missing records.

The archive omits duplicate subdirectories, operating-system metadata,
internal review notes, redundant editorial verification reports, and an
outdated manuscript/PDF copy. All four supplied solver logs are preserved
byte for byte. The TFF files and both generated SMT-LIB inputs are unchanged.
The log checker reads the actual scenario statistics instead of printing
hard-coded values that differ from the included log.

For a publication snapshot, record the Git commit containing this package.
SHA256SUMS fixes the bytes distributed here. On systems with sha256sum, use
sha256sum -c SHA256SUMS. On macOS, use shasum -a 256 -c SHA256SUMS.
