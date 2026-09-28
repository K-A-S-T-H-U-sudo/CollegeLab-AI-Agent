"""
Bayesian Reasoning Engine for CollegeLab AI Agent.
Calculates posterior fault probabilities based on prior lab distributions and symptom likelihoods.
Provides explicit mathematical explanations of probability updates.
"""

from typing import List, Dict, Any, Tuple
from ai.models import Symptom, BayesianHypothesis
from ai.knowledge_base import BAYESIAN_HYPOTHESES, CATEGORIES


class BayesianEngine:
    """
    Computes P(Fault | Evidence) using Bayes' Theorem:
      P(H_i | E) = [ P(H_i) * P(E | H_i) ] / sum_k [ P(H_k) * P(E | H_k) ]

    Priors: Historical fault distribution in college laboratories.
    Likelihoods: P(Symptom | Hypothesis) representing true-positive/false-alarm rates.
    Evidence: Real observed test outcomes from local sensors.
    Posteriors: Probability distribution across all hypotheses given the real evidence.
    """

    def __init__(self, hypotheses_dict: Dict[str, Any] = None):
        self.hypotheses_def = hypotheses_dict or BAYESIAN_HYPOTHESES

    def _normalize_symptoms(self, symptoms: List[Symptom]) -> Dict[str, bool]:
        """
        Maps raw sensory symptoms into canonical boolean failure propositions.
        Each value is True IF the corresponding failure is observed.
        """
        # Default all failure propositions to False (nominal)
        presence = {
            "adapter_down": False,
            "no_valid_ip": False,
            "gateway_failed": False,
            "dns_failed": False,
            "internet_failed": False,
            "ram_high": False,
            "cpu_high": False,
            "disk_critical": False,
            "spooler_stopped": False
        }

        for sym in symptoms:
            k = sym.key
            abnormal = sym.is_abnormal

            if k == "adapter_up" and abnormal:
                presence["adapter_down"] = True
            elif k == "adapter_available" and abnormal:
                presence["adapter_down"] = True
            elif k == "has_valid_ip" and abnormal:
                presence["no_valid_ip"] = True
            elif k == "is_apipa" and bool(sym.observed_value):
                presence["no_valid_ip"] = True
            elif k == "gateway_failed" and abnormal:
                presence["gateway_failed"] = True
            elif k == "gateway_reachable" and abnormal:
                presence["gateway_failed"] = True
            elif k == "dns_failed" and abnormal:
                presence["dns_failed"] = True
            elif k == "dns_resolution_ok" and abnormal:
                presence["dns_failed"] = True
            elif k == "internet_failed" and abnormal:
                presence["internet_failed"] = True
            elif k == "internet_reachable" and abnormal:
                presence["internet_failed"] = True
            elif k == "ram_usage_high" and abnormal:
                presence["ram_high"] = True
            elif k == "cpu_usage_high" and abnormal:
                presence["cpu_high"] = True
            elif k == "disk_space_critical" and abnormal:
                presence["disk_critical"] = True
            elif k == "spooler_service_stopped" and abnormal:
                presence["spooler_stopped"] = True

        return presence

    def compute_posteriors(self, symptoms: List[Symptom]) -> List[BayesianHypothesis]:
        """
        Takes real observed symptoms, calculates likelihoods and posterior probabilities
        for all supported hypotheses, and provides an explainable mathematical breakdown.
        """
        symptom_presence = self._normalize_symptoms(symptoms)

        results: List[BayesianHypothesis] = []
        unnormalized_scores: Dict[str, float] = {}
        likelihood_products: Dict[str, float] = {}
        step_logs: Dict[str, List[str]] = {}
        active_symptoms_map: Dict[str, List[str]] = {}

        # 1. Compute Likelihood Product P(E | H_i) for each hypothesis
        for fault_id, data in self.hypotheses_def.items():
            prior = data["prior"]
            likelihood_prod = 1.0
            log = [
                f"Candidate Hypothesis: {data['name']} [{fault_id}]",
                f"1. Prior Probability P(H): {prior:.3f} ({prior * 100:.1f}%)",
                "2. Observed Diagnostic Evidence & Likelihood Factors:"
            ]
            active_symptoms = []

            for sym_key, p_sym_given_h in data["likelihoods"].items():
                is_failed = symptom_presence.get(sym_key, False)
                sym_readable = sym_key.replace("_", " ").title()

                if is_failed:
                    active_symptoms.append(sym_key)
                    # Symptom is present (failed)
                    p_e = p_sym_given_h
                    likelihood_prod *= p_e
                    log.append(f"   [FAIL] {sym_readable}: P(Fail | H) = {p_e:.2f}")
                else:
                    # Symptom is absent (passed)
                    p_e = 1.0 - p_sym_given_h
                    likelihood_prod *= p_e
                    log.append(f"   [PASS] {sym_readable}: P(Pass | H) = {p_e:.2f}")

            # Floor likelihood product to prevent division by zero
            likelihood_prod = max(likelihood_prod, 1e-12)
            likelihood_products[fault_id] = likelihood_prod
            score = prior * likelihood_prod
            unnormalized_scores[fault_id] = score
            step_logs[fault_id] = log
            active_symptoms_map[fault_id] = active_symptoms

        # 2. Total Marginal Probability P(E) = sum_k [ P(H_k) * P(E | H_k) ]
        total_marginal = sum(unnormalized_scores.values())
        if total_marginal <= 0:
            total_marginal = 1.0

        # 3. Compute Posterior P(H_i | E) and assemble hypotheses
        for fault_id, data in self.hypotheses_def.items():
            score = unnormalized_scores[fault_id]
            posterior = score / total_marginal

            log = step_logs[fault_id]
            log.append("3. Mathematical Bayesian Synthesis:")
            log.append(f"   Likelihood Product P(E | H) = {likelihood_products[fault_id]:.6e}")
            log.append(f"   Joint Probability P(H) * P(E | H) = {score:.6e}")
            log.append(f"   Marginal Probability P(E) = {total_marginal:.6e}")
            log.append(f"   Posterior Probability P(H | E) = {posterior:.4f} ({posterior * 100:.1f}%)")

            # Add plain-English verdict
            if posterior >= 0.70:
                log.append("   Verdict: HIGHLY PROBABLE root cause based on evidence alignment.")
            elif posterior >= 0.30:
                log.append("   Verdict: MODERATE probability; secondary factor or partially aligned.")
            elif posterior < 0.01:
                log.append("   Verdict: RULED OUT (< 1% posterior); evidence contradicts this fault.")
            else:
                log.append("   Verdict: LOW probability based on observed test successes.")

            breakdown_str = "\n".join(log)

            hyp = BayesianHypothesis(
                fault_id=fault_id,
                name=data["name"],
                category=data["category"],
                prior=data["prior"],
                likelihood_product=likelihood_products[fault_id],
                posterior=round(posterior, 4),
                active_symptoms=active_symptoms_map[fault_id],
                math_breakdown=breakdown_str,
                recommended_action=data.get("recommended_action", ""),
                action_key=data.get("action_key")
            )
            results.append(hyp)

        # Sort descending by posterior probability
        results.sort(key=lambda h: h.posterior, reverse=True)
        return results

    def explain_probability_shift(self, top_hyp: BayesianHypothesis, second_hyp: BayesianHypothesis = None) -> str:
        """
        Generates human-readable explanation of why the top hypothesis won.
        Identifies key distinguishing symptoms that shifted the probabilities.
        """
        if top_hyp.fault_id == "hyp_nominal":
            return (
                "Bayesian Analysis confirms the computer is in a nominal operational state. "
                f"Posterior probability is {top_hyp.posterior * 100:.1f}%. "
                "All real diagnostic sensors returned normal values, significantly decreasing the probability of all supported faults."
            )

        explanation = (
            f"Bayesian Analysis ranks '{top_hyp.name}' as the most probable cause "
            f"with a posterior confidence of {top_hyp.posterior * 100:.1f}% "
            f"(prior base rate was {top_hyp.prior * 100:.1f}%).\n"
        )
        if top_hyp.active_symptoms:
            readable_syms = [s.replace("_", " ").title() for s in top_hyp.active_symptoms]
            explanation += f"Key observed failure evidence driving this probability shift: {', '.join(readable_syms)}.\n"

        if second_hyp and second_hyp.posterior > 0.001:
            ratio = (top_hyp.posterior / max(second_hyp.posterior, 0.0001))
            explanation += (
                f"Compared to '{second_hyp.name}' ({second_hyp.posterior * 100:.1f}%), "
                f"the top hypothesis is {ratio:.1f}x more probable given the symptom pattern."
            )
        return explanation
