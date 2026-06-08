import jwt
from dotenv import load_dotenv
import os

load_dotenv()

SAMPLE_JWT = os.getenv("SAMPLE_JWT")
print(SAMPLE_JWT)

header = jwt.get_unverified_header(SAMPLE_JWT)
payload = jwt.get_unverified_payload(SAMPLE_JWT)

print("Header:", header)
print("Payload:", payload)