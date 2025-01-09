import matplotlib.pyplot as plt
from PIL.Image import Transpose
from networkx.algorithms.bipartite import color

from . import *
from ..classes.class_connection import Connection, UI_CONFIG_CONNECTION
from ..classes.class_nation import UI_CONFIG_CUSTOMNATION, UI_CONFIG_GENERICNATION
from ..classes.class_province import UI_CONFIG_PROVINCE
from ..classes.class_region import UI_CONFIG_REGION
from ..classes.class_settings import UI_CONFIG_SETTINGS
import queue
import threading

# UI VARIABLES
########################################################################################################################


class MainInterface(ttk.Frame):

    def __init__(self, master=None):
        self.master = master
        super().__init__()

        self.grid(column=0, row=0, sticky='NEWS')
        self.columnconfigure(0, minsize=380, weight=380)
        self.columnconfigure(1, minsize=1060, weight=1060)
        self.columnconfigure(2, minsize=480, weight=480)
        self.rowconfigure(0, minsize=1080, weight=1)

        self.map = DominionsMap()
        self.settings = DreamAtlasSettings(index=0)

        self.empty = True
        self.focus = None
        self.view_coordinates = [0, 0]
        self.view_zoom = 1.0

        self.selected_lense = ttk.IntVar()
        self.previous_lense = 1
        self.selected_plane = ttk.IntVar()
        self.current_plane = 1

        self.viewing_bitmaps = None
        self.bitmap_colors = None
        self.viewing_photoimages = None
        self.viewing_connections = None
        self.viewing_nodes = None
        self.viewing_borders = None

        self.build_gui()
        self.update_gui()

    def build_gui(self):  # This builds the high level widgets for the UI that are never removed

        # WIDGET FUNCTIONS

        # BUILD UI
        major_frames = list()  # Build 3 major frames
        for frame in range(3):
            major_frames.append(ttk.Frame(self, padding=4))
            major_frames[-1].grid(row=0, column=frame, sticky='NEWS')
            major_frames[-1].grid_rowconfigure(0, weight=1)
            major_frames[-1].grid_columnconfigure(0, weight=1)
        major_frames[2].grid_rowconfigure(0, weight=860)
        major_frames[2].grid_rowconfigure(1, weight=130)
        major_frames[2].grid_rowconfigure(2, weight=50)
        major_frames[2].grid_rowconfigure(3, weight=40)

        # Object explorer_panel lets you view and select all the objects in the map
        explorer_frame = ttk.Labelframe(major_frames[0], text="Explorer", padding=2)
        explorer_frame.grid(row=0, column=0, sticky='NEWS')
        explorer_frame.grid_columnconfigure(0, weight=100)
        explorer_frame.grid_columnconfigure(1, weight=1)
        explorer_frame.grid_rowconfigure(0, weight=1)

        self.explorer_panel = ttk.Treeview(explorer_frame, bootstyle="default", show="tree")
        explorer_scrollbar = ttk.Scrollbar(explorer_frame, bootstyle="warning", orient='vertical', command=self.explorer_panel.yview)
        self.explorer_panel['yscrollcommand'] = explorer_scrollbar.set
        self.explorer_panel.grid(row=0, column=0, sticky='NEWS')
        explorer_scrollbar.grid(row=0, column=1, sticky='NEWS')

        # Making the map viewing/editing window
        viewing_frame = ttk.Labelframe(major_frames[1], text="Viewer", padding=3)
        viewing_frame.grid(row=0, column=0, sticky='NEWS')
        viewing_frame.grid_rowconfigure(0, weight=100)
        viewing_frame.grid_rowconfigure(1, weight=1)
        viewing_frame.grid_columnconfigure(0, weight=100)
        viewing_frame.grid_columnconfigure(1, weight=1)
        self.viewing_canvas = ttk.Canvas(viewing_frame, takefocus=True, confine=False, )
        self.viewing_canvas.grid(row=0, column=0, sticky='NEWS')
        viewing_x_scrollbar = ttk.Scrollbar(viewing_frame, bootstyle="success", orient='horizontal', command=self.viewing_canvas.xview)
        viewing_y_scrollbar = ttk.Scrollbar(viewing_frame, bootstyle="success", orient='vertical', command=self.viewing_canvas.yview)
        self.viewing_canvas['xscrollcommand'] = viewing_x_scrollbar.set
        self.viewing_canvas['yscrollcommand'] = viewing_y_scrollbar.set
        viewing_x_scrollbar.grid(row=1, column=0, sticky='NEWS')
        viewing_y_scrollbar.grid(row=0, column=1, sticky='NEWS')

        # Making the province editing panel
        self.editor_frame = ttk.Labelframe(major_frames[2], text="Editor", padding=3)
        self.editor_frame.grid(row=0, column=0, sticky='NEWS')
        self.editor_frame.grid_columnconfigure(0, weight=1)

        # Making the display options buttons
        display_options_frame = ttk.Labelframe(major_frames[2], text="Display", padding=4)
        display_options_frame.grid(row=1, column=0, sticky='NEWS')
        display_options = ['Show Nodes', 'Show Connections', 'Show Borders', 'Show Capitals', 'Show Thrones', 'Show Armies', 'Enable Wraparound', 'Illwinter Icons']
        display_tags = ['nodes', 'connections', 'borders', 'capitals', 'thrones', 'armies', 'wraparound', 'icons']
        display_states = [1, 1, 1, 1, 1, 0, 1, 0]
        display_active = [1, 1, 0, 0, 0, 1, 0, 0]
        display_styles = ['primary', 'primary', 'primary', 'primary', 'primary', 'primary', 'secondary', 'secondary']
        self.display_options = list()
        for i, option in enumerate(display_options):
            variable = ttk.IntVar()
            tag = display_tags[i]
            active = display_active[i]
            ttk.Checkbutton(display_options_frame, bootstyle=display_styles[i], text=option, variable=variable, command=lambda: self.refresh_option_view(), padding=7, state=UI_STATES[display_states[i]]).grid(row=i//4, column=i % 4, sticky='NEWS')
            self.display_options.append([variable, tag, active])

        # Making the map lense buttons
        self.selected_lense.set(0)
        lense_button_frame = ttk.Labelframe(major_frames[2], text="Lense", padding=3)
        lense_button_frame.grid(row=2, column=0, sticky='NEWS')
        lense_button_frame.grid_rowconfigure(0, weight=1)
        for index, lense in enumerate(['Art', 'Provinces', 'Regions', 'Terrain', 'Population', 'Resources']):
            ttk.Radiobutton(lense_button_frame, bootstyle="dark-outline-toolbutton", text=lense, variable=self.selected_lense, command=lambda: self.refresh_lense_view(), value=index, state=ttk.NORMAL).grid(row=0, column=index, sticky='NEWS')
            lense_button_frame.grid_columnconfigure(index, weight=1)

        # Making the plane selection buttons
        plane_button_frame = ttk.Labelframe(major_frames[2], text="Plane", padding=3)
        plane_button_frame.grid(row=3, column=0, sticky='NEWS')
        plane_button_frame.grid_rowconfigure(0, weight=1)
        self.selected_plane.set(1)
        for plane in range(1, 10):
            ttk.Radiobutton(plane_button_frame, bootstyle='dark-outline-toolbutton', text=str(plane), variable=self.selected_plane, command=lambda: self.refresh_plane_view(), value=plane, state=ttk.NORMAL).grid(row=0, column=plane-1, sticky='NEWS')
            plane_button_frame.grid_columnconfigure(plane-1, weight=1)

        # BUTTON BINDINGS
        # self.explorer_panel.tag_bind("explorer_tag", "<<TreeviewSelect>>", item_selected)

        # viewing_panel.bind("<1>", )
        # viewing_panel.bind("<2>", )
        # viewing_panel.bind("<3>", )
        # viewing_panel.bind("<4>", )
        # viewing_panel.bind("<5>", )
        # viewing_panel.bind("<6>", )
        # viewing_panel.bind("<7>", )
        # viewing_panel.bind("<8>", )
        # viewing_panel.bind("<9>", )
        # viewing_panel.bind("<w>", v_drag)
        # viewing_panel.bind("<a>", v_drag)
        # viewing_panel.bind("<s>", v_drag)
        # viewing_panel.bind("<d>", v_drag)
        # self.viewing_canvas.bind("<Button-1>", left_click)
        # self.viewing_canvas.bind("<Button-3>", right_click)
        # self.viewing_canvas.bind("<Motion>", mouse_motion)
        # self.viewing_canvas.bind("Control-z", undo)

    def update_gui(self):
        self.update_explorer_panel()
        self.update_viewing_panel()
        self.update_editor_panel()
        self.refresh_plane_view()
        self.refresh_option_view()
        self.refresh_lense_view()

    # UPDATE FUNCTIONS
    def update_explorer_panel(self):

        for i in self.explorer_panel.winfo_children():
            i.destroy()

        if not self.empty:  # If there is data
            parent = self.explorer_panel.insert("", ttk.END, text="All provinces")
            for plane in self.map.planes:
                plane_tag = self.explorer_panel.insert(parent, ttk.END, text=f'Plane {plane}')
                for province in self.map.province_list[plane]:
                    self.explorer_panel.insert(plane_tag, ttk.END, text=f'Province {province.index}', tags="explorer_tag")

            regions_super_list = [["Homelands", self.map.homeland_list], ["Peripheries", self.map.periphery_list], ["Thrones", self.map.throne_list]]
            for i, (text, region_list) in enumerate(regions_super_list):
                parent = self.explorer_panel.insert("", ttk.END, text=text)
                for j, region in enumerate(region_list):
                    region_tag = self.explorer_panel.insert(parent, ttk.END, text=f'{region.name}')
                    for province in region.provinces:
                        self.explorer_panel.insert(region_tag, ttk.END, text=f'Province {province.index}', tags="explorer_tag")

    def update_viewing_panel(self):  # This is run whenever the screen needs get updated

        # Need to premake the map layers and set to hidden only using when needed, also draw virtual maps at the other positions and teleport back around when you get to one edge
        if not self.empty:  # If there is data

            self.viewing_bitmaps = [None]*10
            self.bitmap_colors = [None]*10
            self.viewing_photoimages = [None]*10
            self.viewing_connections = [None]*10
            self.viewing_nodes = [None]*10
            self.viewing_borders = [None]*10

            for plane in self.map.planes:  # Create all the PIL objects
                self.viewing_bitmaps[plane] = list()
                self.bitmap_colors[plane] = provinces_2_colours(self.map.province_list[plane])
                self.viewing_photoimages[plane] = list()
                self.viewing_connections[plane] = list()
                self.viewing_nodes[plane] = list()
                self.viewing_borders[plane] = list()

                # Making province border objects (useful for a lot of stuff)
                for i, (x, y), array in pixel_matrix_2_bitmap_arrays(self.map.pixel_map[plane]):  # Iterating through every province index on this pixel map
                    image = Image.fromarray(array, mode='L').convert(mode='1', dither=Image.Dither.NONE)
                    image = image.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
                    image = image.transpose(method=Image.Transpose.ROTATE_90)
                    bitmap = ImageTk.BitmapImage(image)
                    iid = self.viewing_canvas.create_image(x, y, anchor=ttk.NW, image=bitmap, state=ttk.HIDDEN, tags=(f'plane{plane}', f'{i}', 'bitmap'))
                    self.viewing_bitmaps[plane].append([i, iid, bitmap])

                # Making art objects
                if self.map.image_file[plane].endswith('.tga'):  # Art layer
                    photoimage = ImageTk.PhotoImage(Image.open(self.map.image_file[plane]))
                    iid = self.viewing_canvas.create_image(0, 0, anchor=ttk.NW, image=photoimage, state=ttk.HIDDEN, tags=(f'plane{plane}', 'photoimage'))
                    self.viewing_photoimages[plane].append([self.map.image_file[plane], iid, photoimage])

                # Making borders
                image = Image.fromarray(np.flip(pixel_matrix_2_borders_array(self.map.pixel_map[plane], thickness=2).transpose(), axis=0), mode='L')
                border = ImageTk.BitmapImage(image.convert(mode='1', dither=Image.Dither.NONE), foreground='black')
                iid = self.viewing_canvas.create_image(0, 0, anchor=ttk.NW, image=border, state=ttk.HIDDEN, tags=(f'plane{plane}', 'borders'))
                self.viewing_borders[plane] = [iid, border]

                # Making connection objects
                virtual_graph, virtual_coordinates = ui_find_virtual_graph(self.map.layout.graph[plane], self.map.layout.coordinates[plane], self.map.map_size[plane], NEIGHBOURS_FULL)
                done_edges = set()
                radius = 15
                for i in virtual_graph:
                    x_1, y_1 = virtual_coordinates[i]
                    for j in virtual_graph[i]:
                        if j not in done_edges:
                            x_2, y_2 = virtual_coordinates[j]
                            iid = self.viewing_canvas.create_line(x_1, y_1, x_2, y_2, state=ttk.HIDDEN, dash=(100, 15), activefill='white', fill='red', tags=(f'plane{plane}', f'{(i, j)}', 'connections'), width=5)
                            self.viewing_connections[plane].append([(i, j), iid])
                    iid = self.viewing_canvas.create_oval(x_1-radius, y_1-radius, x_1+radius, y_1+radius, state=ttk.HIDDEN, activefill='white', fill='red',tags=(f'plane{plane}', f'{i}', 'nodes'), width=5)
                    self.viewing_nodes[plane].append([i, iid])
                    done_edges.add(i)

    def update_editor_panel(self):
        if not self.empty:  # If there is data
            if self.focus is not None:  # If there is a focus
                InputWidget(master=self.editor_frame, ui_config=UI_CONFIG_PROVINCE, cols=1, target_class=self.focus).grid(row=0, column=0, sticky="NEWS")

    def refresh_option_view(self):  # This function handles switching the views and updating the viewer images
        if not self.empty:  # If there is data
            for variable, tag, active in self.display_options:
                self.viewing_canvas.itemconfigure(tag, state=ttk.HIDDEN)
                if variable.get():
                    for iid in self.viewing_canvas.find_withtag(tag):
                        if f'plane{self.current_plane}' in self.viewing_canvas.gettags(iid):
                            self.viewing_canvas.itemconfigure(iid, state=UI_STATES[active])

    def refresh_lense_view(self):
        if not self.empty:  # If there is data
            current_lense = self.selected_lense.get()
            for plane in self.map.planes:
                for i, iid, bitmap in self.viewing_bitmaps[plane]:
                    colour = self.bitmap_colors[plane][i-1][current_lense]
                    bitmap._BitmapImage__photo.config(foreground=colour)
            self.previous_lense = current_lense

    def refresh_plane_view(self):
        if not self.empty:  # If there is data
            new_plane = self.selected_plane.get()
            self.viewing_canvas.config(confine=True, scrollregion=(0, 0, self.map.map_size[new_plane][0], self.map.map_size[new_plane][1]))
            self.viewing_canvas.itemconfigure(f'plane{self.current_plane}', state=ttk.HIDDEN)
            self.viewing_canvas.itemconfigure(f'plane{new_plane}', state=ttk.NORMAL)
            self.current_plane = new_plane

    def load_map(self, folder):

        self.map.load_folder(folder)
        self.empty = False
        # self.focus = Connection([2, 45], 33)
        self.update_gui()

    def load_file(self, file):

        self.map.load_file(file)
        self.empty = False
        self.update_gui()

    def save_map(self, folder):

        self.map.publish(folder)


class InputToplevel(ttk.Toplevel):

    def __init__(self, master, title, ui_config, cols, target_type=None, target_class=None, target_location=None, map=None):
        self.master = master
        super().__init__(title=title, iconphoto=ART_ICON, transient=master)
        self.grid()
        self.columnconfigure(0, weight=1)
        InputWidget(master=self, ui_config=ui_config, cols=cols, target_type=target_type, target_class=target_class, target_location=target_location, map=None).grid(row=0, column=0, sticky='NEWS')


class InputWidget(ttk.Frame):

    def __init__(self, master, ui_config, cols, target_type=None, target_class=None, target_location=None, map=None):
        self.master = master
        super().__init__(master=master)
        self.ui_config = ui_config
        self.cols = cols
        if target_class is None:
            target_class = type(target_type)
        self.target_class = target_class
        self.target_location = target_location
        self.map = map

        self.grid()
        self.grid_columnconfigure(0, weight=1)
        self.inputs = dict()
        self.BUTTONS = [
            ['Update', lambda: self.update()],
            ['Add', lambda: self.add()],
            ['Generate', lambda: self.generate()],
            ['Save', lambda: self.save()],
            ['Load', lambda: self.load()],
            ['Clear', lambda: self.clear()],
            ['Close', lambda: self.master.destroy()]
        ]
        self.make_gui()

    def make_gui(self):

        do_nation = False
        do_custom = False
        do_connection= False

        indices, frames, types = [0]*9, list(), dict()  # Make the label frames for the inputs
        for index, (text, input_type) in enumerate(self.ui_config['label_frames']):
            frames.append(ttk.Labelframe(self, text=text, padding=5))
            self.grid_rowconfigure(index, weight=1)
            frames[-1].grid(row=index, column=0, sticky='NEWS', pady=5, padx=10)
            types[input_type] = frames[-1]

        for index, attribute in enumerate(self.ui_config['attributes']):  # Automatically builds settings input based on type

            _, frame, label, options, active = self.ui_config['attributes'][attribute]

            if frame == 4:
                do_nation = True
                continue

            elif frame == 5:
                do_custom = True
                continue

            elif frame == 6:
                do_connection = True
                continue

            state = ttk.NORMAL
            if not active:
                state = ttk.DISABLED

            row, col = indices[frame] // self.cols, self.cols * (indices[frame] % self.cols)
            indices[frame] += 1

            ttk.Label(types[frame], text=label).grid(row=row, column=col, sticky='NEWS', pady=5, padx=5)

            if frame == 0:
                self.inputs[attribute] = ttk.Entry(types[frame], textvariable=ttk.StringVar(), state=state)
            elif frame == 1:
                self.inputs[attribute] = ttk.Combobox(types[frame], values=options, textvariable=ttk.StringVar(), state=state)
            elif frame == 2:
                self.inputs[attribute] = EntryScaleWidget(types[frame], variable=ttk.IntVar(), from_=options[0], to=options[1], state=state)
            elif frame == 3:
                self.inputs[attribute] = ttk.Checkbutton(types[frame], bootstyle="success-round-toggle", variable=ttk.IntVar(), state=state)
            self.inputs[attribute].grid(row=row, column=1+col, sticky='NEWS', pady=5, padx=10)

        if do_nation:  # Nation selection          AGE_NATIONS[AGES.index(self.inputs['age'].get())]
            self.inputs['nations'] = MultiOptionWidget(frames[4], cols=8, options_list=EA_NATIONS, text_index=1)

        if do_custom:  # Custom nation addition/selection  turn this into general addition loader
            self.inputs['custom_nations'] = CustomNationWidget(frames[5], cols=8)

        if do_connection:
            self.inputs['connection_int'] = MultiOptionWidget(frames[6], cols=4, options_list=SPECIAL_NEIGHBOUR, text_index=1)

        if len(self.ui_config['buttons']) > 0:
            button_frame = ttk.Frame(self, bootstyle='primary')
            button_frame.grid(row=len(frames), column=0, sticky='NEWS')

            for index, button in enumerate(self.ui_config['buttons']):
                ttk.Button(button_frame, bootstyle='primary', text=self.BUTTONS[button][0], command=self.BUTTONS[button][1]).grid(row=0, column=index, sticky='WE')
                button_frame.grid_columnconfigure(index, weight=1)

        self.class_2_input()

    def input_2_class(self):

        for attribute in self.ui_config['attributes']:
            attribute_type, widget, _, options, active = self.ui_config['attributes'][attribute]
            if active:
                if widget == 0:
                    setattr(self.target_class, attribute, self.inputs[attribute].get())
                if widget == 1:
                    setattr(self.target_class, attribute, options.index(self.inputs[attribute].get()))
                if widget == 2:
                    setattr(self.target_class, attribute, int(self.inputs[attribute].get()))
                if widget == 3:
                    setattr(self.target_class, attribute, self.inputs[attribute].state())
                elif widget == 4:
                    self.target_class.nations = self.inputs['nations'].options_list
                elif widget == 5:
                    self.target_class.custom_nations = self.inputs['custom_nations'].nations_list

    def class_2_input(self):
        for attribute in self.ui_config['attributes']:
            attribute_type, widget, _, options, __ = self.ui_config['attributes'][attribute]

            if getattr(self.target_class, attribute) is not None:
                if widget == 0:
                    self.inputs[attribute].delete(0, END)
                    self.inputs[attribute].insert(1, str(getattr(self.target_class, attribute)))
                elif widget == 1:
                    self.inputs[attribute].set(options[getattr(self.target_class, attribute)])
                elif widget == 2:
                    self.inputs[attribute].set(getattr(self.target_class, attribute))
                elif widget == 3:
                    if getattr(self.target_class, attribute):
                        self.inputs[attribute].invoke()
                elif widget == 4:
                    for i in getattr(self.target_class, attribute):
                        self.inputs[attribute].options[i].invoke()
                    self.inputs[attribute].options_list = getattr(self.target_class, attribute)
                elif widget == 5:
                    self.inputs[attribute].nations_list = getattr(self.target_class, attribute)

    def add(self):
        self.input_2_class()
        self.target_location.append(self.target_class)

    def generate(self):
        self.input_2_class()
        self.master.destroy()
        GeneratorLoadingWidget(master=self.master.master, map=self.map, settings=self.target_class).generate()

    def save(self):
        self.input_2_class()
        self.target_class.save_file(tkf.asksaveasfilename(parent=self.master, initialdir=ROOT_DIR.parent))

    def load(self):
        self.target_class.load_file(tkf.askopenfilename(parent=self.master, initialdir=ROOT_DIR.parent))
        self.class_2_input()

    def clear(self):
        self.destroy()
        self.__init__(self.master, self.ui_config, self.cols, target_class=self.target_class)


class MultiOptionWidget(ttk.Frame):

    def __init__(self, master, cols, options_list, text_index):
        self.master = master
        super().__init__(master=master)
        self.grid()

        self.options = dict()
        for i, entry in enumerate(options_list):
            self.options[entry[0]] = ttk.Checkbutton(self, text=entry[text_index], bootstyle="dark-outline-toolbutton", variable=ttk.IntVar())
            self.options[entry[0]].grid(row=i // cols, column=i % cols, sticky='WE', pady=2, padx=2)


class CustomNationWidget(ttk.Frame):

    def __init__(self, master, cols):
        self.master = master
        self.cols = cols
        super().__init__(master=master)
        self.grid()
        self.nation_inputs = dict()
        self.nation_list = list()
        self.update()

    def update(self):
        miniframes, row = list(), -1

        for i, nation in enumerate(self.nation_list):
            row, col = i // self.cols, i % self.cols
            mini_frame = ttk.Frame(self)
            mini_frame.grid(row=row, column=col, sticky='WE', pady=2, padx=2)

            self.nation_inputs[i] = ttk.Checkbutton(mini_frame, text=nation[1], bootstyle='warning-outline', variable=ttk.IntVar)
            self.nation_inputs[i].grid(row=0, column=0, sticky='WE')
            ttk.Checkbutton(mini_frame, text=X, bootstyle='warning-outline', command=lambda: self.remove(i)).grid(row=0, column=1, sticky='WE')
            mini_frame.grid_columnconfigure(0, weight=5)
            mini_frame.grid_columnconfigure(1, weight=1)
            miniframes.append(mini_frame)

        add_custom = ttk.Button(self, bootstyle='warning-outline', text='Add Custom Nation', command=lambda: InputToplevel(self, 'Add Custom Nation', UI_CONFIG_CUSTOMNATION, 1, self.nation_list))
        add_custom.grid(row=row+1, column=0)
        add_generic = ttk.Button(self, bootstyle='success-outline', text='Add Generic Start', command=lambda: InputToplevel(self, 'Add Generic Start', UI_CONFIG_GENERICNATION, 1, self.nation_list))
        add_generic.grid(row=row+1, column=1)

    def remove(self, i):

        self.nation_list.pop(i)
        self.nation_inputs[i].destroy()
        self.__init__(self.master, self.cols)


class EntryScaleWidget(ttk.Frame):

    def __init__(self, master, variable, from_, to, state):
        self.master = master
        self.variable = variable
        super().__init__(master=master)
        self.grid()
        self.entry = ttk.Entry(self, textvariable=variable, state=state)
        self.scale = ttk.Scale(self, orient=ttk.HORIZONTAL, variable=variable, from_=from_, to=to, length=150, state=state)
        self.entry.grid(row=0, column=0, sticky='NEWS', pady=2)
        self.scale.grid(row=0, column=1, sticky='NEWS', padx=5, pady=2)

    def set(self, i):
        self.entry.insert(1, i)
        self.scale.set(i)

    def get(self):
        return int(self.variable.get())


class GeneratorLoadingWidget(ttk.Toplevel):

    def __init__(self, master, settings, map=None):
        self.master = master
        self.map = map
        self.settings = settings
        super().__init__(title='Generating Map', iconphoto=ART_ICON)
        self.grid()
        self.columnconfigure(0, minsize=500)
        self.rowconfigure(0, weight=1, minsize=30)
        self.rowconfigure(1, weight=1, minsize=15)
        self.progress_bar = ttk.Progressbar(self, maximum=100, mode='determinate', bootstyle='success', orient=ttk.HORIZONTAL, variable=ttk.IntVar())
        self.status_label_var = ttk.StringVar()
        self.status_label_var.set('Initialising...')
        self.status_label = ttk.Label(self, textvariable=self.status_label_var)
        self.progress_bar.grid(row=0, column=0, sticky='NEWS', pady=2)
        self.status_label.grid(row=1, column=0, sticky='NEWS', pady=2)

    def generate(self):
        self.queue = queue.Queue()  # Some funky threading to make this work
        ThreadedGenerator(self.queue, self, self.map, self.settings).start()
        self.master.after(100, self.process_queue)

    def process_queue(self):
        try:
            msg = self.queue.get_nowait()
        except queue.Empty:
            self.master.after(100, self.process_queue)


class ThreadedGenerator(threading.Thread):
    def __init__(self, queue, ui, map, settings):
        super().__init__()
        self.queue = queue
        self.ui = ui
        self.map = map
        self.settings = settings

    def run(self):
        self.map = DreamAtlasGenerator(settings=self.settings, ui=self.ui, queue=self.queue)
        self.queue.put("Task finished")
        self.ui.destroy()


def run_interface():
    app = ttk.Window(title="DreamAtlas Map Editor", themename="flatly", iconphoto=ART_ICON)

    def _config():
        x = 1

    style_button = ttk.IntVar()

    def swap_theme():
        if style_button.get():
            app.style.theme_use('cyborg')
        else:
            app.style.theme_use('flatly')

    ui = MainInterface(app)

    menu = ttk.Menu(app)
    app.config(menu=menu)
    file_menu = ttk.Menu(menu, tearoff=0)  # The FILE dropdown menu
    file_menu.add_command(label="New", command=lambda: [ui.destroy(), ui.__init__(app)])
    file_menu.add_command(label="Save", command=lambda: ui.save_map(tkf.asksaveasfilename(parent=app, initialdir=ROOT_DIR.parent)))
    file_menu.add_command(label="Load map", command=lambda: ui.load_map(tkf.askdirectory(parent=app, initialdir=ROOT_DIR.parent)))
    file_menu.add_command(label="Load file", command=lambda: ui.load_file(tkf.askopenfilename(parent=app, initialdir=ROOT_DIR.parent)))
    file_menu.add_separator()
    file_menu.add_command(label="Settings", command=_config)
    file_menu.add_separator()
    file_menu.add_checkbutton(label="Dark Mode", command=lambda: swap_theme(), variable=style_button)  # The HELP button

    tools_menu = ttk.Menu(menu, tearoff=0)  # The TOOLS dropdown menu
    tools_menu.add_command(label="Pixel mapping", command=_config)

    generate_menu = ttk.Menu(menu, tearoff=0)  # The GENERATE dropdown menu
    generate_menu.add_command(label="DreamAtlas", command=lambda: InputToplevel(master=ui, title='Generate DreamAtlas Map', ui_config=UI_CONFIG_SETTINGS, cols=2, target_class=ui.settings, map=ui.map))

    menu.add_cascade(label="File", menu=file_menu)
    menu.add_cascade(label="Tools", menu=tools_menu)
    menu.add_cascade(label="Generators", menu=generate_menu)

    app.mainloop()
