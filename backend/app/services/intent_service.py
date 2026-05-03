"""Intent classification and slot extraction."""

from __future__ import annotations

import json

from app.repositories.knowledge_point_repository import KnowledgePointRepository
from app.schemas.chat import IntentResult
from app.services.llm import LLMMessage, LLMService


class IntentService:
    """Hybrid intent recognition with LLM and rule fallback."""

    def __init__(
        self,
        *,
        llm_service: LLMService,
        knowledge_point_repository: KnowledgePointRepository,
    ) -> None:
        self.llm_service = llm_service
        self.knowledge_point_repository = knowledge_point_repository

    async def classify(self, *, message: str) -> IntentResult:
        llm_result = await self._classify_with_llm(message)
        if llm_result is not None:
            if not list(llm_result.slots.get("knowledge_point_ids") or []):
                fallback_kp_ids = await self._extract_knowledge_points(message)
                if fallback_kp_ids:
                    llm_result.slots["knowledge_point_ids"] = fallback_kp_ids
            return llm_result
        return await self._classify_with_rules(message)

    async def _classify_with_llm(self, message: str) -> IntentResult | None:
        prompt = (
            "你是意图识别器。请只输出 JSON，字段为: "
            "primary_intent, slots。"
            "primary_intent 仅允许 CLARIFY_CONCEPT/SOLVE_PROBLEM/PLAN_REQUEST。"
            "slots 可包含 concept 与 knowledge_point_ids(字符串数组)。"
        )
        raw = await self.llm_service.chat(
            messages=[
                LLMMessage(role="system", content=prompt),
                LLMMessage(role="user", content=message),
            ],
            temperature=0.0,
            max_tokens=200,
            fallback_text="",
        )
        if not raw:
            return None
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return None
        primary_intent = str(payload.get("primary_intent") or "").strip()
        slots = payload.get("slots") if isinstance(payload.get("slots"), dict) else {}
        kp_ids = slots.get("knowledge_point_ids")
        if not isinstance(kp_ids, list):
            kp_ids = []
        valid_kp_ids = await self._filter_valid_knowledge_points([str(item) for item in kp_ids])
        slots["knowledge_point_ids"] = valid_kp_ids
        if primary_intent not in {"CLARIFY_CONCEPT", "SOLVE_PROBLEM", "PLAN_REQUEST"}:
            primary_intent = "CLARIFY_CONCEPT"
        return IntentResult(primary_intent=primary_intent, slots=slots)

    async def _classify_with_rules(self, message: str) -> IntentResult:
        text = message.strip()
        if any(word in text for word in ["计划", "安排", "复习计划"]):
            primary_intent = "PLAN_REQUEST"
        elif any(word in text for word in ["不会", "做不出", "怎么解", "题"]):
            primary_intent = "SOLVE_PROBLEM"
        else:
            primary_intent = "CLARIFY_CONCEPT"

        slots: dict = {}
        kp_ids = await self._extract_knowledge_points(text)
        if kp_ids:
            slots["knowledge_point_ids"] = kp_ids
        return IntentResult(primary_intent=primary_intent, slots=slots)

    async def _extract_knowledge_points(self, text: str) -> list[str]:
        all_points = await self.knowledge_point_repository.list(subject="math")
        matched: list[str] = []
        for item in all_points:
            if item.name in text:
                matched.append(item.id)

        keyword_mapping: list[tuple[str, str]] = [
            ("三角函数", "kp_trig_def"),
            ("正弦", "kp_sin_func"),
            ("余弦", "kp_cos_func"),
            ("复合函数单调", "kp_comp_func_mono"),
            ("复合函数求导", "kp_derivative_chain"),
            ("链式法则", "kp_derivative_chain"),
            ("导数定义", "kp_derivative_concept"),
            ("导数概念", "kp_derivative_concept"),
            ("求导法则", "kp_derivative_basic"),
            ("导数", "kp_derivative_concept"),
            ("单调性", "kp_func_mono"),
        ]
        for keyword, kp_id in keyword_mapping:
            if keyword in text and kp_id not in matched:
                matched.append(kp_id)
        return matched[:3]

    async def _filter_valid_knowledge_points(self, kp_ids: list[str]) -> list[str]:
        if not kp_ids:
            return []
        points = await self.knowledge_point_repository.get_by_ids(kp_ids)
        valid = {item.id for item in points}
        return [item for item in kp_ids if item in valid]
