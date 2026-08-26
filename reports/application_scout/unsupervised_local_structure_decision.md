# Unsupervised Local-Structure Reopen Test

## Protocol

No label, purity, entropy, class count, or reliability score enters the recursive
ball cover. APS uses a label-free uniform 12,000-row representation subset. A
KMeans cover with the exact same region count receives the same feature schema
and downstream model budget.

Region-count match: **True**.

## Matched Macro-F1 deltas

```text
             ball_minus_raw                 ball_minus_kmeans                
                       mean  median     std              mean  median     std
dataset                                                                      
aps_failure         -0.0013 -0.0011  0.0067           -0.0005 -0.0010  0.0062
secom               -0.0001  0.0000  0.0006            0.0000  0.0000  0.0000
steel_plates        -0.0007  0.0012  0.0124            0.0065  0.0083  0.0098
```

Mean ball-minus-raw: -0.0007; mean ball-minus-KMeans:
0.0020. Raw win/tie/loss: 25/16/34.

## Decision

**KILL**

The gate requires two datasets at least +1pp over Raw, one at least +2pp, and
positive ball-minus-KMeans means on two datasets. Failure closes all local
structure feature variants on this application branch.
