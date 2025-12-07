import os
import requests
import json

PINATA_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiI1MzdiY2E3ZS1iNDY5LTRjZWEtOWYxZS05OWM3NzE1NGY3MjEiLCJlbWFpbCI6Im51cmlrd3lAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInBpbl9wb2xpY3kiOnsicmVnaW9ucyI6W3siZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiRlJBMSJ9LHsiZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiTllDMSJ9XSwidmVyc2lvbiI6MX0sIm1mYV9lbmFibGVkIjpmYWxzZSwic3RhdHVzIjoiQUNUSVZFIn0sImF1dGhlbnRpY2F0aW9uVHlwZSI6InNjb3BlZEtleSIsInNjb3BlZEtleUtleSI6IjczMzNhYmVhMDFlZDQwNzQ4NTg0Iiwic2NvcGVkS2V5U2VjcmV0IjoiZjk3OTgxZjRhYTI5NzE4ZGRlOTNhNjJmYWM1ZmYzNTM1NGNjZWY5NTA5YTEzMjVhZDc0YTRjMTNiMjlkODNhZSIsImV4cCI6MTc5NjY1NzI2NX0.DRXHBqrmC6xR2uNUa8gEe7nTa5oiLEi7JwcZD_PiCEs"

def pin_folder_to_ipfs(folder_path: str):
    try:
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

        headers = {
            "Authorization": f"Bearer {PINATA_JWT}"
        }

        files = []

        # Берём только название конечной папки
        folder_name = os.path.basename(folder_path.rstrip("/"))

        for root, _, filenames in os.walk(folder_path):
            for filename in filenames:
                full_path = os.path.join(root, filename)

                # Путь внутри IPFS должен быть:
                # EsVnxVKl/filename.jpg
                relative_path = os.path.relpath(full_path, folder_path)
                ipfs_path = f"{folder_name}/{relative_path}".replace("\\", "/")

                files.append(
                    ("file", (ipfs_path, open(full_path, "rb"), "application/octet-stream"))
                )

        data = {
            "pinataMetadata": json.dumps({
                "name": folder_name
            })
        }

        res = requests.post(url, headers=headers, files=files, data=data)
        print(res.json())
        return res.json()

    except Exception as e:
        print("Error:", e)


pin_folder_to_ipfs("storage/images/EsVnxVKl")
