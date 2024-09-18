# NavalArt Hull Designer

## 简介

NavalArt Hull Designer 是一个扩展工具，用于设计 NavalArt 游戏中的船体。这个工具旨在简化船体的设计过程。

经过初步的调研，我们发现大部分 NavalArt (下文简称NA) 玩家在设计船体时，需要花费大量的时间在微调船体的线型上。这个过程不仅繁琐，而且容易出现偏差，导致船体的线型不够流畅。因此，我们希望通过这个工具，帮助玩家更快速地设计出流线型的船体。

另外，我们还将尝试加入许多其他部件的建造功能：例如舰桥、栏杆、栏板、梯子等。这些功能将使玩家在设计船体时更加方便。

## 配置调试环境

### 环境

- Python 3.10
- 依赖库请参考 `requirements.txt`

### 安装步骤

1. 克隆此仓库到本地
   ```bash
   git clone https://github.com/JasonLee-p/NavalArtHullDesigner.git/
   cd NavalArtHullDesigner
   ```

2. 安装所需依赖
   ```bash
   pip install -r requirements.txt
   ```
   ###### 大陆推荐使用清华镜像源加速安装
   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

### 调试

运行主入口文件，以启动编辑器：
```bash
python NavalArtHullDesigner.py
```

### 构建可执行文件
```bash
python build.py
```

## 功能（预期）

- 提供直观的 GUI 供设计和编辑；
- 支持导入和导出 NavalArt 游戏设计文件，基于组件色彩进行映射；
- 提供非常方便的船体编辑功能：基于截面组设计船体（类似工艺战舰的进阶船体外壳）；
- 提供方便的舰桥设计功能：基于截面和厚度设计舰桥（类似工艺战舰的钢板）；
- 提供方便的栏杆，栏板，梯子设计功能；
- 支持导入模型或图片，用于设计参考；
- 使用机器学习模型，提供线型检查，预测船体线型，减少用户微调工作量，优化船体流线型；


## 如何贡献

- 您可以从以下几个方面贡献：
  - 提出新的功能需求；
  - 提出改进建议；
  - 提交代码；
  - 提交文档；
  - 提交测试用例；
  - 提交 bug 报告；
- 我们目前需要集中力量开发应用的核心部分：基础组件的渲染和操作功能（详情查看ShipPaint，ShipRead和pyqtOpenGL）