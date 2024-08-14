from app.database.models import User, Personal_task, async_session
from sqlalchemy import select, update, delete

async def get_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return user
    
async def get_personal_tasks(user_id):
    async with async_session() as session:
        result = await session.scalars(select(Personal_task).where(Personal_task.user_id == user_id))
        personal_tasks = result.all()
        return personal_tasks
    
async def get_personal_task_from_tg_id(tg_id):
    user = await get_user(tg_id)
    if user:
        personal_tasks = await get_personal_tasks(user.id)
        return personal_tasks
    return []

async def get_personal_task_from_task_id(task_id):
    async with async_session() as session:
        result = await session.scalar(select(Personal_task).where(Personal_task.task_id == task_id))
        return result

 