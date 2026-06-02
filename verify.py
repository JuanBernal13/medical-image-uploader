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

    print("\n--- Testing Add Tag ---")
    r = httpx.post(f"{BASE_URL}/api/v1/images/{image_id}/tags", json={"tag": "Chest-Xray"})
    print("Status:", r.status_code)
    tags_res = r.json()
    print("Response:", tags_res)
    assert r.status_code == 200
    assert "Chest-Xray" in tags_res

    print("\n--- Testing List Images By Tag ---")
    r = httpx.get(f"{BASE_URL}/api/v1/images/tags/Chest-Xray")
    print("Status:", r.status_code)
    tag_imgs = r.json()
    print("Response:", tag_imgs)
    assert r.status_code == 200
    assert len(tag_imgs) >= 1

    print("\n--- Testing Search By Modality ---")
    r = httpx.get(f"{BASE_URL}/api/v1/images/search/modality/XRAY")
    print("Status:", r.status_code)
    modality_res = r.json()
    print("Response:", modality_res)
    assert r.status_code == 200
    assert len(modality_res) >= 1

    print("\n--- Testing Search By Body Part ---")
    r = httpx.get(f"{BASE_URL}/api/v1/images/search/body-part/CHEST")
    print("Status:", r.status_code)
    body_part_res = r.json()
    print("Response:", body_part_res)
    assert r.status_code == 200
    assert len(body_part_res) >= 1

    print("\n--- Testing Search By Age Range ---")
    r = httpx.get(f"{BASE_URL}/api/v1/images/search/age?min_age=40&max_age=50")
    print("Status:", r.status_code)
    age_res = r.json()
    print("Response:", age_res)
    assert r.status_code == 200
    assert len(age_res) >= 1

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

    print("\n--- Testing Get Reviewers List ---")
    r = httpx.get(f"{BASE_URL}/api/v1/reviewers")
    print("Status:", r.status_code)
    reviewers_list = r.json()
    print("Response:", reviewers_list)
    assert r.status_code == 200
    assert "Dr. House" in reviewers_list

    print("\n--- Testing Reviewer Stats ---")
    r = httpx.get(f"{BASE_URL}/reviewers/Dr. House/stats")
    print("Status:", r.status_code)
    reviewer_stats = r.json()
    print("Response:", reviewer_stats)
    assert r.status_code == 200
    assert reviewer_stats["total_reviews"] >= 1

    print("\n--- Testing Get Image Reviews Count ---")
    r = httpx.get(f"{BASE_URL}/api/v1/images/{image_id}/reviews/count")
    print("Status:", r.status_code)
    count_res = r.json()
    print("Response:", count_res)
    assert r.status_code == 200
    assert count_res["reviews_count"] == 1

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

    print("\n--- Testing Update Comment ---")
    r = httpx.put(f"{BASE_URL}/api/v1/reviews/{review_id}/comments/0", json={"text": "Updated comment text."})
    print("Status:", r.status_code)
    update_comment_res = r.json()
    print("Response:", update_comment_res)
    assert r.status_code == 200
    assert update_comment_res["comments"][0]["text"] == "Updated comment text."

    print("\n--- Testing Reprocess Image Dimensions ---")
    r = httpx.post(f"{BASE_URL}/api/v1/images/{image_id}/reprocess")
    print("Status:", r.status_code)
    reprocess_res = r.json()
    print("Response:", reprocess_res)
    assert r.status_code == 200

    print("\n--- Testing Patch Review Status ---")
    r = httpx.patch(f"{BASE_URL}/api/v1/reviews/{review_id}/status", json={"status": "PENDING"})
    print("Status:", r.status_code)
    status_patch_res = r.json()
    print("Response:", status_patch_res)
    assert r.status_code == 200
    assert status_patch_res["status"] == "PENDING"

    print("\n--- Testing Get Pending Reviews ---")
    r = httpx.get(f"{BASE_URL}/api/v1/reviews/pending")
    print("Status:", r.status_code)
    pending_list = r.json()
    print("Response:", pending_list)
    assert r.status_code == 200
    assert len(pending_list) >= 1

    print("\n--- Testing List All Patient IDs ---")
    r = httpx.get(f"{BASE_URL}/api/v1/patients")
    print("Status:", r.status_code)
    patients_list = r.json()
    print("Response:", patients_list)
    assert r.status_code == 200
    assert "PATIENT_999" in patients_list

    print("\n--- Testing Remove Tag ---")
    r = httpx.delete(f"{BASE_URL}/api/v1/images/{image_id}/tags/Chest-Xray")
    print("Status:", r.status_code)
    remove_tag_res = r.json()
    print("Response:", remove_tag_res)
    assert r.status_code == 200
    assert "Chest-Xray" not in remove_tag_res

    print("\n--- Testing Delete Comment ---")
    r = httpx.delete(f"{BASE_URL}/api/v1/reviews/{review_id}/comments/0")
    print("Status:", r.status_code)
    del_comment_res = r.json()
    print("Response:", del_comment_res)
    assert r.status_code == 200
    assert len(del_comment_res["comments"]) == 0

    print("\n--- Testing Delete Image ---")
    r = httpx.delete(f"{BASE_URL}/api/v1/images/{image_id}")
    print("Status:", r.status_code)
    assert r.status_code == 204

    print("\nAll integration tests passed successfully!")

if __name__ == "__main__":
    test_api()
