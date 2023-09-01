import unittest
from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .views import *
from .forms import *
from .models import *
from django.core.paginator import Paginator
from django.utils import timezone

import re
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.contrib.staticfiles import finders
from reportlab.pdfgen import canvas
from xhtml2pdf import pisa
from io import BytesIO
from PIL import Image

from django.http import HttpResponse






class ProfileViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_profile_view_authenticated(self):
        request = self.factory.get(reverse('profile'))
        request.user = self.user

        response = profile(request)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inicio/profile.html')

    def test_profile_view_not_authenticated(self):
        request = self.factory.get(reverse('profile'))

        response = profile(request)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/profile/')

if __name__ == '__main__':
    unittest.main()




class MisPartesPolicialesTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_mis_partes_policiales(self):
        # Crear datos de prueba
        user = Usuario.objects.create(user=self.user)
        personal_policial = PersonalPolicial.objects.create(usuario=user)
        partes_policiales = [
            PartePolicial.objects.create(personalPolicial=personal_policial),
            PartePolicial.objects.create(personalPolicial=personal_policial),
            PartePolicial.objects.create(personalPolicial=personal_policial),
        ]

        # Crear una solicitud con paginación
        request = self.factory.get('/mis_partes_policiales/?page=2')
        request.user = self.user

        # Llamar a la vista y obtener la respuesta
        response = mis_partes_policiales(request)

        # Comprobar que la respuesta contiene los objetos de PartePolicial correctos
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['partes_policiales'].count(), 3)
        self.assertEqual(list(response.context_data['partes_policiales']), partes_policiales[3:])

        # Comprobar la paginación
        paginator = Paginator(partes_policiales, 6)
        self.assertEqual(response.context_data['partes_policiales'].paginator, paginator)
        self.assertEqual(response.context_data['partes_policiales'].number, 2)
        self.assertEqual(response.context_data['partes_policiales'].has_previous(), True)
        self.assertEqual(response.context_data['partes_policiales'].has_next(), False)

        # Comprobar el template utilizado
        self.assertTemplateUsed(response, 'partes_policiales/mis_partes_policiales.html')




class PartePolicialCreateViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.personal_policial = PersonalPolicial.objects.create(
            usuario=self.user,
            # Agregue los demás campos necesarios para crear un objeto de PersonalPolicial
        )
    
    def test_get_form_kwargs(self):
        request = self.factory.get('/parte_policial/create/')
        request.user = self.user

        view = PartePolicialCreateView()
        view.setup(request)

        expected_kwargs = {'user': self.user}
        actual_kwargs = view.get_form_kwargs()

        self.assertEqual(actual_kwargs, expected_kwargs)
        
    def test_form_valid(self):
        request = self.factory.post('/parte_policial/create/')
        request.user = self.user

        view = PartePolicialCreateView()
        view.setup(request)

        form = PartePolicialForm(data={'field1': 'value1', 'field2': 'value2'})  # Agregue los campos necesarios al formulario
        form.is_valid()

        response = view.form_valid(form)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profile'))
        
        parte_policial = PartePolicial.objects.get()  # Obtenga el objeto PartePolicial creado
        self.assertEqual(parte_policial.personalPolicial, self.personal_policial)
        self.assertEqual(parte_policial.fecha.date(), timezone.now().date())
        
    def test_get_context_data(self):
        request = self.factory.get('/parte_policial/create/')
        request.user = self.user

        view = PartePolicialCreateView()
        view.setup(request)

        context = view.get_context_data()

        self.assertEqual(context['vehiculo'], "-Sin datos, contacte a logística-")
        self.assertEqual(context['subcircuito'], "-Sin datos, contacte a logística-")
        self.assertEqual(context['fecha'].date(), timezone.now().date())


def remove_html_tags(text):
    return re.sub('<[^>]*>', '', text)

class TestRemoveHtmlTags(unittest.TestCase):
    def test_remove_html_tags(self):
        self.assertEqual(remove_html_tags('<p>Hello, <b>world!</b></p>'), 'Hello, world!')
        self.assertEqual(remove_html_tags('<a href="http://example.com">Click here</a>'), 'Click here')
        self.assertEqual(remove_html_tags('Plain text'), 'Plain text')
        self.assertEqual(remove_html_tags(''), '')

if __name__ == '__main__':
    unittest.main()


class PartePolicialPDFTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.image_path = finders.find('images/EscudonPNa.jpg')
        self.parte = PartePolicial.objects.create(observaciones='Observaciones', estado='Estado')

    def test_parte_policial_pdf(self):
        request = self.factory.get('/parte/policial/1')
        response = parte_policial_pdf(request, 1)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="parte_policial_1.pdf"')

    def test_create_pdf(self):
        image_pdf = BytesIO()
        doc = canvas.Canvas(image_pdf)

        parte = self.parte
        personal_policial = 'Nombre Apellido'

        doc.setFont('Helvetica-Bold', 14)
        doc.drawString(100, 700, 'POLICIA NACIONAL DEL ECUADOR')
        doc.setFont('Helvetica', 12)
        doc.drawString(100, 650, 'Parte Policial')
        doc.drawString(100, 600, f'Fecha: {parte.fecha}')
        doc.drawString(100, 550, f'Tipo de Parte: {parte.tipo_parte}')
        doc.drawString(100, 500, f'Observaciones: {parte.observaciones}')
        doc.drawString(100, 450, f'Estado: {parte.estado}')
        doc.drawString(100, 400, 'Firma de responsabilidad:')
        doc.drawString(100, 350, f'Responsable: {personal_policial}')
        doc.drawString(100, 300, 'Firma: ________________________')

        doc.save()

        pdf = BytesIO()
        pisa.CreatePDF(image_pdf.getvalue(), pdf)

        self.assertIsNotNone(pdf.getvalue())

    def tearDown(self):
        PartePolicial.objects.all().delete()



class OrdenMantenimientoPdfTestCase(TestCase):
    def test_orden_mantenimiento_pdf(self):
        # Crear una orden de mantenimiento de prueba
        orden_mantenimiento = OrdenMantenimiento.objects.create()

        # Obtener la URL de la vista
        url = reverse('orden_mantenimiento_pdf', args=[orden_mantenimiento.id])

        # Realizar una petición GET a la URL
        response = self.client.get(url)

        # Comprobar que la respuesta es un objeto HttpResponse
        self.assertIsInstance(response, HttpResponse)

        # Comprobar que la respuesta tiene el tipo de contenido correcto
        self.assertEqual(response['Content-Type'], 'application/pdf')

        # Comprobar que la respuesta tiene el encabezado Content-Disposition correcto
        self.assertEqual(
            response['Content-Disposition'],
            f'attachment; filename="orden_mantenimiento_{orden_mantenimiento.id}.pdf"'
        )



class QuejaSugerenciaTests(TestCase):
    def test_queja_sugerencia_post_valid(self):
        form_data = {
            'nombre': 'John Doe',
            'queja_sugerencia': '¡Excelente servicio!'
        }
        response = self.client.post(reverse('queja_sugerencia'), data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quejas/agradecimiento.html')

    def test_queja_sugerencia_post_invalid(self):
        form_data = {
            'nombre': '',
            'queja_sugerencia': '¡Excelente servicio!'
        }
        response = self.client.post(reverse('queja_sugerencia'), data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quejas/queja_sugerencia.html')
        self.assertFormError(response, 'form', 'nombre', 'Este campo es requerido.')

    def test_queja_sugerencia_get(self):
        response = self.client.get(reverse('queja_sugerencia'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quejas/queja_sugerencia.html')
        self.assertIsInstance(response.context['form'], QuejaSugerenciaForm)
