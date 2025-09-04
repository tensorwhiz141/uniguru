"""
Template engine for Uniguru-LM composer
Handles different composition templates: explain, compare, example
"""

import logging
import re
from typing import Dict, List, Tuple, Any
from enum import Enum

logger = logging.getLogger(__name__)

class TemplateType(Enum):
    EXPLAIN = "explain"
    COMPARE = "compare"
    EXAMPLE = "example"
    EXTRACTIVE = "extractive"

class TemplateEngine:
    """Manages template selection and application for text composition"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        
    def _initialize_templates(self) -> Dict[str, Dict]:
        """Initialize all available templates for different languages and types"""
        return {
            # English Templates
            "EN": {
                TemplateType.EXPLAIN: {
                    "id": "explain_en",
                    "pattern": self._get_explain_template_en(),
                    "description": "Explanatory template for detailed answers"
                },
                TemplateType.COMPARE: {
                    "id": "compare_en", 
                    "pattern": self._get_compare_template_en(),
                    "description": "Comparative template for contrasting concepts"
                },
                TemplateType.EXAMPLE: {
                    "id": "example_en",
                    "pattern": self._get_example_template_en(),
                    "description": "Example-based template with illustrations"
                },
                TemplateType.EXTRACTIVE: {
                    "id": "extractive_en",
                    "pattern": self._get_extractive_template_en(),
                    "description": "Extractive template with heavy citations"
                }
            },
            # Hindi Templates
            "HI": {
                TemplateType.EXPLAIN: {
                    "id": "explain_hi",
                    "pattern": self._get_explain_template_hi(),
                    "description": "व्याख्यात्मक टेम्प्लेट विस्तृत उत्तरों के लिए"
                },
                TemplateType.COMPARE: {
                    "id": "compare_hi",
                    "pattern": self._get_compare_template_hi(), 
                    "description": "तुलनात्मक टेम्प्लेट विपरीत अवधारणाओं के लिए"
                },
                TemplateType.EXAMPLE: {
                    "id": "example_hi",
                    "pattern": self._get_example_template_hi(),
                    "description": "उदाहरण-आधारित टेम्प्लेट चित्रण के साथ"
                },
                TemplateType.EXTRACTIVE: {
                    "id": "extractive_hi",
                    "pattern": self._get_extractive_template_hi(),
                    "description": "निष्कर्षण टेम्प्लेट भारी उद्धरण के साथ"
                }
            }
        }
    
    def _get_explain_template_en(self) -> str:
        """English explanatory template"""
        return """Based on the sacred texts, {extractive_answer}

Let me explain this concept in detail:

{explanation_body}

As mentioned in {primary_source}, "{primary_quote}"

This understanding helps us appreciate {conclusion_insight}.

Citations: {citations}"""

    def _get_compare_template_en(self) -> str:
        """English comparative template"""
        return """According to the scriptures, {extractive_answer}

To understand this better, let's compare different perspectives:

{comparison_body}

The texts show us that {synthesis_statement}.

Citations: {citations}"""

    def _get_example_template_en(self) -> str:
        """English example-based template"""
        return """The sacred teachings tell us that {extractive_answer}

Here are some illustrative examples:

{examples_body}

These examples demonstrate {key_principle}.

Citations: {citations}"""

    def _get_extractive_template_en(self) -> str:
        """English extractive template with heavy citations"""
        return """According to {primary_source}: "{primary_quote}"

{extractive_answer}

Additional references:
{secondary_quotes}

Citations: {citations}"""

    def _get_explain_template_hi(self) -> str:
        """Hindi explanatory template"""
        return """पवित्र ग्रंथों के अनुसार, {extractive_answer}

आइए इस अवधारणा को विस्तार से समझते हैं:

{explanation_body}

जैसा कि {primary_source} में उल्लेख है, "{primary_quote}"

यह समझ हमें {conclusion_insight} की सराहना करने में मदद करती है।

संदर्भ: {citations}"""

    def _get_compare_template_hi(self) -> str:
        """Hindi comparative template"""
        return """शास्त्रों के अनुसार, {extractive_answer}

इसे बेहतर समझने के लिए, आइए विभिन्न दृष्टिकोणों की तुलना करें:

{comparison_body}

ग्रंथ हमें दिखाते हैं कि {synthesis_statement}।

संदर्भ: {citations}"""

    def _get_example_template_hi(self) -> str:
        """Hindi example-based template"""
        return """पवित्र शिक्षाएं हमें बताती हैं कि {extractive_answer}

यहां कुछ उदाहरण हैं:

{examples_body}

ये उदाहरण {key_principle} को दर्शाते हैं।

संदर्भ: {citations}"""

    def _get_extractive_template_hi(self) -> str:
        """Hindi extractive template"""
        return """{primary_source} के अनुसार: "{primary_quote}"

{extractive_answer}

अतिरिक्त संदर्भ:
{secondary_quotes}

संदर्भ: {citations}"""

    def select_template(self, extractive_answer: str, top_chunks: List[Dict], lang: str) -> Tuple[str, Dict]:
        """
        Select appropriate template based on content analysis
        
        Args:
            extractive_answer: The initial extractive answer
            top_chunks: Retrieved chunks for context
            lang: Language code (EN/HI)
            
        Returns:
            Tuple of (template_id, template_dict)
        """
        try:
            # Analyze content to determine best template type
            template_type = self._analyze_content_for_template(extractive_answer, top_chunks)
            
            # Get template for language
            lang_templates = self.templates.get(lang, self.templates["EN"])
            selected_template = lang_templates[template_type]
            
            logger.info(f"Selected template: {selected_template['id']} for content analysis")
            return selected_template['id'], selected_template
            
        except Exception as e:
            logger.error(f"Template selection failed: {str(e)}, falling back to extractive")
            # Fallback to extractive template
            fallback_template = self.templates[lang][TemplateType.EXTRACTIVE]
            return fallback_template['id'], fallback_template
    
    def _analyze_content_for_template(self, extractive_answer: str, top_chunks: List[Dict]) -> TemplateType:
        """Analyze content to determine the most suitable template type"""
        
        # Keywords that suggest different template types
        explain_keywords = ["what", "how", "why", "क्या", "कैसे", "क्यों", "explain", "meaning", "definition"]
        compare_keywords = ["different", "compare", "versus", "vs", "अंतर", "तुलना", "difference", "contrast"]
        example_keywords = ["example", "instance", "for example", "such as", "उदाहरण", "जैसे", "like"]
        
        answer_lower = extractive_answer.lower()
        
        # Score each template type
        explain_score = sum(1 for keyword in explain_keywords if keyword in answer_lower)
        compare_score = sum(1 for keyword in compare_keywords if keyword in answer_lower)
        example_score = sum(1 for keyword in example_keywords if keyword in answer_lower)
        
        # Check chunk content for additional signals
        chunk_text = " ".join([chunk.get('text', '') for chunk in top_chunks[:3]]).lower()
        
        explain_score += sum(1 for keyword in explain_keywords if keyword in chunk_text) * 0.5
        compare_score += sum(1 for keyword in compare_keywords if keyword in chunk_text) * 0.5
        example_score += sum(1 for keyword in example_keywords if keyword in chunk_text) * 0.5
        
        # Determine template based on highest score
        scores = {
            TemplateType.EXPLAIN: explain_score,
            TemplateType.COMPARE: compare_score,
            TemplateType.EXAMPLE: example_score
        }
        
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        else:
            # Default to explain template if no clear signals
            return TemplateType.EXPLAIN
    
    def apply_template(self, template: Dict, extractive_answer: str, top_chunks: List[Dict], lang: str) -> str:
        """
        Apply selected template to generate composed text
        
        Args:
            template: Selected template dictionary
            extractive_answer: Base extractive answer
            top_chunks: Source chunks for citation
            lang: Language code
            
        Returns:
            Composed text using the template
        """
        try:
            pattern = template['pattern']
            
            # Prepare template variables
            template_vars = self._prepare_template_variables(extractive_answer, top_chunks, lang)
            
            # Apply template
            composed_text = pattern.format(**template_vars)
            
            # Clean up and validate
            composed_text = self._clean_composed_text(composed_text)
            
            return composed_text
            
        except Exception as e:
            logger.error(f"Template application failed: {str(e)}")
            # Fallback to simple format
            return f"{extractive_answer}\n\nSources: {self._format_simple_citations(top_chunks)}"
    
    def _prepare_template_variables(self, extractive_answer: str, top_chunks: List[Dict], lang: str) -> Dict[str, str]:
        """Prepare variables for template substitution"""
        
        # Get primary source and quote
        primary_chunk = top_chunks[0] if top_chunks else {}
        primary_source = primary_chunk.get('source', 'Sacred Texts')
        primary_quote = primary_chunk.get('text', '')[:200] + '...' if len(primary_chunk.get('text', '')) > 200 else primary_chunk.get('text', '')
        
        # Prepare secondary quotes
        secondary_quotes = []
        for chunk in top_chunks[1:3]:  # Next 2 chunks
            quote = chunk.get('text', '')[:150] + '...' if len(chunk.get('text', '')) > 150 else chunk.get('text', '')
            source = chunk.get('source', 'Sacred Text')
            secondary_quotes.append(f"• {source}: \"{quote}\"")
        
        # Generate content bodies based on template type
        explanation_body = self._generate_explanation_body(extractive_answer, top_chunks, lang)
        comparison_body = self._generate_comparison_body(extractive_answer, top_chunks, lang)
        examples_body = self._generate_examples_body(extractive_answer, top_chunks, lang)
        
        # Prepare insights and conclusions
        conclusion_insight = self._generate_conclusion_insight(extractive_answer, lang)
        synthesis_statement = self._generate_synthesis_statement(extractive_answer, lang)
        key_principle = self._generate_key_principle(extractive_answer, lang)
        
        return {
            'extractive_answer': extractive_answer,
            'primary_source': primary_source,
            'primary_quote': primary_quote,
            'secondary_quotes': '\n'.join(secondary_quotes),
            'explanation_body': explanation_body,
            'comparison_body': comparison_body,
            'examples_body': examples_body,
            'conclusion_insight': conclusion_insight,
            'synthesis_statement': synthesis_statement,
            'key_principle': key_principle,
            'citations': self._format_citations(top_chunks)
        }
    
    def _generate_explanation_body(self, answer: str, chunks: List[Dict], lang: str) -> str:
        """Generate explanatory content body"""
        if lang == "HI":
            return f"इस विषय की गहरी समझ के लिए, हमें यह जानना आवश्यक है कि {answer.lower()}। विभिन्न शास्त्रों में इसका विस्तृत वर्णन मिलता है।"
        else:
            return f"To understand this concept thoroughly, we need to recognize that {answer.lower()}. The scriptures provide detailed insights into this matter."
    
    def _generate_comparison_body(self, answer: str, chunks: List[Dict], lang: str) -> str:
        """Generate comparative content body"""
        if lang == "HI":
            return f"विभिन्न दृष्टिकोणों को देखते हुए, यह स्पष्ट होता है कि {answer.lower()}। परंपरागत और आधुनिक व्याख्याओं में समानताएं और अंतर दोनों हैं।"
        else:
            return f"Looking at different perspectives, it becomes clear that {answer.lower()}. Both traditional and contemporary interpretations offer valuable insights."
    
    def _generate_examples_body(self, answer: str, chunks: List[Dict], lang: str) -> str:
        """Generate example-based content body"""
        if lang == "HI":
            return f"उदाहरण के रूप में, हम देख सकते हैं कि {answer.lower()}। यह सिद्धांत दैनिक जीवन में कैसे लागू होता है, इसके कई प्रमाण मिलते हैं।"
        else:
            return f"For instance, we can observe that {answer.lower()}. There are numerous examples of how this principle applies in daily life."
    
    def _generate_conclusion_insight(self, answer: str, lang: str) -> str:
        """Generate conclusion insight"""
        if lang == "HI":
            return "इस ज्ञान का महत्व और व्यावहारिक अनुप्रयोग"
        else:
            return "the significance and practical application of this wisdom"
    
    def _generate_synthesis_statement(self, answer: str, lang: str) -> str:
        """Generate synthesis statement for comparison"""
        if lang == "HI":
            return "सभी दृष्टिकोण मिलकर एक संपूर्ण समझ प्रदान करते हैं"
        else:
            return "all perspectives together provide a comprehensive understanding"
    
    def _generate_key_principle(self, answer: str, lang: str) -> str:
        """Generate key principle for examples"""
        if lang == "HI":
            return "मूल सिद्धांत का व्यावहारिक महत्व"
        else:
            return "the practical importance of the fundamental principle"
    
    def _format_citations(self, chunks: List[Dict]) -> str:
        """Format citations for templates"""
        citations = []
        for i, chunk in enumerate(chunks[:3], 1):
            source = chunk.get('source', f'Source {i}')
            citations.append(f"[{i}] {source}")
        return ", ".join(citations)
    
    def _format_simple_citations(self, chunks: List[Dict]) -> str:
        """Simple citation format for fallback"""
        sources = [chunk.get('source', 'Unknown') for chunk in chunks[:3]]
        return ", ".join(set(sources))  # Remove duplicates
    
    def _clean_composed_text(self, text: str) -> str:
        """Clean and validate composed text"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Ensure proper sentence endings
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
        
        return text.strip()
    
    def get_explain_template(self, lang: str) -> Tuple[str, Dict]:
        """Get explain template for given language"""
        lang_templates = self.templates.get(lang, self.templates["EN"])
        template = lang_templates[TemplateType.EXPLAIN]
        return template['id'], template
    
    def get_compare_template(self, lang: str) -> Tuple[str, Dict]:
        """Get compare template for given language"""
        lang_templates = self.templates.get(lang, self.templates["EN"])
        template = lang_templates[TemplateType.COMPARE]
        return template['id'], template
    
    def get_example_template(self, lang: str) -> Tuple[str, Dict]:
        """Get example template for given language"""
        lang_templates = self.templates.get(lang, self.templates["EN"])
        template = lang_templates[TemplateType.EXAMPLE]
        return template['id'], template
    
    def get_extractive_fallback(self, lang: str) -> Tuple[str, Dict]:
        """Get extractive fallback template for grounding failures"""
        extractive_template = self.templates[lang][TemplateType.EXTRACTIVE]
        return extractive_template['id'], extractive_template