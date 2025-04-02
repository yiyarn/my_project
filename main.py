import sys
import cv2
import torch
import collections
from llm_module import analyze_with_llm, LLMQueryThread  # 从 LLM 模块中导入所需功能

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QHBoxLayout, QVBoxLayout, QWidget, QComboBox, QTextEdit, QSizePolicy, QLabel, QDialog, QScrollArea
from PySide6.QtCore import Qt, QEvent, QThread, Signal
from PySide6.QtGui import QImage, QPixmap, QPainter, QPalette, QColor, QMovie
from PySide6.QtCharts import QChart, QLineSeries, QScatterSeries, QBarCategoryAxis, QChartView, QValueAxis
from ui_mainwindow import Ui_MainWindow

from ultralytics import YOLO
from dehaze import *
from models import *

# 主窗口
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.OPENROUTER_API_KEY ="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"

        # 设置窗口背景颜色、大小
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#E6F0FA"))
        self.setPalette(palette)
        self.resize(1280, 720)

        # 加载 YOLO 模型、图片
        self.model_path = r"./model/yolov8n.pt"
        self.model = YOLO(self.model_path)
        self.gray_light = QPixmap("./images/gray_light.png")
        self.green_light = QPixmap("./images/green_light.png")
        self.yellow_light = QPixmap("./images/yellow_light.png")
        self.red_light = QPixmap("./images/red_light.png")
        default_image_path = "images/UAV.jpg"
        default_pixmap = QPixmap(default_image_path)
        if not default_pixmap.isNull():
            self.imageLabel.setPixmap(default_pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            print(f"无法加载默认图片：{default_image_path}")
        self.loading_label = QLabel(self.warningGroupBox)
        self.loading_label.setFixedSize(40, 40)
        self.loading_label.hide()
        self.loading_movie = QMovie("images/Spinner.gif")
        self.loading_movie.setScaledSize(self.loading_label.size())
        self.loading_label.setMovie(self.loading_movie)
        self.analysis_layout = QHBoxLayout()
        self.analysis_layout.addWidget(self.llmResultTextEdit)
        self.analysis_layout.addWidget(self.loading_label)
        self.warningLayout.addLayout(self.analysis_layout)
        self.imageLabel.installEventFilter(self)
        self.loadImageButton.clicked.connect(self.load_image)
        self.processButton.clicked.connect(self.process_image)
        self.quitButton.clicked.connect(self.quit_app)
        self.llmAnalysisButton.clicked.connect(self.analyze_with_llm)
        self.targetSelector.currentIndexChanged.connect(self.update_display)
        self.llmResultTextEdit.setReadOnly(True)
        self.llmResultTextEdit.setLineWrapMode(QTextEdit.WidgetWidth)
        self.llmResultTextEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.dehaze_model = None
        self.init_dehaze_model()

        # 美化按钮
        self.loadImageButton.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #dfdfea, stop: 1 #d5d5e0);
                color: #333333;
                font-size: 14px;
                padding: 8px 16px;
                border-radius: 8px;
                border: 1px solid #c5c5d0;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e9e9f4, stop: 1 #dfdfea);
            }
        """)
        self.processButton.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #c9cae1, stop: 1 #bfbfd7);
                color: #333333;
                font-size: 14px;
                padding: 8px 16px;
                border-radius: 8px;
                border: 1px solid #afafc7;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #d3d4eb, stop: 1 #c9cae1);
            }
        """)
        self.quitButton.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e3d8e6, stop: 1 #d9cedc);
                color: #333333;
                font-size: 14px;
                padding: 8px 16px;
                border-radius: 8px;
                border: 1px solid #c9becb;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ede2f0, stop: 1 #e3d8e6);
            }
        """)
        self.llmAnalysisButton.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #b8d8d8, stop: 1 #aecfce);
                color: #333333;
                font-size: 14px;
                padding: 8px 16px;
                border-radius: 8px;
                border: 1px solid #9ec3c3;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #c2e2e2, stop: 1 #b8d8d8);
            }
        """)

    # 事件过滤
    def eventFilter(self, obj, event):
        if obj == self.imageLabel and event.type() == QEvent.MouseButtonPress:
            self.show_original_image()
            return True
        return super().eventFilter(obj, event)

    # 初始化去雾模型
    def init_dehaze_model(self):
        try:
            model_config = {
                'model_name': 'dehazeformer-b',
                'checkpoint_path': r'./model/dehazeformer-b.pth'
            }
            self.dehaze_model = eval(model_config['model_name'].replace('-', '_'))()
            self.dehaze_model.cuda()
            checkpoint = torch.load(model_config['checkpoint_path'])
            state_dict = checkpoint['state_dict']
            new_state_dict = collections.OrderedDict()
            for k, v in state_dict.items():
                name = k[7:]
                new_state_dict[name] = v
            self.dehaze_model.load_state_dict(new_state_dict)
            self.dehaze_model.eval()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"去雾模型初始化失败: {str(e)}")
            self.close()

    # 显示原图
    def show_original_image(self):
        if hasattr(self, 'detection_results'):
            image = cv2.imread(self.image_path)
            dehazed_image = dehaze_image(image)

            for res in self.detection_results:
                box = res["box"]
                obj_type = res["type"]
                confidence = res["confidence"]
                cv2.rectangle(dehazed_image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
                label = f"{obj_type}: {confidence:.2f}%"
                cv2.putText(dehazed_image, label, (int(box[0]), int(box[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            annotated_image_rgb = cv2.cvtColor(dehazed_image, cv2.COLOR_BGR2RGB)
            h, w, ch = annotated_image_rgb.shape
            bytes_per_line = ch * w
            q_image = QImage(annotated_image_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)

            dialog = QDialog(self)
            dialog.setWindowTitle("检测结果")
            layout = QVBoxLayout(dialog)
            label = QLabel(dialog)
            label.setPixmap(pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            layout.addWidget(label)
            dialog.setLayout(layout)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "警告", "请先进行图像处理！")

    # 加载图片
    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "上传图片", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)")
        if file_name:
            self.image_path = file_name
            pixmap = QPixmap(file_name)
            self.imageLabel.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    # 处理图片
    def process_image(self):
        if not hasattr(self, 'image_path'):
            QMessageBox.warning(self, "警告", "请先加载图片！")
            return

        image = cv2.imread(self.image_path)
        if image is None:
            QMessageBox.warning(self, "错误", "无法加载图片！")
            return

        dehazed_image = dehaze_image(image, self.dehaze_model)
        results = self.model(dehazed_image)

        result = results[0]
        num_objects = len(result.boxes)
        object_types = [result.names[int(cls)] for cls in result.boxes.cls]
        confidences = [float(conf) * 100 for conf in result.boxes.conf]
        boxes = result.boxes.xyxy

        self.detection_results = []
        for i in range(num_objects):
            self.detection_results.append({
                "type": object_types[i],
                "confidence": confidences[i],
                "box": boxes[i]
            })

        unique_types = list(set(object_types))
        unique_types.sort()

        self.targetSelector.clear()
        self.targetSelector.addItem("全部类型")
        for obj_type in unique_types:
            self.targetSelector.addItem(obj_type)

        self.targetSelector.setCurrentIndex(0)
        self.update_display()
        self.set_warning_lights(confidences)

    # 更新显示内容
    def update_display(self):
        selected_type = self.targetSelector.currentText()
        if selected_type == "全部类型":
            filtered_results = self.detection_results
        else:
            filtered_results = [res for res in self.detection_results if res["type"] == selected_type]

        if filtered_results:
            types = [res["type"] for res in filtered_results]
            confidences = [res["confidence"] for res in filtered_results]
            boxes = [res["box"] for res in filtered_results]
            self.objectTypeLabel.setText(f"目标类型: {', '.join(set(types))}")
            self.confidenceLabel.setText(f"置信度: {', '.join([f'{conf:.2f}%' for conf in confidences])}")
            self.positionLabel.setText(f"目标位置（Xmin,Ymin,Xmax,Ymax）: {', '.join([f'({int(box[0])}, {int(box[1])}, {int(box[2])}, {int(box[3])})' for box in boxes])}")
        else:
            self.objectTypeLabel.setText("目标类型: N/A")
            self.confidenceLabel.setText("置信度: N/A")
            self.positionLabel.setText("目标位置: N/A")

        self.update_confidence_chart(filtered_results)
        self.update_image_display(filtered_results)

    # 更新表格
    def update_confidence_chart(self, filtered_results):
        chart = QChart()
        if not filtered_results:
            chart.setTitle("置信度分布")
            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_view.setMinimumSize(self.confidenceChartGroupBox.width() - 20, 200)
            for i in reversed(range(self.confidenceChartLayout.count())):
                item = self.confidenceChartLayout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    widget.deleteLater()
            self.confidenceChartLayout.addWidget(chart_view)
            return

        confidences = [res["confidence"] for res in filtered_results]
        num_objects = len(confidences)

        if num_objects == 1:
            scatter_series = QScatterSeries()
            scatter_series.append(0, confidences[0])
            scatter_series.setMarkerSize(10.0)
            scatter_series.setColor(QColor("#76a1d1"))
            chart.addSeries(scatter_series)
            axis_x = QBarCategoryAxis()
            axis_x.append(["目标 1"])
            chart.addAxis(axis_x, Qt.AlignBottom)
            scatter_series.attachAxis(axis_x)
            axis_y = QValueAxis()
            axis_y.setRange(0, 100)
            axis_y.setTitleText("置信度 (%)")
            chart.addAxis(axis_y, Qt.AlignLeft)
            scatter_series.attachAxis(axis_y)
            chart.setTitle("置信度分布 (点表示)")
        else:
            line_series = QLineSeries()
            for i, conf in enumerate(confidences):
                line_series.append(i, conf)
            chart.addSeries(line_series)
            axis_x = QBarCategoryAxis()
            categories = [f"目标 {i + 1}" for i in range(num_objects)]
            axis_x.append(categories)
            chart.addAxis(axis_x, Qt.AlignBottom)
            line_series.attachAxis(axis_x)
            axis_y = QValueAxis()
            axis_y.setRange(0, 100)
            axis_y.setTitleText("置信度 (%)")
            chart.addAxis(axis_y, Qt.AlignLeft)
            line_series.attachAxis(axis_y)
            chart.setTitle("置信度分布 (百分比)")

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumSize(self.confidenceChartGroupBox.width() - 20, 200)

        for i in reversed(range(self.confidenceChartLayout.count())):
            item = self.confidenceChartLayout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                widget.deleteLater()
        self.confidenceChartLayout.addWidget(chart_view)

    # 更新图像显示
    def update_image_display(self, filtered_results):
        image = cv2.imread(self.image_path)
        dehazed_image = dehaze_image(image, self.dehaze_model)

        for res in filtered_results:
            box = res["box"]
            obj_type = res["type"]
            confidence = res["confidence"]
            cv2.rectangle(dehazed_image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
            label = f"{obj_type}: {confidence:.2f}%"
            cv2.putText(dehazed_image, label, (int(box[0]), int(box[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        annotated_image_rgb = cv2.cvtColor(dehazed_image, cv2.COLOR_BGR2RGB)
        h, w, ch = annotated_image_rgb.shape
        bytes_per_line = ch * w
        q_image = QImage(annotated_image_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.imageLabel.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    # 更新指示灯
    def set_warning_lights(self, confidences):
        self.greenLightLabel.setPixmap(QPixmap())
        self.yellowLightLabel.setPixmap(QPixmap())
        self.redLightLabel.setPixmap(QPixmap())

        max_confidence = max(confidences) if confidences else 0
        if max_confidence < 50:
            light_status = f"绿灯：置信度低，较为安全。 (最大置信度: {max_confidence:.2f}%)"
            self.greenLightLabel.setPixmap(self.green_light.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        elif 50 <= max_confidence <= 80:
            light_status = f"黄灯：置信度中等，注意观察。 (最大置信度: {max_confidence:.2f}%)"
            self.yellowLightLabel.setPixmap(self.yellow_light.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            light_status = f"红灯：置信度较高，需关注。 (最大置信度: {max_confidence:.2f}%)"
            self.redLightLabel.setPixmap(self.red_light.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.llmAnalysisLabel.setText(light_status)
        self.light_status = light_status

    # 调用 LLM 进行分析
    def analyze_with_llm(self):
        analyze_with_llm(self, self.OPENROUTER_API_KEY)  # 调用 llm_module 中的 analyze_with_llm 函数

    # LLM 分析完成后的回调函数
    def on_llm_analysis_finished(self, result):
        self.llmResultTextEdit.setText(result)
        self.loading_movie.stop()
        self.loading_label.hide()

    def quit_app(self):
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())