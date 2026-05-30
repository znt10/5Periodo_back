from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import Produto


PRODUTOS = {
    Produto.Categoria.SALGADOS_GDE: [
        "Coxinha",
        "Risoles de queijo",
        "Risole presunto e queijo",
        "Bolinho de carne",
        "Kibe",
        "Kibe Queijo",
        "Salsicha",
        "Bolinho ovo",
    ],
    Produto.Categoria.SALGADOS_MINI: [
        "Coxinha",
        "Risoles de queijo",
        "Risole presunto e queijo",
        "Bolinho de carne",
        "Kibe",
        "Kibe Queijo",
    ],
    Produto.Categoria.ESFIHAS_GDE: [
        "Carne",
        "Frango",
        "Bauru",
        "Calabresa",
        "Hamburger",
        "Salsicha com cheddar",
        "Torta de banana",
    ],
    Produto.Categoria.ESFIHAS_MINI: [
        "Carne",
        "Frango",
        "Bauru",
        "Calabresa",
        "Hamburger",
        "Salsicha com cheddar",
        "Torta de banana",
    ],
    Produto.Categoria.FOGAZZAS_GDE: [
        "Presunto e Queijo",
        "2 Queijos",
        "Calabresa",
        "Frango",
        "Pizza",
        "Chocolate",
        "Doce de leite",
    ],
    Produto.Categoria.FOGAZZAS_MINI: [
        "Presunto e Queijo",
        "2 Queijos",
        "Calabresa",
        "Frango",
        "Pizza",
        "Chocolate",
        "Doce de leite",
    ],
    Produto.Categoria.RECHEIOS: [
        "Açúcar+canela",
        "Bisnaga de chocolate",
        "Bisnaga doce de leite",
        "Bisnaga Beijinho",
        "Calabresa",
        "Carne",
        "Catupiry",
        "Frango",
        "Laranja",
        "Limão",
        "Massa de empada",
        "Massa Pastel",
        "Mussarela",
        "Óleo",
        "Orégano",
        "Ovo",
        "Palmito",
        "Pimenta",
        "Presunto",
        "Tomate",
    ],
    Produto.Categoria.MERCADO: [
        "Açúcar",
        "Café",
        "Detergente",
        "Leite",
        "Nescau",
        "Bombril",
        "Adoçante",
    ],
}


class Command(BaseCommand):
    help = "Cadastra a lista padrao de produtos do UniStock."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limpar",
            action="store_true",
            help="Remove todos os produtos antes de cadastrar a lista padrao.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["limpar"]:
            total_removidos, _ = Produto.objects.all().delete()
            self.stdout.write(f"Registros removidos: {total_removidos}")

        criados = 0
        atualizados = 0

        for categoria, nomes in PRODUTOS.items():
            for nome in nomes:
                _, created = Produto.objects.update_or_create(
                    nome_produto=nome.strip(),
                    categoria=categoria,
                    defaults={
                        "unidade_medida": Produto.UnidadeMedida.UNIDADE,
                        "quantidade_por_embalagem": None,
                        "estoque_minimo_sugerido": 1,
                    },
                )

                if created:
                    criados += 1
                else:
                    atualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Produtos cadastrados. Criados: {criados}. Atualizados: {atualizados}."
            )
        )
