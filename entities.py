#entities.py
import peewee as pw
import datetime 
import decimal
import pandas as pd
import io

db = pw.SqliteDatabase('mercadinho.db')

class BaseModel(pw.Model):
    class Meta:
        database = db

class Produto(BaseModel):
    nome = pw.CharField(unique=True)
    preco = pw.DecimalField()
    codigo_barras = pw.CharField(unique=True)  # Garantindo que cada código de barras seja único
    disponivel = pw.BooleanField(default=True)

    @classmethod
    def buscar_produtos(cls, **kwargs):
        """Busca produtos com base nos critérios fornecidos.

        Args:
            **kwargs: Dicionário com os critérios de busca. As chaves são os nomes dos campos e os valores são os valores a serem filtrados.

        Returns:
            os produtos encontrados.
        """
        query = cls.select()
        for campo, valor in kwargs.items():
            if campo in ['nome', 'codigo_barras']:
                query = query.where(getattr(cls, campo).contains(valor))
            elif campo in ['preco']:
                if isinstance(valor, (int, float)):
                    query = query.where(getattr(cls, campo) == valor)
                elif isinstance(valor, tuple) and len(valor) == 2:
                    query = query.where(getattr(cls, campo).between(*valor))
            else:
                query = query.where(getattr(cls, campo) == valor)
        results = query
        return results
    
    @classmethod
    def editar_produto(cls, criterios, **kwargs):
        """Edita um produto baseado nos critérios de busca e nos novos dados.

        Args:
            criterios (dict): Dicionário com os critérios de busca (nome, id ou codigo_barras).
            **kwargs: Dicionário com os novos dados a serem atualizados.

        Returns:
            Produto: O produto editado, caso exista.
            None: Caso nenhum produto seja encontrado.
        """


        try:
            with db.atomic():
                produto = cls.get(**criterios)
                for campo, valor in kwargs.items():
                    setattr(produto, campo, valor)
                produto.save()
                return produto
        except cls.DoesNotExist:
            print(f"Produto com os critérios {criterios} não encontrado.")
            return None
        except Exception as e:
            print(f"Erro ao atualizar o produto: {str(e)}")
            return None

    @classmethod
    def excluir_produto(cls, **kwargs):
        try:
            with db.atomic():
                produto = cls.get(**kwargs)
                produto.delete_instance()
                print(f"Produto {produto.nome} excluído")
        except cls.DoesNotExist:
            print("Produto não encontrado.")
        except Exception as e:
            print(f"Erro ao excluir o produto: {str(e)}")

    def save(self, *args, **kwargs):
        # Garantir que o nome seja capitalizado antes de salvar
        self.nome = self.nome.title()
        super().save(*args, **kwargs)
        
        
class Venda(BaseModel):
    data = pw.DateTimeField(default=datetime.datetime.now())
    valor_total = pw.DecimalField(default=0)
    FORMA_PAGAMENTO_CHOICES = (
        ('PIX', 'Pix'),
        ('DINHEIRO', 'Dinheiro'),
        ('CARTÃO', 'Cartão'),
    )
    forma_pagamento = pw.CharField(choices=FORMA_PAGAMENTO_CHOICES)
    cancelada = pw.BooleanField(default=False)
    
    @classmethod
    def registrar_venda(cls, produtos, quantidades, forma_pagamento,valor_recebido=None):
        forma_pagamento = forma_pagamento.upper()
        formas_pagamento_validas = [opcao[0] for opcao in cls.FORMA_PAGAMENTO_CHOICES]
        if forma_pagamento not in formas_pagamento_validas:
            raise ValueError("Forma de pagamento inválida.")
        
        try:
            with db.atomic():
                venda = cls.create(forma_pagamento=forma_pagamento)
                for produto, quantidade in zip(produtos, quantidades):
                    ItemVenda.create(venda=venda, produto=produto, quantidade=quantidade, valor_unitario=produto.preco)

                venda.valor_total = round(venda.itens.select(pw.fn.SUM(ItemVenda.valor_unitario * ItemVenda.quantidade)).scalar(), 2)
                venda.save()
                
                troco = 0.00
                if forma_pagamento == 'DINHEIRO':
                    if valor_recebido is not None:
                        troco = valor_recebido - venda.valor_total
                        MovimentacaoCaixa.registrar_entrada(venda.valor_total)
                        print(f'Troco: R$ {troco:.2f}')
                    else:
                        MovimentacaoCaixa.registrar_entrada(venda.valor_total)
                        print("Valor recebido não informado")
                        # raise ValueError("Valor recebido não informado")
                        
                return venda, troco
            
        except Exception as e:
            print(f"Erro ao registrar venda: {str(e)}")
            return None, 0.00
    
    @classmethod
    def buscar_vendas(cls, **kwargs):
        """Busca vendas com base nos critérios fornecidos.

        Args:
            **kwargs: Argumentos nomeados representando os critérios de busca.
                - id: ID da venda
                - data_inicial: Data inicial da venda
                - data_final: Data final da venda
                - forma_pagamento: Forma de pagamento

        Returns:
            vendas encontradas.
        """

        query = cls.select()

        for campo, valor in kwargs.items():
            if campo == 'id':
                query = query.where(cls.id == valor)
            elif campo == 'data':
                data_inicial = datetime.datetime.strptime(str(valor), '%Y-%m-%d').date()
                query = query.where(cls.data >= data_inicial)
                data_final = datetime.datetime.strptime(str(valor), '%Y-%m-%d').date() + datetime.timedelta(days=1)
                query = query.where(cls.data <= data_final)    
            elif campo == 'data_inicial':
                data_inicial = datetime.datetime.strptime(str(valor), '%Y-%m-%d').date()
                query = query.where(cls.data >= data_inicial)
            elif campo == 'data_final':
                data_final = datetime.datetime.strptime(str(valor), '%Y-%m-%d').date() + datetime.timedelta(days=1)
                query = query.where(cls.data <= data_final)
            elif campo == 'forma_pagamento':
                query = query.where(cls.forma_pagamento == valor.upper())
            else:
                query = query.where(getattr(cls, campo) == valor)

        results = query
        return results

    def cancelar_venda(self):
        if self.cancelada:
            print("A venda já está cancelada.")
            return
        
        with db.atomic():
            # Remover todos os itens da venda
            for item in self.itens:
                item.remover_item(venda=self)
                
            self.cancelada = True
            self.save()
            print('Venda cancelada e ajustada no caixa')

class ItemVenda(BaseModel):
    venda = pw.ForeignKeyField(Venda, backref='itens')
    produto = pw.ForeignKeyField(Produto)
    quantidade = pw.DecimalField()
    valor_unitario = pw.DecimalField()
    
    def remover_item(self, venda=None):
        if venda is None:
            venda = self.venda  # Obter a venda associada ao item
        
        with db.atomic():

            if self.venda.cancelada:
                # Se a venda já estiver cancelada, não faz mais ajustes financeiros
                self.delete_instance()
                return
            
            # Remove o item da venda
            valor_item = self.valor_unitario * self.quantidade
            self.delete_instance()
            
            # Atualiza o valor total da venda
            vt = self.venda.itens.select(pw.fn.SUM(ItemVenda.valor_unitario * ItemVenda.quantidade)).scalar() 
            venda.valor_total = vt if vt is not None else 0 

            # Atualiza o saldo do caixa se a venda não estiver cancelada
            if not venda.cancelada and venda.forma_pagamento == 'DINHEIRO':
                MovimentacaoCaixa.registrar_saida(valor_item, "Remoção de item da venda")
                print('Item removido e ajustado no caixa')
            
            venda.save()
        
            # Cancelar a venda se não houver mais itens
            if venda.valor_total == 0 and not venda.cancelada:
                venda.cancelar_venda()
                print('Venda cancelada devido a remoção de todos os itens')
            
class MovimentacaoCaixa(BaseModel):
    valor = pw.DecimalField(max_digits=10, decimal_places=2)
    tipo = pw.CharField()  # 'entrada' ou 'saida'
    descricao = pw.CharField()
    data_hora = pw.DateTimeField(default=datetime.datetime.now)

    @staticmethod
    def registrar_entrada(valor, descricao='Entrada de dinheiro'):
        MovimentacaoCaixa.create(valor=valor, tipo='entrada', descricao=descricao)

    @staticmethod
    def registrar_saida(valor, descricao='Saída de dinheiro'):
        MovimentacaoCaixa.create(valor=valor, tipo='saida', descricao=descricao)

    @staticmethod
    def calcular_saldo():
        entradas = MovimentacaoCaixa.select(pw.fn.SUM(MovimentacaoCaixa.valor)).where(MovimentacaoCaixa.tipo == 'entrada').scalar() or decimal.Decimal('0.00')
        saidas = MovimentacaoCaixa.select(pw.fn.SUM(MovimentacaoCaixa.valor)).where(MovimentacaoCaixa.tipo == 'saida').scalar() or decimal.Decimal('0.00')
        return round(entradas - saidas,2)

class Relatorios:
    @staticmethod
    def gerar_relatorio_produtos(**kwargs):
        """Gera um relatório com todos os produtos com base nos critérios fornecidos."""
        produtos = Produto.buscar_produtos(**kwargs)
        results = produtos
        return results
        
    
    @staticmethod
    def gerar_relatorio_vendas(**kwargs):
        """Gera um relatório com todas as vendas dentro do intervalo de datas fornecido."""
        vendas = Venda.buscar_vendas(**kwargs)
        results = vendas
        return results

    @staticmethod
    def gerar_relatorio_itens_venda(**kwargs):
        """Gera um relatório com todos os itens de uma venda específica com base no ID fornecido ou outros critérios."""
        query = ItemVenda.select()
        for campo, valor in kwargs.items():
            if campo == 'id_venda':
                query = query.where(ItemVenda.venda == valor)
            elif campo == 'id_produto':
                query = query.where(ItemVenda.produto == valor)
            elif campo == 'data_venda':
                venda = Venda.get_or_none(Venda.id == kwargs.get('id_venda'))
                if venda:
                    query = query.where(ItemVenda.venda == venda)
            else:
                raise ValueError(f"Criterio {campo} não suportado.")
        results = query
        return results

    @staticmethod
    def gerar_relatorio_movimentacoes(**kwargs):
        """Gera um relatório com as movimentações de caixa, filtradas por tipo e outros critérios se especificado."""
        query = MovimentacaoCaixa.select()
        
        for campo, valor in kwargs.items():
            if campo == 'tipo':
                query = query.where(MovimentacaoCaixa.tipo == valor.lower())
            elif campo == 'data_inicial':
                data_inicial = datetime.datetime.strptime(str(valor), '%Y-%m-%d').date()
                query = query.where(MovimentacaoCaixa.data_hora >= data_inicial)
            elif campo == 'data_final':
                data_final = datetime.datetime.strptime(str(valor), '%Y-%m-%d').date() + datetime.timedelta(days=1)
                query = query.where(MovimentacaoCaixa.data_hora < data_final)
            elif campo == 'id':
                query = query.where(MovimentacaoCaixa.id == valor)
            elif campo == 'descricao':
                query = query.where(MovimentacaoCaixa.descricao.contains(valor))  # Usar .contains para permitir filtragem parcial
            else:
                raise ValueError(f"Criterio {campo} não suportado.")
        results = query
        return results

    
    @staticmethod
    def gerar_relatorio_saldo():
        """Gera um relatório com o saldo atual do caixa."""
        saldo = MovimentacaoCaixa.calcular_saldo()
        df = pd.DataFrame({
            'Descrição': ['Saldo Atual'],
            'Valor': [saldo]
        })
        return df

    @staticmethod
    def exportar_relatorio(df, nome_arquivo):
        """Exporta o DataFrame para um arquivo CSV."""
        df.to_excel(nome_arquivo, index=False)

    @staticmethod
    def visualizar_relatorio(df):
        df = pd.DataFrame(list(df.dicts()))  # Convertendo os resultados para um formato de lista de dicionários
        """Exibe o relatório na tela. Pode ser substituído ou adaptado para diferentes bibliotecas de interface."""
        #print(df)
        return df
        
db.create_tables([Produto, Venda, ItemVenda, MovimentacaoCaixa])
