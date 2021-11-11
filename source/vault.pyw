import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from functools import partial
from util import Vault, CustomException
import pyperclip


class Window(QMainWindow, Vault):
    def __init__(self):
        self.key_set = False
        self.vault = None
        super().__init__()
        self._construct_main_window()
        
    def _construct_main_window(self):
        super().__init__()
        #Main window
        self.setWindowTitle('Vault')
        self.centralWidget = QWidget() 
        self.setCentralWidget(self.centralWidget)
        self.setGeometry(300, 300, 500, 500)

        #Central layout
        central_layout = QVBoxLayout()
        self.centralWidget.setLayout(central_layout)

        #Menu bar
        file, about = self.menuBar().addMenu("File"), self.menuBar().addMenu("About")
        file.addAction('New', self._create_new_vault_from_file)
        file.addAction('Exit', self.close)
        
        #Status bar
        self.status_bar = QStatusBar() #Set status_bar hook
        self.setStatusBar(self.status_bar)
        self.status_bar_message = QLabel()
        self.status_bar.addPermanentWidget(self.status_bar_message)
        
        #Text edit area
        self.text_edit = QTextEdit() #Set text_edit hook
        
        #Control buttons
        file_input_button = QPushButton("Open")
        save_button = QPushButton("Save")
        file_input_button.clicked.connect(self._open_existing_vault)
        save_button.clicked.connect(self._encrypt_and_save)

        #Button row
        button_row = QHBoxLayout()
        button_row.addWidget(file_input_button)
        button_row.addWidget(save_button)
        central_layout.addLayout(button_row)

        #Pack central layout
        central_layout.addWidget(self.text_edit)
        self.centralWidget.setLayout(central_layout)
    
    def _open_existing_vault(self):
        #Top level function that do not throw exceptions
        try:
            self.vault = self._open_file()
            if self.vault:
                self._passcode_prompt()
                self._decrypt_and_display(self.vault)
            else:
                self.vault = None
                self.key_set = False
        except BaseException:
            self.vault = None
            self.key_set = False

    def _open_file(self, file_type = "Vault Files (*.vault)"):

        file_dialog = QFileDialog()
        vault = file_dialog.getOpenFileName(self, "Open vault", "./vault", file_type)
        return vault[0] if vault else None
        
    def _passcode_prompt(self, fname = None):
    
        dialog = QDialog(parent = self.centralWidget)
        form_layout = QFormLayout()
        input_field = QLineEdit()
        input_field.setMinimumWidth(15)
        form_layout.addRow("Passcode" ,input_field)
        dialog.setWindowTitle("Enter passcode")
        btns = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        btnbox = QDialogButtonBox(btns)
        form_layout.addWidget(btnbox)
        dialog.setLayout(form_layout)
        dialog.setFixedSize(300, 70)

        def save_passcode():
            self.key = None
            text = input_field.text()
            if text:
                try:
                    e, d, N = self.parse_key(text)
                    self.set_keys(e, d, N)
                    self.key_set = True
                    dialog.close()
                except BaseException:
                    self.key_set = False

        btnbox.rejected.connect(dialog.close)
        btnbox.accepted.connect(save_passcode)
        
        response = dialog.exec_()

    def _decrypt_and_display(self, path):
        try:
            plain_text = self.read(path)
            self.text_edit.setText(plain_text)
            self.status_bar_message.setText(path)
        except BaseException:
            self.vault = None
            raise CustomException(f"Could not decrypt vault {path} ...")
    
    def _encrypt_and_save(self):
        
        if (self.key_set and self.vault):
            plain_text = self.text_edit.toPlainText()
            self.overwrite(plain_text, self.vault)
        else:
            try:
                #There is no current vault set and user wants to 
                #create new vault from the content of text edit
                data = self.text_edit.toPlainText()
                self.generate_keys()
                e, d, N = self.enc_pair[0], self.dec_pair[0], self.dec_pair[1]
                passcode = f"{e}-{d}-{N}"
                self._display_passcode(passcode)
                self.key_set = True
                vault = self._file_save_dialog()
                self.overwrite(data, vault)

            except BaseException as err:
                self.key_set = False
                self.vault = None

    def _create_new_vault_from_file(self):
        try:
            file_path = self._open_file(file_type = "Text Files (*.tsv *.csv *.txt)")
            if file_path:
                self.generate_keys()
                self.key_set = True
                e, d, N = self.enc_pair[0], self.dec_pair[0], self.dec_pair[1]
                passcode = f"{e}-{d}-{N}"
                self._display_passcode(passcode)
                self.create_from_file(file_path)
                self._decrypt_and_display(self.vault)
        except BaseException as err:
            self.vault = None
            self.key_set = False

    def _display_passcode(self, passcode):

        dialog = QDialog(parent = self.centralWidget)
        dialog.setWindowTitle("Passcode")
        layout = QHBoxLayout()
        label = QLabel()
        label.setText(passcode)
        copy_button = QPushButton("Copy")

        def f(passcode):
            pyperclip.copy(passcode)
            dialog.close()
        copy_and_close = partial(f, passcode)

        copy_button.clicked.connect(copy_and_close)
        layout.addWidget(label)
        layout.addWidget(copy_button)
        dialog.setLayout(layout)
        
        dialog.exec_()

    def _file_save_dialog(self):
        file_dialog = QFileDialog()
        vault = file_dialog.getSaveFileName(self, "Save file", "./vault", "Vault Files (*.vault)")
        if (vault):
            self.vault = vault[0]
            self.status_bar_message.setText(vault[0])
        else:
            raise CustomException("File was not saved...")
        
        return vault[0] if vault else None

if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon('icon.png'))
    window = Window()
    window.show()
    sys.exit(app.exec_())