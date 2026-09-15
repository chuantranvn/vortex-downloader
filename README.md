<div align="center">

# ⚡ VORTEX DOWNLOADER
### **Trình Tải Video & Tệp Tin Đa Luồng Thế Hệ Mới (Kiến Trúc Microservices)**

<p align="center">
  <img src="client/desktop_gui/assets/vortex_icon.png" width="120" height="120" alt="Vortex Downloader Logo" style="border-radius: 24px; box-shadow: 0 10px 30px rgba(14, 165, 233, 0.4);" />
</p>

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PySide6](https://img.shields.io/badge/PySide6-Qt6%20GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://pypi.org/project/PySide6/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-2024%2B-red?style=for-the-badge&logo=youtube&logoColor=white)](https://github.com/yt-dlp/yt-dlp)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-7.1%20Static-green?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![Chrome MV3](https://img.shields.io/badge/Extension-Manifest%20V3-blueviolet?style=for-the-badge&logo=googlechrome&logoColor=white)](https://developer.chrome.com/docs/extensions/mv3/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

<p align="center">
  <b>Tăng tốc tải dữ liệu tối đa băng thông • Bóc tách video 8K/4K/1080p/MP3 • Tiện ích nhúng Chrome/Edge • Giao diện Frosted Milky White 2026</b>
</p>

<p align="center">
  <a href="USER_GUIDE.md"><b>📖 Hướng Dẫn Sử Dụng Chi Tiết</b></a> • 
  <a href="ARCHITECTURE.md"><b>🏗️ Kiến Trúc Hệ Thống & Dev Guide</b></a> • 
  <a href="installer_output/Vortex_Downloader_Setup.exe"><b>📦 Tải Bộ Cài Đặt (.exe)</b></a>
</p>

---

</div>

## 🌟 Điểm Nhấn Công Nghệ Vượt Trội

* 🚀 **Tải đa luồng chuẩn IDM (Multi-threaded Range Engine):** Tự động chia nhỏ tệp tin thành **8 đến 32 phần song song** thông qua HTTP Range header, tối đa hóa 100% băng thông đường truyền internet.
* 🎬 **Trích xuất video thông minh (Media Extractor):** Hỗ trợ YouTube, Facebook, TikTok, Instagram và các luồng HLS/m3u8. Tự động bóc tách từ **8K (4320p), 4K (2160p), 2K (1440p), Full HD (1080p), 720p** đến **Chế độ chỉ tải MP3**.
* 🧩 **Tích hợp FFmpeg 7.1 tĩnh độc lập:** Tự động hòa trộn luồng hình ảnh độ nét cao và âm thanh tốt nhất mà không yêu cầu người dùng phải tự cài đặt FFmpeg trên Windows.
* 🌐 **Tiện ích trình duyệt thế hệ mới (Manifest V3 Extension):** Nút tải nổi gradient trực tiếp trên trình phát video, menu dropdown chống rớt hover, hiển thị ước tính dung lượng tệp (~MB) và nút tắt `✕` linh hoạt.
* 🎨 **Giao diện Desktop hiện đại 2026 (Frosted Milky White):** Thiết kế thanh lịch với nền trắng đục mờ ảo, thanh điều hướng Sidebar thông minh kèm bộ đếm động, huy hiệu trạng thái tròn (Pills), cập nhật tiến trình thời gian thực qua **WebSocket**, hỗ trợ thu nhỏ xuống Khay hệ thống (System Tray).
* 📋 **Tự động bắt link Clipboard (Clipboard Monitor):** Nhận diện ngay lập tức khi bạn bấm `Ctrl + C` bất kỳ đường dẫn tải nào khi lướt web.
* 🚀 **Khởi động cùng Windows (Auto-start):** Tùy chọn chạy ngầm dưới khay hệ thống ngay khi bật máy tính, sẵn sàng bắt link tải tự động mà không làm phiền người dùng.
* 💾 **Lưu trữ lịch sử bền vững (SQLite DB):** Toàn bộ tác vụ tải, trạng thái, đường dẫn tệp và kích thước tệp thật được lưu trữ vĩnh viễn trong cơ sở dữ liệu SQLite tại `%APPDATA%\VortexDownloader\data\`.

---

## 🏗️ Kiến Trúc Hệ Thống (Microservices Architecture)

```mermaid
graph TD
    User([Người dùng / Web Browser]) -->|Lướt web / Xem Video| Ext[Extension Chrome/Edge MV3]
    User -->|Ctrl + C Link| GUI[Desktop GUI - PySide6]

    Ext -->|REST API :8000| Gateway[API Gateway - Port 8000]
    GUI -->|REST API :8000| Gateway
    Gateway -->|WebSocket Progress Hub| GUI

    subgraph Backend Services
        Gateway -->|Tải file Range đa luồng| Core[Core Engine - Port 8001]
        Gateway -->|Bóc tách & Tải Video/Audio| Media[Media Extractor - Port 8002]
        Gateway <-->|Đồng bộ & Lưu trữ| DB[(SQLite History DB)]
        Media -->|Hòa trộn luồng| FFmpeg[FFmpeg 7.1 Static Binary]
    end

    Core --> Disk[(Ổ Đĩa Cứng Downloads)]
    Media --> Disk
```

### Chi tiết các dịch vụ:
| Dịch vụ | Cổng (Port) | Công nghệ | Nhiệm vụ chính |
| :--- | :---: | :---: | :--- |
| **API Gateway** | `8000` | FastAPI, Uvicorn, SQLite | Điều phối thông minh, quản trị tác vụ, WebSocket Hub tập trung |
| **Core Engine** | `8001` | FastAPI, aiohttp, HTTP Range | Tải tệp tin trực tiếp đa luồng, ghép nối chunk tự động, Pause/Resume |
| **Media Extractor**| `8002` | yt-dlp, FFmpeg 7.1, asyncio | Bóc tách metadata, tải đa phân đoạn (16 fragments), chuyển đổi sang MP4/MP3 |
| **Desktop Client** | Desktop | PySide6, Qt6, Dark Theme | Bảng điều khiển tác vụ, lọc trạng thái, menu ngữ cảnh chuột phải, System Tray |
| **Browser Extension**| Chrome/Edge | Vanilla JS, CSS3, Manifest V3 | Nút tải nổi trên trình duyệt, tự động dò phân giải, click-to-toggle menu |

---

## 📸 Giao Diện Trực Quan

### 1. Nút Tải Nổi Thông Minh Trên Trình Duyệt
* Tích hợp trực tiếp trên khung phát video YouTube / Facebook / Web phim.
* Menu xổ xuống với các mức chất lượng và dung lượng ước tính (~MB, ~GB).
* Nút tắt `✕` để ẩn thanh tải cho video hiện tại khi không muốn bị vướng mắt.

### 2. Giao Diện Desktop Điều Khiển Tập Trung
* Bộ lọc trạng thái: `Tất cả`, `Đang tải`, `Hoàn tất`, `Tạm dừng`.
* Menu chuột phải: `Tạm dừng`, `Tiếp tục`, `Mở thư mục chứa file`, `Xóa khỏi lịch sử`.
* Cột tiến độ thời gian thực: Tốc độ tải (MB/s), phần trăm hoàn thành, dung lượng thực tế, thời gian còn lại (ETA).

---

## 📦 Cài Đặt Nhanh Bằng Bộ Cài Đặt Windows (Setup Wizard)

Đối với người dùng cuối không muốn cài đặt Python hay cấu hình dòng lệnh, dự án cung cấp sẵn bộ cài đặt hoàn chỉnh:

* **File cài đặt:** `installer_output/Vortex_Downloader_Setup.exe` (hoặc `Vortex_Downloader_Setup_v1.0.exe`)
* **Tính năng của bộ cài:**
  * 🪄 **Trình hướng dẫn cài đặt chuẩn (Setup Wizard):** Chọn thư mục cài đặt (`Program Files` hoặc `AppData`).
  * 🖥️ **Tạo biểu tượng nhanh:** Tự động tạo Shortcut trên màn hình Desktop và Start Menu.
  * 🚀 **Tự động khởi động cùng Windows (Run on Startup):** Tích hợp tùy chọn khởi động ngầm êm ái ở khay hệ thống (System Tray) khi bật máy tính. Có thể bật/tắt dễ dàng qua checkbox trên thanh công cụ hoặc menu chuột phải khay hệ thống.
  * 🧩 **Tích hợp sẵn mọi thứ:** Đã nhúng sẵn Python runtime, FFmpeg 7.1 tĩnh và Extension Chromium, người dùng chỉ cần chạy file `.exe` là có thể tải ngay.
  * 🗑️ **Trình gỡ cài đặt sạch sẽ:** Hỗ trợ Uninstall chuẩn từ Windows Apps & Settings / Control Panel.

### 🛠️ Lệnh Đóng Gói Bộ Cài Đặt (Dành Cho Lập Trình Viên)
Để tự đóng gói lại toàn bộ ứng dụng từ mã nguồn:
```powershell
python build_installer.py
```
Script sẽ tự động tạo icon `.ico`, chạy PyInstaller thu thập binary và biên dịch Inno Setup xuất ra `installer_output/Vortex_Downloader_Setup.exe`.

---

## ⚡ Hướng Dẫn Cài Đặt Cho Lập Trình Viên (Dev Mode)

### 1. Yêu cầu hệ thống
* **Hệ điều hành:** Windows 10/11 (hoặc Linux / macOS).
* **Python:** Phiên bản `3.10` trở lên.
* **Trình duyệt:** Google Chrome, Microsoft Edge, Cốc Cốc, Brave hoặc bất kỳ trình duyệt nhân Chromium nào.

### 2. Cài đặt môi trường
Mở PowerShell hoặc Terminal tại thư mục dự án:
```powershell
# Tạo môi trường ảo Python
python -m venv .venv

# Kích hoạt môi trường ảo (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Cài đặt toàn bộ thư viện cần thiết
pip install -r requirements.txt
```

### 3. Khởi chạy phát triển (Dev Run)
Chỉ cần chạy lệnh sau để chạy trực tiếp từ mã nguồn:
```powershell
python run_app.py
```

---

## 🧩 Cài Đặt Extension Vào Trình Duyệt (Chrome / Edge)

1. Mở trình duyệt và truy cập vào trang quản lý tiện ích:
   * **Google Chrome:** `chrome://extensions`
   * **Microsoft Edge:** `edge://extensions`
2. Bật chế độ **Nhà phát triển (Developer Mode)** ở góc trên bên phải.
3. Bấm vào nút **Tải tiện ích đã giải nén (Load unpacked)**.
4. Chọn thư mục `extension` trong thư mục dự án `vortex-downloader`.
5. Truy cập bất kỳ video nào trên **YouTube** để thấy thanh tải nổi Vortex xuất hiện ngay trên video!

---

## 📡 Tài Liệu API & WebSocket

Khi hệ thống khởi chạy, bạn có thể xem tài liệu tương tác Swagger UI tại:
* **API Gateway Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Core Engine Documentation:** [http://localhost:8001/docs](http://localhost:8001/docs)
* **Media Extractor Documentation:** [http://localhost:8002/docs](http://localhost:8002/docs)

### Các Endpoint Tiêu Biểu:
* `POST /api/v1/download`: Khởi tạo tác vụ tải mới (hệ thống tự động định tuyến đến Core Engine hoặc Media Extractor).
* `POST /api/v1/extract`: Trích xuất thông tin độ phân giải, định dạng và dung lượng video.
* `GET /api/v1/tasks`: Lấy danh sách toàn bộ tác vụ trong lịch sử SQLite.
* `POST /api/v1/tasks/{id}/pause`: Tạm dừng tác vụ tải.
* `POST /api/v1/tasks/{id}/resume`: Tiếp tục tác vụ tải.
* `POST /api/v1/tasks/{id}/cancel`: Xóa hoàn toàn tác vụ khỏi bộ nhớ và SQLite.
* `WS /ws/progress`: Kênh WebSocket phát sóng tiến độ theo thời gian thực (500ms heartbeat).

---

## 📁 Cấu Trúc Mã Nguồn

```text
vortex-downloader/
├── client/                     # Mã nguồn máy khách
│   └── desktop_gui/            # Giao diện Desktop PySide6
│       ├── assets/             # Biểu tượng 3D squircle cao cấp
│       ├── add_dialog.py       # Cửa sổ thêm link tải thủ công
│       ├── main_window.py      # Cửa sổ chính & khay hệ thống
│       ├── styles.py           # Bảng phong cách Dark Theme QSS
│       └── websocket_worker.py # Luồng nền lắng nghe WebSocket
├── common/                     # Thư viện dùng chung giữa các dịch vụ
│   ├── database.py             # Quản lý cơ sở dữ liệu SQLite bền vững
│   └── schemas.py              # Mô hình dữ liệu chuẩn Pydantic
├── extension/                  # Tiện ích mở rộng trình duyệt (MV3)
│   ├── background/             # Service worker nền
│   ├── content/                # Thanh tải nổi & cầu nối tương tác video
│   ├── icons/                  # Bộ biểu tượng đa kích thước (16-128px)
│   ├── popup/                  # Giao diện popup kiểm tra trạng thái
│   └── manifest.json           # Tệp cấu hình Chrome Manifest V3
├── services/                   # Các dịch vụ Microservices độc lập
│   ├── core_engine/            # Cổng 8001: Bộ tải tệp tin HTTP Range đa luồng
│   ├── media_extractor/        # Cổng 8002: Bộ bóc tách và ghép video yt-dlp + FFmpeg
│   └── gateway/                # Cổng 8000: API Gateway điều phối & WebSocket Hub
├── .gitignore                  # Cấu hình bỏ qua tệp nhị phân và cache
├── requirements.txt            # Danh sách gói phụ thuộc Python
├── run_app.py                  # Trình khởi động 1-Click toàn bộ hệ thống
└── README.md                   # Tài liệu hướng dẫn sử dụng chính thức
```

---

## 🤝 Đóng Góp Phát Triển (Contributing)

Mọi đóng góp nhằm cải thiện tính năng, sửa lỗi hoặc tối ưu hóa hiệu năng đều được chào đón nồng nhiệt!
1. **Fork** dự án về tài khoản GitHub của bạn.
2. Tạo nhánh tính năng mới (`git checkout -b feature/TinhNangMoi`).
3. Commit các thay đổi (`git commit -m 'Thêm tính năng mới'`).
4. Push lên nhánh của bạn (`git push origin feature/TinhNangMoi`).
5. Mở một **Pull Request** trên GitHub.

---

## 📄 Bản Quyền (License)

Dự án được phát hành theo giấy phép mã nguồn mở [MIT License](LICENSE). Tự do sử dụng, chỉnh sửa và phân phối cho mục đích cá nhân cũng như thương mại.

<div align="center">
  <b>Phát triển với ❤️ bởi <a href="https://github.com/chuantranvn">chuantranvn</a></b>
</div>
