import tkinter as tk

HEIGHT = 600
WIDTH = 1080

border_effects = {"flat" : tk.FLAT, "sunken" : tk.SUNKEN, "raised" : tk.RAISED, "groove" : tk.GROOVE, "ridge" : tk.RIDGE}

class Plant_GUI(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.active_index = 0
        self.passive_index = 0
        self.pack()

        self.main_window()
        self.menu_tabs()
        self.lighting_buttons()
        self.image_viewer()


    def main_window(self):
        self.main_window = tk.Canvas(master = self.master, width = WIDTH, height=HEIGHT, bg='black')

        self.border = int(WIDTH*0.025)
        self.x_mid1 = int(WIDTH*0.475)
        self.y_mid1 = int(HEIGHT*0.35)

        # Camera box
        self.camera_pos = [self.border, 100]
        self.c_dim = [self.x_mid1 - 2*self.border, int(WIDTH*0.35)]
        self.draw_rect(self.camera_pos, self.c_dim, 'darkgrey')

        # Lighting box
        self.lighting_pos = [self.x_mid1, 2*self.border]
        self.l_dim = [WIDTH - (self.lighting_pos[0] + 3*self.border), self.y_mid1 - (self.lighting_pos[1] + self.border)]
        self.draw_rect(self.lighting_pos, self.l_dim, 'darkgrey')
        self.draw_rect((self.lighting_pos[0]+5, self.lighting_pos[1]-5), self.l_dim, 'darkgrey')

        # Movement box
        self.movement_pos = [self.lighting_pos[0], self.y_mid1]
        self.m_dim = [self.l_dim[0], HEIGHT - (self.y_mid1 + 3*self.border)]
        self.draw_rect(self.movement_pos, self.m_dim, 'darkgrey')
        self.draw_rect((self.movement_pos[0]+5, self.movement_pos[1]-5), self.m_dim, 'darkgrey')

        self.main_window.pack()


    def draw_rect(self, x0y0, dim, color):
        self.main_window.create_line(x0y0[0], x0y0[1], x0y0[0] + dim[0] , x0y0[1],
                                     fill = color)
        self.main_window.create_line(x0y0[0] + dim[0] , x0y0[1], x0y0[0] + dim[0] , x0y0[1] + dim[1],
                                     fill = color)
        self.main_window.create_line(x0y0[0] + dim[0] , x0y0[1] + dim[1], x0y0[0], x0y0[1] + dim[1],
                                     fill = color)
        self.main_window.create_line(x0y0[0], x0y0[1], x0y0[0], x0y0[1] + dim[1],
                                     fill = color)
    ## TABS

    def menu_tabs(self):
        pass
        #self.passiveLightButton = tk.Button(text='Hi', command=self.toggle_button)
        #self.passiveLightButton.place(x = 50, y = 300)

    ## IMAGE

    def image_viewer(self):
        self.take_image()
        self.show_image()

    def take_image(self):
        self.takeImage = tk.Button(text='Take Image', width=48, height=1)
        self.takeImage.place(x = self.camera_pos[0],
                             y = self.camera_pos[1] + self.c_dim[1]+8)

    def show_image(self):
        pass

    ## LIGHTING

    def lighting_buttons(self):
        self.lighting_font = 'Courier'
        self.lighting_font_size = 14
        self.active_lighting_pos = [self.lighting_pos[0] + 15, self.lighting_pos[1] + 20]
        self.passive_lighting_pos = [self.lighting_pos[0] + 15, self.active_lighting_pos[1] + 50]


        self.active_lighting_button()
        self.passive_lighting_button()

    def active_lighting_button(self):

        # Active lighting label
        self.activeLightLabel = tk.Label(text='Active Lighting')
        self.activeLightLabel.config(font=(self.lighting_font, self.lighting_font_size + 4,'normal'),
                                     bg='black',
                                     fg='white')

        self.activeLightLabel.place(x = self.active_lighting_pos[0], y = self.active_lighting_pos[1])

        # Active lighting button
        self.activeLightButton = tk.Button(text='OFF',command=self.active_toggle_button, width=10, height=1)
        self.activeLightButton.config(font=(self.lighting_font, self.lighting_font_size+2, 'bold'),
                                     bg='darkgrey',
                                     fg='black')

        self.activeLightButton.place(x = self.active_lighting_pos[0] + 300, y = self.active_lighting_pos[1] - 10)

    def active_toggle_button(self):
        if self.active_index:
            self.activeLightButton.config(text='ON')
            self.activeLightButton.config(font=(self.lighting_font,self.lighting_font_size+2,'bold'),
                                         bg='green',
                                         fg='black')
        else:
            self.activeLightButton.config(text='OFF')
            self.activeLightButton.config(font=(self.lighting_font,self.lighting_font_size+2,'bold'),
                                         bg='darkgrey',
                                         fg='black')

        self.active_index = not self.active_index

    def passive_lighting_button(self):

        # LABEL
        self.passiveLightLabel = tk.Label(text='Passive Lighting')
        self.passiveLightLabel.config(font=(self.lighting_font,self.lighting_font_size + 4,'normal'),
                                      bg='black',
                                      fg='white')

        self.passiveLightLabel.place(x = self.passive_lighting_pos[0], y = self.passive_lighting_pos[1])

        # BUTTON
        self.passiveLightButton = tk.Button(text='OFF', command=self.passive_toggle_button, width=10, height=1)
        self.passiveLightButton.config(font=(self.lighting_font,self.lighting_font_size+2,'bold'),
                                       bg='darkgrey',
                                       fg='black')

        self.passiveLightButton.place(x = self.passive_lighting_pos[0] + 300, y = self.passive_lighting_pos[1] - 10)

    def passive_toggle_button(self):
        if self.passive_index:
            self.passiveLightButton.config(text='ON')
            self.passiveLightButton.config(font=(self.lighting_font,self.lighting_font_size+2,'bold'),
                                           bg='green',
                                           fg='black')
        else:
            self.passiveLightButton.config(text='OFF')
            self.passiveLightButton.config(font=(self.lighting_font,self.lighting_font_size+2,'bold'),
                                           bg='darkgrey',
                                           fg='black')

        self.passive_index = not self.passive_index

    def create_widgets(self):
        camera_preview = tk.Label(text = 'hello', width = 20, height = 20)
        camera_preview.place(x = 10, y = 200)

    def create_button(self):
        button = tk.Button(text = 'hello', width = 10, height = 1, bg='blue')
        button.place(x = 75, y = 75)


#c = tk.Frame(master = window, width = WIDTH, height=HEIGHT, bg='black')
#c#.pack()


root = tk.Tk()
app = Plant_GUI(master=root)
app.mainloop()