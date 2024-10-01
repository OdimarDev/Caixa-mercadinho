# relatorios_ui.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QLineEdit, QPushButton, QTableView, QFileDialog, QLabel, QDateEdit, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QAbstractTableModel, Qt, QDate
import pandas as pd
from entities import Relatorios


class DataFrameModel(QAbstractTableModel):
    def __init__(self, dataframe, parent=None):
        super().__init__(parent)
        self._dataframe = dataframe

    def rowCount(self, parent=None):
        return len(self._dataframe)

    def columnCount(self, parent=None):
        return len(self._dataframe.columns)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._dataframe.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(section + 1)
        return None


class RelatorioApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        
        # Layout principal
        self.layout.addWidget(QLabel('Tipo de Relatório:'))
        
        # ComboBox para seleção de tipo de relatório
        self.combo_tipo_relatorio = QComboBox()
        self.combo_tipo_relatorio.addItems([
            'Relatório de Produtos',
            'Relatório de Vendas do Dia',
            'Relatório de Vendas do Periodo',
            'Relatório de Itens de Venda',
            'Relatório de Movimentações de Caixa',
            'Relatório de Saldo'
        ])
        self.combo_tipo_relatorio.currentIndexChanged.connect(self.atualizar_ui_relatatorio)
        self.layout.addWidget(self.combo_tipo_relatorio)

        # Layout para filtros e data
        self.caixa_layout = QHBoxLayout()
        self.layout.addLayout(self.caixa_layout)

        # Campo de filtros
        self.input_filtros = QLineEdit()
        self.input_filtros.setPlaceholderText('Digite os filtros aqui (ex: nome=produto)')
        self.caixa_layout.addWidget(QLabel('Filtros:'))
        self.caixa_layout.addWidget(self.input_filtros)

        

        # Botão de gerar relatório
        self.button_gerar = QPushButton('Gerar Relatório')
        self.button_gerar.clicked.connect(self.gerar_relatorio)
        self.layout.addWidget(self.button_gerar)

        # Tabela para exibir o relatório
        self.table_view = QTableView()
        self.layout.addWidget(self.table_view)

        # Botão de exportar
        self.button_exportar = QPushButton('Exportar para CSV')
        self.button_exportar.clicked.connect(self.exportar_csv)
        self.layout.addWidget(self.button_exportar)

        self.df = pd.DataFrame()  # DataFrame para armazenar o relatório

    def atualizar_ui_relatatorio(self):
        tipo_relatorio = self.combo_tipo_relatorio.currentText()
        # Remove widgets antigos, se existirem
        for i in reversed(range(self.caixa_layout.count())): 
            widget = self.caixa_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
         # Recria o campo de filtros
        self.input_filtros = QLineEdit()  # Recriar o input_filtros
        self.input_filtros.setPlaceholderText('Digite os filtros aqui (ex: nome=produto)')
        self.caixa_layout.addWidget(QLabel('Filtros:'))
        self.caixa_layout.addWidget(self.input_filtros)
        # DataEdit
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        
        # DataEdit
        self.date_edit1 = QDateEdit()
        self.date_edit1.setCalendarPopup(True)
        self.date_edit1.setDate(QDate.currentDate())
        
        # DataEdit
        self.date_edit2 = QDateEdit()
        self.date_edit2.setCalendarPopup(True)
        self.date_edit2.setDate(QDate.currentDate())
        
        if tipo_relatorio == 'Relatório de Vendas do Dia':
            self.caixa_layout.addWidget(QLabel('Selecione a data:'))
            self.caixa_layout.addWidget(self.date_edit)
        if tipo_relatorio == 'Relatório de Vendas do Periodo':
            self.caixa_layout.addWidget(QLabel('Selecione a data Inicial:'))
            self.caixa_layout.addWidget(self.date_edit)
            self.caixa_layout.addWidget(QLabel('Selecione a data Final:'))
            self.caixa_layout.addWidget(self.date_edit2)
            

    def gerar_relatorio(self):
        tipo_relatorio = self.combo_tipo_relatorio.currentText()
        filtros = self.input_filtros.text()
        filtros_dict = self.parse_filtros(filtros)
        print(self.date_edit.text(),'------------------------')

        try:
            if tipo_relatorio == 'Relatório de Produtos':
                resultados = Relatorios.gerar_relatorio_produtos(**filtros_dict)
            elif tipo_relatorio == 'Relatório de Vendas do Dia':
                if 'data' in filtros_dict:
                    del filtros_dict['data']
                # Obter e imprimir a data selecionada no widget date_edit
                data_selecionada = self.date_edit.date().toString('yyyy-MM-dd')
                resultados = Relatorios.gerar_relatorio_vendas(**filtros_dict, data=data_selecionada )
            elif tipo_relatorio == 'Relatório de Vendas do Periodo':
                if 'data' in filtros_dict:
                    del filtros_dict['data']
                # Obter e imprimir a data selecionada no widget date_edit
                data_in = self.date_edit.date().toString('yyyy-MM-dd')
                data_fin = self.date_edit2.date().toString('yyyy-MM-dd')
                resultados = Relatorios.gerar_relatorio_vendas(**filtros_dict, data_inicial=data_in, data_final=data_fin)
            elif tipo_relatorio == 'Relatório de Itens de Venda':
                resultados = Relatorios.gerar_relatorio_itens_venda(**filtros_dict)
            elif tipo_relatorio == 'Relatório de Movimentações de Caixa':
                resultados = Relatorios.gerar_relatorio_movimentacoes(**filtros_dict)
            elif tipo_relatorio == 'Relatório de Saldo':
                resultados = Relatorios.gerar_relatorio_saldo()
    
                
            self.df = Relatorios.visualizar_relatorio(resultados)# Convertendo os resultados para um DataFrame
            # Verificar se as colunas 'disponivel' e 'cancelada' existem no DataFrame antes de tentar substituí-las
            if 'disponivel' in self.df.columns:
                self.df['disponivel'] = self.df['disponivel'].replace({True: "Sim", False: "Não"})

            if 'cancelada' in self.df.columns:
                self.df['cancelada'] = self.df['cancelada'].replace({True: "Sim", False: "Não"})
            # Verificar se o DataFrame não está vazio antes de tentar exibi-lo
            if not self.df.empty:
                self.table_view.setModel(DataFrameModel(self.df))
            else:
                print("O relatório está vazio.")
                self.mostrar_mensagem_erro("Nenhum dado encontrado para o relatório solicitado.")
        except IndexError as e:
            print(str(e),'\n---------------')
        except AttributeError as e:
            print(str(e))
            # Extrair a mensagem do erro e exibir uma mensagem mais amigável ao usuário
            atributo_erros = str(e).split("'")# Isso captura o nome do atributo do erro de AttributeError
            print(atributo_erros)
            atributo_erro = atributo_erros[-2]
            print(f"Erro: A categoria '{tipo_relatorio}' não possui o atributo '{atributo_erro}'.")
            
            # Exibir uma mensagem mais amigável ao usuário
            erro_msg = f"A categoria '{tipo_relatorio}' não possui o atributo '{atributo_erro}'."
            self.mostrar_mensagem_erro(erro_msg)  # Método para exibir mensagem ao usuário

        
        
    def parse_filtros(self, filtros):
        filtros_dict = {}
        for filtro in filtros.split(';'):
            if '=' in filtro:
                chave, valor = filtro.split('=', 1)
                filtros_dict[chave.strip()] = valor.strip()
        return filtros_dict

    def exportar_csv(self):
        if self.df.empty:
            print("Nenhum relatório gerado para exportar.")
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Salvar Relatório", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        if file_name:
            Relatorios.exportar_relatorio(self.df, file_name)
            print(f"Relatório exportado para {file_name}")

    def mostrar_mensagem_erro(self, mensagem):
        """Exibe uma mensagem de erro em um QLabel ou em uma MessageBox."""
        # Exibir a mensagem de erro em um QLabel, MessageBox, ou outro componente PyQt5
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(mensagem)
        msg_box.setWindowTitle("Erro")
        msg_box.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RelatorioApp()
    window.show()
    sys.exit(app.exec_())
