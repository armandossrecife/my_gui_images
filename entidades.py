import mimetypes
import os
from datetime import datetime
from urllib.parse import urlparse

import PIL.Image
import requests
from tqdm import tqdm


class Util:
    EXTENSOES_IMAGEM = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

    def extrair_nome_extensao_url(self, url):
        try:
            parsed_url = urlparse(url)
            if parsed_url.scheme not in ("http", "https"):
                raise ValueError(f"Protocolo nao suportado: {parsed_url.scheme}")

            caminho_arquivo = parsed_url.path
            if not caminho_arquivo:
                raise ValueError("Caminho do arquivo ausente na URL")

            nome_arquivo, extensao = os.path.splitext(os.path.basename(caminho_arquivo))
            extensao = extensao.lower()
            if not nome_arquivo:
                raise ValueError("Nome do arquivo ausente na URL")
            if extensao not in self.EXTENSOES_IMAGEM:
                raise ValueError("A URL precisa apontar para um arquivo de imagem suportado")

            return nome_arquivo, extensao
        except Exception as ex:
            raise ValueError(str(ex)) from ex

    def criar_nome_unico(self, directory_path, nome_arquivo, extensao):
        filename = f"{nome_arquivo}{extensao}"
        filename_path = os.path.join(directory_path, filename)
        if not os.path.exists(filename_path):
            return filename

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{nome_arquivo}_{timestamp}{extensao}"

    def list_files_by_date(self, directory_path):
        try:
            if not os.path.isdir(directory_path):
                return []

            file_paths = [
                os.path.join(directory_path, file)
                for file in os.listdir(directory_path)
                if self._is_supported_image_path(os.path.join(directory_path, file))
            ]

            file_info = []
            for file_path in file_paths:
                try:
                    creation_time = os.path.getctime(file_path)
                    creation_datetime = datetime.fromtimestamp(creation_time)
                    file_info.append((file_path, creation_datetime))
                except OSError as e:
                    print(f"Error getting creation time for {file_path}: {e}")

            file_info.sort(key=lambda x: x[1])
            return [file_path for file_path, _ in file_info]
        except OSError as e:
            print(f"Error listing files: {e}")
            return []

    def _is_supported_image_path(self, file_path):
        _, extensao = os.path.splitext(file_path)
        return os.path.isfile(file_path) and extensao.lower() in self.EXTENSOES_IMAGEM


class Download:
    def __init__(self, url, path_arquivo):
        self.url = url
        self.path_arquivo = path_arquivo
        self.callback = None

    def set_callback(self, callback):
        self.callback = callback

    def executa(self):
        try:
            print("Aguarde...")
            response = requests.get(self.url, stream=True, timeout=(5, 30))
            response.raise_for_status()
            self._validar_content_type(response)

            total_size = int(response.headers.get("content-length", 0))
            with open(self.path_arquivo, "wb") as file:
                with tqdm(total=total_size, unit="B", unit_scale=True, desc=self.path_arquivo) as pbar:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                            pbar.update(len(chunk))
                            if self.callback:
                                self.callback(total_size, pbar.n)

            self._validar_arquivo_imagem()
            print(
                f"Download completo. Tamanho: {total_size}, Arquivo salvo em: {self.path_arquivo}"
            )
            return total_size
        except requests.exceptions.MissingSchema as ex:
            self._remover_arquivo_invalido()
            raise Exception("URL invalida. Certifique-se de fornecer uma URL valida.") from ex
        except requests.exceptions.RequestException as e:
            self._remover_arquivo_invalido()
            raise Exception(f"Erro na conexao: {e}") from e
        except (OSError, PIL.UnidentifiedImageError, ValueError) as e:
            self._remover_arquivo_invalido()
            raise Exception(f"Arquivo baixado nao e uma imagem valida: {e}") from e

    def _validar_content_type(self, response):
        content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
        guessed_type, _ = mimetypes.guess_type(self.path_arquivo)
        if content_type and not content_type.startswith("image/"):
            raise ValueError(f"Content-Type inesperado: {content_type}")
        if guessed_type and not guessed_type.startswith("image/"):
            raise ValueError(f"Extensao de arquivo inesperada: {self.path_arquivo}")

    def _validar_arquivo_imagem(self):
        with PIL.Image.open(self.path_arquivo) as image:
            image.verify()

    def _remover_arquivo_invalido(self):
        try:
            if os.path.exists(self.path_arquivo):
                os.remove(self.path_arquivo)
        except OSError as e:
            print(f"Erro ao remover arquivo invalido {self.path_arquivo}: {e}")
