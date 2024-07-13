# NavalArt Hull Editor

NavalArt Hull Editor 是一个扩展工具，用于设计和编辑 NavalArt 游戏中的船体。这个工具旨在简化船体的设计过程，使玩家能够更高效地创建和调整他们的船只。

## 项目结构

```plaintext
NavalArtHullEditor/
├── NavalArtHullEditor.py（主入口）
├── main_editor.py（主编辑器，包含主窗口和主要功能）
├── main_logger.py（日志和状态栏）
├── config_read.py（配置文件管理）
├── startWindow.py（启动窗口GUI）
├── funcs_utils.py（工具函数和类）
├── calculation.py（一些计算函数）
├── path_lib.py（初始化路径）
├── cv2_replacements.py（OpenCV 替代品）
├── ship_read/（读取和解析工程文件）
│   ├── SectionHandler/（工程文件组件）
│   │   ├── baseSH.py（组件基类）
│   │   ├── model.py（模型组件）
│   │   ├── ladder.py（梯子组件）
│   │   ├── armorSectionGroup.py（装甲组件）
│   │   ├── hullSectionGroup.py（船体组件）
│   │   ├── bridge.py（舰桥组件）
│   ├── na_project.py（.naprj工程文件）
│   ├── na_design.py（.na游戏设计文件读取）
├── ship_paint/
│   ├── HullItem.py（船体组件的绘制对象）
│   ├── （未来将添加其他工程文件组件的绘制对象）
├── operation/
│   ├── basic_op.py（操作基类以及操作栈）
│   ├── path_op.py（路径操作）
│   ├── section_op.py（截面操作）
│   ├── modelMatrix_op.py（位姿操作）
│   ├── （未来将添加其他操作）
├── predict/
│   ├── （未来将添加机器学习预测相关代码）
├── GUI/（GUI设计）
│   ├── main_widgets.py（主要窗口控件）
│   ├── element_structure_single_item.py（结构视图组件信息控件）
│   ├── element_structure_widgets.py（结构视图Tab控件）
│   ├── element_edit_widget.py（元素编辑控件）
│   ├── sub_element_edit_widgets.py（子组件编辑控件）
│   ├── basic_windows.py（基础小型窗口部件）
│   ├── basic_data.py（GUI基本数据）
│   ├── basic_widget/（基本控件）
│   ├── theme_config_color/（主题配置）
│   ├── UI_design/（UI设计.png文件）
├── pyqtOpenGL/
│   ├── GLGraphicsItem.py（绘图对象）
│   ├── camera.py（相机）
│   ├── GLViewWidget/（OpenGL视图窗口）
│   ├── items/（GLGraphicsItem的子类）
│   ├── ...
├── resources/
│   ├── models/（包含一个示例工程文件的3D模型）
├── sample_projects/
│   ├── 示例工程文件 sample.naprj（文件解析和储存格式为 JSON）
```

## 配置调试环境

### 环境

- Python 3.10
- 需要的库请参考 `requirements.txt`

### 安装步骤

1. 克隆此仓库到本地
   ```bash
   git clone https://github.com/JasonLee-p/NavalArtPluginNew.git/
   cd NavalArtPluginNew
   ```

2. 安装所需依赖
   ```bash
   pip install -r requirements.txt
   ```
   ###### 使用清华镜像源加速安装
   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

### 调试

运行主入口文件，以启动编辑器：
```bash
python NavalArtHullEditor.py
```

### 构建可执行文件
使用nuitka进行构建；

### 构建安装包
使用InstallShield进行构建；

## 功能（预期）

- 提供直观的 GUI 供设计和编辑；
- 支持导入和导出 NavalArt 游戏设计文件，基于组件色彩进行映射；
- 提供非常方便的船体编辑功能：基于截面组设计船体（类似工艺战舰的进阶船体外壳）；
- 提供方便的舰桥设计功能：基于截面和厚度设计舰桥（类似工艺战舰的钢板）；
- 提供方便的栏杆，栏板，梯子设计功能；
- 支持导入模型或图片，用于设计参考；
- 使用机器学习模型，提供线型检查，预测船体线型，减少用户微调工作量，优化船体流线型；
