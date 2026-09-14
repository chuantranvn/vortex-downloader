(function () {
    "use strict";

    const GATEWAY_URL = "http://localhost:8000";
    const ICON_DATA_URI = "data:image/png;base64,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";

    // Quản lý video đã bị người dùng ấn tắt hẳn
    const dismissedUrls = new Set();

    function getCleanUrl() {
        try {
            const u = new URL(window.location.href);
            // Với YouTube, chỉ lấy ?v=... để giữ đồng nhất
            if (u.searchParams.has("v")) {
                return `${u.origin}${u.pathname}?v=${u.searchParams.get("v")}`;
            }
            return `${u.origin}${u.pathname}`;
        } catch (e) {
            return window.location.href;
        }
    }

    function isCurrentUrlDismissed() {
        const clean = getCleanUrl();
        return dismissedUrls.has(clean);
    }

    function dismissCurrentUrl() {
        const clean = getCleanUrl();
        dismissedUrls.add(clean);
    }

    function undismissCurrentUrl() {
        const clean = getCleanUrl();
        dismissedUrls.delete(clean);
        try {
            sessionStorage.removeItem("vortex_dismissed_" + clean);
            sessionStorage.removeItem("vortex_minimized_" + clean);
        } catch (e) {}
    }

    function isCurrentUrlMinimized() {
        const clean = getCleanUrl();
        try {
            return sessionStorage.getItem("vortex_minimized_" + clean) === "1";
        } catch (e) {
            return false;
        }
    }

    function setMinimizedState(minimized) {
        const clean = getCleanUrl();
        try {
            if (minimized) {
                sessionStorage.setItem("vortex_minimized_" + clean, "1");
            } else {
                sessionStorage.removeItem("vortex_minimized_" + clean);
            }
        } catch (e) {}
    }

    function formatBytes(bytes) {
        if (!bytes || bytes <= 0) return "";
        const units = ["B", "KB", "MB", "GB"];
        let size = bytes;
        let unitIdx = 0;
        while (size >= 1024 && unitIdx < units.length - 1) {
            size /= 1024;
            unitIdx++;
        }
        return `~${size.toFixed(unitIdx === 3 ? 1 : 0)} ${units[unitIdx]}`;
    }

    function showToast(message, isSuccess = true) {
        const existing = document.querySelector(".vortex-toast");
        if (existing) existing.remove();

        const toast = document.createElement("div");
        toast.className = "vortex-toast";
        if (!isSuccess) {
            toast.style.borderColor = "#f38ba8";
            toast.style.color = "#f38ba8";
        }
        toast.innerHTML = `
            <span>${isSuccess ? "⚡" : "⚠️"}</span>
            <span>${message}</span>
        `;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transition = "opacity 0.4s ease";
            setTimeout(() => toast.remove(), 400);
        }, 3500);
    }

    function documentCookieToNetscape() {
        try {
            if (!document.cookie) return "";
            const parts = document.cookie.split(";");
            let lines = [
                "# Netscape HTTP Cookie File",
                "# Fallback from document.cookie",
                ""
            ];
            const expiry = Math.floor(Date.now() / 1000) + 31536000;
            for (const p of parts) {
                const eq = p.indexOf("=");
                if (eq > 0) {
                    const name = p.substring(0, eq).trim();
                    const value = p.substring(eq + 1).trim();
                    lines.push(`.youtube.com\tTRUE\t/\tTRUE\t${expiry}\t${name}\t${value}`);
                }
            }
            return lines.join("\n") + "\n";
        } catch (e) {
            return "";
        }
    }

    function requestCookies() {
        return new Promise((resolve) => {
            try {
                chrome.runtime.sendMessage({ type: "GET_NETSCAPE_COOKIES" }, (response) => {
                    if (chrome.runtime.lastError || !response || !response.cookies) {
                        // Fallback sang document.cookie nếu service worker chưa phản hồi
                        const fallback = documentCookieToNetscape();
                        resolve(fallback);
                    } else {
                        resolve(response.cookies);
                    }
                });
            } catch (e) {
                resolve(documentCookieToNetscape());
            }
        });
    }

    async function triggerDownload(formatId = null) {
        const videoUrl = getCleanUrl();
        showToast("⚡ Đang mở hộp thoại tải xuống Vortex...", true);

        const cookies = await requestCookies();

        // Lấy folder lưu trữ từ storage
        let saveFolder = null;
        try {
            const stored = await chrome.storage.local.get("vortex_save_folder");
            if (stored.vortex_save_folder) {
                saveFolder = stored.vortex_save_folder;
            }
        } catch (e) {}

        // Lấy tiêu đề video từ trang YouTube hiện tại
        let videoTitle = "";
        try {
            const titleEl = document.querySelector("h1.ytd-watch-metadata yt-formatted-string, #title h1, h1.title");
            if (titleEl && titleEl.textContent.trim()) {
                videoTitle = titleEl.textContent.trim();
            } else if (document.title) {
                videoTitle = document.title.replace(/ - YouTube$/, "").trim();
            }
        } catch (e) {}

        try {
            const payload = {
                url: videoUrl,
                format_id: formatId,
                cookies: cookies,
                title: videoTitle
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
                showToast("✨ Đã mở hộp thoại tải xuống Vortex trên máy tính!", true);
            } else {
                showToast("Lỗi: Không thể gửi yêu cầu mở hộp thoại đến Gateway!", false);
            }
        } catch (err) {
            showToast("Vortex Downloader chưa bật! Hãy chạy run_app.py", false);
        }
    }

    // Cache kết quả trích xuất theo clean URL
    const qualityCache = new Map();

    async function fetchVideoQualities(videoUrl, menuElement, statusElement) {
        const clean = getCleanUrl();
        if (qualityCache.has(clean)) {
            renderQualities(qualityCache.get(clean), menuElement, statusElement);
            return;
        }

        const cookies = await requestCookies();

        try {
            if (statusElement) statusElement.textContent = "⏳ Đang dò tất cả chất lượng...";
            const res = await fetch(`${GATEWAY_URL}/api/v1/extract`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: videoUrl, cookies: cookies })
            });

            if (!res.ok) {
                if (statusElement) statusElement.textContent = "⚡ Sẵn sàng tải với các mức chuẩn";
                return;
            }

            const data = await res.json();
            if (data && Array.isArray(data.formats) && data.formats.length > 0) {
                qualityCache.set(clean, data);
                renderQualities(data, menuElement, statusElement);
            } else {
                if (statusElement) statusElement.textContent = "⚡ Sẵn sàng tải các mức chuẩn";
            }
        } catch (e) {
            if (statusElement) statusElement.textContent = "⚡ Sẵn sàng tải các mức chuẩn";
        }
    }

    async function setupFolderRow(menuElement) {
        if (!menuElement) return;
        let storedFolder = null;
        try {
            const stored = await chrome.storage.local.get("vortex_save_folder");
            storedFolder = stored.vortex_save_folder;
        } catch (e) {}

        const display = storedFolder
            ? (storedFolder.length > 25 ? "..." + storedFolder.slice(-22) : storedFolder)
            : "Mặc định (downloads/)";

        const oldRow = menuElement.querySelector(".vortex-folder-row");
        const oldDivider = menuElement.querySelector(".vortex-folder-divider");
        if (oldRow) oldRow.remove();
        if (oldDivider) oldDivider.remove();

        const divider = document.createElement("div");
        divider.className = "vortex-menu-divider vortex-folder-divider";

        const folderRow = document.createElement("div");
        folderRow.className = "vortex-folder-row";
        folderRow.title = `Thư mục lưu hiện tại: ${storedFolder || 'Mặc định (downloads/)'}`;
        folderRow.innerHTML = `
            <span class="vortex-folder-icon">📁</span>
            <span class="vortex-folder-text">${display}</span>
            <button type="button" class="vortex-btn-change-folder" title="Đổi thư mục lưu trữ video trên máy tính">Đổi</button>
        `;

        const btnChange = folderRow.querySelector(".vortex-btn-change-folder");
        btnChange.addEventListener("click", async (e) => {
            e.stopPropagation();
            btnChange.disabled = true;
            btnChange.textContent = "⏳...";
            showToast("Đang mở hộp thoại chọn thư mục trên máy tính...", true);

            try {
                const res = await fetch(`${GATEWAY_URL}/api/v1/system/browse_folder`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.status === "ok" && data.folder) {
                        await chrome.storage.local.set({ vortex_save_folder: data.folder });
                        showToast(`📁 Đã đổi thư mục lưu: ${data.folder}`, true);
                        const folderText = folderRow.querySelector(".vortex-folder-text");
                        if (folderText) {
                            folderText.textContent = data.folder.length > 25 ? "..." + data.folder.slice(-22) : data.folder;
                            folderRow.title = `Thư mục lưu hiện tại: ${data.folder}`;
                        }
                    }
                } else {
                    showToast("Không thể mở hộp thoại chọn thư mục!", false);
                }
            } catch (err) {
                showToast("Vortex Downloader chưa bật! Hãy chạy run_app.py", false);
            } finally {
                btnChange.disabled = false;
                btnChange.textContent = "Đổi";
            }
        });

        menuElement.appendChild(divider);
        menuElement.appendChild(folderRow);
    }

    function renderQualities(data, menuElement, statusElement) {
        const formats = data.formats || [];
        const heightMap = new Map();
        let maxAudioSize = 0;

        for (const f of formats) {
            const fsize = f.filesize_approx || f.filesize || 0;
            if (f.resolution === "audio only" || f.vcodec === "none") {
                if (fsize > maxAudioSize) maxAudioSize = fsize;
            }

            let h = null;
            if (f.resolution && f.resolution.includes("x")) {
                const parts = f.resolution.split("x");
                h = parseInt(parts[1], 10);
            } else if (f.format_note && /^\d+p/.test(f.format_note)) {
                h = parseInt(f.format_note, 10);
            }

            if (h && !isNaN(h) && h >= 144) {
                if (!heightMap.has(h) || fsize > (heightMap.get(h).filesize || 0)) {
                    heightMap.set(h, {
                        height: h,
                        filesize: fsize,
                        fps: f.fps || 30,
                        note: f.format_note || `${h}p`
                    });
                }
            }
        }

        const sortedHeights = Array.from(heightMap.keys()).sort((a, b) => b - a);
        if (sortedHeights.length === 0) {
            if (statusElement) statusElement.textContent = "⚡ Sẵn sàng tải các mức chuẩn";
            return;
        }

        // Định dạng nhãn đẹp theo chuẩn công nghệ
        function getQualityBadge(h) {
            if (h >= 4320) return { icon: "🎬", label: `${h}p (8K UHD)` };
            if (h >= 2160) return { icon: "🎬", label: `${h}p (4K UHD)` };
            if (h >= 1440) return { icon: "🎬", label: `${h}p (2K QHD)` };
            if (h >= 1080) return { icon: "🖥️", label: `${h}p Full HD` };
            if (h >= 720) return { icon: "📺", label: `${h}p HD` };
            if (h >= 480) return { icon: "📱", label: `${h}p SD` };
            if (h >= 360) return { icon: "📱", label: `${h}p` };
            return { icon: "📱", label: `${h}p` };
        }

        let html = `
            <div class="vortex-menu-item" data-format="bestvideo+bestaudio/best">
                <div class="vortex-item-left">
                    <span>🌟</span>
                    <span>Chất lượng tốt nhất (${sortedHeights[0]}p)</span>
                </div>
            </div>
            <div class="vortex-menu-divider"></div>
        `;

        for (const h of sortedHeights) {
            const info = heightMap.get(h);
            const badge = getQualityBadge(h);
            const totalEstimatedBytes = (info.filesize > 0) ? (info.filesize + maxAudioSize) : 0;
            const sizeStr = formatBytes(totalEstimatedBytes);

            html += `
                <div class="vortex-menu-item" data-format="bestvideo[height<=${h}]+bestaudio/best">
                    <div class="vortex-item-left">
                        <span>${badge.icon}</span>
                        <span>${badge.label}</span>
                    </div>
                    ${sizeStr ? `<span class="vortex-item-size">${sizeStr}</span>` : ""}
                </div>
            `;
        }

        const audioSizeStr = formatBytes(maxAudioSize);
        html += `
            <div class="vortex-menu-divider"></div>
            <div class="vortex-menu-item" data-format="audio_only">
                <div class="vortex-item-left">
                    <span>🎵</span>
                    <span>Chỉ tải MP3 (Âm thanh)</span>
                </div>
                ${audioSizeStr ? `<span class="vortex-item-size">${audioSizeStr}</span>` : ""}
            </div>
        `;

        menuElement.innerHTML = html;
        setupFolderRow(menuElement);

        // Gán lại sự kiện click cho các item mới
        const container = menuElement.closest(".vortex-floating-container");
        menuElement.querySelectorAll(".vortex-menu-item").forEach((item) => {
            item.addEventListener("click", (e) => {
                e.stopPropagation();
                if (container) container.classList.remove("open");
                const fmt = item.getAttribute("data-format");
                triggerDownload(fmt);
            });
        });

        if (statusElement) {
            statusElement.textContent = `✅ Tìm thấy ${sortedHeights.length} mức độ phân giải`;
        }
    }

    function createFloatingBar() {
        const container = document.createElement("div");
        container.className = "vortex-floating-container";
        if (isCurrentUrlMinimized()) {
            container.classList.add("minimized");
        }
        container.innerHTML = `
            <div class="vortex-btn-group">
                <div class="vortex-download-btn" title="Bấm để chọn chất lượng tải">
                    <img src="${ICON_DATA_URI}" class="vortex-btn-icon" alt="Vortex" />
                    <span>Tải video này</span>
                    <span class="vortex-btn-arrow">▼</span>
                </div>
                <div class="vortex-close-btn" title="Thu nhỏ thanh tải">✕</div>
            </div>
            <div class="vortex-mini-badge" title="Vortex Downloader - Bấm để mở lại (chuột phải để ẩn hẳn)">
                <img src="${ICON_DATA_URI}" class="vortex-mini-icon" alt="Vortex" />
                <span class="vortex-mini-dot"></span>
            </div>
            <div class="vortex-dropdown-menu">
                <div class="vortex-menu-item" data-format="bestvideo+bestaudio/best">
                    <div class="vortex-item-left">
                        <span>🌟</span>
                        <span>Chất lượng tốt nhất</span>
                    </div>
                </div>
                <div class="vortex-menu-item" data-format="bestvideo[height<=4320]+bestaudio/best">
                    <div class="vortex-item-left">
                        <span>🎬</span>
                        <span>4320p (8K UHD)</span>
                    </div>
                </div>
                <div class="vortex-menu-item" data-format="bestvideo[height<=2160]+bestaudio/best">
                    <div class="vortex-item-left">
                        <span>🎬</span>
                        <span>2160p (4K UHD)</span>
                    </div>
                </div>
                <div class="vortex-menu-item" data-format="bestvideo[height<=1440]+bestaudio/best">
                    <div class="vortex-item-left">
                        <span>🎬</span>
                        <span>1440p (2K QHD)</span>
                    </div>
                </div>
                <div class="vortex-menu-item" data-format="bestvideo[height<=1080]+bestaudio/best">
                    <div class="vortex-item-left">
                        <span>🖥️</span>
                        <span>1080p Full HD</span>
                    </div>
                </div>
                <div class="vortex-menu-item" data-format="bestvideo[height<=720]+bestaudio/best">
                    <div class="vortex-item-left">
                        <span>📺</span>
                        <span>720p HD</span>
                    </div>
                </div>
                <div class="vortex-menu-item" data-format="bestvideo[height<=480]+bestaudio/best">
                    <div class="vortex-item-left">
                        <span>📱</span>
                        <span>480p SD</span>
                    </div>
                </div>
                <div class="vortex-menu-item" data-format="bestvideo[height<=360]+bestaudio/best">
                    <div class="vortex-item-left">
                        <span>📱</span>
                        <span>360p</span>
                    </div>
                </div>
                <div class="vortex-menu-divider"></div>
                <div class="vortex-menu-item" data-format="audio_only">
                    <div class="vortex-item-left">
                        <span>🎵</span>
                        <span>Chỉ tải MP3 (Âm thanh)</span>
                    </div>
                </div>
                <div class="vortex-menu-status">⏳ Đang lấy danh sách chất lượng...</div>
            </div>
        `;

        // Ngăn chặn sự kiện nổi bọt lên video player (tránh pause/play video ngoài ý muốn)
        container.addEventListener("click", (e) => e.stopPropagation());
        container.addEventListener("mousedown", (e) => e.stopPropagation());

        const mainBtn = container.querySelector(".vortex-download-btn");
        const closeBtn = container.querySelector(".vortex-close-btn");
        const miniBadge = container.querySelector(".vortex-mini-badge");
        const dropdownMenu = container.querySelector(".vortex-dropdown-menu");
        const statusEl = container.querySelector(".vortex-menu-status");
        setupFolderRow(dropdownMenu);

        // Bấm vào nút tải -> Bật/Tắt menu chọn chất lượng
        mainBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            container.classList.toggle("open");
        });

        // Bấm nút X -> Thu nhỏ thanh tải thành icon mini ở góc
        closeBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            container.classList.remove("open");
            container.classList.add("minimized");
            setMinimizedState(true);
            showToast("Đã thu nhỏ thanh tải. Bấm vào icon ở góc để mở lại!", true);
        });

        // Bấm chuột trái vào mini badge -> Bung mở lại thanh tải
        miniBadge.addEventListener("click", (e) => {
            e.stopPropagation();
            container.classList.remove("minimized");
            setMinimizedState(false);
            showToast("Đã mở lại thanh tải Vortex!", true);
        });

        // Bấm chuột phải vào mini badge -> Ẩn hẳn (vẫn có thể mở lại từ Popup Extension)
        miniBadge.addEventListener("contextmenu", (e) => {
            e.preventDefault();
            e.stopPropagation();
            dismissCurrentUrl();
            container.style.transition = "all 0.2s ease";
            container.style.opacity = "0";
            container.style.transform = "scale(0.85)";
            setTimeout(() => {
                if (container.parentElement) container.remove();
            }, 200);
            showToast("Đã ẩn thanh tải. Bạn có thể mở lại từ icon tiện ích Vortex!", true);
        });

        // Hover mượt mà với thời gian trễ 250ms khi rời chuột (tránh mất menu khi lia chuột nhanh)
        let closeTimer = null;
        container.addEventListener("mouseenter", () => {
            if (closeTimer) clearTimeout(closeTimer);
        });
        container.addEventListener("mouseleave", () => {
            closeTimer = setTimeout(() => {
                container.classList.remove("open");
            }, 250);
        });

        // Đóng dropdown khi click bên ngoài trang web
        document.addEventListener("click", (e) => {
            if (!container.contains(e.target)) {
                container.classList.remove("open");
            }
        });

        // Sự kiện click cho các item mặc định ban đầu
        container.querySelectorAll(".vortex-menu-item").forEach((item) => {
            item.addEventListener("click", (e) => {
                e.stopPropagation();
                container.classList.remove("open");
                const fmt = item.getAttribute("data-format");
                triggerDownload(fmt);
            });
        });

        // Tự động trích xuất các chất lượng cụ thể theo thời gian thực
        fetchVideoQualities(window.location.href, dropdownMenu, statusEl);

        return container;
    }

    let lastKnownUrl = window.location.href;

    function injectFloatingBar() {
        if (isCurrentUrlDismissed()) {
            // Đã bị người dùng bấm X đóng trên video này
            const existing = document.querySelector(".vortex-floating-container");
            if (existing) existing.remove();
            return;
        }

        // Kiểm tra xem trang có đổi URL (YouTube SPA) không
        if (window.location.href !== lastKnownUrl) {
            lastKnownUrl = window.location.href;
            const existing = document.querySelector(".vortex-floating-container");
            if (existing) existing.remove();
            if (isCurrentUrlDismissed()) return;
        }

        // Ưu tiên YouTube Player
        const ytPlayer = document.querySelector("#movie_player") || document.querySelector(".html5-video-player");
        if (ytPlayer) {
            if (!ytPlayer.querySelector(".vortex-floating-container")) {
                ytPlayer.style.position = "relative";
                ytPlayer.appendChild(createFloatingBar());
            }
            return;
        }

        // Các trang web chứa thẻ <video> khác
        const videos = document.querySelectorAll("video");
        for (const vid of videos) {
            const parent = vid.parentElement;
            if (parent && !parent.querySelector(".vortex-floating-container")) {
                const rect = vid.getBoundingClientRect();
                if (rect.width > 220 && rect.height > 160) {
                    const style = window.getComputedStyle(parent);
                    if (style.position === "static") {
                        parent.style.position = "relative";
                    }
                    parent.appendChild(createFloatingBar());
                    break;
                }
            }
        }
    }

    // Lắng nghe sự kiện chuyển video của YouTube (SPA)
    window.addEventListener("yt-navigate-finish", () => {
        lastKnownUrl = window.location.href;
        const existing = document.querySelector(".vortex-floating-container");
        if (existing) existing.remove();
        setTimeout(injectFloatingBar, 500);
    });

    window.addEventListener("popstate", () => {
        setTimeout(injectFloatingBar, 500);
    });

    setTimeout(injectFloatingBar, 1000);

    const observer = new MutationObserver(() => {
        injectFloatingBar();
    });
    observer.observe(document.body, { childList: true, subtree: true });

    // Lắng nghe lệnh từ Popup Extension
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.action === "RESTORE_FLOATING_BAR") {
            undismissCurrentUrl();
            setMinimizedState(false);

            let container = document.querySelector(".vortex-floating-container");
            if (container) {
                container.classList.remove("minimized");
                container.style.opacity = "1";
                container.style.transform = "none";
                container.classList.add("open");
                setTimeout(() => container.classList.remove("open"), 3000);
            } else {
                injectFloatingBar();
                setTimeout(() => {
                    const c = document.querySelector(".vortex-floating-container");
                    if (c) {
                        c.classList.remove("minimized");
                        c.classList.add("open");
                        setTimeout(() => c.classList.remove("open"), 3000);
                    }
                }, 100);
            }
            showToast("⚡ Đã hiển thị lại thanh tải Vortex!", true);
            sendResponse({ success: true });
            return true;
        }
    });

})();
