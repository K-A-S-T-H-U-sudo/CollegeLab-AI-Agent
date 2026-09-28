"""
Data models and structures for CollegeLab AI Agent reasoning.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import datetime


@dataclass
class Symptom:
    """Represents an observable system symptom or metric state."""
    key: str
    description: str
    observed_value: Any
    is_abnormal: bool
    category: str


@dataclass
class Fact:
    """A logical proposition asserted into working memory."""
    name: str
    value: Any
    confidence: float = 1.0
    source: str = "observation"  # "observation" or "inference"
    evidence: List[str] = field(default_factory=list)


@dataclass
class Rule:
    """A knowledge-base production rule (IF conditions THEN consequences)."""
    rule_id: str
    name: str
    antecedents: List[str]       # List of fact keys required (supports '!' prefix for negation)
    consequents: List[str]       # List of facts asserted when rule fires
    diagnosis_name: str
    category: str
    confidence_factor: float
    recommended_action: str
    action_key: Optional[str]
    explanation: str


@dataclass
class BayesianHypothesis:
    """Represents a diagnostic hypothesis with Bayesian prior and posterior."""
    fault_id: str
    name: str
    category: str
    prior: float
    likelihood_product: float = 1.0
    posterior: float = 0.0
    active_symptoms: List[str] = field(default_factory=list)
    math_breakdown: str = ""
    recommended_action: str = ""
    action_key: Optional[str] = None


@dataclass
class DiagnosisReport:
    """Comprehensive diagnostic outcome combining Logic and Bayesian reasoning."""
    timestamp: str
    computer_id: str
    lab_name: str
    overall_status: str  # "Healthy", "Warning", "Critical"
    primary_fault: Optional[str]
    category: str
    confidence: str      # "High", "Medium", "Low", "N/A"
    confidence_score: float
    confidence_reason: str = ""
    test_result_summary: str = ""
    what_was_observed: str = ""
    what_it_means: str = ""
    why_considered: str = ""
    why_others_less_likely: str = ""
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    reasoning_trace: List[str] = field(default_factory=list)
    backward_chaining_goals: List[Dict[str, Any]] = field(default_factory=list)
    bayesian_rankings: List[Dict[str, Any]] = field(default_factory=list)
    recommended_action: str = ""
    action_key: Optional[str] = None
    raw_diagnostics: Dict[str, Any] = field(default_factory=dict)

