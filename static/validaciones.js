

document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("termsModal");
    const openBtn = document.getElementById("openModal");
    const closeBtn = document.getElementById("closeModal");

    // Abrir modal
    openBtn.onclick = () => {
        modal.style.display = "block";
    };

    // Cerrar modal
    closeBtn.onclick = () => {
        modal.style.display = "none";
    };

    // Cerrar si se da click fuera del contenido
    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };
});
