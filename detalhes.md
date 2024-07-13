# Classes do programa

![Diagrama de Classes](https://github.com/armandossrecife/my_gui_images/blob/main/docs/my_downloads_images.jpg "Diagrama de Classes")

## Módulo entidades

**Classe Util**:
- extrair_nome_extensao_url: Extrai o nome do arquivo e sua extensão a partir de uma URL, tratando erros como protocolos não suportados e caminhos de arquivo ausentes.
- list_files_by_date: Lista arquivos em um diretório ordenados por data de criação, tratando exceções.

**Classe Download**:
- Baixa uma imagem de uma URL com barra de progresso e tratamento de erros.
- Suporta a configuração de uma função de retorno para atualizações de progresso.

## Módulo gui

**MenuWindow (Janela de Menu)**:
- Oferece um menu principal com botões para carregar imagens, visualizar a imagem mais recente e visualizar todas as imagens.
- Carrega imagens baixadas anteriormente e armazena seus caminhos.

**EntradaWindow (Janela de Entrada)**:
- Permite aos usuários inserir uma URL e baixar a imagem.
- Trata validações e mensagens de erro.

**WindowImageViewer (Janela de Visualização)**:
- Exibe uma imagem selecionada usando PIL e canvas Tkinter com barras de rolagem vertical e horizontal.
- Trata possíveis erros caso o arquivo de imagem não seja encontrado.

**ViewAllImagesWindow (Janela de Visualização de Todas as Imagens)**:
- Lista todas as imagens baixadas como miniaturas usando PIL e botões Tkinter.
- Permite abrir imagens individuais em janelas separadas.
