import requests
import time
import os
import json

BASE_URL = "http://localhost:8000"

def test_dedup():
    print("Testing Entity Deduplication across two consecutive uploads...")
    
    # 1. Create World
    res = requests.post(f"{BASE_URL}/worlds")
    res.raise_for_status()
    world_id = res.json()["id"]
    print(f"Created world: {world_id}")

    # 2. Upload first manuscript (we can just mock a text file)
    text_content = "Elara Vance entered the Sunken City. She spoke to Kaelen."
    files = {"file": ("test1.txt", text_content, "text/plain")}
    res = requests.post(f"{BASE_URL}/worlds/{world_id}/manuscripts", files=files)
    res.raise_for_status()
    job_id1 = res.json()["job_id"]
    print(f"Upload 1 started. Job ID: {job_id1}")

    # Wait for job 1 to finish
    while True:
        status_res = requests.get(f"{BASE_URL}/jobs/{job_id1}").json()
        if status_res["status"] == "done":
            break
        elif status_res["status"] == "failed":
            print("Job 1 failed:", status_res)
            return
        time.sleep(2)
    print("Upload 1 finished.")

    # 3. Upload second manuscript (similar content to trigger deduplication)
    text_content2 = "Elara Vance, also known as Elara, discovered a new artifact in the Sunken City."
    files = {"file": ("test2.txt", text_content2, "text/plain")}
    res = requests.post(f"{BASE_URL}/worlds/{world_id}/manuscripts", files=files)
    res.raise_for_status()
    job_id2 = res.json()["job_id"]
    print(f"Upload 2 started. Job ID: {job_id2}")

    # Wait for job 2 to finish
    while True:
        status_res = requests.get(f"{BASE_URL}/jobs/{job_id2}").json()
        if status_res["status"] == "done":
            break
        elif status_res["status"] == "failed":
            print("Job 2 failed:", status_res)
            return
        time.sleep(2)
    print("Upload 2 finished.")

    # 4. Check entities
    res = requests.get(f"{BASE_URL}/worlds/{world_id}/entities")
    res.raise_for_status()
    entities = res.json()["entities"]
    
    print("\n--- Entities after two uploads ---")
    elara_count = 0
    sunken_city_count = 0
    for ent in entities:
        print(f"[{ent['id']}] {ent['canonical_name']} ({ent['entity_type']}) - Provenance: {ent['provenance']}")
        if "elara" in ent['canonical_name'].lower():
            elara_count += 1
        if "sunken city" in ent['canonical_name'].lower():
            sunken_city_count += 1
            
    if elara_count == 1 and sunken_city_count == 1:
        print("\nSUCCESS: Deduplication worked! Only one Elara and one Sunken City exists.")
    else:
        print(f"\nFAILURE: Found {elara_count} Elaras and {sunken_city_count} Sunken Cities.")

if __name__ == "__main__":
    test_dedup()
