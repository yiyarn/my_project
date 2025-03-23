import sys
import cv2
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QHBoxLayout, QWidget, QComboBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap, QPainter, QPalette, QColor
from PySide6.QtCharts import QChart, QLineSeries, QScatterSeries, QBarCategoryAxis, QChartView, QValueAxis
from ui_mainwindow import Ui_MainWindow
from ultralytics import YOLO
from dehaze import dehaze_image


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#E6F0FA"))
        self.setPalette(palette)

        # 手动设置窗口大小
        self.resize(1280, 720)

        # 初始化 YOLOv8 模型
        self.model_path = r"./models/yolov8n.pt"
        self.model = YOLO(self.model_path)

        # 加载图标
        self.gray_light = QPixmap("./images/gray_light.png")
        self.green_light = QPixmap("./images/green_light.png")
        self.yellow_light = QPixmap("./imahges/yellow_light.png")
        self.red_light = QPixmap("./images/red_light.png")

        # 连接按钮信号
        self.loadImageButton.clicked.connect(self.load_image)
        self.processButton.clicked.connect(self.process_image)
        self.quitButton.clicked.connect(self.quit_app)

        # 连接目标选择下拉框信号
        self.targetSelector.currentIndexChanged.connect(self.update_target_info)

        # 美化按钮（使用指定的莫兰迪色）
        self.loadImageButton.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #dfdfea, stop: 1 #d5d5e0); /* 浅灰紫色 */
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
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #c9cae1, stop: 1 #bfbfd7); /* 浅蓝紫色 */
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
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e3d8e6, stop: 1 #d9cedc); /* 浅粉紫色 */
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

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "上传图片", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.image_path = file_name
            pixmap = QPixmap(file_name)
            self.imageLabel.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def process_image(self):
        if not hasattr(self, 'image_path'):
            QMessageBox.warning(self, "警告", "请先加载图片！")
            return

        image = cv2.imread(self.image_path)
        if image is None:
            QMessageBox.warning(self, "错误", "无法加载图片！")
            return

        dehazed_image = dehaze_image(image)
        results = self.model(dehazed_image)
        annotated_image = results[0].plot()

        annotated_image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        h, w, ch = annotated_image_rgb.shape
        bytes_per_line = ch * w
        q_image = QImage(annotated_image_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.imageLabel.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        result = results[0]
        num_objects = len(result.boxes)
        object_types = [result.names[int(cls)] for cls in result.boxes.cls]
        confidences = [float(conf) * 100 for conf in result.boxes.conf]

        # 存储检测结果以供下拉框使用
        self.detection_results = {
            "object_types": object_types,
            "confidences": confidences,
            "boxes": result.boxes.xyxy
        }

        # 更新目标选择下拉框
        self.targetSelector.clear()
        for i in range(num_objects):
            self.targetSelector.addItem(f"目标 {i + 1}")

        if num_objects > 0:
            # 默认显示第一个目标的信息
            self.update_target_info(0)
        else:
            # 如果没有检测到目标，清空信息
            self.objectTypeLabel.setText("目标类型: N/A")
            self.confidenceLabel.setText("置信度: N/A")
            self.positionLabel.setText("目标位置: N/A")

        # 创建置信度图表并嵌入到 confidenceChartLayout 中
        chart = QChart()

        if num_objects == 1:
            # 只有一个目标，绘制点
            scatter_series = QScatterSeries()
            scatter_series.append(0, confidences[0])  # x=0, y=置信度
            scatter_series.setMarkerSize(10.0)  # 设置点的大小
            scatter_series.setColor(QColor("#76a1d1"))  # 设置点颜色为 #76a1d1
            chart.addSeries(scatter_series)

            # 设置 X 轴（仅显示一个点）
            axis_x = QBarCategoryAxis()
            axis_x.append(["目标 1"])
            chart.addAxis(axis_x, Qt.AlignBottom)
            scatter_series.attachAxis(axis_x)

            # 设置 Y 轴（置信度范围 0-100）
            axis_y = QValueAxis()
            axis_y.setRange(0, 100)
            axis_y.setTitleText("置信度 (%)")
            chart.addAxis(axis_y, Qt.AlignLeft)
            scatter_series.attachAxis(axis_y)

            chart.setTitle("置信度分布 (点表示)")
        else:
            # 多个目标，绘制折线
            line_series = QLineSeries()
            for i, conf in enumerate(confidences):
                line_series.append(i, conf)  # x 轴为目标索引，y 轴为置信度
            chart.addSeries(line_series)

            # 设置 X 轴（目标索引）
            axis_x = QBarCategoryAxis()
            categories = [f"目标 {i + 1}" for i in range(num_objects)]
            axis_x.append(categories)
            chart.addAxis(axis_x, Qt.AlignBottom)
            line_series.attachAxis(axis_x)

            # 设置 Y 轴（置信度范围 0-100）
            axis_y = QValueAxis()
            axis_y.setRange(0, 100)
            axis_y.setTitleText("置信度 (%)")
            chart.addAxis(axis_y, Qt.AlignLeft)
            line_series.attachAxis(axis_y)

            chart.setTitle("置信度分布 (百分比)")

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        # 动态调整大小以适配 GroupBox
        chart_view.setMinimumSize(self.confidenceChartGroupBox.width() - 20, 200)

        # 移除旧的 chartView（如果存在），并将新图表添加到 confidenceChartLayout
        for i in reversed(range(self.confidenceChartLayout.count())):
            item = self.confidenceChartLayout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                widget.deleteLater()
        self.confidenceChartLayout.addWidget(chart_view)

        self.set_warning_lights(confidences)

    def update_target_info(self, index):
        if hasattr(self, 'detection_results'):
            object_types = self.detection_results["object_types"]
            confidences = self.detection_results["confidences"]
            boxes = self.detection_results["boxes"]

            if 0 <= index < len(object_types):
                obj_type = object_types[index]
                confidence = confidences[index]
                box = boxes[index]
                self.objectTypeLabel.setText(f"目标类型: {obj_type}")
                self.confidenceLabel.setText(f"置信度: {confidence:.2f}%")
                self.positionLabel.setText(
                    f"目标位置: xmin: {int(box[0])}, ymin: {int(box[1])}, xmax: {int(box[2])}, ymax: {int(box[3])}")
            else:
                self.objectTypeLabel.setText("目标类型: N/A")
                self.confidenceLabel.setText("置信度: N/A")
                self.positionLabel.setText("目标位置: N/A")
        else:
            self.objectTypeLabel.setText("目标类型: N/A")
            self.confidenceLabel.setText("置信度: N/A")
            self.positionLabel.setText("目标位置: N/A")

    def set_warning_lights(self, confidences):
        # 重置预警灯状态（全部置灰）
        self.greenLightLabel.setPixmap(QPixmap())  # 清空图标
        self.yellowLightLabel.setPixmap(QPixmap())
        self.redLightLabel.setPixmap(QPixmap())

        # 遍历置信度，取最大值
        max_confidence = max(confidences) if confidences else 0
        print(f"最大置信度：{max_confidence}%")  # 调试输出

        # 根据置信度设置预警灯
        if max_confidence < 50:
            light_status = f"绿灯：置信度低，较为安全。 (最大置信度: {max_confidence:.2f}%)"
            self.greenLightLabel.setPixmap(self.green_light.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        elif 50 <= max_confidence <= 80:
            light_status = f"黄灯：置信度中等，注意观察。 (最大置信度: {max_confidence:.2f}%)"
            self.yellowLightLabel.setPixmap(
                self.yellow_light.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:  # > 80
            light_status = f"红灯：置信度较高，需关注。 (最大置信度: {max_confidence:.2f}%)"
            self.redLightLabel.setPixmap(self.red_light.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # 如果置信度 > 80%，强制亮红灯
        if max_confidence > 80:
            self.greenLightLabel.setPixmap(QPixmap())
            self.yellowLightLabel.setPixmap(QPixmap())
            self.redLightLabel.setPixmap(self.red_light.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            light_status = f"红灯：置信度较高，岸边有人钓鱼。 (最大置信度: {max_confidence:.2f}%)"

        self.llmAnalysisLabel.setText(light_status)

    def quit_app(self):
        self.close()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())