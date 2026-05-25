# NavalArt Hull Designer 转 Unity 可行性简报

## 结论

项目转到 Unity **可行，但不适合做“逐行移植”**。更稳妥的方式是把现有 Python/PyQt/OpenGL 项目拆成三层：文件格式与业务数据、几何生成算法、编辑器交互与渲染，然后在 Unity/C# 中重建编辑器壳、场景交互和网格渲染。现有 `.naprj` JSON 工程格式和 NavalArt `.na` XML 导入/导出逻辑价值很高，应优先保留兼容；PyQt GUI 与自研 pyqtOpenGL 基本需要重写。

综合判断：**中高可行性，迁移成本中高，建议做 Unity 重构版而不是原代码移植版。**

## 当前项目概况

项目是一个 Windows 桌面船体设计工具，入口为 `NavalArtHullDesigner.py`，主编辑器由 `main_editor.py` 驱动。技术栈以 Python 为主，依赖 PyQt5、NumPy、Pillow、ujson、PyYAML、matplotlib、psutil、requests，并实际依赖 PyOpenGL 与 assimp_py。构建方式使用 Nuitka 输出 Windows 独立包。

源码规模约 **2.5 万行 Python**。其中：

| 模块 | 代码量 | 迁移含义 |
|---|---:|---|
| `pyqtOpenGL` | 约 10.9k 行 | 自研 OpenGL 渲染、拾取、相机、网格、材质；Unity 中大多由引擎替代 |
| `GUI` | 约 6.5k 行 | PyQt 控件、布局、主题、属性面板；Unity UI Toolkit/uGUI 需要重写 |
| `ShipRead` | 约 2.5k 行 | 工程文件、组件模型、`.na`/`.naprj` 解析；迁移价值最高 |
| `ShipPaint` | 约 700 行 | 船体曲线与网格生成；可作为 C# 算法迁移重点 |
| `operation` | 约 430 行 | 撤销/重做操作栈；可按 Command 模式迁移 |
| `tests` | 58 个测试通过 | 有一定回归基础，但覆盖集中在工具函数、配置和网格法线 |

本地虚拟环境中执行 `pytest -q` 结果为 **58 passed, 13 warnings**。全局 Python 环境缺少 `OpenGL` 包，会在测试收集阶段失败，这说明环境声明与实际依赖不完全一致。

## 现有核心能力

1. 工程文件

`.naprj` 是 JSON 格式，核心数据包括项目名、作者、编辑时间、船体截面组、装甲截面组、舰桥、梯子、外部模型、参考图片。每个截面组以位置、旋转、颜色、装甲、曲率和多个截面节点表达。

2. NavalArt 文件兼容

`ShipRead/na_project.py` 读取 NavalArt `.na` XML 文件，将 `part`、可调船体块和主武器等映射为内部对象。`ShipRead/designer_project.py` 已实现将截面组导出为 NavalArt `id=0` 可调船体块的逻辑。

样例 `KMS Hindenburg.na` 中有 **2341 个 part**，其中 **651 个可调船体块**。这意味着 Unity 版要考虑大批量对象的生成、合批、编辑响应和导出性能。

3. 几何生成

船体核心几何来自截面节点：每个截面只记录左侧点，右侧通过对称生成；上下弧面由曲率参数控制；相邻截面之间生成对称柱体网格。核心算法集中在 `ShipPaint/HullItem.py` 与 `pyqtOpenGL/items/MeshData.py` 的 `SymetryCylinderMesh`。

这部分适合迁移到 Unity 的 `Mesh` 生成流程，算法复杂度可控，但需要重写数据结构、法线生成、顶点更新和坐标系适配。

4. 交互编辑

现有编辑器支持场景选择、框选、节点拖拽、相机平移/旋转/缩放、属性面板编辑、快捷键、复制粘贴、撤销重做。选择依赖 OpenGL 离屏 framebuffer 拾取；Unity 里应改为 Collider/Raycast 或 SceneView picking。

5. 完成度

项目已有主编辑流程、保存、打开、部分导出、主题配置、模型/图片引用和操作栈。仍有不少未完成项，包括新建工程、另存为、菜单导出入口、主题/相机设置弹窗、部分添加截面按钮、桥/梯子的正式网格绘制等。

## Unity 迁移匹配度

| 当前能力 | Unity 对应实现 | 难度 | 评价 |
|---|---|---:|---|
| `.naprj` JSON 读写 | C# DTO + Newtonsoft/System.Text.Json | 低 | 强烈建议兼容旧格式 |
| `.na` XML 读写 | `System.Xml` / LINQ to XML | 中 | 可迁移，需做导出一致性测试 |
| 截面参数模型 | ScriptableObject/纯 C# model | 低中 | 很适合 Unity 数据层 |
| 船体网格生成 | Unity `Mesh` 动态生成 | 中 | 可迁移，需坐标和法线验证 |
| OpenGL 渲染 | Unity Renderer/Material/Shader | 中 | 原渲染代码不可直接复用，但 Unity 替代能力强 |
| 选择/框选/节点拖拽 | Raycast、Handle、Gizmo、Editor Tool | 中高 | 需要重写交互体验 |
| PyQt 属性面板 | UI Toolkit 或 uGUI | 中高 | 代码不可复用，设计可复用 |
| 撤销/重做 | Command 模式或 Unity Undo | 中 | Runtime 版自己做，Editor 扩展可用 Unity Undo |
| 外部 OBJ 模型 | Unity 导入管线或 Runtime OBJ loader | 中 | 取决于是否运行时导入 |
| 参考图片 | Texture2D + Quad/Plane | 低中 | 简单可行 |
| Nuitka 打包 | Unity Build | 低 | 发行体验反而更好 |

## 主要风险

1. 不是语言迁移，而是框架重建

PyQt 信号、控件、窗口布局、OpenGL 拾取和 GLGraphicsItem 场景树都与 Unity 架构不同。强行逐行翻译会制造大量低价值工作，建议以现有行为为规格，从 Unity 重新实现。

2. 坐标系与单位转换

现有项目的船体延伸方向主要以 z 轴组织，左右对称使用 x，竖向使用 y；Unity 默认 y 为竖直、z 为前后。可以保留现有数学坐标并在渲染层转换，也可以整体改成 Unity 坐标。前者迁移更稳，后者长期更自然，但需要更多验证。

3. 几何导出一致性

`.naprj -> .na` 会把截面相邻节点转换为 NavalArt 可调船体块。Unity 版必须保证导出 XML 与当前 Python 版在位置、长度、高度、宽度、曲率、颜色、装甲上的结果一致，否则会破坏用户已有工作流。

4. 运行时导入模型

Python 版用 assimp_py 加载 OBJ/DAE 等模型。Unity 编辑器内导入模型很成熟，但打包后的运行时动态导入 OBJ 需要额外库或自写解析器。若目标是 Unity Editor 工具，风险较低；若目标是独立运行时工具，风险中等。

5. UI 工作量容易被低估

现有 `GUI` 模块虽然可重用代码不多，但沉淀了很多工作流：结构树、属性编辑、主题、状态栏、右键菜单、多标签、最近项目、AI Agent 面板。Unity 重做时需要先定义 MVP，否则容易陷入“把所有 PyQt 控件照搬”的范围膨胀。

6. 许可证与发行

仓库包含 GPL-3.0 许可证。若 Unity 版基于该代码形成衍生发行，需要确认 GPL 与 Unity 商业发布、第三方运行时库的兼容策略。内部自用风险较低，对外分发需提前处理。

## 推荐迁移方案

### 方案 A：Unity 独立运行时编辑器

把 Unity 作为最终用户使用的独立船体设计软件。优点是发行体验好、3D 交互能力强、后续可做更丰富的可视化；缺点是运行时 UI、文件对话框、运行时模型导入、Undo、窗口化体验都要自己做。

适合目标：面向玩家发布一个完整替代工具。

### 方案 B：Unity Editor 扩展工具

把船体设计器做成 Unity Editor 窗口，用 UI Toolkit、SceneView、Handles、Unity Undo 和资源导入管线。优点是迁移更快，可以借用 Editor 能力；缺点是用户必须安装 Unity，不适合普通玩家直接使用。

适合目标：先验证几何、导入导出、编辑体验，做内部工具或技术原型。

### 方案 C：双栈渐进迁移

保留 Python 版作为稳定工具，同时开发 Unity 核心原型。先让 Unity 读取 `.naprj` 并生成相同网格，再做编辑，最后做导出和完整 UI。优点是风险最低；缺点是短期维护两套。

适合目标：保护已有功能，同时逐步拿到 Unity 的 3D 体验收益。

**推荐：先走方案 C，用 Unity Editor 扩展做 MVP；验证通过后再决定是否产品化为独立运行时编辑器。**

## 阶段路线

### 第 0 阶段：规格冻结，1 周

- 固化 `.naprj` schema，并为样例工程建立版本化测试数据。
- 明确 Unity 目标形态：Editor 扩展还是独立运行时。
- 明确坐标系策略：内部保持 NavalArt/Python 坐标，显示层转换到 Unity。
- 用当前 Python 版导出若干 `.na` 作为黄金样例。

交付物：格式说明、黄金样例、Unity 项目骨架。

### 第 1 阶段：只读查看器，2 到 3 周

- C# 实现 `.naprj` 读取。
- 移植船体截面、装甲截面、参考图片、外部模型的最小数据结构。
- 移植 `SymetryCylinderMesh` 与曲率点生成。
- 在 Unity 中生成 Mesh、材质、线框或选中高亮。

交付物：Unity 能打开样例 `.naprj` 并显示船体，和 Python 截图/网格结果大体一致。

### 第 2 阶段：核心编辑 MVP，3 到 5 周

- 结构树与属性面板。
- 单选、多选、框选或基础点击选择。
- 节点拖拽、截面 z 移动、组位置/旋转/缩放。
- Command 模式撤销/重做。
- 保存 `.naprj`。

交付物：能完成现有核心船体截面编辑闭环。

### 第 3 阶段：导出与兼容，2 到 4 周

- C# 实现 `.na` XML 导出。
- 与 Python 版导出做字段级 diff。
- 验证 NavalArt 游戏内导入效果。
- 补齐颜色、装甲、曲率、文件路径、引用资源。

交付物：Unity 版导出的 `.na` 可被 NavalArt 正常使用。

### 第 4 阶段：完整产品化，4 到 8 周

- 新建/另存为/最近项目/设置/主题。
- 桥、梯子、栏杆/栏板正式网格化。
- 性能优化：Mesh 合并、对象池、增量更新。
- 打包、日志、异常恢复、用户文档。

交付物：可替代现有 Python 版的 Beta。

## 人力与周期粗估

单人开发：

- 技术原型：3 到 5 周。
- 可用 MVP：8 到 12 周。
- 接近当前桌面版功能完整度：3 到 5 个月。

两人开发：

- 一人负责数据/几何/导出，一人负责 Unity UI/交互。
- MVP 可压缩到 5 到 8 周。
- 完整版约 2 到 4 个月。

以上估算基于当前代码已有清晰数据结构和算法，但 UI/交互需要重建。

## 最小可行产品范围

建议 Unity MVP 只做这些：

- 打开 `.naprj`。
- 显示船体截面组与装甲截面组。
- 显示结构树。
- 选中截面/节点并编辑位置。
- 拖拽修改节点 x 值和移动截面 z。
- 保存 `.naprj`。
- 导出 `.na`。

暂缓：

- AI Agent 面板。
- 完整主题系统。
- 桥、梯子、栏杆的高级编辑。
- 运行时导入复杂模型格式。
- 多窗口编辑。

## 关键技术建议

1. 数据层与 Unity 对象分离

建立纯 C# 数据模型，例如 `ProjectData`、`HullSectionGroupData`、`HullSectionData`、`Node2D`。Unity 场景对象只做显示和交互，不直接作为保存格式。

2. 保持 `.naprj` 兼容

Unity 版应先读取旧 JSON，不要一开始设计新格式。需要新增字段时添加 `schema_version`，旧字段保持向后兼容。

3. 网格算法先做单元测试

把曲率点生成、对称点生成、顶底面、侧面、法线生成写成纯 C# 测试。先保证算法可测，再接 Unity Mesh。

4. 用增量更新而不是重建全场景

节点拖拽时只更新受影响截面及相邻截面的 Mesh，沿用当前 Python 版的局部重建思路。

5. 优先 Editor 扩展验证

EditorWindow + UI Toolkit + SceneView Handles 可以显著降低第一版交互成本。等核心能力稳定后，再评估独立运行时。

## 最终建议

建议立项迁移，但目标应定义为 **Unity 重构版 NavalArt Hull Designer**，而不是“把 Python 项目搬进 Unity”。可复用的核心资产是文件格式、组件抽象、几何规则、导出逻辑和测试样例；不可复用或低价值复用的是 PyQt 控件、自研 OpenGL 渲染框架、Nuitka 打包链路。

短期最优决策：先做一个 Unity 只读查看器加 `.na` 导出一致性验证。如果 2 到 3 周内可以稳定读取 `.naprj`、显示船体并导出接近 Python 版的 `.na`，则继续投入完整编辑器；如果几何一致性或 NavalArt 导出兼容出现严重偏差，再回到 Python 版渐进增强会更稳。
