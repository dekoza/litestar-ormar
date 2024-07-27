from uuid import UUID, uuid4

import ormar
import pytest
import pytest_asyncio
from litestar.repository import NotFoundError
from litestar.repository.filters import CollectionFilter, NotInCollectionFilter

from litestar_ormar import OrmarRepository
from tests.settings import create_config, init_tests

base_ormar_config = create_config()


class ExampleModel(ormar.Model):
    ormar_config = base_ormar_config.copy()

    id: UUID = ormar.UUID(default=uuid4, primary_key=True, autoincrement=True)
    name: str = ormar.String(max_length=10)


class OtherModel(ormar.Model):
    ormar_config = base_ormar_config.copy()
    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=10)


create_test_database = init_tests(base_ormar_config)


class OrmarTestRepository(OrmarRepository):
    model_type = ExampleModel


class OrmarOtherRepository(OrmarRepository):
    model_type = OtherModel


repo = OrmarTestRepository()
other_repo = OrmarOtherRepository()


@pytest_asyncio.fixture(autouse=True, scope="function")
async def cleanup():
    yield
    async with base_ormar_config.database:
        await ExampleModel.objects.delete(each=True)
        await OtherModel.objects.delete(each=True)


@pytest.mark.asyncio
async def test_add():
    async with base_ormar_config.database:
        obj = ExampleModel(name="test")
        result = await repo.add(obj)
        assert result is not None
        result = await ExampleModel.objects.first()
        assert result is not None


@pytest.mark.asyncio
async def test_add_many():
    async with base_ormar_config.database:
        objects = [ExampleModel(name=f"test_{i}") for i in range(5)]
        result = await repo.add_many(objects)
        assert len(objects) == len(result)
        result = await ExampleModel.objects.all()
        assert len(objects) == len(result)


@pytest.mark.asyncio
async def test_count():
    async with base_ormar_config.database:
        objects = [ExampleModel(name=f"test_{i}") for i in range(5)]
        await repo.add_many(objects)
        result = await repo.count()
        assert len(objects) == result


@pytest.mark.asyncio
async def test_count_filtered():
    async with base_ormar_config.database:
        objects = [ExampleModel(name=f"test_{i}") for i in range(5)]
        await repo.add_many(objects)
        await ExampleModel(name="other").save()

        result = await repo.count(name__startswith="o")
        assert result == 1

        filter = CollectionFilter(field_name="name", values=["other"])
        result = await repo.count(filter)
        assert result == 1

        filter = NotInCollectionFilter(field_name="name", values=["other"])
        result = await repo.count(filter)
        assert result == 5

        result = await repo.count(name__startswith="nope")
        assert result == 0


@pytest.mark.asyncio
async def test_delete():
    async with base_ormar_config.database:
        obj = await ExampleModel(name="other").save()
        assert obj.saved
        assert await repo.count(id=obj.id) == 1
        obj2 = await repo.delete(obj.id)
        assert obj2 is not None
        assert obj2.id == obj.id
        assert await repo.count(id=obj.id) == 0


@pytest.mark.asyncio
async def test_delete_nonexistent():
    async with base_ormar_config.database:
        with pytest.raises(NotFoundError):
            await repo.delete(uuid4())


@pytest.mark.asyncio
async def test_delete_many():
    async with base_ormar_config.database:
        objects = [await ExampleModel(name=f"test_{i}").save() for i in range(5)]
        ids_to_del = [obj.id for obj in objects]
        ids_to_del.append(uuid4())  # add nonexistent
        del_objects = await repo.delete_many(ids_to_del)
        assert await repo.count(id__in=ids_to_del) == 0
        assert len(del_objects) == len(objects)


@pytest.mark.asyncio
async def test_exists():
    async with base_ormar_config.database:
        assert not await repo.exists(name="test")

        await ExampleModel(name="test").save()
        assert await repo.exists(name="test")


@pytest.mark.asyncio
async def test_get():
    async with base_ormar_config.database:
        obj = await ExampleModel(name="example").save()
        obj2 = await repo.get(obj.id)
        assert obj2 is not None
        assert obj2.id == obj.id


@pytest.mark.asyncio
async def test_get_nonexistent():
    async with base_ormar_config.database:
        with pytest.raises(NotFoundError):
            await repo.get(uuid4())


@pytest.mark.asyncio
async def test_get_one():
    async with base_ormar_config.database:
        objects = [await ExampleModel(name=f"test_{i}").save() for i in range(5)]
        obj_ids = [obj.id for obj in objects]
        result = await repo.get_one(name__startswith="test")
        assert result is not None
        assert result.id in obj_ids


@pytest.mark.asyncio
async def test_get_one_nonexistent():
    async with base_ormar_config.database:
        with pytest.raises(NotFoundError):
            await repo.get_one(name="nope")


@pytest.mark.asyncio
async def test_get_or_create():
    async with base_ormar_config.database:
        obj = await ExampleModel(name="test").save()
        obj2, created = await repo.get_or_create(name="test")
        assert obj2 is not None
        assert obj2.id == obj.id
        assert not created

        obj3, created = await repo.get_or_create(name="new one")
        assert obj3 is not None
        assert created


@pytest.mark.asyncio
async def test_get_one_or_none():
    async with base_ormar_config.database:
        obj = await repo.get_one_or_none(name="test")
        assert obj is None

        obj2 = await ExampleModel(name="test").save()
        result = await repo.get_one_or_none(name="test")
        assert result is not None
        assert result.id == obj2.id


@pytest.mark.asyncio
async def test_update():
    async with base_ormar_config.database:
        obj = ExampleModel(name="example")
        with pytest.raises(NotFoundError):
            await repo.update(obj)
        assert not await ExampleModel.objects.filter(name="example").exists()

        await obj.save()
        assert await ExampleModel.objects.filter(name="example").exists()
        assert not await ExampleModel.objects.filter(name="updated").exists()
        obj.name = "updated"
        result = await repo.update(obj)
        assert result is not None
        assert result.name == "updated"

        assert await ExampleModel.objects.filter(id=obj.id, name="updated").exists()


@pytest.mark.asyncio
async def test_update_many():
    async with base_ormar_config.database:
        objects = [await ExampleModel(name=f"test_{i}").save() for i in range(5)]
        for o in objects:
            o.name = "up " + o.name
        updated = await repo.update_many(objects)
        selected = await ExampleModel.objects.filter(name__startswith="up").count()
        assert selected == len(objects) == len(updated)


@pytest.mark.parametrize(
    "Model, repository", [(ExampleModel, repo), (OtherModel, other_repo)]
)
@pytest.mark.asyncio
async def test_upsert(Model, repository):
    async with base_ormar_config.database:
        assert 0 == await Model.objects.filter(name="example").count()
        # insert
        obj = Model(name="example")
        assert 0 == await Model.objects.filter(id=obj.id).count()
        await repository.upsert(obj)
        assert 1 == await Model.objects.filter(id=obj.id).count()
        assert 1 == await Model.objects.filter(name="example").count()
        # update
        obj.name = "updated"
        await repository.upsert(obj)
        assert 0 == await Model.objects.filter(name="example").count()
        assert 1 == await Model.objects.filter(name="updated").count()


@pytest.mark.asyncio
async def test_upsert_bad_id():
    async with base_ormar_config.database:
        with pytest.raises(NotFoundError):
            obj = OtherModel(id=5, name="test")
            await other_repo.upsert(obj)


@pytest.mark.asyncio
async def test_upsert_copied_id():
    async with base_ormar_config.database:
        obj = await OtherModel(name="test").save()
        assert obj.id is not None

        new_obj = OtherModel(name="updated")
        assert new_obj.id is None
        new_obj.id = obj.id
        assert new_obj.id is not None
        await other_repo.upsert(new_obj)

        assert 0 == await OtherModel.objects.filter(name="test").count()
        assert 1 == await OtherModel.objects.filter(name="updated").count()


@pytest.mark.asyncio
async def test_upsert_many():
    async with base_ormar_config.database:
        objects = [await ExampleModel(name=f"test_{i}").save() for i in range(5)]
        objects.extend([await ExampleModel(name=f"new_{i}").save() for i in range(5)])

        for o in objects:
            o.name = f"up_{o.name}"
        await repo.upsert_many(objects)

        assert 10 == await ExampleModel.objects.count()


@pytest.mark.asyncio
async def test_upsert_many_mismatched():
    # TODO: check if this behavior is OK
    async with base_ormar_config.database:
        objects = [await OtherModel(name=f"test_{i}").save() for i in range(5)]
        for o in objects:
            o.name = f"up_{o.name}"
        objects.append(OtherModel(id=10000, name="badboy"))
        with pytest.raises(NotFoundError):
            await other_repo.upsert_many(objects)
        assert 5 == await OtherModel.objects.count()


@pytest.mark.asyncio
async def test_list():
    async with base_ormar_config.database:
        objects = [await OtherModel(name=f"test_{i}").save() for i in range(5)]

        retrieved = await other_repo.list()

        assert set(obj.id for obj in objects) == set(obj.id for obj in retrieved)


@pytest.mark.asyncio
async def test_list_filtered():
    async with base_ormar_config.database:
        [await OtherModel(name=f"test_{i}").save() for i in range(5)]
        more_objects = [await OtherModel(name=f"other_{i}").save() for i in range(3)]

        retrieved = await other_repo.list(name__startswith="other")

        assert set(obj.id for obj in more_objects) == set(obj.id for obj in retrieved)


@pytest.mark.asyncio
async def test_list_and_count():
    async with base_ormar_config.database:
        objects = [await OtherModel(name=f"test_{i}").save() for i in range(5)]

        retrieved, count = await other_repo.list_and_count()

        assert set(obj.id for obj in objects) == set(obj.id for obj in retrieved)
        assert count == len(objects)


@pytest.mark.asyncio
async def test_typechecker():
    obj = await OtherModel(name="test").save()

    with pytest.raises(TypeError):
        await repo.add(obj)

    with pytest.raises(TypeError):
        await repo.add_many([obj])
