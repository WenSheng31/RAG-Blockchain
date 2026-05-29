/* Guided Search */

const state = { currentStep: 1, choices: { type: "", context: "", goal: "" } };

function getStepSection(step) {
  return document.querySelector(`.guided-question[data-step="${step}"]`);
}

function getStepIndicator(step) {
  return document.querySelector(`[data-step-indicator="${step}"]`);
}

function showStep(step) {
  document.querySelectorAll(".guided-question").forEach(el => el.classList.remove("active"));
  const section = getStepSection(step);
  if (section) section.classList.add("active");

  document.querySelectorAll("[data-step-indicator]").forEach(el => {
    el.classList.remove("bg-mark", "text-mark-fg", "border-transparent");
  });
  const ind = getStepIndicator(step);
  if (ind) ind.classList.add("bg-mark", "text-mark-fg", "border-transparent");

  document.getElementById("prev-step-btn").disabled = step <= 1;
  state.currentStep = step;
}

function loadStep2Options(typeChoice) {
  const section = getStepSection(2);
  const optionsEl = section.querySelector(".guided-options");
  optionsEl.innerHTML = '<span class="text-sm text-dim">載入中…</span>';

  fetch("/api/guided-step2-options/?type=" + encodeURIComponent(typeChoice))
    .then(r => r.json())
    .then(data => {
      optionsEl.innerHTML = data.options.map(opt =>
        `<button type="button"
                 class="guided-option border border-line rounded-lg p-4 text-sm text-left cursor-pointer hover:bg-lift hover:border-line-dark transition-colors"
                 data-field="context"
                 data-value="${opt}">${opt}</button>`
      ).join("");
      bindOptionClicks(section);
    })
    .catch(() => {
      optionsEl.innerHTML = '<span class="text-sm text-dim">載入失敗</span>';
    });
}

function fetchResults() {
  const { type, context, goal } = state.choices;
  const resultArea = document.getElementById("guided-result-area");
  const resultList = document.getElementById("guided-result-list");
  const resultSummary = document.getElementById("guided-result-summary");

  resultArea.classList.remove("hidden");
  resultList.innerHTML = '<div class="guided-loading">搜尋中…</div>';
  resultSummary.textContent = "";

  const params = new URLSearchParams({ type, context, goal });
  fetch("/api/guided-search/?" + params.toString())
    .then(r => r.json())
    .then(data => {
      resultSummary.textContent = data.message || "";

      if (!data.results || data.results.length === 0) {
        resultList.innerHTML = '<div class="guided-empty">找不到符合條件的關鍵詞。</div>';
        return;
      }

      resultList.innerHTML = data.results.map(kw => {
        const kwJson  = JSON.stringify(kw.keyword).replace(/"/g, "&quot;");
        const urlJson = JSON.stringify(kw.url).replace(/"/g, "&quot;");
        return `<div class="border border-line rounded-lg p-4 cursor-pointer hover:bg-lift transition-colors"
              onclick="handleResultClick(${kw.id}, ${kwJson}, ${urlJson})">
           <div class="guided-result-title">${kw.keyword}</div>
           <div class="guided-result-meta">${kw.group}${kw.category ? " / " + kw.category : ""}</div>
           <div class="guided-result-count">文章 ${kw.article_count} · Q&amp;A ${kw.question_count}</div>
         </div>`;
      }).join("");
    })
    .catch(() => {
      resultList.innerHTML = '<div class="guided-empty">搜尋失敗，請稍後再試。</div>';
    });
}

function handleResultClick(id, keyword, url) {
  logGuidedResultClick(id, keyword);
  window.location.href = url;
}

function logGuidedResultClick(id, keyword) {
  const { type, context, goal } = state.choices;
  const body = new URLSearchParams({
    keyword_id: id,
    keyword_name: keyword,
    type,
    context,
    goal,
  });
  fetch("/api/log-guided-result-click/", {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRFToken(),
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: body.toString(),
  }).catch(() => {});
}

function handleOptionClick(e) {
  const btn = e.currentTarget;
  const field = btn.dataset.field;
  const value = btn.dataset.value;

  const section = btn.closest(".guided-question");
  section.querySelectorAll(".guided-option").forEach(b => b.classList.remove("selected"));
  btn.classList.add("selected");

  state.choices[field] = value;

  if (field === "type") {
    loadStep2Options(value);
    setTimeout(() => showStep(2), 100);
  } else if (field === "context") {
    showStep(3);
  } else if (field === "goal") {
    fetchResults();
  }
}

function bindOptionClicks(container) {
  container.querySelectorAll(".guided-option").forEach(btn => {
    btn.removeEventListener("click", handleOptionClick);
    btn.addEventListener("click", handleOptionClick);
  });
}

function openGuidedModal() {
  document.getElementById("guided-modal").classList.remove("hidden");
  resetGuided();
}

function closeGuidedModal() {
  document.getElementById("guided-modal").classList.add("hidden");
}

function resetGuided() {
  state.choices = { type: "", context: "", goal: "" };
  document.querySelectorAll(".guided-option").forEach(b => b.classList.remove("selected"));
  document.getElementById("guided-result-area").classList.add("hidden");
  document.getElementById("guided-result-list").innerHTML = "";
  document.getElementById("guided-result-summary").textContent = "";
  showStep(1);
}

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".guided-question").forEach(section => bindOptionClicks(section));

  document.getElementById("prev-step-btn").addEventListener("click", function () {
    if (state.currentStep > 1) showStep(state.currentStep - 1);
  });

  document.getElementById("reset-guided-btn").addEventListener("click", resetGuided);
});
