# First Research Direction Ranking — 2026-08-24

Eligibility evidence: 162 structured papers, five runnable core GBC/3WD author
paths, 14 synthetic families, and 1,014 append-only experiment records. This is the
requested first Top 10, not the final 2–5 survivors. Only Candidate 1 currently
has cross-method, cross-real-dataset evidence. MDL-based local construction is
excluded after direct collision with arXiv:2605.11406.

# Candidate 1

## 暂定题目

从全局纯度到局部可靠性约束：粒球生成中的风险–校准–结构成本自适应停止

## 核心问题

单一全局 purity 为什么会在不同区域产生欠分裂、无收益爆炸和有害过分裂，如何用局部可验证决策替代？

## Existing Failure

H-003 经 original GBC 与 accelerated GBG、五个 OpenML 数据集、210 次 purity 扫描复现。Phoneme 出现 1→数百球相变；Electricity 增加约千球几乎无收益；Ionosphere 细化后退化。

## Proposed Mechanism

暂不锁定算法。局部 cross-fit pruning 也已失败；任何后续动作必须避免在小粒上耗尽验证样本，并同时约束 risk、proper score 和新增球成本。M01、M02、M05、M12 已被淘汰。

## Why Granular Computing?

失败发生在粒的生成、停止和局部尺度，而非下游分类器拼接。

## Why Existing Work Cannot Directly Solve It?

Adaptive GBG、GBG++、local-density GBG 和 2026 MDL-GBC 均是最近近邻。MDL 方案已占位；现有公开证据尚未显示其解决跨区域 purity phase regimes 或联合 risk/calibration/cost 约束。

## Novelty Risk

MEDIUM–HIGH。局部验证和 cost-complexity 与决策树剪枝相邻，必须证明非等价机制或统计性质。

## Preliminary Experiment

原始/accelerated 两套 105-run 扫描；M01 15-run kill test；M02/M04 各 45-run global controls；M12 45-run red team。

## Result

问题稳定存在。普通 global validation、单目标 Brier、confidence bound、经验膝点和局部 cross-fit pruning 均在关键数据上失败。

## Theoretical Opportunity

局部动作的有限样本风险界；满足 risk/calibration 约束时的最小球数；全局阈值不可同时最优的反例/不可能性命题。

## Computational Cost

CPU。局部 cross-fit/重采样可能增加 3–10 倍生成成本，需要 VOI 式预算控制。

## Target Venue Level

若有统计性质和跨方法实验，可冲击高水平 fuzzy/AI journal；当前未到投稿阶段。

## Next Decisive Experiment

转向 Candidate 2 的 sequential three-way/VOI 证据获取，或先完成 Candidate 6 的不可能性/样本复杂度分析；禁止继续调 local pruning 阈值。

# Candidate 2

## 暂定题目

三支粒化决策：在统计证据不足时选择 split、keep 或 investigate

## 核心问题

局部 purity 证据不足时，系统是否应继续分裂、保持当前粒，还是购买额外验证/重采样信息？

## Existing Failure

M01 证明“统一更保守”会加剧爆炸；M02 证明单次 validation 会误选；H-003 表明不同区域需要相反动作。

## Proposed Mechanism

以置信区间形成三支状态：可靠 keep、明确 split、uncertain/investigate；investigate 的采样次数由预期风险下降/成本控制。

## Why Granular Computing?

动作直接改变粒结构，且 uncertain 区域对应粒化决策而不是最终样本分类。

## Why Existing Work Cannot Directly Solve It?

3WD、sequential 3WD、uncertainty-invariance GBRS 和 cost-sensitive 3WD 已拥挤；必须区别于把 ACCEPT/DEFER/REJECT 名称套在 split 上。

## Novelty Risk

HIGH。VOI 与三支决策均成熟，组合本身不构成创新。

## Preliminary Experiment

M01/M02 negative controls；S3WD smoke 显示 coverage 0.630、selective Accuracy 0.971，但 defer-as-error Accuracy 0.611。

## Result

继续获取信息有必要，但尚无局部 VOI 策略证据。

## Theoretical Opportunity

有限预算下错误 split/keep 概率；sequential evidence 的停止界；相对固定 purity 的 regret bound。

## Computational Cost

CPU，中等；主要成本是局部重采样。

## Target Venue Level

有理论可达 IJAR/Information Sciences/TFS 层级；否则为高碰撞增量工作。

## Next Decisive Experiment

在三个 H-003 数据集上比较 fixed、Wilson、global CV 与三支 sequential test；若 uncertain 分支不能以更少评估达到更低 regret，淘汰。

# Candidate 3

## 暂定题目

局部交错边界下的粒球失真：从球内标签混合到表示选择

## 核心问题

什么局部几何统计量决定球形粒会丢失交错/弯曲边界信息？

## Existing Failure

修正后的 XOR v2 与 sector-wheel/checkerboard 跨生成器复现两种 GBC 的负 gap；Gaussian XOR 完全不失败，排除了“同类区域不连通”这一简单解释。

## Proposed Mechanism

先建立 boundary mixing、曲率/尺度失配和局部拓扑量；只有预测 failure 后才允许选择 ball/ellipsoid/manifold patch。

## Why Granular Computing?

目标是识别粒表示的适用条件，而非给普通分类器加模块。

## Why Existing Work Cannot Directly Solve It?

Boundary-aware MDL-GBC、interval granulation、local-density GBG 和 structure-aware GBC 是直接近邻。MDL/boundary-aware 命名已高度占用。

## Novelty Risk

HIGH。

## Preliminary Experiment

XOR v2 140 runs；alternating v2 90 runs；sector wheel 29/30 negative gaps。V1 距离错误已废弃。

## Result

现象跨方法/生成器，但尚无真实数据几何对应和可预测统计量。

## Theoretical Opportunity

球化信息损失关于局部曲率、margin、covering number 的界；表示误差的必要条件。

## Computational Cost

CPU。

## Target Venue Level

若形成定理和真实压力测试，可达高水平；否则容易与现有 boundary-aware 工作碰撞。

## Next Decisive Experiment

验证一个预先定义的 boundary-mixing/curvature 指标能否跨 XOR、wheel、checkerboard 和真实数据预测 gap；预测失败即降级。

# Candidate 4

## 暂定题目

粒球 purity 不是概率：校准风险与统计覆盖的系统审计

## 核心问题

粒球 purity 在什么条件下可以解释为置信度，何时会产生严重失准？

## Existing Failure

固定 p=.85 时 Electricity/Ionosphere ECE 约 0.25/0.24；所有球满足 purity stop 仍有显著测试 gap。M04 表明只优化 Brier 会牺牲 Accuracy。

## Proposed Mechanism

先做校准审计与有限样本分析；候选修复是 conformal/local proper-score constraint，而非直接以 ECE 分裂。

## Why Granular Computing?

purity 被大量方法当作结构质量/置信代理，失准来自粒级聚合。

## Why Existing Work Cannot Directly Solve It?

Uncertainty-invariance 3WD、fuzzy GBRS、selective/conformal prediction 是近邻；直接 GBC conformal 标题暂未发现，但任务迁移风险高。

## Novelty Risk

MEDIUM–HIGH。

## Preliminary Experiment

25 real-data fixed-purity runs、105-run scan、45-run M04 control。

## Result

失准跨数据明显但不普遍；Banknote ECE 仅约 0.012。校准必须与 Accuracy/成本联合处理。

## Theoretical Opportunity

粒内 exchangeability 条件下 coverage；purity 与真实条件概率偏差界；selective risk guarantee。

## Computational Cost

CPU。

## Target Venue Level

有 coverage/risk guarantee 时优先级高；仅 ECE 改善则中低。

## Next Decisive Experiment

用 split conformal 检查不同 purity 路径的 coverage-risk；若粒化不提供超越 Mondrian/local conformal 的性质，否决。

# Candidate 5

## 暂定题目

自适应粒球生成的 seed/中心不稳定性与局部密度偏差

## 核心问题

随机初始中心和 overlap refinement 是否会在不平衡密度下系统改变 failure region？

## Existing Failure

Campaign v1 的 imbalanced-density trial 中 adaptive gap −0.086、original 约持平；moons 上结果相反。作者 adaptive 文件的 overlap 半径还硬编码前两维。

## Proposed Mechanism

先分离算法定义与实现缺陷，测量结构的 bootstrap/seed variation；不预设 stability stop 是答案。

## Why Granular Computing?

不稳定性发生在粒中心、split 和 overlap resolution。

## Why Existing Work Cannot Directly Solve It?

GBG++ 已占据“fast/stable”，local-density GBG 直接相关；M03 已判定 PARTIAL_COLLISION。

## Novelty Risk

HIGH。

## Preliminary Experiment

仅一组 3-seed synthetic observation，证据弱。

## Result

方法特异信号，未升级假设。

## Theoretical Opportunity

样本扰动下中心/成员分配稳定界。

## Computational Cost

CPU，中等重采样成本。

## Target Venue Level

当前不足以评估；大概率为复现/实现审计而非独立论文。

## Next Decisive Experiment

对 density ratio、imbalance 和初始中心做五 seed 网格；若不跨生成器复现，立即淘汰。

# Candidate 6

## 暂定题目

粒化复杂度相变：纯度路径上的球数爆炸与泛化非单调性

## 核心问题

能否预测 purity 变化何时导致球数相变而非有效风险下降？

## Existing Failure

Phoneme 1→数百球跃迁、Electricity 千球无收益、Ionosphere 过分裂退化在两种生成方法上出现。

## Proposed Mechanism

Theory-first：分析递归 split 的复杂度路径、最小可分纯度和噪声/重叠条件，不使用经验 knee（M12 已淘汰）。

## Why Granular Computing?

相变由粒递归和纯度停止共同产生。

## Why Existing Work Cannot Directly Solve It?

复杂度/稳定性常被报告，但尚未发现针对 purity path phase regimes 的系统理论；MDL-GBC 是最近机制近邻。

## Novelty Risk

MEDIUM。

## Preliminary Experiment

两套 105-run real purity paths。

## Result

跨方法现象稳定；理论尚空缺。

## Theoretical Opportunity

球数关于 purity、label noise、margin 的上下界；不可兼容全局阈值命题；split path 的非单调泛化反例。

## Computational Cost

CPU + 理论分析。

## Target Venue Level

若有非平凡界，可成为 Candidate 1 的理论主线；单独经验曲线级别较低。

## Next Decisive Experiment

在可解析 Gaussian/XOR mixture 上推导最小反例并验证球数阶；若只能事后拟合曲线，合并回 Candidate 1。

# Candidate 7

## 暂定题目

三支 defer 阈值在分布漂移下的失准

## 核心问题

训练分布学习的 accept/defer/reject 阈值在 shift 后是否保持 coverage 与 selective risk？

## Existing Failure

当前仅 S3WD smoke：coverage 0.630、selective Accuracy 0.971、总体 0.611。尚无 shift 证据。

## Proposed Mechanism

先构造 drift stress test，再考虑阈值重校准/change detection；不预设新算法。

## Why Granular Computing?

defer 区由粒结构/隶属度阈值产生。

## Why Existing Work Cannot Directly Solve It?

Sequential 3WD、incremental 3WD 和 streaming granulation 已拥挤；需证明 shift-specific failure。

## Novelty Risk

HIGH。

## Preliminary Experiment

仅单一 moons smoke。

## Result

不足以形成假设。

## Theoretical Opportunity

shift 下 selective risk/coverage 漂移界。

## Computational Cost

CPU。

## Target Venue Level

未定。

## Next Decisive Experiment

对 covariate/prior/concept shift 做五 seed threshold stress test；无稳定失准则淘汰。

# Candidate 8

## 暂定题目

粒球分类距离的下游敏感性：center 与 center-minus-radius 的 failure region

## 核心问题

生成结构相同但分类距离不同，结论和 failure region 会变化多少？

## Existing Failure

V1 使用 nearest center 高估 XOR/sector gap；审计作者代码后，v2 center-minus-radius 将效应约减半但未消失。

## Proposed Mechanism

系统拆分 representation/generation/decision 三层，建立等结构下游敏感性基准；不立即发明距离。

## Why Granular Computing?

radius 进入粒级决策，点分类器没有这一结构耦合。

## Why Existing Work Cannot Directly Solve It?

大量论文混合生成和分类改动；需组件级控制实验。可能属于实验方法贡献而非新算法。

## Novelty Risk

MEDIUM–HIGH。

## Preliminary Experiment

230 v1 + 230 corrected-v2 targeted runs；clean-room 与作者 43 个预测一致。

## Result

下游距离是重要混杂因素，且错误实现能制造夸大 failure。

## Theoretical Opportunity

两种距离规则预测分歧区域的几何刻画。

## Computational Cost

CPU，低。

## Target Venue Level

更适合作为 benchmark/analysis paper 子贡献。

## Next Decisive Experiment

加入 radius-normalized、membership 和 3WD 决策，在固定粒结构上跨真实数据比较；若仅实现细节差异，合并到工具论文。

# Candidate 9

## 暂定题目

面向科研 Agent 的反例目标函数：避免近零参考损失导致的虚假 failure

## 核心问题

自动 failure search 如何避免比值目标在参考误差接近零时制造夸大结论？

## Existing Failure

Campaign v1 trial 009 的 ratio 高达 9.33，但 GBC Accuracy 近 1 且 absolute gap 非负。

## Proposed Mechanism

预注册多目标 failure criterion：absolute gap、结构成本、seed stability、校准，并对 ratio 设置 denominator floor。

## Why Granular Computing?

不是粒计算专属；价值在于本仓库的自动科研循环。

## Why Existing Work Cannot Directly Solve It?

属于通用 benchmark/search methodology，可能缺乏粒计算独特性。

## Novelty Risk

HIGH（作为论文）；LOW（作为基础设施贡献）。

## Preliminary Experiment

72-run campaign 已给出算术反例。

## Result

规则已在后续实验采用 absolute gap 修正。

## Theoretical Opportunity

多目标搜索选择偏差与 false discovery 控制。

## Computational Cost

低。

## Target Venue Level

单独论文优先级低；适合作为开放 benchmark/artifact。

## Next Decisive Experiment

比较不同 failure objectives 对排名稳定性和假阳性率的影响；若无一般性，保留为工程规范。

# Candidate 10

## 暂定题目

流式环境中的局部粒度动作：keep/update/split/merge/forget

## 核心问题

H-003 的全局规则不兼容在 concept/density/class drift 下是否进一步放大？

## Existing Failure

目前没有流式实验；仅静态 H-003 提供动机。

## Proposed Mechanism

先建立 drift generator 和 rebuild-vs-incremental baseline，再决定是否需要 change-point × granulation。

## Why Granular Computing?

粒结构提供可更新单元和 memory/cost 权衡。

## Why Existing Work Cannot Directly Solve It?

Incremental/online granular computing 与 streaming feature selection 已有大量工作，撞题风险高。

## Novelty Risk

HIGH。

## Preliminary Experiment

无。

## Result

仅为待证问题，排名最低。

## Theoretical Opportunity

更新成本–风险–内存界；漂移下结构稳定性。

## Computational Cost

CPU。

## Target Venue Level

未定。

## Next Decisive Experiment

实现 4 类 drift 与 full rebuild baseline；若 incremental GBC 文献已覆盖同一问题或无独特 failure，直接淘汰。

## Ranking summary

1. Candidate 1 — P0 problem, mechanism unresolved.
2. Candidate 2 — P1, high collision risk.
3. Candidate 3 — P1, boundary-aware collision risk.
4. Candidate 4 — P1, theory-dependent.
5. Candidate 6 — P1 theory track for Candidate 1.
6. Candidate 5 — P2 replication needed.
7. Candidate 8 — P2 analysis/artifact.
8. Candidate 7 — P2, no shift evidence.
9. Candidate 9 — infrastructure, not main paper.
10. Candidate 10 — speculative, lowest priority.

No entry is added to `candidates/survivors.md` yet. Second-round validation and
deeper novelty checks must reduce this list to 2–5.
