from app import db
from app.models import BigBag, Estorno, AuditLog
from app.services import processar_estorno

def test_estorno_valido_e_auditoria(app):
    with app.app_context():
        r=processar_estorno("BB-2026-0001","Rasgado","x","Ana")
        assert r["status"]=="SUCESSO"; assert BigBag.query.filter_by(codigo="BB-2026-0001").first().status=="ESTORNADO"
        log=AuditLog.query.one(); assert '"status": "DISPONIVEL"' in log.dados_anteriores and '"status": "ESTORNADO"' in log.dados_novos

def test_repetido(app):
    with app.app_context():
        processar_estorno("BB-2026-0001","Rasgado","","Ana")
        assert processar_estorno("BB-2026-0001","Rasgado","","Ana")["status"]=="JA_ESTORNADO"

def test_bloqueado_inexistente_e_motivo(app):
    with app.app_context():
        total_inicial = Estorno.query.count()
        assert processar_estorno("BB-2026-0008","Outro","","Ana")["status"]=="BLOQUEADO"
        assert processar_estorno("BB-2026-9999","Outro","","Ana")["status"]=="NAO_ENCONTRADO"
        assert processar_estorno("BB-2026-0002","","","Ana")["status"]=="DADOS_INVALIDOS"
        assert Estorno.query.count() == total_inicial + 3
