from collections import UserDict
import json
from datetime import date 
import typing as t

class Field:
    """
    Class parent representing a field used in the record of the address book.
    """
    def __init__(self, value: str) -> None:
        self.value = value 
      
    def __valid_value(self, value) -> None:
        if not isinstance(value, str):
            raise TypeError(f'Value {value} is not valid. Must be string')
        
    @property
    def value(self) :
        return self._value
    
    @value.setter
    def value(self, value: str, validation: t.Callable | None = None) -> None:
        self.__valid_value(value)
        if validation is not None:
            value = validation(value)
        self._value = value

    def __str__(self) -> str:
        return f'{self.value}'
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(value={self.value})'
    
    def __eq__(self, val):  # ==
        if isinstance(val, self.__class__): # можно и через if hasattr(val, 'value'):
            val = val.value
        return self.value == val
    

class Name(Field):
    """
    Class representing the name field in a record of  the address book.
    """
    pass
 
       
class Phone(Field):
    """
    Class representing the phone field in a record of the address book.
    """ 
    def __valid_phone(self, value) -> str: 
        phone = ''.join(filter(str.isdigit, value))
        if 9 >= len(phone) <= 15 : #псевдо проверка номера
            raise ValueError(f"Phone number {value} isn't correct")
        return phone

    @Field.value.setter # переопределяем сеттер родительского класса
    def value(self, value: str) -> None:
        Field.value.fset(self, value, self.__valid_phone)
        

class Birthday(Field):
    """
    Class representing the birthday field in a record of the address book.
    The date is stored in ISO 8601 format.
    """

    def __valid_date(self, value: str) -> str:
        """
        Input date string to a valid ISO-formatted date.
        Args:
            value (str): The input date string.
        Raises:
            ValueError: If the input date string is not in a valid date format(ISO).
        Returns:
            str: The valid ISO-formatted date string.    
        """
        try:
            date.fromisoformat(value)
        except ValueError: 
            raise ValueError(f'Value {value} is not correct format! Also "2023-12-30"')
        return value    
    
    @Field.value.setter
    def value(self, value: str) -> None:
        Field.value.fset(self, value, self.__valid_date)
        
    def get_date(self) -> date:
        return date.fromisoformat(self.value)    

class Record:
    """
    Class representing a record in an address book.

    Attributes:
        name (Name): The name of the contact.
        phones (list): A list of phone numbers associated with the contact.
        birthday (Birthday): The birthday of the contact.
    """
  
    def __init__(
            self, 
            name: Name | str, 
            phones: list[Phone] | list[str] = [], 
            birthday: Birthday | str | None = None, 
        ) -> None:

        self.name = self._name(name)
        self.phones = [self._phone(phone) for phone in phones]
        self.birthday = None if birthday is None else self._birthday(birthday)
        

    def _name(self, name: str | Name) -> Name:
        if not isinstance(name, Name):
            name = Name(name)
        return name

    def _phone(self, phone: str | Phone) -> Phone:
        if not isinstance(phone, Phone):
            phone = Phone(phone)
        return phone

    def _birthday(self, birthday: str | Birthday) -> Birthday:
        if not isinstance(birthday, Birthday):
            birthday = Birthday(birthday)
        return birthday    
  
    def add_phone(self, phone: Phone | str) -> None:
        """
        Add a new phone number to the list of phone numbers for the contact.
        Args:
            phone (Phone) or try valid Str: The phone number to be added to the contact.
        Returns:
            None: This method does not return any value.
        """
        if phone in self.phones:
            raise ValueError("this phone number has already been added")
        
        phone = self._phone(phone)
        self.phones.append(phone)

    def remove_phone(self, phone: Phone | str) -> None:
        """
        Remove a phone number from the list of phone numbers for the contact.

        Args:
            phone (Phone) or try valid Str: The phone number to be removed from the contact.
        Raises:
            ValueError: If the phone number is not found in the contact's list of phone numbers.
        Returns: 
            None: This method does not return any value.
        """
        phone = self._phone(phone) # єту строку может после райза?
        if phone not in self.phones:
            raise ValueError(f"The phone '{phone}' is not in this record.")
        self.phones.remove(phone)
        
    def change_phone(self, old_phone: Phone | str, new_phone: Phone | str) -> None:
        """
        Change a phone number in the list of phone numbers for the contact.

        Args:
            old_phone (Phone)  or try valid Str: The existing phone number to be replaced.
            new_phone (Phone)  or try valid Str: The new phone number to replace the existing one.
        Raises:
            ValueError: If the old phone number is not found in the contact's list of phone numbers.
            ValueError: If the new phone number is already in contact's list of phone numbers.
        """
        
        if (old_phone := self._phone(old_phone)) not in self.phones: 
            raise ValueError(f"The phone '{old_phone}' is not in this record '{self.name}'.")
        if (new_phone := self._phone(new_phone)) in self.phones:
            raise ValueError(f"The phone '{new_phone}' already in record '{self.name}'.")
        inx = self.phones.index(old_phone)
        self.phones[inx] = new_phone
        
    def change_birthday(self, birthday):
        self.birthday = self._birthday(birthday)   

    def days_to_birthday(self) -> int :
        """
        Calculate the number of days remaining until the contact's next birthday.

        Returns:
            int: The number of days remaining until the contact's next birthday.
        Raises:
            KeyError: If the contact does not have a birthday set.
        """
        if self.birthday == None:
            raise KeyError(f"No birthday set for the contact {self.name}.")
        
        today = date.today()
        try:
            bday = self.birthday.get_date().replace(year=today.year) # дата др в этом году 
            if today > bday : # если др уже прошло берем дату следующего(в следующем году)
                bday= bday.replace(year=today.year+1)
            return (bday - today).days
        except ValueError: # исключение для високосной дати 1го дня уууу-02-29
            exept_temp = Record(self.name, [] , today.replace(month=2, day=28).isoformat()) 
            return exept_temp.days_to_birthday() + 1
        
    
    def __str__(self) -> str:
        # вывод телефонов с новой строки и табуляцией
        birthday_str = f'birthday: {self.birthday or "Empty"}'
        phones_str = ", ".join([str(ph) for ph in self.phones])
        return (
            f'<Record>:\n\tname: {self.name}'
            f'\n\tphones: {phones_str or "Empty"}\n\t'
            f'{birthday_str}\n'
        )

    def __repr__(self) -> str:
        # __repr__ используется для того что бы показать как создается екземпляр
        # т.е. если выполнить эту строку в repl python будет создан такой же екземпляр,
        # конечно, при условии , что все необходимые классы тоже импортированы
        # repl python
        # (встроенная в пайтон среда выполенния, которую можно вызвать просто выполнив команду python)
        return (
            f'Record(name={self.name!r}, '
            f'phones=[{", ".join([ph.__repr__() for ph in self.phones])}, '
            f'birthday={self.birthday!r})'
        )

    def to_dict(self) -> dict[str, dict[str, list[str] | str | None]]:
        phones = [str(phone) for phone in self.phones]
        birthday = None if self.birthday is None else str(self.birthday)
        return {
            str(self.name): {
                "phones": phones,
                "birthday": birthday,
            },
        }
          
class AddressBook(UserDict):
    """
    A class representing an address book, which is a dictionary 
    with record names as keys and record objects as values.
    """
    
    def add_record(self, record: Record) -> None:
        """
        Add a record to the address book.

        Args:
            record (Record): The record object to be added.
        Raises:
            TypeError: If the given object is not an instance of the Record class.
        """
        self[record.name.value] = record # отрабативает __setitem__ 
    
    def __getitem__(self, key: str) -> Record:
        """
        Retrieve a record from the address book by its name.

        Args:
            key (str): The name of the record to retrieve.
        Returns:
            Record: The record object corresponding to the given name.
        Raises:
            KeyError: If the provided name is not found in the address book.
        """
        record = self.data.get(key)
        if record is None:
            raise KeyError(f"This name {key} isn't in Address Book")
        return record
    
    def __setitem__(self, key: str, val: Record) -> None:
        """
        Add or update a record in the address book.

        Args:
            key (str): The name of the record.
            val (Record): The record object to be added or updated.
        Raises:
            TypeError: If the given value is not an instance of the Record class.
            KeyError: If the provided name is already present in the address book.
        """
        if not isinstance(val, Record):
            raise TypeError("Record must be an instance of the Record class.")
        if key in self.data:
            raise KeyError(f"This name '{key}' is already in contacts")
        self.data[key] = val

    def __delaitem__(self, key: str) -> None:
        """
        Delete a record from the address book by its name.

        Args:
            key (str): The name of the record to delete.
        Raises:
            KeyError: If the provided name is not found in the address book.
        """
        if not isinstance(key, str):
            raise KeyError("Value must be string")
        if key not in self.data:
            raise KeyError(f"Can't delete contact {key} isn't in Address Book")
        del self.data[key]

    def to_dict(self) -> dict:
        """
        Convert the address book to a dictionary.

        Returns:
            dict: A dictionary representing the address book.
        """
        res_dict = {}
        for record in self.data.values():
            res_dict.update(record.to_dict())
        return res_dict

    def from_dict(self, data_json: dict) -> None:
        """
        Load data from a dictionary into the address book.

        Args:
            data_json (dict): A dictionary containing data for the address book.
        Raises:
            TypeError: If the provided data is not a dictionary.
        """
        if not isinstance(data_json, dict):
            raise TypeError("this is not dict")
        
        for name, record in data_json.items():
            self.add_record(
                Record(name=name, phones=record['phones'], birthday=record['birthday'])
            )

    def __str__(self) -> str:
        return '\n'.join([str(r) for r in self.values()])
    
    def search(self, search_word: str) -> list[Record]:
        """
        Search for records containing the given search word.

        Args:
            search_word (str): The word to search in the adress book.
        
        Returns:
            list[Record] or []: list whith found records.
        """
        search_list = []
        for record in self.data.values():
            str_val_record = f"{record.name} {' '.join([str(ph)for ph in record.phones])} {record.birthday}"
            if search_word in str_val_record:
                search_list.append(record)
        return search_list 
              

    def iterator(self, item_number: int) -> t.Generator[Record, int, None]:
        """
        Iterate through the records in the address book and yield groups of records.

        Args:
            item_number (int) > 0: The number of records to be yielded at a time.
        
        Yields:
            List[Record]: A list containing a group of records.
        
        Notes:
            If the given item_number is greater than the total number of records in the address book,
            all records will be yielded in one group.

        """
        if item_number <= 0:
            raise ValueError("Item number must be greater than 0.")
        elif item_number > len(self.data): # если количство виводов(за раз) больше чем количество записей
            item_number = len(self.data) # виводим все
        counter = 0
        list_records = []
        for record in self.data.values():
            list_records.append(record)
            counter += 1
            if not counter % item_number: # условие для вивода в количестве item_number накоплений
                yield list_records
                list_records = []
            elif counter == len(self.data):
                yield list_records

class AddressBookEncoder(json.JSONEncoder):
    def default(self, obj: AddressBook | Record) -> dict[str, str | list[str]] | t.Any:
        if isinstance(obj, (AddressBook, Record)):
            return obj.to_dict()
        return super().default(obj)


if __name__ == '__main__':
    rec1 = Record("aaa")
    rec2 = Record("bbb")
  
    print(id(rec1.phones))
    print(id(rec2.phones))

    # rec1.add_phone('12234566854')
    # print(rec1.phones)
    # print(rec2.phones)
    # rec2.add_phone('9765434789966')
    # print(rec1.phones)
    # print(rec2.phones)
    # rec2.add_phone('12234566854')
    # rec1.add_phone('9765434789966')
    # print(rec1.phones)
    # print(rec2.phones)

    # name_1 = Name('Bill')
    # print(name_1.__dict__)
    # phone_1 = Phone('1234567890')
    # print(phone_1.__dict__)
    # b_day_1 = Birthday('2023-12-30')
    # print(b_day_1.__dict__)
    # name_2 = Name('Nimbus2000')
    # phone_2 = Phone('+380666529589')
    # phone_20 = Phone('+380990666435')
    # b_day_2 = Birthday('2023-12-30')
    # rec_2 = Record(name_2, [phone_2, phone_20], b_day_2)
    # ab = AddressBook()
    # ab.add_record(rec_1)
    # ab.add_record(rec_2)
    # res = ab.search("name")
    # print('\n'.join([str(r) for r in res]))

    # ab = AddressBook()
    # ab.add_record(rec)

    # print(ab)
    # file_json = "test.json"
    # with open(file_json, "w") as fh:
    #     json.dump(ab, fh, cls=AddressBookEncoder, sort_keys=True, indent=2)

    # with open(file_json, "r") as fh:
    #     unpacked = json.load(fh)

    # ab_jsone = AddressBook()
    # ab_jsone.from_dict(unpacked)
    # print(ab_jsone)

    # assert isinstance(ab_jsone['Bill'], Record)
    # assert isinstance(ab_jsone['Bill'].name, Name)
    # assert isinstance(ab_jsone['Bill'].phones, list)
    # assert isinstance(ab_jsone['Bill'].phones[0], Phone)
    # assert ab_jsone['Bill'].phones[0].value == '1234567890'
    # print('All Ok)')  
   





