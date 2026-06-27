import os
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

import PIL.Image
import PIL.ImageTk

import entidades


IMAGE_DIRECTORY = Path(__file__).resolve().parent / "imagens"


class MenuWindow:
    def __init__(self, my_app, my_title, image_directory=IMAGE_DIRECTORY) -> None:
        self.app = my_app
        self.app.title(my_title)
        self.image_directory = Path(image_directory)

        self.menu_label = tk.Label(self.app, text="Menu")
        self.msg_label = tk.Label(self.app, text="")
        self.janela_carrega_imagem_button = tk.Button(
            self.app, text="Carrega Imagem", command=self.carrega_janela_entrada
        )
        self.janela_view_imagem_button = tk.Button(
            self.app, text="Mostra ultima imagem", command=self.carrega_view_image
        )
        self.janela_view_all_images_button = tk.Button(
            self.app, text="Mostra as imagens salvas", command=self.carrega_view_all_images
        )
        self.last_image = None
        self.image_paths = []
        self.load_images()

        self.menu_label.pack()
        self.msg_label.pack()
        self.janela_carrega_imagem_button.pack()
        self.janela_view_imagem_button.pack()
        self.janela_view_all_images_button.pack()

    def carrega_janela_entrada(self):
        self.janela_carrega_imagem_button.config(state="disabled")
        self.entrada_window = EntradaWindow(self)

    def carrega_view_image(self):
        self.load_images()
        if not self.image_paths:
            messagebox.showinfo("Info", "Imagem nao existe!")
            return

        self.janela_view_imagem_button.config(state="disabled")
        WindowImageViewer(
            self.image_paths[-1],
            self.app,
            on_close=lambda: self.janela_view_imagem_button.config(state="normal"),
        )

    def carrega_view_all_images(self):
        self.load_images()
        if not self.image_paths:
            messagebox.showinfo("Info", "Ainda nao foram carregadas imagens!")
            return

        self.janela_view_all_images_button.config(state="disabled")
        ViewAllImagesWindow(self)

    def load_images(self):
        utilidades = entidades.Util()
        self.image_paths = utilidades.list_files_by_date(self.image_directory)


class EntradaWindow:
    def __init__(self, menu_window):
        self.menu_window = menu_window
        self.app = tk.Toplevel(menu_window.app)
        self.app.title("Entrada de Imagem")
        self.app.transient(menu_window.app)

        self.url_label = tk.Label(self.app, text="URL da imagem:")
        self.url_entry = tk.Entry(self.app, width=50)
        self.msg_label = tk.Label(self.app, text="")
        self.download_button = tk.Button(self.app, text="Download", command=self.download_image)

        self.url_label.pack()
        self.url_entry.pack(padx=5, pady=5, fill=tk.BOTH)
        self.msg_label.pack()
        self.download_button.pack()

        self.utilidades = entidades.Util()
        self.download_thread = None
        self.download_queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.closed = False

        self.app.protocol("WM_DELETE_WINDOW", self.destroy)

    def download_image(self):
        url = self.url_entry.get().strip()
        if not url:
            self.msg_label.config(text="URL Vazia!")
            return

        try:
            os.makedirs(self.menu_window.image_directory, exist_ok=True)
            nome, extensao = self.utilidades.extrair_nome_extensao_url(url)
            filename = self.utilidades.criar_nome_unico(
                self.menu_window.image_directory,
                nome,
                extensao,
            )
        except ValueError as ve:
            self.msg_label.config(text=str(ve))
            return
        except OSError as ex:
            self.msg_label.config(text=f"Nao foi possivel criar o arquivo: {ex}")
            return

        filename_path = os.path.join(self.menu_window.image_directory, filename)
        self.download_button.config(state="disabled")
        self.msg_label.config(text="Aguarde...")
        self.cancel_event = threading.Event()

        self.download_thread = threading.Thread(
            target=self._download_worker,
            args=(url, filename_path, self.cancel_event),
            daemon=True,
        )
        self.download_thread.start()
        self.app.after(100, self._check_download_queue)

    def _download_worker(self, url, filename_path, cancel_event):
        try:
            download = entidades.Download(
                url,
                filename_path,
                cancel_event=cancel_event,
            )
            download.executa()
        except Exception as ex:
            self.download_queue.put((None, ex))
            return

        self.download_queue.put((filename_path, None))

    def _check_download_queue(self):
        if self.closed:
            return

        try:
            filename_path, error = self.download_queue.get_nowait()
        except queue.Empty:
            self.app.after(100, self._check_download_queue)
            return

        self._download_finished(filename_path, error)

    def _download_finished(self, filename_path, error):
        self.download_button.config(state="normal")

        if error:
            self.msg_label.config(text=f"Erro no download: {error}")
            return

        self.msg_label.config(text="Download concluido com sucesso!")
        self.menu_window.last_image = filename_path
        self.menu_window.load_images()

    def destroy(self):
        self.closed = True
        self.cancel_event.set()
        self.menu_window.janela_carrega_imagem_button.config(state="normal")
        self.app.destroy()


class ViewAllImagesWindow:
    def __init__(self, menu_window):
        self.menu_window = menu_window
        self.app = tk.Toplevel(menu_window.app)
        self.app.title("All Images")
        self.app.transient(menu_window.app)

        self.image_paths = []
        self.thumbnail_photos = []
        self.find_images()

        self.thumbnail_frame = tk.Frame(self.app)
        self.thumbnail_frame.pack(expand=True, fill=tk.Y)

        self.create_widgets()
        self.app.protocol("WM_DELETE_WINDOW", self.destroy)

    def create_widgets(self):
        self.canvas = tk.Canvas(self.thumbnail_frame, width=150, height=320)
        self.canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)

        self.scrollbar = tk.Scrollbar(
            self.thumbnail_frame, orient=tk.VERTICAL, command=self.canvas.yview
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        self.inner_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            (0, 0), anchor="nw", window=self.inner_frame
        )
        self.inner_frame.bind("<Configure>", self._update_scroll_region)

        self.display_thumbnails()

    def find_images(self):
        utilidades = entidades.Util()
        self.image_paths = utilidades.list_files_by_date(self.menu_window.image_directory)

    def display_thumbnails(self):
        for image_path in self.image_paths:
            try:
                with PIL.Image.open(image_path) as image:
                    thumbnail = image.copy()
                    thumbnail.thumbnail((100, 100), PIL.Image.Resampling.LANCZOS)
            except (OSError, PIL.UnidentifiedImageError) as ex:
                print(f"Erro ao carregar miniatura {image_path}: {ex}")
                continue

            thumbnail_photo = PIL.ImageTk.PhotoImage(thumbnail)
            self.thumbnail_photos.append(thumbnail_photo)
            thumbnail_button = tk.Button(
                self.inner_frame,
                image=thumbnail_photo,
                command=lambda path=image_path: self.open_image(path),
            )
            thumbnail_button.pack(side=tk.TOP, pady=2)

    def _update_scroll_region(self, _event=None):
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def open_image(self, image_path):
        WindowImageViewer(image_path, self.app)

    def destroy(self):
        self.menu_window.janela_view_all_images_button.config(state="normal")
        self.app.destroy()


class WindowImageViewer:
    def __init__(self, image_path, parent, on_close=None):
        self.parent = parent
        self.on_close = on_close
        self.image_path = image_path
        self.image = None
        self.image2 = None

        if not os.path.exists(image_path):
            messagebox.showerror("Erro", "Image not found!", parent=parent)
            self._notify_close()
            return

        try:
            self.image = PIL.Image.open(image_path)
        except (OSError, PIL.UnidentifiedImageError) as ex:
            messagebox.showerror("Erro", f"Nao foi possivel abrir a imagem: {ex}", parent=parent)
            self._notify_close()
            return

        self.app = tk.Toplevel(parent)
        self.app.title("View Image")
        self.app.transient(parent)

        self.image_frame = tk.Frame(self.app)
        self.image_frame.pack(expand=True, fill=tk.BOTH)

        self.create_widgets()
        self.app.protocol("WM_DELETE_WINDOW", self.destroy)

    def create_widgets(self):
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

        self.display_image()

    def display_image(self):
        width, height = self.image.size
        self.canvas.config(scrollregion=(0, 0, width, height))
        self.image2 = PIL.ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.image2)

    def destroy(self):
        self._notify_close()
        self.app.destroy()

    def _notify_close(self):
        if self.on_close:
            self.on_close()
            self.on_close = None
