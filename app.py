from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
app.secret_key = "ana_portfolio_secret"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs("data", exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

JSON_FILE = "data/conteudo.json"

ADMIN_EMAIL = "admin@portfolioana.com"
ADMIN_PASSWORD = "Ana@2026Portfolio"


def carregar_dados():
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "nome": "Ana Carolina Gonçalves Lopes",
            "cargo": "Estagiária de Marketing",
            "sobre": "",
            "instagram": "",
            "linkedin": "",
            "whatsapp": "",
            "foto": "",
            "projetos": []
        }


def salvar_dados(dados):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


@app.route("/")
def index():
    return render_template("index.html", dados=carregar_dados())


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        senha = request.form["senha"]

        if email == ADMIN_EMAIL and senha == ADMIN_PASSWORD:
            session["logado"] = True
            return redirect(url_for("admin"))

        flash("Login inválido")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/admin")
def admin():

    if not session.get("logado"):
        return redirect(url_for("login"))

    return render_template("admin.html", dados=carregar_dados())


@app.route("/salvar", methods=["POST"])
def salvar():

    if not session.get("logado"):
        return redirect(url_for("login"))

    dados = carregar_dados()

    dados["nome"] = request.form["nome"]
    dados["cargo"] = request.form["cargo"]
    dados["sobre"] = request.form["sobre"]
    dados["instagram"] = request.form["instagram"]
    dados["linkedin"] = request.form["linkedin"]
    dados["whatsapp"] = request.form["whatsapp"]
    dados["email"] = request.form["email"]

    salvar_dados(dados)

    return redirect(url_for("admin"))


@app.route("/upload_perfil", methods=["POST"])
def upload_perfil():

    if not session.get("logado"):
        return redirect(url_for("login"))

    file = request.files["foto"]

    if file:

        name = secure_filename(file.filename)

        path = os.path.join(app.config["UPLOAD_FOLDER"], name)

        file.save(path)

        dados = carregar_dados()
        dados["foto"] = "uploads/" + name
        salvar_dados(dados)

    return redirect(url_for("admin"))


@app.route("/novo_projeto", methods=["POST"])
def novo_projeto():

    if not session.get("logado"):
        return redirect(url_for("login"))

    titulo = request.form["titulo"]
    descricao = request.form["descricao"]

    arquivos = request.files.getlist("imagens")

    if len(arquivos) > 7:
        return "Máximo de 7 imagens por projeto"

    imagens = []

    for file in arquivos:
        if file:

            name = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], "projetos_" + name)

            file.save(path)

            imagens.append("uploads/projetos_" + name)

    dados = carregar_dados()

    dados["projetos"].append({
        "id": len(dados["projetos"]) + 1,
        "titulo": titulo,
        "descricao": descricao,
        "imagens": imagens
    })

    salvar_dados(dados)

    return redirect(url_for("admin"))


@app.route("/projeto/<int:id>")
def projeto(id):

    dados = carregar_dados()

    projeto = next((p for p in dados["projetos"] if p["id"] == id), None)

    if not projeto:
        return "Projeto não encontrado"

    return render_template("projeto.html", projeto=projeto)


if __name__ == "__main__":
    app.run(debug=True)