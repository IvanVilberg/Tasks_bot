from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os, datetime

import app.keyboards as kb
from app.database.models import async_session, User, Personal_task
from app.database.requests import get_user, get_personal_tasks, get_personal_task_from_task_id

router = Router()

class Registration(StatesGroup):
    name = State()
    surname = State()
    
class CreatePersonalTask(StatesGroup):
    task_id = State()
    user_id = State()
    title = State()
    description = State()
    status = State()
    created_date = State()
    updated_date = State()
    due_date = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    # await message.answer_photo(photo=InputFile("~/Документы/TelegramBot/images/big_logo.jpg"), caption='Добро пожаловать в Tasks - бота который поможет вам в достижении ваших и корпоративных целей и задач',
    #     reply_markup=await kb.hello_buttons())
    
    await message.answer(
        'Добро пожаловать в Tasks - бота который поможет вам в достижении ваших и корпоративных целей и задач',
        reply_markup=await kb.hello_buttons()
    )
    
@router.callback_query(F.data == 'start')
async def start_login(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id
    user = await get_user(tg_id)
    
    if user:
        await callback.message.answer(f"Здравствуйте! \nРады снова вас видеть\n{user.name} {user.surname}", reply_markup=kb.main)
    else:
        await callback.message.answer("В первый раз пользуетесь нашим сервисом? \nПожалуйста, пройдите регистрацию")
        await callback.message.answer('Введите имя:')
        await state.set_state(Registration.name)
        await callback.answer()

         
@router.message(Registration.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите фамилию:')
    await state.set_state(Registration.surname)
    
@router.message(Registration.surname)
async def process_surname(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    await state.update_data(username=message.text)
    user_data = await state.get_data()
    date = datetime.date
    name = user_data["name"]
    surname = user_data["username"]
    
    async with async_session() as session:
        async with session.begin():
            new_user = User(tg_id = tg_id, name=name, surname=surname, mode = "-")
            session.add(new_user)
            await session.commit()
    
    await message.answer(f'Регистрация завершена!\nВаше имя: {user_data["name"]}\nВаша фамилия: {user_data["username"]}', reply_markup=kb.main)
    await state.clear()

@router.message(F.text == 'Создать персональную задачу')
async def create_personal_task(message: Message, state: FSMContext):
    await message.answer('Введите заголовок задачи:')
    await state.set_state(CreatePersonalTask.title)

@router.message(CreatePersonalTask.title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title = message.text)
    await message.answer('Введите описание задачи:')
    await state.set_state(CreatePersonalTask.description)
    
@router.message(CreatePersonalTask.description)
async def create_personal_task_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)

    user = await get_user(message.from_user.id)
    user_id = user.user_id
    status = "В ожидании"
    created_date = datetime.datetime.now()

    task = await state.get_data()
    title = task["title"]
    description = task["description"]

    async with async_session() as session:
        async with session.begin():
            new_personal_task = Personal_task(
                user_id=user_id,
                title=title,
                description=description,
                status=status,
                created_date=created_date,
                updated_date=created_date,
                due_date=None
            )
            session.add(new_personal_task)
            await session.commit()

    await message.answer("Задача успешно создана")
    await state.clear()
    

@router.message(F.text == 'Аккаунт')
async def display_account(message: Message):
    user = await get_user(message.from_user.id)
    
    personal_tasks = await get_personal_tasks(user.user_id)
    
    completed_tasks = 0
    pending_tasks = 0
    in_progress_tasks = 0
    
    for task in personal_tasks:
        if task.status == "Выполнено":
            completed_tasks += 1
        elif task.status == "В ожидании":
            pending_tasks += 1
        elif task.status == "В работе":
            in_progress_tasks += 1
    
    await message.answer(f'Аккаунт: \n{user.name} {user.surname} \n'
                         f'Кол-во задач: {len(personal_tasks)} \n'
                         f'Выполненные задачи: {completed_tasks} \n'
                         f'Не выполненные задачи: {pending_tasks} \n'
                         f'Задачи в процессе: {in_progress_tasks}')   

    
@router.message(F.text == 'Персональные задачи')
async def display_personal_tasks(message: Message):
    user = await get_user(message.from_user.id)
    

    
    if not user:
        await message.answer("Пользователь не найден")
        return
    
    personal_tasks = await get_personal_tasks(user.user_id)
    
    if not personal_tasks:
        await message.answer("У вас пока нет персональных задач")
        return
    
    for task in reversed(personal_tasks):
        
        created_task_str = task.created_date.strftime('%d-%m-%Y %H:%M')
        
        await message.answer(f"❗️Задача: \n{task.title}\nОписание: \n{task.description}\nСтатус: \n{task.status} \nДата создания {created_task_str}",
            reply_markup= await kb.options_task(task.task_id))
        
        
@router.callback_query(F.data.startswith('done_'))
async def mark_task_done(callback: CallbackQuery):
    task_id = int(callback.data.split('_')[1])
    async with async_session() as session:
        async with session.begin():
            task = await get_personal_task_from_task_id(task_id)
            task.status = 'Выполнено'
            task.updated_date = datetime.datetime.now()
            await session.commit()
    await callback.message.edit_text(f"Задача '{task.title}' обновлена до статуса 'Выполнено'.")
    await callback.answer()

@router.callback_query(F.data.startswith('inwork_'))
async def mark_task_in_work(callback: CallbackQuery):
    task_id = int(callback.data.split('_')[1])
    async with async_session() as session:
        async with session.begin():
            task = await get_personal_task_from_task_id(task_id)
            task.status = 'В работе'
            task.updated_date = datetime.datetime.now()
            await session.commit()
    await callback.message.edit_text(f"Задача '{task.title}' обновлена до статуса 'В работе'.")
    await callback.answer()

@router.callback_query(F.data.startswith('delete_'))
async def delete_task(callback: CallbackQuery):
    task_id = int(callback.data.split('_')[1])
    async with async_session() as session:
        async with session.begin():
            task = await get_personal_task_from_task_id(task_id)
            await session.delete(task)
            await session.commit()
    await callback.message.edit_text("Задача удалена.")
    await callback.answer()