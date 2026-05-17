from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta
from html import escape
from typing import Literal

from django.http import HttpResponse
from django.utils import timezone

from app.models import Pedido


# ─── Tipos ────────────────────────────────────────────────────────────────────

Periodo = Literal["dia", "semana", "mes"]


@dataclass
class PedidoRelatorio:
    id: str
    hora: str
    responsavel: str
    status: str
    descricao: str
    itens: list[dict[str, str | int]]
    total_itens: int


@dataclass
class LojaRelatorio:
    nome: str
    pedidos: list[PedidoRelatorio]
    total_itens: int


STATUS_LABELS = {
    Pedido.Status.PENDENTE:  "Pendente",
    Pedido.Status.ENTREGUE:  "Entregue",
    Pedido.Status.CANCELADO: "Cancelado",
}

PERIODO_LABELS: dict[Periodo, str] = {
    "dia":    "Diário",
    "semana": "Semanal",
    "mes":    "Mensal",
}


# ─── Helpers internos ─────────────────────────────────────────────────────────

def _responsavel_nome(pedido: Pedido) -> str:
    if not pedido.responsavel:
        return "Sem responsável"
    return (
        pedido.responsavel.get_full_name()
        or pedido.responsavel.first_name
        or pedido.responsavel.username
        or pedido.responsavel.email
    )


def _intervalo(periodo: Periodo, agora_local):
    """Retorna (inicio, fim) no horário local para o período escolhido."""
    inicio_dia = agora_local.replace(hour=0, minute=0, second=0, microsecond=0)
    fim_dia    = agora_local.replace(hour=23, minute=59, second=59, microsecond=999999)

    if periodo == "dia":
        return inicio_dia, fim_dia

    if periodo == "semana":
        # Segunda-feira da semana atual → domingo
        segunda = inicio_dia - timedelta(days=agora_local.weekday())
        domingo = segunda + timedelta(days=6)
        return segunda, domingo.replace(hour=23, minute=59, second=59, microsecond=999999)

    # mes
    primeiro = inicio_dia.replace(day=1)
    # último dia do mês: primeiro dia do próximo mês - 1 segundo
    if agora_local.month == 12:
        proximo_mes = primeiro.replace(year=agora_local.year + 1, month=1)
    else:
        proximo_mes = primeiro.replace(month=agora_local.month + 1)
    ultimo = proximo_mes - timedelta(seconds=1)
    return primeiro, ultimo


def _label_periodo(periodo: Periodo, inicio, fim) -> str:
    """Texto legível do intervalo para exibir no relatório."""
    fmt = "%d/%m/%Y"
    if periodo == "dia":
        return inicio.strftime(fmt)
    return f"{inicio.strftime(fmt)} a {fim.strftime(fmt)}"


def _buscar_pedidos(periodo: Periodo):
    agora_local = timezone.localtime(timezone.now())
    inicio, fim = _intervalo(periodo, agora_local)

    pedidos = (
        Pedido.objects.filter(data_pedido__range=(inicio, fim))
        .select_related("responsavel", "loja")
        .prefetch_related("itens__produto")
        .order_by("loja__nome_loja", "responsavel__first_name", "-data_pedido")
    )
    return agora_local, inicio, fim, list(pedidos)


def _montar_lojas(pedidos: list[Pedido]) -> list[LojaRelatorio]:
    agrupadas: dict[str, list[PedidoRelatorio]] = defaultdict(list)

    for pedido in pedidos:
        itens = [
            {"produto": item.produto.nome_produto, "quantidade": item.quantidade}
            for item in pedido.itens.all()
        ]
        total_itens = sum(int(item["quantidade"]) for item in itens)
        loja_nome   = pedido.loja.nome_loja if pedido.loja else "Sem loja"

        agrupadas[loja_nome].append(
            PedidoRelatorio(
                id=str(pedido.public_id)[:8],
                hora=timezone.localtime(pedido.data_pedido).strftime("%d/%m %H:%M"),
                responsavel=_responsavel_nome(pedido),
                status=STATUS_LABELS.get(pedido.status, pedido.status),
                descricao=pedido.descricao or "",
                itens=itens,
                total_itens=total_itens,
            )
        )

    return [
        LojaRelatorio(
            nome=nome,
            pedidos=pedidos_loja,
            total_itens=sum(p.total_itens for p in pedidos_loja),
        )
        for nome, pedidos_loja in agrupadas.items()
    ]


# ─── CSS ──────────────────────────────────────────────────────────────────────

def _css() -> str:
    return """
    @page {
      size: A4;
      margin: 14mm 12mm 16mm;
      @bottom-left  { content: "UniStock - Relatório interno"; color: #64748b; font-size: 9px; }
      @bottom-right { content: "Página " counter(page) " de " counter(pages); color: #64748b; font-size: 9px; }
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: #f1f5f9;
      color: #172033;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 12px;
      line-height: 1.45;
    }

    /* ── Hero ── */
    .hero {
      background: #0f172a;
      color: white;
      padding: 24px;
      border-radius: 18px;
      margin-bottom: 18px;
    }
    .eyebrow {
      color: #93c5fd;
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 2px;
      text-transform: uppercase;
      margin-bottom: 8px;
    }
    .badge-periodo {
      display: inline-block;
      background: #1d4ed8;
      color: white;
      font-size: 9px;
      font-weight: 900;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      padding: 3px 10px;
      border-radius: 999px;
      margin-bottom: 10px;
    }
    h1 { margin: 0; font-size: 28px; letter-spacing: -0.5px; }
    .hero p { margin: 8px 0 0; color: #cbd5e1; font-size: 12px; }

    /* ── Métricas ── */
    .metrics { margin-bottom: 18px; }
    .metric {
      background: #ffffff;
      border: 1px solid #dbe3ef;
      border-radius: 14px;
      display: inline-block;
      margin-right: 1.2%;
      padding: 13px 14px;
      vertical-align: top;
      width: 23.35%;
    }
    .metric:last-child { margin-right: 0; }
    .metric span {
      color: #64748b;
      display: block;
      font-size: 9px;
      font-weight: 800;
      letter-spacing: 1.4px;
      text-transform: uppercase;
    }
    .metric strong { color: #1d4ed8; display: block; font-size: 24px; margin-top: 5px; }

    /* ── Loja ── */
    .store {
      background: white;
      border: 1px solid #dbe3ef;
      border-radius: 16px;
      margin-bottom: 14px;
      overflow: hidden;
      page-break-inside: avoid;
    }
    .store-header {
      align-items: center;
      background: #e8eef7;
      border-bottom: 1px solid #dbe3ef;
      display: flex;
      justify-content: space-between;
      padding: 12px 14px;
    }
    .store-title { color: #0f172a; font-size: 15px; font-weight: 900; text-transform: uppercase; }
    .store-total { color: #1d4ed8; font-size: 11px; font-weight: 800; }

    /* ── Pedido ── */
    .pedido {
      padding: 13px 14px 16px;
      border-bottom: 1px solid #e5eaf2;
      page-break-inside: avoid;
    }
    .pedido:last-child { border-bottom: 0; }
    .pedido-top { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 9px; }
    .pedido-id  { color: #0f172a; font-size: 13px; font-weight: 900; }
    .meta       { color: #64748b; font-size: 11px; margin-top: 2px; }
    .status {
      border-radius: 999px;
      border: 1px solid #bfdbfe;
      background: #eff6ff;
      color: #1d4ed8;
      font-size: 10px;
      font-weight: 900;
      height: fit-content;
      padding: 5px 9px;
      text-transform: uppercase;
      white-space: nowrap;
    }
    .status-entregue  { background: #f0fdf4; border-color: #bbf7d0; color: #15803d; }
    .status-cancelado { background: #fff1f2; border-color: #fecdd3; color: #be123c; }

    /* ── Tabela ── */
    table { border-collapse: collapse; width: 100%; }
    th {
      background: #172033;
      color: white;
      font-size: 10px;
      letter-spacing: 1px;
      padding: 8px;
      text-align: left;
      text-transform: uppercase;
    }
    th:last-child, td:last-child { text-align: center; width: 90px; }
    td { border-bottom: 1px solid #e5eaf2; color: #263248; padding: 8px; }
    tr:nth-child(even) td { background: #f8fafc; }

    .descricao {
      background: #f8fafc;
      border-left: 3px solid #1d4ed8;
      color: #475569;
      margin: 9px 0;
      padding: 8px 10px;
    }
    .empty {
      background: white;
      border: 1px solid #dbe3ef;
      border-radius: 16px;
      color: #64748b;
      font-size: 14px;
      font-weight: 700;
      padding: 40px;
      text-align: center;
    }
    """


# ─── HTML ─────────────────────────────────────────────────────────────────────

def _status_class(status: str) -> str:
    s = status.lower()
    if s == "entregue":
        return "status status-entregue"
    if s == "cancelado":
        return "status status-cancelado"
    return "status"


def _html(context: dict) -> str:
    lojas_html = ""
    for loja in context["lojas"]:
        pedidos_html = ""
        for pedido in loja.pedidos:
            linhas = "".join(
                f"<tr><td>{escape(str(item['produto']))}</td>"
                f"<td>{item['quantidade']} un</td></tr>"
                for item in pedido.itens
            )
            descricao = (
                f'<div class="descricao">{escape(pedido.descricao)}</div>'
                if pedido.descricao else ""
            )
            pedidos_html += f"""
              <div class="pedido">
                <div class="pedido-top">
                  <div>
                    <div class="pedido-id">Pedido #{escape(pedido.id)}</div>
                    <div class="meta">{pedido.hora} · Responsável: {escape(pedido.responsavel)}</div>
                  </div>
                  <div class="{_status_class(pedido.status)}">{escape(pedido.status)}</div>
                </div>
                {descricao}
                <table>
                  <thead><tr><th>Produto</th><th>Qtd</th></tr></thead>
                  <tbody>{linhas}</tbody>
                </table>
              </div>
            """

        lojas_html += f"""
          <section class="store">
            <div class="store-header">
              <div class="store-title">{escape(loja.nome)}</div>
              <div class="store-total">{len(loja.pedidos)} pedidos · {loja.total_itens} itens</div>
            </div>
            {pedidos_html}
          </section>
        """

    corpo = lojas_html or '<div class="empty">Nenhum pedido registrado neste período.</div>'

    # 4 métricas: pedidos, itens, lojas, média de itens/pedido
    total_pedidos = context["total_pedidos"]
    total_itens   = context["total_itens"]
    media = round(total_itens / total_pedidos, 1) if total_pedidos else 0

    return f"""
    <!doctype html>
    <html lang="pt-BR">
      <head>
        <meta charset="utf-8">
        <style>{_css()}</style>
      </head>
      <body>
        <header class="hero">
          <div class="badge-periodo">Relatório {escape(context["periodo_label"])}</div>
          <h1>Pedidos por loja</h1>
          <p>
            Período: {escape(context["intervalo"])} ·
            Emitido em {context["data"]} às {context["hora"]} · UniStock
          </p>
        </header>

        <section class="metrics">
          <div class="metric"><span>Total de pedidos</span><strong>{total_pedidos}</strong></div>
          <div class="metric"><span>Total de itens</span><strong>{total_itens}</strong></div>
          <div class="metric"><span>Lojas com pedidos</span><strong>{len(context["lojas"])}</strong></div>
          <div class="metric"><span>Média itens/pedido</span><strong>{media}</strong></div>
        </section>

        {corpo}
      </body>
    </html>
    """


# ─── Função pública genérica ──────────────────────────────────────────────────

def gerar_relatorio_pedidos_pdf(periodo: Periodo = "dia") -> HttpResponse:
    """
    Gera o relatório PDF para o período informado.

    Uso nas views:
        gerar_relatorio_pedidos_pdf("dia")
        gerar_relatorio_pedidos_pdf("semana")
        gerar_relatorio_pedidos_pdf("mes")
    """
    from weasyprint import HTML

    agora_local, inicio, fim, pedidos = _buscar_pedidos(periodo)
    lojas       = _montar_lojas(pedidos)
    total_itens = sum(loja.total_itens for loja in lojas)

    context = {
        "periodo_label": PERIODO_LABELS[periodo],
        "intervalo":     _label_periodo(periodo, inicio, fim),
        "data":          agora_local.strftime("%d/%m/%Y"),
        "hora":          agora_local.strftime("%H:%M"),
        "total_pedidos": len(pedidos),
        "total_itens":   total_itens,
        "lojas":         lojas,
    }

    nome_arquivo = f"Relatorio_{periodo.capitalize()}_{agora_local.date().isoformat()}.pdf"
    pdf_bytes    = HTML(string=_html(context)).write_pdf()

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
    return response