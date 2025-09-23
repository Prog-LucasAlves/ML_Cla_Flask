# 🏥 Sistema de Predição de Diabetes com Flask

Um sistema de machine learning(Modelo de Classificação) para predição de diabetes baseado em indicadores clínicos, desenvolvido com Flask e XGBoost.

![Python](https://img.shields.io/badge/Python-3.12.4-blue)
![Flask](https://img.shields.io/badge/Flask->=3.1.2-green)
![XGBoost](https://img.shields.io/badge/XGBoost->=3.0.5-orange)
![MIT](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
* Instalação e Uso
* Estrutura do Projeto
* Dataset
* API Endpoints
* Contribuição
* Licença
* Contato

## 🌟 Visão Geral

Este projeto é uma aplicação web que utiliza machine learning para prever o risco de diabetes com base em 8 indicadores clínicos. O sistema foi desenvolvido para demonstrar a aplicação prática de ciência de dados na área da saúde.

> [!IMPORTANT]
> ⚠️ Aviso Importante: Este projeto é para fins educacionais e de demonstração. Não deve ser usado para diagnósticos médicos reais.

## 🚀 Funcionalidades

* ✅ Interface web responsiva e intuitiva
* ✅ Formulário interativo com validação de dados
* ✅ Predição em tempo real usando modelo XGBoost
* ✅ Exibição de probabilidades e resultados claros
* ✅ Sistema robusto de tratamento de erros

## 🛠 Tecnologias Utilizadas

### Backend

1. Python - Linguagem princiapal
2. Flask - Franework Web
3. XGBoost - Algoritmo de Machine Learning
4. Pandas - Manipulação de Dados
5. Scikit-learn - Pré-processamento e Validação
6. joblib - Serialização do modelo

### Frontend

1. HTML5 - Estrutura da página
2. CSS - Estilização

### Ferramentas de Desenvolvimento

1. Git - Controle de versão
2. uv - Ambiente Virtual e Gerenciamento de Pacotes Python

## 📥 Instalação e Uso

- Pré-requisitos

1. Python 3.12.4 ou superior
2. [uv](https://docs.astral.sh/uv/guides/install-python/) ou pip

- Passo a passo para instalação

1. Clone o Repositório

```bash
git clone https://github.com/Prog-LucasAlves/ML_Cla_Flask.git
cd diabetes-prediction-flask
```

2. Inicializando o Projeto

```bash
uv init
```

3. Versão do Python

```bash
uv python install 3.12.4
```

4. Crie um Ambiente Virtual

```bash
uv venv
```

5. Ativando Ambiente Virtual

```bash
.venv/scripts/activate
```

6. Instale as dependências

```bash
uv add -r requirements.txt
```

7. Pre-commit

```bash
uv add --group dev pre-commit
pre-commit install
pre-commit autoupdate
```

8. Execute a aplicação

```bash
python app.py
```

## 📁 Estrutura do Projeto

```
DIR
|
|-- data                                   # Pasta de dados
      |-- diabetes_prediction_dataset.csv  # Dataset
|-- model                                  # Pasta de Modelos e Artefatos de ML
      |-- diabetes_model.pkl               # Modelo Treinado (XGBoost)
      |-- feature_names.pkl                # Nomes das Features Usadas no Modelo
      |-- gender_encoder.pkl               # Encoder para Variável 'gender'
      |-- patient.ipynb                    # Jupyter Notebook com dados **FAKE** para serem preditos
      |-- model.ipynb                      # Jupyter Notebook com Análise de Treinamento
      |-- pca.pkl                          # Objeto PCA para Redução de Dimensionalidade
      |-- scater.pkl                       # Scaler para Normalização dos Dados
      |-- smoking_encoder.pkl              # Encoder para Variável 'smoking_history'
|-- static                                 # Arquivos CSS
      |-- styles.css                       # Estilos CSS da aplicação
|-- templates                              # Templates HTML
      |-- index.html                       # Página Principal da Aplicação
|-- .gitignore                             # Arquivo para Ignorar Arquivos no Git
|-- .pre-commit-config.yaml                # Configuração do pre-commit para Qualidade de Código
|-- .python-version                        # Versão do Python Usada no Projeto
|-- app.py                                 # Aplicação Flask
|-- LICENSE                                # Licença do Projeto
|-- pyproject.toml                         # Configuração do Projeto
|-- README.md                              # Documentação do Projeto
|-- requirements.txt                       # Dependências do Projeto
|
```

📊 data/

- **diabetes_prediction_dataset.csv**: Dataset contendo os dados de pacientes com variáveis clínicas usadas para prever diabetes. Inclui features como idade, gênero, IMC, histórico de tabagismo, etc.

🤖 model/

- diabetes_model.pkl: Modelo de machine learning treinado (XGBoost) serializado para fazer previsões.
- feature_names.pkl: Lista com os nomes das features na ordem correta para alimentar o modelo.
- gender_encoder.pkl: LabelEncoder para transformar valores categóricos da variável 'gender'.
- model.ipynb: Notebook Jupyter contendo toda a análise exploratória, pré-processamento, treinamento e avaliação do modelo.
- pca.pkl: Objeto PCA (Principal Component Analysis) para redução de dimensionalidade.
- scaler.pkl: Objeto StandardScaler para normalização das features numéricas.
- smoking_encoder.pkl: Encoder LabelEncoder para a variável categórica 'smoking_history'.

🎨 static/

- styles.css: Arquivo de estilos CSS que define o design responsivo da aplicação web, incluindo layout, cores, animações e responsividade.

📄 templates/

- index.html: Template HTML principal que renderiza o formulário de entrada de dados e exibe os resultados das previsões.

⚙️ Arquivos de Configuração

- .gitignore: Especifica quais arquivos e diretórios devem ser ignorados pelo Git (ex: pycache/, .env, etc.).
- .pre-commit-config.yaml: Configura hooks para verificação de qualidade de código antes dos commits.
- .python-version: Especifica a versão do Python compatível com o projeto (geralmente usado com pyenv).

🐍 Arquivos Principais Python

- app.py: Aplicação Flask que serve a interface web, processa requisições e faz previsões usando o modelo treinado.

📜 Documentação e Licença

- LICENSE: Arquivo de licença do projeto (MIT, Apache, GPL, etc.).
- pyproject.toml: Arquivo de configuração para gerenciamento de dependências com uv.
- README.md: Documentação completa do projeto com instruções de instalação, uso e detalhes técnicos.
- requirements.txt: Lista de dependências Python necessárias para executar o projeto.

## 📊 Dataset

### **Variáveis Utilizadas**
- O modelo utiliza 8 features para a **predição**:

1. Gênero (gender) - Categórica
2. Idade (age) - Numérica
3. Hipertensão (hypertension) - Binária
4. Doença Cardíaca (heart_disease) - Binária
5. Histórico de Tabagismo (smoking_history) - Categórica
6. IMC (bmi) - Numérica
7. Nível de HbA1c(Hemoglobina Glicada) (HbA1c_level) - Numérica
8. Nível de Glicose (blood_glucose_level) - Numérica

### **Variável Alvo**

1. Diabetes (diabetes) - Binária (0 = Não, 1 = Sim)

### **Exemplo de Dados**

```python
{
    "gender": "Female",
    "age": 80.0,
    "hypertension": 0,
    "heart_disease": 1,
    "smoking_history": "never",
    "bmi": 25.19,
    "hba1c_level": 6.6,
    "blood_glucose_level": 140
}
```

## 🌐 API Endpoints

### **GET/**

- Retorna a página principal com o formulário de predição.

### **POST/**

- Processa os dados do formulário e retorna a predição.

#### **Exemplo de Request**

```json
{
    "gender": "Female",
    "age": 45,
    "hypertension": 0,
    "heart_disease": 0,
    "smoking_history": "never",
    "bmi": 25.0,
    "hba1c_level": 5.5,
    "blood_glucose_level": 120
}
```

#### **Exemplo de Response**

```json
{
    "prediction": 0,
    "probability": 0.15,
    "status": "success"
}
```

## 🤝 Contribuição

- Contribuições são ben-vindas!

## 📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](https://github.com/Prog-LucasAlves/ML_Cla_Flask/blob/main/LICENSE) para detalhes.

- ⭐ Se este projeto foi útil, deixe uma estrela no GitHub! -
