document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("keyword-search");
    const resultsBox = document.getElementById("search-results");

    if (!input || !resultsBox) return;

    let debounceTimer = null;
    let currentQuery = "";
    let lastLoggedQuery = "";

    const DEBOUNCE_DELAY = 300;

    function getCSRFToken() {
        const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfInput ? csrfInput.value : "";
    }

    function logKeywordSearch(query) {
        if (!query || query.length < 2) return;
        if (query === lastLoggedQuery) return;
        lastLoggedQuery = query;
        fetch("/api/log-keyword-search/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCSRFToken(),
            },
            body: new URLSearchParams({ query }),
        }).catch(error => console.error("搜尋紀錄失敗：", error));
    }

    function logKeywordSearchClick(keywordId, keywordName, query, targetUrl) {
        fetch("/api/log-keyword-search-click/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCSRFToken(),
            },
            body: new URLSearchParams({ keyword_id: keywordId, keyword_name: keywordName, query }),
        }).finally(() => { window.location.href = targetUrl; });
    }

    input.addEventListener("input", function () {
        const query = input.value.trim();
        currentQuery = query;
        clearTimeout(debounceTimer);

        if (query.length === 0) {
            resultsBox.innerHTML = "";
            return;
        }

        resultsBox.innerHTML = `<div class="p-3">搜尋中...</div>`;

        debounceTimer = setTimeout(() => {
            logKeywordSearch(query);

            fetch(`/api/keyword-autocomplete/?q=${encodeURIComponent(query)}`)
                .then(response => {
                    if (!response.ok) throw new Error("伺服器回應失敗");
                    return response.json();
                })
                .then(data => {
                    if (query !== currentQuery) return;
                    resultsBox.innerHTML = "";

                    if (!data.results || data.results.length === 0) {
                        resultsBox.innerHTML = `<div class="p-3">找不到相關關鍵字</div>`;
                        return;
                    }

                    data.results.forEach(item => {
                        const a = document.createElement("a");
                        const targetUrl = `/keywords/${item.id}/`;
                        a.href = targetUrl;
                        a.className = "block px-3 py-2.5 text-sm hover:bg-lift transition-colors cursor-pointer";
                        a.innerHTML = `
                            <div>${item.text}</div>
                            <div class="text-sm">
                                ${item.group || ""}${item.category ? " / " + item.category : ""}
                            </div>
                        `;
                        a.addEventListener("click", function (event) {
                            event.preventDefault();
                            logKeywordSearchClick(item.id, item.text, query, targetUrl);
                        });
                        resultsBox.appendChild(a);
                    });
                })
                .catch(error => {
                    console.error("搜尋錯誤：", error);
                    if (query !== currentQuery) return;
                    resultsBox.innerHTML = `<div class="p-3">發生錯誤，請稍後再試</div>`;
                });
        }, DEBOUNCE_DELAY);
    });
});
