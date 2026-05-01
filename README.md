# KD-Meu-Buteco

Uma aplicação para encontrar os melhores butecos de Belo Horizonte - MG perto de sua localização.

Basta inserir o endereço e a distância de procura e todos os resultados são retornados

Pode-se procurar em uma região retângular, passando o tamanho da semi-diagonal, ou em uma
região círcular, passando o tamanho do raio. Ambos são dados em quilômetros

## Como funciona?
Nossa busca é baeada em uma Kd-Tree que divide a região metropolitana em sub-regiões usando as
localizações dos bares. Ao procurar em uma região, pode-se retirar regiões que não intersectam
a região de interesse, ao mesmo tempo que inclue as regiões totalmente inclusas. A busca numa
região retângular segue a lógica da busca em intervalo, enquanto a busca em círculo adapta essa lógica para uma comparação da distância euclidiana

## O que foi usado?
- **Python**: A linguagem na qual o projeto e a KD-tree foram feitos
- **dash-leaflet**: A biblioteca que gera o frontend da aplicação
- **geopy**: A biblioteca que converte endereços em localizações 

## Como executar?
Após clonar o repositório, baixe as dependencias com `pip install -r requirements.txt` e execute o arquivo `main.py` em `src/`

*É recomendável fazer isso em um ambiente python isolado, como `venv`*

## Quem somos?

- Caio César Moraes Costa
- Leonardo Barreto Gaião

#### Esse projeto é a entrega de nosso trabalho de Algoritimos II. Leia o relatório para mais detalhes