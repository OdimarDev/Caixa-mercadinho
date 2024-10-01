import unittest
import pandas as pd
from entities import Produto, Venda, ItemVenda, MovimentacaoCaixa, Relatorios
import decimal


class TestEntities(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.produto1 = Produto.create(
            nome='Produto 1', preco=10.00, codigo_barras='1111111')
        cls.produto2 = Produto.create(
            nome='Produto 2', preco=20.00, codigo_barras='2222222')
        cls.produto3 = Produto.create(
            nome='Produto 3', preco=30.00, codigo_barras='3333333')

    @classmethod
    def tearDownClass(cls):
        Produto.delete().execute()
        Venda.delete().execute()
        ItemVenda.delete().execute()
        MovimentacaoCaixa.delete().execute()

    def test_criar_produto(self):
        produto = Produto.create(nome='Produto Teste',
                                 preco=15.00, codigo_barras='4444444')
        self.assertIsNotNone(produto.id)
        self.assertEqual(produto.nome, 'Produto Teste')
        self.assertEqual(produto.preco, decimal.Decimal('15.00'))
        self.assertEqual(produto.codigo_barras, '4444444')

    def test_buscar_produto_por_codigo_barras(self):
        produto = Produto.buscar_produtos(codigo_barras='1111111').get()
        self.assertEqual(produto.nome, 'Produto 1')

    def test_editar_produto(self):
        Produto.editar_produto(
            {'codigo_barras': '1111111'}, nome='Produto 1 Editado', preco=12.00)
        produto = Produto.buscar_produtos(codigo_barras='1111111').get()
        self.assertEqual(produto.nome, 'Produto 1 Editado')
        self.assertEqual(produto.preco, decimal.Decimal('12.00'))

    def test_excluir_produto(self):
        produto = Produto.create(
            nome='Produto a Excluir', preco=5.00, codigo_barras='55555555555')
        Produto.excluir_produto(codigo_barras='55555555555')
        produtos = Produto.buscar_produtos(codigo_barras='55555555555')
        self.assertEqual(produtos.count(), 0)

    def test_registrar_venda(self):
        venda, troco = Venda.registrar_venda(
            [self.produto1, self.produto2],
            [1, 2],
            'DINHEIRO',
            valor_recebido=60.00
        )
        self.assertIsNotNone(venda)
        self.assertEqual(venda.valor_total, decimal.Decimal('50.00'))
        self.assertEqual(troco, decimal.Decimal('10.00'))

    def test_cancelar_venda(self):
        venda, _ = Venda.registrar_venda(
            [self.produto1, self.produto2],
            [1, 2],
            'DINHEIRO',
            valor_recebido=60.00
        )
        venda.cancelar_venda()
        venda = Venda.get(Venda.id == venda.id)
        self.assertTrue(venda.cancelada)
        self.assertEqual(venda.valor_total, decimal.Decimal('0.00'))

    def test_remover_item_venda(self):
        venda, _ = Venda.registrar_venda(
            [self.produto1, self.produto2],
            [1, 2],
            'DINHEIRO',
            valor_recebido=60.00
        )
        for item in venda.itens:
            item.remover_item()
        venda = Venda.get(Venda.id == venda.id)
        self.assertTrue(venda.cancelada)

    def test_registrar_entrada_caixa(self):
        MovimentacaoCaixa.registrar_entrada(
            decimal.Decimal('100.00'), 'Entrada Teste')
        movimentacoes = MovimentacaoCaixa.select().where(
            MovimentacaoCaixa.tipo == 'entrada')
        self.assertGreater(movimentacoes.count(), 0)

    def test_registrar_saida_caixa(self):
        MovimentacaoCaixa.registrar_saida(
            decimal.Decimal('50.00'), 'Saída Teste')
        movimentacoes = MovimentacaoCaixa.select().where(
            MovimentacaoCaixa.tipo == 'saida')
        self.assertGreater(movimentacoes.count(), 0)

    def test_calcular_saldo_caixa(self):
        MovimentacaoCaixa.registrar_entrada(decimal.Decimal('200.00'))
        MovimentacaoCaixa.registrar_saida(decimal.Decimal('100.00'))
        saldo = MovimentacaoCaixa.calcular_saldo()
        self.assertEqual(saldo, decimal.Decimal('100.00'))

    def test_gerar_relatorio_produtos(self):
        df = Relatorios.gerar_relatorio_produtos()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)

    def test_gerar_relatorio_vendas(self):
        venda, _ = Venda.registrar_venda(
            [self.produto1],
            [2],
            'DINHEIRO',
            valor_recebido=20.00
        )
        df = Relatorios.gerar_relatorio_vendas()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)

    def test_gerar_relatorio_itens_venda(self):
        venda, _ = Venda.registrar_venda(
            [self.produto1],
            [2],
            'DINHEIRO',
            valor_recebido=20.00
        )
        df = Relatorios.gerar_relatorio_itens_venda(id_venda=venda.id)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)

    def test_gerar_relatorio_movimentacoes(self):
        MovimentacaoCaixa.registrar_entrada(
            decimal.Decimal('100.00'), 'Saldo inicial')
        MovimentacaoCaixa.registrar_saida(
            decimal.Decimal('20.00'), 'Pagamento de fornecedor')
        df = Relatorios.gerar_relatorio_movimentacoes()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)

    def test_gerar_relatorio_saldo(self):
        df = Relatorios.gerar_relatorio_saldo()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        self.assertAlmostEqual(df['Valor'][0], decimal.Decimal('80.00'))

    def test_exportar_relatorio(self):
        df = Relatorios.gerar_relatorio_produtos()
        Relatorios.exportar_relatorio(df, 'relatorio_produtos.csv')
        with open('relatorio_produtos.csv', 'r') as file:
            content = file.read()
        self.assertIn('nome,preco,codigo_barras,disponivel', content)

    def test_visualizar_relatorio(self):
        df = Relatorios.gerar_relatorio_produtos()
        with self.assertLogs('root', level='INFO') as log:
            Relatorios.visualizar_relatorio(df)
            self.assertIn('Produto 1', log.output[0])


if __name__ == '__main__':
    unittest.main()
