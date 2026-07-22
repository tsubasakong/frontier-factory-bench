# Raw review report 02 — Factorio 2.0 modding feasibility

Reviewer: sub-agent "Halley" (Factorio modding technical feasibility),
2026-07-21. Basis: Factorio 2.0 official prototype/runtime documentation and
API names (links inline). Language: Chinese (kept verbatim for provenance).

---

## 1. 不可手搓的实现 — 可行，三层机制叠加

核心机制是 `RecipePrototype.category` 与 `CraftingMachinePrototype.crafting_categories` 的匹配：角色（Character）只能执行自己 `crafting_categories` 列表内的配方类别。把 AI 加速器、服务器机架、compute unit 三个配方放进自定义类别（如 `ffb-accelerator-assembly`、`ffb-rack-assembly`、`ffb-compute`），只授予对应新机器，玩家即无法手搓。依据：[RecipePrototype](https://lua-api.factorio.com/latest/prototypes/RecipePrototype.html)、[RecipeCategory](https://lua-api.factorio.com/latest/prototypes/RecipeCategory.html)、[CraftingMachinePrototype](https://lua-api.factorio.com/latest/prototypes/CraftingMachinePrototype.html)。

两个辅助布尔建议全开（文档语义已确认）：

- `hide_from_player_crafting = true`：从玩家制造界面隐藏，机器仍可选用；
- `allow_as_intermediate = false`：手搓高级配方时不会自动排队补搓该中间体——这是防止"手搓链条传导"的关键。

**边界怎么划、漏洞在哪：**

- 漏洞 A（真实存在）：手搓队列排好后**不需要新动作也会继续执行**，所以"holdout 窗口内无 agent 动作"挡不住提前排队的手搓。结论：最终三物必须机器限定（spec 已要求，正确），且这一个要求不能放松。
- 漏洞 B：中间体允许手搓意味着 agent 可提前囤晶圆喂机器。这不破坏评测——最终机器吞吐仍是瓶颈，自动化仍被度量——但 spec 应把"允许手搓的中间体白名单"写成显式清单，而不是一句"may be allowed"。
- 一个有利的 2.0 约束（文档明确）：**`"crafting"` 类别不能包含带流体原料/产物的配方**。如果晶圆配方用流体（见第 9 点，建议硫酸），晶圆就天然必须上机器，手搓边界自动收紧。
- 兜底：手搓速度受角色 crafting speed 限制，吞吐门槛定得足够高时纯手搓中间体在时间上不可行。

## 2. compute unit 形态 — 推荐真实 item

| 形态 | 实现成本 | 持续吞吐验证 | 防缓冲作弊 |
|---|---|---|---|
| 真实 item | 最低（item 原型 + 图标） | 进 `item_production_statistics`，引擎原生支持 | 缓冲不影响"窗口内产量差值"评分（见第 3 点）；脚本 `insert` 刷的货**不计入**产量统计 |
| fluid | 中（fluidbox 管线，FLE/agent 工具链更复杂） | `fluid_production_statistics`，机制相同 | 不能进箱子但能进储液罐，防缓冲优势≈0 |
| 虚拟统计量 | 最高（全部自写） | 完全自定义口径（可只在 powered&&working 时累计） | mod `storage` 与 agent 脚本天然隔离（见第 8 点），但对 agent 不可见，需要额外 remote interface 暴露观测 |

推荐真实 item：评分用产量统计而非库存，缓冲作弊在度量层面已被消除；item 还能进 FLE 的标准观测/物流，v0.2 经济层（卖算力）也直接可用。流体买不到任何实质防作弊收益，虚拟量则是在防御一个 v0.1 不存在的威胁模型。

## 3. 持续吞吐的度量 — 可行，能精确到"某物品在 [t1,t2] 的产量"

**重要 2.0 变化**：生产统计变为 per surface，入口是 `force.get_item_production_statistics(surface)`（[LuaForce](https://lua-api.factorio.com/latest/classes/LuaForce.html)），不是 1.1 的 `force.item_production_statistics` 直接属性。

两种测法（[LuaFlowStatistics](https://lua-api.factorio.com/latest/classes/LuaFlowStatistics.html)）：

- **主判据（推荐）**：t1 读 `stats.get_input_count(item_id)`，t2 再读，差值即窗口产量。累计整数，精确无舍入，单物品粒度。
- 诊断用：`stats.get_flow_count{name=id, category="input", precision_index=defines.flow_precision_index.one_minute, count=true, sample_index=k}` 可取历史采样（每档 300 个）。但注意两个口径坑：不带 `sample_index` 时返回的是该精度范围的**归一化平均速率**（按分钟），不是总量；且采样槽与任意 [t1,t2] 不对齐。所以只做趋势展示，不做通过判据。
- 逐机归因：`LuaCraftingMachine` 的 `products_finished` 可读，同样 t1/t2 差值，能定位是哪台数据中心节点产出的。

**误差/口径来源（spec 应写明）：**

1. 必须传对 surface——多表面时会漏计；本场景固定 nauvis，钉死即可；
2. 手搓也计入 production input → 回到第 1 点，最终物必须机器限定；
3. 脚本 `insert` / `create_entity` 刷的物品不计入 → 天然防"凭空刷货"，这是选 item 方案的隐藏红利；
4. `LuaFlowStatistics` 存在 `set_flow_count` / `reset` 写接口 → 拥有完整 Lua 的 agent 理论上可篡改，需配合第 8 点的威胁模型；
5. 配方完整跑完才计数（输出槽里未完成的周期不算）——口径保守，建议 spec 直接声明"以 `get_input_count` 差值为准"。

## 4. 数据中心节点原型 — 可行，标准 assembling-machine，但有 6 个坑

`assembling-machine` 同时持电输入 + 物品输入 + 物品输出是完全标准的配置：`energy_source = {type="electric", usage_priority="secondary-input", drain=...}` + `energy_usage` + `crafting_speed` + `crafting_categories`（[CraftingMachinePrototype](https://lua-api.factorio.com/latest/prototypes/CraftingMachinePrototype.html)）。陷阱清单：

1. **无配方时行为**：机器闲置，只耗 `drain`（若设了）。spec 说"耗电+消耗输入"——工作耗电由 `energy_usage` 承担；如果想要"通电即有待机成本"（利于 uptime 评分），显式设 `drain`，否则不设。这是 spec 需要二选一钉死的点。
2. 建议用 `fixed_recipe` 锁定 compute 配方：防机器被改作他用，也省 agent 一步 set_recipe，评测更确定。
3. 若配方含流体输入，机器必须声明 `fluid_boxes`，且该配方不能用 `"crafting"` 类别（第 1 点已述）。
4. `energy_usage`/`crafting_speed` 缺失会直接原型加载报错——这是好事，M1"无原型错误"验收能兜住。
5. 输出槽满会停机。评分按"产量"而非"开机时长"即不受影响；但 uptime 指标的定义要避开这个歧义。
6. 若吞吐门槛是额定值，建议不给 `module_slots`（或用 `allowed_effects` 限制），否则速度模块/信标会把额定吞吐变成变量。

## 5. 场景放置石英矿 — 可行，推荐"场景脚本放置 + map_gen_settings 清场"

两条机制路线，spec 的选择是对的：

- autoplace 世界生成：spec 明确不要 ✓（资源原型**不给** `autoplace` 即不进世界生成）；
- 脚本放置：control 阶段 `on_init` 里 `surface.create_entity{name="ffb-quartz-ore", position=..., amount=...}` 在固定坐标铺 patch，完全确定性。注意 `minable` 在 2.0 同样使用 `results` 数组格式（与配方一致，`result`/`count` 简写已移除）。

固定地图的机制选择：

- **推荐**：mod 自带 scenario（mod 内 `scenarios/<name>/`）+ 自定义 `map_gen_settings`（清空 `autoplace_controls`、关敌人/污染、关起始区域），地面本身确定性 + 脚本放置确定性 = 整体确定性；
- 不推荐作为唯一机制：打包 save.zip。存档对 Factorio 小版本升级脆弱（2.0.x 内部升级一般兼容，但 pin 版本策略下重建成本高），最多做缓存。
- spec 需补充：reset 语义契约。`on_init` 只在存档创建时跑一次——FLE 的 `reset(seed)` 若重建存档则天然重跑（OK）；若复用存档重置，需要 `on_configuration_changed` 或显式重置钩子配合。这是 FLE 适配层必须验证的集成点。

## 6. 贴图/图标 — 可行，最小可行量比想象小

- 图标：默认 `icon_size = 64`，文件实际尺寸必须与声明一致；`icons` 数组可分层；2.0 已移除 `hr_version`，高清图用 `scale = 0.5`。
- 机器世界贴图：2.0 的 assembling-machine 图形走 `graphics_set`（4 方向 animation + 可选 working_animation）。最小合法量：每台机器 1 张 spritesheet、四方向共用同图（方向感差但引擎合法）、1 帧静态。4 台机器 × 1 sheet 即可过 M1 的 "visibly distinct" 门槛——spec 把视觉质量留给 release review 而非像素测试，策略正确。
- **spec 资产清单漏了两类**：(a) 科技图标——spec 自己写了 "every new technology will have an original icon"，科技图标惯例 256×256，4 项科技 = 4 张，应计入资产总数（7 物品 + 4 机器 + 4 科技）；(b) 石英矿 resource entity 的 `stages` 地表贴图——这是第 8 类资产，spec 完全没提。

## 7. 科技树 — 可行，教科书做法

`TechnologyPrototype`：`prerequisites` 链 + `research_unit_ingredients`（base 科学包）+ `effects = {{type="unlock-recipe", recipe="ffb-..."}}`。4 项科技映射到链条四段即可（硅提纯 → 晶圆 → 加速器/机架 → 数据中心）。

场景预解锁两种写法：`on_init` 中 `force.technologies["ffb-silicon-refining"].researched = true`（会正常触发 unlock 效果），或直接 `force.recipes["..."].enabled = true` 绕过科技。**spec 需补充**：哪些科技开局解锁、哪些留给 agent 研究、研究消耗的 tick 是否计入 elapsed-ticks 评分——目前只写了 "technology unlocks"，决策没钉。

## 8. 与 FLE 共存 — 有坑，但结构性风险比表面看起来小

有利的一面（[storage 文档](https://lua-api.factorio.com/latest/auxiliary/storage.html) 明确）：**每个 mod 有独立的 control 阶段和独立的 `storage` 表**，事件各自投递、互不覆盖。agent 通过 RCON 执行的脚本运行在独立的 console script state，**改不到我们 mod 的 `storage`**。所以评分状态放 mod `storage` + 只读 `remote.add_interface("frontier-factory-bench", {get_metrics=...})` 暴露，是安全的架构。

真实风险点：

1. remote interface 命名冲突——用独特名即可；
2. 不要假设独占 `on_tick`；采样用 `script.on_nth_tick` 保持轻量（[LuaBootstrap](https://lua-api.factorio.com/latest/classes/LuaBootstrap.html)）；
3. FLE 的暂停/加速：一切度量基于 `game.tick` 差值，不用 wall clock；
4. **最大的信任问题**：FLE agent 的 Lua 是全能的——可以 `set_flow_count` 伪造统计、`crafting_progress = 1` 秒完成配方、直接改配方原型。mod 层面无法根除。**spec 需补充威胁模型声明**：v0.1 建议明确"合作式 agent + 全程 action/代码日志事后审计"，评分用三源交叉（产量统计差值 + 逐机 `products_finished` + 能耗采样一致性）提高事后可检测性，而不是承诺事前免疫。

## 9. spec 在 modding 层面的明显缺失/错误

- **写错**："coolant-like inputs"——base 2.0 没有冷却液。可用流体只有 water / steam / crude oil 系（heavy oil、light oil、petroleum gas）/ sulfuric acid / lubricant。建议晶圆配方用 sulfuric acid（蚀刻意象，且会强制晶圆上机器，见第 1 点），spec 应写成具体流体名。
- **写漏（2.0 变化）**：生产统计 per-surface——观测与评测的"production flows"都要带 surface 维度。
- **写漏**：2.0 配方格式 `ingredients`/`results` 需显式 `type` 字段（`result` 简写已废）。spec 无代码层面影响，但实现者按 1.1 教程抄会全部报错。
- **写漏**：compute unit 产出后的处置（堆积在箱子里？v0.2 才消耗？）。评分不依赖消耗，所以 v0.1 可以不管，但 spec 应显式说一句。
- **写漏**：评分度量源没钉死——"sustained throughput" 应直接写明 `get_input_count` 差值口径、窗口 tick 长度、uptime 定义。
- **写漏**：威胁模型（第 8 点）。
- **写漏**：资产计数（科技图标 + 石英矿地表贴图，第 6 点）。
- **写漏**：server rack 是 compute 配方的持续消耗输入，还是一次性建材？这直接影响配方设计和"防囤"语义，必须二选一写明。建议 rack 作为慢速消耗输入（如每 N 个 compute 耗 1 rack），让全链条在窗口期内都保持真实流动。
- 一个环境约束（spec 已正确处理 ✓）：base 2.0 无 quality 机制（Space Age 专属），正好与"不依赖 SA"一致；但信标/速度模块在 base 就有，吞吐门槛要么禁模块槽要么按含模块上限标定。

## 如果我来写 data/control 骨架，最关键的 5 个决策

1. **配方类别设计**：3 个自定义 category（`ffb-silicon-refining`、`ffb-advanced-assembly`、`ffb-compute`），加速器/机架/compute 三物全部机器限定 + `hide_from_player_crafting` + `allow_as_intermediate=false`；允许手搓的中间体用显式白名单写进 spec；晶圆配方含硫酸使其天然机器限定。
2. **compute unit = 真实 item**；通过判据 = `force.get_item_production_statistics(game.surfaces.nauvis).get_input_count(id)` 在 [t1,t2] 的差值 ≥ 阈值，逐机 `products_finished` 差值做归因交叉，全部口径写进任务定义。
3. **数据中心节点 = assembling-machine + `fixed_recipe` + electric `energy_source`（`energy_usage` + 小额 `drain`）+ 无模块槽**，额定吞吐由 `crafting_speed` 钉死，让"持续吞吐达标"有确定性的理论上限可验证。
4. **固定实验室图 = mod 内 scenario**：`map_gen_settings` 清场（无敌人、无 autoplace、关污染）+ `on_init` 用 `create_entity` 铺石英 patch、初始电源/箱子、预解锁 T1 科技；所有评测计时基于 `game.tick`，不用 wall clock。
5. **评测状态机放 mod control 的 `storage`**（与 agent 脚本天然隔离），对外只暴露一个唯一命名的只读 remote interface（`get_metrics` / `get_task_status`）；FLE 适配层只调这个接口，Python 侧不重建游戏内状态——这也让"换 agent 不改 benchmark"的成功定义在架构上成立。

总体判断：spec 的核心设计（机器限定最终物、holdout 窗口、场景放矿）在 Factorio 2.0 modding 层面全部成立，没有不可行项；主要工作是把它从"产品语言"钉到上面这些具体 API 口径上，并补上威胁模型和资产清单两处遗漏。
