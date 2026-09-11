// Vortex Downloader - Background Service Worker
chrome.runtime.onInstalled.addListener(() => {
    console.log("Vortex Downloader Integration Module đã được cài đặt thành công!");
});

// Lắng nghe lệnh từ Content Script hoặc Popup nếu cần
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "CHECK_GATEWAY") {
        fetch("http://localhost:8000/health")
            .then(res => res.json())
            .then(data => sendResponse({ online: true, data }))
            .catch(() => sendResponse({ online: false }));
        return true; // Cho phép async sendResponse
    }
});
