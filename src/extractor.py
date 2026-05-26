from google import genai
from pydantic import ValidationError

from schemas import InvoiceData
from prompts import CLASSIFICATION_AND_EXTRACTION_PROMPT
from config import GEMINI_API_KEY

import json
import time
import random


client = genai.Client(api_key=GEMINI_API_KEY)


def clean_response(text):

    text = text.replace("```json", "")
    text = text.replace("```", "")

    return text.strip()


def extract_invoice_data(raw_text, retries=5):

    error = None

    delay = 10

    for attempt in range(retries):

        try:

            print(f"Sending request to Gemini... Attempt {attempt + 1}")

            response = client.models.generate_content(

                model="gemini-2.5-flash-lite",

                contents=CLASSIFICATION_AND_EXTRACTION_PROMPT + "\n\n" + raw_text,

                config={
                    "response_mime_type": "application/json"
                }
            )

            print("Gemini response received successfully")

            cleaned = clean_response(response.text)

            data = json.loads(cleaned)

            validated = InvoiceData(**data)

            return validated.model_dump(), None

        except (json.JSONDecodeError, ValidationError) as e:

            error = f"Validation Error: {str(e)}"

            print(error)

            if attempt >= 1:
                break

            time.sleep(2)

        except Exception as e:

            error = str(e)

            print(f"Attempt {attempt + 1} failed: {error}")

            if "429" in error or "RESOURCE_EXHAUSTED" in error:

                sleep_time = delay + random.uniform(1, 3)

                print(
                    f"Rate limit hit. "
                    f"Retrying in {sleep_time:.2f} seconds..."
                )

                time.sleep(sleep_time)

                delay *= 2

            else:

                print("Retrying after temporary failure...")

                time.sleep(3)

    return None, error