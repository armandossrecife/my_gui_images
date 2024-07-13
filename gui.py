import tkinter as tk
import os
import entidades
import PIL.Image
import PIL.ImageTk
from tkinter import messagebox
import entidades

class MenuWindow: 
    def __init__(self, my_app, my_title) -> None:
        # App Frame
        self.app = my_app
        self.app.title(my_title)

        # Add UI elements
        self.menu_label = tk.Label(self.app, text="Menu")
        self.menu_label.pack()

        self.msg_label = tk.Label(self.app, text="")
        self.msg_label.pack()        
    
        self.janela_carrega_imagem_button = tk.Button(self.app, text="Carrega Imagem", command=self.carrega_janela_entrada)
        self.janela_carrega_imagem_button.pack()

        self.janela_view_imagem_button = tk.Button(self.app, text="Mostra última imagem", command=self.carrega_view_image)
        self.janela_view_imagem_button.pack()

        self.janela_view_all_images_button = tk.Button(self.app, text="Mostra as Imagens salvas", command=self.carrega_view_all_images)
        self.janela_view_all_images_button.pack()

        self.last_image = None

        self.image_paths = []

        self.load_images()

    def carrega_janela_entrada(self):
        self.entrada_window = EntradaWindow(tk.Tk(), "Entrada de Imagem", self)
        # Armazena a referência à janela
        self.janela_carrega_imagem_button.config(state="disabled")

    def carrega_view_image(self):
        if len(self.image_paths) > 0: 
            # Armazena a referência à janela
            self.janela_view_imagem_button.config(state="disabled")
            image_path = self.image_paths[-1]
            downloaded_image_path = image_path  # Replace with your actual path
            view_window_image = WindowImageViewer(downloaded_image_path, self)
            view_window_image.app.mainloop()
        else: 
            messagebox.showinfo("Info", "Imagem não existe!") 
        
    def carrega_view_all_images(self):
        if len(self.image_paths) > 0:
            self.janela_view_all_images_button.config(state="disabled")
            view_all_images = ViewAllImagesWindow(self)
            view_all_images.app.mainloop()
        else:
            messagebox.showinfo("Info", "Ainda não foram carregadas imagens!") 

    def load_images(self):
            utilidades = entidades.Util()
            self.image_paths = utilidades.list_files_by_date("imagens")

class EntradaWindow(): 
    def __init__(self, my_app, my_title, menu_window):
        # App Frame
        self.app = my_app
        self.app.title(my_title)

        # Armazena a referência a janela principal
        self.menu_window = menu_window

        # Add UI elements
        self.url_label = tk.Label(self.app, text="URL da imagem:")
        self.url_label.pack()

        self.url_entry = tk.Entry(self.app, width=50)
        self.url_entry.pack(padx=5, pady=5,fill = tk.BOTH)

        self.msg_label = tk.Label(self.app, text="")
        self.msg_label.pack()        

        self.download_button = tk.Button(self.app, text="Download", command=self.download_image)
        self.download_button.pack()

        self.utilidades = entidades.Util()

        # Bind the close button to the destroy function
        self.app.protocol("WM_DELETE_WINDOW", self.destroy)

    def download_image(self):
        try:
            url = self.url_entry.get()
            if len(url) == 0:
                raise ValueError('URL Vazia!')
            os.makedirs("imagens", exist_ok=True)  
            self.msg_label.config(text="Aguarde...")
            self.msg_label.update_idletasks()
            nome, extensao = self.utilidades.extrair_nome_extensao_url(url)
            filename = nome + extensao
            filename_path = "imagens" + "/" + filename 
            # Executa o download
            download = entidades.Download(url, filename_path)
            download.executa()
            self.msg_label.config(text="Download concluído com sucesso!")
            self.menu_window.last_image = filename_path
            self.menu_window.load_images()
        except ValueError as ve: 
            print(f'Erro: {str(ve)}')
            self.msg_label.config(text=f'{str(ve)}')
        except Exception as ex:
            print("Error:", ex)
            self.msg_label.config(text=f'Erro no download: {str(ex)}')
    
    def destroy(self):
        # Reabilita o botão na janela principal
        self.menu_window.janela_carrega_imagem_button.config(state="normal")
        self.app.destroy()

class ViewWindow:
    def __init__(self, image_path, menu_window):
        self.app = tk.Toplevel()
        self.app.title("Image Viewer")

        # Armazena a referência ao menu principal
        self.menu_window = menu_window

        # Error handling: Check if image exists before loading
        if not os.path.exists(image_path):
            self.show_error_message("Image not found!")
            return

        # Load image using PIL
        self.image = PIL.Image.open(image_path)

        # Create Scrollbar objects
        self.x_scrollbar = tk.Scrollbar(self.app, orient=tk.HORIZONTAL)
        self.y_scrollbar = tk.Scrollbar(self.app, orient=tk.VERTICAL)

        # Create Canvas using the image size
        self.canvas = tk.Canvas(self.app, xscrollcommand=self.x_scrollbar.set,
                               yscrollcommand=self.y_scrollbar.set,
                               width=self.image.width, height=self.image.height)

        # Set Scrollbar commands
        self.x_scrollbar.config(command=self.canvas.xview)
        self.y_scrollbar.config(command=self.canvas.yview)

        # Convert image to PhotoImage
        self.photo = PIL.ImageTk.PhotoImage(self.image)

        # Create an image object on the canvas with scrollbars
        self.image_on_canvas = self.canvas.create_image(0, 0, image=self.photo, anchor="nw")

        # Pack the widgets
        self.canvas.pack(side="left", fill="both", expand=True)
        self.x_scrollbar.pack(side="bottom", fill="x")
        self.y_scrollbar.pack(side="right", fill="y")

        # Bind the close button to the destroy function
        self.app.protocol("WM_DELETE_WINDOW", self.destroy)

    def show_error_message(self, message):
        self.app = tk.Toplevel()
        self.app.title("Error")
        tk.Label(self.app, text=message).pack()

    def destroy(self):
        # Reabilita o botão na janela principal
        self.menu_window.janela_view_imagem_button.config(state="normal")
        self.app.destroy()

class ViewAllImagesWindow:
    def __init__(self, menu_window):
        # Create the main window
        self.app = tk.Toplevel()
        self.app.title("All Images")
    
        # Store reference to parent window
        self.menu_window = menu_window

        # List to store image paths
        self.image_paths = []

        # Get all image paths from the "imagens" folder
        self.find_images()

        # Create a frame to hold the thumbnail list
        self.thumbnail_frame = tk.Frame(self.app)
        self.thumbnail_frame.pack(expand=True, fill=tk.Y)

        self.create_widgets()  # Separate function to create widgets

        # Bind the close button to the destroy function
        self.app.protocol("WM_DELETE_WINDOW", self.destroy)
    
    def create_widgets(self):
        # Create a canvas for scrolling
        self.canvas = tk.Canvas(self.thumbnail_frame)
        self.canvas.config(width=150, height=320)
        self.canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)

        # Create a scrollbar
        self.scrollbar = tk.Scrollbar(self.thumbnail_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure scrollbar and canvas
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        # Create inner frame to hold buttons (avoid directly adding to canvas)
        self.inner_frame = tk.Frame(self.canvas)

        self.display_thumbnails()  # Separate function to display the buttons
    
    def find_images(self):
        # TODO: if filename.endswith((".jpg", ".jpeg", ".png")):
        utilidades = entidades.Util()
        self.image_paths = utilidades.list_files_by_date("imagens")

    def display_thumbnails(self):
        for i, image_path in enumerate(self.image_paths):
            # Create a thumbnail using PIL
            thumbnail = PIL.Image.open(image_path).resize((100, 100), PIL.Image.ANTIALIAS)
            thumbnail_photo = PIL.ImageTk.PhotoImage(thumbnail)
            # Create a button with the thumbnail and path information
            thumbnail_button = tk.Button(self.inner_frame, image=thumbnail_photo, command=lambda path=image_path: self.open_image(path))
            thumbnail_button.image = thumbnail_photo
            thumbnail_button.pack(side=tk.TOP)
        
            # Place the inner frame on the canvas with an anchor (optional)
        self.canvas.create_window((0, 0), anchor="nw", window=self.inner_frame)

        # Update scroll region based on inner frame size (optional)
        self.canvas.update_idletasks()  # Wait for widgets to be drawn
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    # Open the selected image in a separate window
    def open_image(self, image_path):
        # Create a WindowImageViewer instance for the selected image
        WindowImageViewer(image_path, self.menu_window)

    def destroy(self):
        # Reabilita o botão na janela principal
        self.menu_window.janela_view_all_images_button.config(state="normal")
        self.app.destroy()

class WindowImageViewer:
  """
  A class to display an image with scrollbars in a tkinter window.
  """

  def __init__(self, image_path, menu_window):
    """
    Initializes the image viewer with a parent window and an image path (default provided).

    Args:
      parent: The parent window for the image viewer (optional).
      image_path: The path to the image file to be displayed.
    """
    self.app = tk.Toplevel()
    self.app.title("View Image")
    
    # Store reference to parent window
    self.menu_window = menu_window

    # Create a frame to hold the image
    self.image_frame = tk.Frame(self.app)
    
    # Error handling: Check if image exists before loading
    if not os.path.exists(image_path):
        self.show_error_message("Image not found!")
        return

    # Load image using PIL
    self.image = PIL.Image.open(image_path)
    self.image_frame.pack(expand=True, fill=tk.BOTH)

    self.create_widgets(image_path)  # Separate function to create widgets

    # Bind the close button to the destroy function
    self.app.protocol("WM_DELETE_WINDOW", self.destroy)

  def create_widgets(self, image_path):
    """
    Creates the canvas, scrollbars, and displays the image.

    Args:
      image_path: The path to the image file to be displayed.
    """
    self.canvas = tk.Canvas(self.image_frame, relief=tk.SUNKEN)
    self.canvas.config(width=800, height=600, highlightthickness=0)

    self.sbarV = tk.Scrollbar(self.image_frame, orient=tk.VERTICAL)
    self.sbarH = tk.Scrollbar(self.image_frame, orient=tk.HORIZONTAL)

    self.sbarV.config(command=self.canvas.yview)
    self.sbarH.config(command=self.canvas.xview)

    self.canvas.config(yscrollcommand=self.sbarV.set)
    self.canvas.config(xscrollcommand=self.sbarH.set)

    self.sbarV.pack(side=tk.RIGHT, fill=tk.Y)
    self.sbarH.pack(side=tk.BOTTOM, fill=tk.X)

    self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    self.display_image(image_path)  # Separate function to display the image

  def display_image(self, image_path):
    """
    Opens the image, sets scroll region, and displays it.

    Args:
      image_path: The path to the image file to be displayed.
    """
    try:
      self.image = PIL.Image.open(image_path)
      width, height = self.image.size
      self.canvas.config(scrollregion=(0, 0, width, height))
      self.image2 = PIL.ImageTk.PhotoImage(self.image)
      self.imgtag = self.canvas.create_image(0, 0, anchor="nw", image=self.image2)
    except FileNotFoundError:
      print("Error: Image file not found!")
    
  def destroy(self):
    # Reabilita o botão na janela principal
    self.menu_window.janela_view_imagem_button.config(state="normal")
    self.app.destroy()