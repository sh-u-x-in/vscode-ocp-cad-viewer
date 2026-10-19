"""ocp_vscode's transport: the websocket client, pointed at a VS Code viewer.

The client itself is `ocp_viewer_core.websocket` - the protocol, the framing,
the port discovery and the listener are the same for any host that talks to a
viewer over a websocket, and a second one needing them is what said they were
never this package's.

What is left here is what is genuinely VS Code's: the sentence printed when
several viewers are open and the editor is about to raise an input box, and the
module-level `set_port` / `get_port` / `find_and_set_port` that scripts and
the docs site's "Addressing a viewer" page have always had.
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

import os

from ocp_viewer_core.comms import MessageType
from ocp_viewer_core.websocket import (
    DEFAULT_HOST,
    WebSocketComms,
    comms_warning,
    default,
    port_check,
)

__all__ = [
    "MessageType",
    "VSCodeComms",
    "comms_warning",
    "default",
    "find_and_set_port",
    "get_host",
    "get_port",
    "is_pytest",
    "listener",
    "port_check",
    "send_backend",
    "send_command",
    "send_config",
    "send_data",
    "set_port",
]


def is_pytest():
    return os.environ.get("OCP_VSCODE_PYTEST") == "1"


class VSCodeComms(WebSocketComms):
    """A viewer in a VS Code panel.

    One method's worth of difference from the shared client: when more than one
    viewer is listening and we are inside a Jupyter kernel, the editor raises an
    input box above the cell, and the user has to be told to look at it.
    """

    def choose_port(self, ports):
        if self._in_kernel():
            print("\n=> 请在上方 VS Code 输入框中选择端口\n")
        return super().choose_port(ports)

    @staticmethod
    def _in_kernel():
        import sys  # noqa: PLC0415

        ipython = sys.modules.get("IPython")
        shell = ipython.get_ipython() if ipython is not None else None
        return shell.__class__.__name__ == "ZMQInteractiveShell"


# The one client this process talks to a viewer with. A module-level instance
# rather than module-level state: `show` binds to it once, and the functions
# below are the names scripts already use for it.
comms = VSCodeComms()


def set_port(port, host=DEFAULT_HOST):
    """Skip discovery and pin to a viewer."""
    comms.set_port(port, host)


def get_port():
    """The port in use, discovering one on first call."""
    if is_pytest():
        return 3939
    return comms.port


def get_host():
    return comms.host


def find_and_set_port():
    """Re-run discovery, after opening or closing a viewer."""
    comms.find_and_set_port()


def send_data(data, port=None, timeit=False):
    return comms._send(data, MessageType.DATA, port, timeit)


def send_config(config, port=None, title=None, timeit=False):
    return comms._send(config, MessageType.CONFIG, port, timeit)


def send_command(data, port=None, title=None, timeit=False):
    result = comms._send(data, MessageType.COMMAND, port, timeit)
    if isinstance(result, dict) and result.get("command") == "status":
        return result["text"]
    return result


def send_backend(data, port=None, timeit=False):
    return comms._send(data, MessageType.BACKEND, port, timeit)


def listener(callback):
    """The receiving loop, returned rather than run - a caller may want a thread.

    Also what delivers the backend's answers: `callback` returns them and the
    loop sends them, because the loop is what holds a connection to the viewer.
    """
    return comms.listener(callback)
