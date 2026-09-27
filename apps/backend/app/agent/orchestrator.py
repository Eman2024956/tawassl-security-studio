import json
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import aiosqlite

from apps.backend.app.agent.budgets import BudgetTracker, BudgetExhaustedError
from apps.backend.app.policy.engine import PolicyEngine
from apps.backend.app.policy.models import ScopeRule
from apps.backend.app.ai.base import BaseAIProvider
from apps.backend.app.worker.runner import IsolatedWorker
from apps.backend.app.api.approvals import compute_proposal_hash
from apps.backend.app.tools.ast_inspector import inspect_python_source

logger = logging.getLogger("tawassl.agent")


class AssessmentOrchestrator:
    """
    Agent execution loop coordinator enforcing:
    Objective -> Plan -> Proposal -> Policy Validation -> Approval -> Isolated Execution -> Evidence -> Finding.
    """

    def __init__(
        self,
        assessment_id: str,
        target_info: Dict[str, Any],
        scope_rule: ScopeRule,
        profile: str,
        ai_provider: BaseAIProvider,
        budget_tracker: BudgetTracker,
        db_path: str
    ):
        self.assessment_id = assessment_id
        self.target_info = target_info
        self.scope_rule = scope_rule
        self.profile = profile
        self.ai = ai_provider
        self.budgets = budget_tracker
        self.db_path = db_path
        self.policy = PolicyEngine(self.scope_rule)
        self.worker = IsolatedWorker()

    async def execute_step(self) -> Dict[str, Any]:
        """Executes a single orchestrated agent step under budget constraints."""
        self.budgets.record_step()

        # Step 1: AI generates assessment plan & tool calls
        plan_response = await self.ai.generate_assessment_plan(
            target_info=self.target_info,
            profile=self.profile,
            catalog_modules=[]
        )

        step_results = []

        for call in plan_response.tool_calls:
            self.budgets.record_tool_call()

            # Step 2: Policy Engine Validation
            policy_check = self.policy.evaluate_proposal(call.tool_name, call.arguments)
            if not policy_check.allowed:
                step_results.append({
                    "tool": call.tool_name,
                    "status": "policy_denied",
                    "reason": policy_check.reason
                })
                continue

            # Step 3: Record Immutable Proposal in Database
            proposal_id = str(uuid.uuid4())
            prop_hash = compute_proposal_hash(self.assessment_id, call.tool_name, call.arguments)

            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO proposals (
                        id, assessment_id, tool_name, arguments_json, arguments_hash,
                        purpose, side_effects, resource_limits_json, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
                    """,
                    (
                        proposal_id,
                        self.assessment_id,
                        call.tool_name,
                        json.dumps(call.arguments),
                        prop_hash,
                        call.rationale or "Diagnostic security check",
                        "Bounded diagnostic inspection",
                        json.dumps({"timeout_sec": 30, "max_output_kb": 512, "network_restricted": True})
                    )
                )
                await db.commit()

            step_results.append({
                "tool": call.tool_name,
                "proposal_id": proposal_id,
                "status": "awaiting_approval",
                "arguments": call.arguments
            })

        return {
            "step": self.budgets.steps_taken,
            "results": step_results,
            "budgets": self.budgets.get_summary()
        }
