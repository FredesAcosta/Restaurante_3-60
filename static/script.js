

document.addEventListener('DOMContentLoaded', () => {
  const lista = document.getElementById('lista-carrito');
  const totalEl = document.getElementById('total-carrito');

  lista.addEventListener('click', e => {
    if (e.target.classList.contains('remove-item')) {
      const li = e.target.closest('li');
      li.remove();
      recalcTotal();
    }
  });

  function recalcTotal() {
    let total = 0;
    document.querySelectorAll('#lista-carrito li').forEach(li => {
      const price = parseFloat(li.querySelector('.precio').textContent.replace('$',''));
      total += price;
    });
    totalEl.textContent = total.toFixed(2);
  }

  recalcTotal();
});
