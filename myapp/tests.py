from django.test import TestCase

# Create your tests here.
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User, Permission
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

class MySeleniumTests(StaticLiveServerTestCase):
    # carregar una BD de test
    fixtures = ['testdb.json',]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        # tanquem browser
        # comentar la propera línia si volem veure el resultat de l'execució al navegador
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        # anem directament a la pàgina d'accés a l'admin panel
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))

        # comprovem que el títol de la pàgina és el que esperem
        self.assertEqual( self.selenium.title , "Log in | Django site admin" )

        # introduïm dades de login i cliquem el botó "Log in" per entrar
        username_input = self.selenium.find_element(By.NAME,"username")
        username_input.send_keys('isard')
        password_input = self.selenium.find_element(By.NAME,"password")
        password_input.send_keys('pirineus')
        self.selenium.find_element(By.XPATH,'//input[@value="Log in"]').click()

        # testejem que hem entrat a l'admin panel comprovant el títol de la pàgina
        self.assertEqual( self.selenium.title , "Site administration | Django site admin" )

    def test_login_error(self):
        # comprovem que amb un usuari i contrasenya inexistent, el test falla
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))
        self.assertEqual( self.selenium.title , "Log in | Django site admin" )

        # introduim dades de login
        username_input = self.selenium.find_element(By.NAME,"username")
        username_input.send_keys('usuari_no_existent')
        password_input = self.selenium.find_element(By.NAME,"password")
        password_input.send_keys('contrasenya_incorrecta')
        self.selenium.find_element(By.XPATH,'//input[@value="Log in"]').click()

        # utilitzem assertNotEqual per testejar que NO hem entrat
        self.assertNotEqual( self.selenium.title , "Site administration | Django site admin" )
    def test_staff_can_view_but_not_add_or_delete_users(self):
        """
        Crea un usuari staff amb permís de 'view_user'
        i comprova que pot veure la llista d'usuaris
        però NO pot crear ni esborrar.
        """

        # Crear usuario staff con permiso de ver usuarios
        user = User.objects.create_user(
            username="staff_viewer",
            password="test1234",
            is_staff=True
        )
        view_perm = Permission.objects.get(codename="view_user")
        user.user_permissions.add(view_perm)

        # Login
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        self.selenium.find_element(By.NAME, "username").send_keys("staff_viewer")
        self.selenium.find_element(By.NAME, "password").send_keys("test1234")
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()

        # Ir a la lista de usuarios
        self.selenium.get(f"{self.live_server_url}/admin/auth/user/")

        # ✔ Puede ver la tabla de usuarios
        table = self.selenium.find_elements(By.ID, "result_list")
        self.assertEqual(len(table), 1, "El usuario debería poder ver la lista de usuarios")

        # ✖ No puede crear usuarios (no aparece el botón Add user)
        add_button = self.selenium.find_elements(By.CLASS_NAME, "addlink")
        self.assertEqual(len(add_button), 0, "El usuario NO debería poder crear usuarios")

        # ✖ No puede borrar usuarios (no aparecen checkboxes)
        delete_checkboxes = self.selenium.find_elements(By.NAME, "_selected_action")
        self.assertEqual(len(delete_checkboxes), 0, "El usuario NO debería poder borrar usuarios")

