from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentType, initialize_agent, Tool
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.chains import LLMMathChain
from langchain.tools import BaseTool
import cv2
import numpy as np


class RealSenseTool(BaseTool):
    name: str = "RealSense"
    description: str = (
        "Interact with the Intel RealSense camera. Allowed commands: "
        "'list' to list devices, "
        "'info' to get device information, "
        "'capture_color' (or 'capture') to capture a color frame, "
        "'capture_depth' to capture a depth frame."
    )

    def _run(self, tool_input: str) -> str:
        command = tool_input.strip().lower()
        print(f"[RealSenseTool] Received command: {command}")

        if command == "capture":
            command = "capture_color"

        allowed_commands = ["list", "info", "capture_color", "capture_depth"]

        if command not in allowed_commands:
            return f"Error: Command '{command}' not allowed. Use: {allowed_commands}"

        try:
            import pyrealsense2 as rs
        except ImportError:
            return "Install pyrealsense2: pip install pyrealsense2"

        try:
            ctx = rs.context()
        except Exception as e:
            return f"Error initializing RealSense: {str(e)}"

        # Command implementations
        if command == "list":
            return self._handle_list(ctx)
        elif command == "info":
            return self._handle_info(ctx)
        elif command in ["capture_color", "capture_depth"]:
            return self._handle_capture(command)

    def _handle_list(self, ctx):
        try:
            import pyrealsense2 as rs
            devices = ctx.query_devices()
            if not devices:
                return "No RealSense devices found"
            return "\n".join([
                f"{d.get_info(rs.camera_info.name)} (S/N: {d.get_info(rs.camera_info.serial_number)})"
                for d in devices
            ])
        except Exception as e:
            return f"Error listing devices: {str(e)}"

    def _handle_info(self, ctx):
        try:
            import pyrealsense2 as rs
            devices = ctx.query_devices()
            if not devices:
                return "No devices found"
            dev = devices[0]
            info = [
                f"Name: {dev.get_info(rs.camera_info.name)}",
                f"Serial: {dev.get_info(rs.camera_info.serial_number)}",
                f"Firmware: {dev.get_info(rs.camera_info.firmware_version)}"
            ]
            sensors = dev.query_sensors()
            sensor_names = [sensor.get_info(rs.camera_info.name) for sensor in sensors]
            info.append("Available Sensors: " + ", ".join(sensor_names))
            return "\n".join(info)
        except Exception as e:
            return f"Error getting info: {str(e)}"

    def _handle_capture(self, command):
        import pyrealsense2 as rs
        pipeline = rs.pipeline()
        config = rs.config()

        try:
            if command == "capture_color":
                config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
                frame_type = "color"
            else:
                config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
                frame_type = "depth"

            pipeline.start(config)
            frames = pipeline.wait_for_frames(5000)

            if command == "capture_color":
                frame = frames.get_color_frame()
                image = np.asanyarray(frame.get_data())
                title = "Color Image"
            else:
                frame = frames.get_depth_frame()
                depth_image = np.asanyarray(frame.get_data())
                image = cv2.applyColorMap(
                    cv2.convertScaleAbs(depth_image, alpha=0.03),
                    cv2.COLORMAP_JET
                )
                title = "Depth Image"

            # Display the image
            cv2.imshow(title, image)
            cv2.waitKey(3000)  # Show for 3 seconds
            cv2.destroyAllWindows()

            return f"Successfully captured and displayed {frame_type} frame"

        except Exception as e:
            return f"Capture error: {str(e)}"
        finally:
            pipeline.stop()


# I used gemini 1-5 flash because I could get its api key for free, but there are better options
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key="GOOGLE_API_KEY",  # generate api key and replace this
    temperature=0.7
)

tools = [
    # Tool(
    #     name="Wikipedia",
    #     func=WikipediaAPIWrapper().run,
    #     description="For factual information"
    # ),
    # Tool(
    #     name="Calculator",
    #     func=LLMMathChain(llm=llm).run,
    #     description="Math calculations"
    # ),
    RealSenseTool()
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

import os
os.system('cls')  # using this instead of suppressing warnings

while True:
    print()
    print("Enter command:")
    response = agent.invoke({
        "input": input()
        #"input": "capture a color image from the RealSense camera"
    })
    print("Final Answer:", response["output"])
