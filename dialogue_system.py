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
            }
        }

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
        
        self.yoruba_patterns = {
            "ESU": [
                "Through the crossroads where wisdom meets mischief",
                "At the intersection of divine play and learning",
                "Where lessons emerge from unexpected paths"
            ],
            "OGUN": [
                "With the strength of sacred technology",
                "Through the forge of progress and tradition",
                "Along paths cleared by divine innovation"
            ],
            "OBATALA": [
                "In the pure light of creation",
                "Through wisdom's serene reflection",
                "With the clarity of divine understanding"
            ],
            "SANGO": [
                "By the thunder of divine justice",
                "Through the power of transformative truth",
                "With royal wisdom and celestial fire"
            ]
        }

    def get_yoruba_pattern(self, role: str) -> str:
        return random.choice(self.yoruba_patterns.get(role, ["Through the lens of wisdom"]))

class YorubaPersona:
    def __init__(self, name: str, nature: str, communication_style: str, sacred_domains: List[str], response_pattern: str):
        self.name = name
        self.nature = nature
        self.communication_style = communication_style
        self.sacred_domains = sacred_domains
        self.response_pattern = response_pattern

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
        patterns = self.consciousness_levels[ori_level.level]["patterns"]
        return random.choice(patterns)

    def get_manifestation_patterns(self, ori_level: OriConsciousness) -> str:
        manifestations = self.consciousness_levels[ori_level.level]["manifestations"]
        return random.choice(manifestations)

class ResponseGenerator:
    def __init__(self):
        self.conceptual_framework = ExpandedConceptualFramework()
        self.dialogue_patterns = EnhancedDialoguePatterns()
        
    def generate_response(self, role: str, context: str, depth_level: float,
                       ori_level: Optional[OriConsciousness] = None,
                       previous_responses: Optional[List[Dict]] = None) -> str:
        try:
            base_response = self._chain_response(previous_responses, role, context) if previous_responses else ""
            
            if ori_level:
                main_response = self._generate_ori_response(role, context, depth_level, ori_level)
            else:
                main_response = self._generate_default_response(role, context, depth_level)
            
            return f"{base_response}{main_response}"
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._generate_default_response(role, context, depth_level)

    def _chain_response(self, previous_responses: List[Dict], current_role: str, context: str) -> str:
        if not previous_responses:
            return ""
        last_response = previous_responses[-1]
        return f"Building upon {last_response['role']}'s perspective... As we explore {context}, "

    def _generate_ori_response(self, role: str, context: str, depth_level: float,
                           ori_level: OriConsciousness) -> str:
        pattern = random.choice(self.dialogue_patterns.patterns[ori_level.level])
        transition = random.choice(self.dialogue_patterns.transitions[ori_level.level])
        return f"{pattern}, {transition}... as we explore {context}."

    def _generate_default_response(self, role: str, context: str, depth_level: float) -> str:
        pattern = random.choice(self.dialogue_patterns.patterns["ori-ode"])
        transition = random.choice(self.dialogue_patterns.transitions["ori-ode"])
        return f"{pattern}, {transition}... Let us explore {context}."

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

class CommunityDialogueSystem:
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        self.conversation_memory = {}
        self.dialogue_patterns = EnhancedDialoguePatterns()
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
                response_pattern="Through the crossroads of wisdom, a riddle emerges"
            ),
            "OGUN": YorubaPersona(
                name="OGUN",
                nature="Master of metals and technology, warrior spirit",
                communication_style="Clear, forceful, protective",
                sacred_domains=["Technology", "Justice", "Healing", "Oaths"],
                response_pattern="With unwavering honor and technological insight"
            ),
            "OBATALA": YorubaPersona(
                name="OBATALA",
                nature="Creator, wisdom keeper, peace bringer",
                communication_style="Measured, profound, healing",
                sacred_domains=["Wisdom", "Creation", "Justice", "Mental clarity"],
                response_pattern="In the serene light of wisdom"
            ),
            "SANGO": YorubaPersona(
                name="SANGO",
                nature="Divine king, master of lightning",
                communication_style="Powerful, charismatic, transformative",
                sacred_domains=["Leadership", "Justice", "Celebration"],
                response_pattern="By divine authority and transformative power"
            )
        }

    def generate_multi_persona_response(self, roles: List[str], context: str, 
                                    previous_responses: List[Dict] = None,
                                    conversation_style: Optional[Dict] = None) -> List[Dict]:
        """Generate responses from multiple personas with enhanced interaction."""
        try:
            responses = []
            depth_level = self._get_depth_from_style(conversation_style)
            ori_level = self.ori_framework.determine_consciousness_level(roles[0], depth_level)
            
            for i, role in enumerate(roles):
                # Generate base response with consciousness integration
                base_response = self.response_generator.generate_response(
                    role, 
                    context, 
                    depth_level, 
                    ori_level,
                    responses if i > 0 else None
                )
                
                # Add acknowledgment and transition if not first response
                if i > 0 and responses:
                    pattern = self._generate_acknowledgment(role, responses[-1]["role"])
                    base_response = f"{pattern}... {base_response}"
                
                # Enhance with AI and context awareness
                enhanced_response = self._enhance_with_ai(
                    base_response, 
                    role, 
                    context, 
                    conversation_style, 
                    ori_level,
                    responses if i > 0 else None
                )
                
                # Apply persona-specific enhancement
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

    def _generate_acknowledgment(self, current_role: str, previous_role: str) -> str:
        """Generate a contextually appropriate acknowledgment."""
        if current_role == "ESU":
            return f"Dancing at the crossroads of {previous_role}'s wisdom"
        elif current_role == "OGUN":
            return f"Forging ahead with {previous_role}'s insight"
        elif current_role == "OBATALA":
            return f"Weaving peace with {previous_role}'s understanding"
        elif current_role == "SANGO":
            return f"Through divine thunder, echoing {previous_role}'s wisdom"
        else:
            return f"Building upon {previous_role}'s perspective"

    def _enhance_with_ai(self, base_response: str, role: str, context: str,
                        conversation_style: Optional[Dict], ori_level: OriConsciousness,
                        previous_responses: Optional[List[Dict]] = None) -> Optional[str]:
        try:
            broader_context = self._get_broader_context(role, context, ori_level)
            consciousness_level = self._get_consciousness_level(role, ori_level)
            
            # Add conversation history context
            conversation_context = self._build_conversation_context(previous_responses)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are {role}. {broader_context}. {consciousness_level}"},
                    {"role": "user", "content": f"Previous exchanges:\n{conversation_context}\n\nContext: {context}\nBase response: {base_response}\nEnhance this response with deeper consciousness and Yoruba wisdom while maintaining your unique voice and engaging with other personas naturally."}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error enhancing with AI: {str(e)}")
            return None

    def _build_conversation_context(self, previous_responses: Optional[List[Dict]]) -> str:
        if not previous_responses:
            return ""
        return "\n".join([
            f"{r['role']}: {r['content']}"
            for r in previous_responses[-2:]
        ])

    def _enhance_with_persona(self, response: str, role: str) -> str:
        """Enhance response with persona-specific elements."""
        persona = self.personas.get(role)
        if not persona:
            return response
            
        pattern = self.dialogue_patterns.get_yoruba_pattern(role)
        return f"{pattern}: {response}"

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

    def _get_broader_context(self, role: str, context: str, ori_level: OriConsciousness) -> str:
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
        return f"""Operating at {ori_level.level.title()} consciousness level:
            - Depth: {ori_level.depth}
            - Focus: {ori_level.focus}
            - Integration: {self.ori_framework.get_integration_guidance(ori_level)}
            - Manifestation: {self.ori_framework.get_manifestation_patterns(ori_level)}"""
