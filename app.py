################################
# Bibliotecas
################################
import flask

################################
# Carregamento de Modelo
################################


################################
# Configurações
################################
app = flask.Flask(__name__, template_folder="templates", static_folder="static")


################################
# Rotas
################################
@app.route("/")
def index():
    return flask.render_template("index.html")


################################
# Execução
################################
if __name__ == "__main__":
    app.run(debug=True)
