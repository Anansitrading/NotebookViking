# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0
"""
NotebookLM storage backend for OpenViking.

Implements the VikingDBInterface using NotebookLM as the storage backend.
Maps collections to notebooks and uses query() for semantic search.

VERIFIED INTERFACES (2026-02-05):
- NotebookLMClient from notebooklm_mcp.api_client via pipx venv
- Methods: list_notebooks, create_notebook, add_text_source, query,
           delete_source, delete_notebook, get_notebook
- Client accessed via subprocess to ~/.local/share/pipx/venvs/notebooklm-mcp-server/bin/python
"""

import hashlib
import json
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from openviking.storage.vikingdb_interface import (
    CollectionNotFoundError,
    RecordNotFoundError,
    VikingDBInterface,
)
from openviking.utils import get_logger
from openviking.utils.config.notebooklm_config import NotebookLMConfig

logger = get_logger(__name__)

# Path to pipx-installed Python with notebooklm-mcp-server
PIPX_VENV_PYTHON = Path.home() / ".local/share/pipx/venvs/notebooklm-mcp-server/bin/python"


@dataclass
class NotebookLMResult:
    """Result from NotebookLM operation."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


def _run_in_pipx_venv(code: str, timeout: int = 60) -> NotebookLMResult:
    """Run Python code in the pipx venv containing notebooklm-mcp-server.

    This is the verified pattern from Oracle-Cortex/scripts/cortex/notebooklm_client.py
    """
    if not PIPX_VENV_PYTHON.exists():
        return NotebookLMResult(
            success=False,
            error=f"pipx venv not found at {PIPX_VENV_PYTHON}. Install with: pipx install notebooklm-mcp-server"
        )

    try:
        result = subprocess.run(
            [str(PIPX_VENV_PYTHON), "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode != 0:
            stderr = result.stderr.lower()
            if "auth" in stderr or "cookie" in stderr or "session" in stderr:
                return NotebookLMResult(
                    success=False,
                    error="Authentication required. Run: notebooklm-mcp-auth"
                )
            return NotebookLMResult(
                success=False,
                error=result.stderr.strip() or "Unknown error"
            )

        # Parse JSON output
        try:
            data = json.loads(result.stdout)
            return NotebookLMResult(success=True, data=data)
        except json.JSONDecodeError:
            return NotebookLMResult(success=True, data={"output": result.stdout.strip()})

    except subprocess.TimeoutExpired:
        return NotebookLMResult(success=False, error="Operation timed out")
    except Exception as e:
        return NotebookLMResult(success=False, error=str(e))


class NotebookLMBackend(VikingDBInterface):
    """
    NotebookLM storage backend implementation.

    Features:
    - Maps collections to NotebookLM notebooks
    - Uses sources for records with L0/L1/L2 tiered naming
    - Leverages query() for semantic search
    - No vector embeddings - pure semantic understanding

    Mapping:
    - Collection → Notebook (via config.notebook_mapping)
    - Record → Source (with L0/L1/L2 prefix naming)
    - Vector Search → query() (semantic)

    VERIFIED: Uses subprocess to pipx venv at:
    ~/.local/share/pipx/venvs/notebooklm-mcp-server/bin/python
    """

    def __init__(self, config: NotebookLMConfig):
        """
        Initialize NotebookLM backend.

        Args:
            config: NotebookLMConfig with notebook mapping and tier settings
        """
        self.config = config
        self._source_cache: Dict[str, Dict[str, Any]] = {}  # collection -> {source_id: metadata}
        self._available = None  # Lazy check

        logger.info(
            f"NotebookLM backend initialized with {len(config.notebook_mapping)} mapped notebooks"
        )

    def _check_available(self) -> bool:
        """Check if NotebookLM client is available."""
        if self._available is None:
            self._available = PIPX_VENV_PYTHON.exists()
            if not self._available:
                logger.warning(
                    f"NotebookLM client not available: pipx venv not found at {PIPX_VENV_PYTHON}. "
                    "Install with: pipx install notebooklm-mcp-server"
                )
        return self._available

    def _require_available(self) -> None:
        """Raise if NotebookLM client not available."""
        if not self._check_available():
            raise RuntimeError(
                f"NotebookLM client not available. "
                f"Expected pipx venv at {PIPX_VENV_PYTHON}. "
                "Install with: pipx install notebooklm-mcp-server"
            )

    # =========================================================================
    # NotebookLM Client Methods (via subprocess to pipx venv)
    # VERIFIED: These match the real NotebookLMClient API
    # =========================================================================

    def _list_notebooks(self) -> NotebookLMResult:
        """List all notebooks. VERIFIED method: list_notebooks()"""
        code = '''
import json
from notebooklm_mcp.server import get_client

client = get_client()
notebooks = client.list_notebooks()
result = [{"id": n.id, "title": n.title} for n in notebooks]
print(json.dumps(result))
'''
        return _run_in_pipx_venv(code)

    def _create_notebook(self, title: str) -> NotebookLMResult:
        """Create a new notebook. VERIFIED method: create_notebook(title)"""
        escaped_title = title.replace("\\", "\\\\").replace('"', '\\"')
        code = f'''
import json
from notebooklm_mcp.server import get_client

client = get_client()
result = client.create_notebook(title="{escaped_title}")
if result:
    print(json.dumps({{"id": result.id, "title": result.title}}))
else:
    print(json.dumps({{"error": "Failed to create notebook"}}))
'''
        return _run_in_pipx_venv(code)

    def _delete_notebook(self, notebook_id: str) -> NotebookLMResult:
        """Delete a notebook. VERIFIED method: delete_notebook(notebook_id)"""
        code = f'''
import json
from notebooklm_mcp.server import get_client

client = get_client()
result = client.delete_notebook(notebook_id="{notebook_id}")
print(json.dumps({{"success": result}}))
'''
        return _run_in_pipx_venv(code)

    def _get_notebook(self, notebook_id: str) -> NotebookLMResult:
        """Get notebook details. VERIFIED method: get_notebook(notebook_id)"""
        code = f'''
import json
from notebooklm_mcp.server import get_client

client = get_client()
result = client.get_notebook("{notebook_id}")
if result:
    print(json.dumps(result))
else:
    print(json.dumps({{"error": "Notebook not found"}}))
'''
        return _run_in_pipx_venv(code)

    def _add_text_source(self, notebook_id: str, text: str, title: str = "Pasted Text") -> NotebookLMResult:
        """Add text as a source. VERIFIED method: add_text_source(notebook_id, text, title)"""
        escaped_text = text.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
        escaped_title = title.replace("\\", "\\\\").replace('"', '\\"')
        code = f'''
import json
from notebooklm_mcp.server import get_client

client = get_client()
result = client.add_text_source(
    notebook_id="{notebook_id}",
    text="""{escaped_text}""",
    title="{escaped_title}"
)
if result:
    print(json.dumps({{"status": "success", "source": result}}))
else:
    print(json.dumps({{"status": "error", "error": "Failed to add source"}}))
'''
        return _run_in_pipx_venv(code, timeout=120)

    def _query(self, notebook_id: str, query_text: str, timeout: int = 120) -> NotebookLMResult:
        """Query a notebook. VERIFIED method: query(notebook_id, query_text, ...)"""
        escaped_query = query_text.replace("\\", "\\\\").replace('"', '\\"').replace('\n', '\\n')
        code = f'''
import json
from notebooklm_mcp.server import get_client

client = get_client()
result = client.query(
    notebook_id="{notebook_id}",
    query_text="{escaped_query}",
    timeout={timeout}
)
if result:
    print(json.dumps({{"status": "success", "answer": result.get("answer", ""), "sources": result.get("sources", [])}}))
else:
    print(json.dumps({{"status": "error", "error": "Query failed"}}))
'''
        return _run_in_pipx_venv(code, timeout=timeout + 10)

    def _delete_source(self, source_id: str) -> NotebookLMResult:
        """Delete a source. VERIFIED method: delete_source(source_id)"""
        code = f'''
import json
from notebooklm_mcp.server import get_client

client = get_client()
result = client.delete_source(source_id="{source_id}")
print(json.dumps({{"success": result}}))
'''
        return _run_in_pipx_venv(code)

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _uri_hash(self, uri: str) -> str:
        """Generate short hash from URI for source naming."""
        return hashlib.sha256(uri.encode()).hexdigest()[:8]

    def _build_source_name(
        self,
        uri: str,
        tier: str = "L1",
        context_type: str = "resource",
        title: Optional[str] = None,
    ) -> str:
        """Build source name from URI using configured pattern."""
        uri_hash = self._uri_hash(uri)
        if title is None:
            title = uri.split("/")[-1] if "/" in uri else uri
        return self.config.format_source_name(
            tier=tier,
            context_type=context_type,
            uri_hash=uri_hash,
            title=title[:50],
        )

    def _parse_source_name(self, source_name: str) -> Dict[str, str]:
        """Parse source name to extract tier, context_type, uri_hash, title."""
        parts = source_name.split("-")
        if len(parts) >= 5:
            return {
                "tier": parts[0],
                "context_type": parts[1],
                "uri_hash": parts[2],
                "title": "-".join(parts[3:-1]),
                "status": parts[-1],
            }
        return {"raw": source_name}

    # =========================================================================
    # Collection Management (maps to Notebooks)
    # =========================================================================

    async def create_collection(self, name: str, schema: Dict[str, Any]) -> bool:
        """
        Create a new collection (notebook).

        Args:
            name: Collection name
            schema: Schema definition (used for title/description)

        Returns:
            True if created, False if already exists
        """
        try:
            self._require_available()

            # Check if already mapped
            if name in self.config.notebook_mapping:
                logger.debug(f"Collection '{name}' already mapped to notebook")
                return False

            # Create new notebook
            title = f"OpenViking-{name}"
            result = self._create_notebook(title=title)

            if not result.success:
                logger.error(f"Failed to create notebook for collection '{name}': {result.error}")
                return False

            notebook_id = result.data.get("id") if result.data else None
            if notebook_id:
                self.config.notebook_mapping[name] = notebook_id
                logger.info(f"Created notebook for collection '{name}': {notebook_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error creating collection '{name}': {e}")
            return False

    async def drop_collection(self, name: str) -> bool:
        """
        Drop a collection (delete notebook).

        Args:
            name: Collection name

        Returns:
            True if dropped successfully
        """
        try:
            self._require_available()
            notebook_id = self.config.get_notebook_id(name)

            result = self._delete_notebook(notebook_id=notebook_id)

            if not result.success:
                logger.error(f"Failed to delete notebook for collection '{name}': {result.error}")
                return False

            if result.data and result.data.get("success"):
                self.config.notebook_mapping.pop(name, None)
                self._source_cache.pop(name, None)
                logger.info(f"Dropped collection: {name}")
                return True

            return False

        except ValueError as e:
            logger.warning(f"Collection '{name}' not found: {e}")
            return False
        except Exception as e:
            logger.error(f"Error dropping collection '{name}': {e}")
            return False

    async def collection_exists(self, name: str) -> bool:
        """Check if a collection (notebook) exists."""
        try:
            notebook_id = self.config.get_notebook_id(name)
            result = self._get_notebook(notebook_id=notebook_id)
            return result.success and result.data and "error" not in result.data
        except ValueError:
            return False
        except Exception:
            return False

    async def list_collections(self) -> List[str]:
        """List all collection names (mapped notebooks)."""
        return list(self.config.notebook_mapping.keys())

    async def get_collection_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get collection (notebook) metadata and statistics."""
        try:
            notebook_id = self.config.get_notebook_id(name)
            result = self._get_notebook(notebook_id=notebook_id)

            if not result.success or not result.data or "error" in result.data:
                return None

            return {
                "name": name,
                "notebook_id": notebook_id,
                "title": result.data.get("title", name),
                "source_count": len(result.data.get("sources", [])),
                "status": "active",
            }

        except ValueError:
            return None
        except Exception as e:
            logger.error(f"Error getting collection info for '{name}': {e}")
            return None

    # =========================================================================
    # CRUD Operations - Single Record (maps to Sources)
    # =========================================================================

    async def insert(self, collection: str, data: Dict[str, Any]) -> str:
        """
        Insert a single record (source).

        Args:
            collection: Collection name
            data: Record data with uri, content, and optional metadata

        Returns:
            ID of the inserted record
        """
        try:
            self._require_available()
            notebook_id = self.config.get_notebook_id(collection)

            # Extract fields
            record_id = data.get("id") or str(uuid.uuid4())
            uri = data.get("uri", f"viking://{collection}/{record_id}")
            content = data.get("content") or data.get("text") or data.get("abstract", "")
            context_type = data.get("context_type", "resource")

            # Determine tier from content length
            content_len = len(content.split()) if content else 0
            if content_len <= self.config.tier_config["L0"]:
                tier = "L0"
            elif content_len <= self.config.tier_config["L1"]:
                tier = "L1"
            else:
                tier = "L2"

            # Build source name
            source_name = self._build_source_name(
                uri=uri,
                tier=tier,
                context_type=context_type,
                title=data.get("title"),
            )

            # Add source to notebook using VERIFIED method
            result = self._add_text_source(
                notebook_id=notebook_id,
                text=content,
                title=source_name,
            )

            if not result.success or (result.data and result.data.get("status") == "error"):
                error_msg = result.error or result.data.get("error", "Unknown error")
                logger.error(f"Failed to insert record: {error_msg}")
                raise RuntimeError(f"Insert failed: {error_msg}")

            # Extract source_id from result if available
            source_id = None
            if result.data and result.data.get("source"):
                source_info = result.data["source"]
                if isinstance(source_info, dict):
                    source_id = source_info.get("id") or source_info.get("source_id")

            # Cache source metadata
            if collection not in self._source_cache:
                self._source_cache[collection] = {}
            self._source_cache[collection][record_id] = {
                "id": record_id,
                "source_id": source_id,  # NotebookLM's internal ID for deletion
                "uri": uri,
                "source_name": source_name,
                "tier": tier,
                "context_type": context_type,
                **data,
            }

            logger.debug(f"Inserted record {record_id} as source '{source_name}'")
            return record_id

        except ValueError as e:
            raise CollectionNotFoundError(str(e))
        except Exception as e:
            logger.error(f"Error inserting record: {e}")
            raise

    async def update(self, collection: str, id: str, data: Dict[str, Any]) -> bool:
        """
        Update a record by ID.

        NotebookLM doesn't support direct source updates, so we delete and re-add.

        Args:
            collection: Collection name
            id: Record ID
            data: Fields to update

        Returns:
            True if updated successfully
        """
        try:
            existing = await self.get(collection, [id])
            if not existing:
                return False

            updated_data = {**existing[0], **data, "id": id}
            await self.delete(collection, [id])
            await self.insert(collection, updated_data)
            return True

        except Exception as e:
            logger.error(f"Error updating record '{id}': {e}")
            return False

    async def upsert(self, collection: str, data: Dict[str, Any]) -> str:
        """Insert or update a record."""
        record_id = data.get("id")
        if record_id:
            exists = await self.exists(collection, record_id)
            if exists:
                await self.update(collection, record_id, data)
                return record_id

        return await self.insert(collection, data)

    async def delete(self, collection: str, ids: List[str]) -> int:
        """
        Delete records by IDs.

        Args:
            collection: Collection name
            ids: List of record IDs to delete

        Returns:
            Number of records deleted
        """
        deleted = 0
        try:
            self._require_available()

            for record_id in ids:
                cached = self._source_cache.get(collection, {}).get(record_id)
                if cached:
                    source_id = cached.get("source_id")
                    if source_id:
                        # Use VERIFIED method: delete_source(source_id)
                        result = self._delete_source(source_id=source_id)
                        if result.success and result.data and result.data.get("success"):
                            self._source_cache.get(collection, {}).pop(record_id, None)
                            deleted += 1
                        else:
                            logger.warning(f"Failed to delete source {source_id}: {result.error}")
                    else:
                        # No source_id cached - just remove from cache
                        logger.warning(f"No source_id for record '{record_id}', removing from cache only")
                        self._source_cache.get(collection, {}).pop(record_id, None)
                        deleted += 1
                else:
                    logger.warning(f"Record '{record_id}' not found in cache")

        except Exception as e:
            logger.error(f"Error deleting records: {e}")

        return deleted

    async def get(self, collection: str, ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get records by IDs.

        Args:
            collection: Collection name
            ids: List of record IDs

        Returns:
            List of records
        """
        records = []
        for record_id in ids:
            cached = self._source_cache.get(collection, {}).get(record_id)
            if cached:
                records.append(cached)
        return records

    async def exists(self, collection: str, id: str) -> bool:
        """Check if a record exists."""
        return id in self._source_cache.get(collection, {})

    # =========================================================================
    # CRUD Operations - Batch
    # =========================================================================

    async def batch_insert(self, collection: str, data: List[Dict[str, Any]]) -> List[str]:
        """Batch insert multiple records."""
        ids = []
        for record in data:
            record_id = await self.insert(collection, record)
            ids.append(record_id)
        return ids

    async def batch_upsert(self, collection: str, data: List[Dict[str, Any]]) -> List[str]:
        """Batch insert or update multiple records."""
        ids = []
        for record in data:
            record_id = await self.upsert(collection, record)
            ids.append(record_id)
        return ids

    async def batch_delete(self, collection: str, filter: Dict[str, Any]) -> int:
        """Delete records matching filter conditions."""
        matching = await self.filter(collection, filter, limit=10000)
        if not matching:
            return 0

        ids = [r.get("id") for r in matching if r.get("id")]
        return await self.delete(collection, ids)

    async def remove_by_uri(self, collection: str, uri: str) -> int:
        """Remove resource(s) by URI."""
        deleted = 0
        cache = self._source_cache.get(collection, {})

        to_delete = []
        for record_id, record in cache.items():
            record_uri = record.get("uri", "")
            if record_uri == uri or record_uri.startswith(f"{uri}/"):
                to_delete.append(record_id)

        if to_delete:
            deleted = await self.delete(collection, to_delete)

        return deleted

    # =========================================================================
    # Search Operations (uses query() for semantic search)
    # =========================================================================

    async def search(
        self,
        collection: str,
        query_vector: Optional[List[float]] = None,
        sparse_query_vector: Optional[Dict[str, float]] = None,
        filter: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
        output_fields: Optional[List[str]] = None,
        with_vector: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search using NotebookLM's query() method.

        NotebookLM doesn't use vector embeddings - it performs semantic search
        natively. The query_vector parameter is ignored; instead, we extract
        the query text from the filter.

        Args:
            collection: Collection name
            query_vector: Ignored - NotebookLM uses semantic search
            sparse_query_vector: Ignored
            filter: Filter conditions - may contain "query" field for search text
            limit: Maximum number of results
            offset: Offset for pagination
            output_fields: Fields to return
            with_vector: Ignored - no vectors

        Returns:
            List of matching records with _score field
        """
        try:
            self._require_available()
            notebook_id = self.config.get_notebook_id(collection)

            # Extract query text from filter
            query_text = ""
            if filter:
                if isinstance(filter, dict):
                    query_text = filter.get("query", "")
                    if not query_text and "conds" in filter:
                        for cond in filter.get("conds", []):
                            if cond.get("field") == "query":
                                query_text = cond.get("conds", [""])[0]
                                break

            if not query_text:
                logger.warning("No query text provided for semantic search")
                return []

            # Perform semantic search using VERIFIED method: query()
            result = self._query(
                notebook_id=notebook_id,
                query_text=query_text,
            )

            if not result.success or (result.data and result.data.get("status") == "error"):
                error_msg = result.error or result.data.get("error", "Unknown error")
                logger.error(f"Notebook query failed: {error_msg}")
                return []

            # Parse results
            records = []
            sources = result.data.get("sources", []) if result.data else []

            for i, source in enumerate(sources[:limit]):
                source_title = source.get("title", "")
                parsed = self._parse_source_name(source_title)

                record = {
                    "id": source.get("source_id", str(uuid.uuid4())),
                    "uri": f"viking://{collection}/{parsed.get('uri_hash', 'unknown')}",
                    "content": source.get("snippet", ""),
                    "title": parsed.get("title", source_title),
                    "context_type": parsed.get("context_type", "resource"),
                    "_score": 1.0 - (i * 0.1),  # Approximate score based on order
                }

                if output_fields:
                    record = {k: v for k, v in record.items() if k in output_fields or k in ["id", "_score"]}

                records.append(record)

            return records[offset:offset + limit] if offset else records[:limit]

        except ValueError as e:
            raise CollectionNotFoundError(str(e))
        except Exception as e:
            logger.error(f"Error searching collection '{collection}': {e}")
            return []

    async def filter(
        self,
        collection: str,
        filter: Dict[str, Any],
        limit: int = 10,
        offset: int = 0,
        output_fields: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Filter records without vector search.

        Uses cached records for filtering since NotebookLM doesn't support
        pure scalar filtering.

        Args:
            collection: Collection name
            filter: Filter conditions
            limit: Maximum number of results
            offset: Offset for pagination
            output_fields: Fields to return
            order_by: Field to sort by
            order_desc: Sort descending

        Returns:
            List of matching records
        """
        cache = self._source_cache.get(collection, {})
        records = list(cache.values())

        # Apply filter
        if filter:
            filtered = []
            for record in records:
                if self._matches_filter(record, filter):
                    filtered.append(record)
            records = filtered

        # Sort
        if order_by and records:
            records = sorted(
                records,
                key=lambda r: r.get(order_by, ""),
                reverse=order_desc,
            )

        # Pagination
        records = records[offset:offset + limit]

        # Field selection
        if output_fields:
            records = [
                {k: v for k, v in r.items() if k in output_fields or k == "id"}
                for r in records
            ]

        return records

    def _matches_filter(self, record: Dict[str, Any], filter: Dict[str, Any]) -> bool:
        """Check if record matches filter conditions."""
        if not filter:
            return True

        op = filter.get("op", "and")
        conds = filter.get("conds", [])

        if not conds:
            field = filter.get("field")
            if field and field in record:
                expected = filter.get("conds", [])
                if expected:
                    return record.get(field) in expected
            return True

        results = []
        for cond in conds:
            if isinstance(cond, dict):
                results.append(self._matches_filter(record, cond))

        if op == "and":
            return all(results) if results else True
        elif op == "or":
            return any(results) if results else True

        return True

    async def scroll(
        self,
        collection: str,
        filter: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        cursor: Optional[str] = None,
        output_fields: Optional[List[str]] = None,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Scroll through large result sets."""
        offset = int(cursor) if cursor else 0

        records = await self.filter(
            collection=collection,
            filter=filter or {},
            limit=limit,
            offset=offset,
            output_fields=output_fields,
        )

        next_cursor = str(offset + limit) if len(records) == limit else None
        return records, next_cursor

    # =========================================================================
    # Aggregation Operations
    # =========================================================================

    async def count(self, collection: str, filter: Optional[Dict[str, Any]] = None) -> int:
        """Count records matching filter."""
        if filter:
            records = await self.filter(collection, filter, limit=100000)
            return len(records)
        return len(self._source_cache.get(collection, {}))

    # =========================================================================
    # Index Operations (no-op for NotebookLM)
    # =========================================================================

    async def create_index(
        self,
        collection: str,
        field: str,
        index_type: str,
        **kwargs,
    ) -> bool:
        """Create an index (no-op for NotebookLM)."""
        logger.debug("Index creation not applicable for NotebookLM backend")
        return True

    async def drop_index(self, collection: str, field: str) -> bool:
        """Drop an index (no-op for NotebookLM)."""
        logger.debug("Index drop not applicable for NotebookLM backend")
        return True

    # =========================================================================
    # Lifecycle Operations
    # =========================================================================

    async def clear(self, collection: str) -> bool:
        """Clear all data in a collection."""
        try:
            cache = self._source_cache.get(collection, {})
            ids = list(cache.keys())

            if ids:
                await self.delete(collection, ids)

            self._source_cache[collection] = {}
            logger.info(f"Cleared all data in collection: {collection}")
            return True

        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False

    async def optimize(self, collection: str) -> bool:
        """Optimize collection (no-op for NotebookLM)."""
        logger.debug("Optimization not applicable for NotebookLM backend")
        return True

    async def close(self) -> None:
        """Close storage connection."""
        self._source_cache.clear()
        logger.info("NotebookLM backend closed")

    # =========================================================================
    # Health & Status
    # =========================================================================

    async def health_check(self) -> bool:
        """Check if storage backend is healthy."""
        try:
            if not self._check_available():
                return False
            result = self._list_notebooks()
            return result.success
        except Exception:
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            total_records = sum(len(cache) for cache in self._source_cache.values())

            return {
                "collections": len(self.config.notebook_mapping),
                "total_records": total_records,
                "backend": "notebooklm",
                "tier_config": self.config.tier_config,
                "pipx_available": self._check_available(),
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "collections": 0,
                "total_records": 0,
                "backend": "notebooklm",
                "error": str(e),
            }

    @property
    def mode(self) -> str:
        """Return the storage mode."""
        return "notebooklm"
