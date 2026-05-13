# -*- coding: utf-8 -*-
"""Tests for undo/redo operation stack behavior."""

import pytest

from operation.basic_op import Operation, OperationStack


class DummyGLWidget:
    def __init__(self):
        self.repaint_count = 0

    def paintGL_outside(self):
        self.repaint_count += 1


class DummyMainEditor:
    def __init__(self):
        self.gl_widget = DummyGLWidget()
        self.status_messages = []

    def show_statu_(self, message, level):
        self.status_messages.append((message, level))


class RecordingOperation(Operation):
    def __init__(self, name, log):
        super().__init__()
        self.name = name
        self.log = log

    def execute(self):
        self.log.append(f"execute:{self.name}")

    def undo(self):
        self.log.append(f"undo:{self.name}")

    def redo(self):
        self.log.append(f"redo:{self.name}")


def make_stack(max_length=5):
    editor = DummyMainEditor()
    stack = OperationStack(editor, max_length=max_length)
    stack.init_stack()
    return stack, editor


def test_execute_adds_operation_and_repaints():
    log = []
    stack, editor = make_stack()

    stack.execute(RecordingOperation("A", log))

    assert log == ["execute:A"]
    assert stack.current_index == 1
    assert editor.gl_widget.repaint_count == 1


def test_undo_runs_current_operation_undo():
    log = []
    stack, _ = make_stack()
    stack.execute(RecordingOperation("A", log))

    stack.undo()

    assert log == ["execute:A", "undo:A"]
    assert stack.current_index == 0


def test_redo_runs_next_operation_redo():
    log = []
    stack, _ = make_stack()
    stack.execute(RecordingOperation("A", log))
    stack.undo()

    stack.redo()

    assert log == ["execute:A", "undo:A", "redo:A"]
    assert stack.current_index == 1


def test_execute_after_undo_clears_redo_history():
    """Executing a new operation after undo should drop the old redo branch."""
    log = []
    stack, _ = make_stack()
    stack.execute(RecordingOperation("A", log))
    stack.execute(RecordingOperation("B", log))
    stack.undo()

    stack.execute(RecordingOperation("C", log))
    stack.redo()

    assert "redo:B" not in log
    assert log == ["execute:A", "execute:B", "undo:B", "execute:C"]


def test_redo_at_stack_tail_does_not_raise():
    """Redo should be safe even when the current index is already at the stack tail."""
    log = []
    stack, _ = make_stack(max_length=2)
    stack.execute(RecordingOperation("A", log))

    stack.redo()

    assert log == ["execute:A"]
