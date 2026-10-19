# 汉化审核报告 — OCP CAD Viewer 4.2.0 中文版

- 审核日期:2026-10-19
- 上游基准:bernhard-42/vscode-ocp-cad-viewer `4.2.0`(提交 `f939251`)
- 本仓库提交:基准之上共 10 个提交(汉化 `079f444`…修复 `364d0af`,诊断日志已撤除)
- 接缝构建:sh-u-x-in/three-cad-viewer 分支 `i18n-labels-5.1.3`(基于上游 `060536e` / v5.1.3,5 个提交,最新 `e294c7c`)
- 英文版:[LOCALIZATION_AUDIT.en.md](./LOCALIZATION_AUDIT.en.md)

## 一、汉化范围与架构

| 层 | 机制 | 规模 |
|---|---|---|
| VS Code 原生层(命令/侧边栏/设置页/通知) | 官方 l10n:`package.nls.json` + `package.nls.zh-cn.json`(%key% 占位,78 键);`vscode.l10n.t()` + `l10n/bundle.l10n.zh-cn.json`(80 键) | 158 键 |
| 3D 视图层(工具栏/标签页/帮助/测量/Studio/悬停) | labels 接缝:`resources/labels/zh-cn.json`(297 键)经 init 消息注入 `Display(labels)`,源码内所有 UI 字符串构造点经 `t()` 查表,英文回退 | 297 键 |
| Python 端(`ocp_vscode/`)与示例脚本(`examples/`) | 直接中文(端口选择提示、测量后端帮助与报错、示例运行器控制台输出) | ~15 处 |

语言设置 `OcpCadViewer.view.language`(`auto`/`en`/`zh-CN`,默认 `auto`,跟随 VS Code 显示语言),变更即时重载已打开的查看器。三维接缝构建以 vendor 方式随附于 `resources/viewer/`,运行时不依赖 npm 包 `three-cad-viewer`(已从依赖移除)。

## 二、验证矩阵

| 项目 | 结果 |
|---|---|
| 接缝源码测试(three-cad-viewer 全量 + 新增 i18n/距离面板用例) | 46 文件 / **1481 通过** / 0 失败 |
| 接缝 lint(`eslint src/`) | 通过 |
| 主仓库 TypeScript 编译(`tsc -p ./`) | 通过 |
| l10n 键覆盖:package.json %key% ↔ 双语表 | 78/78/0 缺失 |
| l10n 键覆盖:src `t()` 字面量 ↔ bundle 表 | 80/80/0 缺失 |
| labels 完整性:源码 t() 静态键 58/58;动态键(几何类型 20 种 + 测量行 + 悬停片段)按上游枚举全集补齐 | 297 键 |
| Python 文件 `py_compile` | 通过 |
| VSIX 终态审计(8 项:版本/接缝/零中文 bundle/labels/注入/l10n 双表/无 npm 依赖/vendor 路径) | 全部通过 |
| 参与逻辑比较的文案(是/否、安装、运行中等)与渲染层查表归一(formatKey 幂等) | 已同步并有专项测试 |

## 三、有意保留英文清单

- 品牌与专有名词:OCP CAD Viewer、Poly Haven、ACES Filmic、PBR Neutral、San Giuseppe Bridge;
- 测量类型过滤下拉(All/Vertex/Edge/Face/Solid)历史上因按渲染文本查状态被排除;接缝已改为按元素身份取键,**现已纳入汉化**(全部/顶点/边/面/实体);
- XYZ 轴字母、数字与 `↔`/`≈`/`⇒` 符号;命令 ID、配置键、`contextValue`、消息类型;
- 输出通道日志(`output.debug/info/error`,约 123 条)——便于对照上游排查;
- Python 后端(BRep 测量)返回的个别动态值如无对应键,回退英文,补键即译。

## 四、已知边界(均为上游行为,非汉化引入)

1. 查看器管理器的刷新耦合在库管理器栏目的渲染上(上游 `libraryManager.ts` 检测循环触发 `statusManager.refresh`);
2. 闭合实体之间的测量有意省略角度/参考/方向行(加权法线和≈0,无意义);
3. 测量数字无单位换算,按生态惯例(1 建模单位 = 1 mm)显示原始模型坐标;
4. VS Code 原生层语言跟随**编辑器显示语言**(官方 l10n 机制),不受 `view.language` 设置控制——该设置仅管辖 3D 视图。

## 五、维护指南

**升级 three-cad-viewer**:

```bash
cd <three-cad-viewer 克隆>
git fetch upstream && git rebase upstream/master i18n-labels-5.1.3   # 解决冲突
yarn install && npx vitest run --no-file-parallelism && yarn lint
yarn build && cp dist/three-cad-viewer.esm.js dist/three-cad-viewer.css <本仓库>/resources/viewer/
```

构建后打开查看器实测;措辞变化的键会优雅回退英文,按输出补 `resources/labels/zh-cn.json` 即可。

**补一条翻译**:在 `resources/labels/zh-cn.json` 加一行 `"英文原文": "中文"`,重开查看器生效(动态键以渲染时的英文原文为准)。

**补丁内容索引**(接缝分支 5 个提交):labels 接口与静态模板本地化;过滤下拉按元素取键(可翻译的前提);悬停状态行翻译参数;formatKey 幂等化(数字前空格归一,`point 1` 不再变 `point  1` 导致查表失配)。

## 六、许可与归属

全部功能归属上游作者 Bernhard Walter([bernhard-42](https://github.com/bernhard-42)),遵循 Apache-2.0。本仓库改动仅为界面文案汉化与接缝构建,请向[上游仓库](https://github.com/bernhard-42/vscode-ocp-cad-viewer)反馈功能问题;汉化勘误欢迎在本仓库提 Issue/PR。
