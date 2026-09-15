# 📖 HƯỚNG DẪN SỬ DỤNG VORTEX DOWNLOADER CHI TIẾT

Chào mừng bạn đến với **Vortex Downloader** — Trình tăng tốc tải xuống đa luồng và trích xuất video thế hệ mới với kiến trúc vi dịch vụ (Microservices), giao diện hiện đại và tiện ích nhúng trình duyệt.

Tài liệu này cung cấp toàn bộ hướng dẫn cài đặt, vận hành và khai thác tối đa sức mạnh của Vortex Downloader trên hệ điều hành Windows.

---

## 📑 MỤC LỤC
1. [Giới thiệu & Tính năng nổi bật](#1-giới-thiệu--tính-năng-nổi-bật)
2. [Cài đặt ứng dụng trên máy tính](#2-cài-đặt-ứng-dụng-trên-máy-tính)
   - [2.1 Cài đặt bằng file Setup Wizard](#21-cài-đặt-bằng-file-setup-wizard)
   - [2.2 Cài đặt tiện ích mở rộng (Extension) cho Chrome / Edge / Cốc Cốc](#22-cài-đặt-tiện-ích-mở-rộng-extension-cho-chrome--edge--cốc-cốc)
3. [Các phương thức tải xuống](#3-các-phương-thức-tải-xuống)
   - [3.1 Tải qua nút nổi trên trình duyệt (Khuyên dùng)](#31-tải-qua-nút-nổi-trên-trình-duyệt-khuyên-dùng)
   - [3.2 Tự động bắt link khi Copy (Clipboard Monitor)](#32-tự-động-bắt-link-khi-copy-clipboard-monitor)
   - [3.3 Thêm liên kết thủ công](#33-thêm-liên-kết-thủ-công)
   - [3.4 Tải file dữ liệu trực tiếp đa luồng (Direct Link)](#34-tải-file-dữ-liệu-trực-tiếp-đa-luồng-direct-link)
4. [Lựa chọn định dạng, chất lượng & số luồng](#4-lựa-chọn-định-dạng-chất-lượng--số-luồng)
5. [Quản lý tác vụ trên giao diện Desktop](#5-quản-lý-tác-vụ-trên-giao-diện-desktop)
   - [5.1 Bộ lọc danh mục thông minh (Sidebar)](#51-bộ-lọc-danh-mục-thông-minh-sidebar)
   - [5.2 Tìm kiếm tức thời (Live Search)](#52-tìm-kiếm-tức-thời-live-search)
   - [5.3 Các thao tác trên từng dòng tác vụ](#53-các-thao-tác-trên-từng-dòng-tác-vụ)
   - [5.4 Thao tác hàng loạt (Batch Actions)](#54-thao-tác-hàng-loạt-batch-actions)
6. [Công cụ & Cài đặt hệ thống](#6-công-cụ--cài-đặt-hệ-thống)
   - [6.1 Đổi thư mục lưu mặc định](#61-đổi-thư-mục-lưu-mặc-định)
   - [6.2 Vượt cơ chế chặn Bot YouTube bằng Cookies](#62-vượt-cơ-chế-chặn-bot-youtube-bằng-cookies)
   - [6.3 Tự động khởi động cùng Windows](#63-tự-động-khởi-động-cùng-windows)
   - [6.4 Điều khiển qua Khay hệ thống (System Tray)](#64-điều-khiển-qua-khay-hệ-thống-system-tray)
7. [Khắc phục sự cố thường gặp (Troubleshooting)](#7-khắc-phục-sự-cố-thường-gặp-troubleshooting)

---

## 1. Giới thiệu & Tính năng nổi bật

Vortex Downloader là giải pháp thay thế hoàn hảo cho các trình download truyền thống cũ kỹ, mang đến trải nghiệm tải dữ liệu tốc độ cao cùng giao diện hiện đại:

* ⚡ **Tải chia mảnh đa luồng (Multi-threaded Range Engine):** Tự động chia file làm **8 đến 32 phần song song**, ép băng thông mạng lên mức kịch sàn tương tự IDM.
* 🎬 **Bóc tách video thông minh:** Hỗ trợ mọi độ phân giải từ **8K UHD (4320p), 4K UHD (2160p), 2K QHD (1440p), Full HD (1080p), 720p** cho tới chế độ **Tách riêng file âm thanh MP3**.
* 🎵 **Hỗ trợ đa nền tảng:** YouTube, Facebook, TikTok, Instagram, Bilibili, các trang web xem phim trực tuyến (luồng HLS/m3u8), và link tải tệp tin thông thường (`.zip`, `.iso`, `.exe`, `.mp4`...).
* 🧩 **Tích hợp FFmpeg tĩnh:** Tự động hòa trộn video độ nét cao và âm thanh tốt nhất mà người dùng không cần cài đặt thêm bất kỳ công cụ dòng lệnh nào.
* 🎨 **Giao diện Frosted Milky White:** Thiết kế sang trọng với màu nền trắng đục tinh tế, tương thích mượt mà cả khi Windows bật Dark Mode hay Light Mode.

---

## 2. Cài đặt ứng dụng trên máy tính

### 2.1 Cài đặt bằng file Setup Wizard

1. Mở thư mục `installer_output\` trong thư mục dự án (hoặc tải file cài đặt mới nhất).
2. Nhấp đúp chuột vào file: **`Vortex_Downloader_Setup.exe`**.
3. Trình hướng dẫn cài đặt (Setup Wizard) sẽ xuất hiện:
   * **Chọn thư mục cài đặt:** Mặc định lưu tại `C:\Program Files (x86)\Vortex Downloader`.
   * **Tùy chọn Icon:** Tích chọn `Tạo biểu tượng ngoài màn hình nền (Create a desktop shortcut)`.
   * **Khởi động cùng Windows:** Tích chọn `Tự động khởi động cùng Windows` nếu bạn muốn ứng dụng luôn sẵn sàng bắt link khi bật máy tính.
4. Nhấn **Cài đặt (Install)** và đợi trong khoảng 5-10 giây để quá trình giải nén hoàn tất.
5. Nhấn **Hoàn thành (Finish)** để mở Vortex Downloader ngay lập tức.

> [!TIP]
> Ứng dụng đã được tích hợp đầy đủ Python runtime, FFmpeg 7.1 tĩnh và các thư viện cần thiết, bạn không cần cài thêm bất kỳ phần mềm phụ trợ nào.

---

### 2.2 Cài đặt tiện ích mở rộng (Extension) cho Chrome / Edge / Cốc Cốc

Để bắt link video trực tiếp ngay trên trình duyệt web chỉ với 1 cú click:

1. Mở trình duyệt web của bạn (Google Chrome, Microsoft Edge, Brave, Cốc Cốc...).
2. Truy cập vào trang quản lý tiện ích:
   * Trên **Chrome**: nhập `chrome://extensions` vào thanh địa chỉ.
   * Trên **Edge**: nhập `edge://extensions` vào thanh địa chỉ.
   * Trên **Cốc Cốc**: nhập `coccoc://extensions` vào thanh địa chỉ.
3. Gạt công tắc **Chế độ dành cho nhà phát triển (Developer mode)** ở góc trên bên phải sang **BẬT (ON)**.
4. Nhấn vào nút **Tải tiện ích đã giải nén (Load unpacked)** ở góc trên bên trái.
5. Trỏ đến thư mục:
   ```
   [Thư mục cài đặt]\extension
   ```
   *(Ví dụ: `C:\Program Files (x86)\Vortex Downloader\extension` hoặc thư mục `extension` trong mã nguồn).*
6. Nhấn **Chọn thư mục (Select Folder)**.
7. Biểu tượng tia chớp xoáy **Vortex Downloader** sẽ xuất hiện trên thanh công cụ của trình duyệt. Bạn hãy ghim (Pin) biểu tượng này lên thanh công cụ để dễ theo dõi.

---

## 3. Các phương thức tải xuống

Vortex Downloader hỗ trợ 4 cách linh hoạt để tải dữ liệu:

### 3.1 Tải qua nút nổi trên trình duyệt (Khuyên dùng)
Khi bạn xem bất kỳ video nào trên YouTube, TikTok, Facebook hay các trang mạng:
1. Một nút tải nổi màu xanh gradient với biểu tượng tia chớp `⚡ Tải Video` sẽ xuất hiện ngay phía trên trình phát video.
2. Di chuột vào nút tải hoặc nhấp chuột để mở danh sách độ phân giải có sẵn:
   * 🌟 **Best Quality:** Tự động lấy độ nét cao nhất có thể.
   * 🎬 **2160p (4K UHD), 1440p (2K), 1080p (Full HD), 720p (HD)...**
   * 🎵 **Audio MP3:** Tự động trích xuất âm thanh thành file MP3 chất lượng cao.
3. Nhấp chọn mức chất lượng mong muốn.
4. Hộp thoại Vortex Downloader trên Desktop sẽ tự động bật lên và điền sẵn thông số. Nhấn **🚀 Bắt đầu tải ngay** để tiến hành tải.

---

### 3.2 Tự động bắt link khi Copy (Clipboard Monitor)
1. Khi đang duyệt web, bạn chỉ cần bôi đen và nhấn `Ctrl + C` (hoặc chuột phải -> Copy link) bất kỳ đường dẫn video hay liên kết tệp tin nào.
2. Vortex Downloader đang chạy ngầm sẽ lập tức phát hiện liên kết hợp lệ và hiển thị thông báo:
   ```
   Phát hiện đường link vừa sao chép: https://...
   Bạn có muốn tải ngay bây giờ không?
   ```
3. Nhấn **Yes** để mở hộp thoại tải ngay lập tức.

---

### 3.3 Thêm liên kết thủ công
1. Trên giao diện chính của Vortex Downloader, nhấn nút lớn màu xanh dương **`＋ Thêm liên kết mới`** ở cột bên trái.
2. Dán đường link URL vào ô nhập liệu.
3. Nhấn nút **`🔍 Phân tích Video`**: hệ thống sẽ tự động quét thông tin video, dung lượng và các độ phân giải có sẵn từ máy chủ.
4. Lựa chọn thư mục lưu, số luồng tải và nhấn **`🚀 Bắt đầu tải ngay`**.

---

### 3.4 Tải file dữ liệu trực tiếp đa luồng (Direct Link)
Khi dán link tải trực tiếp (ví dụ file `.zip`, `.iso`, `.exe`, `.tar.gz`, `.mp4` từ Google Drive, OneDrive, Fshare, v.v.):
1. Hệ thống tự động nhận diện đây là liên kết file trực tiếp.
2. Kích hoạt engine **Core Engine HTTP Range**: chia tệp làm **16 luồng song song**.
3. Tốc độ tải sẽ được tối ưu hóa tối đa theo đường truyền internet của bạn.
4. Khi tải xong, hệ thống tự động ghép nối các phần lại thành 1 file hoàn chỉnh duy nhất mà không bị lỗi dữ liệu.

---

## 4. Lựa chọn định dạng, chất lượng & số luồng

Trong hộp thoại **Thêm URL Tải Xuống**, bạn có các tùy biến mạnh mẽ:

| Tùy chọn | Mô tả & Khuyến nghị |
| :--- | :--- |
| **🎯 Độ phân giải** | Lựa chọn từ 8K đến 144p hoặc MP3. Vortex **chỉ tải đúng 1 bản bạn chọn**, không tải thừa thãi gây tốn ổ cứng và băng thông. |
| **Số luồng tải (Threads)** | Số kết nối song song (từ 1 đến 32 luồng). Khuyến nghị để mặc định **16 luồng** để đạt tốc độ tối đa mà không bị máy chủ giới hạn. |
| **Thư mục lưu trữ** | Thư mục trên ổ cứng nơi file tải về sẽ được lưu (nhấn `📁 Chọn thư mục` để thay đổi). |
| **Tên file** | Tự động lấy theo tiêu đề video thực tế; bạn có thể chỉnh sửa lại tên theo ý muốn trước khi bắt đầu tải. |

---

## 5. Quản lý tác vụ trên giao diện Desktop

Giao diện chính được bố trí khoa học theo 2 phân vùng:

### 5.1 Bộ lọc danh mục thông minh (Sidebar bên trái)
* **📥 Tất cả tệp (N):** Xem toàn bộ lịch sử tải về.
* **⚡ Đang tải (N):** Chỉ xem các tiến trình đang hoạt động hoặc đang ghép nối.
* **✅ Đã hoàn thành (N):** Các tệp đã tải xong 100%.
* **⏸ Tạm dừng (N):** Các tệp đang ở trạng thái dừng tải tạm thời.
* **⚠️ Lỗi / Thất bại (N):** Các tệp bị lỗi kết nối hoặc link hết hạn.

*(Số đếm `(N)` tự động cập nhật thời gian thực theo trạng thái thực tế của tác vụ).*

---

### 5.2 Tìm kiếm tức thời (Live Search)
* Nhập từ khoá vào ô **`🔍 Tìm kiếm tệp...`** ở góc trên bên phải.
* Danh sách sẽ lọc ngay lập tức theo từng ký tự bạn gõ với độ trễ 0ms.
* Xoá ô tìm kiếm để danh sách hiển thị đầy đủ trở lại.

---

### 5.3 Các thao tác trên từng dòng tác vụ
Mỗi dòng tác vụ hiển thị: Icon loại tệp, Tên tệp, Dung lượng, Thanh tiến trình %, Tốc độ (MB/s), Thời gian còn lại, Huy hiệu trạng thái và Cột thao tác nhanh:

* **Mở tệp trực tiếp:** Nhấp đúp chuột (Double click) vào dòng tệp đã hoàn tất để mở ngay bằng phần mềm mặc định trên Windows.
* **📂 Nút Thư mục:** Mở thư mục chứa file trong Windows File Explorer và tự động trỏ tới đúng vị trí file.
* **⏸ Nút Tạm dừng:** Tạm dừng tiến trình tải đang chạy để nhường băng thông cho công việc khác.
* **▶ Nút Tiếp tục:** Tiếp tục tải lại phần còn lại mà không cần tải lại từ đầu (Resume support).
* **✕ Nút Xoá:** Xoá tác vụ này khỏi danh sách.
* **Menu chuột phải:** Nhấp chuột phải vào bất kỳ dòng nào để chọn các thao tác: *Tiếp tục tải, Tạm dừng, Mở tệp, Mở thư mục chứa tệp, Sao chép URL tải, Xoá khỏi danh sách*.

---

### 5.4 Thao tác hàng loạt (Batch Actions)
* **Chọn tất cả:** Nhấn nút **`☑ Chọn tất cả`** để tick chọn toàn bộ các tệp đang hiển thị.
* **Xoá nhiều tệp cùng lúc:** Tick chọn các ô checkbox ở cột đầu tiên, nút **`🗑 Xoá N đã chọn`** màu đỏ sẽ xuất hiện trên thanh công cụ. Nhấn vào đó để xóa toàn bộ các mục đã chọn trong nháy mắt (phản hồi 0ms).
* **Dọn dẹp Hoàn tất:** Nhấn nút **`✅ Dọn dẹp Hoàn tất`** ở góc dưới bên phải để xóa sạch tất cả tác vụ đã tải xong khỏi danh sách chỉ với 1 cú click.
* **Xoá mục Lỗi:** Nhấn nút **`⚠️ Xoá mục Lỗi`** để dọn các tác vụ hỏng.

---

## 6. Công cụ & Cài đặt hệ thống

Khu vực **CÔNG CỤ & CÀI ĐẶT** nằm ở góc dưới bên trái của thanh Sidebar:

### 6.1 Đổi thư mục lưu mặc định
* Nhấn vào **`⚙ Đổi thư mục lưu`**: một cửa sổ chọn thư mục sẽ mở ra.
* Chọn thư mục mong muốn (ví dụ `D:\Downloads` hoặc `E:\Phim`).
* Kể từ các lần tải sau, Vortex Downloader sẽ tự động ưu tiên lưu vào thư mục này.
* Nhấn **`📂 Thư mục tải về`** bất kỳ lúc nào để mở nhanh thư mục lưu mặc định.

---

### 6.2 Vượt cơ chế chặn Bot YouTube bằng Cookies
Một số video YouTube nhạy cảm, video giới hạn độ tuổi hoặc video 4K có thể yêu cầu đăng nhập tài khoản để xem. Nếu tải gặp lỗi `403 Forbidden` hoặc `Sign in to confirm you're not a bot`:
1. Trên trình duyệt Chrome/Edge, cài đặt tiện ích xuất cookie (ví dụ: *Get cookies.txt LOCALLY*).
2. Mở YouTube, đăng nhập tài khoản của bạn, sau đó xuất ra file `cookies.txt`.
3. Trong Vortex Downloader, nhấn nút **`🍪 Cookies YouTube`**.
4. Chọn file `cookies.txt` vừa xuất. Hệ thống sẽ tự động lưu và áp dụng cookie này cho mọi lượt tải tiếp theo, vượt qua 100% cơ chế chặn bot của YouTube.

---

### 6.3 Tự động khởi động cùng Windows
* Bạn có thể bật hoặc tắt tính năng này bất kỳ lúc nào bằng cách gạt checkbox **`🚀 Khởi động cùng Windows`** ở thanh Sidebar.
* Khi bật tính năng này: mỗi khi máy tính bật lên, Vortex Downloader sẽ tự động chạy ngầm dưới Khay hệ thống (System Tray) mà không mở bung cửa sổ làm gián đoạn công việc của bạn.

---

### 6.4 Điều khiển qua Khay hệ thống (System Tray)
Khi nhấn nút tắt `✕` trên góc cửa sổ chính, Vortex Downloader không bị tắt hẳn mà thu nhỏ êm ái xuống Khay hệ thống (gần đồng hồ Windows):
* **Nhấp đúp chuột vào icon khay:** Mở lại cửa sổ ứng dụng.
* **Chuột phải vào icon khay:** Mở menu điều khiển nhanh:
  * 🖥️ *Hiện giao diện chính*
  * 📂 *Mở thư mục tải về*
  * ➕ *Thêm liên kết mới*
  * ☑ *Khởi động cùng Windows* (đồng bộ 2 chiều)
  * 🚪 *Thoát hoàn toàn ứng dụng*

---

## 7. Khắc phục sự cố thường gặp (Troubleshooting)

### ❓ Trạng thái báo "○ Mất kết nối Gateway"
* **Nguyên nhân:** Dịch vụ API trung tâm đang khởi động hoặc cổng 8000 bị chặn bởi tường lửa/antivirus.
* **Cách xử lý:** 
  1. Đợi khoảng 2-3 giây để 3 vi dịch vụ backend hoàn tất khởi chạy.
  2. Nếu vẫn báo đỏ, mở Task Manager và kiểm tra xem các tiến trình `VortexDownloader.exe` có đang bị chặn không, hoặc khởi động lại ứng dụng.

### ❓ Tải video YouTube bị báo lỗi "403 Forbidden" hoặc tải chậm
* **Nguyên nhân:** YouTube đang hạn chế địa chỉ IP hoặc yêu cầu xác thực tài khoản xem video.
* **Cách xử lý:** Nhấn nút **`🍪 Cookies YouTube`** trên Sidebar và nạp tệp `cookies.txt` từ trình duyệt của bạn (xem mục 6.2).

### ❓ Dung lượng ổ đĩa bị tăng lên nhiều sau khi sử dụng lâu
* **Nguyên nhân:** Các video chất lượng cao (4K/8K) sau khi tải về sẽ chiếm bộ nhớ trên ổ cứng trong thư mục tải về của bạn.
* **Cách xử lý:** Nhấn nút **`📂 Thư mục tải về`** trên Sidebar để vào thư mục `Downloads` và xóa bớt các file video cũ không còn nhu cầu xem.

---

<div align="center">
  <b>Vortex Downloader Engine Pro • 2026 Edition</b><br>
  <i>Tải nhanh hơn • Thiết kế tinh tế hơn • Ổn định tối đa</i>
</div>
