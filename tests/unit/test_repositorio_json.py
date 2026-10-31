import json

import pytest
from soporte import FECHA, datos

from solicitudes.errores import ErrorDeDominio
from solicitudes.modelos import RegistroAcademico
from solicitudes.repositorio import RepositorioJSON


@pytest.fixture
def ruta(tmp_path):
    return tmp_path / "datos.json"


def registro_de_ejemplo():
    registro = RegistroAcademico()
    registro.obtener_o_crear_estudiante(datos())
    registro.agregar_responsable("Marta Ruiz", "Secretaría Académica")
    registro.agregar_solicitud(datos(), FECHA).responsable_id = 1
    return registro


def test_archivo_inexistente_devuelve_registro_vacio(ruta):
    assert RepositorioJSON(ruta).cargar() == RegistroAcademico()


def test_guardar_y_cargar_conserva_todo_el_registro(ruta):
    repositorio = RepositorioJSON(ruta)
    original = registro_de_ejemplo()
    repositorio.guardar(original)
    assert repositorio.cargar() == original


def test_formato_del_archivo_es_el_mismo_de_la_version_inicial(ruta):
    RepositorioJSON(ruta).guardar(registro_de_ejemplo())
    contenido = json.loads(ruta.read_text(encoding="utf-8"))
    assert list(contenido) == ["ultimo_id", "ultimo_resp", "estudiantes", "responsables", "solicitudes"]
    assert list(contenido["solicitudes"][0]) == [
        "id", "legajo", "tipo", "prioridad", "estado", "descripcion", "fecha", "vence", "responsable_id"]
    assert contenido["solicitudes"][0]["vence"] == "2026-11-07"
    assert "Secretaría Académica" in ruta.read_text(encoding="utf-8")  # sin escapes \u00xx


def test_guardar_no_deja_archivos_temporales(ruta, tmp_path):
    RepositorioJSON(ruta).guardar(registro_de_ejemplo())
    assert [p.name for p in tmp_path.iterdir()] == ["datos.json"]


def test_guardar_reemplaza_el_contenido_anterior(ruta):
    repositorio = RepositorioJSON(ruta)
    repositorio.guardar(registro_de_ejemplo())
    repositorio.guardar(RegistroAcademico())
    assert repositorio.cargar() == RegistroAcademico()


@pytest.mark.parametrize("contenido", ['{"ultimo_id": 1, ', "", "no es json", "{}", '{"ultimo_id": 1}'])
def test_archivo_corrupto_o_incompleto_se_informa_y_no_se_modifica(ruta, contenido):
    ruta.write_text(contenido, encoding="utf-8")
    with pytest.raises(ErrorDeDominio, match="el archivo de datos está corrupto"):
        RepositorioJSON(ruta).cargar()
    assert ruta.read_text(encoding="utf-8") == contenido


def test_valor_de_enumeracion_desconocido_se_considera_corrupcion(ruta):
    repositorio = RepositorioJSON(ruta)
    repositorio.guardar(registro_de_ejemplo())
    contenido = ruta.read_text(encoding="utf-8").replace('"CERTIFICADO"', '"INVENTADO"')
    ruta.write_text(contenido, encoding="utf-8")
    with pytest.raises(ErrorDeDominio, match="corrupto"):
        repositorio.cargar()
