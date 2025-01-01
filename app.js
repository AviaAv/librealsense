const { ApiClient, CameraControlsApi, StatusApi } = require('real_sense_api');

// helper class, helps us avoid using promises and callbacks
class CameraApiWrapper {
    constructor(basePath = 'http://127.0.0.1:8000') {
        const apiClient = new ApiClient();
        apiClient.basePath = basePath;

        // Initialize APIs - wraps every function call
        this.status = this._wrapApi(new StatusApi(apiClient));
        this.camera_controls = this._wrapApi(new CameraControlsApi(apiClient));
    }

    _wrapApi(api) {
        // Create a proxy to automatically wrap all methods
        return new Proxy(api, {
            get: (target, prop) => {
                const original = target[prop];

                // all functions are wrapped as 'Promises', so we can await them in our code
                if (typeof original === 'function') {
                    return async (...args) => {
                        return new Promise((resolve, reject) => {
                            original.call(target, ...args, (error, data) => {
                                if (error) reject(error);
                                else resolve(data);
                            });
                        });
                    };
                }

                // non functions are returned as-is
                return original;
            }
        });
    }
}

// Usage example
async function manageCamera() {
    try {
        const camera = new CameraApiWrapper();
        let exposure = await camera.camera_controls.getExposureRGBCameraExposureGetGet();
        console.log("current exposure is", exposure.val);

        const status = await camera.status.getCameraStatusCameraStatusGet();
        console.log(status);

        if (!status.is_on) {
            await camera.camera_controls.toggleCameraToggleCameraPost();
            console.log('Camera toggled on.');
        }
        if (!status.depth_on) {
            await camera.camera_controls.toggleDepthToggleDepthPost();
            console.log('Depth toggled on.');
        }
        if (!status.color_on) {
            await camera.camera_controls.toggleColorToggleColorPost();
            console.log('Color toggled on.');
        }

        new_exposure = exposure.val === 39 ? 312 : 39;
        await camera.camera_controls.setExposureRGBCameraExposurePost(new_exposure);
        console.log(`Exposure set to: ${new_exposure}`);

    } catch (error) {
        console.error('Error managing camera:', error);
    }
}

// to use this wrapper on other files too
module.exports = CameraApiWrapper;

// call the example
manageCamera();
