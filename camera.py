from opcua import Client
import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import math

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise Exception("Kamera kann nicht geöffnet werden")
ret, frame = cap.read()
print("Initial frame captured: ", ret)

running = False
photo = None
width_scale = None
height_scale = None
real_size_cm = (2, 2)
red_cube_center = None


def update_brightness(val, brightness_var):
    global cap
    if cap:
        cap.set(cv2.CAP_PROP_BRIGHTNESS, float(val))
        brightness_var.set_value(float(val))
        print(f"Brightness updated to: {val}")


def gui(brightness_var, width_scale_var, height_scale_var, red_cube_center_var):
    root = tk.Tk()
    root.title("Webcam Object and Light Spot Detection")

    canvas = tk.Canvas(root, width=640, height=480)
    canvas.pack()

    entry = tk.Entry(root)
    entry.pack()

    scale_button = tk.Button(
        root,
        text="Skalieren",
        command=lambda val: scale_value(val, width_scale_var, height_scale_var),
    )
    scale_button.pack()

    output_label = tk.Label(root, text="")
    output_label.pack()

    brightness_scale = tk.Scale(
        root,
        from_=0,
        to=100,
        orient="horizontal",
        label="Brightness",
        command=lambda val: update_brightness(val, brightness_var),
    )
    brightness_scale.set(50)
    brightness_scale.pack()

    detect_button = tk.Button(
        root,
        text="Detect Red Cube",
        command=lambda val: find_red_cube_scale(
            val, width_scale_var, height_scale_var, red_cube_center_var
        ),
    )
    detect_button.pack()

    detect_button2 = tk.Button(
        root, text="Detect light_spot", command=mask_light_spot_and_show_measurements
    )
    detect_button2.pack()

    width_scale_label = tk.Label(root, text="Width Scale: N/A")
    height_scale_label = tk.Label(root, text="Height Scale: N/A")
    width_scale_label.pack()
    height_scale_label.pack()

    root.mainloop()


def find_red_cube_scale(width_scale_var, height_scale_var, red_cube_center_var):
    global width_scale, height_scale, cap, photo, canvas, red_cube_center
    ret, frame = cap.read()
    print("Frame read for red cube detection: ", ret)
    if ret:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 + mask2
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print("Number of red contours found: ", len(contours))
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            print(f"Red cube bounding box: x={x}, y={y}, w={w}, h={h}")
            width_scale = real_size_cm[0] / w
            height_scale = real_size_cm[1] / h
            print(f"Width scale: {width_scale}, Height scale: {height_scale}")
            width_scale_var.set_value(width_scale)
            height_scale_var.set_value(height_scale)
            width_scale_label.config(text=f"Width Scale: {width_scale:.2f} cm/pixel")
            height_scale_label.config(text=f"Height Scale: {height_scale:.2f} cm/pixel")
            red_cube_center_x = x + w // 2
            red_cube_center_y = y + h // 2
            red_cube_center = (red_cube_center_x, red_cube_center_y)
            red_cube_center_var.set_value(list(red_cube_center))
            print(f"Red cube center: {red_cube_center}")
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(frame_rgb)
        photo = ImageTk.PhotoImage(image=im)
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)


def scale_value(width_scale_var, height_scale_var):
    global width_scale, height_scale
    try:
        value = float(entry.get())
        width_scale = value
        height_scale = value
        width_scale_var.set_value(width_scale)
        height_scale_var.set_value(height_scale)
        print(f"Scale value set to: {value}")
        output_label.config(text=f"Skalierter Wert: {width_scale}")
        width_scale_label.config(text=f"Width Scale: {width_scale:.2f} cm/pixel")
        height_scale_label.config(text=f"Height Scale: {height_scale:.2f} cm/pixel")
    except ValueError:
        print("Invalid input for scale value.")
        output_label.config(text="Bitte geben Sie eine gültige Zahl ein.")


def get_line_end_point(center, angle, length=1000):
    end_point = (
        int(center[0] + math.cos(math.radians(angle)) * length),
        int(center[1] + math.sin(math.radians(angle)) * length),
    )
    print(f"Line end point for angle {angle}: {end_point}")
    return end_point


def mask_light_spot_and_show_measurements():
    global photo, canvas, width_scale, height_scale, red_cube_center
    ret, frame = cap.read()
    print("Frame read for light spot detection: ", ret)
    if ret and width_scale is not None and height_scale is not None:
        roi_x, roi_y, roi_w, roi_h = (
            100,
            100,
            frame.shape[1] - 200,
            frame.shape[0] - 200,
        )
        print(f"ROI defined: x={roi_x}, y={roi_y}, w={roi_w}, h={roi_h}")
        roi = frame[roi_y : roi_y + roi_h, roi_x : roi_x + roi_w]
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        max_val = gray_roi.max()
        print(f"Max value in ROI: {max_val}")
        normalized_roi = np.where(gray_roi == max_val, 255, gray_roi)
        _, thresh_roi = cv2.threshold(normalized_roi, 254, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(
            thresh_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        print("Number of light spot contours found: ", len(contours))
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            print(f"Light spot bounding box: x={x}, y={y}, w={w}, h={h}")
            real_width = w * width_scale
            real_height = h * height_scale
            print(f"Real width: {real_width} cm, Real height: {real_height} cm")
            cv2.drawContours(
                frame, [largest_contour], -1, (0, 255, 0), 2, offset=(roi_x, roi_y)
            )
            cv2.rectangle(
                frame,
                (roi_x + x, roi_y + y),
                (roi_x + x + w, roi_y + y + h),
                (255, 0, 0),
                2,
            )
            cv2.putText(
                frame,
                f"Width: {real_width:.2f} cm",
                (roi_x + x, roi_y + y - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                1,
            )
            cv2.putText(
                frame,
                f"Height: {real_height:.2f} cm",
                (roi_x + x, roi_y + y + h + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                1,
            )
            cv2.circle(frame, red_cube_center, 5, (255, 0, 0), -1)
            if red_cube_center is not None:
                angles = [90, 210, 330]
                line_length = 100
                for angle in angles:
                    end_x = int(
                        red_cube_center[0] + line_length * math.cos(math.radians(angle))
                    )
                    end_y = int(
                        red_cube_center[1] + line_length * math.sin(math.radians(angle))
                    )
                    print(
                        f"Drawing line at angle {angle} from red cube center to ({end_x}, {end_y})"
                    )
                    cv2.line(frame, red_cube_center, (end_x, end_y), (255, 0, 0), 2)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                im = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(image=im)
                canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(frame_rgb)
        photo = ImageTk.PhotoImage(image=im)
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    root.update_idletasks()


client = Client("opc.tcp://0.0.0.0:4849/freeopcua/server/")
client.connect()
print("Client connected to server.")

try:
    root = client.get_root_node()
    print("Objects node is: ", root)

    # Node objects have methods to read and write node attributes
    #  as well as browse or populate address space
    print("Children of root are: ", root.get_children())

    brightness = root.get_child(["0:Objects", "2:Camera", "2:Brightness"])
    widthScale = root.get_child(["0:Objects", "2:Camera", "2:WidthScale"])
    heightScale = root.get_child(["0:Objects", "2:Camera", "2:HeightScale"])
    red_cube_center = root.get_child(["0:Objects", "2:Camera", "2:RedCubeCenter"])

    # Pass OPC UA nodes to GUI
    gui(brightness, width_scale, height_scale, red_cube_center)


except Exception as e:
    print("An error occurred:", e)

finally:
    client.disconnect()
    print("Client disconnected.")
