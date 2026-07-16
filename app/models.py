from datetime import datetime, timezone
from . import db


def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class BigBag(db.Model):
    __tablename__ = "big_bags"
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False, index=True)
    lote = db.Column(db.String(30), nullable=False)
    produto = db.Column(db.String(100), nullable=False)
    peso_kg = db.Column(db.Float, nullable=False)
    data_fabricacao = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, index=True)
    localizacao = db.Column(db.String(80), nullable=False)
    observacao = db.Column(db.Text, default="")
    ultimo_movimento_em = db.Column(db.DateTime, nullable=False, default=now)

    def as_dict(self):
        return {"id": self.id, "codigo": self.codigo, "lote": self.lote,
                "produto": self.produto, "peso_kg": self.peso_kg,
                "data_fabricacao": self.data_fabricacao.isoformat(), "status": self.status,
                "localizacao": self.localizacao, "observacao": self.observacao,
                "ultimo_movimento_em": self.ultimo_movimento_em.isoformat()}


class Estorno(db.Model):
    __tablename__ = "estornos"
    id = db.Column(db.Integer, primary_key=True)
    big_bag_id = db.Column(db.Integer, db.ForeignKey("big_bags.id"), nullable=True)
    codigo_informado = db.Column(db.String(30), nullable=False, index=True)
    motivo = db.Column(db.String(100), default="")
    observacao = db.Column(db.Text, default="")
    responsavel = db.Column(db.String(100), default="")
    resultado = db.Column(db.String(30), nullable=False, index=True)
    mensagem = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, nullable=False, default=now, index=True)
    big_bag = db.relationship("BigBag")


class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    acao = db.Column(db.String(50), nullable=False)
    entidade = db.Column(db.String(50), nullable=False)
    entidade_id = db.Column(db.Integer)
    dados_anteriores = db.Column(db.Text)
    dados_novos = db.Column(db.Text)
    usuario = db.Column(db.String(100), nullable=False)
    criado_em = db.Column(db.DateTime, nullable=False, default=now)

