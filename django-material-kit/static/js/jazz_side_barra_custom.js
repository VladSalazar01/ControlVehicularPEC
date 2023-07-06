document.addEventListener('DOMContentLoaded', function () {
    var sidebar = document.querySelector('.main-sidebar');
    var appHome = sidebar.querySelector('#content-main .app-home');
    
    // Crear el grupo 'Información de Usuario'
    if (appHome) {
        var infoUsuarioGroup = document.createElement('li');
        infoUsuarioGroup.className = 'nav-item has-treeview';
        infoUsuarioGroup.innerHTML = `
            <a href="#" class="nav-link">
                <i class="nav-icon fas fa-users"></i>
                <p>
                    Información de Usuario
                    <i class="right fas fa-angle-left"></i>
                </p>
            </a>
            <ul class="nav nav-treeview" style="display: none;"></ul>
        `;
        appHome.appendChild(infoUsuarioGroup);

        var modelosUsuarios = appHome.querySelectorAll('[href*="home/usuario/"], [href*="home/tecnico/"], [href*="home/personalpolicial/"]');
        var subMenu = infoUsuarioGroup.querySelector('.nav-treeview');
        modelosUsuarios.forEach(function(modelo) {
            subMenu.appendChild(modelo.parentElement);
        });

        infoUsuarioGroup.querySelector('.nav-link').addEventListener('click', function(event) {
            event.preventDefault();
            var displayStyle = subMenu.style.display;
            subMenu.style.display = displayStyle === 'none' ? 'block' : 'none';
        });
    }

    // Código para el segundo grupo (sin cambios)
    var gestionOrdenesTrabajo = sidebar.querySelector('[href*="home/ordendetrabajo/"]');
    if (gestionOrdenesTrabajo) {
        var modelosOrdenesTrabajo = sidebar.querySelectorAll('[href*="home/ordenmantenimiento/"], [href*="home/ordencombustible/"]');
        modelosOrdenesTrabajo.forEach(function(modelo) {
            modelo.parentElement.style.display = 'none';
        });

        gestionOrdenesTrabajo.parentElement.style.backgroundColor = '#f2f2f2';
        gestionOrdenesTrabajo.parentElement.style.fontWeight = 'bold';

        gestionOrdenesTrabajo.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            modelosOrdenesTrabajo.forEach(function(modelo) {
                modelo.parentElement.style.display = modelo.parentElement.style.display === 'none' ? '' : 'none';
                modelo.parentElement.style.backgroundColor = '#fff';
                modelo.parentElement.style.borderLeft = '2px solid #ccc';
                modelo.parentElement.style.paddingLeft = '10px';
                modelo.parentElement.style.listStyle = 'none';
                modelo.parentElement.style.backgroundImage = 'none';
                var icon = modelo.parentElement.querySelector('.nav-icon');
                if (icon) {
                    icon.style.display = 'none';
                }
            });
        });
    }
});