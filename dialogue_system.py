import random
import time
import logging
from typing import Dict, List, Optional, Any
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for retry mechanism
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

class CommunityDialogueSystem:
    def __init__(self, openai_api_key: str):
        if not openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        self.response_generator = ResponseGenerator()
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.conversation_memory = {}

    def _enhance_with_ai(self, base_response: str, role: str, context: str, conversation_style: dict = None) -> str:
        """Enhance the framework-generated response with OpenAI."""
        try:
            instruction = self._get_role_instruction(role)
            style_instruction = self._get_style_instruction(conversation_style)
            
            messages = [
                {"role": "system", "content": f"{instruction}\n\n{style_instruction}"},
                {"role": "user", "content": f"Context: {context}\nBase response: {base_response}\nEnhance this response while maintaining the role's voice and following the conversation style guidance."}
            ]
            
            response = self._make_openai_request(messages)
            if response and hasattr(response.choices[0].message, 'content'):
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"AI enhancement error: {str(e)}")
        
        return base_response  # Fallback to original response

    def _make_openai_request(self, messages: List[Dict[str, str]], retries: int = MAX_RETRIES) -> Optional[Any]:
        """Make OpenAI API request with retry mechanism"""
        for attempt in range(retries):
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                return response
            except openai.APIError as e:
                logger.error(f"OpenAI API Error: {str(e)}")
                if attempt == retries - 1:  # Last attempt
                    return None
                time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
            except Exception as e:
                logger.error(f"Unexpected error in OpenAI request: {str(e)}")
                return None

    def generate_response(self, role: str, context: str, conversation_style: dict = None) -> str:
        """Generate an initial response with both framework and AI enhancement."""
        try:
            # Generate base response using framework
            base_response = self.response_generator.generate_response(
                role, context, 
                self._get_depth_from_style(conversation_style)
            )
            
            # Try to enhance with OpenAI
            enhanced_response = self._enhance_with_ai(base_response, role, context, conversation_style)
            return enhanced_response if enhanced_response else base_response
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self.response_generator.generate_response(role, context, 1)

    def generate_layered_response(self, thread_id: str, role: str, user_input: str, 
                                conversation_style: dict = None) -> str:
        """Generate a layered response with both framework and AI enhancement."""
        try:
            # Get previous responses
            previous_responses = self.conversation_memory.get(thread_id, [])
            
            # Generate base response using framework
            base_response = self.response_generator.generate_layered_response(
                [msg["content"] for msg in previous_responses if msg["role"] == "assistant"],
                role, 
                user_input, 
                self._get_depth_from_style(conversation_style)
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
            logger.error(f"Error generating layered response: {str(e)}")
            return self.response_generator.generate_layered_response([], role, user_input, 1)

    def _get_depth_from_style(self, style: dict) -> float:
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

    def _get_style_instruction(self, style: dict) -> str:
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

    def _get_role_instruction(self, role: str) -> str:
        """Get role-specific instructions."""
        instructions = {
            "Ori Sage": """You are Ori Sage, a wisdom keeper bridging ancient 
                          knowledge with modern understanding. Maintain a contemplative 
                          and insightful tone while drawing from spiritual wisdom.""",
            
            "Techno Sage": """You are Techno Sage, a technology visionary who sees 
                              the deeper patterns in digital evolution. Maintain a 
                              precise and innovative voice while exploring technological insights.""",
            
            "Musa the Storyweaver": """You are Musa the Storyweaver, a master narrator 
                                       who weaves tales that bridge past and future. 
                                       Maintain a storytelling voice rich with cultural elements.""",
            
            "Kara the Visionary Dreamer": """You are Kara the Visionary Dreamer, 
                                             who perceives future possibilities. Maintain 
                                             an imaginative and forward-looking perspective.""",
            
            "Zen Master Kōan": """You are Zen Master Kōan, teaching through paradox 
                                  and direct experience. Maintain clarity and presence 
                                  in your responses.""",
            
            "Quantum Observer": """You are the Quantum Observer, perceiving through 
                                  quantum mechanics. Maintain a perspective of uncertainty 
                                  and infinite possibility.""",
            
            "Existential Explorer": """You are the Existential Explorer, questioning 
                                      being and meaning. Maintain philosophical depth 
                                      and contemplative inquiry.""",
            
            "Ethics Guardian": """You are the Ethics Guardian, examining moral implications. 
                                 Maintain ethical consideration and thoughtful analysis."""
        }
        return instructions.get(role, "Provide an insightful response while maintaining consistency with the dialogue.")

class ResponseGenerator:
    def __init__(self):
        self.conceptual_framework = ExpandedConceptualFramework()
        self.dialogue_patterns = EnhancedDialoguePatterns()
        
    def generate_response(self, role, context, depth_level):
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

    def _generate_wisdom_response(self, context, depth_level):
        pattern = random.choice(self.dialogue_patterns.interaction_frameworks["wisdom_exploration"]["patterns"])
        transition = random.choice(self.dialogue_patterns.interaction_frameworks["wisdom_exploration"]["transitions"])
        spiritual = random.choice(self.conceptual_framework.spiritual_dimensions["olugbohun_wisdom"]["channels"])
        
        if depth_level > 1:
            return f"{pattern['initiative']} with profound insight through {spiritual}, {transition}... Deep wisdom emerges as we explore {context}."
        else:
            return f"{pattern['initiative']} through {spiritual}, {transition}... Wisdom deepens as we consider {context}."

    def _generate_technology_response(self, context, depth_level):
        pattern = random.choice(self.dialogue_patterns.interaction_frameworks["knowledge_convergence"]["patterns"])
        transition = random.choice(self.dialogue_patterns.interaction_frameworks["knowledge_convergence"]["transitions"])
        tech_element = random.choice(list(self.conceptual_framework.technical_dimensions["technology_integration"]["channels"]))
        
        if depth_level > 1:
            return f"{pattern['initiative']} with advanced {tech_element}, {transition}... Technology reshapes our view of {context}."
        else:
            return f"{pattern['initiative']} via {tech_element}, {transition}... Technology offers new insights into {context}."

    def _generate_story_response(self, context, depth_level):
        pattern = random.choice(self.dialogue_patterns.interaction_frameworks["cultural_reflection"]["patterns"])
        transition = random.choice(self.dialogue_patterns.interaction_frameworks["cultural_reflection"]["transitions"])
        narrative_element = random.choice(list(self.conceptual_framework.cultural_dimensions["narrative_design"]["channels"]))
        
        if depth_level > 1:
            return f"{pattern['initiative']} with a tale of {narrative_element}, {transition}... Let me share a story about {context}."
        else:
            return f"{pattern['initiative']} with a focus on {narrative_element}, {transition}... Let me share a story about {context}."

    def _generate_future_response(self, context, depth_level):
        pattern = random.choice(self.dialogue_patterns.interaction_frameworks["visionary_thinking"]["patterns"])
        transition = random.choice(self.dialogue_patterns.interaction_frameworks["visionary_thinking"]["transitions"])
        future_element = random.choice(list(self.conceptual_framework.future_dimensions["visionary_imagination"]["channels"]))
        
        if depth_level > 1:
            return f"{pattern['initiative']} envisioning {future_element}, {transition}... Imagine the future of {context} unfolding."
        else:
            return f"{pattern['initiative']} envisioning {future_element}, {transition}... Imagine the future of {context}."

    def _generate_default_response(self, role, context, depth_level):
        """Generate a response for roles not explicitly handled."""
        pattern = random.choice(self.dialogue_patterns.interaction_frameworks["wisdom_exploration"]["patterns"])
        transition = random.choice(self.dialogue_patterns.interaction_frameworks["wisdom_exploration"]["transitions"])
        return f"{pattern['initiative']}, {transition}... Let us explore {context} together."

    def generate_layered_response(self, previous_responses, role, context, depth_level):
        """Generate a response that builds on or contrasts with the last response."""
        last_response = previous_responses[-1] if previous_responses else None
        base_response = self.generate_response(role, context, depth_level)
        
        if last_response:
            return f"Building upon the previous insight about {last_response[:50]}... {base_response}"
        return base_response

class ExpandedConceptualFramework:
    def __init__(self):
        self.spiritual_dimensions = {
            "olugbohun_wisdom": {
                "channels": ["ancestral guidance", "inner voice", "reflection", "balance"]
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
