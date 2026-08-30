from unittest.mock import MagicMock, Mock, patch

from logassistant.agent_tools.knowledge_base import (
    _get_vector_store,
    get_mitre_knowledge_base,
)


def test_vector_store_creation_success(monkeypatch):
    monkeypatch.setenv("QDRANT_URL", "Test")
    with (
        patch("logassistant.agent_tools.knowledge_base.QdrantClient", new=Mock()),
        patch(
            "logassistant.agent_tools.knowledge_base.HuggingFaceEmbeddings", new=Mock()
        ),
        patch("logassistant.agent_tools.knowledge_base.QdrantVectorStore", new=Mock()),
    ):
        store = _get_vector_store()
        assert store is not None


def test_vector_store_return_information():
    fake_store = MagicMock()
    fake_content = MagicMock()
    fake_content.page_content = "Successful tested query"
    fake_store.similarity_search.return_value = [fake_content]
    with patch(
        "logassistant.agent_tools.knowledge_base._get_vector_store",
        return_value=fake_store,
    ):
        result = get_mitre_knowledge_base.invoke({"query": "brute force"})
        assert result == "Successful tested query"
