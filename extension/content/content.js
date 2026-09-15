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

    function isPlatformSite() {
        const host = window.location.hostname.toLowerCase();
        return host.includes("youtube.com") || host.includes("youtu.be") ||
               host.includes("tiktok.com") ||
               host.includes("facebook.com") || host.includes("fb.watch") ||
               host.includes("instagram.com") ||
               host.includes("twitter.com") || host.includes("x.com") ||
               host.includes("twitch.tv") ||
               host.includes("vimeo.com") ||
               host.includes("soundcloud.com");
    }

    function getMediaTitle() {
        try {
            // YouTube title
            const ytTitle = document.querySelector("h1.ytd-watch-metadata yt-formatted-string, #title h1, h1.title");
            if (ytTitle && ytTitle.textContent.trim()) return ytTitle.textContent.trim();

            // Tin tức báo chí & web xem phim
            const pageH1 = document.querySelector("h1.title-detail, h1.title-news, h1.article-title, h1.entry-title, h1.film-title, h1");
            if (pageH1 && pageH1.textContent.trim()) {
                return pageH1.textContent.trim();
            }

            if (document.title) {
                return document.title
                    .replace(/ - YouTube$/i, "")
                    .replace(/ - VnExpress$/i, "")
                    .replace(/ \| Báo Dân trí$/i, "")
                    .replace(/ - Tuổi Trẻ Online$/i, "")
                    .trim();
            }
        } catch (e) {}
        return "Video_" + Math.floor(Date.now() / 1000);
    }

    async function resolveMediaSource(videoEl) {
        // Tầng 1: Thuộc tính trực tiếp của thẻ <video>
        if (videoEl) {
            if (videoEl.currentSrc && !videoEl.currentSrc.startsWith("blob:") && /^https?:\/\//i.test(videoEl.currentSrc)) {
                return { url: videoEl.currentSrc, type: videoEl.currentSrc.includes(".m3u8") ? "m3u8" : "direct" };
            }
            if (videoEl.src && !videoEl.src.startsWith("blob:") && /^https?:\/\//i.test(videoEl.src)) {
                return { url: videoEl.src, type: videoEl.src.includes(".m3u8") ? "m3u8" : "direct" };
            }
            const sources = videoEl.querySelectorAll("source");
            for (const s of sources) {
                const src = s.src || s.getAttribute("src");
                if (src && !src.startsWith("blob:") && /^https?:\/\//i.test(src)) {
                    return { url: src, type: src.includes(".m3u8") ? "m3u8" : "direct" };
                }
            }

            // Tầng 2: Data attributes trên thẻ video hoặc container bao bọc
            const containers = [videoEl, videoEl.parentElement, videoEl.closest(".player, .video-player, .jwplayer, .vjs-tech")].filter(Boolean);
            for (const c of containers) {
                for (const attr of ["data-src", "data-video-src", "data-url", "data-hls-src", "data-hls", "data-mp4", "data-file"]) {
                    const val = c.getAttribute(attr);
                    if (val && !val.startsWith("blob:") && /^https?:\/\//i.test(val)) {
                        return { url: val, type: val.includes(".m3u8") ? "m3u8" : "direct" };
                    }
                }
            }
        }

        // Tầng 3: Performance Resource Timing (bắt .m3u8, .ts, .mp4 trong các request vừa nạp)
        try {
            const entries = window.performance.getEntriesByType("resource");
            let m3u8Url = null;
            let tsUrl = null;
            let mp4Url = null;

            for (let i = entries.length - 1; i >= 0; i--) {
                const name = entries[i].name;
                if (!name || name.startsWith("blob:") || name.startsWith("data:")) continue;
                if (/\.m3u8(?:\?.*)?$/i.test(name) || name.includes(".m3u8")) {
                    m3u8Url = name;
                    break;
                } else if (/\.mp4(?:\?.*)?$/i.test(name)) {
                    if (!mp4Url) mp4Url = name;
                } else if (/\.ts(?:\?.*)?$/i.test(name)) {
                    if (!tsUrl) tsUrl = name;
                }
            }

            if (m3u8Url) return { url: m3u8Url, type: "m3u8" };
            if (mp4Url) return { url: mp4Url, type: "direct" };
            if (tsUrl) return { url: tsUrl, type: "ts" };
        } catch (e) {}

        // Tầng 4: Background Sniffer (webRequest trên tab này)
        try {
            const bgResp = await new Promise((res) => {
                chrome.runtime.sendMessage({ type: "GET_TAB_MEDIA" }, (resp) => {
                    res(resp && resp.media ? resp.media : []);
                });
            });

            if (bgResp && bgResp.length > 0) {
                const m3u8 = bgResp.find(m => m.isPlaylist || m.url.includes(".m3u8"));
                if (m3u8) return { url: m3u8.url, type: "m3u8" };

                const mp4 = bgResp.find(m => m.isDirectMp4 || m.url.includes(".mp4"));
                if (mp4) return { url: mp4.url, type: "direct" };

                const ts = bgResp.find(m => m.isTsSegment || m.url.includes(".ts"));
                if (ts) return { url: ts.url, type: "ts" };

                return { url: bgResp[0].url, type: "media" };
            }
        } catch (e) {}

        return null;
    }

    async function directFetch(endpoint, method = "GET", body = null) {
        const urls = [
            `http://127.0.0.1:8000${endpoint}`,
            `http://localhost:8000${endpoint}`
        ];
        let lastErr = null;
        for (const u of urls) {
            try {
                const opts = {
                    method: method,
                    headers: { "Content-Type": "application/json" }
                };
                if (body) opts.body = JSON.stringify(body);
                const res = await fetch(u, opts);
                if (res.ok) {
                    try { return await res.json(); } catch (e) { return {}; }
                }
            } catch (err) {
                lastErr = err;
            }
        }
        throw lastErr || new Error("Failed to connect to Gateway");
    }

    function callGateway(endpoint, method = "GET", body = null) {
        return new Promise((resolve, reject) => {
            try {
                chrome.runtime.sendMessage({
                    type: "GATEWAY_REQUEST",
                    endpoint: endpoint,
                    method: method,
                    body: body
                }, (response) => {
                    if (chrome.runtime.lastError || !response) {
                        directFetch(endpoint, method, body).then(resolve).catch(reject);
                        return;
                    }
                    if (response.ok) {
                        resolve(response.data || {});
                    } else {
                        reject(new Error(response.error || "Gateway error"));
                    }
                });
            } catch (e) {
                directFetch(endpoint, method, body).then(resolve).catch(reject);
            }
        });
    }

    async function triggerDownload(formatId = null, targetUrl = null, videoEl = null) {
        let finalUrl = targetUrl;
        let finalFormat = formatId;

        if (!finalUrl) {
            if (isPlatformSite()) {
                finalUrl = getCleanUrl();
            } else {
                showToast("🔍 Đang dò tìm nguồn video / luồng phim...", true);
                const resolved = await resolveMediaSource(videoEl);
                if (resolved && resolved.url) {
                    finalUrl = resolved.url;
                    if (resolved.type === "direct" || resolved.type === "ts") {
                        finalFormat = null;
                    } else if (resolved.type === "m3u8") {
                        finalFormat = "bestvideo+bestaudio/best";
                    }
                } else {
                    finalUrl = window.location.href;
                }
            }
        }

        showToast("⚡ Đang mở hộp thoại tải xuống Vortex...", true);
        const cookies = await requestCookies();

        let saveFolder = null;
        try {
            const stored = await chrome.storage.local.get("vortex_save_folder");
            if (stored.vortex_save_folder) {
                saveFolder = stored.vortex_save_folder;
            }
        } catch (e) {}

        const videoTitle = getMediaTitle();

        try {
            const payload = {
                url: finalUrl,
                format_id: finalFormat,
                cookies: cookies,
                title: videoTitle
            };
            if (saveFolder) {
                payload.save_path = saveFolder;
            }

            await callGateway("/api/v1/system/open_add_dialog", "POST", payload);
            showToast("✨ Đã mở hộp thoại tải xuống Vortex trên máy tính!", true);
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
            const data = await callGateway("/api/v1/extract", "POST", { url: videoUrl, cookies: cookies });
            if (data && Array.isArray(data.formats) && data.formats.length > 0) {
                qualityCache.set(clean, data);
                renderQualities(data, menuElement, statusElement);
            } else {
                if (statusElement) statusElement.textContent = "⚡ Sẵn sàng tải với các mức chuẩn";
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
                const data = await callGateway("/api/v1/system/browse_folder", "GET");
                if (data && data.status === "ok" && data.folder) {
                    await chrome.storage.local.set({ vortex_save_folder: data.folder });
                    showToast(`📁 Đã đổi thư mục lưu: ${data.folder}`, true);
                    const folderText = folderRow.querySelector(".vortex-folder-text");
                    if (folderText) {
                        folderText.textContent = data.folder.length > 25 ? "..." + data.folder.slice(-22) : data.folder;
                        folderRow.title = `Thư mục lưu hiện tại: ${data.folder}`;
                    }
                } else if (data && data.status !== "cancelled") {
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

    function createFloatingBar(videoElement = null) {
        const isPlatform = isPlatformSite();
        const container = document.createElement("div");
        container.className = "vortex-floating-container";
        if (isCurrentUrlMinimized()) {
            container.classList.add("minimized");
        }

        let menuItemsHtml = "";
        if (isPlatform) {
            menuItemsHtml = `
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
            `;
        } else {
            menuItemsHtml = `
                <div class="vortex-menu-item" data-action="auto">
                    <div class="vortex-item-left">
                        <span>🌟</span>
                        <span>Tải video này (Chất lượng gốc)</span>
                    </div>
                </div>
                <div class="vortex-menu-item" data-action="hls">
                    <div class="vortex-item-left">
                        <span>🎬</span>
                        <span>Tải luồng phim HLS / .TS (Ghép MP4 tự động)</span>
                    </div>
                </div>
                <div class="vortex-menu-divider"></div>
                <div class="vortex-menu-item" data-format="audio_only">
                    <div class="vortex-item-left">
                        <span>🎵</span>
                        <span>Chỉ tải MP3 (Âm thanh)</span>
                    </div>
                </div>
                <div class="vortex-menu-status">⚡ Đang kết nối luồng video / .ts...</div>
            `;
        }

        container.innerHTML = `
            <div class="vortex-btn-group">
                <div class="vortex-download-btn" title="Bấm để tải video này về máy tính">
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
                ${menuItemsHtml}
            </div>
        `;

        // Ngăn chặn sự kiện nổi bọt lên video player (tránh pause/play video ngoài ý muốn)
        container.addEventListener("click", (e) => e.stopPropagation());
        container.addEventListener("mousedown", (e) => e.stopPropagation());

        const mainBtn = container.querySelector(".vortex-download-btn");
        const arrowBtn = container.querySelector(".vortex-btn-arrow");
        const closeBtn = container.querySelector(".vortex-close-btn");
        const miniBadge = container.querySelector(".vortex-mini-badge");
        const dropdownMenu = container.querySelector(".vortex-dropdown-menu");
        const statusEl = container.querySelector(".vortex-menu-status");
        setupFolderRow(dropdownMenu);

        // Bấm vào nút tải:
        // - Với web phim/tin tức: bấm trực tiếp để kích hoạt tải ngay lập tức
        // - Với YouTube: mở menu chọn độ phân giải
        mainBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            if (!isPlatform) {
                triggerDownload(null, null, videoElement);
            } else {
                container.classList.toggle("open");
            }
        });

        if (arrowBtn) {
            arrowBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                container.classList.toggle("open");
            });
        }

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
                triggerDownload(fmt, null, videoElement);
            });
        });

        if (isPlatform) {
            // Tự động trích xuất các chất lượng cụ thể theo thời gian thực cho YouTube
            fetchVideoQualities(window.location.href, dropdownMenu, statusEl);
        } else {
            // Cập nhật trạng thái nhận diện media thời gian thực cho web xem phim & tin tức
            async function updateMediaStatus() {
                const res = await resolveMediaSource(videoElement);
                if (res && res.url) {
                    if (res.type === "m3u8") {
                        if (statusEl) statusEl.textContent = "✅ Đã bắt luồng phim gốc (.m3u8 / .ts)";
                    } else if (res.type === "ts") {
                        if (statusEl) statusEl.textContent = "✅ Đã bắt file video gốc (.ts)";
                    } else {
                        const cleanExt = (res.url.split("?")[0].split(".").pop() || "mp4").toLowerCase();
                        if (statusEl) statusEl.textContent = `✅ Đã bắt video gốc (.${cleanExt})`;
                    }
                } else {
                    if (statusEl) statusEl.textContent = "⚡ Nhấn Play video để bắt luồng tốt nhất";
                }
            }

            if (videoElement) {
                videoElement.addEventListener("play", updateMediaStatus);
                videoElement.addEventListener("loadedmetadata", updateMediaStatus);
                videoElement.addEventListener("timeupdate", () => {
                    if (statusEl && !statusEl.textContent.includes("✅")) updateMediaStatus();
                }, { once: true });
            }
            setTimeout(updateMediaStatus, 1200);
        }

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
                ytPlayer.appendChild(createFloatingBar(null));
            }
            return;
        }

        // Các trang web chứa thẻ <video> khác (Báo chí, Web xem phim)
        const videos = document.querySelectorAll("video");
        for (const vid of videos) {
            const parent = vid.parentElement;
            if (parent && !parent.querySelector(".vortex-floating-container")) {
                const rect = vid.getBoundingClientRect();
                if (rect.width > 200 && rect.height > 140) {
                    const style = window.getComputedStyle(parent);
                    if (style.position === "static") {
                        parent.style.position = "relative";
                    }
                    parent.appendChild(createFloatingBar(vid));
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
