import argparse
import math
from pathlib import Path

import pymupdf
from pathvalidate.argparse import sanitize_filepath_arg
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg


def make_cmd_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i',
        '--input-dir',
        required=True,
        type=sanitize_filepath_arg,
        help='Path to a directory with SVG files.',
    )
    parser.add_argument(
        '-o',
        '--output-dir',
        required=True,
        type=sanitize_filepath_arg,
        help='Output path for the PNG files.',
    )
    parser.add_argument(
        '-s', '--image-size', type=int, default=64, help='Image size for the PNG files.'
    )
    return parser.parse_args()


def make_pixmap(file_path: Path, image_size: int) -> pymupdf.Pixmap:
    drawing = svg2rlg(file_path)

    if not drawing:
        raise OSError(f'An error has ocurred while processing file: {file_path}')

    pdf = renderPDF.drawToString(drawing)
    doc = pymupdf.Document(stream=pdf)

    size_to_dpi = math.ceil(image_size * 2.22)

    return doc.load_page(0).get_pixmap(alpha=True, dpi=size_to_dpi)  # type: ignore


def save_pixmap_to_file(
    pixmap: pymupdf.Pixmap, output_dir: Path, file_name: str
) -> None:
    output_file_path = f'{output_dir.joinpath(file_name)}.png'

    pixmap.save(output_file_path)

    print(f'PNG image created: {file_name}')


def main() -> None:
    args = make_cmd_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    file_paths = Path(args.input_dir).glob('*.svg')

    for file_path in file_paths:
        pix = make_pixmap(file_path, args.image_size)

        save_pixmap_to_file(pix, output_dir, file_path.stem)


if __name__ == "__main__":
    main()
