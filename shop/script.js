document.addEventListener('DOMContentLoaded', async function(){
  // fetch and render products
  const productsDiv = document.getElementById('products');
  const productSelect = document.getElementById('product');
  try {
    const menuRes = await fetch('/api/v1/menu/categories');
    // Attempt to fetch products too
    const productsRes = await fetch('/api/v1/menu/products');
    // Populate product select if available
    if (productsRes.ok) {
      const products = await productsRes.json();
      // Fallback: if API returns a different structure, just leave select placeholder
      if (Array.isArray(products)) {
        products.forEach(p => {
          if (p && p.code) {
            const opt = document.createElement('option');
            opt.value = p.code;
            opt.text = p.name || p.code;
            productSelect.add(opt);
          }
        });
      }
    }
  } catch (e) {
    // ignore errors in MVP
  }
  // show order area
  document.getElementById('order').style.display = 'block'

  // handle guest order
  document.getElementById('guestForm').addEventListener('submit', async function(ev){
    ev.preventDefault();
    const payload = {
      name: document.getElementById('name').value,
      phone: document.getElementById('phone').value,
      address: document.getElementById('address').value,
      items: [{ product_id: document.getElementById('product').value, quantity: parseInt(document.getElementById('qty').value || '1', 10) }],
      notes: ''
    };
    try {
      const res = await fetch('/api/v1/orders/guest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      document.getElementById('status').textContent = 'Order placed. ID: ' + (data.order_id || 'unknown');
    } catch (err) {
      document.getElementById('status').textContent = 'Failed to place order';
    }
  });
});
