const GATEWAY_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", async () => {
    const statusBadge = document.getElementById("gateway-status");
    const tabTitleEl = document.getElementById("tab-title");
    const btnQuick = document.getElementById("btn-quick-download");
    const btnAudio = document.getElementById("btn-audio-download");
    const btnRestore = document.getElementById("btn-restore-bar");
    const statusMsg = document.getElementById("status-message");
    const folderInput = document.getElementById("save-folder");
    const btnSaveFolder = document.getElementById("btn-save-folder");
    const btnBrowseFolder = document.getElementById("btn-browse-folder");

    let currentUrl = "";

    // Load saved folder từ storage, nếu chưa có thì lấy default từ gateway
    try {
        const stored = await chrome.storage.local.get("vortex_save_folder");
        if (stored.vortex_save_folder) {
            folderInput.value = stored.vortex_save_folder;
        } else {
            fetch(`${GATEWAY_URL}/api/v1/system/settings`)
                .then(r => r.json())
                .then(data => {
                    if (data.default_download_dir) {
                        folderInput.placeholder = `Mặc định: ${data.default_download_dir}`;
                    }
                })
                .catch(() => {});
        }
    } catch (e) {}

    // Chọn folder từ hộp thoại hệ thống
    if (btnBrowseFolder) {
        btnBrowseFolder.addEventListener("click", async () => {
            btnBrowseFolder.disabled = true;
            btnBrowseFolder.innerText = "⏳...";
            statusMsg.style.color = "#f9e2af";
            statusMsg.innerText = "Đang mở cửa sổ chọn thư mục trên máy tính...";
            try {
                const res = await fetch(`${GATEWAY_URL}/api/v1/system/browse_folder`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.status === "ok" && data.folder) {
                        folderInput.value = data.folder;
                        await chrome.storage.local.set({ vortex_save_folder: data.folder });
                        statusMsg.style.color = "#a6e3a1";
                        statusMsg.innerText = `📁 Đã chọn: ${data.folder}`;
                        setTimeout(() => { statusMsg.innerText = ""; }, 3000);
                    } else {
                        statusMsg.innerText = "";
                    }
                } else {
                    statusMsg.style.color = "#f38ba8";
                    statusMsg.innerText = "Không thể mở hộp thoại chọn thư mục!";
                }
            } catch (err) {
                statusMsg.style.color = "#f38ba8";
                statusMsg.innerText = "Vortex Downloader chưa bật! Hãy chạy run_app.py";
            } finally {
                btnBrowseFolder.disabled = false;
                btnBrowseFolder.innerText = "📂 Chọn";
            }
        });
    }

    // Lưu folder khi bấm nút save
    btnSaveFolder.addEventListener("click", () => {
        const folder = folderInput.value.trim();
        chrome.storage.local.set({ vortex_save_folder: folder }, () => {
            statusMsg.style.color = "#a6e3a1";
            statusMsg.innerText = folder
                ? `💾 Đã lưu thư mục: ${folder}`
                : "💾 Đã đặt về thư mục mặc định";
            setTimeout(() => { statusMsg.innerText = ""; }, 2500);
        });
    });

    // Lưu folder khi nhấn Enter
    folderInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") btnSaveFolder.click();
    });

    // 1. Kiểm tra trạng thái Gateway
    try {
        const res = await fetch(`${GATEWAY_URL}/health`);
        if (res.ok) {
            statusBadge.className = "status-badge online";
            statusBadge.innerText = "● Gateway Đang Hoạt Động";
        } else {
            throw new Error();
        }
    } catch {
        statusBadge.className = "status-badge offline";
        statusBadge.innerText = "○ Vortex Downloader Chưa Bật";
    }

    // 2. Lấy thông tin tab đang xem
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab) {
        currentUrl = tab.url;
        tabTitleEl.innerText = tab.title || currentUrl;
    }

    function requestCookies() {
        return new Promise((resolve) => {
            try {
                chrome.runtime.sendMessage({ type: "GET_NETSCAPE_COOKIES" }, (response) => {
                    if (chrome.runtime.lastError || !response) {
                        resolve("");
                    } else {
                        resolve(response.cookies || "");
                    }
                });
            } catch (e) {
                resolve("");
            }
        });
    }

    async function getSaveFolder() {
        try {
            const stored = await chrome.storage.local.get("vortex_save_folder");
            return stored.vortex_save_folder || null;
        } catch (e) {
            return null;
        }
    }

    async function sendDownload(formatId = null) {
        if (!currentUrl || currentUrl.startsWith("chrome://") || currentUrl.startsWith("edge://")) {
            statusMsg.style.color = "#f38ba8";
            statusMsg.innerText = "Không thể tải từ trang hệ thống của trình duyệt!";
            return;
        }

        statusMsg.style.color = "#f9e2af";
        statusMsg.innerText = "⚡ Đang mở hộp thoại tải xuống...";

        const cookies = await requestCookies();
        const saveFolder = await getSaveFolder();
        const title = tabTitleEl ? tabTitleEl.innerText.replace(/ - YouTube$/, "").trim() : "";

        try {
            const payload = {
                url: currentUrl,
                format_id: formatId,
                cookies: cookies,
                title: title
            };
            if (saveFolder) {
                payload.save_path = saveFolder;
            }

            const res = await fetch(`${GATEWAY_URL}/api/v1/system/open_add_dialog`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                statusMsg.style.color = "#a6e3a1";
                statusMsg.innerText = "✨ Đã mở hộp thoại tải xuống Vortex!";
            } else {
                statusMsg.style.color = "#f38ba8";
                statusMsg.innerText = "Lỗi khi gửi yêu cầu mở hộp thoại!";
            }
        } catch {
            statusMsg.style.color = "#f38ba8";
            statusMsg.innerText = "Không thể kết nối đến Vortex Downloader!";
        }
    }

    btnQuick.addEventListener("click", () => sendDownload("bestvideo+bestaudio/best"));
    btnAudio.addEventListener("click", () => sendDownload("audio_only"));

    if (btnRestore) {
        btnRestore.addEventListener("click", () => {
            if (!tab || !tab.id) {
                statusMsg.style.color = "#f38ba8";
                statusMsg.innerText = "Không tìm thấy tab hiện tại!";
                return;
            }

            if (!currentUrl || currentUrl.startsWith("chrome://") || currentUrl.startsWith("edge://")) {
                statusMsg.style.color = "#f38ba8";
                statusMsg.innerText = "Không thể chạy trên trang hệ thống!";
                return;
            }

            statusMsg.style.color = "#f9e2af";
            statusMsg.innerText = "Đang gửi lệnh khôi phục...";

            chrome.tabs.sendMessage(tab.id, { action: "RESTORE_FLOATING_BAR" }, (response) => {
                if (chrome.runtime.lastError) {
                    statusMsg.style.color = "#f38ba8";
                    statusMsg.innerText = "Không thể kết nối trang! (Hãy F5 trang video)";
                } else {
                    statusMsg.style.color = "#a6e3a1";
                    statusMsg.innerText = "⚡ Đã khôi phục thanh tải nổi!";
                }
            });
        });
    }
});
