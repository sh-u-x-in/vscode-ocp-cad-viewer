# OCP CAD Viewer 中文版(fork)

这是由 [sh-u-x-in](https://github.com/sh-u-x-in) 维护的 **vscode-ocp-cad-viewer 中文版 fork**,版本对齐上游 **4.2.0**。本 fork **不发布到 VS Code 应用商店**,请从本仓库的 [Releases](https://github.com/sh-u-x-in/vscode-ocp-cad-viewer/releases) 下载 `.vsix` 安装。英文原版说明见 [README.en.md](README.en.md)。

> 本仓库专注于界面汉化与 3D 视图标签接线,功能与上游 4.2.0 保持一致。

![概览](screenshots/overview.png)

## 这是什么

_OCP CAD Viewer_ 是一个在 VS Code 中显示 [CadQuery](https://github.com/cadquery/cadquery) 与 [build123d](https://github.com/gumyr/build123d) 模型的扩展,底层使用 [three-cad-viewer](https://github.com/bernhard-42/three-cad-viewer) 渲染。

一段典型的使用代码:

```python
# build123d
from build123d import Box
from ocp_vscode import show

show(Box(1, 2, 3))
```

```python
# CadQuery
import cadquery as cq
from ocp_vscode import show

show(cq.Workplane().box(1, 2, 3))
```

## 汉化架构:双表方案

本 fork 的界面文案分两层处理:

1. **VS Code 扩展层(官方 l10n 查表)**
   - `package.json` 中所有用户可见文案改为 `%key%` 占位符;
   - `package.nls.json` 为英文原文,`package.nls.zh-cn.json` 为中文;
   - 代码层字符串经 `vscode.l10n.t(...)` 包装,译文在 `l10n/bundle.l10n.zh-cn.json`;
   - 该层**自动跟随 VS Code 的显示语言**,无需额外设置。

2. **3D 视图层(labels 接缝)**
   - 标签通过 three-cad-viewer 的 labels 接缝注入,语言包位于 `resources/labels/zh-cn.json`;
   - 查看器初始化时由扩展读取并放入 `init` 消息的 `settings.labels`;
   - 由设置 `OcpCadViewer.view.language` 控制:
     - `auto`(默认):跟随 VS Code 显示语言(以 `zh` 开头即中文);
     - `en`:英文;
     - `zh-CN`:中文。
   - 设置变更即时生效(已打开的查看器会自动重载);读取或解析语言包失败时自动回退英文。
   - 切换后重新打开查看器生效;读取或解析语言包失败时自动回退英文。

命令 ID、配置键、`contextValue`、消息类型等内部标识始终保持英文,不做翻译。

## 安装

### 前置条件

- Microsoft VS Code 1.85.0 或更高版本;
- 已安装 [Python 扩展](https://marketplace.visualstudio.com/items?itemName=ms-python.python);
- 用于 CAD 开发的 Python 环境中可使用 `python` 以及 `pip` 或 `uv pip`。

### 安装 vsix

1. 打开 [Releases](https://github.com/sh-u-x-in/vscode-ocp-cad-viewer/releases),下载最新的 `.vsix`;
2. 在 VS Code 中打开扩展视图,点击右上角 `...` → **Install from VSIX...**,选择下载的文件;
3. 或使用命令行:

    ```bash
    code --install-extension ocp-cad-viewer-<版本>.vsix
    ```

VSCodium / code-server 也可用同样的 vsix 方式安装。

### 安装 Python 包

扩展需要配套的 Python 包 `ocp-vscode`:

```bash
pip install ocp-vscode
```

或在虚拟环境中使用 `uv add ocp-vscode`。安装后打开扩展侧边栏,按 **快速安装 build123d** / **快速安装 CadQuery** 完成依赖安装。

## 从源码构建

```bash
yarn install        # 或 npm install
npx tsc -p ./
npx @vscode/vsce package
```

3D 视图的 labels 接缝依赖 [sh-u-x-in/three-cad-viewer](https://github.com/sh-u-x-in/three-cad-viewer) 的接缝分支。主线会将该分支以 git 依赖形式集成;在集成完成前,请勿直接修改 `package.json` 的依赖版本。

## 同步上游

```bash
git remote add upstream https://github.com/bernhard-42/vscode-ocp-cad-viewer.git
git fetch upstream
git merge upstream/main
```

合并后请同步检查 `package.nls*.json`、`l10n/bundle.l10n.zh-cn.json` 与 `resources/labels/zh-cn.json`,补齐上游新增文案。

## 使用与文档

- 详细文档(英文,上游维护):[bernhard-42.github.io/ocp_viewer_docs](https://bernhard-42.github.io/ocp_viewer_docs/)
- [安装与 Quickstart](https://bernhard-42.github.io/ocp_viewer_docs/viewers/ocp_vscode/installation/)
- [查看器与库管理器](https://bernhard-42.github.io/ocp_viewer_docs/viewers/ocp_vscode/managers/)
- [Python `show` 命令](https://bernhard-42.github.io/ocp_viewer_docs/show/)
- [故障排除](https://bernhard-42.github.io/ocp_viewer_docs/viewers/ocp_vscode/troubleshooting/)

![运行示例](screenshots/ocp_vscode_run.png)

## 致谢与反馈

- 感谢上游作者 [Bernhard Walter](https://github.com/bernhard-42) 及 CadQuery、build123d、three-cad-viewer 社区。
- 与汉化无关的功能问题、崩溃与安装问题,请优先反馈到[上游仓库](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues)。
- 翻译错误、漏译、术语不一致等汉化问题,请在本仓库提交 [Issue](https://github.com/sh-u-x-in/vscode-ocp-cad-viewer/issues)。
