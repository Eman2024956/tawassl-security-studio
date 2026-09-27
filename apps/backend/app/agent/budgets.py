import time
from typing import Optional
from pydantic import BaseModel


class BudgetExhaustedError(Exception):
    def __init__(self, resource_name: str, current_value: int | float, limit_value: int | float):
        self.resource_name = resource_name
        self.current_value = current_value
        self.limit_value = limit_value
        super().__init__(
            f"Hard Safety Budget Exhausted: {resource_name} reached {current_value} (limit: {limit_value}). Execution stopped."
        )


class BudgetTracker:
    """
    Manages and enforces hard execution budgets.
    Never silently resets counters. Any attempt to consume past the limit raises BudgetExhaustedError.
    """

    def __init__(
        self,
        max_steps: int = 20,
        max_requests: int = 50,
        max_tool_calls: int = 30,
        timeout_seconds: float = 300.0,
        max_output_bytes: int = 2 * 1024 * 1024
    ):
        self.max_steps = max_steps
        self.max_requests = max_requests
        self.max_tool_calls = max_tool_calls
        self.timeout_seconds = timeout_seconds
        self.max_output_bytes = max_output_bytes

        self.steps_taken = 0
        self.requests_made = 0
        self.tool_calls_made = 0
        self.bytes_produced = 0
        self.start_time = time.time()

    def record_step(self) -> None:
        self._check_timeout()
        if self.steps_taken >= self.max_steps:
            raise BudgetExhaustedError("steps", self.steps_taken + 1, self.max_steps)
        self.steps_taken += 1

    def record_request(self, count: int = 1) -> None:
        self._check_timeout()
        if self.requests_made + count > self.max_requests:
            raise BudgetExhaustedError("requests", self.requests_made + count, self.max_requests)
        self.requests_made += count

    def record_tool_call(self) -> None:
        self._check_timeout()
        if self.tool_calls_made >= self.max_tool_calls:
            raise BudgetExhaustedError("tool_calls", self.tool_calls_made + 1, self.max_tool_calls)
        self.tool_calls_made += 1

    def record_output(self, byte_count: int) -> None:
        self.bytes_produced += byte_count
        if self.bytes_produced > self.max_output_bytes:
            raise BudgetExhaustedError("output_bytes", self.bytes_produced, self.max_output_bytes)

    def _check_timeout(self) -> None:
        elapsed = time.time() - self.start_time
        if elapsed > self.timeout_seconds:
            raise BudgetExhaustedError("timeout_seconds", elapsed, self.timeout_seconds)

    def get_summary(self) -> dict:
        return {
            "steps_taken": self.steps_taken,
            "max_steps": self.max_steps,
            "requests_made": self.requests_made,
            "max_requests": self.max_requests,
            "tool_calls_made": self.tool_calls_made,
            "max_tool_calls": self.max_tool_calls,
            "elapsed_seconds": round(time.time() - self.start_time, 2),
            "timeout_seconds": self.timeout_seconds,
        }
