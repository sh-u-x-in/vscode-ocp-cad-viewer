"""`python -m ocp_vscode --backend`: the measurement backend for a VS Code viewer.

`controller.ts` spawns this with the port of the viewer it has just opened.
The backend itself is `ocp_viewer_core.backend`, shared with every host; what
this module supplies is the transport, which is the only part that is ours.

Run with no arguments it points at `ocp_viewer`, which is the standalone
viewer - that used to be started from here.
"""

#
# Copyright 2025 Bernhard Walter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import argparse

from ocp_viewer_core.backend import ViewerBackend

from ocp_vscode.comms import comms, set_port


MOVED = """
独立版 OCP 查看器现已并入 ocp_viewer 包

    安装:`[uv] pip install ocp_viewer`
    运行:`python -m ocp_viewer`
    使用:`from ocp_viewer import show, ...`
"""


def main():
    # MOVED as the epilog too, because `--help` exits inside parse_args, before
    # the no-arguments branch below can print it - and `--help` is the other
    # thing people type when the old command stops starting a viewer.
    parser = argparse.ArgumentParser(
        prog="python -m ocp_vscode",
        description="OCP CAD Viewer 测量后端",
        epilog=MOVED,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--backend",
        action="store_true",
        help="运行测量后端(本模块的用途)",
    )
    parser.add_argument("--port", type=int, help="查看器监听的端口")
    args = parser.parse_args()

    # `python -m ocp_vscode` with no arguments started the standalone viewer for
    # years, so that is the command people will type. Say where it went rather
    # than answering with an argparse usage line.
    if not args.backend:
        print(MOVED)
        return

    if args.port is None:
        parser.error("--backend 需要 --port")

    # The backend takes nothing: it computes an answer and returns it. Driving
    # it and delivering that answer are this host's, and both are the listener's
    # - it is the thing with a connection to the viewer.
    set_port(args.port)
    backend = ViewerBackend()

    try:
        backend.start()
        comms.listener(backend.handle_event)()
    except ConnectionRefusedError:
        print(
            f"无法连接到端口 {args.port} 上的 OCP CAD Viewer。\n"
            "这是测量后端,它连接的是一个已经在运行的查看器。\n"
            "如需独立查看器,请使用 `python -m ocp_viewer`。"
        )
    except Exception as ex:  # noqa: BLE001
        print(ex)


if __name__ == "__main__":
    main()
