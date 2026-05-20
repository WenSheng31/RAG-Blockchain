/* =========================
   CSRF Token
========================= */
function getCSRFToken() {
    const name = "csrftoken=";
    const cookies = document.cookie.split(";");

    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name)) {
            return cookie.substring(name.length);
        }
    }
    return "";
}

/* =========================
   Task Panel Toggle
========================= */
function toggleTaskPanel() {
    const panel = document.getElementById("task-float-panel");
    const iconWrap = document.getElementById("task-toggle-icon");

    if (!panel) return;

    panel.classList.toggle("collapsed");
    const collapsed = panel.classList.contains("collapsed");

    if (iconWrap) {
        iconWrap.innerHTML = `<i data-lucide="${collapsed ? "chevron-up" : "chevron-down"}" class="w-3 h-3"></i>`;
        if (window.lucide) lucide.createIcons();
    }
}

/* =========================
   Drag & Snap
========================= */
const panel = document.getElementById("task-float-panel");
let isDragging = false;
let dragStartX, dragStartY, panelStartLeft, panelStartTop;
let rafId = null;
let latestMouseX, latestMouseY;

function startDrag(e) {
    if (!panel) return;
    e.preventDefault();

    const rect = panel.getBoundingClientRect();
    isDragging = true;
    dragStartX = e.clientX;
    dragStartY = e.clientY;
    panelStartLeft = rect.left;
    panelStartTop = rect.top;

    // 固定到 left/top，停用 transition 避免卡頓
    panel.style.right = "auto";
    panel.style.left = panelStartLeft + "px";
    panel.style.top = panelStartTop + "px";
    panel.style.transition = "none";
    panel.style.willChange = "left, top";

    document.addEventListener("mousemove", onDrag);
    document.addEventListener("mouseup", stopDrag);
}

function onDrag(e) {
    if (!isDragging) return;
    latestMouseX = e.clientX;
    latestMouseY = e.clientY;
    if (!rafId) rafId = requestAnimationFrame(applyDrag);
}

function applyDrag() {
    rafId = null;
    if (!isDragging || !panel) return;

    const x = panelStartLeft + (latestMouseX - dragStartX);
    const y = panelStartTop + (latestMouseY - dragStartY);
    const maxX = window.innerWidth - panel.offsetWidth;
    const maxY = window.innerHeight - panel.offsetHeight;

    panel.style.left = Math.max(0, Math.min(x, maxX)) + "px";
    panel.style.top = Math.max(0, Math.min(y, maxY)) + "px";
}

function stopDrag() {
    if (!isDragging) return;
    isDragging = false;

    if (rafId) { cancelAnimationFrame(rafId); rafId = null; }

    panel.style.willChange = "";
    panel.style.transition = "";

    document.removeEventListener("mousemove", onDrag);
    document.removeEventListener("mouseup", stopDrag);
    snapToEdge();
}

/* 自動吸附最近邊緣 */
function snapToEdge() {
    if (!panel) return;

    const rect = panel.getBoundingClientRect();
    const snapLeft = rect.left + rect.width / 2 < window.innerWidth / 2;

    if (snapLeft) {
        panel.style.left = "16px";
        panel.style.right = "auto";
    } else {
        panel.style.right = "16px";
        panel.style.left = "auto";
    }
}

/* =========================
   Abort Task
========================= */
function confirmAbortTask() {
    const confirmed = confirm("確定要中斷測驗嗎？目前進度將不會被儲存。");
    if (!confirmed) return;

    fetch("/task/abort/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/json",
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Abort task failed");
        }
        return response.json();   // 若後端沒回 JSON，也可改成 return response.text();
    })
    .then(() => {
        showAbortModal();
    })
    .catch(error => {
        console.error("中斷測驗發生錯誤：", error);
        alert("中斷測驗失敗，請稍後再試。");
    });
}

/* =========================
   Abort Modal
========================= */
function showAbortModal() {
    const modal = document.getElementById("abort-modal");
    if (!modal) return;

    modal.classList.remove("hidden");
    document.addEventListener("keydown", handleAbortEsc);
}

function closeAbortModal() {
    const modal = document.getElementById("abort-modal");
    if (!modal) return;

    modal.classList.add("hidden");
    document.removeEventListener("keydown", handleAbortEsc);
}

function handleAbortEsc(e) {
    if (e.key === "Escape") {
        closeAbortModal();
    }
}

/* =========================
   Navigation
========================= */
function goHome() {
    window.location.href = "/";
}

/* =========================
   Sidebar Toggle
========================= */
(function () {
    const sidebar = document.getElementById("sidebar");
    const mainWrapper = document.getElementById("main-wrapper");
    const backdrop = document.getElementById("sidebar-backdrop");
    if (!sidebar) return;

    const SIDEBAR_W = "224px"; // w-56
    const DESKTOP_BP = 768;

    function isMobile() { return window.innerWidth < DESKTOP_BP; }

    function applyState(open) {
        if (open) {
            sidebar.classList.remove("hidden");
            if (isMobile()) {
                if (mainWrapper) mainWrapper.style.marginLeft = "0";
                if (backdrop) backdrop.classList.remove("hidden");
            } else {
                if (mainWrapper) mainWrapper.style.marginLeft = SIDEBAR_W;
                if (backdrop) backdrop.classList.add("hidden");
            }
        } else {
            sidebar.classList.add("hidden");
            if (mainWrapper) mainWrapper.style.marginLeft = "0";
            if (backdrop) backdrop.classList.add("hidden");
        }
    }

    window.toggleSidebar = function () {
        const open = sidebar.classList.contains("hidden");
        applyState(open);
        if (!isMobile()) localStorage.setItem("sidebarOpen", open ? "1" : "0");
    };

    // 初始化：手機預設收合，桌面依 localStorage
    const saved = localStorage.getItem("sidebarOpen");
    applyState(isMobile() ? false : saved !== "0");

    // 視窗大小改變時重新評估
    window.addEventListener("resize", function () {
        if (!sidebar.classList.contains("hidden")) {
            applyState(true);
        }
    });
})();
