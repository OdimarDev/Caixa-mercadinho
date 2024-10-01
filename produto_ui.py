#produto_ui.py
import re
from sqlite3 import IntegrityError
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import QAbstractTableModel, QVariant, Qt, QSortFilterProxyModel
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QLineEdit, QMessageBox, QHeaderView, QTableView,
    QDialog, QCheckBox
)
from entities import  Produto, Relatorios
from decimal import Decimal

class ProductFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_id = ""
        self.filter_name = ""
        self.filter_price = ""
        self.filter_barcode = ""
        self.filter_available = ""

    def set_filter_id(self, text):
        self.filter_id = text
        self.invalidateFilter()

    def set_filter_name(self, text):
        self.filter_name = text.lower()
        self.invalidateFilter()

    def set_filter_price(self, text):
        self.filter_price = text.lower()
        self.invalidateFilter()

    def set_filter_barcode(self, text):
        self.filter_barcode = text.lower()
        self.invalidateFilter()

    def set_filter_available(self, text):
        self.filter_available = text.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        index_id = model.index(source_row, 0, source_parent)
        index_name = model.index(source_row, 1, source_parent)
        index_price = model.index(source_row, 2, source_parent)
        index_barcode = model.index(source_row, 3, source_parent)
        index_available = model.index(source_row, 4, source_parent)

        id = model.data(index_id)
        name = model.data(index_name).lower()
        price = model.data(index_price)
        barcode = model.data(index_barcode).lower()
        available = model.data(index_available).lower()

        return (self.filter_id in str(id) or self.filter_id == "") and \
               (self.filter_name in name or self.filter_name == "") and \
               (self.filter_price in str(price) or self.filter_price == "") and \
               (self.filter_barcode in barcode or self.filter_barcode == "") and \
               (self.filter_available in available or self.filter_available == "")

class ProductTableModel(QAbstractTableModel):
    def __init__(self, produtos=None, parent=None):
        super().__init__(parent)
        self.produtos = produtos or []

    def rowCount(self, parent=None):
        return len(self.produtos)

    def columnCount(self, parent=None):
        return 6  # Número de colunas

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        produto = self.produtos[index.row()]

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return produto.id
            elif index.column() == 1:
                return produto.nome
            elif index.column() == 2:
                 # Retorna o preço como um número decimal
                return round(float(produto.preco),2)
            elif index.column() == 3:
                return produto.codigo_barras
            elif index.column() == 4:
                return 'Sim' if produto.disponivel else 'Não'
            elif index.column() == 5:
                return 'EDITAR' #QUERO Q ESSE EDITAR SEJA um botão q abrira uma tela para q eu possa editar o produto
        
        elif role == Qt.TextAlignmentRole:
            if index.column() == 5:
                return QVariant(Qt.AlignCenter)
            
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            headers = ['ID', 'Nome do Produto', 'Preço', 'Código de Barras', 'Disponível', "Editar"]
            if orientation == Qt.Horizontal:
                return headers[section]
        return QVariant()

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()

        # Converta ModelSelect para lista, se necessário
        if hasattr(self.produtos, 'select'):
            self.produtos = list(self.produtos)

        # Verifique se self.produtos é uma lista e ordene
        if isinstance(self.produtos, list):
            key_func = {
                0: lambda p: p.id,
                1: lambda p: p.nome,
                2: lambda p: p.preco,
                3: lambda p: p.codigo_barras,
                4: lambda p: p.disponivel,
            }[column]

            self.produtos.sort(key=key_func, reverse=(order == Qt.DescendingOrder))

            self.layoutChanged.emit()
        else:
            print(f"Erro: self.produtos não é uma lista. Ele é do tipo {type(self.produtos)}")

class ProductView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setLayout(QVBoxLayout())

        # Filtros e botão de atualização
        self.filter_layout = QHBoxLayout()
        self.layout().addLayout(self.filter_layout)

        # Campos de filtro para cada coluna
        self.id_filter_label = QLabel('Filtrar por ID:')
        self.filter_layout.addWidget(self.id_filter_label)
        self.id_filter_input = QLineEdit(self)
        self.id_filter_input.textChanged.connect(self.filter_table)
        self.filter_layout.addWidget(self.id_filter_input)

        self.name_filter_label = QLabel('Filtrar por Nome:')
        self.filter_layout.addWidget(self.name_filter_label)
        self.name_filter_input = QLineEdit(self)
        self.name_filter_input.textChanged.connect(self.filter_table)
        self.filter_layout.addWidget(self.name_filter_input)

        self.price_filter_label = QLabel('Filtrar por Preço:')
        self.filter_layout.addWidget(self.price_filter_label)
        self.price_filter_input = QLineEdit(self)
        self.price_filter_input.textChanged.connect(self.filter_table)
        self.filter_layout.addWidget(self.price_filter_input)

        self.barcode_filter_label = QLabel('Filtrar por Código de Barras:')
        self.filter_layout.addWidget(self.barcode_filter_label)
        self.barcode_filter_input = QLineEdit(self)
        self.barcode_filter_input.textChanged.connect(self.filter_table)
        self.filter_layout.addWidget(self.barcode_filter_input)

        self.available_filter_label = QLabel('Filtrar por Disponível:')
        self.filter_layout.addWidget(self.available_filter_label)
        self.available_filter_input = QLineEdit(self)
        self.available_filter_input.textChanged.connect(self.filter_table)
        self.filter_layout.addWidget(self.available_filter_input)

        self.refresh_button = QPushButton('Atualizar Lista')
        self.refresh_button.clicked.connect(self.load_products)
        
        
        self.filter_layout.addWidget(self.refresh_button)

        # Tabela de produtos
        self.product_table = QTableView()
        self.layout().addWidget(self.product_table)

        self.product_filter_proxy_model = ProductFilterProxyModel()

        
        # Botão de edição
        self.add_button = QPushButton('Adicionar Produto')
        self.add_button.clicked.connect(self.open_add_product_form)
        self.layout().addWidget(self.add_button)
        
        self.load_products()  # Carregar produtos ao inicializar

        self.product_table.doubleClicked.connect(self.handle_double_click)

    def open_add_product_form(self):
        self.add_product_form = ProductForm(self)
        self.add_product_form.exec_()

    def open_edit_product_form(self, produto):
        # Abre o formulário de edição com os detalhes do produto
        self.edit_product_form = EditProductForm(produto, self)
        self.edit_product_form.exec_()
        
    def load_products(self):
        relatorios = Relatorios()
        produtos = relatorios.gerar_relatorio_produtos()

        # Criar e configurar o modelo de dados
        self.product_model = ProductTableModel(produtos)
        self.product_filter_proxy_model.setSourceModel(self.product_model)
        self.product_table.setModel(self.product_filter_proxy_model)

        # Permitir ordenação
        self.product_table.setSortingEnabled(True)
        self.product_table.setTabKeyNavigation(True)

        # Ajustar a largura das colunas
        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)


    def handle_double_click(self, index):
        if index.column() == 5:  # Verifica se a coluna clicada é a coluna "EDITAR"
            # Obtenha o índice do modelo filtrado
            proxy_index = index

            # Converta o índice do modelo filtrado para o índice do modelo de origem
            source_index = self.product_filter_proxy_model.mapToSource(proxy_index)

            # Obtenha o produto correspondente do modelo original
            produto = self.product_model.produtos[source_index.row()]

            # Abra o formulário de edição com os detalhes do produto
            self.open_edit_product_form(produto)
            
    def filter_table(self):
        self.product_filter_proxy_model.set_filter_id(self.id_filter_input.text())
        self.product_filter_proxy_model.set_filter_name(self.name_filter_input.text())
        self.product_filter_proxy_model.set_filter_price(self.price_filter_input.text())
        self.product_filter_proxy_model.set_filter_barcode(self.barcode_filter_input.text())
        self.product_filter_proxy_model.set_filter_available(self.available_filter_input.text())

class EditProductForm(QDialog):
    def __init__(self, produto, parent=None):
        super().__init__(parent)
        self.produto = produto
        # Armazenar uma cópia dos dados originais do produto
        self.original_data = {
            'nome': produto.nome,
            'preco': produto.preco,
            'codigo_barras': produto.codigo_barras,
            'disponivel': produto.disponivel
        }
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Editar Produto')
        self.setLayout(QVBoxLayout())

        
        self.id_label = QLabel(f'ID: {self.produto.id}')
        self.nome_input = QLineEdit(self.produto.nome)
        self.preco_input = QLineEdit(f'{self.produto.preco:.2f}')
        self.codigo_barras_input = QLineEdit(self.produto.codigo_barras)
        self.disponivel_checkbox = QCheckBox('Disponível')
        self.disponivel_checkbox.setChecked(self.produto.disponivel)


        self.price_validator = QDoubleValidator(0.0, 1e6, 2, self)
        self.price_validator.setNotation(QDoubleValidator.StandardNotation)
        self.preco_input.setValidator(self.price_validator)
        
        self.save_button = QPushButton('Salvar')
        self.save_button.clicked.connect(self.save_changes)

        self.cancel_button = QPushButton('Cancelar')
        self.cancel_button.clicked.connect(self.reject)

        self.layout().addWidget(self.id_label)
        self.layout().addWidget(QLabel('Nome:'))
        self.layout().addWidget(self.nome_input)
        self.layout().addWidget(QLabel('Preço:'))
        self.layout().addWidget(self.preco_input)
        self.layout().addWidget(QLabel('Código de Barras:'))
        self.layout().addWidget(self.codigo_barras_input)
        self.layout().addWidget(self.disponivel_checkbox)
        self.layout().addWidget(self.save_button)
        self.layout().addWidget(self.cancel_button)

    def save_changes(self):
        try:
            nome = self.nome_input.text().strip()
            preco_text = self.preco_input.text().strip()
            codigo_barras = self.codigo_barras_input.text().strip()
            disponivel = self.disponivel_checkbox.isChecked()

            if not nome or not preco_text or not codigo_barras:
                QMessageBox.warning(self, 'Erro', 'Preencha todos os campos!')
                return

            try:
                if Decimal(preco_text.replace(',', '.')) < 0:
                    QMessageBox.warning(self, 'Erro', 'Preço inválido! Deve ser um valor maior do que 0.')
                    return
                else:
                    preco = Decimal(preco_text.replace(',', '.'))
            except ValueError:
                QMessageBox.warning(self, 'Erro', 'Preço inválido! Deve ser um número válido.')
                return

            # Atualizar os atributos do produto
            self.produto.nome = nome
            self.produto.preco = preco
            self.produto.codigo_barras = codigo_barras
            self.produto.disponivel = disponivel
            self.produto.save()

            QMessageBox.information(self, 'Sucesso', 'Produto atualizado com sucesso!')
            self.accept()

            # Atualizar a listagem de produtos
            self.parent().load_products()
            
        except Exception as e:
            # Reverter os dados no formulário se houver erro
            self.produto.nome = self.original_data['nome']
            self.produto.preco = self.original_data['preco']
            self.produto.codigo_barras = self.original_data['codigo_barras']
            self.produto.disponivel = self.original_data['disponivel']
            
            if 'UNIQUE constraint failed' in str(e):
                QMessageBox.warning(self, 'Erro', 'Erro ao atualizar produto: Já existe um produto com esse nome ou código de barras cadastrado!')
            else:
                QMessageBox.critical(self, 'Erro', f'Erro ao atualizar produto: {str(e)}')
  
class ProductForm(QDialog):
    def __init__(self, parent=None, product_list_widget=None):
        super().__init__(parent)
        self.product_list_widget = product_list_widget
        self.initUI()

    def initUI(self):
        self.setLayout(QVBoxLayout())

        self.name_label = QLabel('Nome:')
        self.layout().addWidget(self.name_label)
        self.name_input = QLineEdit(self)
        self.layout().addWidget(self.name_input)

        self.price_label = QLabel('Preço:')
        self.layout().addWidget(self.price_label)
        self.price_input = QLineEdit(self)
        self.layout().addWidget(self.price_input)
        
        self.price_validator = QDoubleValidator(0.0, 1e6, 2, self)
        self.price_validator.setNotation(QDoubleValidator.StandardNotation)
        self.price_input.setValidator(self.price_validator)
        
        self.barcode_label = QLabel('Código de Barras:')
        self.layout().addWidget(self.barcode_label)
        self.barcode_input = QLineEdit(self)
        self.layout().addWidget(self.barcode_input)

        self.save_button = QPushButton('Salvar')
        self.save_button.clicked.connect(self.save_product)
        self.layout().addWidget(self.save_button)

    def save_product(self):
        nome = self.name_input.text().strip()
        preco_text = self.price_input.text().strip()
        codigo_barras = self.barcode_input.text().strip()

        if not nome or not preco_text or not codigo_barras:
            QMessageBox.warning(self, 'Erro', 'Preencha todos os campos!')
            return

        # Validação do preço
        try:
            if Decimal(preco_text.replace(',', '.')) < 0:
                QMessageBox.warning(self, 'Erro', 'Preço inválido! Deve ser um valor maior do que 0.')
                return
            else:
                preco = Decimal(preco_text.replace(',', '.'))
        except ValueError:
            QMessageBox.warning(self, 'Erro', 'Preço inválido!')
            return

        # Validar código de barras com expressão regular (opcional)
        if not re.match(r'^\d+$', codigo_barras):
            QMessageBox.warning(self, 'Erro', 'Código de barras inválido!')
            return

        try:
            Produto.create(nome=nome, preco=preco, codigo_barras=codigo_barras)
            QMessageBox.information(self, 'Sucesso', f'Produto {nome} registrado!')
            
            # Atualizar a listagem de produtos
            self.parent().load_products()
                
            self.name_input.clear()
            self.price_input.clear()
            self.barcode_input.clear()
            
        except IntegrityError as e:
            # Tratar especificamente a exceção de integridade, como a violação de unicidade
            if 'UNIQUE constraint failed' in str(e):
                QMessageBox.warning(self, 'Erro', 'Código de barras já cadastrado!')
            else:
                self.show_error_message(f"Erro ao salvar produto: {str(e)}")
        except Exception as e:
            self.show_error_message(f"Erro ao salvar produto: {str(e)}")
            
    def show_error_message(self, message):
        QMessageBox.critical(self, 'Erro', message)

class DeleteProductForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setLayout(QVBoxLayout())

        self.id_label = QLabel('ID do Produto para Exclusão:')
        self.layout().addWidget(self.id_label)
        self.id_input = QLineEdit(self)
        self.layout().addWidget(self.id_input)

        self.delete_button = QPushButton('Excluir Produto')
        self.delete_button.clicked.connect(self.delete_product)
        self.layout().addWidget(self.delete_button)

    def delete_product(self):
        try:
            id = int(self.id_input.text())
            Produto.excluir_produto(id=id)
            self.parent().load_products()
        except Exception as e:
            self.parent().show_error_message(f"Erro ao excluir produto: {str(e)}")
