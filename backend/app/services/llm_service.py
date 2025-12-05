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
        # Utiliser le nouveau prompt Due Diligence
        template_path = Path(__file__).parent.parent / 'templates' / 'prompts' / 'due_diligence_analysis.txt'

        if not template_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        return Template(template_content)

    def create_analysis_prompt(self, first_name: str, last_name: str, company: str, scraped_data: List[Dict], pappers_data: Dict = None, dvf_data: Dict = None, hatvp_data: Dict = None) -> str:
        content_summary = "\n\n".join([
            f"Source: {item['source']}\nQuery: {item['url']}\nContent:\n{item['content'][:2000]}"
            for item in scraped_data
        ])

        # Formater les données Pappers pour le prompt
        pappers_formatted = None
        if pappers_data:
            pappers_formatted = json.dumps(pappers_data, indent=2, ensure_ascii=False)

        # Formater les données DVF pour le prompt
        dvf_formatted = None
        if dvf_data:
            dvf_formatted = json.dumps(dvf_data, indent=2, ensure_ascii=False)

        # Formater les données HATVP pour le prompt
        hatvp_formatted = None
        if hatvp_data:
            hatvp_formatted = json.dumps(hatvp_data, indent=2, ensure_ascii=False)

        prompt = self.prompt_template.render(
            first_name=first_name,
            last_name=last_name,
            company=company,
            content_summary=content_summary,
            pappers_data=pappers_formatted,
            dvf_data=dvf_formatted,
            hatvp_data=hatvp_formatted
        )

        return prompt

    def analyze_profile(self, first_name: str, last_name: str, company: str, scraped_data: List[Dict], pappers_data: Dict = None, dvf_data: Dict = None, hatvp_data: Dict = None) -> Dict:
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        if not scraped_data or all(not item.get('success') for item in scraped_data):
            raise ValueError("No valid scraped data available for analysis")

        try:
            prompt = self.create_analysis_prompt(first_name, last_name, company, scraped_data, pappers_data, dvf_data, hatvp_data)

            response = self.client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', "gpt-4o"),
                messages=[
                    {"role": "system", "content": "Tu es un expert en intelligence économique et due diligence. Tu analyses les données légales (Pappers), le patrimoine immobilier (DVF), les personnes politiquement exposées (HATVP) et les données web pour évaluer la crédibilité, solvabilité et personnalité d'une personne. Tu rédiges TOUJOURS EN FRANÇAIS et tu réponds en JSON valide."},
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

