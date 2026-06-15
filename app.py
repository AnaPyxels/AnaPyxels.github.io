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


# =========================================================
# DADOS
# =========================================================
def carregar_dados():
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "nome": "Ana Carolina Gonçalves Lopes",
            "cargo": "Estagiária de Marketing",
            "sobre": "",
            "email": "",
            "linkedin": "",
            "whatsapp": "",
            "foto": "",
            "formacao": [],
            "experiencias": [],
            "projetos": []
        }


def salvar_dados(dados):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


# =========================================================
# LOGIN / LOGOUT
# =========================================================
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
    return redirect(url_for("login"))


# =========================================================
# DASHBOARD
# =========================================================
@app.route("/admin")
def admin():
    if not session.get("logado"):
        return redirect(url_for("login"))

    return render_template("admin.html", dados=carregar_dados())


# =========================================================
# PERFIL
# =========================================================
@app.route("/admin/perfil")
def admin_perfil():
    if not session.get("logado"):
        return redirect(url_for("login"))

    return render_template("admin/perfil.html", dados=carregar_dados())


@app.route("/salvar_perfil", methods=["POST"])
def salvar_perfil():
    if not session.get("logado"):
        return redirect(url_for("login"))

    dados = carregar_dados()

    dados["nome"] = request.form["nome"]
    dados["cargo"] = request.form["cargo"]
    dados["sobre"] = request.form["sobre"]
    dados["email"] = request.form["email"]

    salvar_dados(dados)
    return redirect(url_for("admin_perfil"))


# =========================================================
# FORMAÇÃO
# =========================================================
@app.route("/admin/formacao")
def admin_formacao():
    if not session.get("logado"):
        return redirect(url_for("login"))

    return render_template("admin/formacao.html", dados=carregar_dados())


@app.route("/add_formacao", methods=["POST"])
def add_formacao():
    if not session.get("logado"):
        return redirect(url_for("login"))

    dados = carregar_dados()

    dados["formacao"].append({
        "curso": request.form["curso"],
        "instituicao": request.form["instituicao"],
        "situacao": request.form.get("situacao", "")
    })

    salvar_dados(dados)
    return redirect(url_for("admin_formacao"))


# =========================================================
# EXPERIÊNCIA / TRABALHOS
# =========================================================
@app.route("/admin/trabalhos")
def admin_trabalhos():
    if not session.get("logado"):
        return redirect(url_for("login"))

    return render_template("admin/trabalhos.html", dados=carregar_dados())


@app.route("/add_experiencia", methods=["POST"])
def add_experiencia():
    if not session.get("logado"):
        return redirect(url_for("login"))

    dados = carregar_dados()

    dados["experiencias"].append({
        "cargo": request.form["cargo"],
        "empresa": request.form["empresa"],
        "descricao": request.form["descricao"]
    })

    salvar_dados(dados)
    return redirect(url_for("admin_trabalhos"))


# =========================================================
# PORTFÓLIO + CRUD
# =========================================================
@app.route("/admin/portfolio")
def admin_portfolio():
    if not session.get("logado"):
        return redirect(url_for("login"))

    return render_template("admin/portfolio.html", dados=carregar_dados())


@app.route("/novo_projeto", methods=["POST"])
def novo_projeto():
    if not session.get("logado"):
        return redirect(url_for("login"))

    dados = carregar_dados()

    titulo = request.form["titulo"]
    descricao = request.form["descricao"]

    arquivos = request.files.getlist("imagens")
    imagens = []

    for file in arquivos:
        if file and file.filename != "":
            name = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], "proj_" + name)
            file.save(path)
            imagens.append("uploads/proj_" + name)

    novo_id = max([p["id"] for p in dados["projetos"]] + [0]) + 1

    dados["projetos"].append({
        "id": novo_id,
        "titulo": titulo,
        "descricao": descricao,
        "imagens": imagens
    })

    salvar_dados(dados)
    return redirect(url_for("admin_portfolio"))


# =========================
# EDITAR PROJETO
# =========================
def buscar_projeto(dados, id):
    return next((p for p in dados["projetos"] if p["id"] == id), None)


@app.route("/editar_projeto/<int:id>", methods=["POST"])
def editar_projeto(id):
    if not session.get("logado"):
        return redirect(url_for("login"))

    dados = carregar_dados()
    projeto = buscar_projeto(dados, id)

    if not projeto:
        return "Projeto não encontrado"

    projeto["titulo"] = request.form["titulo"]
    projeto["descricao"] = request.form["descricao"]

    salvar_dados(dados)
    return redirect(url_for("admin_portfolio"))


@app.route("/deletar_projeto/<int:id>")
def deletar_projeto(id):
    if not session.get("logado"):
        return redirect(url_for("login"))

    dados = carregar_dados()

    dados["projetos"] = [
        p for p in dados["projetos"] if p["id"] != id
    ]

    salvar_dados(dados)
    return redirect(url_for("admin_portfolio"))


# =========================================================
# CONTATO
# =========================================================
@app.route("/admin/contato")
def admin_contato():
    if not session.get("logado"):
        return redirect(url_for("login"))

    return render_template("admin/contato.html", dados=carregar_dados())


@app.route("/salvar_contato", methods=["POST"])
def salvar_contato():
    if not session.get("logado"):
        return redirect(url_for("login"))

    dados = carregar_dados()

    dados["email"] = request.form["email"]
    dados["instagram"] = request.form["instagram"]
    dados["linkedin"] = request.form["linkedin"]
    dados["whatsapp"] = request.form["whatsapp"]

    salvar_dados(dados)
    return redirect(url_for("admin_contato"))


# =========================================================
# CONFIG
# =========================================================
@app.route("/admin/config")
def admin_config():
    if not session.get("logado"):
        return redirect(url_for("login"))

    return render_template("admin/config.html", dados=carregar_dados())


# =========================================================
# FRONT
# =========================================================
@app.route("/")
def index():
    return render_template("index.html", dados=carregar_dados())


@app.route("/projeto/<int:id>")
def projeto(id):
    dados = carregar_dados()
    projeto = next((p for p in dados["projetos"] if p["id"] == id), None)

    if not projeto:
        return "Projeto não encontrado"

    return render_template("projeto.html", projeto=projeto)


# =========================================================
if __name__ == "__main__":
    app.run(debug=True)