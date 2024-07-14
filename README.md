# My GUI Images

Aplicação GUI para manipular imagens.

Instale as dependências:

```bash
pip install requests
pip install tqdm
pip install pillow
```

Execute o arquivo principal

```bash
python3 main.py
```

[Detalhes do programa](https://github.com/armandossrecife/my_gui_images/blob/main/detalhes.md)

## Telas da Aplicação

Tela Principal

![Tela Principal](https://github.com/armandossrecife/my_gui_images/blob/main/docs/T1-Download-Imagem.png "Faz download de imagem")

Tela Mostra Imagem

![Tela Mostra Imagem](https://github.com/armandossrecife/my_gui_images/blob/main/docs/T2-Mostra-Imagem.png "Mostra Imagem")

Tela Menu de Imagens 

![Tela Mostra Botões de Imagens](https://github.com/armandossrecife/my_gui_images/blob/main/docs/T3-Menu-Mostra-Imagens.png "Botões de Imagens")

Tela Mostra Imagem Selecionada

![Tela Mostra Imagem Selecionada](https://github.com/armandossrecife/my_gui_images/blob/main/docs/T4-Tela-Imagem-Selecionada.png "Imagem Selecionada")

# Incompatibilidade da biblioteca Pillow

Caso aconteça o erro: ANTIALIAS

The error message indicates that your code is trying to use the ANTIALIAS attribute of the PIL.Image module, but this attribute has been deprecated in Pillow versions 10.0.0 and above. 

Use Alternative Resampling Filter (Recommended)

The recommended approach is to use the replacement for ANTIALIAS, which is PIL.Image.Resampling.LANCZOS. This provides a similar high-quality downsampling filter:

Faça a alteração na classe ViewAllImagesWindow

```python
    def display_thumbnails(self):
        for i, image_path in enumerate(self.image_paths):
            # Create a thumbnail using PIL
            #thumbnail = PIL.Image.open(image_path).resize((100, 100), PIL.Image.ANTIALIAS)
            thumbnail = PIL.Image.open(image_path).resize(
                (100, 100), PIL.Image.Resampling.LANCZOS)
```



