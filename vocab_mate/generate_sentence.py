# views.py
import hashlib
import datetime
import os
from django.http import JsonResponse
from django.conf import settings
from openai import OpenAI
from .models import DailySentence

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class DailySentenceGenerator:
    def __init__(self, count=20):
        self.count = count

    def _hash(self, text: str):
        """Generate hash to detect duplicates."""
        return hashlib.sha256(text.lower().encode()).hexdigest()

    def _generate_hindi_english(self, existing_sentences):
        """Ask OpenAI for Hindi-English pairs excluding previous ones."""
        prompt = f"""
        You are a Hindi-English language teacher.
        Generate {self.count} unique daily-use sentences.
        Each should be a Hindi-English pair in JSON format:
        [{{"hindi": "...", "english": "..."}}]

        Do not repeat any of these existing sentences:
        {existing_sentences}
        Sentences should be simple and common in daily life, like greetings, eating, family, work, travel.
        
        IMPORTANT: Return ONLY valid JSON array, no other text or explanations.
        Example format: [{{"hindi": "नमस्ते", "english": "Hello"}}, {{"hindi": "धन्यवाद", "english": "Thank you"}}]
        """
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8
            )
            content = response.choices[0].message.content.strip()
            print(f"OpenAI Response: {content}")  # Debug print
            
            import json
            import re
            
            # Extract JSON from the response - look for JSON array pattern
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_content = json_match.group(0)
                # Clean up any markdown formatting
                json_content = json_content.replace('```json', '').replace('```', '').strip()
                sentences = json.loads(json_content)
            else:
                # Fallback: try to extract from markdown blocks
                if '```json' in content:
                    start = content.find('```json') + 7
                    end = content.find('```', start)
                    json_content = content[start:end].strip()
                elif '```' in content:
                    start = content.find('```') + 3
                    end = content.find('```', start)
                    json_content = content[start:end].strip()
                else:
                    json_content = content
                
                sentences = json.loads(json_content)
            if not isinstance(sentences, list):
                sentences = []
        except Exception as ex:
            print(f"Error generating sentences: {ex}")
            sentences = []
        return sentences

    def _translate_to_german(self, english_sentences):
        """Translate English sentences to German."""
        prompt = f"""
        Translate these English sentences to German.
        Return JSON list of objects: [{{"english": "...", "german": "..."}}]
        Sentences: {english_sentences}
        
        IMPORTANT: Return ONLY valid JSON array, no other text or explanations.
        Example format: [{{"english": "Hello", "german": "Hallo"}}, {{"english": "Thank you", "german": "Danke"}}]
        """
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            print(f"German Translation Response: {content}")  # Debug print
            
            import json
            import re
            
            # Extract JSON from the response - look for JSON array pattern
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_content = json_match.group(0)
                # Clean up any markdown formatting
                json_content = json_content.replace('```json', '').replace('```', '').strip()
                translated = json.loads(json_content)
            else:
                # Fallback: try to extract from markdown blocks
                if '```json' in content:
                    start = content.find('```json') + 7
                    end = content.find('```', start)
                    json_content = content[start:end].strip()
                elif '```' in content:
                    start = content.find('```') + 3
                    end = content.find('```', start)
                    json_content = content[start:end].strip()
                else:
                    json_content = content
                
                translated = json.loads(json_content)
            
            if not isinstance(translated, list):
                translated = []
        except Exception as ex:
            print(f"Error translating to German: {ex}")
            translated = []
        return translated

    def generate_daily(self):
        """Main logic to generate and save new unique sentences."""
        today = datetime.date.today()
        
        # Step 1: Get existing sentence hashes to avoid repetition
        existing_english = list(DailySentence.objects.values_list("english", flat=True))
        
        # Step 2: Generate Hindi-English pairs
        hindi_english_pairs = self._generate_hindi_english(existing_english)
        unique_sentences = []

        for s in hindi_english_pairs:
            h = self._hash(s["english"])
            if not DailySentence.objects.filter(hash=h).exists():
                unique_sentences.append(s)
            if len(unique_sentences) == self.count:
                break

        # Step 3: Translate to German
        english_sentences = [s["english"] for s in unique_sentences]
        print(f"Translating {len(english_sentences)} sentences to German...")
        translated = self._translate_to_german(english_sentences)
        print(f"German translations received: {len(translated)}")
        translated_dict = {t["english"]: t["german"] for t in translated}
        print(f"Translation dictionary: {translated_dict}")

        # Step 4: Add German translations to sentences and save to DB
        complete_sentences = []
        for s in unique_sentences:
            english = s["english"]
            german = translated_dict.get(english, "")
            
            # Add German to the sentence object
            complete_sentence = {
                "hindi": s["hindi"],
                "english": english,
                "german": german
            }
            complete_sentences.append(complete_sentence)
            
            # Save to database
            DailySentence.objects.create(
                hindi=s["hindi"],
                english=english,
                german=german,
                hash=self._hash(english)
            )

        return JsonResponse({
            "date": str(today),
            "sentences": complete_sentences,
            "status": "newly_generated",
            "total_sentences_in_db": DailySentence.objects.count()
        })
