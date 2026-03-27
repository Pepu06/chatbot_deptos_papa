import sys
from pathlib import Path
import argparse
import asyncio

# Permite ejecutar este script directamente: `python3 scripts/test_photo_local.py ...`
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.property_agent import property_agent


async def main() -> None:
    parser = argparse.ArgumentParser(description="Prueba local de foto con PropertyAgent")
    parser.add_argument("image_path", help="Ruta a la imagen local")
    parser.add_argument(
        "--mensaje",
        default="Analizá la imagen y guardá la información del departamento con su nota.",
        help="Mensaje de texto para acompañar la imagen"
    )

    args = parser.parse_args()
    image_file = Path(args.image_path)

    if not image_file.exists() or not image_file.is_file():
        print(f"❌ No existe el archivo: {image_file}")
        return

    image_data = image_file.read_bytes()
    user_message = args.mensaje

    print("=" * 80)
    print("🧪 TEST LOCAL DE FOTO")
    print("=" * 80)
    print(f"📷 Imagen: {image_file}")
    print(f"💬 Mensaje: {user_message}")
    print()

    response = await property_agent.handle_message(
        user_message=user_message,
        image_data=image_data
    )

    print("🤖 Respuesta del PropertyAgent:")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
