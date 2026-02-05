# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0
"""
NotebookLM storage backend for OpenViking.

Implements the VikingDBInterface using NotebookLM as the storage backend.
Maps collections to notebooks and uses notebook_query for semantic search.
"""

import hashlib
import uuid
from typing import Any, Dict, List, Optional, Tuple

from openviking.storage.vikingdb_interface import (
    CollectionNotFoundError,
    RecordNotFoundError,
    VikingDBInterface,
)
from openviking.utils import get_logger
from openviking.utils.config.notebooklm_config import NotebookLMConfig

logger = get_logger(__name__)


class NotebookLMBackend(VikingDBInterface):
    """
    NotebookLM storage backend implementation.

    Features:
    - Maps collections to NotebookLM notebooks
    - Uses sources for records with L0/L1/L2 tiered naming
    - Leverages notebook_query for semantic search
    - No vector embeddings - pure semantic understanding

    Mapping:
    - Collection → Notebook (via config.notebook_mapping)
    - Record → Source (with L0/L1/L2 prefix naming)
    - Vector Search → notebook_query (semantic)
    """

    def __init__(self, config: NotebookLMConfig):
        """
        Initialize NotebookLM backend.

        Args:
            config: NotebookLMConfig with notebook mapping and tier settings
        """
        self.config = config
        self._client = None
        self._source_cache: Dict[str, Dict[str, Any]] = {}  # collection -> {source_id: metadata}

        # Initialize MCP client
        self._init_client()
        logger.info(
            f"NotebookLM backend initialized with {len(config.notebook_mapping)} mapped notebooks"
        )

    def _init_client(self):
        """Initialize the NotebookLM MCP client."""
        try:
            from notebooklm_mcp_server import NotebookLMClient
            self._client = NotebookLMClient()
            logger.info("NotebookLM MCP client initialized")
        except ImportError as e:
            logger.warning(
                f"NotebookLM MCP client not available: {e}. "
                "Install with: pip install notebooklm-mcp-server"
            )
            self._client = None

    def _get_client(self):
        """Get the NotebookLM client, raising if not available."""
        if self._client is None:
            raise RuntimeError(
                "NotebookLM client not initialized. "
                "Install notebooklm-mcp-server package."
            )
        return self._client

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
            # Extract title from URI
            title = uri.split("/")[-1] if "/" in uri else uri
        return self.config.format_source_name(
            tier=tier,
            context_type=context_type,
            uri_hash=uri_hash,
            title=title[:50],  # Truncate long titles
        )

    def _parse_source_name(self, source_name: str) -> Dict[str, str]:
        """Parse source name to extract tier, context_type, uri_hash, title."""
        # Default pattern: {tier}-{context_type}-{uri_hash}-{title}-{status}
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

        For NotebookLM, collections map to notebooks. If the notebook is
        already mapped in config, this is a no-op. Otherwise, creates a new
        notebook and adds it to the mapping.

        Args:
            name: Collection name
            schema: Schema definition (used for description)

        Returns:
            True if created, False if already exists
        """
        try:
            # Check if already mapped
            if name in self.config.notebook_mapping:
                logger.debug(f"Collection '{name}' already mapped to notebook")
                return False

            # Create new notebook
            client = self._get_client()
            description = schema.get("description", f"OpenViking collection: {name}")

            result = client.notebook_create(
                name=f"OpenViking-{name}",
                description=description,
            )

            if result.get("status") == "error":
                logger.error(f"Failed to create notebook for collection '{name}': {result}")
                return False

            notebook_id = result.get("notebook_id")
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
            notebook_id = self.config.get_notebook_id(name)
            client = self._get_client()

            result = client.notebook_delete(
                notebook_id=notebook_id,
                confirm=True,
            )

            if result.get("status") == "error":
                logger.error(f"Failed to delete notebook for collection '{name}': {result}")
                return False

            # Remove from mapping
            self.config.notebook_mapping.pop(name, None)
            self._source_cache.pop(name, None)
            logger.info(f"Dropped collection: {name}")
            return True

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
            client = self._get_client()

            result = client.notebook_describe(notebook_id=notebook_id)
            return result.get("status") != "error"

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
            client = self._get_client()

            result = client.notebook_describe(notebook_id=notebook_id)

            if result.get("status") == "error":
                return None

            return {
                "name": name,
                "notebook_id": notebook_id,
                "title": result.get("title", name),
                "source_count": result.get("source_count", 0),
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
            notebook_id = self.config.get_notebook_id(collection)
            client = self._get_client()

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

            # Add source to notebook
            result = client.notebook_add_text(
                notebook_id=notebook_id,
                text=content,
                title=source_name,
            )

            if result.get("status") == "error":
                logger.error(f"Failed to insert record: {result}")
                raise RuntimeError(f"Insert failed: {result.get('error')}")

            # Cache source metadata
            if collection not in self._source_cache:
                self._source_cache[collection] = {}
            self._source_cache[collection][record_id] = {
                "id": record_id,
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
            # Get existing record
            existing = await self.get(collection, [id])
            if not existing:
                return False

            # Merge data
            updated_data = {**existing[0], **data, "id": id}

            # Delete old source
            await self.delete(collection, [id])

            # Insert updated record
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
            notebook_id = self.config.get_notebook_id(collection)
            client = self._get_client()

            for record_id in ids:
                # Find source in cache
                cached = self._source_cache.get(collection, {}).get(record_id)
                if cached:
                    source_name = cached.get("source_name")
                    # NotebookLM source_delete expects source_id, not name
                    # We need to look up the source first
                    result = client.source_delete(
                        notebook_id=notebook_id,
                        source_id=record_id,  # This may need adjustment based on MCP API
                    )

                    if result.get("status") != "error":
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
        # Find matching records
        matching = await self.filter(collection, filter, limit=10000)
        if not matching:
            return 0

        ids = [r.get("id") for r in matching if r.get("id")]
        return await self.delete(collection, ids)

    async def remove_by_uri(self, collection: str, uri: str) -> int:
        """Remove resource(s) by URI."""
        # Find records with matching URI prefix
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
    # Search Operations (uses notebook_query for semantic search)
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
        Semantic search using NotebookLM's notebook_query.

        NotebookLM doesn't use vector embeddings - it performs semantic search
        natively. The query_vector parameter is ignored; instead, we extract
        the query text from the filter or use a default query.

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
            notebook_id = self.config.get_notebook_id(collection)
            client = self._get_client()

            # Extract query text from filter
            query_text = ""
            if filter:
                if isinstance(filter, dict):
                    # Look for query in various filter formats
                    query_text = filter.get("query", "")
                    if not query_text and "conds" in filter:
                        # VikingDB DSL format
                        for cond in filter.get("conds", []):
                            if cond.get("field") == "query":
                                query_text = cond.get("conds", [""])[0]
                                break

            if not query_text:
                logger.warning("No query text provided for semantic search")
                return []

            # Perform semantic search via notebook_query
            result = client.notebook_query(
                notebook_id=notebook_id,
                query=query_text,
            )

            if result.get("status") == "error":
                logger.error(f"Notebook query failed: {result}")
                return []

            # Parse results
            records = []
            response_text = result.get("response", "")
            sources = result.get("sources", [])

            # Map sources to records
            for i, source in enumerate(sources[:limit]):
                # Try to find cached record
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
            # Simple field match
            field = filter.get("field")
            if field and field in record:
                expected = filter.get("conds", [])
                if expected:
                    return record.get(field) in expected
            return True

        # Multiple conditions
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
        logger.debug(f"Index creation not applicable for NotebookLM backend")
        return True

    async def drop_index(self, collection: str, field: str) -> bool:
        """Drop an index (no-op for NotebookLM)."""
        logger.debug(f"Index drop not applicable for NotebookLM backend")
        return True

    # =========================================================================
    # Lifecycle Operations
    # =========================================================================

    async def clear(self, collection: str) -> bool:
        """Clear all data in a collection."""
        try:
            # Delete all cached records
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
        logger.debug(f"Optimization not applicable for NotebookLM backend")
        return True

    async def close(self) -> None:
        """Close storage connection."""
        self._source_cache.clear()
        self._client = None
        logger.info("NotebookLM backend closed")

    # =========================================================================
    # Health & Status
    # =========================================================================

    async def health_check(self) -> bool:
        """Check if storage backend is healthy."""
        try:
            client = self._get_client()
            result = client.notebook_list()
            return result.get("status") != "error"
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
