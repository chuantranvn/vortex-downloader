const GATEWAY_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", async () => {
    const statusBadge = document.getElementById("gateway-status");
    const tabTitleEl = document.getElementById("tab-title");
    const btnQuick = document.getElementById("btn-quick-download");
    const btnAudio = document.getElementById("btn-audio-download");
    const statusMsg = document.getElementById("status-message");

    let currentUrl = "";

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

    async function sendDownload(formatId = null) {
        if (!currentUrl || currentUrl.startsWith("chrome://")) {
            statusMsg.style.color = "#f38ba8";
            statusMsg.innerText = "Không thể tải từ trang hệ thống của trình duyệt!";
            return;
        }

        statusMsg.style.color = "#f9e2af";
        statusMsg.innerText = "Đang gửi lệnh tải...";

        try {
            const res = await fetch(`${GATEWAY_URL}/api/v1/download`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    url: currentUrl,
                    format_id: formatId
                })
            });

            if (res.ok) {
                const data = await res.json();
                statusMsg.style.color = "#a6e3a1";
                statusMsg.innerText = `Đã bắt đầu tải: ${data.file_name.substring(0, 25)}...`;
            } else {
                statusMsg.style.color = "#f38ba8";
                statusMsg.innerText = "Lỗi khi gửi yêu cầu tải!";
            }
        } catch {
            statusMsg.style.color = "#f38ba8";
            statusMsg.innerText = "Không thể kết nối đến Vortex Downloader!";
        }
    }

    btnQuick.addEventListener("click", () => sendDownload("bestvideo+bestaudio/best"));
    btnAudio.addEventListener("click", () => sendDownload("audio_only"));
});
