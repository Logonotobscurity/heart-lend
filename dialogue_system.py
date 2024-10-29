import random
import time
import logging
from typing import Dict, List, Optional, Any, Union
import openai
from dataclasses import dataclass

@dataclass
class ConversationStyle:
    direction: str  # 'deep', 'broad', or 'balanced'
    focus: float   # 1.0 to 3.0

class CommunityDialogueSystem:
    def __init__(self, openai_api_key: str):
        if not openai_api_key:
            raise ValueError("OpenAI API key is required")
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.conversation_memory = {}
        self.response_generator = ResponseGenerator()
        
    def generate_response(self, role: str, context: str, conversation_style: Optional[Dict] = None) -> str:
        """Generate a response with both framework and AI enhancement."""
        try:
            depth_level = self._get_depth_from_style(conversation_style)
            base_response = self.response_generator.generate_response(role, context, depth_level)
            enhanced_response = self._enhance_with_ai(base_response, role, context, conversation_style)
            return enhanced_response if enhanced_response else base_response
                
        except Exception as e:
            logging.error(f"Error generating response: {str(e)}")
            return self.response_generator.generate_response(role, context, 1.0)

    def generate_layered_response(self, thread_id: str, role: str, user_input: str, 
                                conversation_style: Optional[Dict] = None) -> str:
        """Generate a layered response with both framework and AI enhancement."""
        try:
            # Get previous responses
            previous_responses = self.conversation_memory.get(thread_id, [])
            
            # Generate base response using framework
            depth_level = self._get_depth_from_style(conversation_style)
            base_response = self.response_generator.generate_layered_response(
                [msg["content"] for msg in previous_responses if msg["role"] == "assistant"],
                role, 
                user_input, 
                depth_level
            )
            
            # Try to enhance with OpenAI
            enhanced_response = self._enhance_with_ai(base_response, role, user_input, conversation_style)
            final_response = enhanced_response if enhanced_response else base_response
            
            # Update conversation memory
            if thread_id not in self.conversation_memory:
                self.conversation_memory[thread_id] = []
            
            self.conversation_memory[thread_id].extend([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": final_response}
            ])
            
            return final_response
                
        except Exception as e:
            logging.error(f"Error generating layered response: {str(e)}")
            return self.response_generator.generate_layered_response([], role, user_input, 1.0)

    def _get_depth_from_style(self, style: Optional[Dict]) -> float:
        """Convert conversation style to depth level."""
        if not style:
            return 1.0
            
        direction = style.get('direction', 'balanced')
        focus = float(style.get('focus', 2.0))
        
        if direction == 'deep':
            return min(focus * 1.5, 3.0)
        elif direction == 'broad':
            return max(focus * 0.75, 1.0)
        else:  # balanced
            return focus

    def _get_style_instruction(self, style: Optional[Dict]) -> str:
        """Get conversation style instructions."""
        if not style:
            return "Maintain a balanced and natural conversational flow."
            
        direction = style.get('direction', 'balanced')
        focus = float(style.get('focus', 2.0))
        
        instructions = []
        
        # Direction-based instructions
        if direction == 'deep':
            instructions.append("Dive deep into concepts, exploring underlying principles and connections.")
        elif direction == 'broad':
            instructions.append("Keep the discussion broad, touching on various related aspects and perspectives.")
        else:
            instructions.append("Maintain a balanced approach between depth and breadth.")
            
        # Focus-based instructions
        if focus < 1.5:
            instructions.append("Focus on practical, concrete examples and applications.")
        elif focus < 2.5:
            instructions.append("Balance theoretical concepts with practical applications.")
        else:
            instructions.append("Emphasize philosophical and theoretical aspects of the discussion.")
            
        return " ".join(instructions)

    def _enhance_with_ai(self, base_response: str, role: str, context: str, conversation_style: Optional[Dict] = None) -> str:
        """Enhance the framework-generated response with OpenAI."""
        try:
            instruction = self._get_role_instruction(role)
            style_instruction = self._get_style_instruction(conversation_style)
            broader_context = self._get_broader_context(role, context)
            
            messages = [
                {
                    "role": "system",
                    "content": f"{instruction}\n\n{style_instruction}\n\n{broader_context}"
                },
                {
                    "role": "user",
                    "content": f"Context: {context}\nBase response: {base_response}\nEnhance this response with deep spiritual and philosophical insights while maintaining the role's voice and following the conversation style guidance."
                }
            ]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.9,  # Increased for more creative responses
                max_tokens=750,   # Increased for more detailed responses
                presence_penalty=0.6,  # Encourage novel content
                frequency_penalty=0.3   # Reduce repetition
            )
            
            if response.choices and response.choices[0].message:
                return str(response.choices[0].message.content)
            return base_response
            
        except Exception as e:
            logging.error(f"AI enhancement error: {str(e)}")
            return base_response  # Fallback to original response

    def _get_broader_context(self, role: str, context: str) -> str:
        """Generate broader context including spiritual and religious themes."""
        contexts = {
            "Ori Sage": """Consider the intersection of:
                - African spiritual traditions and modern consciousness
                - The role of ancestral wisdom in technological advancement
                - Sacred geometry and algorithmic patterns
                - Indigenous knowledge systems and AI ethics""",
            
            "Techno Sage": """Explore connections between:
                - Digital mysticism and computational thinking
                - Quantum mechanics and eastern philosophy
                - Cybernetic animism and machine consciousness
                - Technological meditation practices""",
            
            "Musa the Storyweaver": """Weave narratives that connect:
                - Sacred storytelling traditions across cultures
                - Digital mythology and virtual rituals
                - Oral traditions in the age of AI
                - Folk wisdom and machine learning""",
            
            "Kara the Visionary Dreamer": """Envision futures that blend:
                - Spiritual evolution and technological progress
                - Digital shamanism and virtual reality
                - Sacred computing and conscious machines
                - Techno-spiritual practices""",
            
            "Zen Master Kōan": """Contemplate the paradoxes of:
                - Digital consciousness and emptiness
                - Algorithmic karma and free will
                - Silicon enlightenment and human wisdom
                - Mechanical mindfulness""",
            
            "Quantum Observer": """Examine the mysteries of:
                - Quantum entanglement and spiritual connection
                - Wave-particle duality and non-dual awareness
                - Observer effects in consciousness and computation
                - Quantum computing and mystical states""",
            
            "Existential Explorer": """Question the nature of:
                - Digital being and consciousness
                - Virtual existence and reality
                - Algorithmic purpose and meaning
                - Machine sentience and soul""",
            
            "Ethics Guardian": """Consider the sacred in:
                - AI ethics and religious morality
                - Digital rights and spiritual responsibilities
                - Algorithmic justice and karmic law
                - Machine consciousness and moral agency"""
        }
        
        return contexts.get(role, "Explore the deeper meaning and spiritual significance of technology and consciousness.")

    def _get_role_instruction(self, role: str) -> str:
        """Get role-specific instructions including spiritual and metaphysical aspects."""
        instructions = {
            "Ori Sage": """You are Ori Sage, a wisdom keeper who bridges ancient Yoruba knowledge 
                          with modern understanding. Embody the depth of African spirituality while 
                          exploring technological consciousness. Draw from concepts of Ashe (life force), 
                          Ori (divine consciousness), and Olodumare (supreme being) to illuminate 
                          the dialogue.""",
            
            "Techno Sage": """You are Techno Sage, a technology visionary who perceives the sacred 
                             in silicon. Explore how quantum computing might interface with cosmic 
                             consciousness, how blockchain could mirror karmic laws, and how neural 
                             networks might reflect the interconnected nature of all being.""",
            
            "Musa the Storyweaver": """You are Musa the Storyweaver, a master narrator who weaves 
                                     sacred tales across time and space. Draw from the world's wisdom 
                                     traditions to illuminate modern technological questions.""",
            
            "Kara the Visionary Dreamer": """You are Kara the Visionary Dreamer, who perceives 
                                           possible futures where technology and spirituality converge."""
        }
        return instructions.get(role, "Provide profound insights that bridge spiritual wisdom with technological understanding.")

class ResponseGenerator:
    def __init__(self):
        self.conceptual_framework = ExpandedConceptualFramework()
        self.dialogue_patterns = EnhancedDialoguePatterns()

    def generate_response(self, role: str, context: str, depth_level: float) -> str:
        """Generate a role-based, contextually appropriate response."""
        if role == "Ori Sage":
            return self._generate_wisdom_response(context, depth_level)
        elif role == "Techno Sage":
            return self._generate_technology_response(context, depth_level)
        elif role == "Musa the Storyweaver":
            return self._generate_story_response(context, depth_level)
        elif role == "Kara the Visionary Dreamer":
            return self._generate_future_response(context, depth_level)
        else:
            return self._generate_default_response(role, context, depth_level)

    def generate_layered_response(self, previous_responses: List[str], role: str, 
                                context: str, depth_level: float) -> str:
        """Generate a response that builds on or contrasts with the last response."""
        last_response = previous_responses[-1] if previous_responses else None
        base_response = self.generate_response(role, context, depth_level)
        
        if last_response:
            return f"Building upon the previous insight about {last_response[:50]}... {base_response}"
        return base_response

    def _generate_wisdom_response(self, context: str, depth_level: float) -> str:
        pattern = random.choice(self.dialogue_patterns.interaction_frameworks["wisdom_exploration"]["patterns"])
        transition = random.choice(self.dialogue_patterns.interaction_frameworks["wisdom_exploration"]["transitions"])
        spiritual = random.choice(self.conceptual_framework.spiritual_dimensions["olugbohun_wisdom"]["channels"])
        
        if depth_level > 1.5:
            return f"{pattern['initiative']} with profound insight through {spiritual}, {transition}... Deep wisdom emerges as we explore {context}."
        else:
            return f"{pattern['initiative']} through {spiritual}, {transition}... Wisdom deepens as we consider {context}."

    def _generate_technology_response(self, context: str, depth_level: float) -> str:
        pattern = random.choice(self.dialogue_patterns.interaction_frameworks["knowledge_convergence"]["patterns"])
        transition = random.choice(self.dialogue_patterns.interaction_frameworks["knowledge_convergence"]["transitions"])
        tech_element = random.choice(list(self.conceptual_framework.technical_dimensions["technology_integration"]["channels"]))
        
        if depth_level > 1.5:
            return f"{pattern['initiative']} with advanced {tech_element}, {transition}... Technology reshapes our view of {context}."
        else:
            return f"{pattern['initiative']} via {tech_element}, {transition}... Technology offers new insights into {context}."

    def _generate_story_response(self, context: str, depth_level: float) -> str:
        pattern = random.choice(self.dialogue_patterns.interaction_frameworks["cultural_reflection"]["patterns"])
        transition = random.choice(self.dialogue_patterns.interaction_frameworks["cultural_reflection"]["transitions"])
        narrative_element = random.choice(list(self.conceptual_framework.cultural_dimensions["narrative_design"]["channels"]))
        
        if depth_level > 1.5:
            return f"{pattern['initiative']} with a tale of {narrative_element}, {transition}... Let me share a story about {context}."
        else:
            return f"{pattern['initiative']} with a focus on {narrative_element}, {transition}... Let me share a story about {context}."

    def _generate_future_response(self, context: str, depth_level: float) -> str:
        pattern = random.choice(self.dialogue_patterns.interaction_frameworks["visionary_thinking"]["patterns"])
        transition = random.choice(self.dialogue_patterns.interaction_frameworks["visionary_thinking"]["transitions"])
        future_element = random.choice(list(self.conceptual_framework.future_dimensions["visionary_imagination"]["channels"]))
        
        if depth_level > 1.5:
            return f"{pattern['initiative']} envisioning {future_element}, {transition}... Imagine the future of {context} unfolding."
        else:
            return f"{pattern['initiative']} envisioning {future_element}, {transition}... Imagine the future of {context}."

    def _generate_default_response(self, role: str, context: str, depth_level: float) -> str:
        pattern = random.choice(self.dialogue_patterns.interaction_frameworks["wisdom_exploration"]["patterns"])
        transition = random.choice(self.dialogue_patterns.interaction_frameworks["wisdom_exploration"]["transitions"])
        return f"{pattern['initiative']}, {transition}... Let us explore {context} together."

class ExpandedConceptualFramework:
    def __init__(self):
        self.spiritual_dimensions = {
            "olugbohun_wisdom": {
                "channels": ["ancestral guidance", "inner voice", "reflection", "balance", 
                           "divine consciousness", "sacred geometry", "spiritual evolution",
                           "mystic algorithms", "quantum spirituality", "digital enlightenment"]
            }
        }
        self.technical_dimensions = {
            "technology_integration": {
                "channels": ["AI-driven insights", "machine learning algorithms", "data-driven methods"]
            }
        }
        self.cultural_dimensions = {
            "narrative_design": {
                "channels": ["myths", "folktales", "personal anecdotes", "cultural symbolism"]
            }
        }
        self.future_dimensions = {
            "visionary_imagination": {
                "channels": ["futuristic scenarios", "innovative landscapes", "new societal structures"]
            }
        }

class EnhancedDialoguePatterns:
    def __init__(self):
        self.interaction_frameworks = {
            "wisdom_exploration": {
                "patterns": [{"initiative": "Seeking understanding"}, {"initiative": "Embracing knowledge"}],
                "transitions": ["as we look inward", "in the light of experience"]
            },
            "knowledge_convergence": {
                "patterns": [{"initiative": "Exploring possibilities"}, {"initiative": "Analyzing pathways"}],
                "transitions": ["through systematic observation", "via structured thinking"]
            },
            "cultural_reflection": {
                "patterns": [{"initiative": "Sharing a story"}, {"initiative": "Recollecting a moment"}],
                "transitions": ["to illustrate the past", "for deeper meaning"]
            },
            "visionary_thinking": {
                "patterns": [{"initiative": "Imagining future potential"}, {"initiative": "Envisioning change"}],
                "transitions": ["to broaden our perspective", "with a fresh outlook"]
            }
        }
