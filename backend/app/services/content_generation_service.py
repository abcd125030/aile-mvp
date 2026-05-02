"""AI content generation service."""

from __future__ import annotations

import json

from app.core.exceptions import bad_request
from app.repositories.content_package_repository import ContentPackageRepository
from app.repositories.knowledge_point_repository import KnowledgePointRepository
from app.schemas.content import ContentGenerateRequest, ContentGenerateResponse, ContentSection
from app.services.llm import LLMMessage, LLMService


class ContentGenerationService:
    """Generate explain content and persist as content package."""

    def __init__(
        self,
        *,
        llm_service: LLMService,
        knowledge_point_repository: KnowledgePointRepository,
        content_package_repository: ContentPackageRepository,
    ) -> None:
        self.llm_service = llm_service
        self.knowledge_point_repository = knowledge_point_repository
        self.content_package_repository = content_package_repository
        self.session = content_package_repository.session

    async def generate(self, *, payload: ContentGenerateRequest) -> ContentGenerateResponse:
        points = await self.knowledge_point_repository.get_by_ids(payload.knowledge_point_ids)
        if not points:
            raise bad_request("未找到有效知识点，无法生成讲解内容")

        point_names = [item.name for item in points]
        sections = await self._generate_sections(
            knowledge_point_names=point_names,
            style=payload.style,
            target_minutes=payload.target_minutes,
        )
        manifest = {
            "sections": [item.model_dump() for item in sections],
            "knowledge_point_ids": [item.id for item in points],
            "style": payload.style,
            "target_minutes": payload.target_minutes,
        }
        package = await self.content_package_repository.create(manifest=manifest, status="ready")
        await self.session.commit()

        return ContentGenerateResponse(
            content_package_id=str(package.id),
            status=package.status,
            sections=sections,
        )

    async def _generate_sections(
        self,
        *,
        knowledge_point_names: list[str],
        style: str,
        target_minutes: int,
    ) -> list[ContentSection]:
        prompt = (
            "你是高中数学学习伙伴。请输出 JSON："
            '{"sections":[{"type":"text","content":"..."},{"type":"example","content":"..."}]}。'
            "要求：中文、简洁、鼓励式。"
        )
        user_prompt = (
            f"知识点: {', '.join(knowledge_point_names)}\n"
            f"风格: {style}\n"
            f"目标时长(分钟): {target_minutes}"
        )
        raw = await self.llm_service.chat(
            messages=[
                LLMMessage(role="system", content=prompt),
                LLMMessage(role="user", content=user_prompt),
            ],
            temperature=0.3,
            max_tokens=900,
            fallback_text="",
        )

        sections = self._parse_sections(raw)
        if sections:
            return sections

        # Fallback content keeps endpoint stable when model output is not valid JSON.
        return [
            ContentSection(
                type="text",
                content=f"我们先从“{knowledge_point_names[0]}”的核心概念入手，先抓住定义和判断方法。",
            ),
            ContentSection(
                type="example",
                content=f"例题：围绕“{knowledge_point_names[0]}”做一道基础题，先说思路再给答案。",
            ),
        ]

    @staticmethod
    def _parse_sections(raw: str) -> list[ContentSection]:
        if not raw:
            return []
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return []
        section_items = payload.get("sections")
        if not isinstance(section_items, list):
            return []
        normalized: list[ContentSection] = []
        for item in section_items:
            if not isinstance(item, dict):
                continue
            section_type = str(item.get("type") or "").strip().lower()
            content = str(item.get("content") or "").strip()
            if section_type not in {"text", "example"} or not content:
                continue
            normalized.append(ContentSection(type=section_type, content=content))
        return normalized[:8]
