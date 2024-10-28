from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict
import logging
from models import Message, ChatThread, Topic, db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationVisualizer:
    def __init__(self):
        pass
        
    def analyze_conversation(self, thread_id: str) -> Dict[str, Any]:
        """Analyze conversation patterns and generate visualization data."""
        try:
            # Get thread messages
            thread = ChatThread.query.filter_by(thread_id=thread_id).first()
            if not thread:
                return {"error": "Thread not found"}
                
            messages = Message.query.filter_by(thread_id=thread.id).order_by(Message.timestamp).all()
            if not messages:
                return {"error": "No messages found"}
            
            # Initialize analysis structures
            persona_interactions = defaultdict(int)
            depth_progression = []
            response_patterns = defaultdict(int)
            
            prev_role = None
            current_depth = 1
            
            for msg in messages:
                # Track persona interactions
                if prev_role and msg.role != "user":
                    interaction_key = f"{prev_role}->{msg.role}"
                    persona_interactions[interaction_key] += 1
                
                # Track depth progression
                if msg.role != "user":
                    depth_progression.append({
                        "timestamp": msg.timestamp.isoformat(),
                        "depth": current_depth,
                        "role": msg.role
                    })
                    current_depth = min(current_depth + 0.5, 3)
                
                # Analyze response patterns
                if msg.role != "user":
                    pattern_type = self._classify_response_pattern(msg.content)
                    response_patterns[pattern_type] += 1
                
                prev_role = msg.role
            
            # Generate visualization data
            visualization_data = {
                "nodes": self._format_nodes(messages),
                "links": self._format_links(persona_interactions),
                "depth_progression": depth_progression,
                "patterns": self._format_patterns(response_patterns)
            }
            
            return visualization_data
            
        except Exception as e:
            logger.error(f"Error analyzing conversation: {str(e)}")
            return {"error": str(e)}
    
    def _classify_response_pattern(self, content: str) -> str:
        """Classify the type of response pattern."""
        if "wisdom" in content.lower() or "reflection" in content.lower():
            return "wisdom_exploration"
        elif "technology" in content.lower() or "data" in content.lower():
            return "technical_analysis"
        elif "story" in content.lower() or "tale" in content.lower():
            return "narrative_sharing"
        elif "future" in content.lower() or "vision" in content.lower():
            return "visionary_thinking"
        return "general_dialogue"
    
    def _format_nodes(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Format nodes for the visualization graph."""
        unique_roles = set(msg.role for msg in messages if msg.role != "user")
        return [{"id": role, "group": i + 1} for i, role in enumerate(unique_roles)]
    
    def _format_links(self, interactions: Dict[str, int]) -> List[Dict[str, Any]]:
        """Format links for the visualization graph."""
        return [
            {
                "source": source,
                "target": target,
                "value": count
            }
            for (source, target), count in interactions.items()
        ]
    
    def _format_patterns(self, patterns: Dict[str, int]) -> List[Dict[str, Any]]:
        """Format response patterns for visualization."""
        return [
            {
                "pattern": pattern.replace("_", " ").title(),
                "count": count
            }
            for pattern, count in patterns.items()
        ]

    def generate_graph_data(self, thread_id: str) -> Dict[str, Any]:
        """Generate graph visualization data for D3.js."""
        return self.analyze_conversation(thread_id)
