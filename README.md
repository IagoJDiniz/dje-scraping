<h1 align="center">Web Scraping de publicações do DJE</h1>

<br/>

<p align="center">
<a href="#-sobre">Sobre</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
<a href="#-tecnologias">Tecnologias</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
<a href="#-funcionalidades-principais">Funcionalidades principais</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
<a href="#-implementações-para-melhoria-de-resultados">Implementações para melhoria de resultados</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
<a href="#%EF%B8%8F-instalação-e-execução">Instalação e execução</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
<a href="#-outros-links">Outros links</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
<a href="#-pontos-de-melhoria">Pontos de melhoria</a>

</p>

## ❔ Sobre

O projeto foi idealizado para realizar a busca das publicações do [DJE](https://dje.tjsp.jus.br/cdje/index.do) do "Caderno 3 - Judicial - 1ª Instância - Capital - Parte I" entre as datas de 01/10/24 e 29/11/24 e salvar no banco de dados principal do projeto
<br/>


## 🔧 Tecnologias

Esse projeto foi desenvolvido com as seguintes tecnologias:

- [Python](https://www.python.org/)
- [Selenium](https://selenium-python.readthedocs.io/)
- [Python dotenv](https://pypi.org/project/python-dotenv/)
- [Requests](https://requests.readthedocs.io/en/latest/)

## 🧠 Funcionalidades principais

  - Busca de publicações por intervalo de datas(hardcode no momento para não ferir os requisitos do teste)
  - Envio das publicações para armazenamento via API
    
## 🚀 Implementações para melhoria de resultados

  - Utilização do webdriver do Selenium ao invés do BeautifulSoup para lidar com certificações do DJE e ter mais controle sobre as páginas
  - Caso a publicação não esteja completa(parte dos dados estar no pdf anterior ou posterior) ele navega para a página correta e une as informações
  - Envio dos posts por dia, faz a coleta daquele dia e ao final envia para a API, reduzindo os riscos de corrompimento de dados
  - Fechamento do navegador ao fim da coleta de cada dia para que ao iniciar o scraping do próximo dia a certificação seja renovada
  - Em caso de impedimento do envio para a API salva o JSON que seria enviado nos arquivos do projeto
  

## ⚙️ Instalação e execução
  <p>Garanta que voce tem o Python instalado e coloque o arquivo executável do [webdriver Firefox](https://github.com/mozilla/geckodriver/releases), de acordo com seu sistema operacional, na raiz do projeto</p>

  ```
  git clone https://github.com/IagoJDiniz/dje-scraping.git
  cd dje-scraping

  pip install -r requirements.txt
  ```
  <p>Crie um arquivo .env com as seguintes variáveis:</p>

  ```
API_URL=http://localhost:3333/register-posts
SCRAPER_API_KEY=mesma_key_utilizada_no_backend
```

  
<p>Por fim execute:</p>

```
python src/main.py
```
<strong>O comando "python" pode ser "python3" caso esteja em uma distribuição linux(Mas isso você já deve saber)</strong>
<br/>
  - A busca, extração e salvamento levam em torno de 4h(são mais de 1300 publicações) e estão sendo executadas diariamente via githubActions nesse repositório
  - Caso tenha interesse em ver o navegador rodando basta "comentar" a linha contendo "--headless" no src/scraper/browser.py
<br/>  

  
  
  

## 📄 Outros links

[API](https://github.com/IagoJDiniz/JusCashCase/)
<br/>
[Front-end](https://github.com/IagoJDiniz/juscash-front/)
<br/>


## 📈 Pontos de melhoria
  - Fazer uma tratativa melhor de identificação de erros humanos, como publicações que duplicaram os advogados ou cujo padrão de escrita dos autores foi ferido(vide processo 0029091-39.2024.8.26.0053 em que um dos advogados aparece mais de 08 vezes)
  - Aprimorar as limitações de tempo até a execução de alguma função, infelizmente testei múltiplas alternativas mas o "time.sleep()" foi o único que conseguiu garantir a execução sem falhas no site do governo
  - Documentar as funções do código, alguns comentários foram utilizados e a estrutura de cada arquivo está bem enxuta, porém isso não tem o mesmo valor de uma documentação completa
