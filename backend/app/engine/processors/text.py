from moviepy.editor import TextClip, ColorClip, CompositeVideoClip
from ..elements.text import TextElement
from ..j2v_base_processor import J2VBaseProcessor
from ..elements.base import HFloat, HInt, HBool # Import hybrid types if needed for logic, though processor works with parsed types

class J2VTextProcessor:
    def process(self, width: int, height: int, element_data: dict, container_duration: float):
        el = TextElement(**element_data)
        settings = el.settings
        
        # Determine duration, fall back to container duration if not specified or invalid
        element_duration = el.duration if el.duration > 0 else container_duration
        if element_duration <= 0: # Handle edge case where duration is still <= 0
            element_duration = container_duration

        # Prepare text content: handle all_caps
        text_content = el.text
        if settings.get("all-caps", False):
            text_content = text_content.upper()

        # TextClip parameters
        font_family = settings.get("font-family", "Arial")
        font_size = int(settings.get("font-size", 70))
        font_color = settings.get("font-color", "white")
        font_weight_str = settings.get("font-weight", "normal") # Expecting string like "bold" or "400"
        
        # Map font_weight to MoviePy's expected values. MoviePy may handle common string weights.
        font_weight = font_weight_str 

        # Handle background color: create a background clip if specified
        bg_color = settings.get("background-color")
        
        # Text alignment within the textbox (from settings)
        # MoviePy's TextClip method='caption' or 'label' can influence alignment.
        # For simplicity, we'll use 'caption' and rely on positioning for overall alignment.
        text_align = settings.get("text-align", "center") # e.g., "left", "center", "right" - not directly used by TextClip but impacts layout.

        # Determine size for TextClip. Use element's width/height if provided, otherwise use container width.
        clip_width_req = el.width if el.width > 0 else width
        clip_height_req = el.height if el.height > 0 else None # Let TextClip determine height based on width and text if not specified

        try:
            txt_clip = TextClip(
                text_content,
                fontsize=font_size,
                color=font_color,
                font=font_family,
                font_weight=font_weight, # Pass font weight if TextClip supports it directly
                method="caption", # Using 'caption' for basic wrapping.
                size=(clip_width_req, clip_height_req) 
            )
            # Ensure clip dimensions are obtained after creation for positioning calculations
            clip_w, clip_h = txt_clip.size

            # Handle background color clip if specified
            final_clip = txt_clip # Start with just the text clip
            if bg_color:
                # Create a background clip that matches the text clip's dimensions and position
                bg_clip = ColorClip(size=(clip_w, clip_h), color=bg_color, duration=element_duration)
                # Composite the text clip onto the background clip. The text clip should be on top.
                # Center the text clip on the background clip.
                final_clip = CompositeVideoClip([bg_clip.set_duration(element_duration), txt_clip.set_position('center').set_duration(element_duration)])
                final_clip = final_clip.set_duration(element_duration) # Ensure the composite clip's duration is set correctly


            # Resolve element's position based on element properties and settings
            # These define the 'canvas' area for the text element.
            element_x = el.x if isinstance(el.x, (int, float)) else width
            element_y = el.y if isinstance(el.y, (int, float)) else height
            element_width_canvas = el.width if isinstance(el.width, (int, float)) else width
            element_height_canvas = el.height if isinstance(el.height, (int, float)) else height

            # Map predefined positions and settings alignment to MoviePy coordinates
            v_align_setting = settings.get("vertical-position", "center") # e.g., 'top', 'center', 'bottom'
            h_align_setting = settings.get("horizontal-position", "center") # e.g., 'left', 'center', 'right'
            
            # Calculate the top-left corner of the final clip within the parent canvas
            # This logic positions the final_clip (text or composite) within the element's defined canvas area (element_x, element_y, element_width_canvas, element_height_canvas)
            
            clip_final_x = element_x
            clip_final_y = element_y
            
            # Adjust clip's final X position based on horizontal alignment and canvas width
            if h_align_setting == "left":
                clip_final_x = element_x
            elif h_align_setting == "right":
                clip_final_x = element_x + element_width_canvas - clip_w # Align right edge of clip with right edge of canvas
            else: # center
                clip_final_x = element_x + (element_width_canvas / 2) - (clip_w / 2) # Center horizontally within canvas
            
            # Adjust clip's final Y position based on vertical alignment and canvas height
            if v_align_setting == "top":
                clip_final_y = element_y
            elif v_align_setting == "bottom":
                clip_final_y = element_y + element_height_canvas - clip_h # Align bottom edge of clip with bottom of canvas
            else: # center
                clip_final_y = element_y + (element_height_canvas / 2) - (clip_h / 2) # Center vertically within canvas

            # Set the calculated position, start time, and duration for the final composite clip
            final_clip = final_clip.set_position((clip_final_x, clip_final_y)).set_start(el.start).set_duration(element_duration)

            # Apply common properties like z-index, transformations etc. handled by apply_common_properties
            return J2VBaseProcessor.apply_common_properties(final_clip, el, container_duration)

        except Exception as e:
            # Ensure cleanup if any error occurs during clip creation or processing
            if 'txt_clip' in locals() and txt_clip:
                try: txt_clip.close()
                except: pass
            if 'bg_clip' in locals() and bg_clip:
                try: bg_clip.close()
                except: pass
            if 'final_clip' in locals() and final_clip:
                try: final_clip.close()
                except: pass
            raise e
