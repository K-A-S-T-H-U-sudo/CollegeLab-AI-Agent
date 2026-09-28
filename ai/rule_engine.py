"""
Explainable Logic & Knowledge Rule Engine for CollegeLab AI Agent.
Implements Propositional Logic, Working Memory, Forward Chaining, and Goal-Directed Backward Chaining.
"""

from typing import List, Dict, Any, Set, Tuple, Optional
from ai.models import Fact, Rule, Symptom
from ai.knowledge_base import RULES, CATEGORIES


class RuleEngine:
    """
    Inference Engine implementing:
    1. Working Memory (Fact Base)
    2. Forward Chaining (Data-driven inference)
    3. Backward Chaining (Goal-driven verification)
    4. Step-by-step explainable reasoning trace
    """

    def __init__(self, rules: List[Rule] = None):
        self.rules = rules or RULES
        self.working_memory: Dict[str, Fact] = {}
        self.fired_rules: List[Rule] = []
        self.reasoning_trace: List[str] = []

    def clear(self):
        """Resets working memory and reasoning logs."""
        self.working_memory.clear()
        self.fired_rules.clear()
        self.reasoning_trace.clear()

    def assert_fact(self, name: str, value: Any = True, confidence: float = 1.0, source: str = "observation"):
        """Adds or updates a proposition in working memory."""
        self.working_memory[name] = Fact(
            name=name,
            value=value,
            confidence=confidence,
            source=source
        )

    def load_symptoms(self, symptoms: List[Symptom]):
        """Populates initial working memory from real observed symptoms."""
        self.clear()
        for sym in symptoms:
            self.assert_fact(sym.key, sym.observed_value, confidence=1.0, source="observation")
            state_str = "ABNORMAL [X]" if sym.is_abnormal else "NORMAL [OK]"
            self.reasoning_trace.append(f"Perceived Observation: '{sym.key}' = {sym.observed_value} ({state_str})")

    def run_forward_chaining(self) -> List[Dict[str, Any]]:
        """
        Executes Forward Chaining:
        Continuously matches rule antecedents against working memory.
        Fires rules, asserts new inferred facts, and logs the deduction steps.
        Terminates when a fixed point is reached (no new rules can fire).
        """
        self.reasoning_trace.append("--- INITIATING FORWARD CHAINING INFERENCE ---")
        fired_ids: Set[str] = set()
        deduced_diagnoses: List[Dict[str, Any]] = []

        changed = True
        cycle = 1

        while changed:
            changed = False
            self.reasoning_trace.append(f"Inference Cycle {cycle}: Evaluating rule premises...")

            for rule in self.rules:
                if rule.rule_id in fired_ids:
                    continue

                # Check if all antecedents are satisfied in current working memory
                satisfied, condition_details = self._evaluate_antecedents(rule.antecedents)

                if satisfied:
                    fired_ids.add(rule.rule_id)
                    self.fired_rules.append(rule)
                    changed = True

                    # Assert consequents into working memory
                    for c in rule.consequents:
                        self.assert_fact(c, True, confidence=rule.confidence_factor, source=f"rule:{rule.rule_id}")

                    trace_msg = (
                        f"-> FIRED {rule.rule_id} ('{rule.name}'):\n"
                        f"   Conditions met: {', '.join(condition_details)}\n"
                        f"   Derived: {', '.join(rule.consequents)}\n"
                        f"   Diagnosis: {rule.diagnosis_name} (Confidence: {int(rule.confidence_factor * 100)}%)"
                    )
                    self.reasoning_trace.append(trace_msg)

                    deduced_diagnoses.append({
                        "rule_id": rule.rule_id,
                        "name": rule.diagnosis_name,
                        "category": rule.category,
                        "confidence_factor": rule.confidence_factor,
                        "recommended_action": rule.recommended_action,
                        "action_key": rule.action_key,
                        "explanation": rule.explanation,
                        "conditions_met": condition_details
                    })

            cycle += 1

        if not deduced_diagnoses:
            self.reasoning_trace.append("Forward chaining completed: No specific fault rules fired.")
        else:
            self.reasoning_trace.append(f"Forward chaining completed: {len(deduced_diagnoses)} conclusion(s) reached.")

        return deduced_diagnoses

    def _evaluate_antecedents(self, antecedents: List[str]) -> Tuple[bool, List[str]]:
        """
        Evaluates a conjunction (AND) of conditions.
        Supports negation via '!' prefix (e.g., '!gateway_reachable').
        """
        condition_details = []
        for antecedent in antecedents:
            if antecedent.startswith("!"):
                key = antecedent[1:]
                # Negation: condition is satisfied if key is missing or false
                fact = self.working_memory.get(key)
                if fact is not None and bool(fact.value):
                    return False, []
                condition_details.append(f"NOT {key} (Passed)")
            else:
                key = antecedent
                fact = self.working_memory.get(key)
                if fact is None or not bool(fact.value):
                    return False, []
                condition_details.append(f"{key} (True)")

        return True, condition_details

    def run_backward_chaining(self, target_goal: str) -> Dict[str, Any]:
        """
        Executes Goal-Driven Backward Chaining:
        Given a target hypothesis/goal (e.g. 'network_layer_broken'),
        determines whether the goal can be proved from the observed facts.
        """
        visited_goals = set()

        def prove(goal: str, depth: int = 0) -> Tuple[bool, List[str]]:
            indent = "  " * depth
            log = [f"{indent}Goal Query: Proving '{goal}'?"]

            if goal in visited_goals:
                log.append(f"{indent}Cycle detected for '{goal}'.")
                return False, log

            visited_goals.add(goal)

            # Check if directly in working memory
            if goal in self.working_memory and bool(self.working_memory[goal].value):
                log.append(f"{indent}Confirmed: '{goal}' is directly established in Working Memory.")
                return True, log

            # Check if any rule has this goal as consequent
            candidate_rules = [r for r in self.rules if goal in r.consequents]
            if not candidate_rules:
                log.append(f"{indent}Failed: No knowledge base rule derives '{goal}'.")
                return False, log

            for rule in candidate_rules:
                log.append(f"{indent}Investigating candidate {rule.rule_id} ('{rule.name}')...")
                all_subgoals_met = True

                for ante in rule.antecedents:
                    if ante.startswith("!"):
                        neg_key = ante[1:]
                        if neg_key in self.working_memory and bool(self.working_memory[neg_key].value):
                            all_subgoals_met = False
                            log.append(f"{indent}Subgoal '{ante}' disproved (found {neg_key}=True).")
                            break
                        else:
                            log.append(f"{indent}Subgoal '{ante}' confirmed satisfied.")
                    else:
                        sub_proved, sub_logs = prove(ante, depth + 1)
                        log.extend(sub_logs)
                        if not sub_proved:
                            all_subgoals_met = False
                            break

                if all_subgoals_met:
                    log.append(f"{indent}Success: {rule.rule_id} successfully proves '{goal}'!")
                    return True, log

            log.append(f"{indent}Failed to prove '{goal}' across all candidate rules.")
            return False, log

        proved, trace_logs = prove(target_goal)
        return {
            "goal": target_goal,
            "proved": proved,
            "proof_trace": trace_logs
        }
