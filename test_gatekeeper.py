import requests
import json

def test_gatekeeper_pipeline():
    """Test the metal surface validation gatekeeper"""
    
    # Test with a metal image (should pass validation)
    print("🧪 Testing Metal Surface Validation Gatekeeper...")
    
    # Test 1: Metal image (should pass to defect inspection)
    try:
        with open('detected_image.jpg', 'rb') as f:
            files = {'file': f}
            response = requests.post('http://localhost:8000/predict', files=files)
            
        if response.status_code == 200:
            result = response.json()
            print("✅ Metal image test:")
            print(f"   Status: {result.get('status')}")
            print(f"   Metal Validation Score: {result.get('metal_validation_score')}")
            if result.get('status') != 'INVALID_INPUT':
                print(f"   Defect Score: {result.get('defect_score')}")
                print(f"   Health Score: {result.get('health_score')}")
        else:
            print(f"❌ Metal test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Metal test error: {e}")
    
    # Test 2: Health check
    try:
        response = requests.get('http://localhost:8000/health')
        if response.status_code == 200:
            health = response.json()
            print("\n🏥 Health Check:")
            print(f"   Status: {health.get('status')}")
            print(f"   Metal Validator Loaded: {health.get('metal_validator_loaded')}")
            print(f"   Defect Inspector Loaded: {health.get('defect_inspector_loaded')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Health check error: {e}")

if __name__ == "__main__":
    test_gatekeeper_pipeline()
