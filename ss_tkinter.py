import pyperclip
import ss_classes as ss
from tkinter import *
from fusion_tool_generator import render_fusion_output


# GLOBAL VARIABLES AND LISTS ========================
grid_block_widgets = []
screen_widgets = []
list_of_ssscreens = []
coords = [1,1]


# INITIALIZE SPLIT SCREENER OBJECTS ========================
ss_canvas = ss.Canvas()
ss_canvas.width = 1920
ss_canvas.height = 1080

ss_margin = ss.Margin(ss_canvas)
ss_grid = ss.Grid(ss_canvas,ss_margin)

ss_margin.top, ss_margin.left, ss_margin.bottom, ss_margin.right, ss_grid.gutter = 25,25,25,25,25
ss_grid.cols = 12
ss_grid.rows = 6


# COLOR PALETTE =====================
hover_color = "#2C5360"
original_color = "#40798C"
click_color = "#70A9A1"
screen_color = "#CFD7C7"
background_color = "#0B2027"


# # RECT TRACKER

# def groups(glist, numPerGroup=2):
# 	result = []

# 	i = 0
# 	cur = []
# 	for item in glist:
# 		if not i < numPerGroup:
# 			result.append(cur)
# 			cur = []
# 			i = 0

# 		cur.append(item)
# 		i += 1

# 	if cur:
# 		result.append(cur)

# 	return result

# def average(points):
# 	aver = [0,0]
	
# 	for point in points:
# 		aver[0] += point[0]
# 		aver[1] += point[1]
		
# 	return aver[0]/len(points), aver[1]/len(points)

# class RectTracker:
	
# 	def __init__(self, canvas):
# 		self.canvas = canvas
# 		self.item = None
		
# 	def draw(self, start, end, **opts):
# 		"""Draw the rectangle"""
# 		return self.canvas.create_rectangle(*(list(start)+list(end)), **opts)
		
# 	def autodraw(self, **opts):
# 		"""Setup automatic drawing; supports command option"""
# 		self.start = None
# 		self.canvas.bind("<Button-1>", self.__update, '+')
# 		self.canvas.bind("<B1-Motion>", self.__update, '+')
# 		self.canvas.bind("<ButtonRelease-1>", self.__stop, '+')
		
# 		self._command = opts.pop('command', lambda *args: None)
# 		self.rectopts = opts
		
# 	def __update(self, event):
# 		if not self.start:
# 			self.start = [event.x, event.y]
# 			return
		
# 		if self.item is not None:
# 			self.canvas.delete(self.item)
# 		self.item = self.draw(self.start, (event.x, event.y), **self.rectopts)
# 		self._command(self.start, (event.x, event.y))
		
# 	def __stop(self, event):
# 		self.start = None
# 		self.canvas.delete(self.item)
# 		self.item = None
		
# 	def hit_test(self, start, end, tags=None, ignoretags=None, ignore=[]):
# 		"""
# 		Check to see if there are items between the start and end
# 		"""
# 		ignore = set(ignore)
# 		ignore.update([self.item])
		
# 		# first filter all of the items in the canvas
# 		if isinstance(tags, str):
# 			tags = [tags]
		
# 		if tags:
# 			tocheck = []
# 			for tag in tags:
# 				tocheck.extend(self.canvas.find_withtag(tag))
# 		else:
# 			tocheck = self.canvas.find_all()
# 		tocheck = [x for x in tocheck if x != self.item]
# 		if ignoretags:
# 			if not hasattr(ignoretags, '__iter__'):
# 				ignoretags = [ignoretags]
# 			tocheck = [x for x in tocheck if x not in self.canvas.find_withtag(it) for it in ignoretags]
		
# 		self.items = tocheck
		
# 		# then figure out the box
# 		xlow = min(start[0], end[0])
# 		xhigh = max(start[0], end[0])
		
# 		ylow = min(start[1], end[1])
# 		yhigh = max(start[1], end[1])
		
# 		items = []
# 		for item in tocheck:
# 			if item not in ignore:
# 				x, y = average(groups(self.canvas.coords(item)))
# 				if (xlow < x < xhigh) and (ylow < y < yhigh):
# 					items.append(item)
	
# 		return items




# RENDERING FUNCTIONS ========================
def delete_widgets(list_of_widgets: list[Widget]):
    for widget in list_of_widgets:
        widget.place_forget()
        widget.destroy()
    list_of_widgets.clear()

def widget_from_screen(root: Tk, screen: ss.Screen, color: str, widget_list: list[Widget]) -> Widget:
    """Creates a Label widget from an ss.Screen object and assigns the screen to it as a property."""

    widget = Label(root, bg=color, bd=0, highlightthickness=0, relief='ridge')
    widget.screen = screen

    widget_list.append(widget)

    return widget

def place_screen_widget(widget: Widget) -> None:
    """Renders one label widget from a ss.Screen object and appends it to a group."""
    screen = widget.screen

    relx = screen.x
    rely = 1 - screen.y
    relw = screen.width
    relh = screen.height

    widget.place(relwidth=relw,relheight=relh, anchor=CENTER, relx=relx, rely=rely, bordermode='outside')
    
def create_grid_blocks() -> list[list[ss.Screen]]:
    """
    The preview grid is just a bunch of Screens that are 1x1 in size.
    Every time a change to the grid is made, we have to recreate all of these screens
    to pass to the renderer.
    """
    grid_blocks = []

    for row in range(ss_grid.rows):
        grid_blocks_row = []
        for col in range(ss_grid.cols):
            block = ss.Screen(ss_grid,1,1,col+1,row+1)
            grid_blocks_row.append(block)
        grid_blocks.append(grid_blocks_row)
        # grid_blocks.reverse()
    
    return grid_blocks

def refresh_grid(root: Tk, screens_only: bool = False):
    """
    Every time the user makes any change to the grid settings, 
    it must be re-rendered so that it previews correctly.
    """
    if not screens_only:
        if len(grid_block_widgets) > 0: # would mean no grid has ever been rendered
            delete_widgets(grid_block_widgets)
         
        # Creating ss.Screen objects for each grid block
        grid_blocks = create_grid_blocks()

        # CREATING widgets and indexing them
        for block_y in range(len(grid_blocks)):
            row = grid_blocks[block_y]

            # nrows = len(grid_blocks)
            ncols = len(row)

            for block_x in range(len(row)):
                block = row[block_x]
                widget = widget_from_screen(root,block,original_color,grid_block_widgets)
                
                widget.index = block_x + 1 + block_y * ncols
                # widget.config(text = widget.index)
                grid_blocks_default_state(widget)

        
        # PLACING widgets
        for widget in grid_block_widgets:
            place_screen_widget(widget)

    there_are_screens = False # assume the grid is empty
    if len(list_of_ssscreens) > 0: # would mean no screen widgets have been created
        there_are_screens = True

            
    # Re-rendering screens on top of the grid 
    if there_are_screens:
        delete_widgets(screen_widgets)
        # render_all_screens(root,list_of_ssscreens)
        for screen in list_of_ssscreens:
            widget_from_screen(root, screen, screen_color, screen_widgets)
        for screen_widget in screen_widgets:
            place_screen_widget(screen_widget)


# USER INTERACTION FUNCTIONS    ==================================
def add_screen(root: Tk, coords: list[int,int] = coords):
    """Creates a ss.Screen object and appends it to a group. Calls the render_screen function"""
    print("Adding screen...")

    try:
        new_screen = ss.Screen.create_from_coords(ss_grid, *coords)  #int(screen_size_entry.get())
    except:
        print("Can't create screen. Have you tried resetting the coordinates?")
        return
    print(new_screen)

    # widget = widget_from_screen(root,new_screen,"yellow",screen_widgets)
    # place_screen_widget(widget)

    list_of_ssscreens.append(new_screen)
    print(list_of_ssscreens)

    refresh_grid(root, screens_only=True)

    for block in grid_block_widgets:
        grid_blocks_default_state(block)
        block.config(bg = original_color)

def clear_screens(announce: StringVar):
    announce.set("")
    delete_widgets(screen_widgets)
    list_of_ssscreens.clear()
    print(list_of_ssscreens)

def update_grid(root: Tk, canvas: ss.Canvas, width: int, height: int, scale_label: Label,
                margin: ss.Margin, top: int, left: int, bottom: int, right: int,
                grid: ss.Grid, cols: int, rows: int, gutter: int) -> None:
    
    # update canvas
    canvas.width, canvas.height = width, height

    canvas_width, canvas_height = update_canvas_dimensions(canvas)
    root.config(width=canvas_width, height=canvas_height)

    scale = canvas_width / canvas.width * 100
    scale_label.config(text=f"Preview scale: {scale: .1f}%")

    # update margin
    margin.top, margin.left, margin.bottom, margin.right = top, left, bottom, right

    # update grid
    grid.cols, grid.rows, grid.gutter = cols, rows, gutter
    refresh_grid(root)

def update_canvas_dimensions(canvas: ss.Canvas) -> tuple[int]:
    aspect_ratio = canvas.width/canvas.height
    max_width = 750
    max_height = 550

    if aspect_ratio > 1:
        canvas_width = max_width
        canvas_height = canvas_width / aspect_ratio
    else:
        canvas_height = max_height
        canvas_width = canvas_height * aspect_ratio

    # scale_var.set(canvas_width / ss_canvas.width * 100)
    # scale_text_var.set(f"Preview scale: {scale_text_value.get(): .1f}%")

    return canvas_width, canvas_height


# INTERFACE WIDGET CREATION FUNCTIONS
def mk_entry(root: Frame, name: str, rownumber: int, colnumber: int, default_value: int, save_at: dict[str,tuple[Widget]]) -> None:
        label = Label(root, text=f"{name}:", justify='left', padx=20,font="Archivo")
        label.grid(row=rownumber, column=colnumber, sticky=W)

        entry = Entry(root, width=5, justify=RIGHT)
        entry.insert(0,default_value)
        entry.grid(row=rownumber, column=colnumber+1, padx = 20)

        save_at[name] = (label,entry)


# OUTPUTTING FUNCTIONS  ==================================
def render_for_fusion(screens: list[ss.Screen], canvas: ss.Canvas, fusion_studio: IntVar, announce: StringVar) -> str:
    fusion_studio = bool(fusion_studio.get())

    

    screen_values = []
    for screen in screens:
        screen_value = screen.get_values()
        screen_values.append(screen_value)
    fusion_output = render_fusion_output(screen_values,canvas.resolution,fusion_studio)
    pyperclip.copy(fusion_output)

    announce.set("Node tree successfully copied to the clipboard.")
    
    return fusion_output

def save_preset():
    ...


# STATE OF BUTTONS      ==================================
def grid_blocks_default_state(widget: Widget):
    widget.bind("<Enter>", become_hover_color)
    widget.bind("<Leave>", become_regular_color)
    widget.bind("<Button-1>", register_first_coord)

def grid_blocks_selected_state(widget: Widget):
    widget.unbind("<Leave>")
    widget.unbind("<Enter>")
    widget.unbind("<Button-1>")
    widget.bind("<ButtonRelease-1>", register_2nd_coord_and_add_screen)


# EVENT HANDLING FUNCS  ==================================
def become_hover_color(event: Event):
    widget = event.widget
    widget.configure(bg = hover_color)

def become_regular_color(event: Event):
    widget = event.widget
    widget.configure(bg = original_color)

def become_selected_color(event: Event):
    widget = event.widget
    widget.configure(bg = click_color)
    grid_blocks_selected_state(widget)

def register_first_coord(event: Event):
    global coords

    coords.clear()
    coords.append(event.widget.index)
    event.widget.config(bg = click_color)

    for block in grid_block_widgets:
        grid_blocks_selected_state(block)
    print(coords)

def should_be_painted(block: Widget, grid:ss.Grid) -> bool:
    global coords

    block_x, block_y = ss.get_coords(block.index,grid.matrix)
    coords_1, coords_2 = ss.get_coords(coords[0],grid.matrix), ss.get_coords(coords[1],grid.matrix)
    coords_x, coords_y = (coords_1[0], coords_2[0]+1), (coords_1[1], coords_2[1]+1)

    if block_x in range(*coords_x):
        if block_y in range(*coords_y):
            return True
    return False

def register_2nd_coord_and_add_screen(event: Event):
    global coords
    global ss_grid

    x,y = event.widget.winfo_pointerxy()
    widget_released_on = event.widget.winfo_containing(x, y)

    coords.append(widget_released_on.index)

    for block in grid_block_widgets:
        if should_be_painted(block, ss_grid):
            block.config(bg = click_color)

    print(coords)

    add_screen(event.widget.master,coords)




# ACTUAL APP    ==================================
def main():
    root = Tk()

    # TK VARS
    fusion_studio = IntVar()
    

    # REGULAR VARS
    canvas_width, canvas_height = update_canvas_dimensions(ss_canvas)

    scale_text_value = DoubleVar()
    scale_text_value.set(canvas_width / ss_canvas.width * 100) # Broke, doesn't update automatically any more

    scale_text = StringVar()
    scale_text.set(f"Preview scale: {scale_text_value.get(): .1f}%")


    #Root Window Settings
    root.title('SplitScreener')
    root.resizable(False,False)


    # SETTING UP THE MAIN TK GRID
    root.columnconfigure(index=1,   weight=1, minsize=200)  # LEFT SIDEBAR
    root.columnconfigure(index=2,   weight=1, minsize=800)  # MAIN SECTION, THE CREATOR
    root.columnconfigure(index=3,   weight=1, minsize=200)  # RIGHT SIDEBAR (nothing there yet)
    root.rowconfigure(   index=1,   weight=3)               # HEADER
    root.rowconfigure(   index=2,   weight=1)               # MAIN SECTION, THE CREATOR FRAME AND SETTINGS
    root.rowconfigure(   index=3,   weight=1)               # THE RENDER BUTTON FRAME
    root.rowconfigure(   index=4,   weight=3)               # FOOTER


    # CREATING THE FRAMES
    header =                Frame(root)
    button_frame_left =     Frame(root)
    creator_frame =         Frame(root)
    button_frame_right =    Frame(root) # useless atm
    render_bttn_frame =     Frame(root)
    footer =                Frame(root)

    # adding them to the grid
    header.grid(            column=1,   row=1,  columnspan=3)
    button_frame_left.grid( column=1,   row=2)
    creator_frame.grid(     column=2,   row=2,  padx=10, pady=10)
    button_frame_right.grid(column=3,   row=2)
    render_bttn_frame.grid( column=2,   row=3)
    footer.grid(            column=1,   row=4,  columnspan=3)


    # APP TITLE
    app_title = Label(header, height=1, text="SplitScreener", font="Archivo 24 bold", justify=CENTER)

    app_title.pack(anchor=S, pady=20)


    # CREATOR FRAME WIDGETS
    # scale label
    preview_scale_lbl = Label(
        creator_frame,
        textvariable=scale_text, 
        justify=LEFT, 
        pady=0, padx = 20,
        font="Archivo 12"
        )

    # the canvas
    canvas = Canvas(
        creator_frame, 
        width = canvas_width, height=canvas_height, 
        bg=background_color, bd=0, highlightthickness=0,
        relief='ridge', cursor="cross"
        )

    

    # tracker = RectTracker(canvas)

    # def onDrag(start, end):
    #     global x,y
    #     items = tracker.hit_test(start, end)
    #     for x in tracker.items:
    #         if x not in items:
    #             canvas.itemconfig(x, fill='grey')
    #         else:
    #             canvas.itemconfig(x, fill='blue')
	
    # tracker.autodraw(fill="", width=2, command=onDrag)

    # gridding...   
    preview_scale_lbl.grid(column=1,row=2,sticky=NE,pady=10)
    canvas.grid(row=1, column=1, sticky=N)

    
    # RENDER BUTTON FRAME WIDGETS
    # the render button
    render_button = Button(
        render_bttn_frame,
        height=2,font="Archivo 16", 
        text="Render Fusion Output", 
        command=lambda: render_for_fusion(
            list_of_ssscreens, 
            ss_canvas,
            fusion_studio, 
            status_bar_text
            )
        )

    # fusion studio checkbox
    fu_studio_checkbox = Checkbutton(
        render_bttn_frame,
        text="Fusion Studio (no MediaIns or Outs)", 
        justify=LEFT,
        variable=fusion_studio, 
        font="Archivo 10", 
        pady=10
        )

    # gridding...
    render_button.grid(     column=1, row=1, sticky=N)
    fu_studio_checkbox.grid(column=1, row=2, sticky=N)


    # FOOTER FRAME WIDGET
    status_bar_text = StringVar()
    status_bar = Label(footer, textvariable=status_bar_text)

    status_bar.pack(pady=25)


    # ADDING SOME BUTTONS ======================
    clear_all_button = Button(
        button_frame_left, text="Clear Screens",
        command=lambda:clear_screens(status_bar_text)
    )
    clear_all_button.grid(row=14, column = 1,pady=10, columnspan=2)


    # CANVAS SETTINGS
    canvas_entries = {}
    mk_entry(button_frame_left, "Width",  1, 1, ss_canvas.width,     canvas_entries)
    mk_entry(button_frame_left, "Height", 2, 1, ss_canvas.height,    canvas_entries)
    Label(button_frame_left, height=1).grid(row=3, column=1)


    # MARGIN SETTINGS 4,5,6,7,8
    margin_entries = {}
    mk_entry(button_frame_left, "Top",     4, 1, ss_margin._top_px,       margin_entries)
    mk_entry(button_frame_left, "Left",    5, 1, ss_margin._left_px,      margin_entries)
    mk_entry(button_frame_left, "Bottom",  6, 1, ss_margin._bottom_px,    margin_entries)
    mk_entry(button_frame_left, "Right",   7, 1, ss_margin._right_px,     margin_entries)
    Label(button_frame_left, height=1).grid(row= 8, column=1)


    # GRID SETTINGS 9,10,11,12,13==================
    grid_entries = {}
    mk_entry(button_frame_left, "Cols",    9, 1, ss_grid.cols,       grid_entries)
    mk_entry(button_frame_left, "Rows",   10, 1, ss_grid.rows,       grid_entries)
    mk_entry(button_frame_left, "Gutter", 11, 1, ss_grid._gutter_px, grid_entries)
    Label(button_frame_left, height=1).grid(row=12, column=1)

    update_grid_button = Button(
        button_frame_left, text="Update Grid", command=lambda: update_grid(
            canvas, ss_canvas, int(canvas_entries['Width'][1].get()), 
            int(canvas_entries['Height'][1].get()), preview_scale_lbl,

            ss_margin, int(margin_entries['Top'][1].get()), int(margin_entries['Left'][1].get()), 
            int(margin_entries['Bottom'][1].get()), int(margin_entries['Right'][1].get()),

            ss_grid, int(grid_entries['Cols'][1].get()), int(grid_entries['Rows'][1].get()), 
            int(grid_entries['Gutter'][1].get())
            )
    )
    update_grid_button.grid(row=13, column=1, columnspan=2)


    # RENDER GRID FOR THE FIRST TIME ====================
    refresh_grid(canvas)
   
    x, y = None, None
    def cool_design(event):
        global x, y
        kill_xy()
        
        dashes = [3, 2]
        x = canvas.create_line(event.x, 0, event.x, 1000, dash=dashes, tags='no')
        y = canvas.create_line(0, event.y, 1000, event.y, dash=dashes, tags='no')
        canvas.tag_raise(x, y)
        
    def kill_xy(event=None):
        canvas.delete('no')

    canvas.bind('<Motion>', cool_design, '+')



    root.mainloop()


if __name__ == "__main__":
    main()