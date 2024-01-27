import aiosqlite as sq

db = sq.connect('tg.db')
cur = db.cursor()


async def db_start():
    await db.execute("""CREATE TABLE IF NOT EXISTS accounts(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            tg_id INTEGER,
                            cart_id TEXT)""")
    await db.execute("""CREATE TABLE IF NOT EXISTS items(
                            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            desc TEXT,
                            price TEXT,
                            photo TEXT)""")
    await db.commit()


async def cmd_start_db(user_id):
    user = cur.execute("SELECT * FROM accounts WHERE tg_id == {key}".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO accounts (tg_id) VALUES ({key})".format(key=user_id))
        await db.commit()


async def add_item(state):
    async with state.proxy() as data:
        cur.execute("INSERT INTO items (name, desc, price, photo, brand) VALUES (?, ?, ?, ?, ?)",
                    (data['name'], data['desc'], data['price'], data['photo'], data['type']))
        await db.commit()


async def add_account(tg_id, cart_id):
    async with sq.connect('tg.db') as db:
        await db.execute('INSERT INTO accounts (tg_id, cart_id) VALUES (?, ?)', (tg_id, cart_id))
        await db.commit()


async def add_item(name, desc, price, photo):
    async with sq.connect('tg.db') as db:
        await db.execute('INSERT INTO items (name, desc, price, photo) VALUES (?, ?, ?, ?)', (name, desc, price, photo))
        await db.commit()


async def get_accounts():
    async with sq.connect('tg.db') as db:
        async with db.execute('SELECT * FROM accounts') as cursor:
            return await cursor.fetchall()


async def get_items():
    async with sq.connect('tg.db') as db:
        async with db.execute('SELECT * FROM items') as cursor:
            return await cursor.fetchall()


# ... Добавьте другие функции, которые вам нужны для работы с базой данных

# Пример использования функций:
# asyncio.run(db_start())
# asyncio.run(add_account(tg_id, cart_id))
# asyncio.run(add_item(name, desc, price, photo))
# accounts = asyncio.run(get_accounts())
# items = asyncio.run(get_items())
