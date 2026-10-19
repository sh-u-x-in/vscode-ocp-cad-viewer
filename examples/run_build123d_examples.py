"""
Run build123d examples with ocp_vscode viewer

This script runs all build123d examples and displays results in the viewer.
Run with a viewer open.

Usage:
    python examples/run_build123d_examples.py [example_name_filter]
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from ocp_vscode import set_viewer_config, Camera

# build123d examples relative to this script's location
_script_dir = Path(os.path.abspath(os.path.dirname(__file__)))
_build123d_examples_dir = _script_dir / "../../build123d/examples"
_build123d_ttt_dir = _script_dir / "../../build123d/docs/assets/ttt"


def run_example(path: Path) -> bool:
    """Run a single example and return True if successful."""
    print(f"\n{'='*60}")
    print(f"正在运行: {path.name}")
    print('='*60)

    with tempfile.TemporaryDirectory(prefix=f"build123d_example_{path.name}") as tmpdir:
        # Use examples dir for benchy (needs assets), otherwise temp dir
        cwd = tmpdir if "benchy" not in path.name else _build123d_examples_dir

        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=cwd,
            check=False,
        )

        if result.returncode != 0:
            print(f"失败: {path.name}(退出码 {result.returncode})")
            return False

        print(f"成功: {path.name}")

        # Reset camera and wait for key press
        set_viewer_config(reset_camera=Camera.ISO, zoom=1)
        input("按回车继续...")

        return True


def main():
    if not _build123d_examples_dir.exists():
        print(f"错误: 未找到 build123d 示例目录 {_build123d_examples_dir}")
        sys.exit(1)

    # Optional filter from command line
    name_filter = sys.argv[1] if len(sys.argv) > 1 else None

    # Collect examples
    examples = []
    for examples_dir in [_build123d_examples_dir, _build123d_ttt_dir]:
        if examples_dir.exists():
            for example in sorted(examples_dir.iterdir()):
                if example.name.startswith("_") or not example.name.endswith(".py"):
                    continue
                if name_filter and name_filter.lower() not in example.name.lower():
                    continue
                examples.append(example)

    if not examples:
        print("未找到示例" + (f"(筛选: '{name_filter}')" if name_filter else ""))
        sys.exit(1)

    print(f"共找到 {len(examples)} 个示例")

    # Run examples
    passed = 0
    failed = 0
    failed_names = []

    for example in examples:
        try:
            if run_example(example):
                passed += 1
            else:
                failed += 1
                failed_names.append(example.name)
        except KeyboardInterrupt:
            print("\n已被用户中断")
            break
        except Exception as e:
            print(f"错误: {example.name}: {e}")
            failed += 1
            failed_names.append(example.name)

    # Summary
    print(f"\n{'='*60}")
    print(f"汇总: {passed} 个通过,{failed} 个失败")
    if failed_names:
        print(f"失败列表: {', '.join(failed_names)}")
    print('='*60)


if __name__ == "__main__":
    main()
