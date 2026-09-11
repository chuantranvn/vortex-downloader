(function () {
    "use strict";

    const GATEWAY_URL = "http://localhost:8000";
    const ICON_DATA_URI = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAA9hAAAPYQGoP6dpAAAJjklEQVRYhVWX628c53XGf+edy95ILu8USdkkI1lyZVt2FEeOG6Nxmzqtm6ppE6SA0Qb+lE+Bm38lQBAYvSABAqRF4X4o6rSJobRxaqGuXEVWJFsSrQtvMinel9zL7Fze9/TDzK6YXZydmZ1dnGee97znPI9w5LXw9AtTlbD0hjFyQcScAimJIIgBAckvUMl/L4AWnwBofnSqiCqqDnWqoLGqfqLK21ESf3/po8ubvZzSOzn93Evf9Iz5exGpiwgiBhEBk58jkl/nSI7+tXhpDqAIVVeEou7IuXLgNPv24rX33+oDOP3cS980Rv5JEM8YQcRDjCDGgHhgTAEoB5IDOMpCAcBpkcSBs6ja4juHs7Z/T1WtWvfa4o3335KFp1+YKvn+ooipiwjGeIgxRXjg+YjxijAFKNNnQciTUjwpzqHO5mFtASTDOYezDtTiVFHVg8Ta035ovDeAuhxhVowB4yN+gPgBXlBC/AD8HAimYKW37OrA5gnVWrAZLkvRLMFlKVjNq0UEp33O6j7yhg9yIa8fLSg2qBiM5+OFZR6bn2dq5hheqQARhEgYIkGI8T2cc8TdmDSKsVEX141xcUwcRextb9HY2cSqItah4vrlgoIIF3zQU/2CKtZWjIcJQk4+9RynT8wBYIIQMQbPBARemcCUEFW6rkPiG1w1xJWrPHy4weWPbiKqVCoVKrU6nSzDSr4cIL38qHLKV7SUozE5McYD8RiojzJY8nlw7y4EJczAEF7XMhiOU/V9GvEGSUUIZqbIKiOIQLPR4PJHS6SHHbR7wF4S4Xkhw2NTSJoCBrCPKEBLPqqCSG8nIwjhYJ1js49zuLOFBCW8yTn83QYztRMMSI2VaI3y82eYPXeSGCFtxkQ7TZa6QvD7ryD7+yTrq8j1KyT7GxgNGBmZZWtrCXWKquQFq4jfS9xL78RQGR4jbjexUYR/fAZjDbNyjGn/ONfimwz9xcsMzI3z4PI65vY2Y1XD4doO86stxq3j09Y6u8kOOrMAxqN12ODk5NNsbi71N25v6/qqIFrUpRgwBvUD4jghtYZw/iTh0h4nq0+wureMfOM8jA7y4M0rnMgqjL28wK9XVkhudzg9eYyKGWW3tMB+Z53/WX2P7eYe1CfY2m/mT65S7Jw8/KNoRAQ1Hloq0W1EJMEgMjJB5U7M/NAIvwzW6Pplqt97l/L2AffPT3K/PMK1Kx+yO6NcqUNl9RNO7ZYYC2f5wtiLfBg7Gska6vngTL9lO3WIKiZvmwoqOEA9D6lWiFJLPDCGNz1BdR+irEX3ieMc/uS/2PnoCh83rxK8cIr71+7TvnaF7qV3aTV2CV77A9a/cYZ3GxdZ398jzKoMB8cJyjXAoI4+A6qK0QKRFjWgJgeQZEoyOIxUStRMlc2kQfOwRef2x6w3bhC39lgvhzTvbeOaB6R7D/B/cYn9f7zIxO8uMP83r3M9u4wVg00ttUoNwfvt2QEYLZLnR0VF8KsVUhUyHOFAmbb4JB1orK5xuLPMQWMLW61wsN/hsbTMgFfDdps0qwnTSx2Wf/AeJ77wOCf/8q9Y69wgCOoMlWoYfDhSA6oOv9fH8/GZs1CplEB94o0HVALD5kyJzoZP5LYY/sxjVM00h+2EaHmLhfICu+E4z5/5MpHvsTEsfGV9hA9+vsiTf/Qct/55lJSYobCMwSDKkaFFrwZ6ozJnwQG+DpLeWSTePCD40nFW9hpUtmJWV1aYvHCB89/9DholfJp2+evXvs2rz3yV7bVVOuMlRod8qpfW2VEIf+cZ2vYAI4a+kDgyvk1/kvXmt3V0oi6kUO0G3PnJz1g4M82Nz1eY2K9AAtd+8Les3Nlm5NwJgj85ztWry7z50+9zKCml2RmCqYyZPeWgFWErg6RpTKfT/a1xre4IgH44h9qM6LBNs7nOeHia+NJlPvjhf3L86+dY+dw0w9kEbDbYeudt/H9ZpPzWJ/z32n9wmLbxp+bxpyeRRNC0y8HaLsYmZEmLdrODOvtIsBRvv5dYJJ/lZBlZs00r2mQ96nB+5mvc/ddLLDc7jL16js2qwC9idq/fYNPUORyqs/9wh6nhs7T++A+pqaXuamweNOhGEfHGA4I0ohW1cC5FNRcmuBxAfwnQQkRkCbbdxhnhwK7zfxs/5+zEec7dKFF/8z3GmpbRL3+VoS/9ObtNwbub8ezQ7+G/9gpP/NkLRBc/xI/r7NU6dDZ2kI01XBaTJB2cpjhcrpSKGvDVKRhQp4i1aJZC1MF2mujICM2qzzur/86J+jN89thTPFOeoxz4xHNn2Qza/HprmeVXJpj/2rMs/vgiJ7ZCPnb32E13YL1KurtCRQSbdXMGyBlwRUfyc/1mECmkVJZiozZkKfbBHXTOxz5/jkWX8OnBbd65e5/q4DhmeAD72XGGXnqR4UrI7b/7Kdm/vcv4Y3/K/y79kmQoRm9cQeJDTGk4Z8AVDODodWA5vvCU5kLTIJ6H8wL84UmSWGk9WMRlBg1r+E99ntoXv0gwOkFlfIzqWB0Cj71by8Q/u0jwyRonas9jzS53Dq+jj8+itz5E0hYTo6dx2qFr97GS4NTmwlUVmZ0/43K9natgNR6pCrMvv8ry5ffprt0HFcQLoDKMNzUH1Xo+zxs7mMM96maKejBNN92gmW7g6kPQbmA6h0xWP8Po6BRLW1eREJxk+TbEoYrK9NyTkSBlMSY3GUawDrRcZvzZF9m9/huiVjNvIp6P+GVMUMYPBij5A5T8QWzaRrptXBZhXYyHR2hTRgYmqVfHuHnvV0jJIQH0Wp2qA+jKsbknfyNw9pHjMagqcZoQpRnl4QkG6qOYUhkJyphyBVMdJByuU6pWECdoM8bstvDaXcLMMeD7DNV8NtbWuLV8FS8UgnIAxoAUjQhFleu+On1b0bNGcrGA5G3ZEyE0kDa22Wvu5zLdGISeSfEQNQiCWBDrEKeIs4g61GU4TZDAIYFfPJzrN6HcsfG2TE4uTEkYLCLUTY8FFZzmRsKqy4dUz4gUBkIw+XWh6cT1TULe0HCIKOL1zI7QMxI5AA5Is9Neu91oVwdH7onydUWNqObmhHxzGBE8z2CM4BmDJ4InghHwRDG9ML3ImTaeIMX/MI8GUI5RrQqvbz+8/4EH0Gnu3awOjd4S+ApQLh657wVNP3KHbEwOTHo+QnohCMVRpO+08jHfl78HTnh9+9O7bwGPJEqnuXezVqn/SEViETMMWgf18v1ZJOqtRN+SapHoyLG43TfQioLGIDdx+g+auW9tP7z/QS/v/wNlKW8DyYApagAAAABJRU5ErkJggg==";

    // Quản lý video đã bị người dùng ấn tắt X
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
        if (dismissedUrls.has(clean)) return true;
        try {
            return sessionStorage.getItem("vortex_dismissed_" + clean) === "1";
        } catch (e) {
            return false;
        }
    }

    function dismissCurrentUrl() {
        const clean = getCleanUrl();
        dismissedUrls.add(clean);
        try {
            sessionStorage.setItem("vortex_dismissed_" + clean, "1");
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

    async function triggerDownload(formatId = null) {
        const videoUrl = window.location.href;
        showToast("Đang kết nối Vortex Downloader...", true);

        try {
            const res = await fetch(`${GATEWAY_URL}/api/v1/download`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    url: videoUrl,
                    format_id: formatId
                })
            });

            if (res.ok) {
                const data = await res.json();
                const displayTitle = data.file_name && data.file_name !== "Đang lấy tiêu đề video..."
                    ? data.file_name.substring(0, 32)
                    : "Video";
                showToast(`Đã bắt đầu tải: ${displayTitle}...`, true);
            } else {
                showToast("Lỗi: Không thể gửi lệnh tải đến Gateway!", false);
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

        try {
            if (statusElement) statusElement.textContent = "⏳ Đang dò tất cả chất lượng...";
            const res = await fetch(`${GATEWAY_URL}/api/v1/extract`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: videoUrl })
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
        container.innerHTML = `
            <div class="vortex-btn-group">
                <div class="vortex-download-btn">
                    <img src="${ICON_DATA_URI}" class="vortex-btn-icon" alt="Vortex" />
                    <span>Tải video này</span>
                    <span class="vortex-btn-arrow">▼</span>
                </div>
                <div class="vortex-close-btn" title="Đóng thanh tải">✕</div>
            </div>
            <div class="vortex-dropdown-menu">
                <div class="vortex-menu-item" data-format="bestvideo+bestaudio/best">
                    <div class="vortex-item-left">
                        <span>🌟</span>
                        <span>Chất lượng tốt nhất</span>
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
        const dropdownMenu = container.querySelector(".vortex-dropdown-menu");
        const statusEl = container.querySelector(".vortex-menu-status");

        // Bấm vào nút tải -> Bật/Tắt menu chọn chất lượng
        mainBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            container.classList.toggle("open");
        });

        // Bấm nút X -> Đóng thanh tải và ghi nhớ cho video hiện tại
        closeBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            dismissCurrentUrl();
            container.style.transition = "all 0.2s ease";
            container.style.opacity = "0";
            container.style.transform = "scale(0.85)";
            setTimeout(() => {
                if (container.parentElement) container.remove();
            }, 200);
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

})();
