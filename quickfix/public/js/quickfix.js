


frappe.ready(function () {
    if (frappe.boot.quickfix_shop_name) {
        
        let shopLabel = document.createElement("span");
        shopLabel.innerHTML = `<strong>${frappe.boot.quickfix_shop_name}</strong>`;
        shopLabel.style.marginLeft = "15px";

        
        document.querySelector(".navbar .container").appendChild(shopLabel);
    }
});