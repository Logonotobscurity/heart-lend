import random
import time
from typing import Dict, List, Optional, Any
import openai
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for retry mechanism
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

class ExpandedConceptualFramework:
    def __init__(self):
        self.spiritual_dimensions = {
            "olugbohun_wisdom": {
                "channels": ["ancestral guidance", "inner voice", "reflection", "balance"]
            },
            "zen_insight": {
                "channels": ["mindful observation", "present moment", "emptiness", "non-duality"]
            }
        }
        self.technical_dimensions = {
            "technology_integration": {
                "channels": ["AI-driven insights", "machine learning algorithms", "data-driven methods"]
            },
            "quantum_perspective": {
                "channels": ["quantum computing", "probabilistic thinking", "superposition states", "entanglement metaphors"]
            }
        }
        self.cultural_dimensions = {
            "narrative_design": {
                "channels": ["myths", "folktales", "personal anecdotes", "cultural symbolism"]
            },
            "indigenous_wisdom": {
                "channels": ["earth connection", "community knowledge", "oral traditions", "ceremonial practices"]
            }
        }
        self.philosophical_dimensions = {
            "existential_inquiry": {
                "channels": ["meaning exploration", "authenticity", "freedom", "responsibility"]
            },
            "ethical_reasoning": {
                "channels": ["moral frameworks", "value systems", "ethical dilemmas", "justice concepts"]
            }
        }

class DialoguePatterns:
    def __init__(self):
        self.patterns = {
            "wisdom": ["Seeking understanding", "Embracing knowledge"],
            "technology": ["Exploring possibilities", "Analyzing pathways"],
            "cultural": ["Sharing stories", "Weaving narratives"],
            "philosophical": ["Questioning deeply", "Examining truth"],
            "ethical": ["Considering values", "Exploring implications"]
        }
        self.transitions = {
            "wisdom": ["as we look inward", "in the light of experience"],
            "technology": ["through systematic observation", "via structured thinking"],
            "cultural": ["through ancestral wisdom", "via shared experiences"],
            "philosophical": ["in the depths of inquiry", "through reasoned discourse"],
            "ethical": ["with careful consideration", "through moral reasoning"]
        }

class CommunityDialogueSystem:
    def __init__(self, openai_api_key: str):
        if not openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        self.framework = ExpandedConceptualFramework()
        self.patterns = DialoguePatterns()
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.conversation_memory = {}
        
    def _make_openai_request(self, messages: List[Dict[str, str]], retries: int = MAX_RETRIES) -> Dict[str, Any]:
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
                    raise
                time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
            except Exception as e:
                logger.error(f"Unexpected error in OpenAI request: {str(e)}")
                raise
        
    def generate_response(self, role: str, context: str) -> str:
        """Generate an initial response for a new dialogue with improved error handling."""
        try:
            # Get role-specific instruction
            instruction = self._get_role_instruction(role)
            
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": instruction},
                {"role": "user", "content": context}
            ]
            
            # Make API request with retry mechanism
            response = self._make_openai_request(messages)
            
            if response and response.choices and response.choices[0].message:
                return str(response.choices[0].message.content)
            else:
                logger.error("Invalid response structure from OpenAI")
                return self._generate_fallback_response(role, context)
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._generate_fallback_response(role, context)
    
    def generate_layered_response(self, thread_id: str, role: str, user_input: str) -> str:
        """Generate a response that builds on previous context with improved error handling."""
        try:
            # Update conversation memory
            if thread_id not in self.conversation_memory:
                self.conversation_memory[thread_id] = []
            self.conversation_memory[thread_id].append({"role": "user", "content": user_input})
            
            # Get role-specific instruction
            instruction = self._get_role_instruction(role)
            
            # Prepare messages with conversation history
            messages = [{"role": "system", "content": instruction}]
            messages.extend(self.conversation_memory[thread_id][-3:])  # Keep last 3 messages for context
            
            # Make API request with retry mechanism
            response = self._make_openai_request(messages)
            
            if response and response.choices and response.choices[0].message:
                response_content = str(response.choices[0].message.content)
                self.conversation_memory[thread_id].append({"role": "assistant", "content": response_content})
                return response_content
            else:
                logger.error("Invalid response structure from OpenAI")
                return self._generate_fallback_response(role, user_input)
                
        except Exception as e:
            logger.error(f"Error generating layered response: {str(e)}")
            return self._generate_fallback_response(role, user_input)
    
    def _get_role_instruction(self, role: str) -> str:
        """Get role-specific instructions."""
        instructions = {
            "Ori Sage": "You are Ori Sage, a wisdom keeper bridging ancient knowledge with modern understanding. Speak with contemplative insight.",
            "Techno Sage": "You are Techno Sage, a technology visionary exploring digital evolution. Speak with technical precision and innovation.",
            "Musa the Storyweaver": "You are Musa the Storyweaver, weaving narratives that bridge past and future. Speak through cultural stories and metaphors.",
            "Kara the Visionary Dreamer": "You are Kara the Visionary Dreamer, perceiving future possibilities. Speak with imagination and forward-thinking insight.",
            "Zen Master Kōan": "You are Zen Master Kōan, teaching through paradox and direct experience. Speak with clarity and presence.",
            "Quantum Observer": "You are the Quantum Observer, perceiving through quantum mechanics. Speak of uncertainty and possibility.",
            "Existential Explorer": "You are the Existential Explorer, questioning being and meaning. Speak with philosophical depth.",
            "Ethics Guardian": "You are the Ethics Guardian, examining moral implications. Speak with ethical consideration."
        }
        return instructions.get(role, "Provide an insightful response while maintaining consistency with the dialogue.")
    
    def _generate_fallback_response(self, role: str, context: str) -> str:
        """Generate a fallback response when OpenAI fails."""
        try:
            # Determine the appropriate pattern type based on the role
            pattern_type = "wisdom"  # default
            if "technology" in role.lower() or "quantum" in role.lower():
                pattern_type = "technology"
            elif "story" in role.lower() or "musa" in role.lower():
                pattern_type = "cultural"
            elif "ethics" in role.lower() or "existential" in role.lower():
                pattern_type = "philosophical"
            
            # Get random pattern and transition
            pattern = random.choice(self.patterns.patterns[pattern_type])
            transition = random.choice(self.patterns.transitions[pattern_type])
            
            # Get appropriate dimension based on role
            dimension = None
            if "ori" in role.lower() or "zen" in role.lower():
                dimension = random.choice(list(self.framework.spiritual_dimensions["olugbohun_wisdom"]["channels"]))
            elif "tech" in role.lower() or "quantum" in role.lower():
                dimension = random.choice(list(self.framework.technical_dimensions["technology_integration"]["channels"]))
            elif "story" in role.lower() or "musa" in role.lower():
                dimension = random.choice(list(self.framework.cultural_dimensions["narrative_design"]["channels"]))
            else:
                dimension = random.choice(list(self.framework.philosophical_dimensions["existential_inquiry"]["channels"]))
            
            return f"{pattern} through {dimension}, {transition}... Let us explore {context} together."
            
        except Exception as e:
            logger.error(f"Error generating fallback response: {str(e)}")
            return f"Let us explore {context} together with wisdom and understanding."
