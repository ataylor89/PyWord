import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import colorchooser
from tkinter import font
import configparser

config = configparser.ConfigParser()
config.read('wordprocessor.ini')
fgcolor = config.get('DEFAULT', 'foreground_color', fallback='#ffffff')
bgcolor = config.get('DEFAULT', 'background_color', fallback='#0099ff')
fontfamily = config.get('DEFAULT', 'font_family', fallback='Courier New')
fontsize = config.getint('DEFAULT', 'font_size', fallback=14)

class WordProcessor(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry('800x600')
        self.title("Word Processor")
        self.menubar = tk.Menu(self)
        self.filemenu = tk.Menu(self.menubar)
        self.filemenu.add_command(label='New', command=self.new_file)
        self.filemenu.add_command(label='Open', command=self.open_file)
        self.filemenu.add_command(label='Save', command=self.save_file)
        self.filemenu.add_command(label='Save as', command=self.save_file_as)
        self.filemenu.add_command(label='Close tab', command=self.close_tab)
        self.filemenu.add_command(label='Exit', command=self.exit)
        self.menubar.add_cascade(label='File', menu=self.filemenu)
        self.colormenu = tk.Menu(self.menubar)
        self.colormenu.add_command(label='Select foreground', command=self.select_fgcolor)
        self.colormenu.add_command(label='Select background', command=self.select_bgcolor)
        self.menubar.add_cascade(label='Colors', menu=self.colormenu)
        self.config(menu=self.menubar)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')
        self.notebook.bind('<<NotebookTabChanged>>', self.handle_tab_changed)
        self.refresh_menu_items()
        self.font = font.Font(family=fontfamily, size=fontsize)

    def new_file(self):
        text = tk.Text(self.notebook, fg=fgcolor, bg=bgcolor, font=self.font)
        self.notebook.add(text, text='Untitled')
        self.notebook.select(self.notebook.tabs()[-1])
        self.refresh_menu_items()

    def open_file(self):
        filename = filedialog.askopenfilename()
        text = tk.Text(self.notebook, fg=fgcolor, bg=bgcolor, font=self.font)
        text.pack(expand=True, fill='both')
        self.notebook.add(text, text=filename)
        with open(filename, 'r') as f:
            contents = f.read()
            text.insert('1.0', contents)
        self.notebook.select(self.notebook.tabs()[-1])
        self.refresh_menu_items()

    def save_file(self):
        tabid = self.notebook.select()
        filename = self.notebook.tab(tabid, "text")
        text = self.notebook.nametowidget(tabid)
        contents = text.get('1.0', 'end')
        with open(filename, 'w') as f:
            f.write(contents)

    def save_file_as(self):
        tabid = self.notebook.select()
        filename = filedialog.asksaveasfilename()
        if filename:
            self.notebook.tab(tabid, text=filename)
            self.save_file()
            self.refresh_menu_items()

    def close_tab(self):
        self.notebook.forget("current")

    def exit(self):
        self.quit()

    def refresh_menu_items(self):
        tabid = self.notebook.select()
        if tabid and self.notebook.tab(tabid, "text") != 'Untitled':
            self.filemenu.entryconfig("Save", state="active")
        else:
            self.filemenu.entryconfig("Save", state="disabled")

    def handle_tab_changed(self, *args):
        self.refresh_menu_items()

    def select_fgcolor(self):
        color = colorchooser.askcolor()
        tabid = self.notebook.select()
        text = self.notebook.nametowidget(tabid)
        text.configure(fg=color[1])

    def select_bgcolor(self):
        color = colorchooser.askcolor()
        tabid = self.notebook.select()
        text = self.notebook.nametowidget(tabid)
        text.configure(bg=color[1])

if __name__ == '__main__':
    app = WordProcessor()
    app.mainloop()