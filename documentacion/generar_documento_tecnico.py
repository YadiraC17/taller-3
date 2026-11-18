from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


DIRECTORY = Path(__file__).resolve().parent
OUTPUT = DIRECTORY / "DOCUMENTO_TECNICO.pdf"
TEMP_OUTPUT = DIRECTORY / "DOCUMENTO_TECNICO.tmp.pdf"
MAX_CONTENT_PAGES = 5

GREEN = colors.HexColor("#143D35")
TEAL = colors.HexColor("#367F70")
INK = colors.HexColor("#1B2C28")
MUTED = colors.HexColor("#68766F")
LIGHT = colors.HexColor("#EEF4EF")
GRID = colors.HexColor("#DCE5DE")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="CoverTitle",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=32,
    leading=38,
    textColor=GREEN,
    alignment=1,
    spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="CoverSubtitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=14,
    leading=19,
    textColor=TEAL,
    alignment=1,
))
styles.add(ParagraphStyle(
    name="SectionTitle",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=15,
    leading=19,
    textColor=GREEN,
    spaceBefore=1,
    spaceAfter=5,
    keepWithNext=True,
))
styles.add(ParagraphStyle(
    name="SubsectionTitle",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=13,
    textColor=TEAL,
    spaceBefore=5,
    spaceAfter=3,
    keepWithNext=True,
))
styles.add(ParagraphStyle(
    name="BodyES",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=8.7,
    leading=12,
    textColor=INK,
    spaceAfter=5,
))
styles.add(ParagraphStyle(
    name="SmallES",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=7.2,
    leading=9,
    textColor=INK,
))
styles.add(ParagraphStyle(
    name="TableHeadES",
    parent=styles["BodyText"],
    fontName="Helvetica-Bold",
    fontSize=7.4,
    leading=9,
    textColor=colors.white,
))
styles.add(ParagraphStyle(
    name="CodeES",
    parent=styles["Code"],
    fontName="Courier",
    fontSize=7.4,
    leading=9,
    textColor=INK,
    backColor=LIGHT,
    borderPadding=6,
))
styles.add(ParagraphStyle(
    name="CalloutES",
    parent=styles["BodyText"],
    fontName="Helvetica-Bold",
    fontSize=8.4,
    leading=11,
    textColor=GREEN,
))


def paragraph(text, style="BodyES"):
    return Paragraph(escape(text), styles[style])


def markup(text, style="BodyES"):
    return Paragraph(text, styles[style])


def make_table(rows, widths, font_size=7.2):
    cell_style = ParagraphStyle(
        name=f"TableCell{font_size}",
        parent=styles["SmallES"],
        fontSize=font_size,
        leading=font_size + 1.8,
    )
    prepared = []
    for row_index, row in enumerate(rows):
        style = "TableHeadES" if row_index == 0 else cell_style
        prepared.append([Paragraph(escape(str(cell)), styles[style] if isinstance(style, str) else style) for cell in row])
    table = Table(prepared, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


class LimitedPagesCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.saved_page_states = []
        self.page_count = 0

    def showPage(self):
        self.saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.saved_page_states)
        content_pages = max(0, page_count - 1)
        if content_pages > MAX_CONTENT_PAGES:
            raise RuntimeError(
                f"El documento tiene {content_pages} páginas de contenido; "
                f"el máximo es {MAX_CONTENT_PAGES}."
            )

        for state in self.saved_page_states:
            self.__dict__.update(state)
            Canvas.showPage(self)
        self.page_count = page_count
        Canvas.save(self)


def draw_cover(canvas, document):
    canvas.saveState()
    canvas.setFillColor(GREEN)
    canvas.rect(0, A4[1] - 14 * mm, A4[0], 14 * mm, stroke=0, fill=1)
    canvas.restoreState()


def draw_content_page(canvas, document):
    if document.page <= 1:
        return
    canvas.saveState()
    canvas.setStrokeColor(GRID)
    canvas.setLineWidth(0.6)
    canvas.line(17 * mm, 15 * mm, A4[0] - 17 * mm, 15 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(17 * mm, 10 * mm, "FINTRACK | Documento técnico")
    canvas.drawRightString(A4[0] - 17 * mm, 10 * mm, f"Página {document.page - 1}")
    canvas.restoreState()


def section_heading(number, title, summary):
    return [
        paragraph(f"{number}. {title}", "SectionTitle"),
        paragraph(summary, "BodyES"),
    ]


def build_story():
    story = [
        Spacer(1, 38 * mm),
        paragraph("FINTRACK", "CoverTitle"),
        paragraph("Documento técnico", "CoverSubtitle"),
        Spacer(1, 8 * mm),
        paragraph("Aplicación Android y API REST para finanzas personales", "CoverSubtitle"),
        Spacer(1, 15 * mm),
        make_table([
            ["Elemento", "Descripción"],
            ["Cliente", "Android nativo, Java"],
            ["Backend", "Python 3.11, Flask, Waitress y SQLAlchemy"],
            ["Producción", "Render + PostgreSQL administrado por Neon"],
            ["Pruebas locales", "SQLite, pytest y Android Gradle"],
            ["API", "https://fintrack-api-392k.onrender.com/api"],
            ["Repositorio", "github.com/YadiraC17/taller-3"],
            ["Fecha", "13/11/2026"],
        ], [42 * mm, 128 * mm], font_size=8),
        paragraph("Integrantes", "SubsectionTitle"),
        markup(
            "CANTORIN LOPE, YADIRA JHENYFER<br/>"
            "DIAZ SILVA JOSE LUIS<br/>"
            "MORALES SANTIAGO ROSSE EMILY",
            "SmallES",
        ),
        Spacer(1, 14 * mm),
        markup("Cliente Android desacoplado de la persistencia: los datos, reglas financieras y reportes se procesan en el servidor.", "CalloutES"),
        PageBreak(),
    ]

    story += section_heading(
        1,
        "Problema y arquitectura",
        "FINTRACK centraliza ingresos, gastos y presupuestos para evitar depender de cálculos y almacenamiento locales en cada teléfono.",
    )
    story.extend([
        paragraph(
            "La aplicación permite que cada usuario registre y consulte sus finanzas desde Android. "
            "La API realiza autenticación, validación, persistencia y reportes; el cliente envía solicitudes "
            "y presenta las respuestas. Así se reducen las tareas y el estado financiero duplicado en el dispositivo."
        ),
        paragraph("Flujo principal", "SubsectionTitle"),
        make_table([
            ["Cliente móvil", "Transporte", "API / reglas", "Persistencia"],
            ["Android Java\nPantallas y JWT", "HTTPS en producción\nJSON + Bearer JWT", "Flask + Waitress\nServicios y SQLAlchemy", "Neon PostgreSQL\nSQLite local"],
        ], [42 * mm, 42 * mm, 43 * mm, 43 * mm], font_size=7.6),
        paragraph("Responsabilidades por capa", "SubsectionTitle"),
        make_table([
            ["Capa", "Responsabilidad"],
            ["Android", "Registro, login y presentación de categorías, movimientos, presupuestos y reportes."],
            ["Rutas Flask", "HTTP, autorización JWT, lectura de parámetros y respuestas JSON."],
            ["Servicios", "Validaciones, reglas de propiedad y cálculos financieros."],
            ["Repositorios / modelos", "Consultas SQLAlchemy y representación de entidades."],
            ["Base de datos", "PostgreSQL persistente en producción; SQLite para desarrollo y pruebas."],
        ], [40 * mm, 130 * mm], font_size=7.5),
        markup(
            "<b>Despliegue:</b> la API pública usa HTTPS. La URL gratuita de Render puede tardar en responder "
            "al reactivarse tras inactividad; Neon almacena la base fuera del sistema de archivos efímero de Render.",
            "CalloutES",
        ),
        PageBreak(),
    ])

    story += section_heading(
        2,
        "Modelo de datos",
        "Las migraciones Alembic definen el mismo esquema para SQLite local y PostgreSQL en producción.",
    )
    story.extend([
        paragraph(
            "Un usuario posee sus categorías, transacciones y presupuestos. Cada transacción y presupuesto "
            "referencia una categoría del mismo usuario. Los tokens revocados se almacenan por su identificador JWT."
        ),
        make_table([
            ["Entidad", "Campos principales", "Relaciones y restricciones"],
            ["usuarios", "id_usuario (PK), nombre, correo, password_hash, fecha_registro, activo", "Correo único e indexado. La contraseña se guarda como hash."],
            ["categorias", "id_categoria (PK), id_usuario (FK), nombre, tipo, descripcion, fecha_creacion", "Pertenece a usuario. Nombre + tipo únicos por usuario."],
            ["transacciones", "id_transaccion (PK), id_usuario (FK), id_categoria (FK), tipo, monto, moneda, fecha", "Monto > 0. Índices para usuario, categoría y fecha."],
            ["presupuestos", "id_presupuesto (PK), id_usuario (FK), id_categoria (FK), monto_limite, moneda, mes, anio", "Monto > 0. Único por usuario, categoría, moneda y periodo."],
            ["revoked_tokens", "jti (PK), expires_at, revoked_at", "Índice de expiración para depurar tokens vencidos al cerrar sesión."],
        ], [29 * mm, 76 * mm, 65 * mm], font_size=7.1),
        paragraph("Relaciones", "SubsectionTitle"),
        make_table([
            ["Relación", "Cardinalidad"],
            ["usuarios -> categorias", "1 a muchos"],
            ["usuarios -> transacciones", "1 a muchos"],
            ["usuarios -> presupuestos", "1 a muchos"],
            ["categorias -> transacciones / presupuestos", "1 a muchos"],
        ], [80 * mm, 90 * mm], font_size=7.6),
        markup(
            "Migraciones incluidas: <b>44791ec6011f</b> (esquema inicial) y <b>8dbe0c31a923</b> "
            "(revocación JWT). El esquema detallado está en <b>backend/SCHEMA.md</b>.",
            "CalloutES",
        ),
        PageBreak(),
    ])

    story += section_heading(
        3,
        "API: autenticación, categorías y movimientos",
        "Las rutas privadas requieren Authorization: Bearer &lt;token&gt;. Todas las rutas de recursos están bajo /api.",
    )
    story.extend([
        make_table([
            ["Método", "Ruta", "Acceso", "Uso / éxito"],
            ["GET", "/", "Público", "Estado del servicio (200)."],
            ["POST", "/auth/register", "Público", "Crear cuenta (201)."],
            ["POST", "/auth/login", "Público", "Obtener JWT (200)."],
            ["GET", "/auth/me", "JWT", "Perfil actual (200)."],
            ["POST", "/auth/logout", "JWT", "Revocar JWT (200)."],
            ["POST", "/categorias", "JWT", "Crear categoría (201)."],
            ["GET", "/categorias", "JWT", "Listar; filtro tipo (200)."],
            ["GET", "/categorias/{id_categoria}", "JWT", "Consultar (200)."],
            ["PUT", "/categorias/{id_categoria}", "JWT", "Actualizar (200)."],
            ["DELETE", "/categorias/{id_categoria}", "JWT", "Eliminar (204)."],
            ["POST", "/transacciones", "JWT", "Registrar movimiento (201)."],
            ["GET", "/transacciones", "JWT", "Listar y filtrar (200)."],
            ["GET", "/transacciones/{id_transaccion}", "JWT", "Consultar (200)."],
            ["PUT", "/transacciones/{id_transaccion}", "JWT", "Actualizar (200)."],
            ["DELETE", "/transacciones/{id_transaccion}", "JWT", "Eliminar (204)."],
        ], [17 * mm, 71 * mm, 18 * mm, 70 * mm], font_size=7),
        paragraph(
            "Registro recibe nombre, correo y password. Transacciones reciben id_categoria, tipo, monto, "
            "moneda, fecha y descripcion opcional. En listados de movimientos: page=1, per_page=50 "
            "(máximo 100), tipo, moneda, categoria, fecha_inicio y fecha_fin.",
            "SmallES",
        ),
        markup(
            "Ejemplo de movimiento: <font name=\"Courier\">{&quot;id_categoria&quot;:1,&quot;tipo&quot;:&quot;GASTO&quot;,"
            "&quot;monto&quot;:42.50,&quot;moneda&quot;:&quot;PEN&quot;,&quot;fecha&quot;:&quot;2026-11-17&quot;}</font>",
            "CalloutES",
        ),
        PageBreak(),
    ])

    story += section_heading(
        4,
        "API: presupuestos y reportes",
        "Los reportes agregan PEN y USD por separado y usan el mes/año actual cuando no se especifica un periodo.",
    )
    story.extend([
        make_table([
            ["Método", "Ruta", "Uso / parámetros / éxito"],
            ["POST", "/presupuestos", "Crear con id_categoria, monto_limite, moneda, mes, anio (201)."],
            ["GET", "/presupuestos", "Listar; mes y anio opcionales (200)."],
            ["GET", "/presupuestos/seguimiento", "Gasto, porcentaje, saldo y estado del límite (200)."],
            ["GET", "/presupuestos/{id_presupuesto}", "Consultar presupuesto (200)."],
            ["PUT", "/presupuestos/{id_presupuesto}", "Actualizar campos enviados (200)."],
            ["DELETE", "/presupuestos/{id_presupuesto}", "Eliminar (204)."],
            ["GET", "/reportes/resumen", "Balance por moneda; mes y anio opcionales (200)."],
            ["GET", "/reportes/gastos-categoria", "Gastos por categoría; periodo opcional (200)."],
            ["GET", "/reportes/evolucion", "Serie mensual por moneda; anio opcional (200)."],
        ], [17 * mm, 65 * mm, 94 * mm], font_size=7.1),
        paragraph("Ejemplo de presupuesto", "SubsectionTitle"),
        markup(
            "<font name=\"Courier\">{&quot;id_categoria&quot;:1,&quot;monto_limite&quot;:500,"
            "&quot;moneda&quot;:&quot;PEN&quot;,&quot;mes&quot;:11,&quot;anio&quot;:2026}</font>",
            "CodeES",
        ),
        paragraph("Seguimiento clasifica el consumo como DENTRO_DEL_PRESUPUESTO (&lt;80%), CERCA_DEL_LIMITE (80% a menos de 100%) o EXCEDIDO (100% o más).", "BodyES"),
        make_table([
            ["Respuesta", "Significado"],
            ["200", "Consulta / actualización completada."],
            ["201", "Recurso creado."],
            ["204", "Eliminación completada; sin cuerpo."],
            ["400", "JSON, parámetro o dato inválido."],
            ["401", "Credenciales incorrectas o JWT ausente, inválido, vencido o revocado."],
            ["404", "Recurso no encontrado o no pertenece al usuario."],
            ["409", "Duplicado o conflicto con relaciones existentes."],
            ["500", "Error interno no esperado."],
        ], [25 * mm, 151 * mm], font_size=7.2),
        PageBreak(),
    ])

    story += section_heading(
        5,
        "Reglas, seguridad y pruebas",
        "La API aplica las reglas antes de guardar o calcular los datos.",
    )
    story.extend([
        make_table([
            ["Regla", "Comportamiento"],
            ["Aislamiento", "El usuario se obtiene del JWT; las consultas y mutaciones se filtran por esa identidad."],
            ["Autenticación", "JWT de 12 horas; cierre de sesión registra el identificador revocado."],
            ["Contraseñas", "Se guarda un hash; el campo nunca forma parte de la respuesta API."],
            ["Movimientos", "Monto positivo, máximo dos decimales; categoría del usuario y tipo coincidente."],
            ["Presupuestos", "Solo categorías GASTO; monto positivo; únicos por categoría, moneda y periodo."],
            ["Monedas", "PEN y USD se agregan por separado, sin conversiones."],
            ["Red", "HTTPS requerido en release; HTTP se permite solo en debug local."],
        ], [35 * mm, 141 * mm], font_size=7.2),
        paragraph("Pruebas y compilación", "SubsectionTitle"),
        paragraph(
            "La suite backend valida registro/login, autorización, revocación, transacciones, paginación, "
            "presupuestos, aislamiento entre usuarios y reportes. Resultado verificado: "
            "<b>24 pruebas aprobadas</b> con <font name=\"Courier\">python -m pytest -q</font> desde backend."
        ),
        paragraph(
            "Android compila con <font name=\"Courier\">gradlew.bat assembleDebug assembleRelease</font>. "
            "La APK de pruebas se firma con la clave debug; la publicación en Google Play requiere una "
            "clave release administrada por el propietario."
        ),
        paragraph("Despliegue", "SubsectionTitle"),
        paragraph(
            "Render ejecuta Flask con Waitress y aplica migraciones al iniciar. Neon conserva PostgreSQL "
            "fuera del disco efímero de Render. La configuración está en render.yaml; las variables "
            "sensibles se definen en el panel de Render y no se guardan en Git."
        ),
        markup(
            "Documentación ampliada: <b>README.md</b>, <b>documentacion/API.md</b> y "
            "<b>backend/SCHEMA.md</b>.",
            "CalloutES",
        ),
    ])
    return story


def generate():
    TEMP_OUTPUT.unlink(missing_ok=True)
    page_counter = {}

    def canvas_factory(*args, **kwargs):
        generated_canvas = LimitedPagesCanvas(*args, **kwargs)
        page_counter["canvas"] = generated_canvas
        return generated_canvas

    document = SimpleDocTemplate(
        str(TEMP_OUTPUT),
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=16 * mm,
        bottomMargin=20 * mm,
        title="FINTRACK - Documento técnico",
        author="FINTRACK",
        subject="Arquitectura, modelo de datos, API, reglas y pruebas",
        pageCompression=1,
    )
    try:
        document.build(
            build_story(),
            onFirstPage=draw_cover,
            onLaterPages=draw_content_page,
            canvasmaker=canvas_factory,
        )
        content_pages = page_counter["canvas"].page_count - 1
        TEMP_OUTPUT.replace(OUTPUT)
    except Exception:
        TEMP_OUTPUT.unlink(missing_ok=True)
        raise

    print(f"Generado: {OUTPUT}")
    print(f"Paginas: 1 portada + {content_pages} de contenido (maximo {MAX_CONTENT_PAGES})")


if __name__ == "__main__":
    generate()
