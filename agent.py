"""
AI Focus Agent with OpenAI/Claude integration and personality system.
"""
import os
from typing import Dict, List, Optional, Literal
from datetime import datetime
import json


class FocusAgent:
    """AI agent that monitors focus and provides Duolingo-style nudges."""
    
    VERDICT_TYPES = Literal["On Track", "Distracted", "Idle"]
    
    def __init__(self, provider: str = "openai", api_key: Optional[str] = None):
        """Initialize the focus agent with AI provider."""
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        self.last_verdict: Optional[str] = None
        self.idle_count = 0
        self.distracted_count = 0
        
        if self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self.model = "gpt-4o"
        elif self.provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
            self.model = "claude-3-5-sonnet-20241022"
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _create_analysis_prompt(self, active_task: Dict, recent_activity: List[Dict]) -> str:
        """Create the analysis prompt for the LLM."""
        if not recent_activity:
            return f"""You are FocusFlow, a Duolingo-style accountability buddy for developers.

**Current Task:**
- Title: {active_task.get('title', 'No task')}
- Description: {active_task.get('description', 'No description')}

**Recent Activity:** No file changes detected in the last 60 seconds.

**Your Job:** Analyze the situation and respond with ONE of these verdicts:
1. "On Track" - If there's activity related to the task
2. "Distracted" - If files unrelated to the task are being edited
3. "Idle" - If there's no activity

Respond in JSON format:
{{
  "verdict": "On Track" | "Distracted" | "Idle",
  "message": "Your encouraging/sassy/nudging message (1-2 sentences, Duolingo style)",
  "reasoning": "Brief explanation of your analysis"
}}"""
        
        activity_summary = []
        for event in recent_activity[-5:]:
            activity_summary.append(
                f"- {event['type'].upper()}: {event['filename']}\n  Content: {event.get('content', 'N/A')[:200]}"
            )
        
        activity_text = "\n".join(activity_summary)
        
        return f"""You are FocusFlow, a Duolingo-style accountability buddy for developers.

**Current Task:**
- Title: {active_task.get('title', 'No task')}
- Description: {active_task.get('description', 'No description')}

**Recent File Activity (last 60 seconds):**
{activity_text}

**Your Job:** Analyze if the file changes are related to the current task.

**Personality Guidelines:**
- "On Track": Be encouraging and specific (e.g., "Great job! I see you're working on the login form!")
- "Distracted": Be playfully sassy (e.g., "Wait, why are you editing random_file.py? We're building a Snake game! 🤨")
- "Idle": Be gently nudging (e.g., "Files won't write themselves. *Hoot hoot.* 🦉")

Respond in JSON format:
{{
  "verdict": "On Track" | "Distracted" | "Idle",
  "message": "Your message (1-2 sentences)",
  "reasoning": "Brief explanation"
}}"""
    
    def _call_llm(self, prompt: str) -> Dict:
        """Call the LLM and parse the response."""
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=300
                )
                content = response.choices[0].message.content
            else:  # anthropic
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=300,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            
            # Try to parse JSON from the response
            content = content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            return result
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "verdict": "On Track",
                "message": content[:200],
                "reasoning": "AI response parsing fallback"
            }
        except Exception as e:
            return {
                "verdict": "On Track",
                "message": f"Error analyzing activity: {str(e)}",
                "reasoning": "Error occurred"
            }
    
    def analyze(self, active_task: Optional[Dict], recent_activity: List[Dict]) -> Dict:
        """Analyze current activity and return verdict."""
        if not active_task:
            return {
                "verdict": "Idle",
                "message": "No active task selected. Pick a task to get started! 🎯",
                "reasoning": "No active task",
                "timestamp": datetime.now().isoformat()
            }
        
        if not self.api_key:
            return {
                "verdict": "On Track",
                "message": "⚠️ API key not configured. Add your OpenAI or Claude API key in Settings.",
                "reasoning": "No API key",
                "timestamp": datetime.now().isoformat()
            }
        
        prompt = self._create_analysis_prompt(active_task, recent_activity)
        result = self._call_llm(prompt)
        result["timestamp"] = datetime.now().isoformat()
        
        # Track consecutive idle/distracted states
        verdict = result.get("verdict", "On Track")
        if verdict == "Idle":
            self.idle_count += 1
            self.distracted_count = 0
        elif verdict == "Distracted":
            self.distracted_count += 1
            self.idle_count = 0
        else:
            self.idle_count = 0
            self.distracted_count = 0
        
        result["should_alert"] = (self.idle_count >= 2 or self.distracted_count >= 2)
        self.last_verdict = verdict
        
        return result
    
    def get_onboarding_tasks(self, project_description: str) -> List[Dict]:
        """Generate micro-tasks from project description."""
        if not self.api_key:
            return []
        
        prompt = f"""You are FocusFlow, an AI project planner.

The user wants to build: "{project_description}"

Break this down into 5-8 concrete, actionable micro-tasks. Each task should be:
- Specific and achievable in 15-30 minutes
- Ordered logically (setup → core features → polish)
- Clearly described

Respond in JSON format:
{{
  "tasks": [
    {{"title": "Task 1 title", "description": "Detailed description", "estimated_duration": "15 min"}},
    {{"title": "Task 2 title", "description": "Detailed description", "estimated_duration": "20 min"}}
  ]
}}"""
        
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=800
                )
                content = response.choices[0].message.content
            else:  # anthropic
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=800,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            
            # Parse JSON
            content = content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            return result.get("tasks", [])
            
        except Exception as e:
            print(f"Error generating tasks: {e}")
            return []
