import tkinter as tk
import gui
import ssl

ssl._create_default_https_context = ssl._create_stdlib_context            

main_window = gui.MenuWindow(my_app=tk.Tk(), my_title='My Image Manipulator')
main_window.app.mainloop()