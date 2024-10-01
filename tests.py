# #tests.py
# import pandas as pd
# import decimal
# import datetime
# # =========================================================================
# from entities import BaseModel
# from entities import Produto, Venda, ItemVenda, MovimentacaoCaixa, Relatorios

# # =========================================================================
# # Criando produtos
# coca_cola = Produto.create(nome='coca-Cola', preco=5.99, codigo_barras='12345678901')
# salgadinho = Produto.create(nome='Salgadinho', preco=3.99, codigo_barras='12345678955')
# guarana = Produto.create(nome='Guaraná Antartica', preco=8.99, codigo_barras='12345678888')
# pepsi = Produto.create(nome='Pepsi', preco=6.99, codigo_barras='123456789015')
# bala = Produto.create(nome='Bala', preco=2.99, codigo_barras='22345678901')
# coca_cola = Produto.create(nome='Coca-Col4', preco=5.99, codigo_barras='12345678902')
# salgadinho = Produto.create(nome='Salgadinh0', preco=3.99, codigo_barras='12345678965')
# guarana = Produto.create(nome='Guaraná Antartic4', preco=8.99, codigo_barras='12345678903')
# pepsi = Produto.create(nome='Peps1', preco=6.99, codigo_barras='123456789016')
# bala = Produto.create(nome='bal4', preco=2.99, codigo_barras='22345678906')

# # =========================================================================
# # Buscar todos os produtos
# produtos = Produto.buscar_produtos()
# resultados = produtos.dicts() 
# df = pd.DataFrame(resultados)
# # Exibindo o DataFrame
# print(df)

# # Buscar produtos por código de barras
# produtos = Produto.buscar_produtos(codigo_barras="22222222222")
# resultados = produtos.dicts() 
# df = pd.DataFrame(resultados)
# # Exibindo o DataFrame
# print(df)

# # Buscar produtos por nome
# produtos = Produto.buscar_produtos(disponivel=1)
# resultados = produtos.dicts() 
# df = pd.DataFrame(resultados)
# # Exibindo o DataFrame
# print(df)

# # Buscar produtos com preço entre _ e _
# produtos = Produto.buscar_produtos(preco=(5.99))
# print(type(produtos))
# resultados = produtos.dicts() 
# df = pd.DataFrame(resultados)
# # Exibindo o DataFrame
# print(df)

# # =========================================================================

# exclua = Produto.excluir_produto(id=10)

# # =========================================================================
# # Editar o produto por ID
# produto_editado = Produto.editar_produto({'id': 8}, nome='Fini')

# # Editar o produto por nome
# produto_editado = Produto.editar_produto({'nome': 'Salgadinh0'}, codigo_barras='22222222222', nome='Doritos')

# # Editar o produto por nome
# produto_editado = Produto.editar_produto({'nome': 'Guaraná Antartic4'}, nome='Pão')

# # Editar o produto por nome
# produto_editado = Produto.editar_produto({'nome': 'Coca-Col4'}, nome='Chocolate')

# # Editar o produto por código de barras
# produto_editado = Produto.editar_produto({'codigo_barras': '123456789016'}, preco=12.99, nome="Fanta")

# # =========================================================================
# # Registrando uma venda
# produtos_venda = [Produto.buscar_produtos(codigo_barras='12345678955').get(), Produto.buscar_produtos(nome='Chocolate').get()]
# print(produtos_venda)
# quantidades = [3, 1]

# venda = Venda.registrar_venda(produtos_venda, quantidades, 'pix')

# print(f"Venda realizada com sucesso! Valor total: R$ {venda[0].valor_total:.2f}")

# produtos_venda = [Produto.buscar_produtos(codigo_barras='22222222222').get(), Produto.buscar_produtos(nome='Fanta').get()]
# print(produtos_venda)
# quantidades = [2, 3]

# venda = Venda.registrar_venda(produtos_venda, quantidades, 'dinheiro')

# print(f"Venda realizada com sucesso! Valor total: R$ {venda[0].valor_total:.2f}")

# produtos_venda = [Produto.buscar_produtos(codigo_barras='12345678901').get(), Produto.buscar_produtos(nome='Doritos').get()]
# print(produtos_venda)
# quantidades = [2, 1]

# venda = Venda.registrar_venda(produtos_venda, quantidades, 'dinheiro')

# print(f"Venda realizada com sucesso! Valor total: R$ {venda[0].valor_total:.2f}")

# produtos_venda = [Produto.buscar_produtos(codigo_barras='22222222222').get(), Produto.buscar_produtos(nome='Coca-Cola').get()]
# print(produtos_venda)
# quantidades = [0.5 , 3]

# venda = Venda.registrar_venda(produtos_venda, quantidades, 'CARTÃO')
# # =========================================================================
# # Buscar vendas
# venda = Venda.buscar_vendas(id=1).get()
# # print(venda,"================+++++++")
# # venda = Venda.buscar_venda(id=1)
# print(type(venda),"================")
# if venda:
#     # Imprimir os dados da venda formatados
#     print(f"ID da venda: {venda.id}")
#     print(f"Data da venda: {venda.data}")
#     print(f"Valor total: R$ {venda.valor_total:.2f}")
#     print(f"Forma de pagamento: {venda.forma_pagamento}")
#     print(f"Cancelada: {venda.cancelada}")

#     # Imprimir os itens da venda
#     print("Itens da venda:")
#     c=1
#     for item in venda.itens:
#         print(f"- {c}) {item.produto.nome} ({item.quantidade}) ---- R$ {item.valor_unitario:.2f}")
#         c=c+1
# else:
#     print("Venda não encontrada.")

# # # =========================================================================
# # Buscar vendas por data
# data_inicial = "2024-07-30"
# data_inicial2 = "2024-07-31"


# df_vendas = Venda.buscar_vendas()

# resultados = df_vendas.dicts() 
# df_vendas = pd.DataFrame(resultados)
# # # Exibindo o DataFrame
# print(df_vendas)

# # df_vendas = pd.DataFrame(df_vendas)  # Cria um DataFrame a partir dos dicionários
# # # Exibir o DataFrame
# # print(df_vendas)

# # Filtrar as vendas por forma de pagamento e status
# df_vendas_pix = df_vendas[(df_vendas['forma_pagamento'] == 'PIX') & (df_vendas['cancelada'] == False)]


# # Calcular a soma dos valores
# soma_vendas_pix = df_vendas_pix['valor_total'].sum()

# print(f"A soma do valor de vendas em Pix não canceladas é: R$ {soma_vendas_pix:.2f}")
# # # =========================================================================
# venda_a_cancelar = Venda.get(Venda.id == 2)
# venda_a_cancelar.cancelar_venda()
# # =========================================================================
# # Obtendo o item a ser removido (substitua 2 pelo ID correto)
# item_a_remover = ItemVenda.get(ItemVenda.id == 7)
# item_a_remover.remover_item()
# # Obtendo o item a ser removido (substitua 2 pelo ID correto)
# item_a_remover = ItemVenda.get(ItemVenda.id == 8)
# item_a_remover.remover_item()

# # =========================================================================
# # Registrando entradas de dinheiro
# MovimentacaoCaixa.registrar_entrada(decimal.Decimal('100.00'), 'Saldo inicial')
# MovimentacaoCaixa.registrar_entrada(decimal.Decimal('50.00'), 'Entrada adicional')

# # Verificar se as entradas foram registradas corretamente
# entradas = MovimentacaoCaixa.select().where(MovimentacaoCaixa.tipo == 'entrada')
# resultados_entradas = [entrada.__data__ for entrada in entradas]
# df_entradas = pd.DataFrame(resultados_entradas)
# print("Entradas de dinheiro:")
# print(df_entradas)

# # =========================================================================
# # Registrando saídas de dinheiro
# MovimentacaoCaixa.registrar_saida(decimal.Decimal('20.00'), 'Pagamento de fornecedor')
# MovimentacaoCaixa.registrar_saida(decimal.Decimal('15.00'), 'Compra de material')

# # Verificar se as saídas foram registradas corretamente
# saidas = MovimentacaoCaixa.select().where(MovimentacaoCaixa.tipo == 'saida')
# resultados_saidas = [saida.__data__ for saida in saidas]
# df_saidas = pd.DataFrame(resultados_saidas)
# print("Saídas de dinheiro:")
# print(df_saidas)

# # =========================================================================
# # Calculando o saldo do caixa
# saldo_atual = MovimentacaoCaixa.calcular_saldo()
# print(f"Saldo atual do caixa: R$ {saldo_atual:.2f}")

# # =========================================================================
# # Verificar se o saldo está correto


# # =========================================================================
# # Teste: Gerar relatório de produtos
# print("=== Relatório de Produtos ===")
# df_produtos = Relatorios.gerar_relatorio_produtos(preco=(3.98, 6.99))
# print(df_produtos)

# # Teste: Gerar relatório de vendas
# print("=== Relatório de Vendas ===")
# hoje = datetime.date.today()
# df_vendas = Relatorios.gerar_relatorio_vendas(data=hoje, cancelada=False, forma_pagamento='dinheiro')
# print(df_vendas)

# # Teste: Gerar relatório de itens de venda
# print("=== Relatório de Itens de Venda ===")
# df_itens_venda = Relatorios.gerar_relatorio_itens_venda(id_produto="1", id_venda='3')
# print(df_itens_venda)

# # Teste: Gerar relatório de movimentações
# print("=== Relatório de Movimentações ===")
# df_movimentacoes = Relatorios.gerar_relatorio_movimentacoes(data_inicial="2024-07-31")
# print(df_movimentacoes)

# # # # Filtrar as vendas por forma de pagamento e status
# # df_entrada = df_movimentacoes[(df_movimentacoes['tipo'] == 'entrada')]
# # df_saida = df_movimentacoes[(df_movimentacoes['tipo'] == 'saida')]

# # # Calcular a soma dos valores
# # soma_df_entrada = df_entrada['valor'].sum()
# # soma_df_saida = df_saida['valor'].sum()
# # print(f"A soma do valor de vendas em Pix não canceladas é: R$ {(soma_df_entrada - soma_df_saida):.2f}")

# # Teste: Gerar relatório de saldo
# print("=== Relatório de Saldo ===")
# df_saldo = Relatorios.gerar_relatorio_saldo()
# print(df_saldo)

# # Teste: Exportar relatório para CSV
# print("=== Exportando Relatório de Produtos para CSV ===")
# Relatorios.exportar_relatorio(df_produtos, 'relatorio_produtos.csv')

# # Teste: Visualizar relatório (substitua esta função conforme necessário para a interface que você está usando)
# print("=== Visualizando Relatório de Vendas ===")
# Relatorios.visualizar_relatorio(df_vendas)

# print("===== Testes dos Relatórios Concluídos com Sucesso! =====")

# # print("===== Testes do caixa concluídos com sucesso! =====")



