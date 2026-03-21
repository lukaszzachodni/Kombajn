from moviepy.editor import ImageClip, vfx, CompositeVideoClip, ColorClip
from ..elements.image import ImageElement
from ..j2v_base_processor import J2VBaseProcessor
from ..elements.base import HFloat, HInt, HBool # Import hybrid types
from ..elements.settings import RotateSettings, CropSettings, CorrectionSettings # Import settings

class J2VImageProcessor:
    def process(self, width: int, height: int, element_data: dict, container_duration: float):
        el = ImageElement(**element_data)
        
        # Determine duration, fall back to container duration if not specified or invalid
        element_duration = el.duration if el.duration > 0 else container_duration
        if element_duration <= 0: # Handle edge case where duration is still <= 0
            element_duration = container_duration

        # --- Image Source Handling ---
        image_source = el.src
        if not image_source and el.prompt:
            # Placeholder for AI image generation.
            # In a real implementation, this would call an AI service.
            # For now, assume src is provided or raise error if prompt is not handled.
            raise NotImplementedError("AI image generation from prompt is not yet implemented.")
            # Example: image_source = call_ai_image_generator(el.prompt, el.model, el.model_settings, el.aspect_ratio, el.connection)
            
        if not image_source:
            raise ValueError("Image source (src or prompt) must be provided.")

        # --- Create Base Clip ---
        try:
            clip = ImageClip(image_source)
            clip = clip.set_duration(element_duration) # Set duration early
        except Exception as e:
            raise IOError(f"Failed to load image from source: {image_source}. Error: {e}") from e

        # --- Apply Transformations ---
        # Target dimensions for resizing/positioning based on element's canvas
        target_width = el.width if isinstance(el.width, (int, float)) and el.width > 0 else width # Use element's width if valid number, else container
        target_height = el.height if isinstance(el.height, (int, float)) and el.height > 0 else height # Use element's height if valid number, else container

        # Resize logic: handles 'cover', 'fill', 'fit', 'contain'
        # The goal is to fit the image within the element's canvas (target_width, target_height)
        # while respecting the specified resize mode and aspect ratio.
        
        current_w, current_h = clip.size
        aspect_ratio_clip = current_w / current_h if current_h > 0 else 1.0 # Avoid division by zero
        aspect_ratio_target = target_width / target_height if target_height > 0 else aspect_ratio_clip # Avoid division by zero

        if el.resize in ["cover", "fill"]:
            # Resize to fill the target area while maintaining aspect ratio, potentially cropping.
            if aspect_ratio_clip > aspect_ratio_target: # Clip is wider than target aspect ratio
                clip = clip.resize(height=target_height) # Resize by height to match target height
            else: # Clip is taller or has same aspect ratio
                clip = clip.resize(width=target_width) # Resize by width to match target width
            # After resizing to fill, it might be larger than target. Crop to target size.
            # Center crop the resized image to fit the target canvas.
            clip = clip.crop(width=target_width, height=target_height, x_center=clip.w/2, y_center=clip.h/2)

        elif el.resize in ["fit", "contain"]:
            # Resize to fit within the target area while maintaining aspect ratio.
            if aspect_ratio_clip < aspect_ratio_target: # Clip is taller than target aspect ratio
                clip = clip.resize(width=target_width) # Resize by width to match target width
            else: # Clip is wider or has same aspect ratio
                clip = clip.resize(height=target_height) # Resize by height to match target height
            # The clip is now resized to fit. It might be smaller than the target canvas.
            # Positioning (centering) within the canvas is handled later by set_position.

        # Cropping (applied *after* resize, if both are specified)
        if el.crop:
            # Ensure crop dimensions are valid and relative to the clip's current size after resize/transformations
            crop_w = el.crop.width if el.crop.width > 0 else clip.w
            crop_h = el.crop.height if el.crop.height > 0 else clip.h
            crop_x = el.crop.x if el.crop.x >= 0 else 0
            crop_y = el.crop.y if el.crop.y >= 0 else 0
            
            clip = clip.crop(x_ பொருள=crop_x, y_ பொருள=crop_y, width=crop_w, height=crop_h)

        # Color Correction
        if el.correction:
            # Apply corrections using MoviePy's VFX. Order might matter.
            clip = clip.fx(vfx.lum_contrast, el.correction.brightness, el.correction.contrast)
            clip = clip.fx(vfx.gamma_corr, el.correction.gamma)
            clip = clip.fx(vfx.colorx, el.correction.saturation) # Assuming colorx can handle saturation factor

        # Flipping
        if el.flip_horizontal:
            clip = clip.fx(vfx.hflip)
        if el.flip_vertical:
            clip = clip.fx(vfx.vflip)
            
        # Zoom and Pan: Advanced effects requiring animation.
        # `el.zoom`, `el.pan`, `el.pan_distance` from J2VElement are placeholders for complex behavior.
        # For now, static zoom/pan are not explicitly implemented beyond basic resizing/positioning.
        # Marked as needing further development.

        # Chroma Key (Green Screen)
        if el.chroma_key:
            # Placeholder for chroma_key implementation. Requires complex masking.
            pass 

        # --- Apply Positioning ---
        # Resolve element's canvas dimensions and position.
        element_x = el.x if isinstance(el.x, (int, float)) else width
        element_y = el.y if isinstance(el.y, (int, float)) else height
        element_width_canvas = el.width if isinstance(el.width, (int, float)) else width
        element_height_canvas = el.height if isinstance(el.height, (int, float)) else height
        
        # Ensure clip dimensions are correctly obtained after transformations.
        clip_w, clip_h = clip.size

        # Calculate the final position of the clip within the parent canvas.
        clip_final_x, clip_final_y = element_x, element_y # Default for 'custom'
        
        if el.position == "custom":
            clip_final_x = element_x
            clip_final_y = element_y
        else:
            # Map predefined positions to MoviePy's alignment strings or coordinates.
            if el.position == "top-left": final_clip_pos = (element_x, element_y)
            elif el.position == "top-right": final_clip_pos = (element_x + element_width_canvas - clip_w, element_y)
            elif el.position == "bottom-left": final_clip_pos = (element_x, element_y + element_height_canvas - clip_h)
            elif el.position == "bottom-right": final_clip_pos = (element_x + element_width_canvas - clip_w, element_y + element_height_canvas - clip_h)
            elif el.position == "center-center": final_clip_pos = (element_x + element_width_canvas / 2 - clip_w / 2, element_y + element_height_canvas / 2 - clip_h / 2)
            else: # Fallback if position is not recognized, use custom logic from x,y.
                final_clip_pos = (element_x, element_y)
            clip_final_x, clip_final_y = final_clip_pos

        clip = clip.set_position((clip_final_x, clip_final_y))
        
        # Note: `rotate` property is inherited from `J2VElement` and expected to be handled by `J2VBaseProcessor.apply_common_properties`.

        # Apply common properties like z-index, timing, etc. via apply_common_properties.
        return J2VBaseProcessor.apply_common_properties(clip, el, container_duration)
