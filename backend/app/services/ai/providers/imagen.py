from io import BytesIO
from typing import List, Optional
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from backend.app.services.ai.base import ImageGenProvider

class ImagenProvider(ImageGenProvider):
    def __init__(self, project_id: str, location: str, model_name: str):
        if not project_id or not location:
            raise ValueError("GCP Project ID and location are required for Imagen")
        
        vertexai.init(project=project_id, location=location)
        self.model = ImageGenerationModel.from_pretrained(model_name)
        self.model_name = model_name

    def generate_images(
        self, 
        prompt: str, 
        number_of_images: int = 1, 
        aspect_ratio: str = "1:1",
        **kwargs
    ) -> List[bytes]:
        try:
            responses = self.model.generate_images(
                prompt=prompt,
                number_of_images=number_of_images,
                aspect_ratio=aspect_ratio,
            )
            
            image_bytes_list = []
            if responses and responses.images:
                for img_obj in responses.images:
                    # Imagen zwraca obiekty, które mają metodę _as_bytes() lub podobną
                    # W oryginalnym kodzie było to bardziej skomplikowane (konwersja PIL)
                    # Tutaj upraszczamy, zakładając dostęp do surowych bajtów
                    if hasattr(img_obj, "image_bytes"):
                        image_bytes_list.append(img_obj.image_bytes)
                    else:
                        # Fallback do zapisu przez PIL jeśli surowe bajty niedostępne
                        img_byte_arr = BytesIO()
                        img_obj.save(img_byte_arr, format="PNG")
                        image_bytes_list.append(img_byte_arr.getvalue())
                        
            return image_bytes_list
        except Exception as e:
            print(f"Imagen error: {e}")
            return []
