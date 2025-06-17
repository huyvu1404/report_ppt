from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from .slide_utils import create_rectangle, create_rounded_rectangle, create_text_box, create_section_rectangle

def create_slide_header(shapes, texts, shape_colors, text_colors, width_scale):
    SECTION_LEFT, SECTION_TOP, SECTION_WIDTH, SECTION_HEIGHT = Inches(2.31), Inches(0.13), Inches(1.42), Inches(0.2)
    SECRTION_SPACING = Inches(0.16)
    NUM_SECTIONS = 3
    create_section_rectangle(shapes, NUM_SECTIONS, (SECTION_LEFT, SECTION_TOP, SECTION_WIDTH, SECTION_HEIGHT), shape_colors, text_colors, width_scale, spacing=SECRTION_SPACING, texts=texts)
    left, top, width, height = Inches(0), Inches(0.46), Inches(10), Inches(0.39)
    create_rectangle(shapes, (left, top, width, height), gradient=True, shadow=False)
    
    left, top, width, height = Inches(-0.35), Inches(0.45), Inches(0.77), Inches(0.4)
    create_rounded_rectangle( shapes, (left, top, width, height), adjustment=0.5, color=RGBColor(255, 255, 255), shadow=False)
    