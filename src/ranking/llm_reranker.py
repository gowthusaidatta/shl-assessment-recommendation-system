"""
LLM-based reranking using Google Gemini.
"""
import logging
from typing import List, Tuple, Dict
import google.generativeai as genai

from src.data.models import Assessment
from config.settings import GEMINI_API_KEY, USE_LLM_RERANKING

logger = logging.getLogger(__name__)


class GeminiReranker:
    """LLM-based reranking using Google Gemini."""
    
    def __init__(self, api_key: str = GEMINI_API_KEY):
        """Initialize Gemini client."""
        if not api_key:
            raise ValueError("Gemini API key is required for LLM reranking")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        logger.info("Gemini reranker initialized")
    
    def rerank(
        self,
        query: str,
        candidates: List[Tuple[Assessment, float]],
        top_k: int = 20
    ) -> List[Tuple[Assessment, float]]:
        """
        Rerank candidates using LLM understanding.
        
        Args:
            query: User query
            candidates: List of (Assessment, score) tuples
            top_k: Number of candidates to return
        
        Returns:
            Reranked list of (Assessment, score) tuples
        """
        if not candidates:
            return []
        
        # Limit to top candidates to avoid token limits
        candidates = candidates[:min(len(candidates), 30)]
        
        # Build prompt
        prompt = self._build_reranking_prompt(query, candidates)
        
        try:
            # Call Gemini
            response = self.model.generate_content(prompt)
            
            # Parse response to get reranked indices
            reranked_indices = self._parse_reranking_response(
                response.text,
                len(candidates)
            )
            
            # Reorder candidates
            reranked = []
            for idx in reranked_indices[:top_k]:
                if 0 <= idx < len(candidates):
                    assessment, original_score = candidates[idx]
                    # Boost score based on LLM ranking
                    boost_factor = 1.0 + (0.5 * (1 - idx / len(candidates)))
                    new_score = original_score * boost_factor
                    reranked.append((assessment, new_score))
            
            # Add remaining candidates
            used_indices = set(reranked_indices[:top_k])
            for idx, (assessment, score) in enumerate(candidates):
                if idx not in used_indices and len(reranked) < top_k:
                    reranked.append((assessment, score))
            
            logger.info(f"LLM reranked {len(reranked)} candidates")
            return reranked[:top_k]
        
        except Exception as e:
            logger.error(f"LLM reranking failed: {e}")
            # Fallback to original ranking
            return candidates[:top_k]
    
    def _build_reranking_prompt(
        self,
        query: str,
        candidates: List[Tuple[Assessment, float]]
    ) -> str:
        """Build prompt for Gemini reranking."""
        prompt = f"""You are an expert in psychometric assessments and talent evaluation.

Given this hiring requirement:
"{query}"

Rank the following SHL assessments from MOST to LEAST relevant (1 = most relevant).
Consider:
- Technical skill match
- Behavioral/personality fit
- Assessment type appropriateness
- Role requirements

Assessments:
"""
        
        for idx, (assessment, score) in enumerate(candidates):
            prompt += f"\n{idx}. {assessment.assessment_name}"
            if assessment.description:
                # Truncate description
                desc = assessment.description[:100]
                prompt += f" - {desc}..."
            prompt += f" (Test Type: {assessment.test_type})"
        
        prompt += """\n\nRespond with ONLY the ranked indices (space-separated), starting with the most relevant.
Example: 3 7 1 12 0 5 2 ...

Ranked indices:"""
        
        return prompt
    
    def _parse_reranking_response(
        self,
        response: str,
        max_count: int
    ) -> List[int]:
        """Parse LLM response to extract ranked indices."""
        try:
            # Extract numbers from response
            import re
            numbers = re.findall(r'\d+', response)
            indices = [int(n) for n in numbers if int(n) < max_count]
            
            # Add missing indices at the end
            all_indices = set(range(max_count))
            missing = sorted(all_indices - set(indices))
            indices.extend(missing)
            
            return indices
        
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            # Fallback to original order
            return list(range(max_count))
    
    def enhance_query_understanding(self, query: str) -> Dict:
        """
        Use LLM to extract skills and intent from query.
        
        Returns:
            Dict with technical_skills, behavioral_skills, test_type_weights
        """
        prompt = f"""Analyze this hiring requirement and extract key information:

"{query}"

Provide a structured analysis:
1. Technical Skills: (list technical/hard skills mentioned)
2. Behavioral Skills: (list soft skills/personality traits mentioned)
3. Test Types Needed: (Knowledge, Personality, or Both)

Keep responses concise (keywords only).

Analysis:"""
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_query_analysis(response.text)
        
        except Exception as e:
            logger.error(f"Query enhancement failed: {e}")
            return {
                "technical_skills": [],
                "behavioral_skills": [],
                "test_type_weights": {"K": 0.5, "P": 0.5}
            }
    
    def _parse_query_analysis(self, response: str) -> Dict:
        """Parse LLM query analysis response."""
        # Simple keyword extraction (can be improved)
        technical_skills = []
        behavioral_skills = []
        
        lines = response.lower().split('\n')
        in_technical = False
        in_behavioral = False
        
        for line in lines:
            if 'technical' in line:
                in_technical = True
                in_behavioral = False
            elif 'behavioral' in line or 'soft' in line:
                in_behavioral = True
                in_technical = False
            elif in_technical and line.strip():
                # Extract skills
                import re
                words = re.findall(r'\b\w+\b', line)
                technical_skills.extend(words[:5])  # Limit
            elif in_behavioral and line.strip():
                words = re.findall(r'\b\w+\b', line)
                behavioral_skills.extend(words[:5])
        
        # Determine weights
        has_technical = len(technical_skills) > 0
        has_behavioral = len(behavioral_skills) > 0
        
        if has_technical and has_behavioral:
            weights = {"K": 0.6, "P": 0.4}
        elif has_technical:
            weights = {"K": 0.8, "P": 0.2}
        elif has_behavioral:
            weights = {"K": 0.2, "P": 0.8}
        else:
            weights = {"K": 0.5, "P": 0.5}
        
        return {
            "technical_skills": technical_skills[:10],
            "behavioral_skills": behavioral_skills[:10],
            "test_type_weights": weights,
            "needs_balance": has_technical and has_behavioral
        }
