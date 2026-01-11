import cv2
import numpy as np
from typing import Dict, Any

class ZenDetector:
    def __init__(self):
        self.defect_area_threshold = 50  # pixels
        self.min_contour_area = 10  # pixels
    
    def analyze_surface(self, image_data: bytes) -> Dict[str, Any]:
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Unable to decode image")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian Blur to remove noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply Canny Edge Detection to find cracks/scratches
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours to identify anomaly sizes
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by minimum area and calculate total defect area
            significant_contours = []
            total_defect_area = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area >= self.min_contour_area:
                    significant_contours.append(contour)
                    total_defect_area += area
            
            # Determine status based on defect area threshold
            status = "Fail" if total_defect_area > self.defect_area_threshold else "Pass"
            
            # Calculate defect score (0-100)
            max_possible_area = image.shape[0] * image.shape[1] * 0.1  # 10% of image as max defect
            defect_score = min((total_defect_area / max_possible_area) * 100, 100)
            
            return {
                "status": status,
                "defect_score": round(defect_score, 1),
                "number_of_defects": len(significant_contours),
                "total_defect_area": round(total_defect_area, 1)
            }
            
        except Exception as e:
            return {
                "status": "Fail",
                "defect_score": 100.0,
                "number_of_defects": 0,
                "error": str(e)
            }
