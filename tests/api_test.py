import json
from unittest.mock import Mock, patch

import pytest
import requests

from myrpl_cli.errors import MissingCredentialsError
from myrpl_cli.credential_manager import CredentialManager
from myrpl_cli.models import Course, Activity, Submission, SubmissionResult
from myrpl_cli.api import API


@pytest.fixture(name="credential_manager")
def mock_credential_manager():
	return Mock(spec=CredentialManager)


@pytest.fixture(name="api")
def mock_api(credential_manager):
	return API(credential_manager)


@pytest.fixture(name="course")
def mock_course():
	return Course(
		id=1,
		name="Test Course",
		university="Test University",
		university_course_id="1",
		description="Test Description",
		active=True,
		semester="1C-2023",
		semester_start_date="2023-01-01T00:00:00Z",
		semester_end_date="2023-06-30T00:00:00Z",
		img_uri="http://example.com/image.png",
		date_created="2023-01-01T00:00:00Z",
		last_updated="2023-01-01T00:00:00Z",
	)


@pytest.fixture(name="activity")
def mock_activity(course):
	return Activity(
		course=course,
		id=1,
		name="Test Activity",
		description="description",
		category_name="Test Category",
		category_id=2,
		category_description="category_description",
		language="python",
		activity_unit_tests="def test1():\n\tassert(True)\n\treturn",
		file_id=1,
	)


@pytest.fixture(name="submission")
def mock_submission(activity):
	return Submission(
		activity=activity,
		id=1,
		submission_file_name="submission.py",
		submission_file_type="text/plain",
		submission_file_id=1,
		is_iotested=False,
		activity_starting_files_name="starting_files.tar.gz",
		activity_starting_files_type="application/gzip",
		activity_starting_files_id=1,
		activity_language="python",
		activity_unit_tests="def test1():\n\tassert(True)\n\treturn",
	)


def test_login(api):
	"""It should login and return the login data"""

	with patch("requests.post") as mock_post:
		mock_response = Mock()
		mock_response.json.return_value = {
			"token_type": "Bearer",
			"access_token": "test_token",
		}
		mock_post.return_value = mock_response

		login_data = api.login("test@example.com", "password")

		mock_post.assert_called_once()
		call_args = mock_post.call_args
		assert call_args[0][0].endswith("/api/auth/login")
		assert json.loads(call_args[1]["data"]) == {
			"username_or_email": "test@example.com",
			"password": "password",
		}
		assert call_args[1]["timeout"] == 10

		assert login_data["token_type"] == "Bearer"
		assert login_data["access_token"] == "test_token"
		assert api.headers["Authorization"] == "Bearer test_token"


def test_fetch_courses(api):
	"""It should request, serialize and return all courses"""

	with patch.object(api, "auth_api_call") as mock_call:
		mock_call.return_value = [
			{
				"id": 1,
				"name": "Curso de prueba 1",
				"university": "FIUBA",
				"university_course_id": "1",
				"description": "Un curso de prueba!",
				"active": False,
				"semester": "1c-2020",
				"semester_start_date": "2020-05-04T00:00:00Z",
				"semester_end_date": "2020-09-26T00:00:00Z",
				"img_uri": "http://res.cloudinary.com/tutecano22/image/upload/v1595991527/avfp865q9iphakzotoxi.png",
				"date_created": "2020-07-29T02:58:48Z",
				"last_updated": "2020-07-29T02:58:48Z",
			},
			{
				"id": 57,
				"name": "Teoría de Algorithms",
				"university": "FIUBA",
				"university_course_id": "75.29/95.06",
				"description": "Curso Buchwald - Genender",
				"active": True,
				"semester": "2C-2023",
				"semester_start_date": "2023-08-13T00:00:00Z",
				"semester_end_date": "2024-01-01T00:00:00Z",
				"img_uri": "http://res.cloudinary.com/tutecano22/image/upload/v1677868354/iamjug66cowfbf4t5ac5.jpg",
				"date_created": "2023-08-03T16:52:59Z",
				"last_updated": "2023-08-03T16:52:59Z",
				"enrolled": True,
				"accepted": True,
			},
			{
				"id": 63,
				"name": "FundamentosMendez 2024 1C",
				"university": "FIUBA",
				"university_course_id": "75.40-95.14",
				"description": "Curso de Fundamentos ",
				"active": True,
				"semester": "2024-1C",
				"semester_start_date": "2024-03-22T00:00:00Z",
				"semester_end_date": "2024-10-01T00:00:00Z",
				"img_uri": "http://res.cloudinary.com/tutecano22/image/upload/v1679706311/gtava0f7f7s3t5sab12q.webp",
				"date_created": "2024-03-22T17:54:41Z",
				"last_updated": "2024-03-22T17:54:41Z",
			},
		]

		courses = api.fetch_courses()

		mock_call.assert_called_once()
		call_args = mock_call.call_args
		assert call_args[0][0] == "get"
		assert call_args[0][1].endswith("/api/courses")

		assert len(courses) == 3
		assert isinstance(courses[0], Course)
		assert courses[0].id == 1
		assert courses[0].name == "Curso de prueba 1"
		assert isinstance(courses[1], Course)
		assert courses[1].id == 57
		assert courses[1].name == "Teoría de Algorithms"
		assert isinstance(courses[2], Course)
		assert courses[2].id == 63
		assert courses[2].name == "FundamentosMendez 2024 1C"


def test_fetch_activities(api, course):
	"""It should request, serialize and return all activities for a course"""

	with patch.object(api, "auth_api_call") as mock_call:
		mock_call.return_value = [
			{
				"id": 5259,
				"course_id": 57,
				"category_id": 630,
				"category_name": "0 - TP0",
				"category_description": "Entrega obligatoria, sin nota",
				"name": "Alumno más bajo",
				"description": 'La Escuela Nacional 32 "Alan Turing" de Bragado tiene una forma',
				"language": "PYTHON3",
				"is_iotested": False,
				"active": True,
				"deleted": False,
				"points": 1,
				"file_id": 485090,
				"submission_status": "SUCCESS",
				"last_submission_date": "2024-03-25T13:30:20Z",
				"date_created": "2023-08-03T16:52:59Z",
				"last_updated": "2024-06-22T21:25:30Z",
			},
			{
				"id": 5790,
				"course_id": 57,
				"category_id": 694,
				"category_name": "1 - División y Conquista",
				"category_description": "Ejercicios de División y Conquista",
				"name": "04 - Picos",
				"description": 'Se tiene un arreglo de _N >= 3_ elementos en forma de pico, esto es: estrictamente creciente hasta una determinada posición `p`, y estrictamente decreciente a partir de ella (con `0 < p < N - 1`). Por ejemplo, en el arreglo `[1, 2, 3, 1, 0, -2]` la posición del pico es `p = 2`. Se pide:\r\n\r\n1. Implementar un algoritmo de división y conquista de orden O(log n) que encuentre la posición `p` del pico: `func PosicionPico(v []int, ini, fin int) int`. La función será invocada inicialmente como: `PosicionPico(v, 0, len(v)-1)`, y tiene como pre-condición que el arreglo tenga forma de pico.\r\n\r\n2. Justificar el orden del algoritmo mediante el teorema maestro.\r\n\r\nNota sobre RPL: en este ejercicio se pide cumplir la tarea "por división y conquista, en O(log(n))". Por las características de la herramienta, no podemos verificarlo de forma automática, pero se busca que se implemente con dicha restricción',
				"language": "PYTHON3",
				"is_iotested": False,
				"active": True,
				"deleted": False,
				"points": 1,
				"file_id": 559135,
				"submission_status": "",
				"date_created": "2024-01-12T22:27:03Z",
				"last_updated": "2024-04-10T20:33:29Z",
			},
			{
				"id": 5799,
				"course_id": 57,
				"category_id": 697,
				"category_name": "3 - Backtracking",
				"category_description": "Ejercicios de Backtracking",
				"name": "02 - Coloreo de grafos",
				"description": "Implementar un algoritmo que reciba un grafo y un número n que",
				"language": "PYTHON3",
				"is_iotested": False,
				"active": True,
				"deleted": False,
				"points": 2,
				"file_id": 559210,
				"submission_status": "",
				"date_created": "2024-01-13T04:52:02Z",
				"last_updated": "2024-06-06T22:23:44Z",
			},
		]

		activities = api.fetch_activities(course)

		assert len(activities) == 3
		assert isinstance(activities[0], Activity)
		assert activities[0].id == 5259
		assert activities[0].course == course
		assert activities[0].category.id == 630
		assert activities[0].category.name == "0 - TP0"
		assert activities[0].category.description == "Entrega obligatoria, sin nota"
		assert activities[0].name == "Alumno más bajo"
		assert activities[0].description == 'La Escuela Nacional 32 "Alan Turing" de Bragado tiene una forma'
		assert activities[0].language == "PYTHON3"
		assert activities[0].activity_unit_tests is None
		assert activities[0].file_id == 485090
		assert activities[0].submission_status == "SUCCESS"
		assert isinstance(activities[1], Activity)
		assert activities[1].id == 5790
		assert activities[1].course == course
		assert activities[1].category.id == 694
		assert activities[1].category.name == "1 - División y Conquista"
		assert activities[1].category.description == "Ejercicios de División y Conquista"
		assert activities[1].name == "04 - Picos"
		assert (
			activities[1].description
			== 'Se tiene un arreglo de _N >= 3_ elementos en forma de pico, esto es: estrictamente creciente hasta una determinada posición `p`, y estrictamente decreciente a partir de ella (con `0 < p < N - 1`). Por ejemplo, en el arreglo `[1, 2, 3, 1, 0, -2]` la posición del pico es `p = 2`. Se pide:\r\n\r\n1. Implementar un algoritmo de división y conquista de orden O(log n) que encuentre la posición `p` del pico: `func PosicionPico(v []int, ini, fin int) int`. La función será invocada inicialmente como: `PosicionPico(v, 0, len(v)-1)`, y tiene como pre-condición que el arreglo tenga forma de pico.\r\n\r\n2. Justificar el orden del algoritmo mediante el teorema maestro.\r\n\r\nNota sobre RPL: en este ejercicio se pide cumplir la tarea "por división y conquista, en O(log(n))". Por las características de la herramienta, no podemos verificarlo de forma automática, pero se busca que se implemente con dicha restricción'
		)
		assert activities[1].language == "PYTHON3"
		assert activities[1].activity_unit_tests is None
		assert activities[1].file_id == 559135
		assert isinstance(activities[2], Activity)
		assert activities[2].id == 5799
		assert activities[2].course == course
		assert activities[2].category.id == 697
		assert activities[2].category.name == "3 - Backtracking"
		assert activities[2].category.description == "Ejercicios de Backtracking"
		assert activities[2].name == "02 - Coloreo de grafos"
		assert activities[2].description == "Implementar un algoritmo que reciba un grafo y un número n que"
		assert activities[2].language == "PYTHON3"
		assert activities[2].activity_unit_tests is None
		assert activities[2].file_id == 559210


def test_fetch_activity_info(api, activity):
	"""It should request, serialize and return the additional info for an activity"""

	with patch.object(api, "auth_api_call") as mock_call:
		mock_call.return_value = {
			"id": 5259,
			"course_id": 57,
			"category_id": 630,
			"category_name": "0 - TP0",
			"category_description": "Entrega obligatoria, sin nota",
			"name": "Alumno más bajo",
			"description": 'La Escuela Nacional 32 "Alan Turing" de Bragado tiene una forma particular de requerir que los alumnos foremen fila. En vez del clásico "de menor a mayor altura", lo hacen primero con alumnos yendo con altura decreciente, hasta llegado un punto que empieza a ir de forma creciente, hasta terminar con todos los alumnos. \r\n\r\nPor ejemplo las alturas podrían set `1.2, 1.15, 1.14, 1.12, 1.02, 0.98, 1.18, 1.23`. \r\n\r\n1. Implementar una función `indice_mas_bajo` que dado un arreglo/lista de alumnos(*) que represente dicha fila, devuelva el índice del alumno más bajo, en **tiempo logarítmico**. Se puede asumir que hay al menos 3 alumnos. En el ejemplo, el alumno más bajo es aquel con altura 0.98.\r\n\r\n2. Implementar una función `validar_mas_bajo` que dado un arreglo/lista de alumnos(*) y un índice, valid (devuelva `True` o `False`) si dicho índice corresponde al del alumno más bajo de la fila. (Aclaración: esto debería poder realizarse en tiempo constante)\r\n\r\n(*)\r\nLos alumnos son de la forma: \r\n```\r\nalumno {\r\n    nombre (string)\r\n    altura (float)\r\n}\r\n```\r\nSe puede acceder a la altura de un alumno haciendo `variable_tipo_alumno.altura`.\r\n\r\n**Importante**: considerar que si la prueba de volumen no pasa, es probable que sea porque no están cumpliendo con la complejidad requerida. ',
			"language": "python",
			"is_iotested": False,
			"active": True,
			"deleted": False,
			"points": 1,
			"file_id": 485090,
			"activity_unit_tests": "import unittest\nimport timeout_decorator\nimport alumno\nimport random\nimport sys\nimport os\n\n\n# Disable\ndef blockPrint():\n    sys.stdout = open(os.devnull, 'w')\n\n# Restore\ndef enablePrint():\n    sys.stdout = sys.__stdout__\n\n\ndef without_print(fn):\n  try:\n    blockPrint()\n    fn()\n  finally:\n    enablePrint()\n\n\nclass AlumnoTest:\n    def __init__(self, nombre, altura):\n        self.nombre = nombre\n        self.altura = altura\n\n\ndef crear_alumnos(alturas):\n    alus = []\n    for i in range(len(alturas)):\n        alus.append(AlumnoTest(\"jaimito\" + str(i), alturas[i]))\n    return alus\n\n\nclass TestMethods(unittest.TestCase):\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_medio(self):\n        alus = crear_alumnos([1.5, 1.4, 1.3, 1.2, 1.14, 1.2, 1.23, 1.32])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 4))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 4)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_bastante_al_inicio(self):\n        alus = crear_alumnos([2, 0.8, 0.9, 1, 1.1, 1.2, 1.4, 1.41, 1.7])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 1))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 1)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_bastante_al_final(self):\n        alus = crear_alumnos([1.7, 1.41, 1.4, 1.2, 1.1, 1, 0.9, 0.8, 2])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 7))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 7)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(6)  # segundos\n    def test_volumen(self):\n        n = 18768\n        k = random.randint(5, n - 5)\n        nums = [(n - k + i if i > k else n - i) for i in range(n)]\n        alus = crear_alumnos(nums)\n        for _ in range(n):\n            without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), k))\n            without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, k)))\n            without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k + 1)))\n            without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k - 1)))\n        k = 4\n        nums = [(n - k + i if i > k else n - i) for i in range(n)]\n        alus = crear_alumnos(nums)\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), k))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, k)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k + 1)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k - 1)))\n",
			"compilation_flags": "",
			"activity_iotests": [],
			"date_created": "2023-08-03T16:52:59Z",
			"last_updated": "2024-04-04T18:56:50Z",
		}
		updated_activity = api.fetch_activity_info(activity)

		assert isinstance(updated_activity, Activity)
		assert updated_activity.id == 5259
		assert updated_activity.course == activity.course
		assert updated_activity.category.id == 630
		assert updated_activity.category.name == "0 - TP0"
		assert updated_activity.category.description == "Entrega obligatoria, sin nota"
		assert updated_activity.name == "Alumno más bajo"
		assert (
			updated_activity.description
			== 'La Escuela Nacional 32 "Alan Turing" de Bragado tiene una forma particular de requerir que los alumnos foremen fila. En vez del clásico "de menor a mayor altura", lo hacen primero con alumnos yendo con altura decreciente, hasta llegado un punto que empieza a ir de forma creciente, hasta terminar con todos los alumnos. \r\n\r\nPor ejemplo las alturas podrían set `1.2, 1.15, 1.14, 1.12, 1.02, 0.98, 1.18, 1.23`. \r\n\r\n1. Implementar una función `indice_mas_bajo` que dado un arreglo/lista de alumnos(*) que represente dicha fila, devuelva el índice del alumno más bajo, en **tiempo logarítmico**. Se puede asumir que hay al menos 3 alumnos. En el ejemplo, el alumno más bajo es aquel con altura 0.98.\r\n\r\n2. Implementar una función `validar_mas_bajo` que dado un arreglo/lista de alumnos(*) y un índice, valid (devuelva `True` o `False`) si dicho índice corresponde al del alumno más bajo de la fila. (Aclaración: esto debería poder realizarse en tiempo constante)\r\n\r\n(*)\r\nLos alumnos son de la forma: \r\n```\r\nalumno {\r\n    nombre (string)\r\n    altura (float)\r\n}\r\n```\r\nSe puede acceder a la altura de un alumno haciendo `variable_tipo_alumno.altura`.\r\n\r\n**Importante**: considerar que si la prueba de volumen no pasa, es probable que sea porque no están cumpliendo con la complejidad requerida. '
		)
		assert updated_activity.language == "python"
		assert (
			updated_activity.activity_unit_tests
			== "import unittest\nimport timeout_decorator\nimport alumno\nimport random\nimport sys\nimport os\n\n\n# Disable\ndef blockPrint():\n    sys.stdout = open(os.devnull, 'w')\n\n# Restore\ndef enablePrint():\n    sys.stdout = sys.__stdout__\n\n\ndef without_print(fn):\n  try:\n    blockPrint()\n    fn()\n  finally:\n    enablePrint()\n\n\nclass AlumnoTest:\n    def __init__(self, nombre, altura):\n        self.nombre = nombre\n        self.altura = altura\n\n\ndef crear_alumnos(alturas):\n    alus = []\n    for i in range(len(alturas)):\n        alus.append(AlumnoTest(\"jaimito\" + str(i), alturas[i]))\n    return alus\n\n\nclass TestMethods(unittest.TestCase):\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_medio(self):\n        alus = crear_alumnos([1.5, 1.4, 1.3, 1.2, 1.14, 1.2, 1.23, 1.32])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 4))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 4)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_bastante_al_inicio(self):\n        alus = crear_alumnos([2, 0.8, 0.9, 1, 1.1, 1.2, 1.4, 1.41, 1.7])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 1))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 1)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_bastante_al_final(self):\n        alus = crear_alumnos([1.7, 1.41, 1.4, 1.2, 1.1, 1, 0.9, 0.8, 2])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 7))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 7)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(6)  # segundos\n    def test_volumen(self):\n        n = 18768\n        k = random.randint(5, n - 5)\n        nums = [(n - k + i if i > k else n - i) for i in range(n)]\n        alus = crear_alumnos(nums)\n        for _ in range(n):\n            without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), k))\n            without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, k)))\n            without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k + 1)))\n            without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k - 1)))\n        k = 4\n        nums = [(n - k + i if i > k else n - i) for i in range(n)]\n        alus = crear_alumnos(nums)\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), k))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, k)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k + 1)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k - 1)))\n"
		)
		assert updated_activity.file_id == 485090


def test_fetch_files(api):
	"""It should request and return the initial code for an activity"""

	with patch.object(api, "auth_api_call") as mock_call:
		mock_call.return_value = {
			"file_1.py": "def initial_code():\n    pass",
			"file_2.py": "def da_function():\n    pass",
		}

		files = api.fetch_files(3)

		mock_call.assert_called_once()
		call_args = mock_call.call_args
		assert call_args[0][0] == "get"
		assert call_args[0][1].endswith("/api/getFileForStudent/3")

		assert files == {
			"file_1.py": "def initial_code():\n    pass",
			"file_2.py": "def da_function():\n    pass",
		}


def test_fetch_submissions(api, activity):
	"""
	It should request, serialize and return
	all the submissions for an activity
	"""

	with patch.object(api, "auth_api_call") as mock_call:
		mock_call.return_value = [
			{
				"id": 569096,
				"activity_id": 5259,
				"submission_file_name": "57_5259_2192",
				"submission_file_type": "application/gzip",
				"submission_file_id": 579801,
				"is_iotested": False,
				"activity_starting_files_name": "2023-08-03_57_Alumno más bajo.tar.gz",
				"activity_starting_files_type": "application/gzip",
				"activity_starting_files_id": 485090,
				"activity_language": "python_3.7",
				"activity_unit_tests": "import unittest\nimport timeout_decorator\nimport alumno\nimport random\nimport sys\nimport os\n\n\n# Disable\ndef blockPrint():\n    sys.stdout = open(os.devnull, 'w')\n\n# Restore\ndef enablePrint():\n    sys.stdout = sys.__stdout__\n\n\ndef without_print(fn):\n  try:\n    blockPrint()\n    fn()\n  finally:\n    enablePrint()\n\n\nclass AlumnoTest:\n    def __init__(self, nombre, altura):\n        self.nombre = nombre\n        self.altura = altura\n\n\ndef crear_alumnos(alturas):\n    alus = []\n    for i in range(len(alturas)):\n        alus.append(AlumnoTest(\"jaimito\" + str(i), alturas[i]))\n    return alus\n\n\nclass TestMethods(unittest.TestCase):\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_medio(self):\n        alus = crear_alumnos([1.5, 1.4, 1.3, 1.2, 1.14, 1.2, 1.23, 1.32])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 4))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 4)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_bastante_al_inicio(self):\n        alus = crear_alumnos([2, 0.8, 0.9, 1, 1.1, 1.2, 1.4, 1.41, 1.7])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 1))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 1)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_bastante_al_final(self):\n        alus = crear_alumnos([1.7, 1.41, 1.4, 1.2, 1.1, 1, 0.9, 0.8, 2])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 7))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 7)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(6)  # segundos\n    def test_volumen(self):\n        n = 18768\n        k = random.randint(5, n - 5)\n        nums = [(n - k + i if i > k else n - i) for i in range(n)]\n        alus = crear_alumnos(nums)\n        for _ in range(n):\n            without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), k))\n            without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, k)))\n            without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k + 1)))\n            without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k - 1)))\n        k = 4\n        nums = [(n - k + i if i > k else n - i) for i in range(n)]\n        alus = crear_alumnos(nums)\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), k))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, k)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k + 1)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k - 1)))\n",
				"activity_iotests": [],
				"submission_status": "FAILURE",
				"is_final_solution": False,
				"exit_message": "Completed all stages",
				"stderr": "",
				"stdout": "2024-03-25 13:23:17,682 RPL-2.0      INFO     Build Started\n2024-03-25 13:23:17,683 RPL-2.0      INFO     Building\n2024-03-25 13:23:17,683 RPL-2.0      INFO     start_BUILD\n/usr/bin/python3.10 /usr/custom_compileall.py\n2024-03-25 13:23:17,776 RPL-2.0      INFO     end_BUILD\n2024-03-25 13:23:17,776 RPL-2.0      INFO     Build Ended\n2024-03-25 13:23:17,776 RPL-2.0      INFO     Run Started\n2024-03-25 13:23:17,777 RPL-2.0      INFO     Running Unit Tests\n2024-03-25 13:23:17,777 RPL-2.0      INFO     start_RUN\n/usr/bin/python3.10 unit_test_wrapper.pyc\n2024-03-25 13:23:18,086 RPL-2.0      INFO     end_RUN\n2024-03-25 13:23:18,086 RPL-2.0      INFO     RUN OK\n2024-03-25 13:23:18,086 RPL-2.0      INFO     Run Ended\n",
				"io_test_run_results": [],
				"unit_test_run_results": [
					{
						"id": 1403361,
						"test_name": "test_bastante_al_final",
						"passed": False,
						"error_messages": 'Traceback (most recent call last):\n  File "/usr/local/lib/python3.10/dist-packages/timeout_decorator/timeout_decorator.py", line 82, in new_function\n    return function(*args, **kwargs)\n  File "./unit_test.py", line 39, in test_bastante_al_final\nAssertionError: 0 != 7\n',
					},
					{
						"id": 1403362,
						"test_name": "test_bastante_al_inicio",
						"passed": False,
						"error_messages": 'Traceback (most recent call last):\n  File "/usr/local/lib/python3.10/dist-packages/timeout_decorator/timeout_decorator.py", line 82, in new_function\n    return function(*args, **kwargs)\n  File "./unit_test.py", line 32, in test_bastante_al_inicio\nAssertionError: 8 != 1\n',
					},
				],
				"submission_date": "2024-03-25T13:23:18Z",
			},
			{
				"id": 569100,
				"activity_id": 5259,
				"submission_file_name": "57_5259_2192",
				"submission_file_type": "application/gzip",
				"submission_file_id": 579805,
				"is_iotested": False,
				"activity_starting_files_name": "2023-08-03_57_Alumno más bajo.tar.gz",
				"activity_starting_files_type": "application/gzip",
				"activity_starting_files_id": 485090,
				"activity_language": "python_3.7",
				"activity_unit_tests": "import unittest\nimport timeout_decorator\nimport alumno\nimport random\nimport sys\nimport os\n\n\n# Disable\ndef blockPrint():\n    sys.stdout = open(os.devnull, 'w')\n\n# Restore\ndef enablePrint():\n    sys.stdout = sys.__stdout__\n\n\ndef without_print(fn):\n  try:\n    blockPrint()\n    fn()\n  finally:\n    enablePrint()\n\n\nclass AlumnoTest:\n    def __init__(self, nombre, altura):\n        self.nombre = nombre\n        self.altura = altura\n\n\ndef crear_alumnos(alturas):\n    alus = []\n    for i in range(len(alturas)):\n        alus.append(AlumnoTest(\"jaimito\" + str(i), alturas[i]))\n    return alus\n\n\nclass TestMethods(unittest.TestCase):\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_medio(self):\n        alus = crear_alumnos([1.5, 1.4, 1.3, 1.2, 1.14, 1.2, 1.23, 1.32])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 4))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 4)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_bastante_al_inicio(self):\n        alus = crear_alumnos([2, 0.8, 0.9, 1, 1.1, 1.2, 1.4, 1.41, 1.7])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 1))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 1)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_bastante_al_final(self):\n        alus = crear_alumnos([1.7, 1.41, 1.4, 1.2, 1.1, 1, 0.9, 0.8, 2])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 7))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 7)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(6)  # segundos\n    def test_volumen(self):\n        n = 18768\n        k = random.randint(5, n - 5)\n        nums = [(n - k + i if i > k else n - i) for i in range(n)]\n        alus = crear_alumnos(nums)\n        for _ in range(n):\n            without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), k))\n            without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, k)))\n            without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k + 1)))\n            without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k - 1)))\n        k = 4\n        nums = [(n - k + i if i > k else n - i) for i in range(n)]\n        alus = crear_alumnos(nums)\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), k))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, k)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k + 1)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k - 1)))\n",
				"activity_iotests": [],
				"submission_status": "SUCCESS",
				"is_final_solution": True,
				"exit_message": "Completed all stages",
				"stderr": "",
				"stdout": "2024-03-25 13:30:15,226 RPL-2.0      INFO     Build Started\n2024-03-25 13:30:15,227 RPL-2.0      INFO     Building\n2024-03-25 13:30:15,227 RPL-2.0      INFO     start_BUILD\n/usr/bin/python3.10 /usr/custom_compileall.py\n2024-03-25 13:30:15,373 RPL-2.0      INFO     end_BUILD\n2024-03-25 13:30:15,373 RPL-2.0      INFO     Build Ended\n2024-03-25 13:30:15,373 RPL-2.0      INFO     Run Started\n2024-03-25 13:30:15,374 RPL-2.0      INFO     Running Unit Tests\n2024-03-25 13:30:15,374 RPL-2.0      INFO     start_RUN\n/usr/bin/python3.10 unit_test_wrapper.pyc\n2024-03-25 13:30:16,671 RPL-2.0      INFO     end_RUN\n2024-03-25 13:30:16,671 RPL-2.0      INFO     RUN OK\n2024-03-25 13:30:16,671 RPL-2.0      INFO     Run Ended\n",
				"io_test_run_results": [],
				"unit_test_run_results": [
					{
						"id": 1403380,
						"test_name": "test_bastante_al_final",
						"passed": True,
					},
					{
						"id": 1403381,
						"test_name": "test_bastante_al_inicio",
						"passed": True,
					},
					{"id": 1403382, "test_name": "test_medio", "passed": True},
					{"id": 1403383, "test_name": "test_volumen", "passed": True},
				],
				"submission_date": "2024-03-25T13:30:15Z",
			},
		]

		submissions = api.fetch_submissions(activity)

		assert len(submissions) == 2
		assert isinstance(submissions[0], Submission)
		assert submissions[0].id == 569096
		assert submissions[0].activity == activity
		assert submissions[0].submission_file_name == "57_5259_2192"
		assert submissions[0].submission_file_type == "application/gzip"
		assert submissions[0].submission_file_id == 579801
		assert submissions[0].is_iotested is False
		assert submissions[0].activity_starting_files_name == "2023-08-03_57_Alumno más bajo.tar.gz"
		assert submissions[0].activity_starting_files_type == "application/gzip"
		assert submissions[0].activity_starting_files_id == 485090
		assert submissions[0].activity_language == "python_3.7"
		assert (
			submissions[0].activity_unit_tests
			== "import unittest\nimport timeout_decorator\nimport alumno\nimport random\nimport sys\nimport os\n\n\n# Disable\ndef blockPrint():\n    sys.stdout = open(os.devnull, 'w')\n\n# Restore\ndef enablePrint():\n    sys.stdout = sys.__stdout__\n\n\ndef without_print(fn):\n  try:\n    blockPrint()\n    fn()\n  finally:\n    enablePrint()\n\n\nclass AlumnoTest:\n    def __init__(self, nombre, altura):\n        self.nombre = nombre\n        self.altura = altura\n\n\ndef crear_alumnos(alturas):\n    alus = []\n    for i in range(len(alturas)):\n        alus.append(AlumnoTest(\"jaimito\" + str(i), alturas[i]))\n    return alus\n\n\nclass TestMethods(unittest.TestCase):\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_medio(self):\n        alus = crear_alumnos([1.5, 1.4, 1.3, 1.2, 1.14, 1.2, 1.23, 1.32])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 4))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 4)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_bastante_al_inicio(self):\n        alus = crear_alumnos([2, 0.8, 0.9, 1, 1.1, 1.2, 1.4, 1.41, 1.7])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 1))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 1)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_bastante_al_final(self):\n        alus = crear_alumnos([1.7, 1.41, 1.4, 1.2, 1.1, 1, 0.9, 0.8, 2])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 7))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 7)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(6)  # segundos\n    def test_volumen(self):\n        n = 18768\n        k = random.randint(5, n - 5)\n        nums = [(n - k + i if i > k else n - i) for i in range(n)]\n        alus = crear_alumnos(nums)\n        for _ in range(n):\n            without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), k))\n            without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, k)))\n            without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k + 1)))\n            without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k - 1)))\n        k = 4\n        nums = [(n - k + i if i > k else n - i) for i in range(n)]\n        alus = crear_alumnos(nums)\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), k))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, k)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k + 1)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k - 1)))\n"
		)
		assert submissions[0].submission_status == "FAILURE"
		assert submissions[0].is_final_solution is False
		assert submissions[0].exit_message == "Completed all stages"
		assert submissions[0].stderr == ""
		assert (
			submissions[0].stdout
			== "2024-03-25 13:23:17,682 RPL-2.0      INFO     Build Started\n2024-03-25 13:23:17,683 RPL-2.0      INFO     Building\n2024-03-25 13:23:17,683 RPL-2.0      INFO     start_BUILD\n/usr/bin/python3.10 /usr/custom_compileall.py\n2024-03-25 13:23:17,776 RPL-2.0      INFO     end_BUILD\n2024-03-25 13:23:17,776 RPL-2.0      INFO     Build Ended\n2024-03-25 13:23:17,776 RPL-2.0      INFO     Run Started\n2024-03-25 13:23:17,777 RPL-2.0      INFO     Running Unit Tests\n2024-03-25 13:23:17,777 RPL-2.0      INFO     start_RUN\n/usr/bin/python3.10 unit_test_wrapper.pyc\n2024-03-25 13:23:18,086 RPL-2.0      INFO     end_RUN\n2024-03-25 13:23:18,086 RPL-2.0      INFO     RUN OK\n2024-03-25 13:23:18,086 RPL-2.0      INFO     Run Ended\n"
		)
		assert submissions[0].io_test_run_results == []
		assert len(submissions[0].unit_test_run_results) == 2
		assert submissions[0].unit_test_run_results[0].id == 1403361
		assert submissions[0].unit_test_run_results[0].test_name == "test_bastante_al_final"
		assert submissions[0].unit_test_run_results[0].passed is False
		assert (
			submissions[0].unit_test_run_results[0].error_messages
			== 'Traceback (most recent call last):\n  File "/usr/local/lib/python3.10/dist-packages/timeout_decorator/timeout_decorator.py", line 82, in new_function\n    return function(*args, **kwargs)\n  File "./unit_test.py", line 39, in test_bastante_al_final\nAssertionError: 0 != 7\n'
		)
		assert submissions[0].unit_test_run_results[1].id == 1403362
		assert submissions[0].unit_test_run_results[1].test_name == "test_bastante_al_inicio"
		assert submissions[0].unit_test_run_results[1].passed is False
		assert (
			submissions[0].unit_test_run_results[1].error_messages
			== 'Traceback (most recent call last):\n  File "/usr/local/lib/python3.10/dist-packages/timeout_decorator/timeout_decorator.py", line 82, in new_function\n    return function(*args, **kwargs)\n  File "./unit_test.py", line 32, in test_bastante_al_inicio\nAssertionError: 8 != 1\n'
		)
		assert submissions[0].submission_date == "2024-03-25T13:23:18Z"


def test_fetch_final_submission(api, activity):
	"""
	It should request, serialize and return
	the final submission for an activity
	"""

	with patch.object(api, "auth_api_call") as mock_call:
		mock_call.return_value = {
			"id": 569100,
			"submission_file_name": "57_5259_2192",
			"submission_file_type": "application/gzip",
			"submission_file_id": 579805,
			"activity_starting_files_name": "2023-08-03_57_Alumno más bajo.tar.gz",
			"activity_starting_files_type": "application/gzip",
			"activity_starting_files_id": 485090,
			"activity_language": "python_3.7",
			"is_iotested": False,
			"activity_unit_tests_content": "",
			"compilation_flags": "",
			"activity_iotests": [],
		}

		final_submission = api.fetch_final_submission(activity)

		assert isinstance(final_submission, Submission)
		assert final_submission.id == 569100
		assert final_submission.activity == activity
		assert final_submission.submission_file_name == "57_5259_2192"
		assert final_submission.submission_file_type == "application/gzip"
		assert final_submission.submission_file_id == 579805
		assert final_submission.is_iotested is False
		assert final_submission.activity_starting_files_name == "2023-08-03_57_Alumno más bajo.tar.gz"
		assert final_submission.activity_starting_files_type == "application/gzip"
		assert final_submission.activity_starting_files_id == 485090
		assert final_submission.activity_language == "python_3.7"
		assert final_submission.is_final_solution is True


def test_fetch_submission_result(api, activity):
	"""
	It should request, serialize and return
	a given submission's result
	"""

	submission = Submission(
		id=1,
		activity=activity,
		submission_file_name="57_5259_2192",
		submission_file_type="application/gzip",
		submission_file_id=579801,
		is_iotested=True,
		activity_starting_files_name="2023-08-03_57_Alumno más bajo.tar.gz",
		activity_starting_files_type="application/gzip",
		activity_starting_files_id=485090,
		activity_language="activity_language",
		activity_unit_tests="activity_unit_tests",
		submission_status="FAILURE",
		is_final_solution=False,
		exit_message="exit_message",
		stderr="stderr",
		stdout="stdout",
		io_test_run_results=[],
		unit_test_run_results=[],
		submission_date="submission_date",
	)
	with patch.object(api, "auth_api_call") as mock_call:
		mock_call.return_value = {
			"id": 569096,
			"activity_id": 5259,
			"submission_file_name": "57_5259_2192",
			"submission_file_type": "application/gzip",
			"submission_file_id": 579801,
			"is_iotested": False,
			"activity_starting_files_name": "2023-08-03_57_Alumno más bajo.tar.gz",
			"activity_starting_files_type": "application/gzip",
			"activity_starting_files_id": 485090,
			"activity_language": "python_3.7",
			"activity_unit_tests": "import unittest\nimport timeout_decorator\nimport alumno\nimport random\nimport sys\nimport os\n\n\n# Disable\ndef blockPrint():\n    sys.stdout = open(os.devnull, 'w')\n\n# Restore\ndef enablePrint():\n    sys.stdout = sys.__stdout__\n\n\ndef without_print(fn):\n  try:\n    blockPrint()\n    fn()\n  finally:\n    enablePrint()\n\n\nclass AlumnoTest:\n    def __init__(self, nombre, altura):\n        self.nombre = nombre\n        self.altura = altura\n\n\ndef crear_alumnos(alturas):\n    alus = []\n    for i in range(len(alturas)):\n        alus.append(AlumnoTest(\"jaimito\" + str(i), alturas[i]))\n    return alus\n\n\nclass TestMethods(unittest.TestCase):\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_medio(self):\n        alus = crear_alumnos([1.5, 1.4, 1.3, 1.2, 1.14, 1.2, 1.23, 1.32])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 4))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 4)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_bastante_al_inicio(self):\n        alus = crear_alumnos([2, 0.8, 0.9, 1, 1.1, 1.2, 1.4, 1.41, 1.7])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 1))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 1)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_bastante_al_final(self):\n        alus = crear_alumnos([1.7, 1.41, 1.4, 1.2, 1.1, 1, 0.9, 0.8, 2])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 7))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 7)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(6)  # segundos\n    def test_volumen(self):\n        n = 18768\n        k = random.randint(5, n - 5)\n        nums = [(n - k + i if i > k else n - i) for i in range(n)]\n        alus = crear_alumnos(nums)\n        for _ in range(n):\n            without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), k))\n            without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, k)))\n            without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k + 1)))\n            without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k - 1)))\n        k = 4\n        nums = [(n - k + i if i > k else n - i) for i in range(n)]\n        alus = crear_alumnos(nums)\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), k))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, k)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k + 1)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k - 1)))\n",
			"activity_iotests": [],
			"submission_status": "FAILURE",
			"is_final_solution": False,
			"exit_message": "Completed all stages",
			"stderr": "",
			"stdout": "2024-03-25 13:23:17,682 RPL-2.0      INFO     Build Started\n2024-03-25 13:23:17,683 RPL-2.0      INFO     Building\n2024-03-25 13:23:17,683 RPL-2.0      INFO     start_BUILD\n/usr/bin/python3.10 /usr/custom_compileall.py\n2024-03-25 13:23:17,776 RPL-2.0      INFO     end_BUILD\n2024-03-25 13:23:17,776 RPL-2.0      INFO     Build Ended\n2024-03-25 13:23:17,776 RPL-2.0      INFO     Run Started\n2024-03-25 13:23:17,777 RPL-2.0      INFO     Running Unit Tests\n2024-03-25 13:23:17,777 RPL-2.0      INFO     start_RUN\n/usr/bin/python3.10 unit_test_wrapper.pyc\n2024-03-25 13:23:18,086 RPL-2.0      INFO     end_RUN\n2024-03-25 13:23:18,086 RPL-2.0      INFO     RUN OK\n2024-03-25 13:23:18,086 RPL-2.0      INFO     Run Ended\n",
			"io_test_run_results": [],
			"unit_test_run_results": [
				{
					"id": 1403361,
					"test_name": "test_bastante_al_final",
					"passed": False,
					"error_messages": 'Traceback (most recent call last):\n  File "/usr/local/lib/python3.10/dist-packages/timeout_decorator/timeout_decorator.py", line 82, in new_function\n    return function(*args, **kwargs)\n  File "./unit_test.py", line 39, in test_bastante_al_final\nAssertionError: 0 != 7\n',
				},
				{
					"id": 1403362,
					"test_name": "test_bastante_al_inicio",
					"passed": False,
					"error_messages": 'Traceback (most recent call last):\n  File "/usr/local/lib/python3.10/dist-packages/timeout_decorator/timeout_decorator.py", line 82, in new_function\n    return function(*args, **kwargs)\n  File "./unit_test.py", line 32, in test_bastante_al_inicio\nAssertionError: 8 != 1\n',
				},
			],
			"submission_date": "2024-03-25T13:23:18Z",
		}

		result = api.fetch_submission_result(submission)

		assert isinstance(result, SubmissionResult)
		assert result.id == 569096
		assert result.activity == activity
		assert result.submission == submission
		assert result.submission_file_name == "57_5259_2192"
		assert result.submission_file_type == "application/gzip"
		assert result.submission_file_id == 579801
		assert result.is_iotested is False
		assert result.activity_starting_files_name == "2023-08-03_57_Alumno más bajo.tar.gz"
		assert result.activity_starting_files_type == "application/gzip"
		assert result.activity_starting_files_id == 485090
		assert result.activity_language == "python_3.7"
		assert (
			result.activity_unit_tests
			== "import unittest\nimport timeout_decorator\nimport alumno\nimport random\nimport sys\nimport os\n\n\n# Disable\ndef blockPrint():\n    sys.stdout = open(os.devnull, 'w')\n\n# Restore\ndef enablePrint():\n    sys.stdout = sys.__stdout__\n\n\ndef without_print(fn):\n  try:\n    blockPrint()\n    fn()\n  finally:\n    enablePrint()\n\n\nclass AlumnoTest:\n    def __init__(self, nombre, altura):\n        self.nombre = nombre\n        self.altura = altura\n\n\ndef crear_alumnos(alturas):\n    alus = []\n    for i in range(len(alturas)):\n        alus.append(AlumnoTest(\"jaimito\" + str(i), alturas[i]))\n    return alus\n\n\nclass TestMethods(unittest.TestCase):\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_medio(self):\n        alus = crear_alumnos([1.5, 1.4, 1.3, 1.2, 1.14, 1.2, 1.23, 1.32])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 4))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 4)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_bastante_al_inicio(self):\n        alus = crear_alumnos([2, 0.8, 0.9, 1, 1.1, 1.2, 1.4, 1.41, 1.7])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 1))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 1)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(1)  # segundos\n    def test_bastante_al_final(self):\n        alus = crear_alumnos([1.7, 1.41, 1.4, 1.2, 1.1, 1, 0.9, 0.8, 2])\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), 7))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, 7)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, 2)))\n\n    @timeout_decorator.timeout(6)  # segundos\n    def test_volumen(self):\n        n = 18768\n        k = random.randint(5, n - 5)\n        nums = [(n - k + i if i > k else n - i) for i in range(n)]\n        alus = crear_alumnos(nums)\n        for _ in range(n):\n            without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), k))\n            without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, k)))\n            without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k + 1)))\n            without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k - 1)))\n        k = 4\n        nums = [(n - k + i if i > k else n - i) for i in range(n)]\n        alus = crear_alumnos(nums)\n        without_print(lambda: self.assertEqual(alumno.indice_mas_bajo(alus), k))\n        without_print(lambda: self.assertTrue(alumno.validar_mas_bajo(alus, k)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k + 1)))\n        without_print(lambda: self.assertFalse(alumno.validar_mas_bajo(alus, k - 1)))\n"
		)
		assert result.submission_status == "FAILURE"
		assert result.is_final_solution is False
		assert result.exit_message == "Completed all stages"
		assert result.stderr == ""
		assert (
			result.stdout
			== "2024-03-25 13:23:17,682 RPL-2.0      INFO     Build Started\n2024-03-25 13:23:17,683 RPL-2.0      INFO     Building\n2024-03-25 13:23:17,683 RPL-2.0      INFO     start_BUILD\n/usr/bin/python3.10 /usr/custom_compileall.py\n2024-03-25 13:23:17,776 RPL-2.0      INFO     end_BUILD\n2024-03-25 13:23:17,776 RPL-2.0      INFO     Build Ended\n2024-03-25 13:23:17,776 RPL-2.0      INFO     Run Started\n2024-03-25 13:23:17,777 RPL-2.0      INFO     Running Unit Tests\n2024-03-25 13:23:17,777 RPL-2.0      INFO     start_RUN\n/usr/bin/python3.10 unit_test_wrapper.pyc\n2024-03-25 13:23:18,086 RPL-2.0      INFO     end_RUN\n2024-03-25 13:23:18,086 RPL-2.0      INFO     RUN OK\n2024-03-25 13:23:18,086 RPL-2.0      INFO     Run Ended\n"
		)
		assert result.io_test_run_results == []
		assert len(result.unit_test_run_results) == 2
		assert result.unit_test_run_results[0].id == 1403361
		assert result.unit_test_run_results[0].test_name == "test_bastante_al_final"
		assert result.unit_test_run_results[0].passed is False
		assert (
			result.unit_test_run_results[0].error_messages
			== 'Traceback (most recent call last):\n  File "/usr/local/lib/python3.10/dist-packages/timeout_decorator/timeout_decorator.py", line 82, in new_function\n    return function(*args, **kwargs)\n  File "./unit_test.py", line 39, in test_bastante_al_final\nAssertionError: 0 != 7\n'
		)
		assert result.unit_test_run_results[1].id == 1403362
		assert result.unit_test_run_results[1].test_name == "test_bastante_al_inicio"
		assert result.unit_test_run_results[1].passed is False
		assert (
			result.unit_test_run_results[1].error_messages
			== 'Traceback (most recent call last):\n  File "/usr/local/lib/python3.10/dist-packages/timeout_decorator/timeout_decorator.py", line 82, in new_function\n    return function(*args, **kwargs)\n  File "./unit_test.py", line 32, in test_bastante_al_inicio\nAssertionError: 8 != 1\n'
		)
		assert result.submission_date == "2024-03-25T13:23:18Z"


# def test_submit(api, activity):
# """
# It should submit a new file and return
# the generated submission for a given activity
# """

# mock_file_content = b"print('Hello, World!')"

# with patch('builtins.open', mock_open(read_data=mock_file_content)) as mock_file, \
#         patch('mimetypes.guess_type', return_value=('text/plain', None)), \
#         patch('requests_toolbelt.multipart.encoder.MultipartEncoder') as mock_multipart, \
#         patch.object(api, 'auth_api_call') as mock_call:

#     mock_multipart.return_value = Mock(
#         content_type='multipart/form-data; boundary=something',
#         to_string=lambda: b'mocked multipart data'
#     )

#     mock_call.return_value = {
#         'id': 4,
#         'activity_id': 1,
#         'submission_file_name': 'submitted.py'
#     }

#     result = api.submit(activity, 'test_file.py', 'Test submission')

#     # Assert that MultipartEncoder was called with correct arguments
#     mock_multipart.assert_called_once()
#     fields_arg = mock_multipart.call_args[1]['fields']
#     assert 'file' in fields_arg
#     assert fields_arg['file'][0] == 'test_file.py'
#     assert fields_arg['file'][2] == 'text/plain'
#     assert fields_arg['description'] == 'Test submission'

#     # Assert that auth_api_call was called correctly
#     mock_call.assert_called_once()
#     call_args = mock_call.call_args
#     assert call_args[0][0] == 'post'
#     assert call_args[0][1].endswith(
#         f'/api/courses/{activity.course.id}/activities/{activity.id}/submissions')
#     assert call_args[1]['data'].to_string() == b'mocked multipart data'
#     assert call_args[1]['headers']['Content-Type'] == 'multipart/form-data; boundary=something'

#     assert result['id'] == 4
#     assert result['submission_file_name'] == 'submitted.py'


def test_renew_token_success(api):
	"""
	It should newew a token using the
	stored credentials
	"""

	api.credential_manager.get_stored_credentials.return_value = (
		"test@example.com",
		"password",
	)

	with patch.object(api, "login") as mock_login:
		mock_login.return_value = {"access_token": "new_token", "token_type": "Bearer"}

		api.renew_token()

		assert api.headers["Authorization"] == "Bearer new_token"
		api.credential_manager.store_token.assert_called_once_with("new_token")


def test_renew_token_missing_credentials(api):
	"""
	When the credentials are missing
	it should raise an error
	"""

	api.credential_manager.get_stored_credentials.return_value = (None, None)

	with pytest.raises(MissingCredentialsError):
		api.renew_token()


def test_auth_api_call_with_token_renewal(api):
	"""
	When the token is expired, it should renew it
	and reattempt the api call
	"""

	with (
		patch.object(api, "make_request") as mock_request,
		patch.object(api, "renew_token") as mock_renew_token,
		patch.object(api.credential_manager, "get_stored_token") as mock_get_stored_token,
	):
		# The first call to make_request raises an HTTPError for 401
		# The second call to make_request succeeds
		mock_request.side_effect = [
			requests.HTTPError(response=Mock(status_code=401)),
			Mock(json=Mock(return_value={"data": "success"})),
		]

		mock_get_stored_token.return_value = "expired_token"

		result = api.auth_api_call("get", "http://test.com")

		assert mock_request.call_count == 2
		call_args_list = mock_request.call_args_list
		call_args = call_args_list[0]
		assert call_args[0][0] == "get"
		assert call_args[0][1] == "http://test.com"
		assert call_args[1]["headers"]["Authorization"] == "Bearer expired_token"

		call_args = call_args_list[1]
		assert call_args[0][0] == "get"
		assert call_args[0][1] == "http://test.com"
		assert call_args[1]["headers"]["Authorization"] == "Bearer expired_token"

		mock_renew_token.assert_called_once()

		assert result == {"data": "success"}


def test_set_final_submission(api, activity):
	submission = Submission(
		id=695375,
		activity=activity,
		submission_file_name="57_5845_2192",
		submission_file_type="application/gzip",
		submission_file_id=706421,
		is_iotested=False,
		activity_starting_files_name="2024-02-16_57_12 - Kilómetros de Mafia.tar.gz",
		activity_starting_files_type="application/gzip",
		activity_starting_files_id=562839,
		activity_language="python_3.7",
		activity_unit_tests="",
		is_final_solution=False,
	)

	with patch.object(api, "auth_api_call") as mock_call:
		mock_call.return_value = {
			"id": 695375,
			"submission_file_name": "57_5845_2192",
			"submission_file_type": "application/gzip",
			"submission_file_id": 706421,
			"activity_starting_files_name": "2024-02-16_57_12 - Kilómetros de Mafia.tar.gz",
			"activity_starting_files_type": "application/gzip",
			"activity_starting_files_id": 562839,
			"activity_language": "python_3.7",
			"is_iotested": False,
			"activity_unit_tests_content": "",
			"compilation_flags": "",
			"activity_iotests": [],
		}

		final_submission = api.set_final_submission(submission)

		assert isinstance(final_submission, Submission)
		# assert final_submission.is_final_solution is True
		assert final_submission.id == 695375
		assert final_submission.activity == activity
		assert final_submission.submission_file_name == "57_5845_2192"
		assert final_submission.submission_file_type == "application/gzip"
		assert final_submission.submission_file_id == 706421
		assert final_submission.is_iotested is False
		assert final_submission.activity_starting_files_name == "2024-02-16_57_12 - Kilómetros de Mafia.tar.gz"
		assert final_submission.activity_starting_files_type == "application/gzip"
		assert final_submission.activity_starting_files_id == 562839
		assert final_submission.activity_language == "python_3.7"
