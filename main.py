from package import AddressBook, AddressBookEncoder, Record, wraps, json, Phone
import re

file_json = "test.json"
with open(file_json, "r") as file:
    unpacked = json.load(file)
a_book = AddressBook()    
a_book.from_dict(unpacked)


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
        except IndexError as err:
            return f"Give me name and phone please {str(err)}"
        except ValueError as err:
            return f"Give me an information: {str(err)}"
        except KeyError as err:
            return f"Give me the name from phonebook {str(err)}"
    return wrapper  

@input_error
def add_handler(data: list[str]) -> str:
    """"""
    name, phone, = data
    record = Record(name, phone, data[2]) if len(data)>= 3 else Record(name, phone) 
    a_book.add_record(record)
    return f"contact {str(record)[9:]} has be added"

@input_error
def add_handler_phone(data : list[str]) -> str:
    """"""
    name, new_phone, = data
    record = a_book.get_record(name)
    record.add_phone(new_phone)
    return f"Successful added phone {Phone(new_phone)} to contact {name}"

@input_error
def change_handler_phone(data: list[str]) -> str:
    """"""
    name, old_phone, new_phone, = data
    record = a_book.get_record(name)
    record.change_phone(old_phone, new_phone)
    return f"contact {name} has be changed phone to {Phone(new_phone)}"

@input_error
def del_handler_phone(data: list[str]) -> str:
    """"""
    name, old_phone, = data
    record = a_book.get_record(name)
    record.remove_phone(old_phone)
    return f"phone - {Phone(old_phone)} from contact {name} has be deleted"

@input_error
def delete_handler(data: list[str]) -> str:
    """"""
    name, = data
    a_book.del_record(name)
    return f"contact {name} has be deleted"

@input_error
def add_handler_birthday(data: list[str]) -> str:
    """"""
    name, birthday = data
    record = a_book.get_record(name)
    if record.birthday is not None:
        return f"this contact {name} is already have a date of birth: {record.birthday}"
    record.change_birthday(birthday)
    return f"contact {name} is added a date of birth: {record.birthday}"
    
@input_error
def change_handler_birthday(data: list[str]) -> str:
    """"""
    name, birthday = data
    record = a_book.get_record(name)
    record.change_birthday(birthday)
    return f"contact {name} is changed to date of birth: {record.birthday}"  

@input_error
def handler_days_to_birthday(data: list[str]) -> str:
    """"""
    name, = data
    record = a_book.get_record(name)
    days = record.days_to_birthday() 
    return f"{days} days left until {name}'s birthday"  

@input_error
def search_handler(data: list[str]) -> str:
    """"""
    search_word, = data
    res = "\n".join(a_book.search(search_word))
    if not res:  #TODO not work???
        return "not found any contact"
    return res

def show_all(*args) -> str:
    # тут может бить красивая формат обертка через цикл и поля рекорда
    return "\n".join([str(record)[9:] for record in a_book.values()])

def hello_handler(*args) -> str:
    return "How can I help you?"

def exit_handler(*args) -> str:
    with open(file_json, "w") as fh:
        json.dump(a_book, fh, cls=AddressBookEncoder, sort_keys=True, indent=2)
    return "Good bye!"

def unknown_command(*args) -> str:
    return 'Unknown command'

def command_parser(row_str: str):
    """"""
    row_str = re.sub(r'\s+', ' ', row_str) 
    elements = row_str.strip().split(" ")
    for key, value in BOT_COMMANDS.items():
        if elements[0].lower() in value:
            return key, elements[1:]
        elif " ".join(elements[:2]).lower() in value: 
            return key, elements[2:] 
    return unknown_command, None

BOT_COMMANDS = {
    # при командах (с одинаковими первими словами)"add" & "add phone" работает какую первую найдет
    hello_handler: ["hello"],
    add_handler: ["add", "+"],
    add_handler_phone: ["add_phone"],
    change_handler_phone: ["change phone"],
    add_handler_birthday : ["birthday"],
    change_handler_birthday: ["change birthday"],
    handler_days_to_birthday: ["days"],
    del_handler_phone: ["del phone"],
    delete_handler: ["delete"],
    search_handler: ["search"],
    show_all: ["show all"],
    exit_handler: ["good bye", "close", "exit"],
}

def main():
    while True:
        user_input = input(">>>")
        if not user_input or user_input.isspace():
            continue

        func_handler, data = command_parser(user_input)
        bot_message = func_handler(data)
      
        print(bot_message)
        
        if func_handler == exit_handler:
            break
        
if __name__ == "__main__":
    main()