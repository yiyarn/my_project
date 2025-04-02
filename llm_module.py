import base64
import requests
import cv2
from PySide6.QtCore import QBuffer, QByteArray, QThread, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QMessageBox, QApplication
from project.dehaze import dehaze_image

def query_llm(prompt, api_key):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen/qwen2.5-vl-32b-instruct:free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code}, {response.text}"

def image_to_base64(image):
    # 使用 QByteArray 和 QBuffer 保存图像
    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QBuffer.WriteOnly)
    image.save(buffer, "JPEG")  # 保存为 JPEG 格式
    buffer.close()
    img_str = byte_array.toBase64().data().decode("utf-8")
    return img_str

class LLMQueryThread(QThread):
    result_signal = Signal(str)

    def __init__(self, prompt, api_key):
        super().__init__()
        self.prompt = prompt
        self.api_key = api_key

    def run(self):
        result = query_llm(self.prompt, self.api_key)  # 传递 api_key
        self.result_signal.emit(result)

def analyze_with_llm(self, api_key):
    if not hasattr(self, 'detection_results'):
        QMessageBox.warning(self, "警告", "请先进行图像处理！")
        return

    self.llmResultTextEdit.setText("分析中...")
    self.loading_label.show()

    self.loading_movie.stop()
    self.loading_movie.jumpToFrame(0)
    self.loading_movie.start()
    QApplication.processEvents()

    # 获取原始图像
    original_image = cv2.imread(self.image_path)
    original_image_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
    h, w, ch = original_image_rgb.shape
    bytes_per_line = ch * w
    q_image_original = QImage(original_image_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
    pixmap_original = QPixmap.fromImage(q_image_original)

    # 获取处理后的图像（去雾 + 目标检测）
    image = cv2.imread(self.image_path)
    dehazed_image = dehaze_image(image, self.dehaze_model)
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
    q_image_annotated = QImage(annotated_image_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
    pixmap_annotated = QPixmap.fromImage(q_image_annotated)

    # 转换为 Base64 编码
    original_image_base64 = image_to_base64(pixmap_original.toImage())
    annotated_image_base64 = image_to_base64(pixmap_annotated.toImage())

    # 准备信息
    num_objects = len(self.detection_results)
    object_types = [res["type"] for res in self.detection_results]
    confidences = [res["confidence"] for res in self.detection_results]
    light_status = self.light_status

    # 构建多模态提示
    prompt_text = f"""
    你是一个水源地保护系统的分析助手。以下是无人机拍摄的图像分析结果：

    - 检测到的目标数量: {num_objects}
    - 目标类型: {', '.join(set(object_types))}
    - 置信度: {', '.join([f'{conf:.2f}%' for conf in confidences])}
    - 预警提示: {light_status}

    请结合以下两张图像（第一张是原始图像，第二张是去雾和目标检测后的图像）进行分析：
    1. 根据分析结果和图像，你判断当前情况下是否发现钓鱼行为？
    2. 图中被识别出的目标的行为可能对水源地造成什么破坏？
    3. 建议采取什么紧急措施来防止破坏？

    请用简洁明了的语言回答，确保用户能够快速理解并采取行动。
    """

    prompt = [
        {"type": "text", "text": prompt_text},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{original_image_base64}"}},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{annotated_image_base64}"}}
    ]

    self.llm_thread = LLMQueryThread(prompt, api_key)  # 传递 api_key
    self.llm_thread.result_signal.connect(self.on_llm_analysis_finished)
    self.llm_thread.start()