# main.py
import sys
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import QStringListModel, QDateTime, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QStackedWidget, QInputDialog, QCompleter, QHeaderView
)

from decimal import Decimal

from produto_ui import Produto, ProductView, MovimentoCaixa
from entities import Produto, Venda
from relatorios_ui import RelatorioApp


class MercadinhoApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.showMaximized()

    def initUI(self):

        self.setWindowTitle('Sistema de Caixa - Mercadinho')
        self.setGeometry(100, 200, 800, 600)
        self.showFullScreen()   # Janela maximizada

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        # Add buttons
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        self.relatorios_button = QPushButton('Relatorios')
        self.relatorios_button.clicked.connect(self.show_relatorios)
        self.button_layout.addWidget(self.relatorios_button)

        self.edit_product_button = QPushButton('Produtos')
        self.edit_product_button.clicked.connect(self.show_products_view)
        self.button_layout.addWidget(self.edit_product_button)

        self.movimentacao_button = QPushButton('Movimentação de Caixa')
        self.movimentacao_button.clicked.connect(
            self.show_movimento_product_form)
        self.button_layout.addWidget(self.movimentacao_button)

        self.register_sale_button = QPushButton('Registrar Venda')
        self.register_sale_button.clicked.connect(self.show_register_sale_form)
        self.button_layout.addWidget(self.register_sale_button)

        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # CRIE OS FORMULARIOS
        self.relatorios = RelatorioApp(self)
        self.products_view = ProductView(self)
        self.movimentacao_button = MovimentoCaixa(self)
        self.register_sale_form = SaleForm(self)

        # Add forms to stacked widget
        self.stacked_widget.addWidget(self.relatorios)
        self.stacked_widget.addWidget(self.products_view)
        self.stacked_widget.addWidget(self.movimentacao_button)
        self.stacked_widget.addWidget(self.register_sale_form)

    def show_relatorios(self):
        self.stacked_widget.setCurrentWidget(self.relatorios)

    def show_products_view(self):
        # pass
        self.stacked_widget.setCurrentWidget(self.products_view)

    def show_movimento_product_form(self):
        self.stacked_widget.setCurrentWidget(self.movimentacao_button)

    def show_register_sale_form(self):
        # Remover a instância antiga do SaleForm
        self.stacked_widget.removeWidget(self.register_sale_form)
        self.register_sale_form.deleteLater()

        # Criar uma nova instância do SaleForm
        self.register_sale_form = SaleForm(self)
        self.stacked_widget.addWidget(self.register_sale_form)
        self.stacked_widget.setCurrentWidget(self.register_sale_form)

    def show_error_message(self, message):
        QMessageBox.critical(self, 'Erro', message)


class SaleForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.load_product_names()  # Carregar nomes de produtos ao inicializar
        self.update_date_time()

    def initUI(self):
        self.setLayout(QVBoxLayout())

        self.product_table = QTableWidget()
        self.product_table.setColumnCount(7)
        self.product_table.setHorizontalHeaderLabels(
            ['Código', 'Código de Barras', 'Descrição do Produto', 'Valor Unitário', 'Quantidade', 'Valor Total', 'Remover'])

        self.total_label = QLabel('Total: R$ 0.00')
        # Ajuste o tamanho e o peso da fonte
        self.total_label.setStyleSheet('font-size: 20px; font-weight: bold;')
        self.layout().addWidget(self.total_label)

        # Configurar o comportamento de redimensionamento das colunas
        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Código
        header.setSectionResizeMode(
            1, QHeaderView.ResizeToContents)  # Código de Barras
        header.setSectionResizeMode(
            2, QHeaderView.ResizeToContents)  # Descrição do Produto
        header.setSectionResizeMode(
            3, QHeaderView.ResizeToContents)  # Valor Unitário
        header.setSectionResizeMode(
            4, QHeaderView.ResizeToContents)  # Quantidade
        header.setSectionResizeMode(
            5, QHeaderView.ResizeToContents)  # Valor Total
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Remover

        self.layout().addWidget(self.product_table)

        self.product_input_layout = QHBoxLayout()
        self.layout().addLayout(self.product_input_layout)

        # Código de Barras
        self.product_label = QLabel('Código de Barras:')
        self.product_input_layout.addWidget(self.product_label)
        self.product_input = QLineEdit(self)
        self.product_input_layout.addWidget(self.product_input)

        # ID
        self.id_label = QLabel('ID:')
        self.product_input_layout.addWidget(self.id_label)
        self.id_input = QLineEdit(self)
        self.product_input_layout.addWidget(self.id_input)

        # Nome
        self.name_label = QLabel('Nome:')
        self.product_input_layout.addWidget(self.name_label)
        self.name_input = QLineEdit(self)
        self.product_input_layout.addWidget(self.name_input)

        # Configurar QCompleter para o campo de nome
        self.completer = QCompleter(self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity(False))
        # Permite filtragem por conteúdo
        self.completer.setFilterMode(Qt.MatchContains)
        self.name_input.setCompleter(self.completer)

        # Quantidade
        self.quantity_label = QLabel('Quantidade:')
        self.product_input_layout.addWidget(self.quantity_label)
        self.quantity_input = QLineEdit(self)
        self.product_input_layout.addWidget(self.quantity_input)

        # Criar um validador para aceitar apenas números
        self.quantity_validator = QDoubleValidator(0.0, 1e6, 3, self)
        self.quantity_validator.setNotation(QDoubleValidator.StandardNotation)
        self.quantity_input.setValidator(self.quantity_validator)

        self.add_button = QPushButton('Adicionar Produto')
        self.add_button.clicked.connect(self.add_product)
        self.product_input_layout.addWidget(self.add_button)

        self.register_button = QPushButton('Registrar Venda')
        self.register_button.clicked.connect(self.register_sale)
        self.layout().addWidget(self.register_button)

        self.cancel_button = QPushButton('Cancelar')
        self.cancel_button.clicked.connect(self.cancel_sale)
        self.layout().addWidget(self.cancel_button)

        # Adiciona layout horizontal para o total e data/hora
        self.bottom_layout = QHBoxLayout()
        self.layout().addLayout(self.bottom_layout)

        self.last_sale_id_label = QLabel('Último ID de Venda: N/A')
        # Ajuste o estilo conforme necessário
        self.last_sale_id_label.setStyleSheet(
            'font-size: 16px; font-weight: bold;')
        self.bottom_layout.addWidget(self.last_sale_id_label)

        # Adiciona o rótulo para a data/hora
        self.date_time_label = QLabel('Data e Hora: N/A')
        # Ajuste o estilo conforme necessário
        self.date_time_label.setStyleSheet(
            'font-size: 16px; font-weight: bold;')
        self.bottom_layout.addWidget(self.date_time_label)

    def update_date_time(self):
        now = QDateTime.currentDateTime()
        self.date_time_label.setText(
            f'Data e Hora: {now.toString("dd/MM/yyyy HH:mm:ss")}')

    def load_product_names(self):
        # Obtém todos os produtos e suas descrições para o QCompleter
        produtos = Produto.select().where(Produto.disponivel == True)
        nomes_produtos = [produto.nome for produto in produtos]

        # Configura o modelo do QCompleter
        self.completer.setModel(QStringListModel(nomes_produtos))
        # Adiciona uma função para atualizar a lista de sugestões quando o texto é alterado
        # self.name_input.textChanged.connect(self.update_completer_list)

    def reset_form(self):
        self.product_table.setRowCount(0)
        self.product_input.clear()
        self.id_input.clear()
        self.name_input.clear()
        self.quantity_input.clear()
        self.update_total()

    def add_product(self):
        try:
            codigo_barras = self.product_input.text()
            id_produto = self.id_input.text()
            nome_produto = self.name_input.text()
            quantidade = Decimal(self.quantity_input.text().replace(
                ',', '.')) if self.quantity_input.text() != "" else Decimal('1')

            produto = None

            if codigo_barras:
                try:
                    produto = Produto.get(
                        Produto.codigo_barras == codigo_barras)
                except Produto.DoesNotExist:
                    pass

            if not produto and id_produto:
                try:
                    produto = Produto.get(Produto.id == int(id_produto))
                except Produto.DoesNotExist:
                    pass

            if not produto and nome_produto:
                try:
                    produto = Produto.get(Produto.nome == nome_produto)
                except Produto.DoesNotExist:
                    pass

            if produto:
                preco = Decimal(produto.preco)
                valor_total = preco * quantidade

                row_position = self.product_table.rowCount()
                self.product_table.insertRow(row_position)
                self.product_table.setItem(
                    row_position, 0, QTableWidgetItem(str(produto.id)))
                self.product_table.setItem(
                    row_position, 1, QTableWidgetItem(produto.codigo_barras))
                self.product_table.setItem(
                    row_position, 2, QTableWidgetItem(produto.nome))
                self.product_table.setItem(
                    row_position, 3, QTableWidgetItem(f'R$ {preco:.2f}'))
                self.product_table.setItem(
                    row_position, 4, QTableWidgetItem(str(quantidade)))
                self.product_table.setItem(
                    row_position, 5, QTableWidgetItem(f'R$ {valor_total:.2f}'))

                # Adiciona botão de remover na última coluna
                remove_button = QPushButton('Remover')
                remove_button.clicked.connect(
                    lambda checked, row=row_position: self.remove_product(row))

                self.product_table.setCellWidget(
                    row_position, 6, remove_button)

                self.product_input.clear()
                self.id_input.clear()
                self.name_input.clear()
                self.quantity_input.clear()

                self.update_total()

            else:
                self.show_error_message(
                    "Produto não encontrado. Verifique o código de barras, ID ou nome do produto.")

        except ValueError:
            self.show_error_message(
                "Quantidade inválida. Verifique o valor inserido.")

        except Exception as e:
            self.show_error_message(f"Erro ao adicionar produto: {str(e)}")

    def remove_product(self, row_position):
        try:
            # Remove a linha
            self.product_table.removeRow(row_position)

            # Atualiza a tabela para garantir que as linhas restantes estejam corretamente indexadas
            self.update_total()

            # Para garantir que o índice da linha removida não cause problemas, você pode iterar sobre as linhas restantes e garantir que os índices estejam corretos
            for row in range(self.product_table.rowCount()):
                button = self.product_table.cellWidget(row, 6)
                if button:
                    button.clicked.disconnect()  # Desconecta qualquer sinal existente
                    button.clicked.connect(
                        lambda checked, row=row: self.remove_product(row))

        except Exception as e:
            self.show_error_message(f"Erro ao remover produto: {str(e)}")

    def update_total(self):
        total = Decimal('0.0')
        for row in range(self.product_table.rowCount()):
            valor_total_item = self.product_table.item(
                row, 5).text().replace('R$ ', '').replace(',', '.')
            total += Decimal(valor_total_item)
        self.total_label.setText(f'Total: R$ {total:.2f}')

    def register_sale(self):
        try:
            produtos = []
            quantidades = []

            for row in range(self.product_table.rowCount()):
                codigo_barras = self.product_table.item(row, 1).text()
                quantidade = Decimal(self.product_table.item(row, 4).text())
                produto = Produto.get(Produto.codigo_barras == codigo_barras)
                produtos.append(produto)
                quantidades.append(quantidade)

            forma_pagamento, ok = QInputDialog.getItem(self, 'Forma de Pagamento', 'Selecione a forma de pagamento:',
                                                       ['PIX', 'DINHEIRO', 'CARTÃO'], 0, False)
            if not ok:
                self.show_error_message("Forma de pagamento não selecionada.")
                return

            valor_total = sum(Decimal(self.product_table.item(row, 5).text().replace(
                'R$ ', '').replace(',', '.')) for row in range(self.product_table.rowCount()))

            if forma_pagamento == 'DINHEIRO':
                valor_recebido, ok = QInputDialog.getDouble(
                    self, 'Valor Recebido', 'Digite o valor recebido (apenas para pagamento em dinheiro):', 0.0, 0.0, 1e6, 2)
                if not ok or valor_recebido <= 0:
                    self.show_error_message("Valor recebido não informado.")
                    return
                if valor_recebido < valor_total:
                    self.show_error_message(
                        "Valor recebido menor que o valor total da venda.")
                    return
            else:
                valor_recebido = Decimal('0.00')

            venda, troco = Venda.registrar_venda(
                produtos, quantidades, forma_pagamento, valor_recebido)

            if venda:
                QMessageBox.information(
                    self, 'Sucesso', f'Venda registrada!\n Valor total: R$ {venda.valor_total:.2f}, Troco: R$ {troco:.2f}')
                # Atualizar data/hora
                self.update_date_time()
                # Atualizar o ID da última venda
                self.last_sale_id_label.setText(
                    f'Último ID de Venda: {venda.id}')
                # Limpar tabela e voltar para a tela de registro de venda
                self.reset_form()
            else:
                self.show_error_message('Erro ao registrar a venda.')
        except Exception as e:
            self.show_error_message(f"Erro ao registrar venda: {str(e)}")

    def cancel_sale(self):
        reply = QMessageBox.question(self, 'Cancelar Venda', 'Tem certeza de que deseja cancelar a venda?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.reset_form()
            self.close()  # Fechar o formulário de venda

    def show_error_message(self, message):
        QMessageBox.critical(self, 'Erro', message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MercadinhoApp()
    ex.showMaximized()
    sys.exit(app.exec_())
