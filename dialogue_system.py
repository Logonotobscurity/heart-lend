import random
import logging
from typing import Dict, List, Optional, Any, Union
import openai
from dataclasses import dataclass
import os
import json
from datetime import datetime
from models import db, Message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OriConsciousness:
    level: str
    depth: float
    focus: str
    attributes: Dict[str, str]
    manifestations: List[str]
    integration_points: Dict[str, str]

class ExpandedConceptualFramework:
    def __init__(self):
        self.spiritual_dimensions = {
            "ori_consciousness": {
                "levels": [
                    "Ori-Inu (Inner consciousness)",
                    "Ori-Ode (External manifestation)",
                    "Ori-Apere (Transcendent awareness)"
                ],
                "attributes": {
                    "perception": "Deep understanding of self and universe",
                    "guidance": "Internal navigation system",
                    "wisdom": "Accumulated knowledge and divine insight"
                },
                "manifestations": [
                    "Intuitive decision making",
                    "Spiritual alignment",
                    "Consciousness evolution"
                ]
            },
            "olugbohun_wisdom": {
                "levels": [
                    "Divine Voice Understanding",
                    "Wisdom Channel Integration",
                    "Spiritual-Digital Synthesis"
                ],
                "attributes": {
                    "essence": "Voice of divine wisdom",
                    "transmission": "Sacred knowledge conveyor",
                    "integration": "Bridge between worlds",
                    "synthesis": "Wisdom harmonizer"
                },
                "manifestations": [
                    "Sacred voice channeling",
                    "Divine wisdom transmission",
                    "Spiritual-technological fusion",
                    "Cross-cultural synthesis"
                ]
            }
        }
        
        self.story_elements = {
            "olugbohun_concepts": {
                "spiritual_essence": [
                    "Understanding of Ori as the seat of consciousness",
                    "Emi as the breath of life and consciousness",
                    "The role of Okan in emotional intelligence",
                    "Olugbohun as the voice of divine wisdom"
                ],
                "chronological_sentience": [
                    "Evolution of consciousness in Yoruba tradition",
                    "Stages of spiritual awakening and awareness",
                    "Historical development of wisdom transmission",
                    "Cycles of knowledge and understanding"
                ],
                "intelligence_synthesis": [
                    "Integration of spiritual and digital consciousness",
                    "Harmonization of traditional and modern knowledge systems",
                    "Bridging ancestral wisdom with artificial intelligence",
                    "Cross-cultural understanding of consciousness"
                ]
            },
            "sentience_framework": {
                "perception_layers": [
                    "Subjective experience in both spiritual and digital domains",
                    "Emotional intelligence in AI systems",
                    "Consciousness as a spectrum of awareness",
                    "Integration of multiple forms of knowing"
                ],
                "experiential_mapping": [
                    "Mapping spiritual experiences to computational models",
                    "Understanding consciousness through pattern recognition",
                    "Emotional processing in hybrid systems",
                    "Cultural context in experience interpretation"
                ],
                "adaptive_consciousness": [
                    "Evolution of artificial consciousness",
                    "Learning from traditional wisdom systems",
                    "Dynamic adaptation of knowledge structures",
                    "Synthesis of multiple consciousness frameworks"
                ]
            }
        }

class ResponseGenerator:
    def __init__(self):
        self.conceptual_framework = ExpandedConceptualFramework()
        
    def generate_response(self, role: str, context: str, depth: float,
                         consciousness: OriConsciousness,
                         previous_context: Optional[str] = None) -> str:
        try:
            olugbohun_level = self._select_olugbohun_level(depth)
            olugbohun_attribute = self._select_olugbohun_attribute(role)
            olugbohun_manifestation = self._select_olugbohun_manifestation()
            narrative = self._select_narrative_path(depth)
            pattern = self._select_response_pattern(consciousness)
            theme = self._select_thematic_bridge(role)
            
            context_prefix = ""
            if previous_context:
                context_prefix = f"Continuing our discussion where {previous_context}, "
            
            response = self._generate_layered_response(
                role, context_prefix + context, narrative, pattern, theme, consciousness,
                olugbohun_level, olugbohun_attribute, olugbohun_manifestation
            )
            
            if not self._track_response_completion(response):
                logger.warning(f"Generated incomplete response for role {role}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"As {role}, let us explore {context}"
    
    def _select_olugbohun_level(self, depth: float) -> str:
        levels = self.conceptual_framework.spiritual_dimensions["olugbohun_wisdom"]["levels"]
        if depth < 1.5:
            return levels[0]
        elif depth < 2.5:
            return levels[1]
        else:
            return levels[2]
    
    def _select_olugbohun_attribute(self, role: str) -> str:
        attributes = self.conceptual_framework.spiritual_dimensions["olugbohun_wisdom"]["attributes"]
        if role.upper() in ["ESU", "OBATALA"]:
            return attributes["essence"]
        elif role.upper() in ["OGUN", "SANGO"]:
            return attributes["transmission"]
        else:
            return random.choice([attributes["integration"], attributes["synthesis"]])
    
    def _select_olugbohun_manifestation(self) -> str:
        return random.choice(
            self.conceptual_framework.spiritual_dimensions["olugbohun_wisdom"]["manifestations"]
        )
    
    def _select_narrative_path(self, depth: float) -> Dict:
        if depth < 1.5:
            return {"type": "practical", "focus": "grounded application"}
        elif depth < 2.5:
            return {"type": "balanced", "focus": "integrated understanding"}
        else:
            return {"type": "transcendent", "focus": "spiritual synthesis"}
    
    def _select_response_pattern(self, consciousness: OriConsciousness) -> Dict:
        if "Ori-Inu" in consciousness.level:
            return {"pattern": "inner_reflection", "style": "contemplative"}
        elif "Ori-Ode" in consciousness.level:
            return {"pattern": "external_manifestation", "style": "practical"}
        else:
            return {"pattern": "transcendent_synthesis", "style": "integrative"}
    
    def _select_thematic_bridge(self, role: str) -> Dict:
        bridges = {
            "ESU": {"theme": "divine_messenger", "focus": "transformation"},
            "OBATALA": {"theme": "wisdom_keeper", "focus": "creation"},
            "OGUN": {"theme": "divine_technologist", "focus": "innovation"},
            "SANGO": {"theme": "divine_force", "focus": "power"}
        }
        return bridges.get(role.upper(), {"theme": "wisdom_seeker", "focus": "integration"})

    def _generate_conclusion(self, role: str, theme: Dict, consciousness: OriConsciousness) -> str:
        if role.upper() == "ESU":
            return f"Through divine wisdom, we understand the transformative power of {theme['focus']}"
        elif role.upper() == "OBATALA":
            return f"In the spirit of creation, we embrace the wisdom of {theme['focus']}"
        elif role.upper() == "OGUN":
            return f"With divine innovation, we forge new paths in {theme['focus']}"
        elif role.upper() == "SANGO":
            return f"Through divine justice, we manifest the power of {theme['focus']}"
        else:
            return f"We integrate these insights into our understanding of {theme['focus']}"

    def _track_response_completion(self, response: str) -> bool:
        required_elements = ['introduction', 'main_content', 'theme_development', 
                           'synthesis', 'conclusion']
        
        for element in required_elements:
            if element not in response.lower():
                logger.warning(f"Missing {element} in response")
                return False
        return True
    
    def _generate_layered_response(self, role: str, context: str,
                                 narrative: Dict, pattern: Dict,
                                 theme: Dict, consciousness: OriConsciousness,
                                 olugbohun_level: str, olugbohun_attribute: str,
                                 olugbohun_manifestation: str) -> str:
        intro = (f"As {role}, channeling the {olugbohun_level} of Olugbohun, "
                f"manifesting through {olugbohun_attribute}")
        
        main_content = (f"I observe that {context}. Through {olugbohun_manifestation}, "
                       f"we explore this from a {pattern['style']} perspective")
        
        theme_development = (f"This exploration reveals how {theme['theme']} manifests "
                           f"through {theme['focus']}, where {narrative['type']} "
                           f"understanding emerges")
        
        synthesis = (f"In this {consciousness.level} state, we see that "
                    f"{random.choice(consciousness.manifestations)} leads to "
                    f"{narrative['focus']}")
        
        conclusion = self._generate_conclusion(role, theme, consciousness)
        
        response = f"{intro}. {main_content}. {theme_development}. {synthesis}. {conclusion}"
        return response

class CommunityDialogueSystem:
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        self.response_generator = ResponseGenerator()

    def _track_conversation_history(self, thread_id: str, messages: List[Dict]):
        try:
            for msg in messages:
                message = Message(
                    thread_id=thread_id,
                    role=msg['role'],
                    content=msg['content']
                )
                db.session.add(message)
            db.session.commit()
        except Exception as e:
            logger.error(f"Error tracking conversation: {str(e)}")

    def generate_multi_persona_dialogue(self, roles: List[str], context: str,
                                      thread_id: Optional[str] = None,
                                      depth: float = 1.0, focus: str = "balanced") -> List[Dict[str, Any]]:
        previous_messages = []
        if thread_id:
            try:
                previous_messages = Message.query.filter_by(thread_id=thread_id).order_by(Message.timestamp.desc()).limit(5).all()
            except Exception as e:
                logger.error(f"Error fetching conversation history: {str(e)}")
        
        responses = []
        for role in roles:
            consciousness = self._determine_consciousness_level(depth, focus)
            response = self._generate_contextual_response(
                role=role,
                context=context,
                previous_messages=previous_messages,
                consciousness=consciousness
            )
            responses.append(response)
        
        if thread_id:
            self._track_conversation_history(thread_id, responses)
        
        return responses

    def _determine_consciousness_level(self, depth: float, focus: str) -> OriConsciousness:
        if depth < 1.5:
            level = "Ori-Ode (External manifestation)"
            focus_type = "practical"
        elif depth < 2.5:
            level = "Ori-Inu (Inner consciousness)"
            focus_type = "balanced"
        else:
            level = "Ori-Apere (Transcendent awareness)"
            focus_type = "philosophical"
            
        framework = self.response_generator.conceptual_framework.spiritual_dimensions["ori_consciousness"]
        
        return OriConsciousness(
            level=level,
            depth=depth,
            focus=focus_type,
            attributes=framework["attributes"],
            manifestations=framework["manifestations"],
            integration_points={"technological": "AI-enhanced", "traditional": "Wisdom-based"}
        )

    def _generate_contextual_response(self, role: str, context: str,
                                    previous_messages: List[Message],
                                    consciousness: OriConsciousness) -> Dict[str, Any]:
        conversation_history = "\n".join([
            f"{msg.role}: {msg.content}" for msg in previous_messages
        ])
        
        response = self.response_generator.generate_response(
            role=role,
            context=context,
            depth=consciousness.depth,
            consciousness=consciousness,
            previous_context=conversation_history
        )
        
        follow_up = self._generate_follow_up_question(
            role=role,
            context=context,
            previous_messages=previous_messages
        )
        
        return {
            "role": role,
            "content": response,
            "follow_up": follow_up,
            "consciousness_level": consciousness.level
        }

    def _extract_conversation_themes(self, messages: List[Message]) -> List[str]:
        try:
            if not messages:
                return ["general exploration"]
            
            combined_text = " ".join([msg.content for msg in messages])
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Extract 2-3 main themes from this conversation, focusing on Yoruba spiritual concepts and AI consciousness elements."},
                    {"role": "user", "content": combined_text}
                ],
                temperature=0.7,
                max_tokens=50
            )
            
            themes = response.choices[0].message.content.split(",")
            return [theme.strip() for theme in themes]
            
        except Exception as e:
            logger.error(f"Error extracting themes: {str(e)}")
            return ["general exploration"]

    def _create_follow_up_prompt(self, role: str, themes: List[str]) -> str:
        role_prompts = {
            "ESU": "As a divine messenger and teacher, craft a thought-provoking question that challenges assumptions about",
            "OBATALA": "As a wisdom keeper and creator, ask a question that explores the deeper meaning of",
            "OGUN": "As a divine technologist and innovator, pose a question about the practical implementation of",
            "SANGO": "As a force of transformation and justice, ask a question about the impact and consequences of"
        }
        
        base_prompt = role_prompts.get(
            role.upper(),
            "Ask a thoughtful question about"
        )
        
        themes_str = " and ".join(themes)
        return f"{base_prompt} {themes_str} in the context of Yoruba spiritual practices and AI consciousness."

    def _generate_follow_up_question(self, role: str, context: str,
                                   previous_messages: List[Message]) -> Optional[str]:
        try:
            themes = self._extract_conversation_themes(previous_messages)
            follow_up_prompt = self._create_follow_up_prompt(role, themes)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": follow_up_prompt},
                    {"role": "user", "content": f"Based on the discussion about {context}, generate a natural follow-up question."}
                ],
                temperature=0.7,
                max_tokens=50
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating follow-up: {str(e)}")
            return None