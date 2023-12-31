from package import AddressBook, Record, wraps, json, Phone, AddressBookEncoder
import re

file_json  = "test.json"
a_book = AddressBook() 
try:
    with open(file_json, "r") as file:
        unpacked = json.load(file)
    a_book.from_dict(unpacked)
except FileNotFoundError:
    with open(file_json, "w") as file:
        json.dump({}, file)
     
def input_error(func):
    @wraps(func) #для отображения доки/имени
    def wrapper(*args):
        """
        декоратор ловит ошибки функций 
        недостаток аргументов и созданние ошибки
        затем возвращает на принт 
        """
        try:
            return func(*args)
        except IndexError:
            command, formula = COMMANDS_HELP.get(func.__name__)
            command = '/'.join(command)
            return (f"Wrong input for this command [{command}]\n"
                    f"for example:\t[{command}] {formula}"
                    )
        except ValueError as err:
            return f"Input error: {str(err)}."
        except KeyError as err:
            return f"Give me the name from phonebook: {str(err)}."
    return wrapper  

@input_error
def add_handler(data: list[str]) -> str:
    """
    Add a new contact to the address book.

    Args:
        data (list): A list containing contact information.

    Returns:
        str: A confirmation message for the added contact.
    """
    if len(data) <= 1 : raise IndexError
    if len(data) >= 3:
        name, phone, birthday = data
        record = Record(name, [phone], birthday)
    else:
        name, phone, = data
        record = Record(name, [phone])     

    a_book.add_record(record)
    return f"contact {str(record)} has be added"

@input_error
def add_handler_phone(data : list[str]) -> str:
    """
    Add a new phone number to an existing contact.

    Args:
        data (list): A list containing contact information.

    Returns:
        str: A confirmation message for the added phone number.
    """
    if len(data) <= 1 : raise IndexError
    name, new_phone, = data
    a_book[name].add_phone(new_phone)
    return f"Successful added phone {Phone(new_phone)} to contact {name}"

@input_error
def change_handler_phone(data: list[str]) -> str:
    """
    Change the phone number of an existing contact.

    Args:
        data (list): A list containing contact information.

    Returns:
        str: A confirmation message for the changed phone number.
    """
    if len(data) <= 2 : raise IndexError
    name, old_phone, new_phone, = data
    a_book[name].change_phone(old_phone, new_phone)
    return f"contact {name} has be changed phone to {Phone(new_phone)}"

@input_error
def del_handler_phone(data: list[str]) -> str:
    """
    Delete a phone number from an existing contact.

    Args:
        data (list): A list containing contact information.

    Returns:
        str: A confirmation message for the deleted phone number.
    """
    if len(data) <= 1 : raise IndexError
    name, old_phone, = data
    a_book[name].remove_phone(old_phone)
    return f"phone - {Phone(old_phone)} from contact {name} has be deleted"

@input_error
def delete_handler(data: list[str]) -> str:
    """
    Delete an existing contact.

    Args:
        data (list): A list containing contact information.

    Returns:
        str: A confirmation message for the deleted contact.
    """
    if len(data) < 1 : raise IndexError
    name, = data
    del a_book[name]
    return f"contact {name} has be deleted"

@input_error
def add_handler_birthday(data: list[str]) -> str:
    """
    Add a birthday to an existing contact.

    Args:
        data (list): A list containing contact information.

    Returns:
        str: A confirmation message for the added birthday.
    """
    if len(data) <= 1 : raise IndexError
    name, birthday, = data
    record = a_book[name]
    if record.birthday is not None:
        return f"this contact {name} is already have a date of birth: {record.birthday}"
    record.change_birthday(birthday)
    return f"contact {name} is added a date of birth: {record.birthday}"
    
@input_error
def change_handler_birthday(data: list[str]) -> str:
    """
    Change the birthday of an existing contact.

    Args:
        data (list): A list containing contact information.

    Returns:
        str: A confirmation message for the changed birthday.
    """
    if len(data) <= 1 : raise IndexError
    name, birthday, = data
    a_book[name].change_birthday(birthday)
    return f"contact {name} is changed to date of birth: {birthday}"  

@input_error
def handler_days_to_birthday(data: list[str]) -> str:
    """
    Get the number of days until the next birthday of an existing contact.

    Args:
        data (list): A list containing contact information.

    Returns:
        str: The number of days until the next birthday.
    """
    if len(data) < 1 : raise IndexError
    name, = data
    days = a_book[name].days_to_birthday() 
    return f"{days} days left until {name}'s birthday"  

@input_error
def search_handler(data: list[str]) -> str:
    """
    Search for contacts by a given keyword.

    Args:
        data (list): A list containing search keyword.

    Returns:
        str: A formatted list of contacts matching the search keyword.
    """
    if len(data) < 1 : raise IndexError
    search_word, = data
    res = "\n".join([str(rec)[9:] for rec in a_book.search(search_word)])
    if not res:  
        return "not found any contact"
    return res

@input_error
def show_page(data: list[str]) -> str:
    """
    Display contacts page by page.

    Args:
        data (list): A list containing the number of records per page.

    Yields:
        str: Formatted contacts for display, separated by pages.
    """
    count_record, = data if len(data) >= 1 else "1"
    try: 
        count_record = int(count_record)
        yield "input any for next page"
        for i, page in enumerate(a_book.iterator(count_record), 1):
            page = "\n".join(map(lambda x: str(x)[9:], page ))
            input("") 
            head = f'{"-" * 15} Page {i} {"-" * 15}\n'
            yield head + page
        yield f'{"-" * 15} end {"-" * 15}\n'   
    except ValueError: # без єтого гавнокода все падает(с вводом не цифр) 
        for _ in range(1):
            yield "invalid input count page"

def help_handler(*args) -> str:
   return "\n".join(
        [
        '{:<26}{:<}'.format(" / ".join(com_anot[0]), com_anot[1]) 
        for com_anot in COMMANDS_HELP.values()
        ]
        )

def show_all(*args) -> str:
    # тут может бить красивая формат обертка через цикл и поля рекорда
    return "\n".join([str(record)[9:] for record in a_book.values()])

def hello_handler(*args) -> str:
    return "How can I help you?"

def exit_handler(*args) -> str:
    with open(file_json, "w") as file:
        json.dump(a_book, file, cls=AddressBookEncoder, sort_keys=True, indent=4)
    return "Good bye!"

def unknown_command(*args) -> str:
    return 'Unknown command'

def command_parser(row_str: str):
    """
    Parse a row string to identify and extract a command and its arguments.

    Args:
        row_str (str): A string containing the command and its arguments.

    Returns:
        tuple: A tuple containing the identified command key and a list of arguments.
    """
    row_str = re.sub(r'\s+', ' ', row_str) 
    elements = row_str.strip().split(" ")
    for key, value in BOT_COMMANDS.items():
        if elements[0].lower() in value[0]:
            return key, elements[1:]
        elif " ".join(elements[:2]).lower() in value[0]: 
            return key, elements[2:] 
    return unknown_command, None

BOT_COMMANDS = {
    # при командах (с одинаковими первими словами)"add" & "add phone" работает какую первую найдет
    hello_handler: (
        ["hello"],
        "hello"
        ),
    add_handler: (
        ["add", "+"], 
        "name phone(num) or name phone(num) date(ISO)"
        ),
    add_handler_phone: (
        ["add_phone"], 
        "name phone(num)"
        ),
    change_handler_phone: (
        ["change phone"], 
        "name old_phone(num) new_phone(num)"
        ),
    add_handler_birthday : (
        ["birthday"], 
        "name date(ISO)"
        ),
    change_handler_birthday: (
        ["change birthday"], 
        "name new_date(ISO)"
        ),
    handler_days_to_birthday: (
        ["days"], 
        "name"),
    del_handler_phone: (
        ["del phone"], 
        "name phone(num)"
        ),
    delete_handler: (
        ["delete"], 
        "name"),
    search_handler: (
        ["search"], 
        "search(alpha/num)"
        ),
    show_all: (
        ["show all"], 
        "show all address book"
        ),
    show_page : (
        ["show page"], 
        "int_num(positive) - show all address book"
        ),
    help_handler: (
        ["help"], 
        "- show all bot commands"
        ),    
    exit_handler: (
        ["good bye", "close", "exit"], 
        "- save changesets and exit"
        ),
}

COMMANDS_HELP = {k.__name__:v for k,v in BOT_COMMANDS.items()}

def main():
    while True:
        user_input = input(">>>")
        if not user_input or user_input.isspace():
            continue

        func_handler, data = command_parser(user_input)
        
        if func_handler == show_page:
            for page in func_handler(data):
                print(page)
            continue    

        bot_message = func_handler(data)    
        print(bot_message)
        
        if func_handler == exit_handler:
            break
        
if __name__ == "__main__":
    main()