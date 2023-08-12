from package import AddressBook, AddressBookEncoder, Record, wraps, json, Phone


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
            return f"Give me an information {str(err)}"
        except KeyError as err:
            return f"Give me the name from phonebook {str(err)}"
    return wrapper  

@input_error
def add_handler(data: list) -> str:
    """"""
    name, phone = data[:2] 
    rec = Record(name, phone, data[2]) if len(data)>= 3 else Record(name, phone) 
    a_book.add_record(rec)
    return f"contact {str(rec)[9:]} has be added"

@input_error
def change_handler_phone(data: list) -> str:
    """"""
    name, old_phone, new_phone = data[:3]
    rec = a_book.get_record(name)
    rec.change_phone(old_phone, new_phone)
    return f"contact {name} has be changed phone to {Phone(new_phone)}"

def show_all(*args) -> str:
    return "\n".join([str(record)[9:] for record in a_book.values()])

def hello_handler(*args):
    return "How can I help you?"

def exit_handler(*args):
    with open(file_json, "w") as fh:
        json.dump(a_book, fh, cls=AddressBookEncoder, sort_keys=True, indent=2)
    return "Good bye!"

def unknown_command(*args):
    return 'Unknown command'

def command_parser(row_str: str):
    elements = row_str.strip().split(" ")
    for key, value in BOT_COMMANDS.items():
        if elements[0].lower() in value:
            return key, elements[1:]
        elif " ".join(elements[:2]).lower() in value: 
            return key, elements[2:] 
    return unknown_command, None

BOT_COMMANDS = {
    add_handler: ["add", "+"],
    exit_handler: ["good bye", "close", "exit"],
    hello_handler: ["hello"],
    change_handler_phone: ["change phone"],
    show_all: ["show all"]
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