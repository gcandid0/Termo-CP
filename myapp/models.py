import secrets
import string
from django.db import models


def _generate_share_code():
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(8))


class MensagemContato(models.Model):
    nome = models.CharField('Nome', max_length=150)
    email = models.EmailField('E-mail')
    mensagem = models.TextField('Mensagem')
    enviado_por_email = models.BooleanField('Enviado por e-mail', default=False)
    criado_em = models.DateTimeField('Recebido em', auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Mensagem de Contato'
        verbose_name_plural = 'Mensagens de Contato'

    def __str__(self):
        return f"{self.nome} <{self.email}> ({self.criado_em:%d/%m/%Y %H:%M})"


class UsoSimulacao(models.Model):
    """Registro anônimo de uso da plataforma para métricas educacionais e pesquisa."""
    substancia = models.CharField('Substância', max_length=50, db_index=True)
    tipo = models.CharField('Tipo de Simulação', max_length=60, db_index=True)
    idioma = models.CharField('Idioma', max_length=10, default='pt-br', db_index=True)
    criado_em = models.DateTimeField('Data/Hora', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Estatística de Uso'
        verbose_name_plural = 'Estatísticas de Uso'

    def __str__(self):
        return f"{self.substancia} · {self.tipo} [{self.idioma}] ({self.criado_em:%d/%m/%Y %H:%M})"


class SimulacaoCompartilhada(models.Model):
    """Snapshot compartilhável de uma simulação de estado ou processo via link curto /s/<codigo>/."""
    codigo = models.CharField('Código', max_length=12, unique=True, default=_generate_share_code, db_index=True)
    titulo = models.CharField('Título', max_length=200)
    substancia = models.CharField('Substância', max_length=60)
    tipo = models.CharField('Tipo', max_length=60)
    payload_json = models.TextField('Dados da Simulação (JSON)')
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Simulação Compartilhada'
        verbose_name_plural = 'Simulações Compartilhadas'

    def __str__(self):
        return f"[{self.codigo}] {self.titulo}"


def _generate_poe_code():
    alphabet = string.ascii_uppercase + string.digits
    return 'POE-' + ''.join(secrets.choice(alphabet) for _ in range(6))


class TentativaExercicio(models.Model):
    """Registro de resolução no Modo Exercício (POE) para auditoria docente e pesquisa educacional."""
    codigo = models.CharField('Código', max_length=16, unique=True, default=_generate_poe_code, db_index=True)
    nome_aluno = models.CharField('Estudante', max_length=120, blank=True, default='Anônimo')
    substancia = models.CharField('Substância', max_length=60, db_index=True)
    tipo = models.CharField('Tipo', max_length=40, db_index=True)
    nivel = models.CharField('Nível', max_length=30, default='basic')
    pontuacao = models.FloatField('Pontuação (%)', default=0.0)
    poe_acertos = models.PositiveSmallIntegerField('Acertos POE (0-3)', default=0)
    tentativas = models.PositiveSmallIntegerField('Tentativas', default=1)
    tempo_segundos = models.PositiveIntegerField('Tempo (s)', default=0)
    usou_dica = models.BooleanField('Usou dica', default=False)
    justificativa = models.TextField('Justificativa escrita', blank=True, default='')
    idioma = models.CharField('Idioma', max_length=10, default='pt-br')
    criado_em = models.DateTimeField('Concluído em', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Resolução de Exercício (POE)'
        verbose_name_plural = 'Resoluções de Exercícios (POE)'

    def __str__(self):
        return f"[{self.codigo}] {self.nome_aluno} · {self.substancia} ({self.pontuacao:.0f}%)"
