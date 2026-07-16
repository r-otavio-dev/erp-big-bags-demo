from io import BytesIO
from datetime import datetime
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from app.models import BigBag, Estorno
from app.services import MOTIVOS, processar_estorno

bp = Blueprint("main", __name__)


@bp.before_app_request
def protect():
    if request.endpoint and request.endpoint.startswith("main.") and request.endpoint not in ("main.login", "main.static") and not session.get("usuario"):
        return redirect(url_for("main.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("usuario") == "admin" and request.form.get("senha") == "admin123":
            session["usuario"] = "admin"
            return redirect(url_for("main.dashboard"))
        flash("Usuário ou senha inválidos.", "danger")
    return render_template("login.html")


@bp.get("/logout")
def logout():
    session.clear(); return redirect(url_for("main.login"))


@bp.get("/")
def dashboard():
    counts = {s: BigBag.query.filter_by(status=s).count() for s in ("DISPONIVEL", "ESTORNADO", "BLOQUEADO")}
    return render_template("dashboard.html", counts=counts, total=BigBag.query.count(), ultimos=Estorno.query.order_by(Estorno.criado_em.desc()).limit(8).all())


@bp.get("/big-bags")
def consulta():
    codigo = request.args.get("codigo", "").strip().upper()
    bag = BigBag.query.filter_by(codigo=codigo).first() if codigo else None
    return render_template("consulta.html", bag=bag, codigo=codigo)


@bp.route("/estornos/novo", methods=["GET", "POST"])
def novo_estorno():
    bag = None; result = None
    codigo = (request.values.get("codigo") or "").strip().upper()
    if codigo: bag = BigBag.query.filter_by(codigo=codigo).first()
    if request.method == "POST" and request.form.get("acao") == "confirmar":
        result = processar_estorno(codigo, request.form.get("motivo"), request.form.get("observacao"), request.form.get("responsavel"))
        bag = result.get("big_bag")
    return render_template("estorno.html", motivos=MOTIVOS, bag=bag, codigo=codigo, result=result)


@bp.get("/api/big-bags/<codigo>")
def api_bag(codigo):
    bag = BigBag.query.filter_by(codigo=codigo.strip().upper()).first()
    return (jsonify(bag.as_dict()), 200) if bag else (jsonify({"erro": "Big bag não encontrado."}), 404)


def _historico_query():
    q = Estorno.query
    if request.args.get("codigo"): q = q.filter(Estorno.codigo_informado.contains(request.args["codigo"].strip().upper()))
    if request.args.get("resultado"): q = q.filter_by(resultado=request.args["resultado"])
    if request.args.get("responsavel"): q = q.filter(Estorno.responsavel.contains(request.args["responsavel"]))
    if request.args.get("inicio"): q = q.filter(Estorno.criado_em >= datetime.fromisoformat(request.args["inicio"]))
    if request.args.get("fim"): q = q.filter(Estorno.criado_em < datetime.fromisoformat(request.args["fim"]).replace(hour=23, minute=59, second=59))
    return q.order_by(Estorno.criado_em.desc())


@bp.get("/historico")
def historico(): return render_template("historico.html", itens=_historico_query().all())


@bp.get("/historico/exportar")
def exportar_historico():
    rows = [{"codigo": e.codigo_informado, "lote": e.big_bag.lote if e.big_bag else "", "produto": e.big_bag.produto if e.big_bag else "", "motivo": e.motivo, "observacao": e.observacao, "responsavel": e.responsavel, "data_hora": e.criado_em, "resultado": e.resultado, "mensagem": e.mensagem} for e in _historico_query().all()]
    out = BytesIO(); pd.DataFrame(rows).to_excel(out, index=False); out.seek(0)
    return send_file(out, as_attachment=True, download_name="historico_estornos.xlsx")


@bp.route("/importacao", methods=["GET", "POST"])
def importacao():
    preview = session.get("import_preview")
    if request.method == "POST" and request.form.get("acao") == "preview":
        f = request.files.get("arquivo")
        if not f or not f.filename.lower().endswith(".xlsx"):
            flash("Selecione um arquivo .xlsx.", "danger")
        else:
            df = pd.read_excel(f).fillna(""); required = {"codigo", "motivo", "observacao", "responsavel"}
            if not required.issubset(df.columns): flash("Colunas obrigatórias: codigo, motivo, observacao, responsavel.", "danger")
            else: session["import_preview"] = df[list(required)].to_dict("records"); preview = session["import_preview"]
    if request.method == "POST" and request.form.get("acao") == "processar" and preview:
        results = []
        for row in preview:
            r = processar_estorno(row["codigo"], row["motivo"], row["observacao"], row["responsavel"])
            results.append({**row, "status_processamento": r["status"], "mensagem": r["mensagem"]})
        session.pop("import_preview", None); session["import_results"] = results
        return render_template("importacao.html", results=results)
    return render_template("importacao.html", preview=preview)


@bp.get("/importacao/relatorio")
def relatorio_importacao():
    out = BytesIO(); pd.DataFrame(session.get("import_results", [])).to_excel(out, index=False); out.seek(0)
    return send_file(out, as_attachment=True, download_name="resultado_importacao.xlsx")

