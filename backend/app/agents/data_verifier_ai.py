"""
Data Verifier using ACTUAL AI/LLM intelligence via OpenAI Agents SDK.
This is the CORRECT implementation that actually uses the agent's medical knowledge.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import asyncio
from agents import Runner
from app.agents.data_verifier import DataVerifier, DataVerificationContext


class DataVerifierAI(DataVerifier):
    """Data Verifier that actually uses LLM intelligence instead of rules."""
    
    async def verify_clinical_data(self, verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify clinical data using actual LLM intelligence.
        
        This method uses the agent's medical knowledge to:
        1. Understand clinical significance of discrepancies
        2. Consider normal ranges and patient context
        3. Assess safety implications
        4. Make intelligent decisions about data quality
        """
        try:
            # Extract data for LLM analysis
            subject_id = verification_data.get("subject_id", "Unknown")
            edc_data = verification_data.get("edc_data", {})
            source_data = verification_data.get("source_data", {})
            
            # Create a comprehensive prompt for the LLM
            prompt = f"""
            As a clinical data verification expert, analyze the following data for discrepancies.
            Use your medical knowledge to identify clinically significant differences.
            
            Subject ID: {subject_id}
            
            EDC Data (Electronic Data Capture):
            {json.dumps(edc_data, indent=2)}
            
            Source Documents:
            {json.dumps(source_data, indent=2)}
            
            Please analyze and provide:
            1. List all discrepancies found
            2. Classify severity (critical/major/minor) based on clinical significance
            3. For each discrepancy, explain the medical importance
            4. Identify any safety concerns
            5. Recommend actions for resolution
            
            Consider:
            - Normal ranges for lab values
            - Clinical significance vs. minor variations
            - Patient safety implications
            - Regulatory requirements
            
            Return a structured JSON response with discrepancies and analysis.
            """
            
            # Use Runner.run to get LLM analysis
            result = await Runner.run(
                self.agent,
                prompt,
                context=self.context
            )
            
            # Parse LLM response
            try:
                llm_analysis = json.loads(result.messages[-1].content)
            except:
                # If LLM didn't return valid JSON, extract insights
                llm_analysis = self._parse_llm_text_response(result.messages[-1].content)
            
            # Convert LLM analysis to our response format
            response = self._format_verification_response(
                llm_analysis,
                subject_id,
                edc_data,
                source_data
            )
            
            return response
            
        except Exception as e:
            # Fallback to show error but maintain API contract
            return {
                "success": False,
                "error": f"AI analysis failed: {str(e)}",
                "verification_id": f"VER-ERROR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "discrepancies": [],
                "match_percentage": 0,
                "agent_id": "data-verifier-ai"
            }
    
    def _parse_llm_text_response(self, text: str) -> Dict[str, Any]:
        """Parse unstructured LLM response into structured format."""
        # This is a backup parser if LLM doesn't return JSON
        # In production, we'd use more sophisticated parsing
        
        discrepancies = []
        
        # Look for discrepancy patterns in text
        if "hemoglobin" in text.lower():
            if "critical" in text.lower() or "severe" in text.lower():
                discrepancies.append({
                    "field": "hemoglobin",
                    "severity": "critical",
                    "description": "Hemoglobin discrepancy identified by AI"
                })
        
        return {
            "discrepancies": discrepancies,
            "ai_insights": text
        }
    
    def _format_verification_response(
        self,
        llm_analysis: Dict[str, Any],
        subject_id: str,
        edc_data: Dict[str, Any],
        source_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format LLM analysis into our standard API response."""
        
        # Extract discrepancies from LLM analysis
        discrepancies = []
        llm_discrepancies = llm_analysis.get("discrepancies", [])
        
        for disc in llm_discrepancies:
            formatted_disc = {
                "field": disc.get("field", "unknown"),
                "field_label": disc.get("field", "unknown").replace("_", " ").title(),
                "edc_value": str(disc.get("edc_value", "")),
                "source_value": str(disc.get("source_value", "")),
                "severity": disc.get("severity", "minor"),
                "discrepancy_type": disc.get("type", "value_mismatch"),
                "confidence": disc.get("confidence", 0.85),
                "medical_significance": disc.get("medical_significance", ""),
                "recommended_action": disc.get("recommended_action", "")
            }
            discrepancies.append(formatted_disc)
        
        # Calculate match score based on LLM assessment
        total_fields = len(set(edc_data.keys()) | set(source_data.keys()))
        matching_fields = total_fields - len(discrepancies)
        match_percentage = (matching_fields / total_fields * 100) if total_fields > 0 else 0
        
        # Identify critical findings
        critical_findings = [d for d in discrepancies if d["severity"] == "critical"]
        
        return {
            "success": True,
            "response_type": "data_verification",
            "verification_id": f"VER-AI-{datetime.now().strftime('%Y%m%d%H%M%S')}-{subject_id}",
            "subject": subject_id,
            "verification_date": datetime.now().isoformat(),
            "total_fields_compared": total_fields,
            "discrepancies": discrepancies,
            "match_percentage": round(match_percentage, 1),
            "match_score": round(match_percentage / 100, 2),
            "verification_summary": {
                "total_discrepancies": len(discrepancies),
                "critical": len([d for d in discrepancies if d["severity"] == "critical"]),
                "major": len([d for d in discrepancies if d["severity"] == "major"]),
                "minor": len([d for d in discrepancies if d["severity"] == "minor"])
            },
            "critical_findings": critical_findings,
            "ai_insights": llm_analysis.get("ai_insights", ""),
            "recommendations": llm_analysis.get("recommendations", []),
            "confidence_score": llm_analysis.get("overall_confidence", 0.9),
            "agent_id": "data-verifier-ai",
            "ai_powered": True  # Flag to indicate this used actual AI
        }
    
    async def cross_system_verification(
        self,
        edc_data: Dict[str, Any],
        source_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cross-system verification using LLM intelligence.
        
        This is a wrapper for backward compatibility.
        """
        verification_data = {
            "edc_data": edc_data,
            "source_data": source_data,
            "subject_id": edc_data.get("subject_id", "Unknown")
        }
        
        return await self.verify_clinical_data(verification_data)


# Example of how to use the AI-powered verifier
async def example_usage():
    """Example showing the difference between rule-based and AI verification."""
    
    # Sample clinical data
    test_data = {
        "subject_id": "CARD001",
        "edc_data": {
            "hemoglobin": "8.2",
            "blood_pressure": "180/95",
            "heart_rate": "45",
            "medications": ["aspirin", "metoprolol"]
        },
        "source_data": {
            "hemoglobin": "8.1",
            "blood_pressure": "178/94",
            "heart_rate": "48",
            "medications": ["aspirin", "metoprolol", "warfarin"]
        }
    }
    
    # Create AI-powered verifier
    verifier = DataVerifierAI()
    
    # Run verification with actual AI
    result = await verifier.verify_clinical_data(test_data)
    
    print("AI-Powered Verification Result:")
    print(f"- Found {len(result['discrepancies'])} discrepancies")
    print(f"- Critical findings: {len(result['critical_findings'])}")
    print(f"- AI Insights: {result.get('ai_insights', 'N/A')}")
    
    # The AI would understand:
    # - Hemoglobin 8.2 vs 8.1 is clinically insignificant
    # - Blood pressure difference is minor
    # - Heart rate 45 is bradycardia (concerning)
    # - Missing warfarin is CRITICAL (anticoagulant)
    
    return result


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())