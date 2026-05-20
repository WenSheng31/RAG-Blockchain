/* AI Summary + Source Modal */

function fetchSummary(keyword, force) {
  const btn = document.getElementById("generate-summary-btn");
  const textEl = document.getElementById("ai-summary-text");
  const sourcesEl = document.getElementById("ai-summary-sources");

  btn.disabled = true;
  textEl.innerHTML = '<span class="inline-block w-4 h-4 border-2 border-t-transparent rounded-full animate-spin mr-2"></span>生成中…';
  sourcesEl.innerHTML = "";

  const url = "/api/keyword-summary/?keyword=" + encodeURIComponent(keyword) + (force ? "&force=1" : "");

  fetch(url)
    .then(r => r.json())
    .then(data => {
      if (data.error) {
        textEl.textContent = data.error;
        btn.disabled = false;
        return;
      }
      textEl.innerHTML = `<div class="prose prose-slate prose-sm max-w-none">${marked.parse(data.summary || "")}</div>`;

      if (data.sources && data.sources.length > 0) {
        const links = data.sources.map(s =>
          `<button type="button" onclick='openSourceModal(${s.id}, ${JSON.stringify(s.title)})'
                   class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md border border-line text-xs hover:bg-lift transition-colors">
             <i data-lucide="file-text" class="w-3 h-3"></i>${s.title}
           </button>`
        ).join(" ");
        sourcesEl.innerHTML = `<div class="mt-2 flex flex-wrap gap-1.5"><span class="text-xs text-dim self-center">來源：</span>${links}</div>`;
        if (window.lucide) lucide.createIcons();
      }

      btn.onclick = function() { fetchSummary(keyword, true); };
      btn.innerHTML = '<i data-lucide="wand-2" class="w-4 h-4"></i> 重新生成';
      if (window.lucide) lucide.createIcons();
      btn.disabled = false;
    })
    .catch(() => {
      textEl.textContent = "生成失敗，請稍後再試。";
      btn.disabled = false;
    });
}

function openSourceModal(id, title) {
  const modal = document.getElementById("source-modal");
  const titleEl = document.getElementById("sourceModalTitle");
  const bodyEl = document.getElementById("sourceModalBody");

  titleEl.textContent = title;
  bodyEl.innerHTML = '<span class="inline-block w-4 h-4 border-2 border-t-transparent rounded-full animate-spin"></span>';
  modal.classList.remove("hidden");

  fetch(`/api/page/${id}/`)
    .then(r => r.json())
    .then(data => {
      bodyEl.innerHTML = `<div class="prose prose-slate prose-sm max-w-none">${marked.parse(data.content || "")}</div>`;
    })
    .catch(() => {
      bodyEl.textContent = "（載入失敗）";
    });
}

function closeSourceModal() {
  document.getElementById("source-modal").classList.add("hidden");
}

document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") closeSourceModal();
});
