import requests
from tqdm import tqdm
from urllib.parse import urlparse
import os
from datetime import datetime

class Util:
    def extrair_nome_extensao_url(self, url):
        try:
            parsed_url = urlparse(url)
            if parsed_url.scheme not in ('http', 'https', 'ftp'):
                raise ValueError(f"Unsupported protocol: {parsed_url.scheme}")

            caminho_arquivo = parsed_url.path
            if not caminho_arquivo:
                raise ValueError("Missing file path in URL")

            nome_arquivo, extensao = os.path.splitext(os.path.basename(caminho_arquivo))
            return nome_arquivo, extensao

        except Exception as ex:
            raise ValueError(f"{str(ex)}") from ex 

    def list_files_by_date(self,directory_path):
        try:
            file_paths = [os.path.join(directory_path, file) for file in os.listdir(directory_path)]
            # Create a list of file paths with their creation dates
            file_info = []
            for file_path in file_paths:
                try:
                    # Get the creation time and convert it to a datetime object
                    creation_time = os.path.getctime(file_path)
                    creation_datetime = datetime.fromtimestamp(creation_time)
                    file_info.append((file_path, creation_datetime))
                except Exception as e:
                    print(f"Error getting creation time for {file_path}: {e}")

            file_info.sort(key=lambda x: x[1])
            # Extract only the file paths
            return [file_path for file_path, _ in file_info]
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

class Download:
    def __init__(self, url, path_arquivo):
        self.url = url
        self.path_arquivo = path_arquivo
        self.callback = None # Function to be called for progress updates

    def set_callback(self, callback):
        self.callback = callback

    def executa(self):
        try:
            print('Aguarde...')
            response = requests.get(self.url, stream=True)  # Enable streaming for progress
            response.raise_for_status()  # Verifica se houve algum erro na requisição
            total_size = int(response.headers.get('content-length', 0))  # Get total file size
            with open(self.path_arquivo, 'wb') as file:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=self.path_arquivo) as pbar:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                            pbar.update(len(chunk))
                            if self.callback:
                                self.callback(total_size, pbar.n)  # Call the callback with total size and current progress
            print(f"Download completo. Tamanho: {total_size}, Arquivo salvo em: {self.path_arquivo}")
            return total_size
        except requests.exceptions.MissingSchema:
            print("URL inválida. Certifique-se de fornecer uma URL válida.")
            raise Exception('URL inválida. Certifique-se de fornecer uma URL válida.')
        except requests.exceptions.RequestException as e:
            print(f"Erro na conexão: {e}")
            raise Exception(f"Erro na conexão: {e}")