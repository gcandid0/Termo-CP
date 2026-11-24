from django.db import models


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
