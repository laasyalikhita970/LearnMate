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
        self.mode = "home"
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
        flashcard_btn = QPushButton("Flashcards")
        # Button Connections
        dashboard_btn.clicked.connect(self.read_current_pdf)
        upload_btn.clicked.connect(self.upload_pdf)
        summary_btn.clicked.connect(self.summarize_pdf)
        flashcard_btn.clicked.connect(self.generate_flashcards)
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
        sidebar.addWidget(flashcard_btn)
        sidebar.addStretch()

        # Content Area
        self.content = QTextEdit()
        self.content.setReadOnly(True)
        self.content.setStyleSheet("""
            font-size: 14px;
            padding: 10px;
        """)
        self.content.setReadOnly(True)
        self.content.setText("Welcome to LearnMate")

        main_layout.addLayout(sidebar, 1)
        main_layout.addWidget(self.content, 4)

        self.setLayout(main_layout)

    # ----------------------------------
    # Change Page
    # ----------------------------------

    def change_page(self, text):
        self.mode = "home"
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
        self.mode = "library"
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
        self.mode = "pdf"
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

        self.mode = "summary"

        if not self.current_pdf:
            self.content.setText("Please upload a PDF first.")
            return

        try:
            doc = fitz.open(self.current_pdf)

            text = ""
            for page in doc:
                text += page.get_text()

            doc.close()

            if not text.strip():
                self.content.setText("No text found in PDF.")
                return

            # ----------------------------
            # SMART CLEANING
            # ----------------------------

            sentences = text.split(".")

            # Remove empty + very short sentences
            cleaned = []
            for s in sentences:
                s = s.strip()
                if len(s) > 40:
                    cleaned.append(s)

            # Score sentences (simple keyword scoring)
            keywords = ["is", "are", "was", "important", "definition", "system", "data", "process"]

            scored = []

            for s in cleaned:
                score = 0
                lower = s.lower()

                for k in keywords:
                    if k in lower:
                        score += 1

                scored.append((score, s))

            # Sort by importance
            scored.sort(reverse=True)

            # Take top sentences
            top_sentences = [s for _, s in scored[:5]]

            summary = ""

            for s in top_sentences:
                summary += "• " + s + ".\n\n"

            self.content.setText("SMART SUMMARY\n\n" + summary)

        except Exception as e:
            self.content.setText(f"Error: {str(e)}")
    def generate_flashcards(self):

            self.mode = "flashcards"

            if not self.current_pdf:
                self.content.setText("Please upload a PDF first.")
                return

            try:
                doc = fitz.open(self.current_pdf)

                text = ""
                for page in doc:
                    text += page.get_text()

                doc.close()

                if not text.strip():
                    self.content.setText("No text found in PDF.")
                    return

                sentences = text.split(".")

                # Clean sentences
                cleaned = []
                for s in sentences:
                    s = s.strip()
                    if len(s) > 40:
                        cleaned.append(s)

                # Take meaningful sentences only
                flashcards = []
                for s in cleaned:

                    words = s.split()
                    if len(words) < 8:
                        continue

                    # create better Q/A logic
                    key_part = " ".join(words[:5])
                    rest_part = " ".join(words[5:15])

                    question = f"What is {key_part}?"
                    answer = rest_part if rest_part else s

                    flashcards.append((question, answer))

                    if len(flashcards) == 6:
                        break

                output = "FLASHCARDS (SMART VERSION)\n\n"

                for i, (q, a) in enumerate(flashcards, 1):
                    output += f"Q{i}: {q}\n"
                    output += f"A{i}: {a}\n\n"

                self.content.setText(output)

            except Exception as e:
                self.content.setText(f"Error: {str(e)}")

# ----------------------------------
# Run App
# ----------------------------------

app = QApplication(sys.argv)

window = LearnMate()
window.show()

sys.exit(app.exec())