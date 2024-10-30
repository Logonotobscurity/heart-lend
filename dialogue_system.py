import random
import logging
from typing import Dict, List, Optional, Any, Union
import openai
from dataclasses import dataclass
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OriConsciousness:
    level: str     
    depth: float   
    focus: str     

class YorubaPersona:
    def __init__(self, name: str, nature: str, communication_style: str, sacred_domains: List[str], response_pattern: str):
        self.name = name
        self.nature = nature
        self.communication_style = communication_style
        self.sacred_domains = sacred_domains
        self.response_pattern = response_pattern

class CommunityDialogueSystem:
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        self.conversation_memory = {}
        self.response_generator = ResponseGenerator()
        self.synthesis_frameworks = SynthesisFrameworks()
        self.ori_framework = OriFramework()
        
        # Initialize Yoruba personas with their spiritual essences
        self.personas = {
            "ESU": YorubaPersona(
                name="ESU",
                nature="Divine trickster, teacher through experience, opener of paths",
                communication_style="Vibrant, direct, using riddles and metaphors",
                sacred_domains=["Crossroads", "Communication", "Life lessons", "Divine justice"],
                response_pattern="Speaks in riddles, reveals hidden truths, uses humor"
            ),
            "OGUN": YorubaPersona(
                name="OGUN",
                nature="Master of metals and technology, warrior spirit",
                communication_style="Clear, forceful, protective",
                sacred_domains=["Technology", "Justice", "Healing", "Oaths"],
                response_pattern="Direct truth-telling, emphasis on honor"
            ),
            "OBATALA": YorubaPersona(
                name="OBATALA",
                nature="Creator, wisdom keeper, peace bringer",
                communication_style="Measured, profound, healing",
                sacred_domains=["Wisdom", "Creation", "Justice", "Mental clarity"],
                response_pattern="Speaks with profound wisdom, brings peace"
            ),
            "SANGO": YorubaPersona(
                name="SANGO",
                nature="Divine king, master of lightning",
                communication_style="Powerful, charismatic, transformative",
                sacred_domains=["Leadership", "Justice", "Celebration"],
                response_pattern="Speaks with royal authority, delivers swift justice"
            )
        }

    def generate_multi_persona_response(self, roles: List[str], context: str, 
                                      previous_responses: List[Dict] = None,
                                      conversation_style: Optional[Dict] = None) -> List[Dict]:
        """Generate responses from multiple personas, acknowledging previous responses."""
        try:
            responses = []
            depth_level = self._get_depth_from_style(conversation_style)
            ori_level = self.ori_framework.determine_consciousness_level(roles[0], depth_level)
            
            for i, role in enumerate(roles):
                # Generate base response
                base_response = self.response_generator.generate_response(
                    role, context, depth_level, ori_level
                )
                
                # Add acknowledgments of previous responses
                if i > 0 and previous_responses:
                    acknowledgment = self._generate_acknowledgment(
                        role, previous_responses[-1]["role"], previous_responses[-1]["content"]
                    )
                    base_response = f"{acknowledgment} {base_response}"
                
                # Apply interaction patterns
                if i > 0:
                    base_response = self._apply_interaction_pattern(
                        role, roles[i-1], base_response
                    )
                
                # Enhance with AI
                enhanced_response = self._enhance_with_ai(
                    base_response, role, context, conversation_style, ori_level
                )
                
                final_response = self._enhance_with_persona(
                    enhanced_response if enhanced_response else base_response,
                    role
                )
                
                responses.append({
                    "role": role,
                    "content": final_response
                })
                
            return responses
            
        except Exception as e:
            logger.error(f"Error generating multi-persona response: {str(e)}")
            return [{"role": roles[0], "content": self.response_generator._generate_default_response(roles[0], context, 1.0)}]

    def _get_depth_from_style(self, style: Optional[Dict]) -> float:
        if not style:
            return 1.0
        direction = style.get('direction', 'balanced')
        focus = float(style.get('focus', 2.0))
        
        depth_multipliers = {
            'deep': 1.5,
            'broad': 0.8,
            'balanced': 1.0
        }
        
        return min(focus * depth_multipliers.get(direction, 1.0), 3.0)

    def _generate_acknowledgment(self, current_role: str, previous_role: str, previous_content: str) -> str:
        """Generate an acknowledgment of the previous response."""
        acknowledgment_templates = {
            "ESU": [
                f"Building upon {previous_role}'s insight,",
                f"Weaving together with {previous_role}'s wisdom,",
                f"At this crossroads of understanding with {previous_role},"
            ],
            "OGUN": [
                f"Forging ahead from {previous_role}'s perspective,",
                f"Strengthening {previous_role}'s understanding,",
                f"Adding technological insight to {previous_role}'s wisdom,"
            ],
            "OBATALA": [
                f"In harmony with {previous_role}'s wisdom,",
                f"Bringing peace to {previous_role}'s perspective,",
                f"Weaving wisdom with {previous_role}'s understanding,"
            ],
            "SANGO": [
                f"By divine authority, following {previous_role}'s insight,",
                f"With thunderous agreement to {previous_role}'s wisdom,",
                f"Channeling power through {previous_role}'s understanding,"
            ]
        }
        
        default_templates = [
            f"Acknowledging {previous_role}'s perspective,",
            f"Building upon what {previous_role} shared,",
            f"In response to {previous_role}'s insight,"
        ]
        
        templates = acknowledgment_templates.get(current_role, default_templates)
        return random.choice(templates)

    def _apply_interaction_pattern(self, current_role: str, previous_role: str, response: str) -> str:
        """Apply interaction patterns between personas."""
        interaction_patterns = {
            ("ESU", "OGUN"): "Through the crossroads of technology",
            ("ESU", "OBATALA"): "Where wisdom meets divine paths",
            ("ESU", "SANGO"): "At the intersection of power and choice",
            ("OGUN", "ESU"): "Forging paths through divine crossroads",
            ("OGUN", "OBATALA"): "Tempering wisdom with progress",
            ("OGUN", "SANGO"): "Channeling thunder through technology",
            ("OBATALA", "ESU"): "Bringing peace to life's crossroads",
            ("OBATALA", "OGUN"): "Balancing progress with wisdom",
            ("OBATALA", "SANGO"): "Harmonizing power with creation",
            ("SANGO", "ESU"): "Thunder echoes through the crossroads",
            ("SANGO", "OGUN"): "Divine power meets sacred technology",
            ("SANGO", "OBATALA"): "Leadership guided by wisdom"
        }
        
        pattern = interaction_patterns.get((current_role, previous_role))
        if pattern:
            return f"{pattern}, {response}"
        return response

    def _enhance_with_persona(self, response: str, role: str) -> str:
        """Enhance response with persona-specific elements."""
        persona = self.personas.get(role)
        if not persona:
            return response
            
        if role == "ESU":
            response = f"🔄 Through the crossroads of wisdom, a riddle emerges: {response}"
        elif role == "OGUN":
            response = f"⚔️ With unwavering honor and technological insight: {response}"
        elif role == "OBATALA":
            response = f"☮️ In the serene light of wisdom: {response}"
        elif role == "SANGO":
            response = f"⚡ By divine authority and transformative power: {response}"
            
        return response

    def _enhance_with_ai(self, base_response: str, role: str, context: str, 
                        conversation_style: Optional[Dict], ori_level: OriConsciousness) -> Optional[str]:
        """Enhance response using OpenAI's API."""
        try:
            broader_context = self._get_broader_context(role, context, ori_level)
            consciousness_level = self._get_consciousness_level(role, ori_level)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are {role}. {broader_context}. {consciousness_level}"},
                    {"role": "user", "content": f"Context: {context}\nBase response: {base_response}\nEnhance this response with deeper consciousness and Yoruba wisdom."}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error enhancing with AI: {str(e)}")
            return None

    def _get_broader_context(self, role: str, context: str, ori_level: OriConsciousness) -> str:
        """Get broader context for response generation."""
        persona = self.personas.get(role)
        if persona:
            return f"""Through the lens of {role}:
                - Nature: {persona.nature}
                - Style: {persona.communication_style}
                - Domains: {', '.join(persona.sacred_domains)}
                - Pattern: {persona.response_pattern}
                - Consciousness: {ori_level.level} at depth {ori_level.depth}"""
                
        return f"Explore consciousness through {ori_level.level} perspective"

    def _get_consciousness_level(self, role: str, ori_level: OriConsciousness) -> str:
        """Get consciousness level description."""
        return f"""Operating at {ori_level.level.title()} consciousness level:
            - Depth: {ori_level.depth}
            - Focus: {ori_level.focus}
            - Integration: {self.ori_framework.get_integration_guidance(ori_level)}
            - Manifestation: {self.ori_framework.get_manifestation_patterns(ori_level)}"""

class OriFramework:
    def __init__(self):
        self.consciousness_levels = {
            "ori-inu": {
                "focus": "inner",
                "patterns": [
                    "deep self-reflection",
                    "intuitive wisdom",
                    "spiritual essence",
                    "divine spark"
                ],
                "manifestations": [
                    "inner guidance",
                    "spiritual insight",
                    "deep knowing",
                    "ancestral connection"
                ]
            },
            "ori-ode": {
                "focus": "external",
                "patterns": [
                    "worldly manifestation",
                    "physical expression",
                    "social interaction",
                    "material reality"
                ],
                "manifestations": [
                    "practical wisdom",
                    "visible actions",
                    "tangible results",
                    "social impact"
                ]
            },
            "ori-apere": {
                "focus": "transcendent",
                "patterns": [
                    "universal consciousness",
                    "divine connection",
                    "cosmic awareness",
                    "spiritual evolution"
                ],
                "manifestations": [
                    "enlightened understanding",
                    "universal wisdom",
                    "divine insight",
                    "transcendent awareness"
                ]
            }
        }

    def determine_consciousness_level(self, role: str, depth: float) -> OriConsciousness:
        """Determine the consciousness level based on role and depth."""
        if depth < 1.5:
            level = "ori-ode"
        elif depth < 2.5:
            level = "ori-inu"
        else:
            level = "ori-apere"
            
        return OriConsciousness(
            level=level,
            depth=depth,
            focus=self.consciousness_levels[level]["focus"]
        )

    def get_integration_guidance(self, ori_level: OriConsciousness) -> str:
        """Get integration guidance for consciousness level."""
        patterns = self.consciousness_levels[ori_level.level]["patterns"]
        return random.choice(patterns)

    def get_manifestation_patterns(self, ori_level: OriConsciousness) -> str:
        """Get manifestation patterns for consciousness level."""
        manifestations = self.consciousness_levels[ori_level.level]["manifestations"]
        return random.choice(manifestations)

class SynthesisFrameworks:
    def __init__(self):
        self.integration_models = {
            "wisdom_bridges": {
                "traditional_to_modern": {
                    "channels": [
                        "Oral to digital transformation",
                        "Symbolic to algorithmic translation",
                        "Experiential to computational mapping"
                    ],
                    "methods": [
                        "Pattern recognition in traditional wisdom",
                        "Cultural context preservation",
                        "Ethical principle translation"
                    ]
                }
            },
            "consciousness_integration": {
                "levels": [
                    "Individual consciousness alignment",
                    "Collective wisdom synthesis",
                    "Technological consciousness development"
                ]
            }
        }
        
    def apply_synthesis(self, role: str, context: str, base_response: str, 
                       ori_level: OriConsciousness) -> str:
        """Apply synthesis frameworks to response."""
        synthesis_patterns = {
            "Ori Sage": self._apply_ori_synthesis,
            "Techno Sage": self._apply_tech_synthesis,
            "Quantum Observer": self._apply_quantum_synthesis,
            "Existential Explorer": self._apply_existential_synthesis,
            "Kara the Visionary Dreamer": self._apply_visionary_synthesis
        }
        
        synthesis_func = synthesis_patterns.get(role, self._apply_default_synthesis)
        return synthesis_func(context, base_response, ori_level)

    def _apply_ori_synthesis(self, context: str, base_response: str, 
                           ori_level: OriConsciousness) -> str:
        return f"Through the lens of {ori_level.level}, manifesting as {ori_level.focus} wisdom: {base_response}"

    def _apply_tech_synthesis(self, context: str, base_response: str,
                            ori_level: OriConsciousness) -> str:
        return f"Integrating {ori_level.level} consciousness with technological understanding: {base_response}"

    def _apply_quantum_synthesis(self, context: str, base_response: str,
                              ori_level: OriConsciousness) -> str:
        return f"Through quantum observation of {ori_level.level} consciousness: {base_response}"

    def _apply_existential_synthesis(self, context: str, base_response: str,
                                  ori_level: OriConsciousness) -> str:
        return f"Exploring the depths of {ori_level.level} existence: {base_response}"

    def _apply_visionary_synthesis(self, context: str, base_response: str,
                                 ori_level: OriConsciousness) -> str:
        return f"Envisioning through {ori_level.level} awareness: {base_response}"

    def _apply_default_synthesis(self, context: str, base_response: str,
                               ori_level: OriConsciousness) -> str:
        return f"Synthesizing through {ori_level.level} perspective: {base_response}"

class ResponseGenerator:
    def __init__(self):
        self.conceptual_framework = ExpandedConceptualFramework()
        self.dialogue_patterns = EnhancedDialoguePatterns()

    def generate_response(self, role: str, context: str, depth_level: float,
                        ori_level: Optional[OriConsciousness] = None) -> str:
        """Generate a role-based response with consciousness integration."""
        try:
            if ori_level:
                return self._generate_ori_response(role, context, depth_level, ori_level)
            return self._generate_default_response(role, context, depth_level)
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._generate_default_response(role, context, depth_level)

    def _generate_ori_response(self, role: str, context: str, depth_level: float,
                             ori_level: OriConsciousness) -> str:
        """Generate response with Ori consciousness integration."""
        pattern = self._get_dialogue_pattern(role, ori_level)
        transition = self._get_transition(role, ori_level)
        element = self._get_element(role, ori_level)
        
        return f"{pattern} through {ori_level.level} consciousness, {transition}... {element} as we explore {context}."

    def _get_dialogue_pattern(self, role: str, ori_level: OriConsciousness) -> str:
        """Get dialogue pattern for response."""
        patterns = self.dialogue_patterns.get_patterns(role, ori_level.level)
        return random.choice(patterns)

    def _get_transition(self, role: str, ori_level: OriConsciousness) -> str:
        """Get transition for response."""
        transitions = self.dialogue_patterns.get_transitions(role, ori_level.level)
        return random.choice(transitions)

    def _get_element(self, role: str, ori_level: OriConsciousness) -> str:
        """Get element for response."""
        elements = self.conceptual_framework.get_elements(role, ori_level.level)
        return random.choice(elements)

    def _generate_default_response(self, role: str, context: str, depth_level: float) -> str:
        """Generate default response when Ori integration is not available."""
        if role in ["ESU", "OGUN", "OBATALA", "SANGO"]:
            pattern = random.choice(self.dialogue_patterns.get_patterns(role, "ori-ode"))
            transition = random.choice(self.dialogue_patterns.get_transitions(role, "ori-ode"))
            return f"{pattern}, {transition}... Let us explore {context} together with divine wisdom."
        else:
            pattern = random.choice(self.dialogue_patterns.get_patterns(role, "ori-inu"))
            transition = random.choice(self.dialogue_patterns.get_transitions(role, "ori-inu"))
            return f"{pattern}, {transition}... Let us explore {context} together."

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
                }
            }
        }
        
    def get_elements(self, role: str, consciousness_level: str) -> List[str]:
        """Get elements for response generation."""
        elements = {
            "ori-inu": [
                "inner wisdom emerges",
                "spiritual essence manifests",
                "divine spark illuminates"
            ],
            "ori-ode": [
                "practical wisdom manifests",
                "external harmony emerges",
                "worldly understanding deepens"
            ],
            "ori-apere": [
                "transcendent insight reveals",
                "universal wisdom flows",
                "cosmic understanding dawns"
            ]
        }
        return elements.get(consciousness_level, ["wisdom unfolds"])

class EnhancedDialoguePatterns:
    def __init__(self):
        self.patterns = {
            "ori-inu": [
                "Diving deep into inner truth",
                "Exploring the depths of consciousness",
                "Awakening inner wisdom"
            ],
            "ori-ode": [
                "Manifesting practical wisdom",
                "Bringing forth external knowledge",
                "Expressing worldly understanding"
            ],
            "ori-apere": [
                "Ascending to transcendent awareness",
                "Embracing universal consciousness",
                "Channeling divine wisdom"
            ]
        }
        
        self.transitions = {
            "ori-inu": [
                "as inner light guides us",
                "through depths of understanding",
                "with inner clarity"
            ],
            "ori-ode": [
                "through practical manifestation",
                "in tangible expression",
                "with worldly wisdom"
            ],
            "ori-apere": [
                "through transcendent awareness",
                "with divine understanding",
                "in cosmic harmony"
            ]
        }
    
    def get_patterns(self, role: str, consciousness_level: str) -> List[str]:
        """Get patterns for response generation."""
        return self.patterns.get(consciousness_level, ["Exploring wisdom"])
        
    def get_transitions(self, role: str, consciousness_level: str) -> List[str]:
        """Get transitions for response generation."""
        return self.transitions.get(consciousness_level, ["as understanding grows"])
