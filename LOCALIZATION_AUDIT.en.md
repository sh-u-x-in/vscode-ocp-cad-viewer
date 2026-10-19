# Localization Audit — OCP CAD Viewer 4.2.0 (Chinese Edition)

- Audit date: 2026-10-19
- Upstream base: bernhard-42/vscode-ocp-cad-viewer `4.2.0` (commit `f939251`)
- This repository: 10 commits on top of the base (localization `079f444` … fixes `364d0af`; diagnostic logging removed before release)
- Seam build: sh-u-x-in/three-cad-viewer branch `i18n-labels-5.1.3` (based on upstream `060536e` / v5.1.3, 5 commits, latest `e294c7c`)
- Chinese version: [LOCALIZATION_AUDIT.zh-CN.md](./LOCALIZATION_AUDIT.zh-CN.md)

## 1. Scope and architecture

| Layer | Mechanism | Size |
|---|---|---|
| VS Code chrome (commands / sidebar / settings / notifications) | Official l10n: `package.nls.json` + `package.nls.zh-cn.json` (%key% placeholders, 78 keys); `vscode.l10n.t()` + `l10n/bundle.l10n.zh-cn.json` (80 keys) | 158 keys |
| 3D viewer (toolbar / tabs / help / measure / studio / hover) | labels seam: `resources/labels/zh-cn.json` (297 keys) injected into `Display(labels)` via the init message; every UI string construction site in the source goes through `t()` with English fallback | 297 keys |
| Python side (`ocp_vscode/`) and example scripts (`examples/`) | Direct Chinese (port-selection prompt, measurement backend help/errors, example runner console output) | ~15 strings |

Language setting `OcpCadViewer.view.language` (`auto`/`en`/`zh-CN`, default `auto`, follows the VS Code display language); changing it reloads an open viewer immediately. The seam build ships as vendored files under `resources/viewer/`; the extension no longer depends on the npm package `three-cad-viewer` at runtime (removed from dependencies).

## 2. Verification matrix

| Item | Result |
|---|---|
| Seam source tests (full three-cad-viewer suite + new i18n / distance-panel cases) | 46 files / **1481 passed** / 0 failed |
| Seam lint (`eslint src/`) | Pass |
| Main repo TypeScript compile (`tsc -p ./`) | Pass |
| l10n key coverage: package.json %key% ↔ both tables | 78/78/0 missing |
| l10n key coverage: src `t()` literals ↔ bundle table | 80/80/0 missing |
| labels completeness: 58/58 static `t()` keys; dynamic keys (20 geometry types + measure rows + hover fragments) filled per the upstream enums | 297 keys |
| Python files `py_compile` | Pass |
| Final VSIX audit (8 checks: version / seam / zero-Chinese bundle / labels / injection / l10n tables / no npm dependency / vendor path) | All pass |
| Comparison-coupled strings (yes/no, install, running state) and render-layer key normalization (idempotent formatKey) | Synced, with dedicated tests |

## 3. Intentionally kept in English

- Brands and proper nouns: OCP CAD Viewer, Poly Haven, ACES Filmic, PBR Neutral, San Giuseppe Bridge;
- The shape filter dropdown (All/Vertex/Edge/Face/Solid) was historically excluded because its selection logic read the rendered text; the seam now derives state from the clicked element, so **it is localized today** (全部/顶点/边/面/实体);
- XYZ axis letters, numbers, and the `↔`/`≈`/`⇒` symbols; command IDs, configuration keys, `contextValue`, message types;
- Output-channel logs (`output.debug/info/error`, ~123 lines) — kept for upstream-comparable troubleshooting;
- Occasional dynamic values returned by the Python (BRep) measurement backend without a matching key fall back to English; add a key to translate.

## 4. Known boundaries (all upstream behavior, not introduced by localization)

1. The Viewer Manager tree refresh is coupled to the Library Manager section being rendered (upstream `libraryManager.ts` detection loop triggers `statusManager.refresh`);
2. Measurements between closed solids intentionally omit the angle/reference/direction rows (area-weighted normals sum to ~0);
3. Measured numbers carry no unit conversion; they are raw model coordinates per the ecosystem convention (1 modeling unit = 1 mm);
4. The VS Code chrome follows the **editor display language** (official l10n) and is not controlled by the `view.language` setting — that setting only governs the 3D view.

## 5. Maintenance guide

**Upgrading three-cad-viewer**:

```bash
cd <three-cad-viewer clone>
git fetch upstream && git rebase upstream/master i18n-labels-5.1.3   # resolve conflicts
yarn install && npx vitest run --no-file-parallelism && yarn lint
yarn build && cp dist/three-cad-viewer.esm.js dist/three-cad-viewer.css <this repo>/resources/viewer/
```

Open the viewer and verify; keys whose wording changed fall back to English gracefully — extend `resources/labels/zh-cn.json` accordingly.

**Adding a translation**: append `"English source": "中文"` to `resources/labels/zh-cn.json` and reopen the viewer (dynamic keys use the English text rendered at runtime).

**Seam patch index** (5 commits on the branch): labels API + static template localization; filter dropdown keyed by element identity (prerequisite for translating it); translator parameter for the hover status line; idempotent formatKey (digit spacing normalized — `point 1` no longer became `point  1` and missed the lookup).

## 6. License and attribution

All functionality is the work of upstream author Bernhard Walter ([bernhard-42](https://github.com/bernhard-42)), licensed Apache-2.0. This repository only translates UI strings and vendors a localized seam build — please report functional issues to the [upstream repository](https://github.com/bernhard-42/vscode-ocp-cad-viewer); translation corrections are welcome as Issues/PRs here.
