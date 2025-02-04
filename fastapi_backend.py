# use "uvicorn fastapi_backend:app --host 0.0.0.0 --port 8000" to run this backend and make it available as server side
# by running 'ipconfig' and looking under "Wireless LAN adapter Wi-Fi" you can see the ipv4 address on your lan and
# access as a client (even from another computer on the LAN) to <ip-address>:8000
# <ip-address>:8000/index is a very basic webpage that allows you to see depth stream, and toggle it

from fastapi import FastAPI, Body, HTTPException
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

def is_checkbox(opt_range):
    # An option is considered a checkbox if the range is from 0 to 1 with a step of 1
    return opt_range.max == 1.0 and opt_range.min == 0.0 and opt_range.step == 1.0

def is_enum(opt, opt_range,s):
    if opt_range.step < 0.9:
        return False
    i = opt_range.min
    while i <= opt_range.max:
        #print(s.get_option_value_description( opt, i ), "for option", opt.name, "val:", i)
        if (s.get_option_value_description(opt, i)) is None:
            return False
        i += opt_range.step

    return True


def generate_option_script(opt, sensor, set_opt_path, get_opt_path):
    opt_range = sensor.get_option_range(opt)

    if is_enum(opt, opt_range, sensor):  # Enum -> Select Dropdown
        return f"""
            document.getElementById('set-{set_opt_path}').addEventListener('change', function(event) {{
                fetch('/{set_opt_path}', {{
                    method: 'POST',
                    body: JSON.stringify(event.target.value),
                    headers: {{ 'Content-Type': 'application/json' }}
                }});
            }});

            fetch('/{get_opt_path}')
                .then(response => response.json())
                .then(data => {{
                    let selectElem = document.getElementById('set-{set_opt_path}');
                    let option = selectElem.querySelector(`option[value="${{data.val}}"]`);
                    if (option) option.selected = true;
                }});
        """

    elif is_checkbox(opt_range):  # Checkbox -> Binary Toggle
        return f"""
            document.getElementById('set-{set_opt_path}').addEventListener('change', function(event) {{
                fetch('/{set_opt_path}', {{
                    method: 'POST',
                    body: JSON.stringify(event.target.checked ? 1 : 0),
                    headers: {{ 'Content-Type': 'application/json' }}
                }});
            }});

            fetch('/{get_opt_path}')
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('set-{set_opt_path}').checked = (data.val == 1);
                }});
        """

    else:  # Regular Value -> Slider
        return f"""
            document.getElementById('set-{set_opt_path}').addEventListener('change', function(event) {{
                fetch('/{set_opt_path}', {{
                    method: 'POST',
                    body: JSON.stringify(event.target.value),
                    headers: {{ 'Content-Type': 'application/json' }}
                }});
            }});

            fetch('/{get_opt_path}')
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('set-{set_opt_path}').value = data.val;
                }});
        """

def draw_option(opt, s, set_opt_path):
    opt_range = s.get_option_range(opt)
    # Check if the option is an enum
    if is_enum(opt, opt_range, s):
        return draw_combobox(opt,s, set_opt_path)
    # Check if the option is a checkbox
    elif is_checkbox(opt_range):
        return draw_checkbox(opt_range, set_opt_path)
    # Otherwise, draw a slider
    else:
        return draw_slider(opt_range, set_opt_path)


def get_combo_labels(opt, opt_range, s):
    selected = None
    counter = 0
    labels = []
    min = int(opt_range.min)
    max = int(opt_range.max)
    step = int(opt_range.step)
    # Iterate through the range to get labels
    for i in range(min, max + 1, step):
        label = s.get_option_value_description(opt, i)  # Replace "example_option" with the actual option name if needed
        labels.append(label)

        # Check the type of the value and determine if it is selected
        if isinstance(opt_range.default, str):
            if label == opt_range.default:
                selected = counter
        else:
            if abs(i - opt_range.default) < 0.001:
                selected = counter

        counter+=1

    return labels, selected

def draw_combobox(opt, s, set_opt_path):
    opt_range = s.get_option_range(opt)
    options, selected = get_combo_labels(opt, opt_range, s)

    options_html = ''.join(
        [f'<option value="{label}" {"selected" if i == selected else ""}>{label}</option>' for i, label in enumerate(options)]
    )
    selected_str = next(label[i] for i, label in enumerate(options))
    return f'<select id="set-{set_opt_path}">Auto{options_html}</select>'

def draw_checkbox(opt_range, set_opt_path):
    checked = 'checked' if opt_range.default else ''
    return f'<input type="checkbox" id="set-{set_opt_path}" {checked}>'

def draw_slider(opt_range, set_opt_path):
    return f'<input type="range" id="set-{set_opt_path}" value="{opt_range.default}" min="{opt_range.min}" max="{opt_range.max}" step="{opt_range.step}">'


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
ctx = rs.context()
dev = ctx.query_devices()[0]
pipeline = rs.pipeline(ctx)
config = rs.config()
streams = {}
for sensor_ in dev.query_sensors():
    pass
    print(dir(sensor_))
    # print(sensor_.get_stream_profiles())
    # print(dir(sensor_.get_stream_profiles()[0]))
    # print(sensor_.profiles)
    # print(dir(sensor_.profiles[0]))

    streams[sensor_.name] = {

    }
streams = {
    "depth":
        {
            "frame_getter": lambda frames: frames.get_depth_frame(),
            "frame_processor": lambda frame: colorizer.colorize(frame).get_data(),
            "config": (rs.stream.depth, 640, 480, rs.format.z16, 30)
        },
    "color":
        {
            "frame_getter": lambda frames: frames.get_color_frame(),
            "frame_processor": lambda frame: frame.get_data(),
            "config": (rs.stream.color, 640, 480, rs.format.bgr8, 30)
        }
}

for stream in streams:
    config.enable_stream(*streams[stream]["config"])
#config.enable_stream(rs.stream.motion)
#config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
#config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
print(rs.format.combined_motion)
print(dir(rs.format))
print(rs.stream.motion)
print(dir(rs.stream))
#config.enable_stream(rs.stream.accel)
config.enable_stream(rs.stream.gyro)
pipeline.start(config)
colorizer = rs.colorizer()
#dev = pipeline.get_active_profile().get_device()

sensors = dev.query_sensors()
flags = {} #{ f"{s.name}" : True for s in sensors}
html_inputs = ""
html_inputs_scripts = ""

html_inputs += '<div style="display: flex; flex-wrap: wrap; justify-content: space-between;">'
for s in sensors:
    base_path = s.name.replace(' ', '_')
    flags[base_path] = True
    print(base_path, flags)
    #print(dir(s))

    html_inputs += f'<div style="flex: 1; min-width: 300px; margin: 10px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">'
    html_inputs += f'<h2>{s.name}</h2>'
    for opt in s.get_supported_options():
        opt_name = opt.name
        set_opt_path = f"{base_path}_{opt_name}"
        get_opt_path = set_opt_path + "/get"

        def create_routes(sensor, option):
            global html_inputs, html_inputs_scripts

            def get_sensor_name():
                return {"message": sensor.name}

            def get_option():
                value = sensor.get_option(option)
                return {"message": f"{option.name} is {value}", "val": value}

            def set_option(value= Body(...)):
                opt_range = sensor.get_option_range(option)
                if is_enum(option, opt_range, sensor):
                    # Convert string label back to numerical value
                    possible_values = range(int(opt_range.min), int(opt_range.max) + 1, int(opt_range.step))
                    for possible_value in possible_values:
                        if sensor.get_option_value_description(option, possible_value) == value:
                            value = possible_value
                            break
                    else:
                        raise HTTPException(status_code=400, detail=f"Invalid enum value: {value}")

                sensor.set_option(option, int(value))
                return {"message": f"{option.name} set to {value}", "val": value}

            app.add_api_route(f"/{base_path}", get_sensor_name, methods=["GET"], tags=["camera-controls"])
            if sensor.supports(option): # we probably can automate it iterating for every option
                app.add_api_route(f"/{get_opt_path}", get_option, methods=["GET"], tags=["camera-controls"])
                app.add_api_route(f"/{set_opt_path}", set_option, methods=["POST"], tags=["camera-controls"])

                html_inputs += f"""
                    <div style="margin: 10px 0; display: flex; justify-content: space-between; align-items: center;">
                        <span style="margin-right: 10px;">Set {sensor.name} {option.name}:</span>
                        <div style="flex-grow: 1; text-align: right;">
                            {draw_option(option, sensor, set_opt_path)}
                        </div>
                    </div>
                """

                html_inputs_scripts += generate_option_script(option, s, set_opt_path, get_opt_path)

        create_routes(s, opt)

    html_inputs += '</div>'  # End of sensor options container

    def create_streams_endpoints(sensor=s, sensor_name=base_path):
        def sensor_feed():
            def generate_frames():
                global camera_on, flags
                while camera_on and flags[sensor_name]:
                    frames = pipeline.wait_for_frames()
                    frame = None
                    # this section can be improved
                    if sensor.is_depth_sensor():
                        frame = frames.get_depth_frame()
                        frame = colorizer.colorize(frame).get_data()  # assuming no throw if 'not frame'
                    elif sensor.is_color_sensor():
                        frame = frames.get_color_frame().get_data()
                    elif sensor.is_motion_sensor():
                        motion_data = None
                        for f in frames:
                            if f.is_motion_frame():
                                motion_data = (f.as_motion_frame().get_motion_data())
                                # frame = f
                                #break
                        #print([i for i in motion_data])
                        text = f"x: {motion_data.x:.6f}\ny: {motion_data.y:.6f}\nz: {motion_data.z:.6f}".split("\n")
                        frame = np.zeros((480, 640, 3), dtype=np.uint8) # probably better load an image instead: image = cv2.imread(path)
                        y0, dy = 50, 40
                        for i, coord in enumerate(text):
                            y = y0 + dy*i
                            cv2.putText(frame, coord, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    else:
                        pass

                    if not sensor.is_motion_sensor() and not frame:  # motion should have its own checks...
                        continue

                    frame = np.asanyarray(frame)
                    yield from encode_and_yield(frame)

                # if camera off, return empty frame
                yield from yield_empty_frame()

            return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

        def toggle_sensor():
            global flags
            flags[sensor_name] = not flags[sensor_name]
            return {"message": f"Camera set depth to be {status_to_on_off(flags[sensor_name])}"}

        app.add_api_route(f"/{sensor_name}_stream", sensor_feed, methods=["GET"], tags=["camera-controls"])
        app.add_api_route(f"/toggle_{sensor_name}", toggle_sensor, methods=["POST"], tags=["camera-controls"])

    create_streams_endpoints()

# Close the main container for all sensors
html_inputs += '</div>'

print("ok")
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
    {html_inputs}
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
    {html_inputs_scripts}
    </script>
    </body>
    </html>
    """)
