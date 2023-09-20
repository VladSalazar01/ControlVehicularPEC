
from bs4 import BeautifulSoup

class AddButtonsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if 'text/html' in response['Content-Type']:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if request.path == '/admin/logout/':
                # Encuentra el contenedor principal y añade el botón "Atrás"
                main_content = soup.find(id='content-main')
                if main_content:
                    back_button = soup.new_tag('a', href='http://127.0.0.1:8000/', **{'class': 'btn btn-primary'})
                    back_button.string = 'Atrás'
                    main_content.insert(0, back_button)
                    # Añadir estilos para posicionar el botón en la esquina superior derecha
                    admin_button['style'] = 'position: absolute; top: 10px; right: 10px; z-index: 1000;'
                    body_tag.insert(0, admin_button)

            elif request.path == '/':
                # Encuentra el contenedor principal y añade el botón "Ir a Administración"
                body_tag = soup.find('body')
                if body_tag:
                    admin_button = soup.new_tag('a', href='http://127.0.0.1:8000/admin/', **{'class': 'btn btn-secondary'})
                    admin_button.string = 'Ir a Administración'
                    # Añadir estilos para posicionar el botón en la esquina superior derecha
                    admin_button['style'] = 'position: absolute; top: 10px; right: 10px; z-index: 1000;'
                    body_tag.insert(0, admin_button)

            response.content = str(soup)

        return response
