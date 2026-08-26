# Raw Industrial Conventional-ML Baselines

## Scope

This first baseline covers three independent real industrial tabular sources:
Steel Plates Faults, SECOM semiconductor yield, and Scania APS failure. It is a
mechanism screen while official mechanical-vibration downloads remain pending;
it cannot by itself satisfy a final fault-diagnosis paper gate.

Five frozen seeds are used. Steel Plates uses seeded stratification, SECOM uses
a chronological split, and APS preserves the official 60k/16k train/test roster.
Every median imputer and scaler is fit on training data only.

KNN and RBF-SVM are diagnostic models and use a stratified 5,000-row fit cap on
larger data. They are not eligible to define the strongest full-data baseline.

## Per-dataset/model metrics

```text
                           macro_f1         balanced_accuracy             mcc         minority_recall          g_mean        
                               mean     std              mean     std    mean     std            mean     std    mean     std
dataset      model                                                                                                           
aps_failure  catboost        0.8291  0.0060            0.9638  0.0036  0.6919  0.0100          0.9488  0.0072  0.9636  0.0037
             extra_trees     0.8556  0.0036            0.7925  0.0035  0.7304  0.0072          0.5861  0.0069  0.7651  0.0045
             knn             0.7340  0.0070            0.6664  0.0101  0.5217  0.0070          0.3344  0.0207  0.5776  0.0175
             lightgbm        0.9095  0.0007            0.9367  0.0025  0.8207  0.0013          0.8795  0.0051  0.9349  0.0026
             random_forest   0.8445  0.0073            0.7781  0.0070  0.7121  0.0140          0.5573  0.0139  0.7461  0.0093
             svm_rbf         0.5641  0.0282            0.5403  0.0182  0.1925  0.0633          0.0827  0.0365  0.2819  0.0617
             xgboost         0.9015  0.0026            0.9344  0.0031  0.8057  0.0050          0.8757  0.0061  0.9325  0.0033
secom        catboost        0.4861  0.0000            0.5000  0.0000  0.0000  0.0000          0.0000  0.0000  0.0000  0.0000
             extra_trees     0.4861  0.0000            0.5000  0.0000  0.0000  0.0000          0.0000  0.0000  0.0000  0.0000
             knn             0.4861  0.0000            0.5000  0.0000  0.0000  0.0000          0.0000  0.0000  0.0000  0.0000
             lightgbm        0.4859  0.0004            0.4997  0.0008 -0.0027  0.0060          0.0000  0.0000  0.0000  0.0000
             random_forest   0.4861  0.0000            0.5000  0.0000  0.0000  0.0000          0.0000  0.0000  0.0000  0.0000
             svm_rbf         0.4861  0.0000            0.5000  0.0000  0.0000  0.0000          0.0000  0.0000  0.0000  0.0000
             xgboost         0.4856  0.0008            0.4990  0.0015 -0.0065  0.0092          0.0000  0.0000  0.0000  0.0000
steel_plates catboost        0.7642  0.0113            0.8057  0.0154  0.6874  0.0242          0.8000  0.0761  0.7941  0.0154
             extra_trees     0.7671  0.0250            0.7562  0.0290  0.6914  0.0251          0.7455  0.0761  0.7329  0.0376
             knn             0.7355  0.0367            0.7514  0.0191  0.6429  0.0302          0.8000  0.0407  0.7271  0.0274
             lightgbm        0.7871  0.0178            0.7948  0.0291  0.7220  0.0181          0.7273  0.1701  0.7782  0.0347
             random_forest   0.7721  0.0228            0.7474  0.0269  0.6927  0.0227          0.7273  0.1437  0.7234  0.0346
             svm_rbf         0.7454  0.0252            0.7916  0.0250  0.6586  0.0248          0.8000  0.1185  0.7761  0.0248
             xgboost         0.7898  0.0167            0.7762  0.0257  0.7203  0.0151          0.6909  0.1220  0.7570  0.0299
```

## Strongest model per dataset

```text
     dataset    model  macro_f1
 aps_failure lightgbm  0.909470
       secom catboost  0.486088
steel_plates  xgboost  0.789837
```

## Tree and boosting comparison

```text
               macro_f1  balanced_accuracy     mcc  fit_seconds
model                                                          
lightgbm         0.7275             0.7437  0.5134       1.9380
xgboost          0.7257             0.7365  0.5065       1.3022
extra_trees      0.7029             0.6829  0.4739       1.0053
random_forest    0.7009             0.6752  0.4683       2.3654
catboost         0.6931             0.7565  0.4598       1.2093
```

## KNN/SVM diagnostic competitiveness

```text
         macro_f1  balanced_accuracy     mcc
model                                       
knn        0.6519             0.6392  0.3882
svm_rbf    0.5985             0.6106  0.2837
```

## Baseline target for GB augmentation

GB structural features and weights must beat the strongest eligible tree or
boosting model **within each matched dataset and seed**. Beating only KNN/SVM
does not count. No large hyperparameter search has been performed at this stage.
