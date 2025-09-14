# Projeto de Classificação - Previsão de Diabetes

Este projeto implementa um modelo de machine learning para prever diabetes em pacientes com base em características médicas. A aplicação é construída com Flask e fornece uma API RESTful para fazer previsões.

## 📋 Descrição do Projeto

O sistema utiliza um modelo de classificação treinado no dataset Pima Indians Diabetes para prever se um paciente tem diabetes baseado em características como:

* Gender
* Age
* Hypertension
* Heart disease
* Smoking history
* BMI
* HbA1c level
* Blood glucose level
* Diabetes

## Como Executar

1. Clone o repositório:
   ```
   git clone https://github.com/Prog-LucasAlves/ML_Cla_Flask.git
   cd ML_Cla_Flask
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Execute a aplicação Flask:
   ```
   streamlit run app.py
   ```

4. Acesse a API em `http://localhost:5000`.

## 📝 Licença

Este projeto é para fins educacionais. O dataset é de domínio público.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.
