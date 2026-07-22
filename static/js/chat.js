/* Online Judge — lightweight polling chat (no WebSockets needed). */
(function () {
  var box = document.querySelector(".chat-box");
  if (!box) return;
  var room = box.dataset.room;
  var listEl = document.getElementById("chat-messages");
  var form = document.getElementById("chat-form");
  var input = document.getElementById("chat-input");
  var errEl = document.getElementById("chat-error");
  var lastId = 0;
  var firstLoad = true;

  function getCookie(name) {
    var m = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
    return m ? decodeURIComponent(m.pop()) : "";
  }
  var csrftoken = getCookie("csrftoken");

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  var AVATAR_COLORS = ["#2563eb", "#16a34a", "#ea580c", "#7c3aed",
                       "#0d9488", "#db2777", "#d97706", "#4f46e5"];
  function avatarColor(name) {
    var h = 0;
    for (var i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) >>> 0;
    return AVATAR_COLORS[h % AVATAR_COLORS.length];
  }

  function nearBottom() {
    return listEl.scrollHeight - listEl.scrollTop - listEl.clientHeight < 80;
  }

  function render(messages) {
    if (!messages.length) return;
    var stick = nearBottom() || firstLoad;
    messages.forEach(function (m) {
      if (m.id <= lastId) return;
      lastId = Math.max(lastId, m.id);
      var div = document.createElement("div");
      div.className = "chat-msg" + (m.mine ? " mine" : "");
      div.innerHTML =
        '<div class="chat-avatar" style="background:' + avatarColor(m.user) + ';">' +
        esc(m.user.charAt(0).toUpperCase()) + "</div>" +
        '<div><div class="meta">' + esc(m.user) + " · " + esc(m.time) + "</div>" +
        '<div class="bubble">' + esc(m.content) + "</div></div>";
      listEl.appendChild(div);
    });
    if (stick) listEl.scrollTop = listEl.scrollHeight;
    firstLoad = false;
  }

  function poll() {
    fetch("/chat/api/" + room + "/messages/?after=" + lastId, {
      credentials: "same-origin",
    })
      .then(function (r) { return r.ok ? r.json() : { messages: [] }; })
      .then(function (data) { render(data.messages || []); })
      .catch(function () {})
      .finally(function () { setTimeout(poll, 2500); });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var content = input.value.trim();
    if (!content) return;
    errEl.textContent = "";
    var body = new URLSearchParams();
    body.append("content", content);
    fetch("/chat/api/" + room + "/send/", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "X-CSRFToken": csrftoken,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: body.toString(),
    })
      .then(function (r) {
        if (r.status === 429) {
          return r.json().then(function (d) {
            errEl.textContent = d.error || "Too fast — try again in a moment.";
          });
        }
        if (r.ok) {
          input.value = "";
          return fetch("/chat/api/" + room + "/messages/?after=" + lastId, {
            credentials: "same-origin",
          })
            .then(function (rr) { return rr.json(); })
            .then(function (data) { render(data.messages || []); });
        }
        errEl.textContent = "Could not send the message.";
      })
      .catch(function () { errEl.textContent = "Network error — try again."; });
  });

  poll();
})();
