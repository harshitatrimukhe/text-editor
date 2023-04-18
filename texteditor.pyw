import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
from tkinter import messagebox
import os
from hashlib import md5
class Notebook(ttk.Notebook):
    def __init__(self, *args):
        ttk.Notebook.__init__(self, *args)
        self.enable_traversal()
        self.pack(expand=1, fill="both")
        self.bind("<B1-Motion>", self.move_tab)
    def current_tab(self):
        return self.nametowidget( self.select() )
    def indexed_tab(self, index):
        return self.nametowidget( self.tabs()[index] )
    def move_tab(self, event):
        if self.index("end") > 1:
            y = self.current_tab().winfo_y() - 5
            try:
                self.insert( min( event.widget.index('@%d,%d' % (event.x, y)), self.index('end')-2), self.select() )
            except tk.TclError:
                pass
class Tab(ttk.Frame):
    def __init__(self, *args, FileDir):
        ttk.Frame.__init__(self, *args)
        self.textbox = self.create_text_widget()
        self.file_dir = FileDir
        self.file_name = os.path.basename(FileDir)
        self.status = md5(self.textbox.get(1.0, 'end').encode('utf-8'))
    def create_text_widget(self):
        xscrollbar = tk.Scrollbar(self, orient='horizontal')
        xscrollbar.pack(side='bottom', fill='x')
        yscrollbar = tk.Scrollbar(self)
        yscrollbar.pack(side='right', fill='y')
        textbox = tk.Text(self, relief='sunken', borderwidth=0, wrap='none')
        textbox.config(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set, undo=True, autoseparators=True)
        textbox.pack(fill='both', expand=True)
        xscrollbar.config(command=textbox.xview)
        yscrollbar.config(command=textbox.yview)
        return textbox
class Editor:
    def __init__(self, master):
        self.master = master
        self.master.title("Notepad+=1")
        self.frame = tk.Frame(self.master)
        self.frame.pack()
        self.filetypes = (("Normal text file", "*.txt"), ("all files", "*.*"))
        self.init_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
        self.untitled_count = 1
        self.nb = Notebook(master)
        self.nb.bind("<Button-2>", self.close_tab)
        self.nb.bind('<<NotebookTabChanged>>', self.tab_change)
        self.nb.bind('<Button-3>', self.right_click_tab)
        self.master.protocol('WM_DELETE_WINDOW', self.exit)
        menubar = tk.Menu(self.master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.new_file)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save_file)
        filemenu.add_command(label="Save As...", command=self.save_as)
        filemenu.add_command(label="Close", command=self.close_tab)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit)
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=self.undo)
        editmenu.add_separator()
        editmenu.add_command(label="Cut", command=self.cut)
        editmenu.add_command(label="Copy", command=self.copy)
        editmenu.add_command(label="Paste", command=self.paste)
        editmenu.add_command(label="Delete", command=self.delete)
        editmenu.add_command(label="Select All", command=self.select_all)
        formatmenu = tk.Menu(menubar, tearoff=0)
        self.word_wrap = tk.BooleanVar()
        formatmenu.add_checkbutton(label="Word Wrap", onvalue=True, offvalue=False, variable=self.word_wrap, command=self.wrap)
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit", menu=editmenu)
        menubar.add_cascade(label="Format", menu=formatmenu)
        self.master.config(menu=menubar)
        self.right_click_menu = tk.Menu(self.master, tearoff=0)
        self.right_click_menu.add_command(label="Undo", command=self.undo)
        self.right_click_menu.add_separator()
        self.right_click_menu.add_command(label="Cut", command=self.cut)
        self.right_click_menu.add_command(label="Copy", command=self.copy)
        self.right_click_menu.add_command(label="Paste", command=self.paste)
        self.right_click_menu.add_command(label="Delete", command=self.delete)
        self.right_click_menu.add_separator()
        self.right_click_menu.add_command(label="Select All", command=self.select_all)
        self.tab_right_click_menu = tk.Menu(self.nb, tearoff=0)
        self.tab_right_click_menu.add_command(label="New Tab", command=self.new_file)
        self.master.bind_class('Text', '<Control-s>', self.save_file)
        self.master.bind_class('Text', '<Control-o>', self.open_file)
        self.master.bind_class('Text', '<Control-n>', self.new_file)
        self.master.bind_class('Text', '<Control-a>', self.select_all)
        self.master.bind_class('Text', '<Control-w>', self.close_tab)
        self.master.bind_class('Text', '<Button-3>', self.right_click)
        self.nb.add(Tab(FileDir='Untitled'), text='Untitled')
        self.nb.add(Tab(FileDir='f'), text=' + ')
    def open_file(self, *args):        
        file_dir = (tkinter
         .filedialog
         .askopenfilename(initialdir=self.init_dir, title="Select file", filetypes=self.filetypes))
        if file_dir:
            try:
                file = open(file_dir)
                new_tab = Tab(FileDir=file_dir)
                self.nb.insert( self.nb.index('end')-1, new_tab, text=os.path.basename(file_dir))
                self.nb.select( new_tab )
                self.nb.current_tab().textbox.insert('end', file.read())
                self.nb.current_tab().status = md5(self.nb.current_tab().textbox.get(1.0, 'end').encode('utf-8'))
            except:
                return
    def save_as(self):
        curr_tab = self.nb.current_tab()
        file_dir = (tkinter
         .filedialog
         .asksaveasfilename(initialdir=self.init_dir, title="Select file", filetypes=self.filetypes, defaultextension='.txt'))
        if not file_dir:
            return
        if file_dir[-4:] != '.txt':
            file_dir += '.txt'
        curr_tab.file_dir = file_dir
        curr_tab.file_name = os.path.basename(file_dir)
        self.nb.tab( curr_tab, text=curr_tab.file_name)
        file = open(file_dir, 'w')
        file.write(curr_tab.textbox.get(1.0, 'end'))
        file.close()
        curr_tab.status = md5(curr_tab.textbox.get(1.0, 'end').encode('utf-8'))
    def save_file(self, *args):
        curr_tab = self.nb.current_tab()
        if not curr_tab.file_dir:
            self.save_as()
        else:
            with open(curr_tab.file_dir, 'w') as file:
                file.write(curr_tab.textbox.get(1.0, 'end'))
            curr_tab.status = md5(curr_tab.textbox.get(1.0, 'end').encode('utf-8'))          
    def new_file(self, *args):                
        new_tab = Tab(FileDir=self.default_filename())
        new_tab.textbox.config(wrap= 'word' if self.word_wrap.get() else 'none')
        self.nb.insert( self.nb.index('end')-1, new_tab, text=new_tab.file_name)
        self.nb.select( new_tab )
    def copy(self):
        try: 
            sel = self.nb.current_tab().textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
        except tk.TclError:
            pass         
    def delete(self):
        try:
            self.nb.current_tab().textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass   
    def cut(self):
        try: 
            sel = self.nb.current_tab().textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
            self.nb.current_tab().textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass        
    def wrap(self):
        if self.word_wrap.get() == True:
            for i in range(self.nb.index('end')-1):
                self.nb.indexed_tab(i).textbox.config(wrap="word")
        else:
            for i in range(self.nb.index('end')-1):
                self.nb.indexed_tab(i).textbox.config(wrap="none")
    def paste(self):
        try: 
            self.nb.current_tab().textbox.insert(tk.INSERT, self.master.clipboard_get())
        except tk.TclError:
            pass      
    def select_all(self, *args):
        curr_tab = self.nb.current_tab()
        curr_tab.textbox.tag_add(tk.SEL, "1.0", tk.END)
        curr_tab.textbox.mark_set(tk.INSERT, tk.END)
        curr_tab.textbox.see(tk.INSERT)
    def undo(self):
        self.nb.current_tab().textbox.edit_undo()
    def right_click(self, event):
        self.right_click_menu.post(event.x_root, event.y_root)
    def right_click_tab(self, event):
        self.tab_right_click_menu.post(event.x_root, event.y_root)
    def close_tab(self, event=None):
        if event is None or event.type == str( 2 ):
            selected_tab = self.nb.current_tab()
        else:
            try:
                index = event.widget.index('@%d,%d' % (event.x, event.y))
                selected_tab = self.nb.indexed_tab( index )
                if index == self.nb.index('end')-1:
                    return
            except tk.TclError:
                return
        if self.save_changes(selected_tab):
            if self.nb.index('current') > 0 and self.nb.select() == self.nb.tabs()[-2]:
                self.nb.select(self.nb.index('current')-1)
            self.nb.forget( selected_tab )
        if self.nb.index("end") <= 1:
            self.master.destroy()
    def exit(self):        
        if self.save_changes(self.nb.current_tab()):
            self.master.destroy()
        else:
            return        
    def save_changes(self, tab):
        if md5(tab.textbox.get(1.0, 'end').encode('utf-8')).digest() != tab.status.digest():
            if self.nb.current_tab() != tab:
                self.nb.select(tab)
            m = messagebox.askyesnocancel('Editor', 'Do you want to save changes to ' + tab.file_dir + '?' )
            if m is None:
                return False
            elif m is True:
                self.save_file()
            else:
                pass    
        return True
    def default_filename(self):
        self.untitled_count += 1
        return 'Untitled' + str(self.untitled_count-1)
    def tab_change(self, event):
        # If last tab was selected, create new tab
        if self.nb.select() == self.nb.tabs()[-1]:
            self.new_file()
def main(): 
    root = tk.Tk()
    app = Editor(root)
    root.mainloop()
if __name__ == '__main__':
    main()