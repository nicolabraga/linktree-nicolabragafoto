(function () {
  "use strict";

  var PIX_KEY = "d38eda0f-0370-4bce-8823-95020e4b2d8e";
  var ALBUMS_URL = "data/albums.json";
  var FEATURED_COUNT = 5; // últimos 5 álbuns ganham destaque + selo "NOVO"
  var AUTO_RELOAD_MS = 3 * 60 * 1000; // recarrega a página a cada 3 minutos

  // ---------- Copiar chave Pix ----------
  function copyPix(btn) {
    var restore = btn.innerHTML;
    var done = function (ok) {
      btn.classList.toggle("copied", ok);
      btn.innerHTML = ok ? "✅ Copiado!" : "⚠️ Copie manualmente";
      showToast(ok ? "✅ Chave Pix copiada!" : "Não foi possível copiar automaticamente.");
      setTimeout(function () {
        btn.classList.remove("copied");
        btn.innerHTML = restore;
      }, 2000);
    };

    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(PIX_KEY).then(function () {
        done(true);
      }).catch(function () {
        fallbackCopy();
      });
    } else {
      fallbackCopy();
    }

    function fallbackCopy() {
      try {
        var tmp = document.createElement("textarea");
        tmp.value = PIX_KEY;
        tmp.style.position = "fixed";
        tmp.style.opacity = "0";
        document.body.appendChild(tmp);
        tmp.focus();
        tmp.select();
        var ok = document.execCommand("copy");
        document.body.removeChild(tmp);
        done(ok);
      } catch (e) {
        done(false);
      }
    }
  }

  function showToast(msg) {
    var toast = document.getElementById("toast");
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("show");
    clearTimeout(showToast._t);
    showToast._t = setTimeout(function () {
      toast.classList.remove("show");
    }, 2200);
  }

  ["pixCopyBtn", "pixCopyBtn2"].forEach(function (id) {
    var btn = document.getElementById(id);
    if (btn) btn.addEventListener("click", function () { copyPix(btn); });
  });

  // ---------- Álbuns recentes ----------
  function renderAlbums(data) {
    var list = document.getElementById("albumsList");
    var updatedEl = document.getElementById("updatedAt");
    var albums = (data && data.albums) || [];

    if (updatedEl) {
      updatedEl.textContent = data && data.updatedAt
        ? "Atualizado em " + formatDate(data.updatedAt)
        : "";
    }

    if (!albums.length) {
      list.innerHTML = '<div class="albums-empty">Nenhum álbum encontrado no momento.</div>';
      return;
    }

    var top15 = albums.slice(0, 15);
    var html = top15.map(function (album, i) {
      var isFeatured = i < FEATURED_COUNT;
      return (
        '<a class="album-card' + (isFeatured ? " featured" : "") + '" href="' +
        escapeAttr(album.url) + '" target="_blank" rel="noopener">' +
          '<span class="album-emoji">' + (album.emoji || "📷") + '</span>' +
          '<span class="album-info">' +
            '<span class="album-title">' + escapeHtml(album.title) + '</span>' +
            '<span class="album-date">' + escapeHtml(album.date) + '</span>' +
          '</span>' +
          (isFeatured ? '<span class="album-badge">NOVO</span>' : '') +
          '<span class="album-chevron">›</span>' +
        '</a>'
      );
    }).join("");

    list.innerHTML = html;
  }

  function formatDate(iso) {
    try {
      var d = new Date(iso);
      return d.toLocaleString("pt-BR", {
        day: "2-digit", month: "2-digit", year: "numeric",
        hour: "2-digit", minute: "2-digit"
      });
    } catch (e) {
      return iso;
    }
  }

  function escapeHtml(str) {
    return String(str || "").replace(/[&<>"']/g, function (c) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c];
    });
  }

  function escapeAttr(str) {
    return escapeHtml(str);
  }

  function loadAlbums() {
    var btn = document.getElementById("refreshBtn");
    if (btn) btn.classList.add("loading");

    fetch(ALBUMS_URL, { cache: "no-store" })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (data) {
        renderAlbums(data);
      })
      .catch(function () {
        var list = document.getElementById("albumsList");
        list.innerHTML = '<div class="albums-empty">Não foi possível carregar os álbuns agora. Tente novamente em instantes.</div>';
      })
      .finally(function () {
        if (btn) btn.classList.remove("loading");
      });
  }

  var refreshBtn = document.getElementById("refreshBtn");
  if (refreshBtn) refreshBtn.addEventListener("click", loadAlbums);

  loadAlbums();

  // ---------- Auto atualização da página a cada 3 minutos ----------
  // Mantém o visitante sempre vendo a versão mais recente publicada,
  // sem precisar recarregar manualmente. Só recarrega se a aba estiver
  // visível, para não interromper o usuário em outra aba.
  setInterval(function () {
    if (document.visibilityState === "visible") {
      window.location.reload();
    }
  }, AUTO_RELOAD_MS);
})();
