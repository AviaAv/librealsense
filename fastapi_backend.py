# use "uvicorn main:app --host 0.0.0.0 --port 8000" to run this backend and make it available as server side
# by running 'ipconfig' and looking under "Wireless LAN adapter Wi-Fi" you can see the ipv4 address on your lan and
# access as a client (even from another computer on the LAN) to <ip-address>:8000
# <ip-address>:8000/index is a very basic webpage that allows you to see depth stream, and toggle it

from fastapi import FastAPI, Body
import pyrealsense2 as rs
import cv2
import numpy as np
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.requests import Request
import random
import string
from pydantic import BaseModel

description = """
RealSense API provides a robust interface for interacting with Intel RealSense depth cameras. This API enables developers to unlock the full potential of depth sensing, from capturing and processing depth data to controlling camera settings and streaming video.

## Depth Streams

You can **read depth streams**.

## Camera Controls

You will be able to:

* **Create camera profiles** (_not implemented_).
* **Read camera settings** (_not implemented_).
"""

tags_metadata = [
    {
        "name": "camera-controls",
        "description": "**Camera Control Endpoints**",
    },
    {
        "name": "streams",
        "description": "*RealSense Streams*",
        "externalDocs": {
            "description": "RealSense Streams Documentation",
            "url": "https://github.com/IntelRealSense/librealsense",
        },
    },
    {
        "name": "status",
        "description": "Get the current status of the camera.",
    },
    {
        "name": "root",
        "description": "RealSense API root pages",
    },
]


app = FastAPI(
    title="RealSense API",
    description=description,
    summary="Unlock the power of RealSense.",
    version="1.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "RealSense Team",
        "url": "http://realsense.intel.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata
)



# Initialize the RealSense camera
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)
colorizer = rs.colorizer()
dev = pipeline.get_active_profile().get_device()

print(dev.query_sensors())
sensors = dev.query_sensors()
exposure_inputs = ""
exposure_input_scripts = ""

for s in sensors:
    base_path = s.name.replace(' ', '_')
    set_exp_path = f"{base_path}_exposure"
    get_exp_path = f"{base_path}_exposure/get"
    print(base_path, set_exp_path, get_exp_path)
    
    # TODO: we can iterate over the options like so:
    # print(f"Supported options for {s.name}: {[opt for opt in s.get_supported_options()]} ")

    def create_routes(sensor):
        global exposure_inputs, exposure_input_scripts

        def get_sensor_name():
            return {"message": sensor.name}

        def get_exposure():
            exposure = sensor.get_option(rs.option.exposure)
            return {"message": f"Exposure is {exposure}", "val" : exposure}

        def set_exposure(exposure: int = Body(...)):
            sensor.set_option(rs.option.exposure, exposure)
            return {"message": f"Exposure set to {exposure}", "val" : exposure}

        app.add_api_route(f"/{base_path}", get_sensor_name, methods=["GET"], tags=["camera-controls"])
        if s.supports(rs.option.exposure): # we probably can automate it iterating for every option
            app.add_api_route(f"/{get_exp_path}", get_exposure, methods=["GET"], tags=["camera-controls"])
            app.add_api_route(f"/{set_exp_path}", set_exposure, methods=["POST"], tags=["camera-controls"])

            exposure_inputs += f"""
                Set {s.name} exposure:
                <input type="number" id="set-{base_path}-exposure" value="0">
                <br/>
                """

            exposure_input_scripts += f"""
                document.getElementById('set-{base_path}-exposure').addEventListener('input', function(event) {{
                    const exposureValue = event.target.value;
                    fetch('/{set_exp_path}', {{
                        method: 'POST',
                        body: exposureValue,
                        headers: {{
                            'Content-Type': 'text/plain'
                        }}
                    }});
                }});
        
                fetch('/{get_exp_path}')
                    .then(response => response.json())
                    .then(data => {{
                        document.getElementById('set-{base_path}-exposure').value = data.val;
                    }});
                """

    create_routes(s)

# Flag to track the camera status
camera_on = True
show_depth = True
show_color = True

@app.get("/", tags=["root"],
         description="Print Hello RealSense",
         response_description="Return Hello RealSense")
def read_root():
    return {"message": f"Hello RealSense!"}


def encode_and_yield(frame):
    # Encode frame as JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    frame_bytes = buffer.tobytes()

    # Yield frame as part of a multipart response
    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def yield_empty_frame():
    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + b'\r\n')

@app.get("/color_stream", tags=["streams"])
def color_feed():
    def generate_frames():
        global camera_on, show_color
        while camera_on and show_color:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue

            # Convert to numpy array
            frame = np.asanyarray(color_frame.get_data())
            yield from encode_and_yield(frame)

        # if camera off, return empty frame
        yield from yield_empty_frame()

    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/depth_stream", tags=["streams"])
def depth_feed():
    def generate_frames():
        global camera_on, show_depth
        while camera_on and show_depth:
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            if not depth_frame:
                continue

            # Convert to numpy array
            frame = np.asanyarray(colorizer.colorize(depth_frame).get_data())
            yield from encode_and_yield(frame)

        # if camera off, return empty frame
        yield from yield_empty_frame()

    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


def status_to_on_off(property_on):
    return 'on' if property_on else 'off'


@app.post("/toggle_depth", tags=["camera-controls"])
def toggle_depth():
    global show_depth
    show_depth = not show_depth
    return {"message": f"Camera set depth to be {status_to_on_off(show_depth)}"}


@app.post("/toggle_color", tags=["camera-controls"])
def toggle_color():
    global show_color
    show_color = not show_color
    return {"message": f"Camera set color to be {status_to_on_off(show_color)}"}


@app.post("/toggle_camera", tags=["camera-controls"])
def toggle_camera():
    global camera_on
    camera_on = not camera_on
    if camera_on:
        pipeline.start(config)
    else:
        pipeline.stop()
    return {"message": f"Camera has set to be {status_to_on_off(camera_on)}"}


@app.get("/camera_status", tags=["status"])
def get_camera_status():
    global camera_on, show_color, show_depth
    return {"message": f"Camera is now {status_to_on_off(camera_on)}, depth is {status_to_on_off(show_depth)} "
                       f"and color is {status_to_on_off(show_color)}",
            "is_on" : camera_on, "depth_on": show_depth, "color_on" : show_color}


@app.get("/index", tags=["root"])
def index():
    return HTMLResponse(content=f"""
    <html>
    <body>
    <h1>RealSense Stream</h1>
    <img src="/color_stream" width="640" height="480" id="color-stream">
    <img src="/depth_stream" width="640" height="480" id="depth-stream">
    <form id="toggle-camera-form">
        <button type="submit" name="toggle_camera">Toggle Camera</button>
        <button type="submit" name="toggle_color">Toggle Color Stream</button>
        <button type="submit" name="toggle_depth">Toggle Depth Stream</button>
    </form>
    {exposure_inputs}
    <script>
    document.getElementById('toggle-camera-form').addEventListener('submit', function(event) {{
        event.preventDefault();
        const formData = new FormData(event.target);
        const action = event.submitter.name;
        const url = '/' + action;
        fetch(url, {{
            method: 'POST',
            body: formData
        }}).then(() => {{
            // timestamp is used to reload image from server
            document.getElementById('color-stream').src = '/color_stream?' + new Date().getTime(); 
            document.getElementById('depth-stream').src = '/depth_stream?' + new Date().getTime(); 
        }});
    }});
    {exposure_input_scripts}
    </script>
    </body>
    </html>
    """)
