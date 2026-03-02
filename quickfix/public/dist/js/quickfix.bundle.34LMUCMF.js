(() => {
  // ../quickfix/quickfix/public/js/navbar.js
  frappe.provide("frappe.views");
  setTimeout(() => {
    if (frappe.boot.quickfix_sname) {
      let shop_name = frappe.boot.quickfix_sname;
      $(".navbar-home").append(
        `<span style="margin-left:10px; font-weight:600;">
                ${shop_name}
            </span>`
      );
    }
  }, 100);
})();
//# sourceMappingURL=quickfix.bundle.34LMUCMF.js.map
