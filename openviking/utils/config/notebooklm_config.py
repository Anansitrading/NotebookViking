# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0
"""
Configuration for NotebookLM storage backend.

NotebookLM serves as a semantic storage backend for OpenViking,
using notebooks as collections and sources as records.
"""

from typing import Dict, Optional

from pydantic import BaseModel, Field, model_validator


class NotebookLMConfig(BaseModel):
    """
    Configuration for NotebookLM storage backend.

    NotebookLM maps OpenViking concepts as follows:
    - Collection → Notebook
    - Record → Source
    - Vector Search → notebook_query (semantic search)
    - URI → Source title with L0/L1/L2 prefix

    Example:
        config = NotebookLMConfig(
            notebook_mapping={
                "resources": "abc123-notebook-id",
                "memories": "def456-notebook-id",
                "skills": "ghi789-notebook-id",
            },
            default_notebook_id="fallback-notebook-id",
        )
    """

    notebook_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Maps collection names to NotebookLM notebook IDs. "
            "Keys are collection names (e.g., 'resources', 'memories', 'skills'), "
            "values are notebook UUIDs."
        ),
    )

    default_notebook_id: Optional[str] = Field(
        default=None,
        description=(
            "Fallback notebook ID for collections not in notebook_mapping. "
            "If None and collection not mapped, operations will fail."
        ),
    )

    auth_token_path: Optional[str] = Field(
        default=None,
        description=(
            "Path to NotebookLM auth tokens file. "
            "Defaults to ~/.notebooklm/tokens.json if not specified."
        ),
    )

    tier_config: Dict[str, int] = Field(
        default_factory=lambda: {
            "L0": 100,   # ~100 tokens summary
            "L1": 2000,  # ~2000 tokens core procedure
            "L2": 0,     # Full content (0 = unlimited)
        },
        description=(
            "Token limits for L0/L1/L2 tiers. "
            "L0 is one-sentence summary, L1 is core procedure, L2 is full content."
        ),
    )

    source_naming_pattern: str = Field(
        default="{tier}-{context_type}-{uri_hash}-{title}-ACTIVE",
        description=(
            "Pattern for naming NotebookLM sources. "
            "Available placeholders: {tier}, {context_type}, {uri_hash}, {title}, {status}"
        ),
    )

    @model_validator(mode="after")
    def validate_config(self):
        """Validate configuration completeness."""
        # Must have at least one notebook configured
        if not self.notebook_mapping and not self.default_notebook_id:
            raise ValueError(
                "NotebookLM backend requires either 'notebook_mapping' "
                "or 'default_notebook_id' to be set"
            )

        # Validate tier_config has required keys
        required_tiers = {"L0", "L1", "L2"}
        if not required_tiers.issubset(self.tier_config.keys()):
            missing = required_tiers - set(self.tier_config.keys())
            raise ValueError(f"tier_config missing required tiers: {missing}")

        # Validate source_naming_pattern has at least {tier}
        if "{tier}" not in self.source_naming_pattern:
            raise ValueError(
                "source_naming_pattern must include {tier} placeholder"
            )

        return self

    def get_notebook_id(self, collection: str) -> str:
        """
        Get notebook ID for a collection.

        Args:
            collection: Collection name (e.g., 'resources', 'memories')

        Returns:
            Notebook ID string

        Raises:
            ValueError: If collection not mapped and no default configured
        """
        if collection in self.notebook_mapping:
            return self.notebook_mapping[collection]

        if self.default_notebook_id:
            return self.default_notebook_id

        raise ValueError(
            f"Collection '{collection}' not mapped and no default_notebook_id configured"
        )

    def format_source_name(
        self,
        tier: str,
        context_type: str,
        uri_hash: str,
        title: str,
        status: str = "ACTIVE",
    ) -> str:
        """
        Format a source name using the configured pattern.

        Args:
            tier: L0, L1, or L2
            context_type: resource, memory, or skill
            uri_hash: Short hash of the URI
            title: Human-readable title
            status: ACTIVE or ARCHIVED

        Returns:
            Formatted source name string
        """
        return self.source_naming_pattern.format(
            tier=tier,
            context_type=context_type,
            uri_hash=uri_hash,
            title=title,
            status=status,
        )
