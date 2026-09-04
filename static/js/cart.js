/**
 * Giỏ hàng phía trình duyệt.
 * - Khách vãng lai: lưu tạm vào LocalStorage.
 * - Khi đăng nhập: tự động đồng bộ LocalStorage lên session của server.
 */
(function () {
  const STORAGE_KEY = "linhkienpc_cart";

  function getCsrfToken() {
    // Thẻ <meta name="csrf-token"> trong base.html luôn có trên mọi trang,
    // kể cả với khách chưa đăng nhập. Hai nguồn còn lại là phương án dự phòng.
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta && meta.content) return meta.content;
    const input = document.querySelector("[name=csrfmiddlewaretoken]");
    if (input) return input.value;
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : "";
  }

  function readLocalCart() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    } catch (e) {
      return {};
    }
  }

  function writeLocalCart(items) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    } catch (e) {
      /* trình duyệt chặn LocalStorage: bỏ qua, server vẫn giữ giỏ hàng trong session */
    }
  }

  window.LocalCart = {
    add(productId, quantity) {
      const items = readLocalCart();
      items[productId] = (items[productId] || 0) + (quantity || 1);
      writeLocalCart(items);
    },
    set(productId, quantity) {
      const items = readLocalCart();
      if (quantity > 0) items[productId] = quantity;
      else delete items[productId];
      writeLocalCart(items);
    },
    remove(productId) {
      const items = readLocalCart();
      delete items[productId];
      writeLocalCart(items);
    },
    clear() {
      writeLocalCart({});
    },
    all: readLocalCart,
  };

  function showToast(message, ok) {
    const toast = document.getElementById("toast");
    if (!toast || !message) return;
    toast.textContent = message;
    toast.className =
      "fixed bottom-6 right-6 z-50 px-5 py-3 rounded-xl text-white text-sm shadow-2xl " +
      (ok === false ? "bg-rose-600" : "bg-slate-900");
    toast.classList.remove("hidden");
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.add("hidden"), 3000);
  }

  function updateBadge(count) {
    const badge = document.getElementById("cart-badge");
    if (!badge) return;
    badge.textContent = count;
    badge.classList.toggle("hidden", !count);
  }

  // Nhận sự kiện do HTMX bắn ra sau khi thao tác giỏ hàng
  document.body.addEventListener("cartUpdated", function (event) {
    const detail = event.detail || {};
    updateBadge(detail.count || 0);
    showToast(detail.message, detail.ok);
  });

  // Đồng bộ LocalStorage lên server khi vừa đăng nhập
  function syncLocalCart() {
    const items = readLocalCart();
    if (!Object.keys(items).length) return;
    fetch("/gio-hang/dong-bo/", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrfToken() },
      body: JSON.stringify({ items: items }),
    })
      .then((r) => r.json())
      .then((data) => {
        updateBadge(data.count);
        window.LocalCart.clear();
      })
      .catch(() => {});
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (document.body.dataset.authenticated === "true") {
      syncLocalCart();
    }
    // Nút "Thêm vào giỏ" không dùng HTMX (fallback bằng fetch)
    document.querySelectorAll("[data-add-to-cart]").forEach(function (button) {
      button.addEventListener("click", function () {
        const productId = button.dataset.addToCart;
        const quantityInput = document.getElementById(button.dataset.quantityInput || "");
        const quantity = quantityInput ? parseInt(quantityInput.value, 10) || 1 : 1;
        if (document.body.dataset.authenticated !== "true") {
          window.LocalCart.add(productId, quantity);
        }
        const form = new FormData();
        form.append("quantity", quantity);
        form.append("csrfmiddlewaretoken", getCsrfToken());
        fetch("/gio-hang/them/" + productId + "/", {
          method: "POST",
          headers: { "X-Requested-With": "XMLHttpRequest" },
          body: form,
        })
          .then((r) => r.json())
          .then((data) => {
            updateBadge(data.count);
            showToast(data.message, data.ok);
          })
          .catch(() => showToast("Không thêm được sản phẩm, vui lòng thử lại.", false));
      });
    });
  });
})();
