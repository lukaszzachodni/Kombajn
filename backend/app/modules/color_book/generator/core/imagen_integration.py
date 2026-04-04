from io import BytesIO
from PIL import Image
from typing import List, Optional, Tuple

from backend.app.modules.color_book.generator.utils.console_messenger import ConsoleMessenger

try:
    from vertexai.preview.generative_models import (
        GenerativeModel as VertexGenerativeModel,
    )
    from vertexai.preview.vision_models import ImageGenerationModel, GeneratedImage
    import vertexai

    _VERTEX_AI_AVAILABLE = True
except ImportError:
    ConsoleMessenger.error(
        "Could not load Vertex AI or PIL modules. "
        "Ensure 'google-cloud-aiplatform' and 'Pillow' are installed."
    )
    ConsoleMessenger.info("Try: pip install google-cloud-aiplatform Pillow")
    _VERTEX_AI_AVAILABLE = False


class ImagenIntegration:
    """
    Handles integration with the Imagen model (for image generation) in Vertex AI.
    """

    def __init__(
        self,
        project_id: str,
        location: str,
        model_name: str,
        max_attempts: int = 2,
        default_upscale: bool = False,
    ) -> None:
        if not _VERTEX_AI_AVAILABLE:
            raise RuntimeError(
                "Vertex AI or Pillow modules are not available. "
                "Make sure you have 'google-cloud-aiplatform' and 'Pillow' installed."
            )

        self.project_id: str = project_id
        self.location: str = location
        self.model_name: str = model_name
        self.max_attempts: int = max_attempts
        self.default_upscale: bool = default_upscale
        self.image_model: Optional[ImageGenerationModel] = None

        try:
            vertexai.init(project=self.project_id, location=self.location)
            self.image_model = ImageGenerationModel.from_pretrained(self.model_name)

            ConsoleMessenger.info(
                f"Imagen model '{self.model_name}' initialized for project {self.project_id} in region {self.location}.",
                color="BRIGHT_BLUE",
            )
        except Exception as e:
            ConsoleMessenger.error(f"Error initializing Imagen model: {e}")
            ConsoleMessenger.info(
                "Make sure Vertex AI API is enabled in your GCP project and you have proper authentication (gcloud auth application-default login)."
            )
            raise

    def _convert_generated_image_to_png_bytes(
        self, generated_image_object: GeneratedImage
    ) -> Optional[bytes]:
        """
        Converts a GeneratedImage object (or PIL.Image) to PNG image bytes.
        """
        pil_image: Optional[Image.Image] = None
        if isinstance(generated_image_object, GeneratedImage):
            if hasattr(generated_image_object, "_pil_image") and isinstance(
                generated_image_object._pil_image, Image.Image
            ):
                pil_image = generated_image_object._pil_image
            elif hasattr(generated_image_object, "to_pil") and callable(
                generated_image_object.to_pil
            ):
                pil_image = generated_image_object.to_pil()
            else:
                try:
                    pil_image = Image.open(BytesIO(generated_image_object.image_bytes))
                except Exception:
                    pil_image = None

        elif isinstance(generated_image_object, Image.Image):
            pil_image = generated_image_object

        if pil_image and isinstance(pil_image, Image.Image):
            img_byte_arr = BytesIO()
            pil_image.save(img_byte_arr, format="PNG")
            return img_byte_arr.getvalue()
        else:
            return None

    def generate_images(
        self,
        prompt: str,
        number_of_images: int,
        aspect_ratio: str = "1:1",
    ) -> Tuple[Optional[List[bytes]], int]:
        """
        Generates images based on a text prompt using Imagen, with retries.

        Args:
            prompt (str): The text prompt for image generation.
            number_of_images (int): The number of image variants to generate.
            aspect_ratio (str): The aspect ratio of the image (e.g., "1:1", "3:4", "9:16").

        Returns:
            Tuple[Optional[List[bytes]], int]: A list of generated image bytes (PNG),
                                                 and the number of attempts made.
                                                 Returns (None, attempts) on failure.
        """
        if not _VERTEX_AI_AVAILABLE:
            ConsoleMessenger.error(
                "Essential modules are not available. Cannot generate image."
            )
            return None, 0

        if not self.image_model:
            ConsoleMessenger.error("Imagen model is not initialized.")
            return None, 0

        for attempt in range(1, self.max_attempts + 1):
            ConsoleMessenger.info(
                f"Generating {number_of_images} image(s) with Imagen (Attempt {attempt}/{self.max_attempts})...",
                color="BLUE",
            )

            try:
                images = self.image_model.generate_images(
                    prompt=prompt,
                    number_of_images=number_of_images,
                    aspect_ratio=aspect_ratio,
                )

                generated_bytes_list: List[bytes] = []
                if images and images.images:
                    for img_obj in images.images:
                        png_bytes: Optional[bytes] = (
                            self._convert_generated_image_to_png_bytes(img_obj)
                        )
                        if png_bytes:
                            generated_bytes_list.append(png_bytes)

                    if generated_bytes_list:
                        ConsoleMessenger.success(
                            f"Successfully generated {len(generated_bytes_list)} image(s) after {attempt} attempt(s)."
                        )
                        return (generated_bytes_list, attempt)
                    else:
                        ConsoleMessenger.warning(
                            f"Attempt {attempt} failed: Could not convert generated image to PNG bytes."
                        )
                else:
                    ConsoleMessenger.warning(
                        f"Attempt {attempt} failed: Imagen did not return any image."
                    )
            except Exception as e:
                ConsoleMessenger.error(f"Attempt {attempt} failed with error: {e}")

            if attempt < self.max_attempts:
                ConsoleMessenger.info(f"Retrying image generation with Imagen...")

        ConsoleMessenger.error(
            f"Failed to generate image after {self.max_attempts} attempts."
        )
        return None, self.max_attempts
