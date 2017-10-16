import os

from argparse import ArgumentParser
from json import load as load_json

import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


FONTS = {
    'arial_bold_32': ImageFont.truetype('arialbd.ttf', 32),
    'arial_bold_44': ImageFont.truetype('arialbd.ttf', 44)
}


def create_icon(id, form=None, size=(94, 94), base_size=(94, 94),
                background_color='#000000', text_color='#FFFFFF'):
    id = str(id) if id else id
    form = str(form) if form else form

    icon = PIL.Image.new('RGBA', (base_size[0], base_size[1]))
    draw = ImageDraw.Draw(icon)

    draw.ellipse((0, 0, base_size[0], base_size[1]), fill=background_color)

    if form:
        font = FONTS['arial_bold_32']
        id_size = draw.textsize(id, font=font)
        form_size = draw.textsize(form, font=font)
        half_height = base_size[1] / 2.0
        draw.text(((base_size[0] - id_size[0]) / 2.0,
                   (half_height - id_size[1] - 2)),
                  id, text_color, font=font)
        draw.text(((base_size[0] - form_size[0]) / 2.0,
                   (half_height + 2)),
                  form, text_color, font=font)
    else:
        font = FONTS['arial_bold_44']
        id_size = draw.textsize(id, font=font)
        draw.text(((base_size[0] - id_size[0]) / 2.0,
                   (base_size[1] - id_size[1]) / 2.0),
                  id, text_color, font=font)

    if size != base_size:
        icon = icon.resize(size, Image.ANTIALIAS)

    return icon


if __name__ == "__main__":
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'static')

    parser = ArgumentParser(description='Generate default icons.')
    parser.add_argument('-o', '--output-dir',
                        help='The directory to save the icons to.',
                        default=os.path.join(static_dir, 'icons'))
    parser.add_argument('-s', '--size', help='The size of the icons.',
                        type=int, default=94)

    args = parser.parse_args()

    pokemon_data = {}
    with open(os.path.join(static_dir, 'data', 'pokemon.json'), 'r') as f:
        pokemon_data = load_json(f)

    for id in range(1, 387):
        color = pokemon_data[str(id)]['types'][0]['color']
        icon = create_icon(id, size=(args.size, args.size),
                           background_color=color)
        icon.save(os.path.join(args.output_dir, '{}.png'.format(id)))

    pokemon_forms = {
        201: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
              'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
              ('!', 'EXCL'), ('?', 'QUES')],
        351: ['NML', 'SUN', 'RN', 'SNW'],
        386: ['NML', 'ATK', 'DEF', 'SPE']
    }

    for id, forms in pokemon_forms.iteritems():
        color = pokemon_data[str(id)]['types'][0]['color']
        for form in forms:
            form_sym = form[0] if isinstance(form, tuple) else form
            form_name = form[1] if isinstance(form, tuple) else form
            icon = create_icon(id, form_sym, size=(args.size, args.size),
                               background_color=color)
            icon.save(os.path.join(
                      args.output_dir, '{}-{}.png'.format(id, form_name)))
