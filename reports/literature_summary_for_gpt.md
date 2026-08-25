# 粒球计算、三支决策及隐私安全方向文献综述

> 用途：本文件可直接上传到 GPT 网页端，作为后续选题、文献核验、实验设计和论文路线讨论的上下文。
>
> 数据日期：2026-08-25。仓库分支：`codex/granular-ball-scout`。

## 1. 一页结论

仓库目前包含两个文献集合：

- 主文献库 162 篇，标题和 DOI 均已去重；
- 隐私/安全专题表 9 篇，其中 2 篇与主库重合；
- 合并按标题去重后共 169 篇；
- 主库中 2022--2026 年文献 125 篇；
- 主库 75 篇完成摘要级受控编码，87 篇仍只有元数据级编码。

最重要的总体判断：

1. 粒球计算已经不是一个稀疏的小方向。2019 年原始 GBC 分类器之后，工作快速扩展到生成机制、粗糙集、模糊粗糙集、属性约简、三支决策、聚类、异常检测、图学习和深度学习。
2. 当前最拥挤的机制不是“应用场景”，而是“如何生成、拆分、合并和停止粒球”。自适应生成、稳定生成、局部密度、合理粒度、三支边界、代价敏感和 MDL 都已经出现。
3. `GB + rough set + feature selection` 和 `GB + three-way decision` 已形成高密度碰撞区。仅把粒球接到新的分类器、粗糙集或三支框架上，通常不足以构成贡献。
4. “粒球保护隐私”的直接证据很少。最接近的 GrBFL 是图像联邦学习预印本，证明的是经验上更难重构，不是差分隐私、信息论隐私或密码学隐私。
5. 仓库 Cheap Test 没有发现粒球在隐私、云审计、多审计者建模或加密前压缩中具有稳定的 GB 特异优势。初始正信号在加入同预算强基线后消失。
6. 当前不建议继续正向包装“GB for privacy/auditing”。更诚实的路线是负结果基准、组件控制研究，或不强调 GB 的通用隐私微聚合/风险审计方法。

## 2. 语料范围与证据等级

### 2.1 主文献库

主库是一个高精度发现语料，不是“162 篇全文均已通读”的系统综述。

| 证据状态 | 数量 | 可以支持什么 |
|---|---:|---|
| 摘要级受控编码 | 75 | 可初步判断任务、表示、粒化方式和贡献类别 |
| 元数据级记录 | 87 | 只能确认题名、年份、期刊、DOI 等，不应推断具体算法细节 |

全文才能确认的字段包括：拆分准则、合并准则、停止条件、数据划分、强基线、统计检验、作者声明的局限和代码一致性。

### 2.2 年份分布

| 年份 | 数量 |
|---:|---:|
| 2026 | 35 |
| 2025 | 41 |
| 2024 | 20 |
| 2023 | 12 |
| 2022 | 17 |
| 2021 | 10 |
| 2020 | 12 |
| 2019 | 9 |
| 2010--2016 | 6 |

2024--2026 共 96 篇，说明该领域正处于快速扩张期。2026 年记录中有 accepted、in press 和预印本，做新颖性判断时必须再次核验正式发表状态。

### 2.3 高频发表渠道

| Venue | 主库数量 |
|---|---:|
| Information Sciences | 23 |
| Lecture Notes in Computer Science | 18 |
| International Journal of Approximate Reasoning | 14 |
| Applied Soft Computing | 11 |
| IEEE Transactions on Fuzzy Systems | 10 |
| Knowledge-Based Systems | 7 |
| IEEE TNNLS | 6 |

因此，检索不能只看安全期刊；粒球核心机制主要发表在信息科学、模糊系统、粗糙集和机器学习期刊。

## 3. 核心概念框架

### 3.1 粒球表示

一个常见粒球摘要包含：

- 中心 `center`：球内样本均值或原型；
- 半径 `radius`：样本到中心的平均或最大距离；
- 数量 `count`：球内样本数；
- 纯度 `purity`：多数类样本比例；
- 标签统计：多数标签或类分布；
- 可选层次关系：父子球、深度和多粒度结构。

典型流程是从粗粒度开始，对低纯度或低质量区域递归拆分，得到数量远小于原始样本数的局部表示，再用于分类、邻域构造、粗糙近似、属性约简、聚类或图构造。

### 3.2 粒球与普通聚类的真正差别

粒球论文通常强调：

- 表示单元不是单样本，而是自适应局部区域；
- 不同区域可以具有不同粒度；
- 标签纯度、边界或局部密度可驱动拆分；
- 下游距离可使用 `||x-center|| - radius`，而不只是中心距离；
- 在噪声、规模和可解释性之间寻找折中。

但这些优点必须与以下解释区分：

- 普通 KMeans 原型压缩；
- 层次聚类或树叶分区；
- kNN/local neighborhood；
- micro-clustering；
- 随机同规模分区；
- 监督式 class-aware prototype construction。

如果固定代表点数、通信预算和下游规则后，普通分区表现相同或更好，就不能把收益归因于“球”。

### 3.3 三支决策

三支决策把二元立即决策扩展为：

- 接受/正域；
- 延迟/边界域；
- 拒绝/负域。

它适合不确定性、成本敏感和序贯信息获取。与粒球结合时，决策对象可从单样本变成粒球等价类或多粒度区域，从而提高效率或表达边界。

风险在于：如果“第三支”只是人为设置阈值，或者等价于普通 selective prediction、拒识分类、代价敏感决策和树剪枝，则新颖性很弱。

## 4. 文献发展主线

### 4.1 理论基础：粗糙集、粒计算和三支决策

代表工作：

1. Yao, *Three-way decisions with probabilistic rough sets*，Information Sciences，2010，[DOI](https://doi.org/10.1016/j.ins.2009.09.021)。奠定概率粗糙集中的三支决策框架。
2. Yao, *Granular Computing and Sequential Three-Way Decisions*，2013，[DOI](https://doi.org/10.1007/978-3-642-41299-8_3)。把多粒度信息获取与序贯三支决策连接起来。
3. *Advances in three-way decisions and granular computing*，Knowledge-Based Systems，2016，[DOI](https://doi.org/10.1016/j.knosys.2015.10.026)。总结三支决策与粒计算的理论联系。
4. *The geometry of three-way decision*，Applied Intelligence，2021，[DOI](https://doi.org/10.1007/s10489-020-02142-z)。从几何角度解释三域结构。

这一基础线说明：三支决策并不依赖粒球。任何 `GB + 3WD` 工作都必须说明粒球相对于其他粒化形式增加了什么。

### 4.2 原始粒球计算与分类

核心起点：

- Xia et al., *Granular ball computing classifiers for efficient, scalable and robust learning*，Information Sciences，2019，[DOI](https://doi.org/10.1016/j.ins.2019.01.010)。

这项工作用多粒度粒球代替单样本作为计算单元，奠定了后续分类、生成、粗糙集和图表示工作的共同接口。其典型论点是减少计算对象、平滑噪声并提高可解释性。

需要注意：仓库复核发现原始作者代码中的纯度计算更偏向二分类，KMeans 随机种子固定，下游分类使用边界距离。复现实验必须披露这些实现约束。

### 4.3 粒球生成机制

这是当前最拥挤、最需要去重的分支。

代表论文：

1. *An Efficient and Adaptive Granular-Ball Generation Method in Classification Problem*，IEEE TNNLS，2024，[DOI](https://doi.org/10.1109/TNNLS.2022.3203381)。研究自适应生成和效率。
2. *GBG++: A Fast and Stable Granular Ball Generation Method for Classification*，IEEE TETCI，2024，[DOI](https://doi.org/10.1109/TETCI.2024.3359091)。强调快速与稳定。
3. *A granular-ball generation method based on local density for classification*，Information Sciences，2025，[DOI](https://doi.org/10.1016/j.ins.2025.122295)。使用局部密度改善生成。
4. *Generation of Granular-Balls for Clustering Based on the Principle of Justifiable Granularity*，IEEE Transactions on Cybernetics，2025，[DOI](https://doi.org/10.1109/TCYB.2025.3534195)。引入合理粒度原则。
5. *CS3W-GBG: A Cost-Sensitive Three-Way Granular-Ball Generation Method*，IEEE Transactions on Fuzzy Systems，2025，[DOI](https://doi.org/10.1109/TFUZZ.2025.3596066)。把代价敏感三支决策用于生成。
6. *Boundary-driven granular ball generation and classification via three-way decision*，Information Sciences，2026 accepted/in press，[DOI](https://doi.org/10.1016/j.ins.2026.123780)。以边界区域驱动生成。
7. *A Boundary-Aware Non-parametric Granular-Ball Classifier Based on Minimum Description Length*，2026 预印本，[arXiv DOI](https://doi.org/10.48550/arXiv.2605.11406)。用局部 MDL 在单球、双球和核心-边界模型之间选择。

新方法若仍然只是提出新的纯度、密度、熵、稳定性、代价或停止指标，碰撞风险很高。需要优先证明：现有生成规则在什么结构条件下失败，以及新规则解决的是粒球特有问题还是通用聚类/树剪枝问题。

### 4.4 粒球粗糙集、模糊粗糙集与属性约简

这是主库中密度最高的应用机制组合之一。

代表论文：

1. *GBRS: A Unified Granular-Ball Learning Model of Pawlak Rough Set and Neighborhood Rough Set*，IEEE TNNLS，2025，[DOI](https://doi.org/10.1109/TNNLS.2023.3325199)。试图统一 Pawlak 与邻域粗糙集。
2. *A novel granular ball computing-based fuzzy rough set for feature selection in label distribution learning*，Knowledge-Based Systems，2023，[DOI](https://doi.org/10.1016/j.knosys.2023.110898)。将粒球模糊粗糙集用于特征选择。
3. *Granular Ball Fuzzy Neighborhood Rough Sets-Based Feature Selection via Multiobjective Mayfly Optimization*，IEEE Transactions on Fuzzy Systems，2024，[DOI](https://doi.org/10.1109/TFUZZ.2024.3440575)。粒球邻域粗糙集与多目标搜索结合。
4. *Three-Way Approximations Fusion With Granular-Ball Computing to Guide Multigranularity Fuzzy Entropy for Feature Selection*，IEEE Transactions on Fuzzy Systems，2024，[DOI](https://doi.org/10.1109/TFUZZ.2024.3436086)。融合三支近似、多粒度模糊熵和特征选择。
5. *Online group streaming feature selection based on fuzzy neighborhood granular ball rough sets*，Expert Systems with Applications，2024，[DOI](https://doi.org/10.1016/j.eswa.2024.123778)。扩展到在线分组流特征选择。
6. *Fuzzy neighborhood based variable-precision granular-ball rough sets with applications to feature selection*，Fuzzy Sets and Systems，2025，[DOI](https://doi.org/10.1016/j.fss.2025.109382)。结合变精度和模糊邻域。

该方向的审稿风险通常是：把新的粗糙近似、熵或启发式搜索替换进既有框架，但没有证明粒球表示本身不可替代。强基线应包括标准 fuzzy rough feature selection、neighborhood rough set、普通局部邻域和非粒球特征选择器。

### 4.5 粒球与三支分类/序贯决策

代表论文：

1. *Granular-Ball Three-Way Decision*，LNCS，2023，[DOI](https://doi.org/10.1007/978-3-031-50959-9_20)。把粒球等价类作为三支决策对象，并提出序贯版本。
2. *3WC-GBNRS++: A Novel Three-Way Classifier With Granular-Ball Neighborhood Rough Sets Based on Uncertainty*，IEEE Transactions on Fuzzy Systems，2024，[DOI](https://doi.org/10.1109/TFUZZ.2024.3397697)。结合粒球邻域粗糙集和不确定性三支分类。
3. *Constructing Three-Way Decision With Fuzzy Granular-Ball Rough Sets Based on Uncertainty Invariance*，IEEE Transactions on Fuzzy Systems，2025，[DOI](https://doi.org/10.1109/TFUZZ.2025.3536564)。研究不确定性不变和序贯三支结构。
4. *A Robust Three-Way Classifier With Shadowed Granular Balls Based on Justifiable Granularity*，IEEE TNNLS，2025，[DOI](https://doi.org/10.1109/TNNLS.2025.3563889)。连接 shadowed set、合理粒度和三支分类。
5. *3W-GBSVM++: Three-way granular-ball SVM based on granularity optimization mechanism*，Applied Soft Computing，2026，[DOI](https://doi.org/10.1016/j.asoc.2026.114593)。把三支粒球结构接入 SVM。

这里最重要的控制问题是：三支收益来自不确定性拒识/延迟决策，还是来自粒球？必须比较非 GB selective classifier、代价敏感分类、conformal prediction、树叶和局部邻域。

### 4.6 聚类、异常检测与流式学习

代表论文：

- *Detecting anomalies with granular-ball fuzzy rough sets*，Information Sciences，2024，[DOI](https://doi.org/10.1016/j.ins.2024.121016)。
- *Multi-view Granular-ball Contrastive Clustering*，AAAI 2025，[DOI](https://doi.org/10.1609/aaai.v39i19.34274)。
- *Adaptive granular-ball based density peak clustering*，Neurocomputing，2025，[DOI](https://doi.org/10.1016/j.neucom.2025.131458)。
- *Granular-Ball Regeneration Clustering With Principle of Justifiable Granularity*，IEEE TNNLS，2025，[DOI](https://doi.org/10.1109/TNNLS.2025.3579376)。
- *Natural granular-ball anomaly detection*，Applied Soft Computing，2026，[DOI](https://doi.org/10.1016/j.asoc.2026.115147)。
- *Three-way role-arbitration outlier detection based on bi-level granular-ball knowledge representation*，Knowledge-Based Systems，2026，[DOI](https://doi.org/10.1016/j.knosys.2026.116038)。

这类工作常把粒球放在 instance-level 与 cluster-level 之间。真正值得研究的机制是：局部拓扑、非均匀密度和边界复杂度是否使自适应多粒度表示优于同数量 microclusters、density peaks、DBSCAN 或局部邻域。

### 4.7 图、图像和深度表示

代表论文：

- *An Adaptive Multi-Granularity Graph Representation of Image via Granular-ball Computing*，IEEE Transactions on Image Processing，2025，[DOI](https://doi.org/10.1109/TIP.2025.3565212)。
- *Square Superpixel Generation and Representation Learning via Granular-ball Computing*，CISAT 2025，[DOI](https://doi.org/10.1109/CISAT66811.2025.11181937)。
- *Multi-granularity graph refinement via granular ball for graph classification*，Neurocomputing，2026，[DOI](https://doi.org/10.1016/j.neucom.2026.133713)。
- *Structure-aware granular-ball hypergraph learning*，Engineering Applications of Artificial Intelligence，2026，[DOI](https://doi.org/10.1016/j.engappai.2026.115428)。
- *Multi-Granularity Graph Contrastive Learning Framework via Granular-Ball on Heterogeneous Graphs*，IEEE TPAMI，2026，[DOI](https://doi.org/10.1109/TPAMI.2026.3720194)。

图像粒矩形、超像素和图粗化已使“粒球 + 图像/图网络”进入高碰撞区。新的图像隐私工作尤其要与 superpixel、saliency、masking 和普通图粗化比较。

## 5. 隐私与安全专题边界

### 5.1 已有直接工作实际证明了什么

最接近的直接工作是：

1. *A New Perspective on Privacy Protection in Federated Learning with Granular-Ball Computing*，2025 arXiv 预印本，[链接](https://arxiv.org/abs/2501.04940)。它将图像分成粒矩形并重构为图，报告梯度重构更困难，补充材料提到成员推断。
2. *Federated open intent classification via granular-ball knowledge representation*，Neural Networks，2026，[出版社页面](https://www.sciencedirect.com/science/article/pii/S0893608026002790)。客户端上传模型和局部粒球知识，用于开放意图分类。

需要严格区分：

| 说法 | 能否由上述工作直接推出 |
|---|---|
| 原始数据不直接上传 | 可以，属于联邦/摘要传输设计 |
| 经验上更难进行某种重构 | GrBFL 有相应实验 |
| 粒球摘要不会泄漏成员或属性 | 不能 |
| 满足 `(epsilon, delta)`-DP | 不能 |
| 信息论隐私 | 不能 |
| 密码学机密性/不可区分性 | 不能 |

“信息减少”不等于“隐私保证”。中心、半径、数量、纯度和层次结构本身都可能泄漏小群体、稀有属性和边界信息。

### 5.2 本轮限定检索没有发现的直接组合

在 2022--2026 scoped search 中未发现以下正式直接工作：

- 粒球 tabular summary 对 membership、attribute、reconstruction 的系统攻击评估；
- 形式化 `granular-ball + differential privacy`；
- `granular-ball + cloud-storage public auditing/PDP/PoR`；
- `granular-ball + malicious multi-auditor auditing`；
- 粒球摘要作为 HE/MPC 前置密码学压缩对象。

这是“本轮检索未发现”，不是数学意义上的不存在证明。

### 5.3 相邻碰撞

- *A privacy enhancing model for Internet of Things using three-way decisions and differential privacy*，Computers and Electrical Engineering，2022，[DOI](https://doi.org/10.1016/j.compeleceng.2022.107894)。三支属性划分后使用 DP，但不使用粒球。
- *Federated learning with three-way decisions for privacy-preserving multicloud resource scheduling*，Applied Soft Computing，2025，[DOI](https://doi.org/10.1016/j.asoc.2025.113634)。是多云资源调度，不是存储完整性审计。
- *Privacy-Preserving Feature Selection with Secure Multiparty Computation*，ICML 2021，[链接](https://proceedings.mlr.press/v139/li21c.html)。给出正式 MPC 特征选择基线。
- *Privacy Preserving Feature Selection for Sparse Linear Regression*，IACR ePrint 2023，[链接](https://eprint.iacr.org/2023/1354)。使用同态加密和半诚实安全证明。

这些工作意味着：如果声称“隐私保护”，必须明确威胁模型、攻击面、敏感度、组合、对手能力或安全证明，不能只报告分类精度和重构 MSE。

## 6. 文献统计揭示的拥挤区与空档

主库的受控标签统计：

| 维度 | 高频类别 | 数量 |
|---|---|---:|
| 任务 | decision analysis | 91 |
| 任务 | classification | 39 |
| 任务 | feature selection | 29 |
| 任务 | clustering | 18 |
| 表示 | granular ball | 78 |
| 表示 | rough-set approximation | 75 |
| 粒化 | granular-ball generation | 76 |
| 不确定性 | three-way boundary/defer region | 96 |
| 决策 | accept/defer/reject | 87 |

### 6.1 高碰撞区

- 新的粒球拆分/停止指标；
- 粒球粗糙集或模糊粗糙集属性约简；
- 粒球三支分类；
- 粒球 + SVM/kNN/图网络的直接拼接；
- 粒球图像分割、图构造和超像素；
- 仅以效率、鲁棒性、可解释性作为通用贡献。

### 6.2 仍有信息增益的研究问题

1. 粒球结构在什么数据几何条件下不可被普通分区替代？
2. 中心、半径、数量、纯度分别贡献什么，是否有组件级反例？
3. 全局 purity threshold 是否在不同局部结构下存在不可兼容性？
4. 自适应粒度的收益来自边界复杂度、密度异质性还是标签使用？
5. 公开粒球摘要的最坏情况泄漏如何随最小球大小变化？
6. 是否能对球中心/半径建立有意义、非空泛的敏感度和隐私界？
7. 负结果是否可以形成一个 matched-budget component benchmark？

## 7. 仓库实验对文献主张的校验

以下是仓库实验结果，不是文献结论：

| 方向 | 关键结果 | 决策 |
|---|---|---|
| Privacy Leakage | 初始 GB 比 matched KMeans 的 membership AUC 低 0.0516，但 Anti-GB 后相对最佳同 utility 对手的优势为 -0.0523，仅 1/30 条件保留优势 | KILL |
| Cloud Auditing | 90 个结构化损坏单元中，相对最强非 GB 基线的平均检测增益 -0.0074 | KILL |
| Multi-Auditor | 120 个条件中，相对最强非 GB 方法的平均 accuracy 增益 -0.0196 | KILL |
| Secure Aggregation | GB 比 matched KMeans accuracy 低 0.0032；压缩门槛通过率 0.044 | KILL |
| DP Granular Ball | Privacy 前置门控失败，因此未运行，未提出 DP 声明 | KILL by gate |

Anti-GB 实验尤其重要：在代表点数和 utility 受控后，随机分区、层次分区、局部原型或 tuned KMeans 可以达到更低泄漏。初始“GB 胜 KMeans”并不能证明球结构必要。

## 8. 当前最可信的研究判断

### 8.1 可以说

- 粒球是一种有用的自适应多粒度表示候选；
- 它在部分分类、粗糙近似和局部结构任务中可能改善效率或鲁棒性；
- 生成机制和粒度选择是该领域的核心问题；
- 隐私、安全和云审计直接工作仍然稀少；
- 强基线和同预算控制经常足以消除表面上的 GB 增益。

### 8.2 不能说

- 粒球天然保护隐私；
- 不传输原始样本就等于差分隐私；
- 粒球压缩天然降低密码学成本且保持 utility；
- 三支策略优于二支策略就证明粒球有效；
- 某一数据集上的正结果足以证明新颖机制；
- 搜索未命中就证明相关论文不存在。

## 9. 推荐给 GPT 网页端的分析任务

上传本文件和 `literature_catalog_for_gpt.csv` 后，可直接给 GPT 以下指令：

```text
你现在是严格的科研选题审稿人。请基于我上传的文献综述和 169 篇去重目录：

1. 区分全文证据、摘要证据和元数据证据，不要把未核验字段当作事实；
2. 把候选想法拆成 representation / granulation / split / merge / stop /
   uncertainty / decision / downstream learner；
3. 对每个候选找出最接近的 5 篇论文和最强的非 GB 解释；
4. 严格区分经验难恢复、减少原始数据传输、差分隐私、信息论隐私和密码学隐私；
5. 任何正结果都要求 matched number of regions / communication budget /
   audit budget / privacy budget；
6. 优先提出能在 CPU、小数据、5 seeds 下证伪的 Cheap Test；
7. 如果 KMeans、tree、kNN、micro-clustering 或 random matched partition
   能完成同样任务，直接判定 GB-specificity 不足；
8. 不要为了形成论文强行推荐正方向，允许输出 KILL 或负结果论文路线。

最后输出：候选方向、文献碰撞、真正空档、最强反解释、Cheap Test、
GO/HOLD/KILL 条件，以及一句可被实验推翻的 paper hypothesis。
```

## 10. 上传建议

为了让 GPT 网页端获得足够上下文，建议同时上传：

1. `literature_summary_for_gpt.md`：当前这份解释性综述；
2. `literature_catalog_for_gpt.csv`：169 篇去重结构化目录；
3. 如需追踪实验，再上传 `final_research_scout.md`。

不要只上传 `papers.csv` 后要求模型“总结全部文献”。其中 87 篇只有元数据，模型容易用题名补全不存在的细节。应先让模型按证据等级筛选，再选择代表论文做全文核验。

