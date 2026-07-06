from taskqueue.core.errors import QueueFull
from taskqueue.core.job import Job
from taskqueue.core.queue import PriorityQueue

import pytest


def _jobs():
    return (
        Job(name="batch.low", priority="low"),
        Job(name="batch.high", priority="high"),
        Job(name="batch.normal", priority="normal"),
    )


def test_ready_batch_orders_by_priority():
    q = PriorityQueue()
    low, high, normal = _jobs()
    for job in (low, high, normal):
        q.enqueue(job)
    batch = q.ready_batch()
    assert [j.priority for j in batch] == ["high", "normal", "low"]


def test_fifo_within_priority():
    q = PriorityQueue()
    first = Job(name="batch.a")
    second = Job(name="batch.b")
    second.created_at = first.created_at + 1
    q.enqueue(first)
    q.enqueue(second)
    assert [j.name for j in q.ready_batch()] == ["batch.a", "batch.b"]


def test_find_and_remove():
    q = PriorityQueue()
    job = Job(name="batch.echo")
    q.enqueue(job)
    assert q.find(job.id) is job
    assert q.remove(job) is True
    assert q.remove(job) is False
    assert q.find(job.id) is None
    assert len(q) == 0


def test_capacity():
    q = PriorityQueue(max_size=1)
    q.enqueue(Job(name="batch.a"))
    with pytest.raises(QueueFull):
        q.enqueue(Job(name="batch.b"))


def test_depth_by_priority():
    q = PriorityQueue()
    for job in _jobs():
        q.enqueue(job)
    assert q.depth_by_priority() == {"high": 1, "normal": 1, "low": 1}
