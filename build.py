"""
用nuitka构建py程序
"""
import subprocess


"""
必要设置
"""
# 程序名称（必须）
PROGRAM_NAME = "NavalArtHullDesigner.py"
# 输出目录（必须）
OUTPUT_DIR = "release"

"""
基础设置
"""
# 图标路径（如./icon.ico）
ICON_PATH = './GUI/UI_design/ICO.ico'
# 是否生成独立包（推荐启用）
STANDALONE = True
# 是否生成单exe文件，若为False则生成文件夹
ONE_FILE = False

"""
程序在windows系统下的参数（可忽略）
"""
# Windows系统下公司名称
COMPANY_NAME = "JasonLee"
# Windows系统下产品名称
PRODUCT_NAME = "NavalArtHullDesigner"
# Windows系统下文件版本
FILE_VERSION = "0.9.0.0"
# Windows系统下产品版本
PRODUCT_VERSION = "0.9.0.0"
# Windows系统下文件描述
FILE_DESCRIPTION = "NavalArtHullDesigner"

"""
管理依赖包和资源（可忽略）
"""
# 启用的库，例如pyqt5
ENABLED_PLUGINS = ['pyqt5']
# 不导入的模块（自己的或第三方的）
#（加*表示
NOFOLLOW_IMPORT_TO = [
    "*.tests", "*.tests.*", "tests.*", "*.test", "*.test.*", "test.*", "test"
]
# 包含的数据目录
INCLUDE_PACKAGE_DATA = ['sample_projects', 'resources']
# 包含的文件
INCLUDE_DATA_FILES = []

"""
其他编译参数（可忽略）
"""
# 是否为debug模式（不推荐启用）
DEBUG = False
# 是否显示编译进度（推荐启用）
SHOW_PROGRESS = True
# 是否显示依赖项
SHOW_MODULES = True


def build_command(_program_name: str) -> str:
    """
    构建 Nuitka 命令行参数。

    :return: 构建的命令字符串
    :rtype: str
    """
    # 列表类型参数：
    enabled_plugin_param = f"--enable-plugin={','.join(ENABLED_PLUGINS)} " if ENABLED_PLUGINS else ""
    nofollow_import_to_param = f"--nofollow-import-to={','.join(NOFOLLOW_IMPORT_TO)} " if NOFOLLOW_IMPORT_TO else ""
    include_package_data_param = f"--include-package-data={','.join(INCLUDE_PACKAGE_DATA)} " if INCLUDE_PACKAGE_DATA else ""
    include_data_files_param = f"--include-data-files={','.join(INCLUDE_DATA_FILES)} " if INCLUDE_DATA_FILES else ""
    # 字符串类型参数：
    company_name_param = f"--windows-company-name={COMPANY_NAME} " if COMPANY_NAME else ''
    product_name_param = f"--windows-product-name={PRODUCT_NAME} " if PRODUCT_NAME else ''
    file_version_param = f"--windows-file-version={FILE_VERSION} " if FILE_VERSION else ''
    product_version_param = f"--windows-product-version={PRODUCT_VERSION} " if PRODUCT_VERSION else ''
    file_description_param = f"--windows-file-description={FILE_DESCRIPTION} " if FILE_DESCRIPTION else ''
    icon_param = f"--windows-icon-from-ico={ICON_PATH} " if ICON_PATH else ''
    # 生成指令
    command = (
        f"nuitka "
        f"{'--standalone ' if STANDALONE else ''}"
        f"{'--onefile ' if ONE_FILE else ''} "
        
        f"{'--python-debug ' if DEBUG else ''}"
        f"--lto=no "
        f"--mingw64 "
        f"{'--show-progress ' if SHOW_PROGRESS else ''}"
        f"{'--show-modules ' if SHOW_MODULES else ''}"

        f"{company_name_param}"
        f"{product_name_param}"
        f"{file_version_param}"
        f"{product_version_param}"
        f"{file_description_param}"
        
        f"{enabled_plugin_param}"
        f"{nofollow_import_to_param}"
        f"{include_package_data_param}"
        f"{include_data_files_param}"
        
        f"--output-dir={OUTPUT_DIR} "
        f"{icon_param}"
        f"{_program_name}"
    )
    return command.strip()


def bulid(program_name: str) -> None:
    """
    用nuitka构建py程序
    :param program_name: 程序名称，带.py后缀
    :return: None
    """
    command = build_command(program_name)
    print(f"执行命令: {command}")
    try:
        subprocess.run(command, check=True, shell=True)  # shell=True 用于支持 Windows 系统
        print(f"{program_name}构建成功")
    except subprocess.CalledProcessError as e:
        print(f"{program_name}构建失败: {e}")


if __name__ == '__main__':
    bulid(PROGRAM_NAME)
