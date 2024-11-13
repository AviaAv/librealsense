# to generate this openapi_client, we needed to first generate the code from fast api, using
# "openapi-generator-cli generate -i http://127.0.0.1:8000/openapi.json -g python -o python_sdk\"
# as it seems, we can generate to different languages, by passing a different language after the -g
# in this case of python, after generation we needed to install packages by running 'pip install .' in the output folder
# afterwards, we can use this:
from openapi_client import ApiClient, Configuration

# next, we need to import the APIs we are interested in, per tag
# writing explicitly to show what classes are used, we can also use 'from openapi_client.api import *', but writing
# explicitly helps us make sure we get all the classes we expect.
# currently, the only function on random_api is 'read_root_get', since only the root endpoint has the 'random' tag
from openapi_client.api import camera_controls_api, status_api

config = Configuration()
config.host = "http://127.0.0.1:8000"
client = ApiClient(config)

camera_controls = camera_controls_api.CameraControlsApi(client)
status = status_api.StatusApi(client)

# get camera status
response = status.get_camera_status_camera_status_get()
print(response["message"])
if not response["is_on"]:
    camera_controls.toggle_camera_toggle_camera_post()
if not response["depth_on"]:
    camera_controls.toggle_depth_toggle_depth_post()
if not response["color_on"]:
    camera_controls.toggle_color_toggle_color_post()

exposure_response = camera_controls.get_exposure_rgb_camera_exposure_get_get()
exposure = exposure_response["val"]
print(exposure_response)
print(camera_controls.set_exposure_rgb_camera_exposure_post(156 if not exposure == 156 else 625))
print(camera_controls.get_exposure_rgb_camera_exposure_get_get())


