// Dropdown menú usuario
function toggleDropdown() {
    const menu = document.getElementById('dropdownMenu');
    menu.style.display = menu.style.display === 'flex' ? 'none' : 'flex';
}
window.onclick = function(event) {
    const menu = document.getElementById('dropdownMenu');
    const avatar = document.querySelector('.user-avatar');
    if (!avatar.contains(event.target) && !menu.contains(event.target)) {
        menu.style.display = 'none';
    }
};

// === Gráficas ===
// Productos más vendidos
const productosData = {
    labels: window.DATA.top_productos_nombres,
    datasets: [{
        label: 'Cantidad vendida',
        data: window.DATA.top_productos_totales,
        backgroundColor: ['#f39c12','#3498db','#2ecc71','#9b59b6','#e74c3c']
    }]
};
new Chart(document.getElementById('chartProductos'), {
    type: 'bar',
    data: productosData,
});

// Pedidos por día
const pedidosDiaData = {
    labels: window.DATA.pedidos_por_dia_fechas,
    datasets: [{
        label: 'Pedidos',
        data: window.DATA.pedidos_por_dia_totales,
        borderColor: '#3498db',
        backgroundColor: '#3498db55',
        fill: true,
        tension: 0.3
    }]
};
new Chart(document.getElementById('chartPedidosDia'), {
    type: 'line',
    data: pedidosDiaData,
});

// Pedidos por estado
const pedidosEstadoData = {
    labels: window.DATA.pedidos_estado_labels,
    datasets: [{
        data: window.DATA.pedidos_estado_totales,
        backgroundColor: ['#2ecc71','#f39c12','#e74c3c','#9b59b6']
    }]
};
new Chart(document.getElementById('chartPedidosEstado'), {
    type: 'pie',
    data: pedidosEstadoData,
});
