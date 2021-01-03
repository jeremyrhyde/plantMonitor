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

        self.master.title("plantMonitor")
        self.main_window = tk.Canvas(master = self.master, width = WIDTH, height=HEIGHT, bg='black')

        self.menu_tabs()
        self.overview_window()
        #self.lighting_buttons()
        #self.image_viewer()


    def overview_window(self):
        self.border = int(WIDTH*0.025)
        self.x_mid1 = int(WIDTH*0.475)
        self.y_mid1 = int(HEIGHT*0.375)
        self.y_mid2 = int(HEIGHT*0.450)

        # Camera box
        self.camera_pos = [self.border, 3*self.border]
        self.c_dim = [self.x_mid1 - 2*self.border, int(WIDTH*0.36)]
        self.draw_rect(self.camera_pos, self.c_dim, 'darkgrey')
        self.image_viewer()

        # Lighting box
        self.lighting_pos = [self.x_mid1, 3*self.border]
        self.l_dim = [WIDTH - (self.lighting_pos[0] + 3*self.border), self.y_mid1 - (self.lighting_pos[1] + int(0.5*self.border))]
        self.draw_rect(self.lighting_pos, self.l_dim, 'darkgrey')
        self.draw_rect((self.lighting_pos[0]+5, self.lighting_pos[1]-5), self.l_dim, 'darkgrey')
        self.lighting_buttons()

        # Movement box
        self.movement_pos = [self.lighting_pos[0], self.y_mid2]
        self.m_dim = [self.l_dim[0], HEIGHT - (self.y_mid2 + 3*self.border)]
        self.draw_rect(self.movement_pos, self.m_dim, 'darkgrey')
        self.draw_rect((self.movement_pos[0]+5, self.movement_pos[1]-5), self.m_dim, 'darkgrey')
        self.movement_inputs()

        self.main_window.pack()


    def draw_rect(self, x0y0, dim, color):
        self.main_window.create_line(x0y0[0], x0y0[1], x0y0[0] + dim[0] , x0y0[1], fill = color)
        self.main_window.create_line(x0y0[0] + dim[0] , x0y0[1], x0y0[0] + dim[0] , x0y0[1] + dim[1], fill = color)
        self.main_window.create_line(x0y0[0] + dim[0] , x0y0[1] + dim[1], x0y0[0], x0y0[1] + dim[1], fill = color)
        self.main_window.create_line(x0y0[0], x0y0[1], x0y0[0], x0y0[1] + dim[1], fill = color)
    ## TABS

    def menu_tabs(self):

        self.main_window.create_line(0, 38, WIDTH , 38, fill = 'darkgrey')
        self.main_window.create_line(0, 40, WIDTH , 40, fill = 'darkgrey')

        self.main_window.pack()

        self.menu_font = 'Hevetica'
        self.menu_font_size = 14

        menu_width = 160

        # Control Menu
        self.controlMenuButton = tk.Button(text='Overiew',command=self.active_button_command, width=10, height=1)
        self.controlMenuButton.config(font=(self.menu_font, self.menu_font_size, 'bold'), bg='darkgrey', fg='black')
        self.controlMenuButton.place(x = 0, y = 5)

        # Display Menu
        self.displayMenuButton = tk.Button(text='Display',command=self.active_button_command, width=10, height=1)
        self.displayMenuButton.config(font=(self.menu_font, self.menu_font_size, 'bold'), bg='darkgrey', fg='black')
        self.displayMenuButton.place(x = menu_width+2, y = 5)

        # Environmental Data Menu
        self.envMenuButton = tk.Button(text='Control',command=self.active_button_command, width=10, height=1)
        self.envMenuButton.config(font=(self.menu_font, self.menu_font_size, 'bold'), bg='darkgrey', fg='black')
        self.envMenuButton.place(x = 2*(menu_width+2), y = 5)

        # Information Data Menu
        self.envMenuButton = tk.Button(text='Information',command=self.active_button_command, width=10, height=1)
        self.envMenuButton.config(font=(self.menu_font, self.menu_font_size, 'bold'), bg='darkgrey', fg='black')
        self.envMenuButton.place(x = 3*(menu_width+2), y = 5)


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
        self.active_lighting_pos = [self.lighting_pos[0] + 20, self.lighting_pos[1] + 20]
        self.passive_lighting_pos = [self.lighting_pos[0] + 20, self.active_lighting_pos[1] + 55]


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
        self.activeLightButton = tk.Button(text='OFF',command=self.active_button_command, width=10, height=1)
        self.activeLightButton.config(font=(self.lighting_font, self.lighting_font_size+2, 'bold'),
                                     bg='darkgrey',
                                     fg='black')

        self.activeLightButton.place(x = self.active_lighting_pos[0] + 290, y = self.active_lighting_pos[1] - 10)

    def active_button_command(self):
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
        self.passiveLightButton = tk.Button(text='OFF', command=self.passive_button_command, width=10, height=1)
        self.passiveLightButton.config(font=(self.lighting_font,self.lighting_font_size+2,'bold'),
                                       bg='darkgrey',
                                       fg='black')

        self.passiveLightButton.place(x = self.passive_lighting_pos[0] + 290, y = self.passive_lighting_pos[1] - 10)

    def passive_button_command(self):
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


    def movement_inputs(self):
        self.movement_arrows = [860,380]

        self.main_window.create_line(self.movement_pos[0]+ int(self.m_dim[0]*0.5), self.movement_pos[1] + 20,
                                     self.movement_pos[0]+ int(self.m_dim[0]*0.5), self.movement_pos[1] + self.m_dim[1] - 20,
                                     fill = 'darkgrey')

        self.main_window.create_line(self.movement_arrows[0], self.movement_arrows[1]+100,
                                     self.movement_arrows[0], self.movement_arrows[1]-100,
                                     fill = 'darkgrey')

        self.main_window.create_line(self.movement_arrows[0]+100, self.movement_arrows[1],
                                     self.movement_arrows[0]-100, self.movement_arrows[1],
                                     fill = 'darkgrey')
        self.main_window.pack()

        self.postion_text()
        self.arrow_keys()
        self.manual_movement_input()

    def postion_text(self):
        self.posTextLabel = tk.Label(text='Current Position:   0, 0   ')
        self.posTextLabel.config(font=(self.lighting_font, 22,'normal'),
                                     bg='green',
                                     fg='white')
        self.posTextLabel.place(x = self.movement_pos[0], y = self.movement_pos[1] - 50)


    def arrow_keys(self):
        diameter = 75

        self.downButton = tk.Button(text='', command=self.passive_button_command, width=1, height=1)
        self.downButton.place(x = self.movement_arrows[0], y = self.movement_arrows[1] + diameter)

        self.leftButton = tk.Button(text='', command=self.passive_button_command, width=1, height=1)
        self.leftButton.place(x = self.movement_arrows[0] - diameter, y = self.movement_arrows[1])

        self.rightButton = tk.Button(text='', command=self.passive_button_command, width=1, height=1)
        self.rightButton.place(x = self.movement_arrows[0] + diameter, y = self.movement_arrows[1])

        self.upButton = tk.Button(text='', command=self.passive_button_command, width=1, height=1)
        self.upButton.place(x = self.movement_arrows[0], y = self.movement_arrows[1] - diameter)


    def manual_movement_input(self):

        # X
        self.xInputLabel = tk.Label(text='X - POS')
        self.xInputLabel.config(font=(self.lighting_font, self.lighting_font_size + 4,'normal'),
                                     bg='black',
                                     fg='white')
        self.xInputLabel.place(x = self.movement_pos[0] + 20, y = self.movement_pos[1] + int(self.m_dim[1]*.3))

        self.xInputEntry = tk.Entry(width = 4)
        self.xInputEntry.place(x = self.movement_pos[0] + 150, y = self.movement_pos[1] + int(self.m_dim[1]*.3))

        # Y
        self.yInputLabel = tk.Label(text='Y - POS')
        self.yInputLabel.config(font=(self.lighting_font, self.lighting_font_size + 4,'normal'),
                                     bg='black',
                                     fg='white')
        self.yInputLabel.place(x = self.movement_pos[0] + 20, y = self.movement_pos[1] + int(self.m_dim[1]*.5))

        self.yInputEntry = tk.Entry(width = 4)
        self.yInputEntry.place(x = self.movement_pos[0] + 150, y = self.movement_pos[1] + int(self.m_dim[1]*.5))

        # Go
        self.goButton = tk.Button(text='GO', command=self.passive_button_command, width=4, height=1)
        self.goButton.place(x = self.movement_pos[0] + int(self.m_dim[0]*0.2), y = self.movement_pos[1] + int(self.m_dim[1]*.8))

root = tk.Tk()
app = Plant_GUI(master=root)
app.mainloop()
