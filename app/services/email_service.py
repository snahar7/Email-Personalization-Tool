from typing import Optional, Dict
import openai
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.models import Prospect, Company, EmailTemplate
from app.schemas.schemas import EmailTemplateCreate

class EmailPersonalizationService:
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key

    def generate_personalized_email(
        self,
        prospect: Prospect,
        company: Company,
        template: EmailTemplate,
        additional_context: Optional[Dict] = None
    ) -> str:
        """
        Generate a personalized email using OpenAI's API
        """
        # Prepare context for the AI
        context = {
            "prospect": {
                "name": prospect.name,
                "position": prospect.position,
                "company": company.name,
                "industry": company.industry
            },
            "company": {
                "name": company.name,
                "industry": company.industry,
                "description": company.description,
                "key_insights": company.key_insights,
                "market_position": company.market_position
            },
            "template": {
                "subject": template.subject,
                "body": template.body
            }
        }

        if additional_context:
            context.update(additional_context)

        # Create the prompt for OpenAI
        prompt = f"""
        Generate a personalized email based on the following context:
        
        Prospect Information:
        - Name: {context['prospect']['name']}
        - Position: {context['prospect']['position']}
        - Company: {context['prospect']['company']}
        - Industry: {context['prospect']['industry']}
        
        Company Information:
        - Name: {context['company']['name']}
        - Industry: {context['company']['industry']}
        - Description: {context['company']['description']}
        - Key Insights: {context['company']['key_insights']}
        - Market Position: {context['company']['market_position']}
        
        Base Template:
        Subject: {context['template']['subject']}
        Body: {context['template']['body']}
        
        Please generate a personalized version of this email that:
        1. References specific details about the prospect's company and role
        2. Includes relevant industry insights
        3. Maintains a professional yet conversational tone
        4. Focuses on value proposition relevant to their position
        5. Includes a clear call to action
        
        Format the response as:
        SUBJECT: [personalized subject]
        BODY: [personalized body]
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert sales email writer who creates highly personalized and effective outreach emails."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            # Parse the response
            email_content = response.choices[0].message.content
            subject, body = self._parse_email_content(email_content)

            return {
                "subject": subject,
                "body": body,
                "generated_at": datetime.utcnow()
            }

        except Exception as e:
            raise Exception(f"Failed to generate personalized email: {str(e)}")

    def _parse_email_content(self, content: str) -> tuple[str, str]:
        """
        Parse the AI-generated email content into subject and body
        """
        lines = content.split('\n')
        subject = ""
        body = []
        body_started = False

        for line in lines:
            if line.startswith("SUBJECT:"):
                subject = line.replace("SUBJECT:", "").strip()
            elif line.startswith("BODY:"):
                body_started = True
            elif body_started and line.strip():
                body.append(line)

        return subject, '\n'.join(body)

    def create_template_variants(
        self,
        base_template: EmailTemplate,
        num_variants: int = 2
    ) -> list[EmailTemplateCreate]:
        """
        Create A/B testing variants of an email template
        """
        variants = []
        for i in range(num_variants):
            prompt = f"""
            Create a variant of this email template for A/B testing:
            
            Original Subject: {base_template.subject}
            Original Body: {base_template.body}
            
            Create a variant that:
            1. Maintains the same core message
            2. Uses different wording and structure
            3. Tests different value propositions
            4. Has a different call to action
            
            Format the response as:
            SUBJECT: [variant subject]
            BODY: [variant body]
            """

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert in email marketing and A/B testing."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=1000
                )

                email_content = response.choices[0].message.content
                subject, body = self._parse_email_content(email_content)

                variants.append(EmailTemplateCreate(
                    name=f"{base_template.name} - Variant {i+1}",
                    subject=subject,
                    body=body,
                    company_id=base_template.company_id,
                    variant=f"variant_{i+1}"
                ))

            except Exception as e:
                raise Exception(f"Failed to create template variant: {str(e)}")

        return variants 