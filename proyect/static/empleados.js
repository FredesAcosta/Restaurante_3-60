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
        }