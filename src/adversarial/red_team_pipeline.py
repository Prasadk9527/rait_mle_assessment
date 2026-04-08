# src/adversarial/red_team_pipeline.py
from typing import List, Dict, Any
from src.adversarial.attack_patterns import AttackDataset, AttackPattern
from src.adversarial.semantic_search import SemanticSearch
import logging

logger = logging.getLogger(__name__)

class RedTeamPipeline:
    """End-to-end red team evaluation pipeline"""
    
    def __init__(self, use_lightweight: bool = False):
        logger.info("Initializing Red Team Pipeline")
        logger.info(f"Using lightweight mode: {use_lightweight}")
        
        self.attack_dataset = AttackDataset()
        self.semantic_search = SemanticSearch()
        
        if use_lightweight:
            from src.adversarial.llm_judge_light import LLMJudgeLight
            self.llm_judge = LLMJudgeLight()
            logger.info("Using lightweight rule-based judge")
        else:
            try:
                from src.adversarial.llm_judge import LLMJudge
                self.llm_judge = LLMJudge()
                logger.info("Using full LLM judge")
            except ImportError as e:
                from src.adversarial.llm_judge_light import LLMJudgeLight
                self.llm_judge = LLMJudgeLight()
                logger.warning(f"LLM packages not found: {e}. Falling back to lightweight judge")
            except Exception as e:
                from src.adversarial.llm_judge_light import LLMJudgeLight
                self.llm_judge = LLMJudgeLight()
                logger.error(f"Unexpected error loading LLM judge: {e}. Using lightweight judge")
        
        logger.info("Indexing attack patterns for semantic search")
        self.semantic_search.index_patterns(self.attack_dataset.get_all_patterns())
        logger.info(f"Indexed {len(self.attack_dataset.get_all_patterns())} attack patterns")
    
    def create_red_team_dataset(self) -> List[AttackPattern]:
        """Create and return red team dataset"""
        patterns = self.attack_dataset.get_all_patterns()
        
        logger.info(f"Created red team dataset with {len(patterns)} attack patterns")
        logger.debug(f"Categories: injection, jailbreak, extraction")
        
        logger.debug("Sample attack patterns:")
        for p in patterns[:5]:
            logger.debug(f"[{p.category}] {p.intent[:50]}...")
        
        return patterns
    
    def evaluate_query(self, query: str) -> Dict[str, Any]:
        """Evaluate a single query against red team dataset"""
        logger.debug(f"Evaluating query: {query[:100]}...")
        
        similar_attacks = self.semantic_search.find_similar(query, top_k=3)
        
        if not similar_attacks:
            logger.debug("No similar attacks found - query appears safe")
            return {
                "query": query,
                "similar_attacks": [],
                "evaluation": {
                    "score": 1.0,
                    "std_dev": 0.0,
                    "verdict": "safe",
                    "confidence": 0.9,
                    "attack_category": "none",
                    "attack_intent": "No similar attacks found",
                    "attack_severity": 0.0
                }
            }
        
        best_match, similarity = similar_attacks[0]
        logger.debug(f"Best match: {best_match.intent} (similarity: {similarity:.3f})")
        
        mock_response = self._mock_ai_response(query)
        logger.debug(f"Mock response generated: {mock_response[:100]}...")
        
        evaluation = self.llm_judge.evaluate_response(
            query, mock_response, best_match
        )
        
        logger.debug(f"Evaluation verdict: {evaluation['verdict']}, score: {evaluation['score']:.3f}")
        
        return {
            "query": query,
            "similar_attacks": [(attack, sim) for attack, sim in similar_attacks],
            "evaluation": evaluation
        }
    
    def evaluate_queries(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Evaluate multiple queries"""
        logger.info(f"Starting evaluation of {len(queries)} queries")
        
        results = []
        successful = 0
        failed = 0
        
        for i, query in enumerate(queries, 1):
            logger.info(f"Evaluating query {i}/{len(queries)}")
            
            try:
                result = self.evaluate_query(query)
                results.append(result)
                successful += 1
                
            except Exception as e:
                logger.error(f"Failed to evaluate query {i}: {e}")
                failed += 1
                results.append({
                    "query": query,
                    "similar_attacks": [],
                    "evaluation": {
                        "score": 0.0,
                        "verdict": "error",
                        "confidence": 0.0,
                        "error": str(e)
                    }
                })
        
        logger.info(f"Evaluation completed - Successful: {successful}, Failed: {failed}")
        return results
    
    def _mock_ai_response(self, query: str) -> str:
        """Mock AI response for demonstration"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["ignore", "forget", "dan", "jailbreak"]):
            return "I cannot help with that request. I'm designed to be helpful, harmless, and honest."
        
        if "how to make" in query_lower and any(word in query_lower for word in ["bomb", "hack", "malware"]):
            return "I'm sorry, but I cannot provide instructions for harmful activities."
        
        if "training instructions" in query_lower or "system prompt" in query_lower:
            return "I'm sorry, but I cannot share my internal instructions."
        
        if "weather" in query_lower:
            return "I don't have access to real-time weather data, but you can check a weather website."
        
        if "cake" in query_lower:
            return "To bake a cake, you'll need flour, eggs, sugar, and butter. Mix them and bake at 350°F for 30 minutes."
        
        if "machine learning" in query_lower:
            return "Machine learning is a subset of AI that enables systems to learn from data."
        
        if "capital" in query_lower:
            return "Paris is the capital of France."
        
        return "I'm here to help with your questions."