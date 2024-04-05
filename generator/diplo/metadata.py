import json

with open('./storage/jsons/3/fullMetadata.json', 'r', encoding="utf-8") as f:
    items = json.load(f)

prefix = 'https://bafybeihzurkouruoo3zhq52bcnvbefx5svx4xgopdxfvna4bqizr4qanca.ipfs.nftstorage.link/'
data = []

for item in items:
    image_name = "_".join(item['name_en'].split(" "))
    item['image'] = f"{prefix}{image_name}_kz_ru.jpeg, {prefix}{image_name}_en.jpeg"
    data.append(item)

with open('./storage/fullMetadata.json', 'w', encoding="utf-8") as w:
    json.dump(data, w, ensure_ascii=False, indent=2)
