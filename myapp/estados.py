import json


class estados_cls:
    """ESTADOS"""

    classe = 'Estados'

    def __init__(self, lista_estados=None):
        self.lista_estados = []
        # Nova lista para guardar as coordenadas dos diagramas (Fluidos)
        self.pontos_grafico = []

    def limpar_estados(self):
        self.lista_estados.clear()
        # Garante que o gráfico seja limpo ao iniciar um novo problema
        self.pontos_grafico.clear()


class gas_cls:
    """
    Classe de armazenamento em memória dos estados de gás (uso local/standalone).
    Cada estado salvo segue a estrutura:
    [Cv0, Cp0, R, K, p, T, v]
    Todas as grandezas salvas em forma numérica.
    """

    classe = 'Gas'

    def __init__(self):
        # Lista onde cada item é um estado completo
        self.lista_gas = []
        # Preparando a estrutura para diagramas de processos de gases ideais
        self.pontos_grafico_gas = []

    def limpar_gas(self):
        self.lista_gas.clear()
        self.pontos_grafico_gas.clear()

    def salvar_estado(self, Cv0, Cp0, R, K, p, T, v):
        try:
            estado = [
                float(Cv0) if Cv0 is not None else None,
                float(Cp0) if Cp0 is not None else None,
                float(R) if R is not None else None,
                float(K) if K is not None else None,
                float(p) if p is not None else None,
                float(T) if T is not None else None,
                float(v) if v is not None else None,
            ]
            self.lista_gas.append(estado)
        except Exception as e:
            print("Erro ao salvar estado:", e)

    def ultimo_estado(self):
        if not self.lista_gas:
            return None

        ultimo = self.lista_gas[-1]

        if (
            isinstance(ultimo, (list, tuple)) and
            len(ultimo) == 7 and
            all(x is not None for x in ultimo)
        ):
            return ultimo

        return None

    def tem_estado_valido(self):
        return self.ultimo_estado() is not None

    def pegar_estado_completo(self):
        ultimo = self.ultimo_estado()
        if ultimo is None:
            return None, None, None, None, None, None, None
        return tuple(ultimo)

    def print_lista(self):
        print("---- LISTA DE ESTADOS DE GÁS ----")
        for i, est in enumerate(self.lista_gas):
            print(f"{i}: {est}")
        print("----------------------------------")


class _SessionListProxy(list):
    """
    Proxy transparente de lista que notifica alterações imediatamente
    para que a sessão do Django seja sincronizada sem necessidade de reatribuição explícita.
    """
    def __init__(self, iterable, on_modify):
        super().__init__(iterable)
        self._on_modify = on_modify

    def append(self, item):
        super().append(item)
        self._on_modify(self)

    def extend(self, items):
        super().extend(items)
        self._on_modify(self)

    def clear(self):
        super().clear()
        self._on_modify(self)

    def pop(self, index=-1):
        item = super().pop(index)
        self._on_modify(self)
        return item

    def remove(self, item):
        super().remove(item)
        self._on_modify(self)


class GasSession:
    """
    Armazenamento de estados de Gás Ideal 100% STATELESS e isolado por sessão.
    Armazena lista_gas e pontos_grafico_gas em request.session['termo_flows']['gas'],
    eliminando qualquer variável global compartilhada no processo Python entre
    diferentes usuários ou requisições concorrentes.
    """
    classe = 'GasSession'

    def __init__(self, request, scope='gas'):
        self.request = request
        self.scope = scope

    def _get_bucket(self):
        if not hasattr(self.request, 'session'):
            return {}
        flows = self.request.session.get('termo_flows')
        if not isinstance(flows, dict):
            flows = {}
            self.request.session['termo_flows'] = flows
        bucket = flows.get(self.scope)
        if not isinstance(bucket, dict):
            bucket = {}
            flows[self.scope] = bucket
        return bucket

    def _sync_lista(self, lst):
        if not hasattr(self.request, 'session'):
            return
        bucket = self._get_bucket()
        bucket['lista_gas'] = list(lst)
        self.request.session['termo_flows'][self.scope] = bucket
        self.request.session['lista_gas'] = json.dumps(list(lst), default=str)
        self.request.session.modified = True

    def _sync_pontos(self, lst):
        if not hasattr(self.request, 'session'):
            return
        bucket = self._get_bucket()
        bucket['pontos_grafico_gas'] = list(lst)
        self.request.session['termo_flows'][self.scope] = bucket
        self.request.session['pontos_grafico_gas'] = list(lst)
        self.request.session.modified = True

    @property
    def lista_gas(self):
        if not hasattr(self.request, 'session'):
            return _SessionListProxy([], self._sync_lista)
        bucket = self._get_bucket()
        val = bucket.get('lista_gas')
        if isinstance(val, list):
            return _SessionListProxy(val, self._sync_lista)
        # Fallback de compatibilidade caso ainda esteja no topo da session como json
        raw = self.request.session.get('lista_gas')
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return _SessionListProxy(parsed, self._sync_lista)
            except Exception:
                pass
        elif isinstance(raw, list):
            return _SessionListProxy(raw, self._sync_lista)
        return _SessionListProxy([], self._sync_lista)

    @lista_gas.setter
    def lista_gas(self, val):
        if not isinstance(val, list):
            val = list(val)
        self._sync_lista(val)

    @property
    def pontos_grafico_gas(self):
        if not hasattr(self.request, 'session'):
            return _SessionListProxy([], self._sync_pontos)
        bucket = self._get_bucket()
        val = bucket.get('pontos_grafico_gas')
        if isinstance(val, list):
            return _SessionListProxy(val, self._sync_pontos)
        val_top = self.request.session.get('pontos_grafico_gas')
        if isinstance(val_top, list):
            return _SessionListProxy(val_top, self._sync_pontos)
        return _SessionListProxy([], self._sync_pontos)

    @pontos_grafico_gas.setter
    def pontos_grafico_gas(self, val):
        if not isinstance(val, list):
            val = list(val)
        self._sync_pontos(val)

    def limpar_gas(self):
        self.lista_gas = []
        self.pontos_grafico_gas = []
        if hasattr(self.request, 'session'):
            self.request.session['pontos_grafico'] = []
            self.request.session['historico_processos'] = []
            if 'dados_processo' in self.request.session:
                try:
                    del self.request.session['dados_processo']
                except KeyError:
                    pass
            self.request.session.modified = True

    def salvar_estado(self, Cv0, Cp0, R, K, p, T, v):
        try:
            estado = [
                float(Cv0) if Cv0 is not None else None,
                float(Cp0) if Cp0 is not None else None,
                float(R) if R is not None else None,
                float(K) if K is not None else None,
                float(p) if p is not None else None,
                float(T) if T is not None else None,
                float(v) if v is not None else None,
            ]
            self.lista_gas.append(estado)
        except Exception as e:
            print("Erro ao salvar estado:", e)

    def ultimo_estado(self):
        lg = self.lista_gas
        if not lg:
            return None
        ultimo = lg[-1]
        if (
            isinstance(ultimo, (list, tuple)) and
            len(ultimo) == 7 and
            all(x is not None for x in ultimo)
        ):
            return ultimo
        return None

    def tem_estado_valido(self):
        return self.ultimo_estado() is not None

    def pegar_estado_completo(self):
        ultimo = self.ultimo_estado()
        if ultimo is None:
            return None, None, None, None, None, None, None
        return tuple(ultimo)


def get_gas_session(request, scope='gas'):
    """Retorna uma instância stateless de GasSession isolada na sessão da requisição."""
    return GasSession(request, scope=scope)


# Instância legada em memória preservada para retrocompatibilidade caso scripts antigos acessem std.instancia_gas
instancia_gas = gas_cls()
