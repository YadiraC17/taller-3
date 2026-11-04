from pathlib import Path

import reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


OUTPUT = Path(__file__).with_name("DOCUMENTACION_TECNICA.pdf")
FONT_DIR = Path(reportlab.__file__).parent / "fonts"
pdfmetrics.registerFont(TTFont("Vera", str(FONT_DIR / "Vera.ttf")))
pdfmetrics.registerFont(TTFont("Vera-Bold", str(FONT_DIR / "VeraBd.ttf")))

GREEN = colors.HexColor("#143D35")
TEAL = colors.HexColor("#367F70")
LIGHT = colors.HexColor("#EEF4EF")
INK = colors.HexColor("#1B2C28")
MUTED = colors.HexColor("#68766F")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", fontName="Vera-Bold", fontSize=34, leading=40, textColor=GREEN, alignment=1, spaceAfter=12))
styles.add(ParagraphStyle(name="CoverSubtitle", fontName="Vera", fontSize=15, leading=22, textColor=TEAL, alignment=1))
styles.add(ParagraphStyle(name="SectionTitle", fontName="Vera-Bold", fontSize=14, leading=18, textColor=GREEN, spaceBefore=5, spaceAfter=7, keepWithNext=True))
styles.add(ParagraphStyle(name="BodyTextES", fontName="Vera", fontSize=9, leading=13, textColor=INK, spaceAfter=5))
styles.add(ParagraphStyle(name="SmallTextES", fontName="Vera", fontSize=7.5, leading=10, textColor=INK))
styles.add(ParagraphStyle(name="TableHeadES", fontName="Vera-Bold", fontSize=8, leading=10, textColor=colors.white))


def paragraph(text, style="BodyTextES"):
    return Paragraph(text, styles[style])


def table(rows, widths):
    prepared = [[paragraph(str(cell), "TableHeadES" if row_index == 0 else "SmallTextES") for cell in row]
                for row_index, row in enumerate(rows)]
    result = Table(prepared, colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#DCE5DE")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return result


def draw_footer(canvas, document):
    if document.page > 1:
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#DCE5DE"))
        canvas.line(18 * mm, 15 * mm, A4[0] - 18 * mm, 15 * mm)
        canvas.setFont("Vera", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(18 * mm, 10 * mm, "FINTRACK | Documento técnico")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Página {document.page - 1}")
        canvas.restoreState()


story = [
    Spacer(1, 52 * mm),
    paragraph("FINTRACK", "CoverTitle"),
    paragraph("Sistema de Control de Gastos Personales", "CoverSubtitle"),
    Spacer(1, 17 * mm),
    table([
        ["Documento", "Descripción técnica del sistema"],
        ["Versión", "1.0"],
        ["Tecnologías", "Python 3.11, Flask, SQLite, SQLAlchemy y JavaScript"],
        ["Fecha", "Noviembre de 2026"],
    ], [43 * mm, 105 * mm]),
    Spacer(1, 42 * mm),
    paragraph("Aplicación web con API REST propia y datos financieros aislados por usuario.", "CoverSubtitle"),
    PageBreak(),
    paragraph("1. Problema y objetivo", "SectionTitle"),
    paragraph("FINTRACK centraliza ingresos, gastos y presupuestos personales para facilitar el seguimiento de hábitos de consumo. Está dirigido a personas que necesitan organizar sus movimientos en soles peruanos (PEN) y dólares estadounidenses (USD), sin conversiones ni sumas entre monedas."),
    paragraph("El objetivo es ofrecer operaciones persistentes, reportes calculados en el servidor y controles de acceso para que cada cuenta consulte exclusivamente sus propios datos."),
    paragraph("2. Arquitectura", "SectionTitle"),
    paragraph("La solución separa presentación, rutas/controladores, servicios, repositorios y modelos. El frontend HTML/CSS/JavaScript usa Fetch API; Flask valida las solicitudes y delega reglas a servicios; los repositorios consultan SQLAlchemy y SQLite. Flask-Migrate versiona el esquema."),
    table([
        ["Capa", "Responsabilidad"],
        ["Frontend", "Formularios, navegación, filtros e indicadores; consume la API por HTTP."],
        ["Rutas", "Autenticación JWT, parámetros, códigos HTTP y respuestas JSON."],
        ["Servicios", "Reglas de propiedad, validaciones y cálculos financieros."],
        ["Repositorios", "Consultas de usuarios, categorías, transacciones, presupuestos y reportes."],
        ["Persistencia", "SQLite local con claves foráneas habilitadas y migraciones."],
    ], [32 * mm, 116 * mm]),
    Spacer(1, 4 * mm),
    paragraph("3. Modelo de datos", "SectionTitle"),
    table([
        ["Entidad", "Relaciones y restricciones"],
        ["Usuario", "Posee categorías, transacciones y presupuestos; correo único y contraseña con hash."],
        ["Categoría", "Pertenece a un usuario; tipo INGRESO/GASTO; nombre y tipo únicos por usuario."],
        ["Transacción", "Pertenece a usuario y categoría; monto NUMERIC(12,2), fecha y moneda PEN/USD."],
        ["Presupuesto", "Pertenece a usuario y categoría de gasto; único por categoría, moneda, mes y año."],
    ], [31 * mm, 117 * mm]),
    PageBreak(),
    paragraph("4. API desarrollada", "SectionTitle"),
    paragraph("Las rutas privadas requieren el encabezado Authorization: Bearer JWT. La identidad proviene del token, nunca de un id_usuario enviado por el cliente."),
    table([
        ["Módulo", "Endpoints principales"],
        ["Autenticación", "POST /auth/register, POST /auth/login, GET /auth/me, GET /auth/logout."],
        ["Categorías", "CRUD en /categorias; filtro opcional por tipo."],
        ["Transacciones", "CRUD en /transacciones; filtros por tipo, categoría, moneda y fechas."],
        ["Presupuestos", "CRUD en /presupuestos; GET /presupuestos/seguimiento calcula consumo real."],
        ["Reportes", "GET /reportes/resumen, /gastos-categoria y /evolucion."],
    ], [34 * mm, 114 * mm]),
    Spacer(1, 4 * mm),
    paragraph("5. Reglas de negocio y seguridad", "SectionTitle"),
    paragraph("Los montos deben ser positivos y tener hasta dos decimales. La categoría debe ser propia y coincidir con el tipo de la transacción; solo las categorías de gasto aceptan presupuestos. No se elimina una categoría con movimientos asociados. Las contraseñas usan hashing; recursos ajenos devuelven 404 y la información sensible no se serializa."),
    paragraph("El seguimiento compara el gasto persistido de la misma categoría, moneda y mes contra el límite. Menos de 80%: dentro del presupuesto; desde 80% y menos de 100%: cerca del límite; 100% o más: excedido. PEN y USD se agregan por separado."),
    paragraph("6. Pruebas y ejecución", "SectionTitle"),
    paragraph("La suite automatizada cubre 17 casos: registro/login, correo duplicado, JWT ausente/inválido/expirado, validación de montos/monedas/tipos, aislamiento, CRUD, filtros, presupuestos y reportes. Comprueba SQLite en memoria y persistencia entre dos instancias Flask con un archivo temporal. Resultado verificado: 17 passed (03/11/2026). Se ejecuta con python -m pytest -q desde backend."),
    paragraph("Para iniciar, instalar backend/requirements.txt, ejecutar flask --app run db upgrade, iniciar python run.py en backend y servir frontend con python -m http.server 5500 --directory frontend. La guía reproducible completa se encuentra en README.md."),
]

document = SimpleDocTemplate(
    str(OUTPUT), pagesize=A4,
    rightMargin=21 * mm, leftMargin=21 * mm,
    topMargin=19 * mm, bottomMargin=22 * mm,
    title="FINTRACK - Documento técnico",
    author="FINTRACK",
)
document.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
print(f"Generado: {OUTPUT} ({document.page - 1} páginas de contenido, más carátula)")