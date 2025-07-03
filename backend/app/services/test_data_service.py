"""Test Data Service for Clinical Trials Agent System."""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import logging

from app.core.config import Settings
from tests.test_data.synthetic_data_generator import generate_test_study, STUDY_PRESETS

logger = logging.getLogger(__name__)

class TestDataService:
    """Service for managing test data integration with agent system."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.test_data_cache: Dict[str, Any] = {}
        self.current_study: Optional[Dict[str, Any]] = None
        
        # Initialize test data if enabled
        if settings.use_test_data:
            self._initialize_test_data()
    
    def _initialize_test_data(self):
        """Initialize test data based on configuration."""
        try:
            study_preset = getattr(self.settings, 'test_data_preset', 'cardiology_phase2')
            logger.info(f"Initializing test data with preset: {study_preset}")
            
            self.current_study = generate_test_study(study_preset)
            self._build_lookup_cache()
            
            logger.info(f"Test data initialized successfully:")
            logger.info(f"  - Study: {self.current_study['study_info']['protocol_id']}")
            logger.info(f"  - Subjects: {len(self.current_study['subjects'])}")
            logger.info(f"  - Sites: {len(self.current_study['sites'])}")
            
        except Exception as e:
            logger.error(f"Failed to initialize test data: {e}")
            self.current_study = None
    
    def _build_lookup_cache(self):
        """Build lookup cache for fast data retrieval."""
        if not self.current_study:
            return
            
        # Subject lookup cache
        self.test_data_cache['subjects'] = {
            subject['subject_id']: subject 
            for subject in self.current_study['subjects']
        }
        
        # Site lookup cache
        self.test_data_cache['sites'] = {
            site['site_id']: site 
            for site in self.current_study['sites']
        }
        
        # Visit data cache (flattened for easy access)
        self.test_data_cache['visit_data'] = {}
        for subject in self.current_study['subjects']:
            for visit in subject['visits']:
                key = f"{subject['subject_id']}_{visit['visit_name']}"
                self.test_data_cache['visit_data'][key] = {
                    'subject_id': subject['subject_id'],
                    'visit_name': visit['visit_name'],
                    'edc_data': visit['edc_data'],
                    'source_data': visit['source_data'],
                    'discrepancies': visit['discrepancies'],
                    'queries': visit['queries']
                }
    
    # Core data retrieval methods for agents
    
    async def get_subject_data(self, subject_id: str, data_source: str = "edc") -> Optional[Dict[str, Any]]:
        """Get complete subject data for specified source.
        
        Args:
            subject_id: Subject identifier
            data_source: "edc" or "source" or "both"
            
        Returns:
            Subject data dictionary or None if not found
        """
        if not self.settings.use_test_data or subject_id not in self.test_data_cache['subjects']:
            return None
            
        subject = self.test_data_cache['subjects'][subject_id]
        
        if data_source == "both":
            return {
                'subject_info': {
                    'subject_id': subject['subject_id'],
                    'site_id': subject['site_id'],
                    'demographics': subject['demographics'],
                    'overall_status': subject['overall_status']
                },
                'edc_data': self._extract_all_visit_data(subject, 'edc_data'),
                'source_data': self._extract_all_visit_data(subject, 'source_data'),
                'data_quality': subject['data_quality']
            }
        elif data_source == "edc":
            return {
                'subject_info': {
                    'subject_id': subject['subject_id'],
                    'site_id': subject['site_id'],
                    'demographics': subject['demographics']
                },
                'visit_data': self._extract_all_visit_data(subject, 'edc_data')
            }
        elif data_source == "source":
            return {
                'subject_info': {
                    'subject_id': subject['subject_id'],
                    'site_id': subject['site_id'],
                    'demographics': subject['demographics']
                },
                'visit_data': self._extract_all_visit_data(subject, 'source_data')
            }
        
        return None
    
    async def get_visit_data(self, subject_id: str, visit_name: str, data_source: str = "edc") -> Optional[Dict[str, Any]]:
        """Get specific visit data.
        
        Args:
            subject_id: Subject identifier
            visit_name: Visit name (e.g., "Baseline", "Week_4")
            data_source: "edc" or "source" or "both"
            
        Returns:
            Visit data dictionary or None if not found
        """
        if not self.settings.use_test_data:
            return None
            
        key = f"{subject_id}_{visit_name}"
        if key not in self.test_data_cache['visit_data']:
            return None
            
        visit_data = self.test_data_cache['visit_data'][key]
        
        if data_source == "both":
            return visit_data
        elif data_source == "edc":
            return {
                'subject_id': visit_data['subject_id'],
                'visit_name': visit_data['visit_name'],
                'data': visit_data['edc_data']
            }
        elif data_source == "source":
            return {
                'subject_id': visit_data['subject_id'],
                'visit_name': visit_data['visit_name'],
                'data': visit_data['source_data']
            }
            
        return None
    
    async def get_discrepancies(self, subject_id: str, visit_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get known discrepancies for testing Data Verifier agent.
        
        Args:
            subject_id: Subject identifier
            visit_name: Optional visit name filter
            
        Returns:
            List of discrepancy dictionaries
        """
        if not self.settings.use_test_data:
            return []
            
        discrepancies = []
        
        if visit_name:
            # Get discrepancies for specific visit
            key = f"{subject_id}_{visit_name}"
            if key in self.test_data_cache['visit_data']:
                discrepancies.extend(self.test_data_cache['visit_data'][key]['discrepancies'])
        else:
            # Get all discrepancies for subject
            subject = self.test_data_cache['subjects'].get(subject_id)
            if subject:
                for visit in subject['visits']:
                    discrepancies.extend(visit['discrepancies'])
        
        return discrepancies
    
    async def get_queries(self, subject_id: str, visit_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get existing queries for testing Query Tracker agent.
        
        Args:
            subject_id: Subject identifier  
            visit_name: Optional visit name filter
            
        Returns:
            List of query dictionaries
        """
        if not self.settings.use_test_data:
            return []
            
        queries = []
        
        if visit_name:
            # Get queries for specific visit
            key = f"{subject_id}_{visit_name}"
            if key in self.test_data_cache['visit_data']:
                queries.extend(self.test_data_cache['visit_data'][key]['queries'])
        else:
            # Get all queries for subject
            subject = self.test_data_cache['subjects'].get(subject_id)
            if subject:
                for visit in subject['visits']:
                    queries.extend(visit['queries'])
        
        return queries
    
    async def get_site_data(self, site_id: str) -> Optional[Dict[str, Any]]:
        """Get site information and performance metrics.
        
        Args:
            site_id: Site identifier
            
        Returns:
            Site data dictionary or None if not found
        """
        if not self.settings.use_test_data:
            return None
            
        return self.test_data_cache['sites'].get(site_id)
    
    async def get_study_info(self) -> Optional[Dict[str, Any]]:
        """Get current study information.
        
        Returns:
            Study information dictionary
        """
        if not self.settings.use_test_data or not self.current_study:
            return None
            
        return self.current_study['study_info']
    
    # Data analysis methods for agent testing
    
    async def get_subjects_with_discrepancies(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get subjects that have discrepancies for testing purposes.
        
        Args:
            severity: Optional severity filter ("critical", "major", "minor")
            
        Returns:
            List of subjects with discrepancy information
        """
        if not self.settings.use_test_data:
            return []
            
        subjects_with_discrepancies = []
        
        for subject in self.current_study['subjects']:
            subject_discrepancies = []
            
            for visit in subject['visits']:
                if severity:
                    visit_discrepancies = [
                        d for d in visit['discrepancies'] 
                        if d['severity'] == severity
                    ]
                else:
                    visit_discrepancies = visit['discrepancies']
                
                subject_discrepancies.extend(visit_discrepancies)
            
            if subject_discrepancies:
                subjects_with_discrepancies.append({
                    'subject_id': subject['subject_id'],
                    'site_id': subject['site_id'],
                    'discrepancy_count': len(subject_discrepancies),
                    'discrepancies': subject_discrepancies
                })
        
        return subjects_with_discrepancies
    
    async def get_site_performance_data(self) -> List[Dict[str, Any]]:
        """Get site performance data for testing Portfolio Manager.
        
        Returns:
            List of site performance summaries
        """
        if not self.settings.use_test_data:
            return []
            
        site_performance = []
        
        for site_id, site_info in self.test_data_cache['sites'].items():
            # Calculate actual performance from subject data
            site_subjects = [
                s for s in self.current_study['subjects'] 
                if s['site_id'] == site_id
            ]
            
            total_subjects = len(site_subjects)
            total_queries = sum(s['data_quality']['query_count'] for s in site_subjects)
            total_discrepancies = sum(s['data_quality']['discrepant_data_points'] for s in site_subjects)
            total_critical = sum(s['data_quality']['critical_findings'] for s in site_subjects)
            
            site_performance.append({
                'site_id': site_id,
                'site_name': site_info['site_name'],
                'country': site_info['country'],
                'investigator': site_info['investigator'],
                'metrics': {
                    'enrolled_subjects': total_subjects,
                    'total_queries': total_queries,
                    'total_discrepancies': total_discrepancies,
                    'critical_findings': total_critical,
                    'query_rate': total_queries / max(total_subjects, 1),
                    'discrepancy_rate': total_discrepancies / max(total_subjects * 50, 1)  # Assume 50 data points per subject
                }
            })
        
        return site_performance
    
    # Utility methods
    
    def _extract_all_visit_data(self, subject: Dict, data_key: str) -> Dict[str, Any]:
        """Extract all visit data of specified type for a subject."""
        visit_data = {}
        for visit in subject['visits']:
            visit_data[visit['visit_name']] = visit[data_key]
        return visit_data
    
    def is_test_mode(self) -> bool:
        """Check if system is running in test data mode."""
        return self.settings.use_test_data and self.current_study is not None
    
    def get_available_subjects(self) -> List[str]:
        """Get list of available subject IDs."""
        if not self.settings.use_test_data:
            return []
        return list(self.test_data_cache['subjects'].keys())
    
    def get_available_sites(self) -> List[str]:
        """Get list of available site IDs."""
        if not self.settings.use_test_data:
            return []
        return list(self.test_data_cache['sites'].keys())
    
    async def regenerate_test_data(self, preset_name: str = None) -> bool:
        """Regenerate test data with optional different preset.
        
        Args:
            preset_name: Optional preset name to use
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if preset_name and preset_name in STUDY_PRESETS:
                self.current_study = generate_test_study(preset_name)
            else:
                # Use current preset
                current_preset = getattr(self.settings, 'test_data_preset', 'cardiology_phase2')
                self.current_study = generate_test_study(current_preset)
            
            self._build_lookup_cache()
            logger.info("Test data regenerated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to regenerate test data: {e}")
            return False

# Example usage in agent functions
async def get_test_data_for_agents(test_data_service: TestDataService) -> Dict[str, Any]:
    """Example of how agents can access test data."""
    
    if not test_data_service.is_test_mode():
        return {"message": "Test data not available"}
    
    # Example data for different agent needs
    return {
        "study_info": await test_data_service.get_study_info(),
        "available_subjects": test_data_service.get_available_subjects(),
        "subjects_with_discrepancies": await test_data_service.get_subjects_with_discrepancies(),
        "site_performance": await test_data_service.get_site_performance_data(),
        "example_subject_data": await test_data_service.get_subject_data(
            test_data_service.get_available_subjects()[0], "both"
        ) if test_data_service.get_available_subjects() else None
    }