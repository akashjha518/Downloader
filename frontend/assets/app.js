// ===============================
// Global State
// ===============================
let quality = "best";
const API_BASE = (window.REELS_API_BASE || "https://akashjha518-flask-api.hf.space").replace(/\/$/, "");

const messages = [
  "Analyzing link…",
  "Contacting servers…",
  "Preparing secure download…",
  "Almost ready 🚀"
];

let msgIndex = 0;
let messageInterval = null;

// ===============================
// Helpers
// ===============================
function qs(id) {
  return document.getElementById(id);
}

function show(el) {
  el.classList.remove("hidden");
}

function hide(el) {
  el.classList.add("hidden");
}

function reelsApiUrl(path) {
  return `${API_BASE}${path.startsWith("/") ? "" : "/"}${path}`;
}

// ===============================
// Quality Selection
// ===============================
function selectQuality(q, el) {
  quality = q;

  document.querySelectorAll(".quality").forEach(card => {
    card.classList.remove("ring", "ring-blue-500");
  });

  el.classList.add("ring", "ring-blue-500");
}

// ===============================
// Preparing State
// ===============================
function showPreparing() {
  const prep = qs("preparingState");
  const ready = qs("readyState");
  const error = qs("errorMsg");
  const msg = qs("prepMessage");

  show(prep);
  hide(ready);
  hide(error);

  msgIndex = 0;
  msg.textContent = messages[msgIndex];

  messageInterval = setInterval(() => {
    msgIndex = (msgIndex + 1) % messages.length;
    msg.textContent = messages[msgIndex];
  }, 1200);
}

function stopPreparing() {
  clearInterval(messageInterval);
  hide(qs("preparingState"));
}

// ===============================
// Prepare Download
// ===============================
async function prepareDownload() {
  const urlInput = qs("videoUrl");
  const error = qs("errorMsg");

  if (!urlInput || !urlInput.value.trim()) {
    error.textContent = "Please paste a valid video link.";
    show(error);
    return;
  }

  hide(error);
  showPreparing();

  try {
    const res = await fetch(
      reelsApiUrl(`/prepare?url=${encodeURIComponent(urlInput.value.trim())}`)
    );

    if (!res.ok) throw new Error("Prepare failed");

    const data = await res.json();
    stopPreparing();

    const ready = qs("readyState");
    const downloadBtn = qs("finalDownloadBtn");

    show(ready);

    downloadBtn.onclick = () => {
      window.location.href =
        reelsApiUrl(`/download/${data.token}?quality=${quality}`);
    };

  } catch (err) {
    stopPreparing();
    error.textContent =
      "Failed to prepare video. Make sure the link is public.";
    show(error);
  }
}

// ===============================
// Download Page Logic
// ===============================
function initDownloadPage() {
  const params = new URLSearchParams(window.location.search);
  const token = params.get("token");

  if (!token) return;

  const downloadBtn = document.getElementById("downloadBtn");
  if (!downloadBtn) return;

    downloadBtn.onclick = () => {
      window.location.href =
      reelsApiUrl(`/download/${token}?quality=${quality}`);
    };
}

// ===============================
// Init on load
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  initDownloadPage();
});

// ===============================
// Expose functions to HTML
// ===============================
if (typeof window.prepareDownload !== "function") {
  window.prepareDownload = prepareDownload;
}
window.selectQuality = selectQuality;
window.reelsApiUrl = reelsApiUrl;
