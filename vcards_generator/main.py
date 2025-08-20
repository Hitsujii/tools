import base64
import os
import requests
import logging
import json
from datetime import datetime, timezone
from io import BytesIO
from PIL import Image  # Pillow

# Logging configuration
logging.basicConfig(
    filename="debug.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def create_vcard_with_photo_from_url(
    full_name, last_name, first_name, job_title,
    email, phone, website, address_street, address_city,
    address_postal, address_country, org, photo_url=None
):
    vcard_lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN;CHARSET=UTF-8:{full_name}",
        f"N;CHARSET=UTF-8:{last_name};{first_name};;;",
        f"TITLE;CHARSET=UTF-8:{job_title}",
        f"EMAIL;CHARSET=UTF-8;TYPE=WORK,INTERNET:{email}",
        f"TEL;TYPE=WORK,VOICE:{phone}",
        f"ADR;CHARSET=UTF-8;TYPE=WORK:;;{address_street};{address_city};;{address_postal};{address_country}",
        f"ORG;CHARSET=UTF-8:{org}"
    ]

    if website:
        vcard_lines.append(f"URL:{website}")

    if photo_url:
        try:
            response = requests.get(photo_url, timeout=10)
            response.raise_for_status()

            img = Image.open(BytesIO(response.content))

            if img.mode == "P":
                img = img.convert("RGBA")

            if img.mode == "RGBA":
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background

            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=90)
            buffer.seek(0)

            photo_data = base64.b64encode(buffer.read()).decode("utf-8")
            photo_data = "".join(photo_data.split())

            vcard_lines.append(f"PHOTO;ENCODING=b;TYPE=JPEG:{photo_data}")

        except requests.RequestException as e:
            logging.error(f"Error downloading photo: {e}")
            print(f"❌ Error downloading photo: {e}")

    current_time = datetime.now(timezone.utc).isoformat(timespec='milliseconds')
    vcard_lines.append(f"REV:{current_time}")
    vcard_lines.append("END:VCARD")

    return "\n".join(vcard_lines)

# Load contacts from JSON file
with open("contacts.json", "r", encoding="utf-8") as f:
    contacts = json.load(f)

# Create vCards for each contact
for contact in contacts:
    try:
        vcard_content = create_vcard_with_photo_from_url(
            contact["full_name"],
            contact["last_name"],
            contact["first_name"],
            contact["job_title"],
            contact["email"],
            contact["phone"],
            contact["website"],
            contact["address_street"],
            contact["address_city"],
            contact["address_postal"],
            contact["address_country"],
            contact["org"],
            contact.get("photo_url")
        )

        # File name with hyphen instead of space
        file_name = f"{contact['full_name'].replace(' ', '-').lower()}.vcf"
        file_path = os.path.join("data", file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(vcard_content)

        print(f"vCard file has been saved: {file_path}")

    except Exception as e:
        logging.error(f"Error processing contact {contact.get('full_name')}: {e}")
        print(f"Error with contact {contact.get('full_name')}: {e}")
