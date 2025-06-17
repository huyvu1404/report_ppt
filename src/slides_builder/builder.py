
from pptx import Presentation
from pptx.util import Inches
from .create_1st_slide import create_first_slide
from .create_2nd_slide import create_second_slide
from .create_3rd_slide import create_third_slide
from .create_4th_slide import create_fourth_slide
from .create_5th_slide import create_fifth_slide

def create_presentation(current_data, previous_data, main_topic, current_json, previous_json):
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(5.63)
    create_first_slide(prs, current_data, previous_data, main_topic, current_json, previous_json)
    create_second_slide(prs, current_data, previous_data, main_topic, current_json, previous_json)
    create_third_slide(prs, current_data, main_topic, current_json)
    create_fourth_slide(prs, current_data, previous_data, main_topic, current_json, previous_json)
    create_fifth_slide(prs, current_data, main_topic, current_json)
    return prs

    
