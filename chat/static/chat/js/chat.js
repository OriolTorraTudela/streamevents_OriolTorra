function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function getChatConfig() {
  const container = document.querySelector(".chat-container");
  if (!container) return null;

  const eventId = container.dataset.eventId ? Number(container.dataset.eventId) : null;
  const loadUrl = container.dataset.loadUrl || null;
  const sendUrl = container.dataset.sendUrl || null;
  const deleteUrlTemplate = container.dataset.deleteUrlTemplate || null;

  return { container, eventId, loadUrl, sendUrl, deleteUrlTemplate };
}

function updateMessageCount(count) {
  const el = document.getElementById("message-count");
  if (el) el.textContent = String(count);
}

function scrollToBottom() {
  const box = document.getElementById("chat-messages");
  if (box) box.scrollTop = box.scrollHeight;
}

function createMessageElement(message) {
  const div = document.createElement("div");
  div.className = "chat-message";
  div.dataset.messageId = message.id;

  if (message.is_highlighted) {
    div.classList.add("highlighted");
  }

  const header = `
    <div class="message-header">
      <strong>${escapeHtml(message.display_name || message.user)}</strong>
      <small class="text-muted">${escapeHtml(message.created_at)}</small>
    </div>
  `;

  const content = `
    <div class="message-content">
      ${escapeHtml(message.message)}
    </div>
  `;

  let actions = "";
  if (message.can_delete) {
    actions = `
      <div class="message-actions">
        <button type="button" class="btn btn-sm btn-outline-danger delete-message">
          Eliminar
        </button>
      </div>
    `;
  }

  div.innerHTML = header + content + actions;
  return div;
}

function getCsrfToken() {
  const input = document.querySelector('#chat-form input[name="csrfmiddlewaretoken"]');
  return input ? input.value : "";
}

function showErrors(errors) {
  const el = document.getElementById("chat-errors");
  if (!el) return;

  if (!errors) {
    el.innerHTML = "";
    return;
  }

  let html = '<div class="alert alert-danger py-2 mb-0">';
  for (const key in errors) {
    const arr = errors[key];
    if (Array.isArray(arr)) {
      for (const msg of arr) {
        html += `<div class="small">${escapeHtml(msg)}</div>`;
      }
    } else {
      html += `<div class="small">${escapeHtml(String(arr))}</div>`;
    }
  }
  html += "</div>";
  el.innerHTML = html;
}

async function loadMessages() {
  const cfg = getChatConfig();
  const box = document.getElementById("chat-messages");
  if (!cfg || !box || !cfg.loadUrl) return;

  try {
    const res = await fetch(cfg.loadUrl);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    box.innerHTML = "";
    const msgs = data.messages || [];

    for (const m of msgs) {
      box.appendChild(createMessageElement(m));
    }

    updateMessageCount(msgs.length);
    scrollToBottom();
  } catch (e) {
    box.innerHTML = `<div class="text-danger small">Error carregant missatges.</div>`;
  }
}

async function sendMessage(ev) {
  ev.preventDefault();

  const cfg = getChatConfig();
  if (!cfg || !cfg.sendUrl) return;

  const form = document.getElementById("chat-form");
  if (!form) return;

  const textarea = form.querySelector("textarea");
  const message = textarea ? textarea.value : "";
  const csrf = getCsrfToken();

  showErrors(null);

  try {
    const res = await fetch(cfg.sendUrl, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrf,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({ message }),
    });

    const data = await res.json();

    if (res.ok && data.success) {
      if (textarea) textarea.value = "";
      await loadMessages();
    } else {
      showErrors(data.errors || { "__all__": ["No s'ha pogut enviar el missatge."] });
    }
  } catch (e) {
    showErrors({ "__all__": ["Error enviant el missatge."] });
  }
}

function buildDeleteUrl(messageId) {
  const cfg = getChatConfig();
  if (!cfg || !cfg.deleteUrlTemplate) return null;
  // template ve com .../message/0/delete/ -> substituïm el 0 pel messageId
  return cfg.deleteUrlTemplate.replace("/0/", `/${messageId}/`);
}

async function deleteMessage(messageId) {
  const deleteUrl = buildDeleteUrl(messageId);
  if (!deleteUrl) return;

  const csrf = getCsrfToken();

  try {
    const res = await fetch(deleteUrl, {
      method: "POST",
      headers: { "X-CSRFToken": csrf },
    });

    const data = await res.json();

    if (res.ok && data.success) {
      await loadMessages();
    } else {
      alert(data.error || "No s'ha pogut eliminar el missatge.");
    }
  } catch (e) {
    alert("Error eliminant el missatge.");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("chat-form");
  if (form) {
    form.addEventListener("submit", sendMessage);
  }

  const box = document.getElementById("chat-messages");
  if (box) {
    box.addEventListener("click", (e) => {
      const btn = e.target.closest(".delete-message");
      if (!btn) return;

      const msgEl = btn.closest(".chat-message");
      if (!msgEl) return;

      const messageId = msgEl.dataset.messageId;
      if (!messageId) return;

      if (confirm("Vols eliminar aquest missatge?")) {
        deleteMessage(messageId);
      }
    });
  }

  loadMessages();
  setInterval(loadMessages, 3000);
});
