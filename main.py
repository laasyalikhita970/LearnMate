import sys
import os
import shutil
import fitz

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QTextEdit,
    QHBoxLayout,
    QVBoxLayout,
    QFileDialog,
    QLabel
)

from PyQt6.QtCore import Qt


class LearnMate(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LearnMate")
        self.resize(1200, 700)

        self.current_pdf = None

        main_layout = QHBoxLayout()

        # Sidebar
        sidebar = QVBoxLayout()

        title = QLabel("LearnMate")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
        """)

        dashboard_btn = QPushButton("Dashboard")
        upload_btn = QPushButton("Upload PDF")
        summary_btn = QPushButton("Summarize PDF")
        subjects_btn = QPushButton("Subjects")
        notes_btn = QPushButton("Notes")
        settings_btn = QPushButton("Settings")

        # Button Connections
        dashboard_btn.clicked.connect(self.read_current_pdf)
        upload_btn.clicked.connect(self.upload_pdf)
        summary_btn.clicked.connect(self.summarize_pdf)

        subjects_btn.clicked.connect(
            lambda: self.change_page("Subjects Page")
        )

        notes_btn.clicked.connect(self.show_library)

        settings_btn.clicked.connect(
            lambda: self.change_page("Settings Page")
        )

        # Sidebar Layout
        sidebar.addWidget(title)
        sidebar.addWidget(dashboard_btn)
        sidebar.addWidget(upload_btn)
        sidebar.addWidget(summary_btn)
        sidebar.addWidget(subjects_btn)
        sidebar.addWidget(notes_btn)
        sidebar.addWidget(settings_btn)
        sidebar.addStretch()

        # Content Area
        self.content = QTextEdit()
        self.content.setReadOnly(True)
        self.content.setText("Welcome to LearnMate")

        main_layout.addLayout(sidebar, 1)
        main_layout.addWidget(self.content, 4)

        self.setLayout(main_layout)

    # ----------------------------------
    # Change Page
    # ----------------------------------

    def change_page(self, text):
        self.content.setText(text)

    # ----------------------------------
    # Upload PDF
    # ----------------------------------

    def upload_pdf(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF",
            "",
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        uploads_folder = "uploads"

        if not os.path.exists(uploads_folder):
            os.makedirs(uploads_folder)

        filename = os.path.basename(file_path)

        destination = os.path.join(
            uploads_folder,
            filename
        )

        shutil.copy(file_path, destination)

        self.current_pdf = destination

        self.content.setText(
            f"PDF Uploaded Successfully\n\n{filename}"
        )

    # ----------------------------------
    # Show Uploaded PDFs
    # ----------------------------------

    def show_library(self):

        uploads_folder = "uploads"

        if not os.path.exists(uploads_folder):
            self.content.setText(
                "No PDFs uploaded yet."
            )
            return

        files = os.listdir(uploads_folder)

        pdfs = [
            file for file in files
            if file.lower().endswith(".pdf")
        ]

        if not pdfs:
            self.content.setText(
                "No PDFs uploaded yet."
            )
            return

        text = "Uploaded PDFs\n\n"

        for pdf in pdfs:
            text += f"• {pdf}\n"

        self.content.setText(text)

    # ----------------------------------
    # Read Current PDF
    # ----------------------------------

    def read_current_pdf(self):

        if not self.current_pdf:
            self.content.setText(
                "Please upload a PDF first."
            )
            return

        try:

            doc = fitz.open(self.current_pdf)

            text = ""

            for page in doc:
                text += page.get_text()

            doc.close()

            if text.strip():
                self.content.setText(
                    text[:10000]
                )
            else:
                self.content.setText(
                    "PDF loaded successfully.\n\n"
                    "No extractable text found.\n\n"
                    "This PDF may be image-based."
                )

        except Exception as e:
            self.content.setText(
                f"Error:\n{str(e)}"
            )

    # ----------------------------------
    # Summarize PDF
    # ----------------------------------

    def summarize_pdf(self):

        if not self.current_pdf:
            self.content.setText(
                "Please upload a PDF first."
            )
            return

        try:

            doc = fitz.open(self.current_pdf)

            text = ""

            for page in doc:
                text += page.get_text()

            doc.close()

            if not text.strip():
                self.content.setText(
                    "No text found in PDF."
                )
                return

            sentences = text.split(".")

            summary = ""

            for sentence in sentences[:5]:
                sentence = sentence.strip()

                if sentence:
                    summary += sentence + ".\n\n"

            self.content.setText(
                "SUMMARY\n\n" + summary
            )

        except Exception as e:
            self.content.setText(
                f"Error:\n{str(e)}"
            )


# ----------------------------------
# Run App
# ----------------------------------

app = QApplication(sys.argv)

window = LearnMate()
window.show()

sys.exit(app.exec())