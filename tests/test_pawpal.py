"""Quick tests for the most important PawPal+ behaviors."""

from pawpal_system import Pet, Priority, Task


def test_mark_complete_changes_status():
    """Task Completion: mark_complete() flips completed False -> True."""
    task = Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Task Addition: adding a task to a Pet grows its task list by one."""
    pet = Pet(name="Rex", species="dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task(title="Feeding", duration_minutes=15, priority=Priority.HIGH))

    assert len(pet.tasks) == 1
