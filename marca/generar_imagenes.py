"""
Genera las imágenes de marca de ChipZone a partir de la identidad de la
landing (fondo tipo placa, "CHIP" con degradado cian-verde y "ZONE"
delineado).

    python marca/generar_imagenes.py

Produce, en esta misma carpeta:
    perfil.png    500x500    foto de perfil de Facebook/Instagram
    portada.png  1640x624    portada de la página de Facebook
    og.png       1200x630    imagen de vista previa del sitio (og:image)

Por qué se generan por código y no a mano: así se regeneran idénticas si
cambia el teléfono, el dominio o un texto, sin depender de un editor de
imágenes ni de acordarse de los colores exactos.

NO reemplaza al logo original del usuario: es una adaptación tipográfica
de la misma marca, la misma que usa la web.
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))

# Los mismos tokens de color que el CSS de la landing.
PCB = (10, 20, 32)
PCB_LINE = (28, 51, 70)
CYAN = (59, 198, 240)
TRACE = (31, 180, 135)
VERDE_CLARO = (191, 243, 217)
ON_PCB = (233, 242, 248)
ON_PCB_DIM = (144, 167, 184)
WA = (37, 211, 102)

FUENTES = "C:/Windows/Fonts/"
BOLD = FUENTES + "segoeuib.ttf"
SEMI = FUENTES + "seguisb.ttf"
REG = FUENTES + "segoeui.ttf"


def fuente(ruta, tam):
    return ImageFont.truetype(ruta, tam)


def ancho(draw, texto, f):
    caja = draw.textbbox((0, 0), texto, font=f)
    return caja[2] - caja[0]


def fondo(w, h):
    """Placa oscura con dos resplandores, como el hero de la web."""
    img = Image.new("RGB", (w, h), PCB)

    brillo = Image.new("RGB", (w, h), PCB)
    d = ImageDraw.Draw(brillo)
    # Resplandor verde arriba a la derecha y cian arriba a la izquierda.
    d.ellipse([w * 0.45, -h * 0.55, w * 1.15, h * 0.75], fill=(16, 58, 52))
    d.ellipse([-w * 0.25, -h * 0.5, w * 0.5, h * 0.7], fill=(12, 44, 66))
    brillo = brillo.filter(ImageFilter.GaussianBlur(max(w, h) // 8))
    img = Image.blend(img, brillo, 0.55)

    # Pistas de circuito: líneas finas con codos, apenas visibles.
    capa = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    paso = max(w, h) // 9
    for i in range(-2, 12):
        x = i * paso
        d.line([(x, h), (x + paso // 2, h - paso // 2),
                (x + paso // 2, paso // 2), (x + paso, 0)],
               fill=PCB_LINE + (70,), width=2)
    img = Image.alpha_composite(img.convert("RGBA"), capa)
    return img.convert("RGB")


def texto_degradado(base, xy, texto, f, colores):
    """Dibuja texto relleno con un degradado horizontal.

    Pillow no rellena texto con degradados: hay que hacer el texto como
    máscara y usarla para recortar una imagen de degradado.
    """
    w, h = base.size
    grad = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(grad)
    n = len(colores) - 1
    for x in range(w):
        t = x / max(w - 1, 1) * n
        i = min(int(t), n - 1)
        f_local = t - i
        c = tuple(int(colores[i][k] + (colores[i + 1][k] - colores[i][k]) * f_local)
                  for k in range(3))
        d.line([(x, 0), (x, h)], fill=c)

    mascara = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mascara).text(xy, texto, font=f, fill=255)
    base.paste(grad, (0, 0), mascara)


def texto_delineado(draw, xy, texto, f, color=ON_PCB, grosor=2):
    """'ZONE' va delineado, como en la web."""
    draw.text(xy, texto, font=f, fill=color + (36,),
              stroke_width=grosor, stroke_fill=color)


# ----------------------------------------------------------------------

def perfil(lado=500):
    """Foto de perfil. Facebook e Instagram la recortan en círculo, así que
    todo el contenido va bien adentro del círculo inscripto."""
    img = fondo(lado, lado).convert("RGBA")
    d = ImageDraw.Draw(img)

    # Anillo, del mismo cian que el borde del logo en la web.
    margen = lado * 0.055
    d.ellipse([margen, margen, lado - margen, lado - margen],
              outline=CYAN, width=int(lado * 0.022))

    f_chip = fuente(BOLD, int(lado * 0.235))
    f_zone = fuente(BOLD, int(lado * 0.185))

    x_chip = (lado - ancho(d, "CHIP", f_chip)) / 2
    texto_degradado(img, (x_chip, lado * 0.305), "CHIP", f_chip,
                    [CYAN, TRACE, VERDE_CLARO])

    d = ImageDraw.Draw(img)
    x_zone = (lado - ancho(d, "ZONE", f_zone)) / 2
    texto_delineado(d, (x_zone, lado * 0.505), "ZONE", f_zone,
                    grosor=int(lado * 0.006))

    ruta = os.path.join(AQUI, "perfil.png")
    img.convert("RGB").save(ruta, "PNG")
    return ruta


def _marca(img, d, x, y, tam):
    """El wordmark CHIPZONE, devuelve el ancho ocupado."""
    f = fuente(BOLD, tam)
    texto_degradado(img, (x, y), "CHIP", f, [CYAN, TRACE, VERDE_CLARO])
    d2 = ImageDraw.Draw(img)
    w_chip = ancho(d2, "CHIP", f)
    texto_delineado(d2, (x + w_chip + tam * 0.06, y), "ZONE", f,
                    grosor=max(2, tam // 34))
    return w_chip + ancho(d2, "ZONE", f) + tam * 0.06


def _lamina(w, h, tam_marca, y_marca, lineas, ruta):
    """Lámina horizontal reutilizable: marca + bajada + datos + contacto."""
    img = fondo(w, h).convert("RGBA")
    d = ImageDraw.Draw(img)

    x = w * 0.5
    ancho_marca = _marca(img, d, 0, y_marca, tam_marca)
    # Recentrar: se dibujó en x=0 para poder medirla, así que se rehace.
    img = fondo(w, h).convert("RGBA")
    d = ImageDraw.Draw(img)
    _marca(img, d, x - ancho_marca / 2, y_marca, tam_marca)
    d = ImageDraw.Draw(img)

    y = y_marca + tam_marca * 1.45
    for texto, tam, color, ruta_fuente, espacio in lineas:
        f = fuente(ruta_fuente, tam)
        d.text(((w - ancho(d, texto, f)) / 2, y), texto, font=f, fill=color)
        y += espacio

    img.convert("RGB").save(ruta, "PNG")
    return ruta


def portada(w=1640, h=624):
    """Portada de la página de Facebook.

    DOS restricciones que mandan el diseño:

    1. **La foto de perfil se superpone sobre el centro-abajo** de la
       portada y tapa lo que haya ahí. Por eso TODO el texto va en la
       mitad de arriba: nada por debajo del 50% de la altura.
    2. El celular recorta los costados, así que todo va centrado.

    Tampoco lleva el wordmark: la foto de perfil ya tiene el logo, y
    repetirlo al lado queda redundante. La portada se usa para decir qué
    hacés y cómo contactarte, que es lo que el logo no dice.
    """
    img = fondo(w, h).convert("RGBA")
    d = ImageDraw.Draw(img)

    lineas = [
        ("Servicio técnico de PC y notebooks", int(h * 0.095), ON_PCB, BOLD, 0.155),
        ("Retiro y entrega a domicilio en toda CABA", int(h * 0.055), ON_PCB_DIM, REG, 0.285),
        ("14 años  ·  Presupuesto sin cargo  ·  Garantía por escrito",
         int(h * 0.046), ON_PCB_DIM, REG, 0.375),
        ("WhatsApp 11 3933-3526", int(h * 0.068), WA, BOLD, 0.455),
    ]
    for texto, tam, color, ruta_fuente, y_rel in lineas:
        f = fuente(ruta_fuente, tam)
        d.text(((w - ancho(d, texto, f)) / 2, h * y_rel), texto, font=f, fill=color)

    ruta = os.path.join(AQUI, "portada.png")
    img.convert("RGB").save(ruta, "PNG")
    return ruta


def og(w=1200, h=630):
    """Vista previa del sitio al compartirlo (WhatsApp, Facebook, etc.)."""
    return _lamina(
        w, h, tam_marca=int(h * 0.19), y_marca=h * 0.20,
        lineas=[
            ("Reparación de computadoras", int(h * 0.078), ON_PCB, SEMI, h * 0.095),
            ("y notebooks a domicilio", int(h * 0.078), ON_PCB, SEMI, h * 0.125),
            ("14 años  ·  Presupuesto sin cargo  ·  Garantía por escrito",
             int(h * 0.046), ON_PCB_DIM, REG, h * 0.095),
            ("chipzoneinformatica.com.ar", int(h * 0.05), CYAN, BOLD, 0),
        ],
        ruta=os.path.join(AQUI, "og.png"),
    )


if __name__ == "__main__":
    for f in (perfil, portada, og):
        ruta = f()
        img = Image.open(ruta)
        print(f"  {os.path.basename(ruta):12s} {img.size[0]}x{img.size[1]}  "
              f"{os.path.getsize(ruta) // 1024} KB")
