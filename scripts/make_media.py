"""Assemble real browser capture frames and draw a code-native social preview."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def social_preview():
    data = json.loads((ROOT / 'docs/evidence.json').read_text())
    image = Image.new('RGB', (1280,640), '#0a131b'); draw = ImageDraw.Draw(image)
    font_root = Path('C:/Windows/Fonts')
    def font(size): return ImageFont.truetype(str(font_root / 'arial.ttf'), size)
    draw.text((64,48), 'NAZMUL HASSAN  /  ANALYTICS PORTFOLIO', font=font(18), fill='#92aab7')
    draw.text((64,118), 'Service desk,', font=font(76), fill='#e8f0f4')
    draw.text((64,207), 'measured clearly.', font=font(76), fill='#73e2ae')
    draw.text((67,318), 'SQL models. Tested data. Decisions that matter.', font=font(26), fill='#a5bac5')
    labels=[('TICKET GRAIN', f"{data['summaries']['public']['opened_tickets']:,}", 'public UCI incidents'), ('QUALITY CHECKS', str(data['dbt_tests']), 'passing dbt tests'), ('THE STACK', 'SQL + Python', 'DuckDB / dbt / Streamlit')]
    for i,(label,value,note) in enumerate(labels):
        x=64+i*390
        draw.rounded_rectangle((x,399,x+365,555), radius=14, fill='#111c24', outline='#25343c', width=2)
        draw.text((x+24,420),label,font=font(15),fill='#92aab7')
        draw.text((x+24,449),value,font=font(34),fill='#73e2ae')
        draw.text((x+24,509),note,font=font(18),fill='#a5bac5')
    draw.text((64,593), 'github.com/iamnajib71/service-desk-analytics',font=font(19),fill='#92aab7')
    image.save(ROOT / 'docs/social-preview.png')


def gif():
    paths=sorted((ROOT / 'docs/img/frames').glob('*.png'))
    frames=[]
    for path in paths:
        im=Image.open(path).convert('RGB')
        im.thumbnail((1040,650))
        frames.append(im.quantize(colors=96, method=Image.Quantize.MEDIANCUT))
    if not frames: raise ValueError('No recorded browser frames')
    frames[0].save(ROOT / 'docs/demo.gif',save_all=True,append_images=frames[1:],duration=1000,loop=0,optimize=False)
    print(f'Recorded {len(frames)} frames / {len(frames)} seconds; GIF bytes: {(ROOT / "docs/demo.gif").stat().st_size}')


if __name__ == '__main__':
    social_preview(); gif()
