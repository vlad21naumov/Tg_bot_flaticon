from aiogram.dispatcher.filters.state import State, StatesGroup

# maybe it won't be used
class UsersIcons(StatesGroup):
    name = State()
    look_icon = State()
    look_history = State()
    # default = State()