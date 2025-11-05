document.addEventListener('DOMContentLoaded', () => {
    const bell = document.getElementById('notificationBell');
    const panel = document.getElementById('notificationPanel');
    const list = document.getElementById('notificationList');
    const badge = document.getElementById('notificationCount');

    let notifications = [
        { mensaje: 'Tu pedido ha cambiado de Pendiente a En preparación.', leido: false },
        { mensaje: 'Tu pedido #102 fue entregado con éxito.', leido: false },
    ];

    // Mostrar notificaciones no leídas
    badge.textContent = notifications.filter(n => !n.leido).length;

    // Mostrar/ocultar panel
    bell.addEventListener('click', () => {
        panel.style.display = panel.style.display === 'block' ? 'none' : 'block';
        renderNotifications();
    });

    // Renderizar lista
    function renderNotifications() {
        list.innerHTML = '';
        notifications.forEach((n, i) => {
            const li = document.createElement('li');
            li.textContent = n.mensaje;
            if (!n.leido) li.classList.add('unread');
            li.addEventListener('click', () => marcarLeido(i));
            list.appendChild(li);
        });
    }

    // Marcar como leído
    function marcarLeido(index) {
        notifications[index].leido = true;
        badge.textContent = notifications.filter(n => !n.leido).length;
        renderNotifications();
    }

    // Simular nueva notificación (puedes reemplazar por AJAX más adelante)
    setTimeout(() => {
        const nueva = { mensaje: 'Tu pedido ha pasado a En camino 🚗', leido: false };
        notifications.unshift(nueva);
        badge.textContent = notifications.filter(n => !n.leido).length;
    }, 8000);
});
