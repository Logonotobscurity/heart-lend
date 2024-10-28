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
            return "Unrecognized role"

    def _generate_wisdom_response(self, context, depth_level):
        pattern = random.choice(self.dialogue_patterns.interaction_frameworks["wisdom_exploration"]["patterns"])
        transition = random.choice(self.dialogue_patterns.interaction_frameworks["wisdom_exploration"]["transitions"])
        spiritual = random.choice(list(self.conceptual_framework.spiritual_dimensions["olugbohun_wisdom"]["channels"]))
        
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

    def generate_layered_response(self, previous_responses, role, context, depth_level):
        """Generate a response that builds on or contrasts with the last response."""
        last_response = previous_responses[-1] if previous_responses else None
        
        if role == "Ori Sage":
            return f"As the Ori Sage, reflecting on {last_response if last_response else context}... " + self._generate_wisdom_response(context, depth_level)
        elif role == "Techno Sage":
            return f"As the Techno Sage, building on {last_response if last_response else context}... " + self._generate_technology_response(context, depth_level)
        elif role == "Musa the Storyweaver":
            return f"As Musa the Storyweaver, inspired by {last_response if last_response else context}... " + self._generate_story_response(context, depth_level)
        elif role == "Kara the Visionary Dreamer":
            return f"As Kara the Visionary Dreamer, imagining beyond {last_response if last_response else context}... " + self._generate_future_response(context, depth_level)
        else:
            return "Unrecognized role"

class CommunityDialogueSystem:
    def __init__(self, openai_api_key: str):
        if not openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        self.response_generator = ResponseGenerator()
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.conversation_memory = {}
        
    def _make_openai_request(self, messages: List[Dict[str, str]], retries: int = MAX_RETRIES) -> Optional[Any]:
        """Make OpenAI API request with retry mechanism"""
        for attempt in range(retries):
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": m["role"], "content": m["content"]} for m in messages],
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
        return None
        
    def generate_response(self, role: str, context: str) -> str:
        """Generate an initial response for a new dialogue with improved error handling."""
        try:
            # First try with OpenAI
            instruction = self._get_role_instruction(role)
            messages = [
                {"role": "system", "content": instruction},
                {"role": "user", "content": context}
            ]
            
            response = self._make_openai_request(messages)
            
            if response and response.choices and response.choices[0].message:
                return str(response.choices[0].message.content)
            
            # If OpenAI fails, use the framework response generator
            return self.response_generator.generate_response(role, context, 1)
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self.response_generator.generate_response(role, context, 1)
    
    def generate_layered_response(self, thread_id: str, role: str, user_input: str) -> str:
        """Generate a response that builds on previous context with improved error handling."""
        try:
            # Update conversation memory
            if thread_id not in self.conversation_memory:
                self.conversation_memory[thread_id] = []
            self.conversation_memory[thread_id].append({"role": "user", "content": user_input})
            
            # First try with OpenAI
            instruction = self._get_role_instruction(role)
            messages = [{"role": "system", "content": instruction}]
            messages.extend(self.conversation_memory[thread_id][-3:])  # Keep last 3 messages for context
            
            response = self._make_openai_request(messages)
            
            if response and response.choices and response.choices[0].message:
                response_content = str(response.choices[0].message.content)
                self.conversation_memory[thread_id].append({"role": "assistant", "content": response_content})
                return response_content
            
            # If OpenAI fails, use the framework response generator
            return self.response_generator.generate_layered_response(
                [m["content"] for m in self.conversation_memory[thread_id] if m["role"] == "assistant"],
                role,
                user_input,
                2 if len(self.conversation_memory[thread_id]) > 4 else 1
            )
                
        except Exception as e:
            logger.error(f"Error generating layered response: {str(e)}")
            return self.response_generator.generate_layered_response(
                [m["content"] for m in self.conversation_memory[thread_id] if m["role"] == "assistant"],
                role,
                user_input,
                1
            )
    
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
