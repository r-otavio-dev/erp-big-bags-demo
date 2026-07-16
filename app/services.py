import json
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError
from . import db
from .models import BigBag, Estorno, AuditLog, now

MOTIVOS = ["Material danificado", "Rasgado", "Contaminado", "Peso incorreto",
           "Identificação ilegível", "Problema de qualidade", "Outro"]


def seed_database():
    produtos = ["PEAD Natural", "PP Copolímero", "PEBD Reciclado", "Masterbatch Azul"]
    codigos_existentes = {row.codigo for row in BigBag.query.with_entities(BigBag.codigo).all()}
    for i in range(1, 81):
        codigo = f"BB-2026-{i:04d}"
        if codigo in codigos_existentes:
            continue
        status = "ESTORNADO" if i in (5, 12, 23) else "BLOQUEADO" if i in (8, 17, 29) else "DISPONIVEL"
        bag = BigBag(codigo=codigo, lote=f"LT-{(i-1)//5+1:03d}",
                     produto=produtos[(i-1) % len(produtos)], peso_kg=500 + (i % 4) * 25,
                     data_fabricacao=date(2026, 1, 1) + timedelta(days=i), status=status,
                     localizacao=f"Armazém A / Posição {i:02d}",
                     observacao="Bloqueio de qualidade" if status == "BLOQUEADO" else "")
        db.session.add(bag)
        db.session.flush()
        if status == "ESTORNADO":
            db.session.add(Estorno(big_bag_id=bag.id, codigo_informado=bag.codigo,
                motivo="Problema de qualidade", responsavel="Carga inicial",
                resultado="SUCESSO", mensagem="Estorno registrado na carga de demonstração."))
    db.session.commit()


def processar_estorno(codigo, motivo, observacao, responsavel):
    codigo = (codigo or "").strip().upper()
    motivo, observacao, responsavel = (motivo or "").strip(), (observacao or "").strip(), (responsavel or "").strip()
    bag = BigBag.query.filter_by(codigo=codigo).first()
    if not motivo or motivo not in MOTIVOS:
        return _erro(bag, codigo, motivo, observacao, responsavel, "DADOS_INVALIDOS", "Motivo obrigatório ou inválido.")
    if not responsavel:
        return _erro(bag, codigo, motivo, observacao, responsavel, "DADOS_INVALIDOS", "Responsável obrigatório.")
    if not bag:
        return _erro(None, codigo, motivo, observacao, responsavel, "NAO_ENCONTRADO", "Big bag não encontrado.")
    if bag.status == "ESTORNADO":
        return _erro(bag, codigo, motivo, observacao, responsavel, "JA_ESTORNADO", "Big bag já estornado.")
    if bag.status == "BLOQUEADO":
        return _erro(bag, codigo, motivo, observacao, responsavel, "BLOQUEADO", "Big bag bloqueado; estorno não permitido.")
    try:
        anterior = bag.as_dict()
        updated = BigBag.query.filter_by(id=bag.id, status="DISPONIVEL").update(
            {"status": "ESTORNADO", "ultimo_movimento_em": now()}, synchronize_session=False)
        if updated != 1:
            db.session.rollback()
            return _erro(bag, codigo, motivo, observacao, responsavel, "JA_ESTORNADO", "Big bag não está mais disponível.")
        db.session.flush()
        db.session.expire_all()
        bag = db.session.get(BigBag, bag.id)
        estorno = Estorno(big_bag_id=bag.id, codigo_informado=codigo, motivo=motivo,
                          observacao=observacao, responsavel=responsavel, resultado="SUCESSO",
                          mensagem="Estorno realizado com sucesso.")
        db.session.add(estorno)
        db.session.add(AuditLog(acao="ESTORNO", entidade="big_bag", entidade_id=bag.id,
            dados_anteriores=json.dumps(anterior, ensure_ascii=False),
            dados_novos=json.dumps(bag.as_dict(), ensure_ascii=False), usuario=responsavel))
        db.session.commit()
        return {"status": "SUCESSO", "mensagem": "Estorno realizado com sucesso.", "big_bag": bag}
    except (IntegrityError, Exception):
        db.session.rollback()
        raise


def _erro(bag, codigo, motivo, observacao, responsavel, resultado, mensagem):
    db.session.add(Estorno(big_bag_id=bag.id if bag else None, codigo_informado=codigo,
        motivo=motivo, observacao=observacao, responsavel=responsavel,
        resultado=resultado, mensagem=mensagem))
    db.session.commit()
    return {"status": resultado, "mensagem": mensagem, "big_bag": bag}
