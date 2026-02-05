# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0
"""Tests for NotebookLMConfig."""

import pytest
from pydantic import ValidationError

from openviking.utils.config import NotebookLMConfig


class TestNotebookLMConfigCreation:
    """Test NotebookLMConfig instantiation."""

    def test_create_with_notebook_mapping(self):
        """Test creating config with notebook mapping."""
        config = NotebookLMConfig(
            notebook_mapping={
                "resources": "notebook-id-1",
                "memories": "notebook-id-2",
            }
        )
        assert config.notebook_mapping["resources"] == "notebook-id-1"
        assert config.notebook_mapping["memories"] == "notebook-id-2"

    def test_create_with_default_notebook(self):
        """Test creating config with default notebook only."""
        config = NotebookLMConfig(
            default_notebook_id="default-notebook-id"
        )
        assert config.default_notebook_id == "default-notebook-id"
        assert config.notebook_mapping == {}

    def test_create_with_both_mapping_and_default(self):
        """Test creating config with both mapping and default."""
        config = NotebookLMConfig(
            notebook_mapping={"resources": "notebook-id-1"},
            default_notebook_id="default-notebook-id",
        )
        assert config.notebook_mapping["resources"] == "notebook-id-1"
        assert config.default_notebook_id == "default-notebook-id"

    def test_default_tier_config(self):
        """Test default tier configuration."""
        config = NotebookLMConfig(default_notebook_id="test-id")
        assert config.tier_config["L0"] == 100
        assert config.tier_config["L1"] == 2000
        assert config.tier_config["L2"] == 0

    def test_default_source_naming_pattern(self):
        """Test default source naming pattern."""
        config = NotebookLMConfig(default_notebook_id="test-id")
        assert "{tier}" in config.source_naming_pattern
        assert "ACTIVE" in config.source_naming_pattern


class TestNotebookLMConfigValidation:
    """Test NotebookLMConfig validation."""

    def test_fails_without_notebook_config(self):
        """Test validation fails when neither mapping nor default provided."""
        with pytest.raises(ValidationError) as exc_info:
            NotebookLMConfig()
        assert "notebook_mapping" in str(exc_info.value) or "default_notebook_id" in str(exc_info.value)

    def test_fails_with_missing_tier(self):
        """Test validation fails when tier_config is missing required tiers."""
        with pytest.raises(ValidationError) as exc_info:
            NotebookLMConfig(
                default_notebook_id="test-id",
                tier_config={"L0": 100, "L1": 2000},  # Missing L2
            )
        assert "L2" in str(exc_info.value)

    def test_fails_without_tier_placeholder(self):
        """Test validation fails when source_naming_pattern missing {tier}."""
        with pytest.raises(ValidationError) as exc_info:
            NotebookLMConfig(
                default_notebook_id="test-id",
                source_naming_pattern="no-tier-placeholder",
            )
        assert "{tier}" in str(exc_info.value)


class TestNotebookLMConfigMethods:
    """Test NotebookLMConfig helper methods."""

    def test_get_notebook_id_from_mapping(self):
        """Test getting notebook ID from mapping."""
        config = NotebookLMConfig(
            notebook_mapping={"resources": "notebook-id-1"},
            default_notebook_id="default-id",
        )
        assert config.get_notebook_id("resources") == "notebook-id-1"

    def test_get_notebook_id_falls_back_to_default(self):
        """Test getting notebook ID falls back to default."""
        config = NotebookLMConfig(
            notebook_mapping={"resources": "notebook-id-1"},
            default_notebook_id="default-id",
        )
        assert config.get_notebook_id("unknown") == "default-id"

    def test_get_notebook_id_raises_without_default(self):
        """Test getting unmapped notebook ID raises without default."""
        config = NotebookLMConfig(
            notebook_mapping={"resources": "notebook-id-1"},
        )
        with pytest.raises(ValueError) as exc_info:
            config.get_notebook_id("unknown")
        assert "unknown" in str(exc_info.value)

    def test_format_source_name(self):
        """Test source name formatting."""
        config = NotebookLMConfig(default_notebook_id="test-id")
        name = config.format_source_name(
            tier="L1",
            context_type="resource",
            uri_hash="abc123",
            title="my-doc",
        )
        assert "L1" in name
        assert "resource" in name
        assert "abc123" in name
        assert "my-doc" in name
        assert "ACTIVE" in name

    def test_format_source_name_custom_status(self):
        """Test source name formatting with custom status."""
        config = NotebookLMConfig(default_notebook_id="test-id")
        name = config.format_source_name(
            tier="L0",
            context_type="memory",
            uri_hash="def456",
            title="session",
            status="ARCHIVED",
        )
        assert "ARCHIVED" in name


class TestNotebookLMConfigExport:
    """Test NotebookLMConfig is properly exported."""

    def test_import_from_config_module(self):
        """Test NotebookLMConfig can be imported from config module."""
        from openviking.utils.config import NotebookLMConfig as ImportedConfig
        assert ImportedConfig is NotebookLMConfig
