# streamlit-desafio-fitness

Este projeto tem como objetivo criar um aplicativo para comparar os resultados obtidos no acompanhamento de um processo de emagrecimento de várias pessoas.

Será criado em [Python]() utilizando o [Streamlit](), pela simplicidade na construção de dashboards, pela facilidade de desenvolvimento e pela simplicidade de implantação. 

## Requisitos Funcionais

1. Os dados de cada participante serão gravados gravados em arquivos ```data_<id>.json```, onde **id** é o identificador de cada participante, no formato **JSON**, e com a seguinte estrutura:
```json
{
  "name": "John Doe",
  "biometrics": [
    {
      "date": "2026-02-01",
      "total_weight": 78.5,
      "muscle_mass_weight": 34.2,
      "fat_mass_weight": 20.1,
      "water_weight": 24.2
    },
  ]
}
```

99. Gerar **log** em console para acompanhamento e em arquivos para análise posterior ou em tempo real por sistemas de observabilidade.

## Implementação

1. Dados

como os dados estão em arquivos JSON separados, vamos usar o ```glob``` utilizando uma máscara ```data_*.json``` para varrer os arquivos de dados de cada participante. Os dados serão armazenados internamente em um ```DataFrame``` para poderem ser facilmente manuipulados para serem consumidos pelos gráficos.

Exemplo do DataFrame:
```code
        date  total_weight  muscle_mass_weight  fat_mass_weight  water_weight      name
0 2026-02-10         112.9               34.54             35.0           0.0    Giba F
1 2026-02-10         112.6               65.70             40.7          48.1      Giba
2 2026-02-10         112.9               34.54             35.0           0.0      Giba
3 2026-02-10         112.6               65.70             40.7          48.1    Giba E
4 2026-02-01          78.5               34.20             20.1          24.2  John Doe
5 2026-02-15          77.8               34.50             19.7          23.6  John Doe
6 2026-02-28          77.2               34.70             19.3          23.2  John Doe
```


99. Log

Vamos utilizar o módulo [logging]() para simular algo semelhante ao [Android LogCat](). Os arquivos serão gerados e quebrados por dia para facilitar a sua manutenção.
Criamos um novo modulo ```log.py``` onde é definido um ```logger``` básico, com as formatação de saída para o console e para um arquivo, e uma rotina para definir o nome e local do arquivo de log.

