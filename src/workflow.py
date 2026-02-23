"""
Core workflow - 极简实现，无框架依赖
"""

import asyncio
import json
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List, Optional, Protocol

from .llm_provider import ProviderRegistry
from .prompt_loader import PromptLoader
from .srt_parser import SRTParser


class TextGenerator(Protocol):
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        system_prompt: str | None = None,
        extra_payload: Dict[str, Any] | None = None,
    ) -> str:
        ...


@dataclass
class KnowledgePoint:
    """知识点"""

    title: str
    content: str
    video_markers: List[Dict[str, str]] = field(default_factory=list)
    source_file: str = ""
    importance: int = 3  # 1-5


@dataclass
class Document:
    """文档对象"""

    path: Path
    content: str = ""
    course_name: Optional[str] = None
    knowledge_points: List[KnowledgePoint] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticSegment:
    """语义分段"""

    title: str
    start_line: int
    end_line: int
    content: str


@dataclass
class TextChunk:
    """最终处理分块"""

    title: str
    content: str
    start_line: int
    end_line: int
    segment_index: int


class ProgressTracker:
    """SQLite 进度追踪 - 替代外部队列"""

    def __init__(self, db_path: str = "knowledge.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                path TEXT UNIQUE,
                status TEXT DEFAULT 'pending',
                stage TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS knowledge_points (
                id INTEGER PRIMARY KEY,
                doc_id INTEGER,
                title TEXT,
                content TEXT,
                video_markers TEXT,
                source_file TEXT,
                FOREIGN KEY (doc_id) REFERENCES documents(id)
            );
            """
        )
        conn.commit()
        conn.close()

    def add_document(self, path: str) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "INSERT OR IGNORE INTO documents (path, status) VALUES (?, 'pending')",
            (path,),
        )
        conn.commit()
        doc_id = cursor.lastrowid or self._get_doc_id(path)
        conn.close()
        return doc_id

    def _get_doc_id(self, path: str) -> int:
        conn = sqlite3.connect(self.db_path)
        row = conn.execute("SELECT id FROM documents WHERE path = ?", (path,)).fetchone()
        conn.close()
        return row[0] if row else 0

    def update_status(
        self, doc_id: int, status: str, stage: Optional[str] = None, result: Optional[str] = None
    ) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "UPDATE documents SET status = ?, stage = ?, result = ? WHERE id = ?",
            (status, stage, result, doc_id),
        )
        conn.commit()
        conn.close()

    def save_knowledge_point(self, doc_id: int, point: KnowledgePoint) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """INSERT INTO knowledge_points (doc_id, title, content, video_markers, source_file)
               VALUES (?, ?, ?, ?, ?)""",
            (
                doc_id,
                point.title,
                point.content,
                json.dumps(point.video_markers, ensure_ascii=False),
                point.source_file,
            ),
        )
        conn.commit()
        conn.close()


class TextCleaner:
    """Stage 1: 规则清理，无需 LLM。"""

    DEFAULT_NOISE_PATTERNS = [
        (
            r"\b(um|uh|uhh|erm|like|you know|right|so|well|okay|ok|actually|basically|literally)\b[,.]?\s*",
            "",
        ),
        (r"(嗯+|啊+|哦+|哎+|唉+|哼+)[,，]?\s*", ""),
        (r"(对吧|那个|这个|就是|然后)[,，]?\s*", ""),
        (r"(大家可以看到|我们来看一下|好的|那么)[,，]?\s*", ""),
        (r"\n\s*\n\s*\n+", "\n\n"),
    ]

    def __init__(self, rules_reference_path: Path | None = None):
        self.noise_patterns = self._load_noise_patterns_from_markdown(rules_reference_path)

    def _load_noise_patterns_from_markdown(
        self, rules_reference_path: Path | None
    ) -> List[tuple[str, str]]:
        if not rules_reference_path or not rules_reference_path.exists():
            return self.DEFAULT_NOISE_PATTERNS

        try:
            markdown = rules_reference_path.read_text(encoding="utf-8")
            rows = re.findall(
                r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|\s*`([^`]*)`\s*\|",
                markdown,
                flags=re.MULTILINE,
            )
            if not rows:
                return self.DEFAULT_NOISE_PATTERNS
            normalized: List[tuple[str, str]] = []
            for pattern, replacement in rows:
                try:
                    pattern_decoded = bytes(pattern, "utf-8").decode("unicode_escape")
                    replacement_decoded = bytes(replacement, "utf-8").decode("unicode_escape")
                except Exception:
                    pattern_decoded = pattern
                    replacement_decoded = replacement
                normalized.append((pattern_decoded, replacement_decoded))
            return normalized or self.DEFAULT_NOISE_PATTERNS
        except Exception:
            return self.DEFAULT_NOISE_PATTERNS

    def clean(self, text: str) -> str:
        original_length = len(text)
        for pattern, replacement in self.noise_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r" +\n", "\n", text)
        text = re.sub(r"\n +", "\n", text)

        if len(text) < original_length * 0.3:
            text = re.sub(r"\s+", " ", text)
        return text.strip()


class MockLLMClient:
    """模拟 LLM 客户端 - 用于测试，不调用外部 API"""

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        system_prompt: str | None = None,
        extra_payload: Dict[str, Any] | None = None,
    ) -> str:
        await asyncio.sleep(0.02)
        prompt_lower = prompt.lower()

        if "语义分段任务" in prompt:
            total_lines_match = re.search(r"总行数:\s*(\d+)", prompt)
            total_lines = int(total_lines_match.group(1)) if total_lines_match else 1000
            mid = max(2, total_lines // 2)
            return json.dumps(
                {
                    "segments": [
                        {"title": "前半部分", "start_line": 1, "end_line": mid},
                        {
                            "title": "后半部分",
                            "start_line": mid + 1,
                            "end_line": total_lines,
                        },
                    ]
                },
                ensure_ascii=False,
            )
        if "子切分任务" in prompt:
            return json.dumps(
                {
                    "chunks": [
                        {
                            "title": "子块1",
                            "content": "这是子切后的内容块，保持原有语义顺序。",
                        }
                    ]
                },
                ensure_ascii=False,
            )
        if "清洗任务" in prompt:
            return "这是清洗后的核心内容，保留事实和观点。"
        if "结构化提取任务" in prompt:
            return """{
  "points": [
    {"title": "示例知识点", "content": "示例内容，包含细节。"}
  ]
}"""
        if "识别可以合并的相似主题" in prompt:
            return """{
  "merged_topics": [
    {
      "id": "topic_0",
      "title": "核心概念",
      "description": "合并后的核心概念",
      "original_indices": [0],
      "keywords": ["概念", "基础"]
    }
  ]
}"""
        if "识别其中的主题聚类" in prompt or "主题聚类" in prompt:
            return """{
  "topics": [
    {
      "id": "topic_0",
      "title": "核心概念",
      "description": "基础定义和原理",
      "point_indices": [0],
      "keywords": ["定义", "原理"]
    }
  ]
}"""
        if "设计教材的章节结构" in prompt:
            return """{
  "course_name": "示例课程",
  "chapters": [
    {
      "order": 1,
      "title": "核心概念",
      "topic_ids": ["topic_0"],
      "description": "掌握核心概念",
      "learning_objectives": ["理解基本定义"]
    }
  ],
  "prerequisites": {
    "核心概念": []
  }
}"""
        if "判断它们是否重复或高度相似" in prompt:
            return """{
  "is_duplicate": false,
  "best_title": "示例标题",
  "confidence": 0.2,
  "reason": "mock: 默认不判重"
}"""
        if "整合以下" in prompt:
            return "这是合并后的知识点内容。"
        if "写一段衔接段落" in prompt:
            return "上一章建立了基础概念，本章将在此基础上推进到更完整的应用场景。"
        if "需看视频画面" in prompt or ("视频" in prompt and "画面" in prompt):
            return "[需看视频画面: 00:01-00:10]（图示说明）\n示例内容。"
        if "json" in prompt_lower:
            return """{
  "points": [
    {"title": "示例知识点", "content": "示例内容"}
  ]
}"""
        if "清理" in prompt or "删除" in prompt or "干货" in prompt:
            return "这是清理后的核心内容。"
        return "模拟生成的内容。"


class WorkflowEngine:
    """工作流引擎 - 语义分段 + 清洗 + 结构化"""

    def __init__(
        self,
        providers: ProviderRegistry | TextGenerator,
        tracker: ProgressTracker,
        enable_video_mark: bool = False,
        chunk_size: int = 60000,
        output_dir: str = "./exports",
        split_output_dirs: bool = False,
        skills_dir: str | Path | None = None,
    ):
        if isinstance(providers, ProviderRegistry):
            self.providers = providers
            self.llm = providers.get()
            self.chunk_size = providers.chunk_size
        elif hasattr(providers, "generate"):
            self.providers = None
            self.llm = providers  # type: ignore[assignment]
            self.chunk_size = max(1000, int(chunk_size))
        else:
            raise TypeError("providers 必须是 ProviderRegistry 或具备 generate() 的对象")

        self.skills_dir = (
            Path(skills_dir)
            if skills_dir is not None
            else Path(__file__).resolve().parent.parent / "skills"
        )
        self.prompt_loader = PromptLoader(self.skills_dir)

        cleaning_rules_reference = (
            self.skills_dir / "transcript-cleaning" / "references" / "rule-patterns.md"
        )
        self.tracker = tracker
        self.cleaner = TextCleaner(rules_reference_path=cleaning_rules_reference)
        self.enable_video_mark = enable_video_mark
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.split_output_dirs = split_output_dirs
        if self.split_output_dirs:
            self.cleaned_output_dir = self.output_dir / "cleaned"
            self.structured_output_dir = self.output_dir / "structured"
            self.cleaned_output_dir.mkdir(parents=True, exist_ok=True)
            self.structured_output_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.cleaned_output_dir = self.output_dir
            self.structured_output_dir = self.output_dir

    async def process_document(self, doc_path: Path) -> Document:
        """处理单个文档并输出清洗/结构化两份结果"""
        total_started = perf_counter()
        stage_durations: Dict[str, float] = {}
        doc_id = self.tracker.add_document(str(doc_path))
        doc = Document(path=doc_path, content=self._load_document_content(doc_path))
        processed_chars = len(doc.content)

        self.tracker.update_status(doc_id, "processing", "rule_cleaning")
        stage_started = perf_counter()
        doc.content = self.cleaner.clean(doc.content)
        stage_durations["rule_cleaning"] = perf_counter() - stage_started

        self.tracker.update_status(doc_id, "processing", "semantic_segmentation")
        stage_started = perf_counter()
        semantic_segments = await self._stage_semantic_segmentation(doc.content)
        stage_durations["semantic_segmentation"] = perf_counter() - stage_started

        self.tracker.update_status(doc_id, "processing", "sub_chunking")
        stage_started = perf_counter()
        chunks = await self._stage_sub_chunk(semantic_segments)
        stage_durations["sub_chunking"] = perf_counter() - stage_started

        self.tracker.update_status(doc_id, "processing", "noise_reduction")
        stage_started = perf_counter()
        cleaned_chunks = await self._stage_noise_reduction(chunks)
        stage_durations["noise_reduction"] = perf_counter() - stage_started
        doc.content = "\n\n".join(chunk.content for chunk in cleaned_chunks).strip()

        cleaned_output = self._save_cleaned_markdown(doc.path, semantic_segments, cleaned_chunks)

        self.tracker.update_status(doc_id, "processing", "structuring")
        stage_started = perf_counter()
        doc.knowledge_points = await self._stage_structure(cleaned_chunks, doc.path)
        stage_durations["structuring"] = perf_counter() - stage_started
        structured_output = self._save_structured_markdown(
            doc.path, doc.knowledge_points, cleaned_chunks
        )

        if self.enable_video_mark:
            self.tracker.update_status(doc_id, "processing", "video_marking")
            stage_started = perf_counter()
            doc = await self._stage_video_mark(doc)
            stage_durations["video_marking"] = perf_counter() - stage_started
        else:
            self.tracker.update_status(doc_id, "processing", "video_marking_skipped")
            stage_durations["video_marking"] = 0.0

        doc.metadata["chunk_size"] = self.chunk_size
        doc.metadata["semantic_segments"] = [
            {
                "title": segment.title,
                "start_line": segment.start_line,
                "end_line": segment.end_line,
            }
            for segment in semantic_segments
        ]
        doc.metadata["chunk_count"] = len(cleaned_chunks)
        doc.metadata["cleaned_output"] = str(cleaned_output)
        doc.metadata["structured_output"] = str(structured_output)
        doc.metadata["processed_chars"] = processed_chars
        doc.metadata["extracted_chars"] = sum(len(point.content) for point in doc.knowledge_points)
        doc.metadata["stage_durations"] = stage_durations
        doc.metadata["total_duration"] = perf_counter() - total_started

        self.tracker.update_status(doc_id, "done", "completed")
        for point in doc.knowledge_points:
            self.tracker.save_knowledge_point(doc_id, point)

        return doc

    def _load_document_content(self, doc_path: Path) -> str:
        text = doc_path.read_text(encoding="utf-8")
        if doc_path.suffix.lower() not in {".srt", ".txt"}:
            return text

        entries = SRTParser.parse(text)
        if not entries:
            return text
        return SRTParser.to_plaintext(entries, include_timestamp=False)

    def _estimate_tokens(self, text: str) -> int:
        return max(1, int(len(text) / 3))

    def _load_skill_prompt(self, skill_name: str, reference_name: str, **variables: Any) -> str:
        return self.prompt_loader.load(skill_name, reference_name, **variables)

    async def _stage_semantic_segmentation(self, text: str) -> List[SemanticSegment]:
        lines = text.splitlines()
        if not lines:
            return [SemanticSegment(title="全文", start_line=1, end_line=1, content=text)]

        numbered_text = "\n".join(f"{idx + 1}|{line}" for idx, line in enumerate(lines))
        prompt = self._load_skill_prompt(
            "transcript-chunking",
            "semantic-segmentation",
            total_lines=len(lines),
            numbered_text=numbered_text,
        )
        try:
            result = await self.llm.generate(prompt, temperature=0.1)
            data = self._parse_json_response(result)
            raw_segments = data.get("segments", [])
            normalized = self._normalize_segments(raw_segments, len(lines))
            if not normalized:
                return [
                    SemanticSegment(
                        title="全文",
                        start_line=1,
                        end_line=len(lines),
                        content="\n".join(lines),
                    )
                ]

            segments: List[SemanticSegment] = []
            for item in normalized:
                start_line = item["start_line"]
                end_line = item["end_line"]
                content = "\n".join(lines[start_line - 1 : end_line]).strip()
                if not content:
                    continue
                segments.append(
                    SemanticSegment(
                        title=item["title"],
                        start_line=start_line,
                        end_line=end_line,
                        content=content,
                    )
                )
            if segments:
                return segments
        except Exception as exc:
            print(f"语义分段失败，回退为单段: {exc}")

        return [
            SemanticSegment(
                title="全文",
                start_line=1,
                end_line=len(lines),
                content="\n".join(lines),
            )
        ]

    def _normalize_segments(
        self, raw_segments: Any, total_lines: int
    ) -> List[Dict[str, int | str]]:
        if not isinstance(raw_segments, list):
            return []

        parsed: List[Dict[str, int | str]] = []
        for idx, item in enumerate(raw_segments):
            if not isinstance(item, dict):
                continue
            try:
                start = int(item.get("start_line", 0))
                end = int(item.get("end_line", 0))
            except (TypeError, ValueError):
                continue
            if end < start or start <= 0:
                continue
            start = max(1, min(start, total_lines))
            end = max(1, min(end, total_lines))
            if end < start:
                continue
            title = str(item.get("title", f"段落{idx + 1}")).strip() or f"段落{idx + 1}"
            parsed.append({"title": title, "start_line": start, "end_line": end})

        if not parsed:
            return []

        parsed.sort(key=lambda x: int(x["start_line"]))
        normalized: List[Dict[str, int | str]] = []
        cursor = 1
        for item in parsed:
            start = max(cursor, int(item["start_line"]))
            if start > total_lines:
                break
            end = max(start, int(item["end_line"]))
            end = min(end, total_lines)
            normalized.append(
                {"title": str(item["title"]), "start_line": start, "end_line": end}
            )
            cursor = end + 1
            if cursor > total_lines:
                break

        if cursor <= total_lines:
            normalized.append(
                {"title": "尾部补全", "start_line": cursor, "end_line": total_lines}
            )
        return normalized

    async def _stage_sub_chunk(self, segments: List[SemanticSegment]) -> List[TextChunk]:
        chunks: List[TextChunk] = []
        for segment_idx, segment in enumerate(segments):
            token_count = self._estimate_tokens(segment.content)
            if token_count <= self.chunk_size:
                chunks.append(
                    TextChunk(
                        title=segment.title,
                        content=segment.content,
                        start_line=segment.start_line,
                        end_line=segment.end_line,
                        segment_index=segment_idx,
                    )
                )
                continue

            subchunks = await self._llm_sub_chunk_segment(segment)
            if not subchunks:
                subchunks = self._fallback_sub_chunk(segment)
            chunks.extend(subchunks)
        return chunks

    async def _llm_sub_chunk_segment(self, segment: SemanticSegment) -> List[TextChunk]:
        prompt = self._load_skill_prompt(
            "transcript-chunking",
            "sub-chunking",
            chunk_size=self.chunk_size,
            segment_title=segment.title,
            segment_start_line=segment.start_line,
            segment_end_line=segment.end_line,
            segment_content=segment.content,
        )
        try:
            result = await self.llm.generate(prompt, temperature=0.1)
            data = self._parse_json_response(result)
            raw_chunks = data.get("chunks", [])
            if not isinstance(raw_chunks, list):
                return []

            normalized: List[TextChunk] = []
            for idx, item in enumerate(raw_chunks):
                if not isinstance(item, dict):
                    continue
                title = str(item.get("title", f"{segment.title}-子块{idx + 1}")).strip()
                content = str(item.get("content", "")).strip()
                if not content:
                    continue
                if self._estimate_tokens(content) > int(self.chunk_size * 1.2):
                    for fallback_idx, piece in enumerate(
                        self._split_text_by_char_limit(content, self.chunk_size * 3)
                    ):
                        normalized.append(
                            TextChunk(
                                title=f"{title}-fallback-{fallback_idx + 1}",
                                content=piece,
                                start_line=segment.start_line,
                                end_line=segment.end_line,
                                segment_index=0,
                            )
                        )
                    continue
                normalized.append(
                    TextChunk(
                        title=title,
                        content=content,
                        start_line=segment.start_line,
                        end_line=segment.end_line,
                        segment_index=0,
                    )
                )
            return normalized
        except Exception as exc:
            print(f"子切分失败，回退规则切分: {exc}")
            return []

    def _fallback_sub_chunk(self, segment: SemanticSegment) -> List[TextChunk]:
        pieces = self._split_text_by_char_limit(segment.content, self.chunk_size * 3)
        return [
            TextChunk(
                title=f"{segment.title}-子块{idx + 1}",
                content=piece,
                start_line=segment.start_line,
                end_line=segment.end_line,
                segment_index=0,
            )
            for idx, piece in enumerate(pieces)
            if piece.strip()
        ]

    def _split_text_by_char_limit(self, text: str, limit: int) -> List[str]:
        lines = [line for line in text.splitlines() if line.strip()]
        if not lines:
            return [text]
        chunks: List[str] = []
        current = ""
        for line in lines:
            candidate = f"{current}\n{line}" if current else line
            if len(candidate) <= limit:
                current = candidate
                continue
            if current:
                chunks.append(current)
            if len(line) <= limit:
                current = line
                continue
            # 单行超限，硬切
            for idx in range(0, len(line), limit):
                piece = line[idx : idx + limit]
                if len(piece) == limit:
                    chunks.append(piece)
                else:
                    current = piece
        if current:
            chunks.append(current)
        return chunks

    async def _stage_noise_reduction(self, chunks: List[TextChunk]) -> List[TextChunk]:
        if not chunks:
            return []

        semaphore = asyncio.Semaphore(4)
        progress_lock = asyncio.Lock()
        total = len(chunks)
        progress = {"done": 0}

        async def _tick() -> None:
            async with progress_lock:
                progress["done"] += 1
                done = progress["done"]
                msg = f"清洗 {done}/{total} 块..."
                if done < total:
                    print(f"\r{msg}", end="", flush=True)
                else:
                    print(f"\r{msg}")

        async def _clean_chunk(index: int, chunk: TextChunk) -> TextChunk:
            prompt = self._load_skill_prompt(
                "transcript-cleaning", "noise-reduction", chunk_content=chunk.content
            )
            try:
                async with semaphore:
                    cleaned = await self.llm.generate(prompt, temperature=0.1)
                cleaned = cleaned.strip()
                if not cleaned or len(cleaned) < int(len(chunk.content) * 0.35):
                    cleaned = chunk.content
                return TextChunk(
                    title=chunk.title,
                    content=cleaned,
                    start_line=chunk.start_line,
                    end_line=chunk.end_line,
                    segment_index=chunk.segment_index,
                )
            except Exception as exc:
                print(f"\n清洗分块失败 ({index + 1}/{total}): {exc}")
                return chunk
            finally:
                await _tick()

        return await asyncio.gather(
            *[_clean_chunk(index, chunk) for index, chunk in enumerate(chunks)]
        )

    async def _stage_structure(
        self, cleaned_chunks: List[TextChunk], source_path: Path
    ) -> List[KnowledgePoint]:
        if not cleaned_chunks:
            return [KnowledgePoint(title="内容摘要", content="", source_file=str(source_path))]

        semaphore = asyncio.Semaphore(4)
        progress_lock = asyncio.Lock()
        total = len(cleaned_chunks)
        progress = {"done": 0}

        async def _tick() -> None:
            async with progress_lock:
                progress["done"] += 1
                done = progress["done"]
                msg = f"结构化 {done}/{total} 块..."
                if done < total:
                    print(f"\r{msg}", end="", flush=True)
                else:
                    print(f"\r{msg}")

        async def _extract_chunk(index: int, chunk: TextChunk) -> List[KnowledgePoint]:
            prompt = self._load_skill_prompt(
                "knowledge-extraction",
                "structured-extraction",
                chunk_content=chunk.content,
            )
            try:
                async with semaphore:
                    result = await self.llm.generate(prompt, temperature=0.2)
                data = self._parse_json_response(result)
                raw_points = (
                    data.get("points")
                    or data.get("knowledge_points")
                    or data.get("items")
                    or []
                )
                parsed: List[KnowledgePoint] = []
                for item in raw_points:
                    if not isinstance(item, dict):
                        continue
                    title = str(item.get("title", "")).strip() or "未命名知识点"
                    content = str(item.get("content", "")).strip()
                    if not content:
                        continue
                    parsed.append(
                        KnowledgePoint(
                            title=title,
                            content=content,
                            source_file=str(source_path),
                        )
                    )
                return parsed
            except Exception as exc:
                print(f"\n结构化分块失败 ({index + 1}/{total}): {exc}")
                return []
            finally:
                await _tick()

        chunk_results = await asyncio.gather(
            *[_extract_chunk(i, chunk) for i, chunk in enumerate(cleaned_chunks)]
        )
        merged_points: List[KnowledgePoint] = []
        seen = set()
        for points in chunk_results:
            for point in points:
                key = f"{point.title}::{point.content}"
                if key in seen:
                    continue
                seen.add(key)
                merged_points.append(point)

        if not merged_points:
            merged_points = [
                KnowledgePoint(
                    title="内容摘要",
                    content="\n\n".join(chunk.content for chunk in cleaned_chunks)[:1000],
                    source_file=str(source_path),
                )
            ]
        return merged_points

    def _save_cleaned_markdown(
        self,
        source_path: Path,
        semantic_segments: List[SemanticSegment],
        cleaned_chunks: List[TextChunk],
    ) -> Path:
        out_path = self.cleaned_output_dir / f"{source_path.stem}_cleaned.md"
        lines: List[str] = [f"# {source_path.stem} 清洗结果", ""]
        lines.extend(
            [
                "## 分块策略",
                "",
                f"- chunk_size(token): {self.chunk_size}",
                f"- 语义分段数: {len(semantic_segments)}",
                f"- 最终处理分块数: {len(cleaned_chunks)}",
                "- 语义分段起始点:",
            ]
        )
        for idx, segment in enumerate(semantic_segments, 1):
            lines.append(
                f"  - S{idx}: line {segment.start_line} ({segment.title}) -> line {segment.end_line}"
            )
        lines.extend(["", "---", ""])

        for idx, chunk in enumerate(cleaned_chunks, 1):
            lines.extend(
                [
                    f"## Chunk {idx}: {chunk.title}",
                    f"_source_lines: {chunk.start_line}-{chunk.end_line}_",
                    "",
                    chunk.content.strip(),
                    "",
                ]
            )

        out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
        return out_path

    def _save_structured_markdown(
        self,
        source_path: Path,
        points: List[KnowledgePoint],
        cleaned_chunks: List[TextChunk],
    ) -> Path:
        out_path = self.structured_output_dir / f"{source_path.stem}_structured.md"
        lines: List[str] = [f"# {source_path.stem} 结构化结果", ""]
        lines.extend(
            [
                "## 统计",
                "",
                f"- 分块数: {len(cleaned_chunks)}",
                f"- 知识点数: {len(points)}",
                "",
                "---",
                "",
            ]
        )

        for idx, point in enumerate(points, 1):
            lines.extend([f"## {idx}. {point.title}", "", point.content.strip(), ""])

        out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
        return out_path

    async def _stage_video_mark(self, doc: Document) -> Document:
        for point in doc.knowledge_points:
            prompt = self._load_skill_prompt(
                "video-marking",
                "video-marking",
                point_title=point.title,
                point_content=point.content,
            )

            try:
                marked_content = await self.llm.generate(
                    prompt, temperature=0.2
                )
                point.content = marked_content
                point.video_markers = self._extract_video_markers(marked_content)
            except Exception as exc:
                print(f"视频标记失败: {exc}")
        return doc

    def _extract_video_markers(self, text: str) -> List[Dict[str, str]]:
        matches = re.findall(
            r"\[需看视频画面:\s*([^\]]+)\]\s*(?:[（(]([^）)]+)[）)])?",
            text,
        )
        markers: List[Dict[str, str]] = []
        for time_range, description in matches:
            markers.append(
                {
                    "time": str(time_range).strip(),
                    "description": str(description).strip() if description else "",
                }
            )
        return markers

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        patterns = [
            r"```json\s*\n(.*?)\n```",
            r"```\s*\n(.*?)\n```",
            r"(\{[\s\S]*\})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1).strip())
                except json.JSONDecodeError:
                    continue

        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
        return {}


class BatchProcessor:
    """批量处理器 - asyncio 并行"""

    def __init__(self, engine: WorkflowEngine, max_workers: int = 3):
        self.engine = engine
        self.semaphore = asyncio.Semaphore(max_workers)

    async def process_directory(self, dir_path: Path) -> List[Document]:
        files = sorted(list(dir_path.glob("*.srt")) + list(dir_path.glob("*.txt")))
        if not files:
            return []

        async def _process_one(file_path: Path) -> Document:
            async with self.semaphore:
                return await self.engine.process_document(file_path)

        tasks = [_process_one(file_path) for file_path in files]
        return await asyncio.gather(*tasks)
