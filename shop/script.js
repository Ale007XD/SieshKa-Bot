document.addEventListener('DOMContentLoaded', function(){
  const form = document.getElementById('orderForm');
  const status = document.getElementById('status');
  form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const payload = {
      name: document.getElementById('name').value,
      phone: document.getElementById('phone').value,
      address: document.getElementById('address').value,
      items: [{ product_id: document.getElementById('item').value, quantity: parseInt(document.getElementById('quantity').value || '1') }],
      notes: document.getElementById('notes').value
    };
    try{
      const res = await fetch('/api/v1/orders/guest', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(payload)
      });
      if(res.ok){
        const data = await res.json();
        status.textContent = 'Order placed. ID: ' + data.order_id;
      } else {
        status.textContent = 'Failed to place order.';
      }
    }catch(err){
      status.textContent = 'Network error. Try again.';
    }
  });
});
