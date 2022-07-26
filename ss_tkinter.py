import ss_classes as ss
from tkinter import *
from ss_generator import render_fusion_output

# GLOBAL VARIABLES AND LISTS ========================
grid_block_widgets = []
screen_widgets = []
list_of_ssscreens = []
coords = [1,1]


# SPLIT SCREENER VARS ========================
ss_canvas = ss.Canvas()
ss_canvas.width = 1920
ss_canvas.height = 1080

ss_margin = ss.Margin(ss_canvas)
ss_grid = ss.Grid(ss_canvas,ss_margin)

ss_margin.top, ss_margin.left, ss_margin.bottom, ss_margin.right, ss_grid.gutter = 40,40,40,40,40
ss_grid.cols = 12
ss_grid.rows = 6

# RENDERING FUNCTIONS ========================
# Computer generates graphics.
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

    relx = screen.x - screen.width/2
    rely = 1 - (screen.y + screen.height/2)
    relw = screen.width
    relh = screen.height

    widget.place(relwidth=relw,relheight=relh, anchor=NW, relx=relx, rely=rely, bordermode='outside')
    
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

        # CREATING widgets
        for row_index in range(len(grid_blocks)):
            row = grid_blocks[row_index]

            for col_index in range(len(row)):
                block = row[col_index]
                widget = widget_from_screen(root,block,original_color,grid_block_widgets)
                widget.index = col_index+1 + row_index * len(row)
                grid_state_1(widget)

        
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
            widget_from_screen(root, screen, "yellow", screen_widgets)
        for screen_widget in screen_widgets:
            place_screen_widget(screen_widget)



# USER INTERACTION FUNCTIONS
# User sets parameters that change what is to be rendered.
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
        grid_state_1(block)
        block.config(bg = original_color)

def add_cols(root: Tk, amount: int = 1):
    ss_grid.cols = ss_grid.cols + amount
    delete_widgets(screen_widgets)
    refresh_grid(root)
    coords.clear()

def register_first_coord(event: Event):
    global coords

    coords.clear()
    coords.append(event.widget.index)
    event.widget.config(bg = click_color)

    for block in grid_block_widgets:
        grid_state_2(block)
    print(coords)

def should_be_painted(block: Widget, grid:ss.Grid) -> bool:
    global coords

    block_x, block_y = ss.get_coords(block.index,grid.matrix)
    coords_1, coords_2 = ss.get_coords(coords[0],grid.matrix), ss.get_coords(coords[1],grid.matrix)
    coords_x, coords_y = (coords_1[0], coords_2[0]+1), (coords_1[1], coords_2[1]+1)
    # xspan = abs(coords_x[0] - coords_x[1])+1
    # yspan = abs(coords_y[0] - coords_y[1])+1

    if block_x in range(*coords_x):
        if block_y in range(*coords_y):
            return True
    return False

def register_second_coord(event: Event):
    global coords
    global ss_grid

    x,y = event.widget.winfo_pointerxy()
    widget_released_on = event.widget.winfo_containing(x, y)

    coords.append(widget_released_on.index)

    for block in grid_block_widgets:
        if should_be_painted(block, ss_grid):
            block.config(bg = click_color)

    print(coords)

def clear_screens():
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
    root.grid_forget()
    root.grid(padx=(770-canvas_width)/2, pady=(620-canvas_height)/2, row = 3, column=2)

    scale = canvas_width / canvas.width * 100
    scale_label.config(text=f"Preview scale: {scale: .1f}%")

    # update margin
    margin.top, margin.left, margin.bottom, margin.right = top, left, bottom, right

    # update grid
    grid.cols, grid.rows, grid.gutter = cols, rows, gutter
    refresh_grid(root)

def update_canvas_dimensions(canvas: ss.Canvas) -> tuple[int]:
    aspect_ratio = canvas.width/canvas.height
    max_geometry = 750
    max_height = 600

    if aspect_ratio > 1:
        canvas_width = max_geometry
        canvas_height = canvas_width / aspect_ratio
    else:
        canvas_height = max_height
        canvas_width = canvas_height * aspect_ratio

    return canvas_width, canvas_height

# WIDGET CREATION FUNCTIONS
def generate_entry(root: Frame, name: str, rownumber: int, colnumber: int, default_value: int, save_at: dict[str,tuple[Widget]]) -> None:
        label = Label(root, text=f"{name}:", justify=LEFT, padx=20)
        label.grid(row=rownumber, column=colnumber)

        entry = Entry(root, width=5, justify=RIGHT)
        entry.insert(0,default_value)
        entry.grid(row=rownumber, column=colnumber+1, padx = 20)

        save_at[name] = (label,entry)


# OUTPUTTING FUNCTIONS
def render_for_fusion(screens: list[ss.Screen], canvas: ss.Canvas):
    screen_values = []
    for screen in screens:
        screen_value = screen.get_values()
        screen_values.append(screen_value)
    render_fusion_output(screen_values,canvas.resolution)

# COLOR PALETTE =====================
hover_color = "#0000cc"
original_color = "#0000ff"
click_color = "#8888ff"

# STATE OF BUTTONS ===========
def grid_state_1(widget: Widget):
    widget.bind("<Enter>", darker_color)
    widget.bind("<Leave>", regular_color)
    widget.bind("<Button-1>", register_first_coord)

def grid_state_2(widget: Widget):
    widget.unbind("<Leave>")
    widget.unbind("<Enter>")
    widget.unbind("<Button-1>")
    widget.bind("<ButtonRelease-1>", register_second_coord)

def darker_color(event: Event):
    widget = event.widget
    widget.configure(bg = hover_color)

def regular_color(event: Event):
    widget = event.widget
    widget.configure(bg = original_color)

def selected_color(event: Event):
    widget = event.widget
    widget.configure(bg = click_color)
    grid_state_2(widget)



def main():

    root = Tk()

    # SETTING UP THE MAIN WINDOW ======================
    x = 1200
    y = 900
    dim = {
        "x": x,
        "y": y,
        "screenx": root.winfo_screenwidth(),
        "screeny": root.winfo_screenheight(),
        "screenx_center": int(root.winfo_screenwidth()/2),
        "screeny_center": int(root.winfo_screenheight()/2),
    }

    #Root Window
    root.title('SplitScreener')
    root.geometry(f"{dim['x']}x{dim['y']}+{dim['screenx_center'] - int(dim['x']/2)}+{dim['screeny_center'] - int(dim['y']/2)}")
    # root.resizable(False,False)


    canvas_width, canvas_height = update_canvas_dimensions(ss_canvas)

    # spacer on top
    Label(height=3).grid(row=1)


    # scale label
    scale = canvas_width / ss_canvas.width * 100
    preview_scale_lbl = Label(text=f"Preview scale: {scale: .1f}%", justify=LEFT, pady=0, padx = 20,font="Archivo 12")
    preview_scale_lbl.grid(column=2,row=2,sticky=E,pady=0)

    # the canvas
    canvas = Canvas(root, width = canvas_width, height = canvas_height, bg="#1e1e1e", bd=0, highlightthickness=0, relief='ridge')
    canvas.grid(padx=10, pady=10, row = 3, column=2)
    
    # the render button
    render_button = Button(height=2,font="Archivo 16", text="Render Fusion Output", command=lambda: render_for_fusion(list_of_ssscreens, ss_canvas))
    render_button.grid(column=2, row=   4)
    
    
    # RENDER GRID FOR THE FIRST TIME ====================
    refresh_grid(canvas)



    # ADDING SOME BUTTONS ======================
    button_frame_left = Frame(bd=0, highlightthickness=0, relief='ridge')
    button_frame_left.grid(column=1, row =3)

    button_frame_right = Frame(bd=0, highlightthickness=0, relief='ridge')
    button_frame_right.grid(column=3, row =3)


    add_screen_button = Button(button_frame_right, text="Add Screen", command=lambda: add_screen(canvas, coords))
    add_screen_button.grid(row=3, column = 2,pady=10)

    clear_all_button = Button(button_frame_right, text="Clear Screens", command=clear_screens)
    clear_all_button.grid(row=4, column = 2,pady=10)
    
    

    # CANVAS SETTINGS
    canvas_entries = {}
    generate_entry(button_frame_left, "Width",  1, 1, ss_canvas.width,     canvas_entries)
    generate_entry(button_frame_left, "Height", 2, 1, ss_canvas.height,    canvas_entries)
    Label(button_frame_left, height=1).grid(row=3, column=1)

    # MARGIN SETTINGS 4,5,6,7,8
    margin_entries = {}
    generate_entry(button_frame_left, "Top",     4, 1, ss_margin._top_px,       margin_entries)
    generate_entry(button_frame_left, "Left",    5, 1, ss_margin._left_px,      margin_entries)
    generate_entry(button_frame_left, "Bottom",  6, 1, ss_margin._bottom_px,    margin_entries)
    generate_entry(button_frame_left, "Right",   7, 1, ss_margin._right_px,     margin_entries)
    Label(button_frame_left, height=1).grid(row= 8, column=1)

    # GRID SETTINGS 9,10,11,12,13==================
    grid_entries = {}
    generate_entry(button_frame_left, "Cols",    9, 1, ss_grid.cols,       grid_entries)
    generate_entry(button_frame_left, "Rows",   10, 1, ss_grid.rows,       grid_entries)
    generate_entry(button_frame_left, "Gutter", 11, 1, ss_grid._gutter_px, grid_entries)
    Label(button_frame_left, height=1).grid(row=12, column=1)

    update_grid_button = Button(
        button_frame_left, text="Update Grid", command=lambda: update_grid(canvas, ss_canvas,
            int(canvas_entries['Width'][1].get()), int(canvas_entries['Height'][1].get()), preview_scale_lbl,
            ss_margin, int(margin_entries['Top'][1].get()), int(margin_entries['Left'][1].get()), int(margin_entries['Bottom'][1].get()), int(margin_entries['Right'][1].get()),
            ss_grid, int(grid_entries['Cols'][1].get()), int(grid_entries['Rows'][1].get()), int(grid_entries['Gutter'][1].get())
            )
    )
    update_grid_button.grid(row=13, column=1, columnspan=2)

    
    
    
    
    root.mainloop()


if __name__ == '__main__':
    main()
