import pdfplumber
import sys
import json
import os
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTableWidget, QVBoxLayout, QLabel,
    QPushButton, QHeaderView, QHBoxLayout, QMessageBox, QFileDialog, QDialog,
    QProgressDialog, QMenuBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont

# Logging configurations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('schedule_app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


def handle_exception(exc_type, exc_value, exc_traceback):
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_exception


def get_icon_path():
    possible_paths = [
        "calendar_icon.ico",
        "calendar_icon.png",
        os.path.join(os.path.dirname(__file__), "calendar_icon.ico"),
        os.path.join(os.path.dirname(__file__), "resources", "calendar_icon.ico"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return ""


def get_config_dir():
    if os.name == 'nt':
        config_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'ScheduleManager')
    else:
        config_dir = os.path.expanduser('~/.config/schedulemanager')
    os.makedirs(config_dir, exist_ok=True)
    return config_dir


# Course details dialog
class CourseDetailsWindow(QDialog):
    def __init__(self, course_data, course_index, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Course Details')
        self.setGeometry(700, 400, 400, 300)

        layout = QVBoxLayout(self)

        def safe_get(data, idx):
            try:
                return data[idx][course_index]
            except (IndexError, KeyError, TypeError):
                return ""

        course_code = QLabel(f"Course Code: {safe_get(course_data, 0)}")
        course_name = QLabel(f"Course Name: {safe_get(course_data, 1)}")
        credits_label = QLabel(f"Credits: {safe_get(course_data, 2)}")
        section = QLabel(f"Section: {safe_get(course_data, 4)}")
        activity = QLabel(f"Activity: {safe_get(course_data, 13)}")
        building = QLabel(f"Building: {safe_get(course_data, 11)}")
        room = QLabel(f"Room: {safe_get(course_data, 12)}")
        staff = QLabel(f"Staff: {safe_get(course_data, 20)}")

        for label in [course_code, course_name, credits_label, section, activity, building, room, staff]:
            label.setFont(QFont("Arial", 10))
            layout.addWidget(label)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)


# PDF extraction
def extract_from_pdf(pdf_path):
    if not pdf_path or not os.path.exists(pdf_path):
        logging.error(f"PDF file not found: {pdf_path}")
        return None

    # Lists for course data
    extracted_course_codes = []
    extracted_courses = []
    extracted_cr = []
    extracted_ct = []
    extracted_sec = []
    extracted_seq = []
    extracted_activity = []
    extracted_sun_periods = []
    extracted_mon_periods = []
    extracted_tue_periods = []
    extracted_wed_periods = []
    extracted_thu_periods = []
    extracted_building = []
    extracted_room = []
    extracted_staff = []

    # Student info variables
    stu_id = ""
    stu_name = ""
    advisor = ""
    department = ""
    major = ""
    semester = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) == 0:
                logging.error("PDF contains no pages")
                return None

            # Extracting the student info
            first_page = pdf.pages[0]
            text = first_page.extract_text() or ""

            lines = text.split('\n')

            for line in lines:
                line_clean = line.strip()

                if 'Department :' in line_clean and 'Classification :' in line_clean:
                    if 'Department :' in line_clean:
                        name_part = line_clean.split('Department :')[0].strip()
                        stu_name = name_part

                    if 'Department :' in line_clean and 'Classification :' in line_clean:
                        dept_part = line_clean.split('Department :')[1].split('Classification :')[0].strip()
                        department = dept_part

                elif 'Major :' in line_clean and 'Stream :' in line_clean:
                    if 'Major :' in line_clean:
                        id_part = line_clean.split('Major :')[0].strip()
                        stu_id = id_part

                    if 'Major :' in line_clean and 'Stream :' in line_clean:
                        major_part = line_clean.split('Major :')[1].split('Stream :')[0].strip()
                        major = major_part

                elif 'Semester :' in line_clean:
                    sem_part = line_clean.split('Semester :')[1].strip()
                    semester = sem_part

            # Extracting schedule tables
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if not tables:
                    continue

                for table in tables:
                    if not table or len(table) < 3:
                        continue

                    for row_idx, row in enumerate(table):
                        if not row or len(row) < 10:
                            continue

                        row_text = ' '.join([str(cell) for cell in row if cell])
                        if any(header in row_text.lower() for header in ['course code', 'course name', 'cr']):
                            continue

                        if all(cell is None or str(cell).strip() == "" for cell in row):
                            continue

                        row_extended = list(row) + [""] * max(0, 15 - len(row))

                        if row_extended[0] and str(row_extended[0]).strip():
                            extracted_course_codes.append(row_extended[0] or "")
                            extracted_courses.append(row_extended[1] or "")
                            extracted_cr.append(row_extended[2] or "")
                            extracted_ct.append(row_extended[3] or "")
                            extracted_sec.append(row_extended[4] or "")
                            extracted_seq.append(row_extended[5] or "")
                            extracted_activity.append(row_extended[6] or "")
                            extracted_sun_periods.append(row_extended[7] or "")
                            extracted_mon_periods.append(row_extended[8] or "")
                            extracted_tue_periods.append(row_extended[9] or "")
                            extracted_wed_periods.append(row_extended[10] or "")
                            extracted_thu_periods.append(row_extended[11] or "")
                            extracted_building.append(row_extended[12] or "")
                            extracted_room.append(row_extended[13] or "")
                            extracted_staff.append(row_extended[14] or "")

        # Validate & return data
        meaningful_courses = [code for code in extracted_course_codes if code and str(code).strip()]

        if not meaningful_courses and not stu_name:
            logging.warning("No meaningful course data or student name found - PDF may not be a valid schedule")
            QMessageBox.warning(None, "No Data Found",
                                 "No schedule data could be extracted from the PDF.\n"
                                 "Please make sure it contains a valid student schedule.")
            return None

        extracted_tables = [
            extracted_course_codes, extracted_courses, extracted_cr, extracted_ct, extracted_sec,
            extracted_seq, extracted_sun_periods, extracted_mon_periods, extracted_tue_periods,
            extracted_wed_periods, extracted_thu_periods, extracted_building, extracted_room,
            extracted_activity, stu_id, stu_name, advisor, department, major, semester, extracted_staff
        ]

        return extracted_tables

    except (pdfplumber.PDFSyntaxError, IOError, OSError):
        logging.exception("Error reading PDF")
        return None

def extract_from_pdf_with_progress(pdf_path, parent=None):
    progress = QProgressDialog("Extracting schedule data...", "Cancel", 0, 100, parent)
    progress.setWindowTitle("Processing PDF")
    progress.setWindowModality(Qt.WindowModal)
    progress.setValue(0)
    progress.show()
    QApplication.processEvents()
    try:
        progress.setValue(20)
        QApplication.processEvents()
        result = extract_from_pdf(pdf_path)
        progress.setValue(100)
        QApplication.processEvents()
        return result
    except (ValueError, TypeError):
        logging.error("Progress extraction failed")
        raise
    finally:
        progress.close()


# Main Application Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Schedule Manager')
        self.setGeometry(600, 350, 700, 520)

        icon_path = get_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        else:
            logging.warning("Application is running without icon")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Student Info Labels
        self.label1 = QLabel('Student ID: ')
        self.label2 = QLabel('Student Name: ')
        self.label3 = QLabel('Advisor: ')
        self.label4 = QLabel('Department: ')
        self.label5 = QLabel('Major: ')
        self.label6 = QLabel('Semester: ')
        font = QFont("Times New Roman", 11)
        for labl in [self.label1, self.label2, self.label3, self.label4, self.label5, self.label6]:
            labl.setFont(font)

        labels_layout = QHBoxLayout()
        left_labels = QVBoxLayout()
        right_labels = QVBoxLayout()
        left_labels.addWidget(self.label2)
        left_labels.addWidget(self.label1)
        left_labels.addWidget(self.label3)
        right_labels.addWidget(self.label4)
        right_labels.addWidget(self.label5)
        right_labels.addWidget(self.label6)
        labels_layout.addLayout(left_labels)
        labels_layout.addLayout(right_labels)
        layout.addLayout(labels_layout)

        # The Schedule Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setRowCount(15)
        self.table.setHorizontalHeaderLabels(['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday'])
        self.table.setVerticalHeaderLabels(
            ['7:00', '8:00', '9:00', '10:00', '11:00', '12:20',
             '1:20', '2:20', '3:30', '4:30', '5:30', '6:30', '7:30', '8:30', '9:30']
        )
        h_header = self.table.horizontalHeader()
        h_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        v_header = self.table.verticalHeader()
        v_header.setMinimumSectionSize(90)
        v_header.setDefaultSectionSize(90)
        layout.addWidget(self.table)

        # Load PDF Button
        btn_layout = QHBoxLayout()
        load_pdf_btn = QPushButton("📂 Choose Your Schedule File")
        load_pdf_btn.clicked.connect(self.choose_pdf_file)
        btn_layout.addStretch()
        btn_layout.addWidget(load_pdf_btn)
        layout.addLayout(btn_layout)

        # Menu Bar
        menubar = self.menuBar()
        help_menu = menubar.addMenu('Help')
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                padding: 6px;
                border: none;
                color: white;
            }
            QTableWidget {
                gridline-color: #444;
                selection-background-color: #3a86ff;
                selection-color: white;
            }
            QPushButton {
                background-color: #3a86ff;
                border: none;
                border-radius: 8px;
                padding: 8px 14px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2663d3;
            }
            QLabel {
                color: white;
            }
        """)

        self.course_window = None
        self.current_courses = None

    # Load last used PDF
    def load_initial_schedule(self):
        last_pdf_path = load_last_pdf_path()
        if last_pdf_path and os.path.exists(last_pdf_path):
            logging.info("Loading last used PDF file")
            courses_data = extract_from_pdf_with_progress(last_pdf_path, self)
            if courses_data:
                self.current_courses = courses_data
                self.update_labels(courses_data)
                self.populate_schedule(courses_data)
                return True
            else:
                logging.warning("Failed to extract data from last PDF file")
        return False

    # Update th student info labels
    def update_labels(self, courses_data):
        try:
            def safe_item(data, idx, default=""):
                try:
                    value = data[idx]
                    if isinstance(value, str):
                        if 'Major :' in value and 'Stream :' in value:
                            value = value.split('Major :')[0].strip()
                        elif 'Department :' in value and 'Classification :' in value:
                            value = value.split('Department :')[0].strip()
                        elif 'Semester :' in value:
                            value = value.split('Semester :')[1].strip()
                    return value if value else default
                except (IndexError, KeyError, TypeError):
                    return default

            if isinstance(courses_data, list) and len(courses_data) >= 20:
                student_id = safe_item(courses_data, 14, "")
                student_name = safe_item(courses_data, 15, "")
                advisor = safe_item(courses_data, 16, "")
                department = safe_item(courses_data, 17, "")
                major = safe_item(courses_data, 18, "")
                semester = safe_item(courses_data, 19, "")
            else:
                student_id = student_name = advisor = department = major = semester = ""

            if 'Major :' in str(student_id):
                student_id = str(student_id).split('Major :')[0].strip()
            if 'Department :' in str(student_name):
                student_name = str(student_name).split('Department :')[0].strip()
            if 'Semester :' in str(semester):
                semester = str(semester).split('Semester :')[1].strip()

            self.label1.setText(f'Student ID: {student_id}')
            self.label2.setText(f'Student Name: {student_name}')
            self.label3.setText(f'Advisor: {advisor}')
            self.label4.setText(f'Department: {department}')
            self.label5.setText(f'Major: {major}')
            self.label6.setText(f'Semester: {semester}')


        except (IndexError, TypeError, AttributeError):
            logging.exception("Error updating labels")

    # Filling the schedule table
    def populate_schedule(self, courses_data):
        try:
            for r in range(self.table.rowCount()):
                for c in range(self.table.columnCount()):
                    self.table.removeCellWidget(r, c)

            count_col = 0
            for day_index in range(6, 11):
                if not isinstance(courses_data, list) or day_index >= len(courses_data):
                    count_col += 1
                    continue
                for i, row_data in enumerate(courses_data[day_index]):
                    if not row_data:
                        continue
                    for period in str(row_data).split(','):
                        period = period.strip()
                        if not period.isdigit():
                            continue
                        period_num = int(period)
                        course = QWidget()
                        main_layout = QVBoxLayout(course)
                        content_layout = QVBoxLayout()

                        try:
                            activity_text = courses_data[13][i] if len(courses_data) > 13 and i < len(
                                courses_data[13]) else ""
                            name_text = courses_data[1][i] if len(courses_data) > 1 and i < len(courses_data[1]) else ""
                            building_text = courses_data[11][i] if len(courses_data) > 11 and i < len(
                                courses_data[11]) else ""
                            room_text = courses_data[12][i] if len(courses_data) > 12 and i < len(
                                courses_data[12]) else ""
                        except (IndexError, KeyError, TypeError):
                            activity_text = name_text = building_text = room_text = ""

                        course_activity = QLabel(activity_text)
                        course_name = QLabel(name_text)
                        course_location = QLabel(f"{building_text} {room_text}".strip())

                        course_name.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: bold;")
                        course_activity.setStyleSheet("color: white; font-size: 11px;")
                        course_location.setStyleSheet("color: #E8E8E8; font-size: 11px;")

                        course_activity.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        course_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        course_location.setAlignment(Qt.AlignmentFlag.AlignCenter)

                        content_layout.addWidget(course_name)
                        content_layout.addWidget(course_activity)
                        content_layout.addWidget(course_location)
                        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

                        button_layout = QHBoxLayout()
                        button_layout.addStretch()

                        info_btn = QPushButton("i")
                        info_btn.setToolTip("View course details")
                        info_btn.setFixedSize(22, 22)
                        info_btn.setStyleSheet("""
                            QPushButton {
                                background-color: rgba(255,255,255,0.15);
                                color: white;
                                font-weight: bold;
                                border: 1px solid rgba(255,255,255,0.7);
                                border-radius: 11px;
                                font-size: 12px;
                            }
                            QPushButton:hover {
                                background-color: rgba(255,255,255,0.35);
                            }
                        """)

                        def make_handler(course_idx):
                            return lambda checked: self.show_course_details(courses_data, course_idx)

                        info_btn.clicked.connect(make_handler(i))
                        button_layout.addWidget(info_btn)

                        main_layout.addLayout(content_layout)
                        main_layout.addLayout(button_layout)
                        main_layout.setContentsMargins(5, 5, 5, 5)
                        course.setLayout(main_layout)

                        course_colors = [
                            "#3FA47A", "#2C3E91", "#C99820", "#8C2F39", "#5C3A8D",
                            "#287D82", "#C65D2E", "#364F6B", "#2E7D4F", "#A44A6E",
                            "#B1761B", "#3B7C88", "#633974"
                        ]
                        color = course_colors[i % len(course_colors)]
                        course.setStyleSheet(f"background-color: {color}; border-radius: 8px;")

                        if 1 <= period_num <= self.table.rowCount():
                            if course is not None:
                                self.table.setCellWidget(period_num - 1, count_col, course)
                count_col += 1

            logging.info("Schedule populated successfully")
        except (IndexError, TypeError, AttributeError):
            logging.exception("Error populating schedule")
            QMessageBox.critical(self, "Error", "Failed to populate schedule (see log).")

    # course details dialog
    def show_course_details(self, course_data, course_index):
        try:
            if self.course_window and self.course_window.isVisible():
                self.course_window.close()
            self.course_window = CourseDetailsWindow(course_data, course_index, self)
            self.course_window.show()
        except (AttributeError, TypeError):
            logging.exception("Error showing course details")
            QMessageBox.critical(self, "Error", "Failed to show course details (see log).")

    def changeEvent(self, event):
        if event.type() == event.Type.WindowStateChange:
            self.update_table_row_heights()
        super().changeEvent(event)

    def update_table_row_heights(self):
        try:
            v_header = self.table.verticalHeader()
            if self.isMaximized():
                v_header.setSectionResizeMode(QHeaderView.ResizeMode.Custom)
                for row in range(self.table.rowCount()):
                    self.table.setRowHeight(row, 120)
            else:
                v_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        except AttributeError:
            logging.exception("Error updating table row heights")

    # Handling the PDF selection
    def choose_pdf_file(self):
        try:
            selected_file_path, _ = QFileDialog.getOpenFileName(self, "Select Schedule PDF", "", "PDF Files (*.pdf)")
            if selected_file_path:
                new_courses = extract_from_pdf_with_progress(selected_file_path, self)
                if new_courses:
                    self.current_courses = new_courses
                    self.update_labels(new_courses)
                    self.populate_schedule(new_courses)
                    save_last_pdf_path(selected_file_path)
                    logging.info("Successfully loaded new PDF file")
                else:
                    QMessageBox.warning(self, "Error",
                                         "Could not extract data from this PDF file.\nPlease make sure it's a valid Schedule PDF.")
        except (ValueError, TypeError, OSError):
            logging.exception("Error in choose_pdf_file")
            QMessageBox.critical(self, "Error", "An unexpected error occurred while choosing the PDF file.")

    def show_about(self):
        dlg = AboutDialog(self)
        dlg.exec()


def save_last_pdf_path(file_path):
    config_dir = get_config_dir()
    config_file = os.path.join(config_dir, "config.json")
    config_data = {
        "last_pdf_path": file_path,
        "version": "1.0.0",
    }
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
        logging.info("Configuration saved successfully")
    except (IOError, OSError, json.JSONEncodeError):
        logging.exception("Failed to save configuration")


def load_last_pdf_path():
    config_file = os.path.join(get_config_dir(), "config.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                path = config_data.get("last_pdf_path", "")
                if path and os.path.exists(path):
                    logging.info(f"Loaded last PDF path: {path}")
                    return path
        except (json.JSONDecodeError, IOError, OSError):
            logging.exception("Error loading configuration")
    return ""


# main
def main():
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Schedule Manager")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Jawad")

        logging.info("Schedule Manager application starting...")

        window = MainWindow()

        if not window.load_initial_schedule():
            logging.info("No previous schedule found, prompting for PDF file")
            default_file_path, _ = QFileDialog.getOpenFileName(None, "Select Schedule PDF", "", "PDF Files (*.pdf)")
            if default_file_path:
                loaded_courses = extract_from_pdf_with_progress(default_file_path, window)
                if loaded_courses:
                    window.current_courses = loaded_courses
                    window.update_labels(loaded_courses)
                    window.populate_schedule(loaded_courses)
                    save_last_pdf_path(default_file_path)
                else:
                    logging.warning("Initial PDF extraction failed")

        window.show()
        logging.info("Application window shown successfully")

        return app.exec()
    except (SystemExit, KeyboardInterrupt):
        return 0
    except (ValueError, TypeError, RuntimeError):
        logging.exception("Application failed to start")
        QMessageBox.critical(None, "Fatal Error",
                             "The application encountered a fatal error and must close.\n"
                             "See schedule_app.log for details.")
        return 1

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Schedule Manager")
        self.setFixedSize(300, 200)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Schedule Manager"))
        layout.addWidget(QLabel("Version 1.0.0"))
        layout.addWidget(QLabel("University Schedule Management App"))
        layout.addWidget(QLabel("© 2025 Juad Al-Mrhoon"))
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

if __name__ == "__main__":
    sys.exit(main())