"""
Web session flow regression tests.
"""

from types import SimpleNamespace

import main_web


class FakeSessionState(dict):
    """Dictionary-backed object that mimics Streamlit session state."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


def test_clear_conversation_state_resets_messages_and_agent_history():
    agent = SimpleNamespace(clear_history_called=False)

    def clear_history():
        agent.clear_history_called = True

    agent.clear_history = clear_history
    session_state = FakeSessionState(
        messages=[{"role": "user", "content": "old"}],
        pending_prompt="queued",
        example_input="example",
        uploaded_file_info={"filename": "demo.txt"},
        agent=agent,
    )

    main_web.clear_conversation_state(session_state)

    assert session_state.messages == []
    assert "pending_prompt" not in session_state
    assert "example_input" not in session_state
    assert "uploaded_file_info" not in session_state
    assert agent.clear_history_called is True


def test_consume_pending_prompt_prefers_session_queue_and_pops_it():
    session_state = FakeSessionState(pending_prompt="queued prompt")

    prompt = main_web.consume_pending_prompt(session_state, None)

    assert prompt == "queued prompt"
    assert "pending_prompt" not in session_state


def test_consume_pending_prompt_falls_back_to_chat_input():
    session_state = FakeSessionState()

    prompt = main_web.consume_pending_prompt(session_state, "chat prompt")

    assert prompt == "chat prompt"
