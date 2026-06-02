import httpx
import time
import sys

BASE_URL = "http://localhost:8000"

def test_api():
    print("Waiting for API to become healthy...")
    retries = 15
    for i in range(retries):
        try:
            r = httpx.get(f"{BASE_URL}/actuator/health")
            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "UP":
                    print("API is healthy!")
                    break
        except Exception:
            pass
        print(f"Waiting... ({i+1}/{retries})")
        time.sleep(2)
    else:
        print("API failed to start or did not become healthy in time.")
        sys.exit(1)

    print("\n--- Testing Actuator Info ---")
    r = httpx.get(f"{BASE_URL}/actuator/info")
    print("Status:", r.status_code)
    print("Response:", r.json())
    assert r.status_code == 200

    print("\n--- Testing Actuator Metrics ---")
    r = httpx.get(f"{BASE_URL}/actuator/metrics")
    print("Status:", r.status_code)
    print("Response:", r.json())
    assert r.status_code == 200

    print("\n--- Testing Upload Image ---")
    dummy_file = b"DUMMY_IMAGE_BINARY_DATA_REPRESENTING_XRAY"
    files = {"file": ("xray.png", dummy_file, "image/png")}
    data = {
        "patient_id": "PATIENT_999",
        "modality": "XRAY",
        "body_part": "CHEST",
        "patient_age": "45",
        "patient_gender": "M"
    }
    r = httpx.post(f"{BASE_URL}/api/v1/images/upload", files=files, data=data)
    print("Status:", r.status_code)
    upload_res = r.json()
    print("Response:", upload_res)
    assert r.status_code == 201
    image_id = upload_res["image_id"]

    print("\n--- Testing Get Image Details ---")
    r = httpx.get(f"{BASE_URL}/api/v1/images/{image_id}")
    print("Status:", r.status_code)
    details = r.json()
    print("Response:", details)
    assert r.status_code == 200
    assert details["metadata"]["patient_id"] == "PATIENT_999"

    print("\n--- Testing Get Image Download URL ---")
    r = httpx.get(f"{BASE_URL}/api/v1/images/{image_id}/download")
    print("Status:", r.status_code)
    download_res = r.json()
    print("Response:", download_res)
    assert r.status_code == 200
    assert "download_url" in download_res

    print("\n--- Testing Create Image Review ---")
    review_data = {
        "reviewer_name": "Dr. House",
        "status": "APPROVED",
        "findings": "Clear lungs, no visible nodules or infections.",
        "severity": "NORMAL"
    }
    r = httpx.post(f"{BASE_URL}/api/v1/images/{image_id}/reviews", json=review_data)
    print("Status:", r.status_code)
    review_res = r.json()
    print("Response:", review_res)
    assert r.status_code == 201
    review_id = review_res["id"]

    print("\n--- Testing Get Image Reviews ---")
    r = httpx.get(f"{BASE_URL}/api/v1/images/{image_id}/reviews")
    print("Status:", r.status_code)
    reviews_list = r.json()
    print("Response:", reviews_list)
    assert r.status_code == 200
    assert len(reviews_list) >= 1

    print("\n--- Testing Add Comment to Review ---")
    comment_data = {
        "author": "Dr. Foreman",
        "text": "Agreed with the findings."
    }
    r = httpx.post(f"{BASE_URL}/api/v1/reviews/{review_id}/comments", json=comment_data)
    print("Status:", r.status_code)
    comment_res = r.json()
    print("Response:", comment_res)
    assert r.status_code == 201
    assert len(comment_res["comments"]) == 1

    print("\n--- Testing Update Metadata ---")
    meta_update = {
        "patient_id": "PATIENT_999",
        "modality": "XRAY",
        "body_part": "LUNGS",
        "patient_age": 46,
        "patient_gender": "M"
    }
    r = httpx.put(f"{BASE_URL}/api/v1/images/{image_id}/metadata", json=meta_update)
    print("Status:", r.status_code)
    meta_res = r.json()
    print("Response:", meta_res)
    assert r.status_code == 200
    assert meta_res["body_part"] == "LUNGS"

    print("\n--- Testing Get Patient Images ---")
    r = httpx.get(f"{BASE_URL}/api/v1/patients/PATIENT_999/images")
    print("Status:", r.status_code)
    patient_imgs = r.json()
    print("Response:", patient_imgs)
    assert r.status_code == 200
    assert len(patient_imgs) >= 1

    print("\n--- Testing System Stats ---")
    r = httpx.get(f"{BASE_URL}/api/v1/stats")
    print("Status:", r.status_code)
    stats_res = r.json()
    print("Response:", stats_res)
    assert r.status_code == 200

    print("\n--- Testing List Images ---")
    r = httpx.get(f"{BASE_URL}/api/v1/images")
    print("Status:", r.status_code)
    imgs_list = r.json()
    print("Response:", imgs_list)
    assert r.status_code == 200
    assert len(imgs_list) >= 1

    print("\n--- Testing Delete Image ---")
    r = httpx.delete(f"{BASE_URL}/api/v1/images/{image_id}")
    print("Status:", r.status_code)
    assert r.status_code == 204

    print("\n--- Testing Image Deleted Verification ---")
    r = httpx.get(f"{BASE_URL}/api/v1/images/{image_id}")
    print("Status:", r.status_code)
    assert r.status_code == 404

    print("\nAll integration tests passed successfully!")

if __name__ == "__main__":
    test_api()
