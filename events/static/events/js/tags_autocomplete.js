// static/ivents/js/tags_autocomplete.js
document.addEventListener("DOMContentLoaded", function () {
  const tagsInput = document.getElementById("id_tags");
  if (!tagsInput) return;

  // Creem un datalist si no existeix
  let dataList = document.getElementById("tags-suggestions");
  if (!dataList) {
    dataList = document.createElement("datalist");
    dataList.id = "tags-suggestions";
    document.body.appendChild(dataList);
  }

  tagsInput.setAttribute("list", "tags-suggestions");

  let lastQuery = "";
  let timeoutId = null;

  const fetchSuggestions = function (query) {
    if (!query) {
      dataList.innerHTML = "";
      return;
    }

    fetch(`/events/api/tags-autocomplete/?q=${encodeURIComponent(query)}`)
      .then((resp) => resp.json())
      .then((data) => {
        dataList.innerHTML = "";
        (data.results || []).forEach((tag) => {
          const opt = document.createElement("option");
          opt.value = tag;
          dataList.appendChild(opt);
        });
      })
      .catch(() => {
        // silenciem errors
      });
  };

  tagsInput.addEventListener("input", function () {
    const value = tagsInput.value;
    const parts = value.split(",");
    const current = parts[parts.length - 1].trim();

    if (current === lastQuery) return;
    lastQuery = current;

    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    timeoutId = setTimeout(() => {
      fetchSuggestions(current);
    }, 250);
  });
});
