# A3 Attack-Validity Duplicate Audit

The raw `results/A3_attack_validity.csv` contains 4,320 rows. The frozen grid
has 3,456 expected rows (four regimes times 864). A shell start-up mistake ran
the 60-dimensional, redundancy 0.1, label-noise 0.15 regime twice.

The extra 864 rows are exact duplicates across every result column and every
protocol/method combination. They are preserved in the raw file as an execution
audit trail. `results/A3_attack_validity_canonical.csv` removes only these exact
duplicate rows and is the sole file used for the statistical decision. No
distinct seed, target release, or experimental outcome was removed.
