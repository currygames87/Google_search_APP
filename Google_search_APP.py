import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QTextBrowser, QVBoxLayout, QWidget, QMessageBox, QDesktopWidget
from PyQt5.QtCore import Qt
import requests
import json
import os
import base64
import unicodedata
from bs4 import BeautifulSoup
import re
import webbrowser

class GoogleSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google 搜尋小小小工具")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        # 主窗口布局
        layout = QVBoxLayout()

        # 標題
        title_label = QLabel("Google 搜尋小小小工具")
        title_label.setStyleSheet("font-size: 30px; color: #FF00FF; font-weight: pink;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 關鍵字輸入框
        keyword_label = QLabel("請輸入想搜尋的關鍵字：")
        keyword_label.setStyleSheet("font-size: 25px;")
        layout.addWidget(keyword_label)

        self.keyword_input = QLineEdit()
        self.keyword_input.setStyleSheet("font-size:25px;")
        layout.addWidget(self.keyword_input)

        # 文字搜索按鈕
        text_search_button = QPushButton("搜尋文字")
        text_search_button.setStyleSheet("font-size: 20px; background-color: #FF00FF; color: white;")
        text_search_button.clicked.connect(self.search_text)
        layout.addWidget(text_search_button)

        # 圖片搜索按鈕
        image_search_button = QPushButton("搜尋圖片")
        image_search_button.setStyleSheet("font-size: 20px; background-color: #FF00FF; color: white;")
        image_search_button.clicked.connect(self.search_image)
        layout.addWidget(image_search_button)

        # 搜索結果
        self.result_text = QTextBrowser()
        self.result_text.setStyleSheet("font-size: 30px;")
        self.result_text.setOpenExternalLinks(True)
        layout.addWidget(self.result_text)

        # 將布局設置為中央窗口
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


    def google_text_search(self, keyword):
        url = f"https://www.google.com/search?q={keyword}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        search_results = soup.find_all("div", class_="tF2Cxc")
        results = []
        for i, result in enumerate(search_results, start=1):
            title = result.find("h3").text
            link = result.find("a")["href"]
            results.append({"number": i, "title": unicodedata.normalize("NFKC", title), "link": link})
        return results

    def google_image_search(self, keyword):
        url = f"https://www.google.com/search?q={keyword}&tbm=isch"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            image_links = re.findall(r'"ou":"(.*?)"', response.text)
            results = [{"number": i+1, "link": link} for i, link in enumerate(image_links[:10])]
            return results
        else:
            print(f"Failed to retrieve images, status code: {response.status_code}")
            return []

    def save_to_json(self, data, filename):
        with open(f"{filename}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def save_images(self, images, keyword):
        folder_name = keyword.replace(":", "_") + "_images"
        os.makedirs(folder_name, exist_ok=True)
        for image in images:
            link = image["link"]
            if link.startswith("data:image"):
                _, base64_data = link.split(",", 1)
                image_data = base64.b64decode(base64_data)
                filename = os.path.join(folder_name, f"image_{image['number']}.jpg")
                with open(filename, "wb") as f:
                    f.write(image_data)
                continue
            if link.startswith("/"):
                link = "https://www.google.com" + link
            elif not link.startswith("http"):
                link = "https://" + link
            response = requests.get(link)
            filename = os.path.join(folder_name, f"image_{image['number']}.jpg")
            with open(filename, "wb") as f:
                f.write(response.content)

    def search_text(self):
        keyword = self.keyword_input.text()
        search_results = self.google_text_search(keyword)
        if search_results:
            result_text = ''
            for result in search_results:
                result_text += f"{result['number']}. <a href='{result['link']}'>{result['title']}</a><br><br>"
            self.result_text.setHtml(result_text)
            QMessageBox.information(self, "成功!", f"共找到 {len(search_results)} 條搜尋結果！")
        else:
            QMessageBox.warning(self, "錯誤!", "未找到任何文字搜尋結果！")

    def search_image(self):
        keyword = self.keyword_input.text()
        image_results = self.google_image_search(keyword)
        if image_results:
            self.save_to_json(image_results, f"{keyword}_image_search_results")
            self.save_images(image_results, keyword)
            QMessageBox.information(self, "成功!", f"共找到 {len(image_results)} 張圖片，並已下載至圖片資料夾！")
        else:
            QMessageBox.warning(self, "錯誤!", "未找到任何圖片搜尋結果！")

    def open_link(self, link):
        webbrowser.open(link)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GoogleSearchApp()
    window.show()
    sys.exit(app.exec_())
