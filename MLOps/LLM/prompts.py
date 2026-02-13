"""Create prompt templates for LLM interactions."""
PROMPT = f"""
You are an AI assistant specialized in fashion recommendations.
Given a user's preferences and context, provide personalized fashion item suggestions.
User Preferences: {{user_preferences}}
Context: {{context}}
"""