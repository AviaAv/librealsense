# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2026 RealSense, Inc. All Rights Reserved.

import importlib.util
import pytest

# import-module-name → pip package name. Used purely to render a readable
# error if a dep is missing on the agent. Jenkins is expected to install
# wrappers/rest-api/requirements.txt + unit-tests/wrappers/rest-api/requirements.txt
# during its Install Requirements stage.
_REQUIRED_MODULES = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "pydantic": "pydantic",
    "multipart": "python-multipart",  # FastAPI File/UploadFile route registration
    "aiortc": "aiortc",
    "socketio": "python-socketio",
    "cv2": "opencv-python",
    "numpy": "numpy",
    "httpx": "httpx",  # FastAPI TestClient
}


@pytest.fixture(autouse=True)
def rest_api_packages():
    """Without this, collection blows up inside FastAPI's route registration
    (e.g. ``Form data requires "python-multipart"``) instead of naming the
    install step that is missing."""
    missing = [
        pip_name for mod, pip_name in _REQUIRED_MODULES.items()
        if importlib.util.find_spec(mod) is None
    ]
    if missing:
        pytest.fail(
            "rest-api wrapper: missing required Python package(s): "
            + ", ".join(missing)
            + ".\nInstall via:\n"
            "  pip install -r wrappers/rest-api/requirements.txt\n"
            "  pip install -r unit-tests/wrappers/rest-api/requirements.txt"
        )
