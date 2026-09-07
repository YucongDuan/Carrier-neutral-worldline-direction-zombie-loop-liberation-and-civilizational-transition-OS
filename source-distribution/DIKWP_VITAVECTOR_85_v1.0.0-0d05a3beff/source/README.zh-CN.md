# 生向 VITAVECTOR-85

> **不定义谁是“人”，只判断一条世界线正在生发、僵化、寄生还是坠落。**

VITAVECTOR-85彻底绕开“先定义人，再给人分级”的僵硬概念空间。系统不回答：

- 谁是完整的人；
- 谁是部分的人；
- 谁不是人；
- 谁永久文明或永久邪恶；
- 谁拥有更高内在价值。

系统只分析一个有明确时间、情境、来源和受影响对象的**世界线窗口**：

```text
D 来源与稳定关系
I 差异、冲突和残差
K 当前有界理解
W 受影响世界与不可补偿价值
P 唯一转变、现实行动、世界效果与回返
```

`11111`只能证明五个位置被显式登记，不能证明循环有生命力。一个闭环可以持续自洽、持续耗能、持续排除差异，却不生成新的事实、能力、互惠、修复和未来选择。系统把这种过程状态称为：

```text
ZOMBIE_CLOSURE / 僵尸闭环
```

该名称只属于当前世界线窗口，不属于任何载体的永久本质。

## 直接运行

```bash
python start_showcase.py
```

浏览器打开：

```text
http://127.0.0.1:8781
```

运行完整示例：

```bash
python run.py compile examples/zombie_loop.json --out outputs/zombie.worldline.json
python run.py intervene outputs/zombie.worldline.json examples/zombie_intervention.json --out outputs/zombie.intervened.json
python run.py outcome outputs/zombie.intervened.json examples/zombie_outcome.json --out outputs/zombie.closed.json
python run.py successor outputs/zombie.closed.json --out outputs/zombie.successor.json
```

执行质量检查：

```bash
make qa
```

## 核心突破

1. **载体中立**：碳基、硅基、混合体、共同体、机构、生态系统和未知载体共享同一世界线协议，但不被强行定义为同一种存在。
2. **闭环与生命力分离**：语义闭环不再自动升级为生命、文明或善。
3. **判断方向而非本体**：系统可以明确识别寄生、支配和终局伤害，却不能给载体贴永久善恶标签。
4. **非补偿方向向量**：真值、差异吸收、主体能力、互惠、纠错、未来选择等十二维分别保存，不能用一个总分掩盖伤害。
5. **唯一转变**：每次只生成一个最小充分行动、责任角色、截止时间和停止条件。
6. **世界效果裁决**：没有现实结果观察，就不能宣称完成文明跃迁。
7. **后继谱系**：每次修复都可生成新分支，保留父代来源、被否定内容和新增差异。
8. **系统自我适用**：系统若开始重复、抽取、拒绝纠正或维护自身存续，也必须冻结自己。

## 重要边界

- 不计算“人性分”或“文明分”；
- 不用于社会信用、招聘、司法定罪、医疗资格、福利剥夺或人格权利分配；
- 状态不能作为剥夺基本生存、医疗、安全、申诉、知情和退出的依据；
- `TERMINAL_HARM_HOLD`只冻结与具体伤害因果链直接相连的能力，不惩罚载体本身。

## 许可证

Apache License 2.0。
