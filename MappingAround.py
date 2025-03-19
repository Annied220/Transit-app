
import tkinter as tk # https://www.geeksforgeeks.org/python-gui-tkinter/
import tkintermapview # https://github.com/TomSchimansky/TkinterMapView

root_tk = tk.Tk()
root_tk.geometry(f"{700}x{600}")
root_tk.title("Map View using the tkintermapview library")

map_widget = tkintermapview.TkinterMapView(root_tk, width=700, height=500, corner_radius=0)
map_widget.pack(fill="both", expand=True)

# set current widget position and zoom
map_widget.set_position(41.6901407, -72.7664725)  # CCSU
map_widget.set_zoom(12)

marker_1 = map_widget.set_marker(41.6901407, -72.7664725, text="Vance")

"""
def add_marker_event(coords):
    print("Add marker:", coords)
    new_marker = map_widget.set_marker(coords[0], coords[1], text="new marker")

map_widget.add_right_click_menu_command(label="Add Marker",
                                        command=add_marker_event,
                                        pass_coords=True)
"""
"""
def left_click_event(coordinates_tuple):
    print("Left click event with coordinates:", coordinates_tuple)
    
map_widget.add_left_click_map_command(left_click_event)
"""

root_tk.mainloop()
