import os
import json
from typing import Dict, List
from pathlib import Path
from jinja2 import Template
from openai import OpenAI

class LLMService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> Template:
        template_path = Path(__file__).parent.parent / 'templates' / 'prompts' / 'profile_analysis.txt'

        if not template_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        return Template(template_content)

    def create_analysis_prompt(self, first_name: str, last_name: str, company: str, scraped_data: List[Dict]) -> str:
        content_summary = "\n\n".join([
            f"Source: {item['source']}\nQuery: {item['url']}\nContent:\n{item['content'][:2000]}"
            for item in scraped_data
        ])

        prompt = self.prompt_template.render(
            first_name=first_name,
            last_name=last_name,
            company=company,
            content_summary=content_summary
        )

        return prompt

    def analyze_profile(self, first_name: str, last_name: str, company: str, scraped_data: List[Dict]) -> Dict:
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        if not scraped_data or all(not item.get('success') for item in scraped_data):
            raise ValueError("No valid scraped data available for analysis")

        try:
            prompt = self.create_analysis_prompt(first_name, last_name, company, scraped_data)

            response = self.client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', "gpt-4o"),
                messages=[
                    {"role": "system", "content": "Tu es un assistant expert en analyse de profils professionnels pour un cabinet de conseil français. Tu rédiges TOUJOURS tes analyses EN FRANÇAIS et tu réponds en JSON valide."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise Exception(f"Failed to analyze profile with OpenAI: {str(e)}")

