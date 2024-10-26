from opcua import Server
import time

# Initialize the server
server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4849/freeopcua/server/")

uri = "http://example.org"
idx = server.register_namespace(uri)

cam_obj = server.nodes.objects.add_object(idx, "Camera")
width_scale_var = cam_obj.add_variable(idx, "WidthScale", 0.0)
height_scale_var = cam_obj.add_variable(idx, "HeightScale", 0.0)
red_cube_center_var = cam_obj.add_variable(idx, "RedCubeCenter", [0, 0])
brightness_var = cam_obj.add_variable(idx, "Brightness", 50.0)

# Allow write access to our variables
width_scale_var.set_writable()
height_scale_var.set_writable()
red_cube_center_var.set_writable()
brightness_var.set_writable()


def start_opcua_server():
    print("Starting OPC UA Server...")
    server.start()
    try:
        while True:
            time.sleep(1)
    finally:
        server.stop()
        print("OPC UA Server stopped.")


start_opcua_server()
