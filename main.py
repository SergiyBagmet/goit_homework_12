from package import AddressBook, Record, wraps





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
            return "Give me name and phone please"
        except ValueError:
            return "Give me an information"
        except KeyError:
            return "Give me the name from phonebook"
    return wrapper  





def hello_handler(*args):
    return "How can I help you?"

def exit_handler(*args):
    return "Good bye!"

def unknown_command(*args):
    return 'Unknown command'

def command_parser(row_str: str):
    elements = row_str.split(" ")
    for key, value in BOT_COMMANDS.items():
        if elements[0].lower() in value:
            return key, elements[1:]
        elif " ".join(elements[:2]).lower() in value: 
            return key, elements[2:] 
    return unknown_command, None

BOT_COMMANDS = {
    # add_handler: ["add", "+"],
    exit_handler: ["good bye", "close", "exit"],
    hello_handler: ["hello"],
    # change_handler: ["change"],
    # show_all: ["show all"]
}

def main():
    a_book = AddressBook()
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