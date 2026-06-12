from django.db import migrations


def popular_planos(apps, schema_editor):
    Plano = apps.get_model('paginas_vendas', 'Plano')

    Plano.objects.get_or_create(
        slug='teste-gratis',
        defaults=dict(
            nome='Teste Gratuito',
            descricao='Aproveite 7 dias gratuitos para testar todos os recursos da plataforma sem compromisso.',
            preco=0,
            duracao_dias=7,
            ativo=True,
            ordem=0,
            eh_teste_gratis=True,
        ),
    )

    Plano.objects.get_or_create(
        slug='1-mes',
        defaults=dict(
            nome='Plano Mensal',
            descricao='',
            preco=29.90,
            duracao_dias=30,
            ativo=True,
            ordem=1,
        ),
    )

    Plano.objects.get_or_create(
        slug='3-meses',
        defaults=dict(
            nome='Plano Trimestral',
            descricao='',
            preco=79.90,
            duracao_dias=90,
            ativo=True,
            ordem=2,
        ),
    )

    Plano.objects.get_or_create(
        slug='6-meses',
        defaults=dict(
            nome='Plano Semestral',
            descricao='',
            preco=149.90,
            duracao_dias=180,
            ativo=True,
            ordem=3,
        ),
    )


def reverter(apps, schema_editor):
    Plano = apps.get_model('paginas_vendas', 'Plano')
    Plano.objects.filter(slug__in=['teste-gratis', '1-mes', '3-meses', '6-meses']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('paginas_vendas', '0005_plano'),
    ]

    operations = [
        migrations.RunPython(popular_planos, reverter),
    ]
