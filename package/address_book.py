from collections import UserDict
import json
from datetime import date 
from dateparser import parse as dt_parser

class Field:
    """
    Class parent representing a field used in the record of the address book.
    """
    def __init__(self, value: str) -> None:
        self._value = None
        self.value = value # при инициализации отрабативает сеттер
      
    @staticmethod
    def __valid_value(value) -> None:
        if type(value) != str:
            raise TypeError('received data must be STR') 
        
    @property
    def value(self) :
        return self._value
    
    @value.setter
    def value(self, value: str) -> None:
        self.__valid_value(value)
        self._value = value

    def __str__(self) -> str:
        return f'{self.value}'
    
    def __eq__(self, val):
        # == 
        if isinstance(val, self.__class__): # если зайдет дочерний селф же станит дочерним?
            val = val.value
        return self.value == val
    

class Name(Field):
    """
    Class representing the name field in a record of  the address book.
    """
    def __init__(self, value: str) -> None:
        self.value = value

    # наследуем геттер и сеттер ради тренировки 
    # в данном случае можно било обойтись без супер 
    @property
    def value(self) -> str:
        return super(Name,Name).value.fget(self)

    @value.setter
    def value(self, value: str) -> None:
        super(Name,Name).value.fset(self, value)  
       

class Phone(Field):
    """
    Class representing the phone field in a record of the address book.
    """
    def __init__(self, value: str) -> None:
        self.value = value # при инициализации отрабативает сеттер
        
    @staticmethod
    def __valid_phone(value) -> str: 
        phone = ''.join(filter(str.isdigit, value))
        if 9 >= len(phone) <= 15 : #псевдо проверка номера
            raise ValueError("Phone number isn't correct")
        return phone

    @Field.value.setter # переопределяем сеттер родительского класса
    def value(self, value: str) -> None:
        super(Phone, Phone).value.__set__(self, value) # родительский сеттер проверка на стр
        self._value  = self.__valid_phone(value)
        

class Birthday(Field):
    """
    Class representing the birthday field in a record of the address book.
    The date is stored in ISO 8601 format.
    """
    def __init__(self, value: str) -> None:
        self._value = None
        self.value = value # при инициализации отрабативает сеттер
    
    @staticmethod
    def __valid_date(value: str) -> str:
        """
        Validate and convert the input date string to a valid ISO-formatted date.
        Args:
            value (str): The input date string.
        Raises:
            FormatDateError: If the input date string is not in a valid date format.
        Returns:
            str: The valid ISO-formatted date string.    
        """
        try:
            return date.isoformat(dt_parser(str(value), settings={'STRICT_PARSING': True}).date())
        except Exception: 
            raise ValueError('not correct date!!!')
            
    @Field.value.setter
    def value(self, value: str) -> None:
        self._value = self.__valid_date(value)
        

class Record:
    """
    Class representing a record in an address book.

    Attributes:
        name (Name): The name of the contact.
        phones (list): A list of phone numbers associated with the contact.
        birthday (Birthday): The birthday of the contact.
    """
  
    def __init__(self, name: Name|str, phone: Phone|str=None, birthday: Birthday|str=None ) -> None:
        #TODO може це слід робити в __new__ ? 
        # може треба було зробити класметодами у відповідних классах і тут викликати замість цих траів?
        name = self.try_valid_type_name(name)
        phone = self.try_valid_type_phone(phone)
        birthday = self.try_valid_type_birthday(birthday)

        self.name = name
        self.phones = [phone] if phone is not None else []
        self.birthday = birthday if birthday is not None else None

    @staticmethod
    def try_valid_type_name(name: str|Name) -> Name: 
        if type(name) != Name:
            try:
                return Name(name) # тут перезаписуємо змінну name в обькт классу
            except Exception: 
                raise ValueError(f"name: '{name}' must be type(Name) or a valid string representation of a Name object")
        return name    

    @staticmethod
    def try_valid_type_phone(phone: str|Phone) -> Phone:
        if type(phone) != Phone and phone != None:
            try:
                return Phone(phone)
            except Exception:
                raise ValueError(f"phone:{phone} must be type(Phone) or a valid string representation of a Phone object")
        return phone    

    @staticmethod
    def try_valid_type_birthday(birthday: str|Birthday) -> str:    
        if type(birthday) != Birthday and birthday != None:
            try:
                return Birthday(str(birthday))
            except Exception: 
                raise ValueError(f"birthday:{birthday} must be type(Birthday) or a valid string representation of a Birthday object")
        return birthday    
    
    def add_phone(self, phone: Phone|str) -> None:
        """
        Add a new phone number to the list of phone numbers for the contact.
        Args:
            phone (Phone) or try valid Str: The phone number to be added to the contact.
        Returns:
            None: This method does not return any value.
        """
        phone = self.try_valid_type_phone(phone)
        if phone in self.phones:
            raise ValueError("this phone number has already been added")
        self.phones.append(phone)

    def remove_phone(self, phone: Phone|str) -> None:
        """
        Remove a phone number from the list of phone numbers for the contact.

        Args:
            phone (Phone) or try valid Str: The phone number to be removed from the contact.
        Raises:
            KeyError: If the phone number is not found in the contact's list of phone numbers.
        Returns: 
            None: This method does not return any value.
        """
        phone = self.try_valid_type_phone(phone)
        if phone not in self.phones:
            raise ValueError(f"The phone '{phone}' is not in this record.")
        self.phones.remove(phone)
        
    def change_phone(self, old_phone: Phone|str, new_phone: Phone|str) -> None:
        """
        Change a phone number in the list of phone numbers for the contact.

        Args:
            old_phone (Phone)  or try valid Str: The existing phone number to be replaced.
            new_phone (Phone)  or try valid Str: The new phone number to replace the existing one.
        Raises:
            ValueError: If the old phone number is not found in the contact's list of phone numbers.
        """
        old_phone = self.try_valid_type_phone(old_phone) # obj_phone or raise
        new_phone = self.try_valid_type_phone(new_phone)
        if old_phone not in self.phones: 
            raise ValueError(f"The phone '{old_phone}' is not in this record '{self.name}'.")
        index = self.phones.index(old_phone)
        self.phones[index] = new_phone
        
    def change_birthday(self, birthday):
        self.birthday = self.try_valid_type_birthday(birthday)   

    def days_to_birthday(self) -> int :
        """
        Calculate the number of days remaining until the contact's next birthday.

        Returns:
            int: The number of days remaining until the contact's next birthday.
        Raises:
            KeyError: If the contact does not have a birthday set.
        """
        if self.birthday == None:
            raise KeyError("No birthday set for the contact.")
        today = date.today()
        bday = date.fromisoformat(self.birthday.value).replace(year=today.year) # дата др в этом году 
        if today > bday : # если др уже прошло берем дату следующего(в следующем году)
           bday= bday.replace(year=today.year+1)
        return (bday - today).days
    
    def __str__(self) -> str:# для принта рекорда..не знаю как принято..сделал как чувствую
        birthday_str = "birthday: "+str(self.birthday) if self.birthday != None else ""
        phones_str = " ".join([ph.value for ph in self.phones]) 
        return f'<Record> name: {self.name} -->> phone(s): {phones_str} {birthday_str}'

    def __repr__(self) -> str:
        birthday_str = str(self.birthday) if self.birthday != None else ""
        phones_str = " ".join([ph.value for ph in self.phones]) if self.phones != [] else ""
        return f'{self.name} {phones_str} {birthday_str}'

    def to_dict(self):
        return {
            "phones": [phone.value for phone in self.phones],
            "birthday": self.birthday.value if self.birthday else None
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
        if not record:
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
        if type(val) != Record:
            raise TypeError("Record must be an instance of the Record class.")
        if key in self.data.keys():
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
            raise KeyError("key(name) must be string")
        if key not in self.data.keys():
            raise KeyError(f"Can't delete contact {key} isn't in Address Book")
        del self.data[key]

    def to_dict(self) -> dict:
        """
        Convert the address book to a dictionary.

        Returns:
            dict: A dictionary representing the address book.
        """
        res_dict = {}
        for key, rec in self.data.items():
            res_dict[key] = rec.to_dict()
        return res_dict

    def from_dict(self, data_json: dict) -> None:
        """
        Load data from a dictionary into the address book.

        Args:
            data_json (dict): A dictionary containing data for the address book.
        Raises:
            TypeError: If the provided data is not a dictionary.
        """
        if type(data_json) != dict:
            raise TypeError("this is not dict")
        
        for name, record in data_json.items():
            res_record = Record(name, birthday=record['birthday'])
            for i in range(len(record["phones"])):
                res_record.add_phone(record["phones"][i])
            self.add_record(res_record)

    def search(self, search_word: str) -> str:
        """
        Search for records containing the given search word.

        Args:
            search_word (str): The word to search for in the records.
        
        Yields:
            str: A string representation of the found records.
        """
        for record in self.data.values():
            if search_word.lower() in record.__repr__().lower():
                yield str(record)[9:]
              

    def iterator(self, item_number: int) -> str:
        """
        Iterate through the records in the address book and yield groups of records.

        Args:
            item_number (int) > 0: The number of records to be yielded at a time.
        Yields:
            str: A string containing the representation of a group of records.
        Notes:
            If the given item_number is greater than the total number of records in the address book,
            all records will be yielded in one group.
        Raises:
            ValueError: If item_number is less than or equal to 0.    
            TODO красивий(табличний .format принт)
        """
        if type(item_number) != int:
            raise ValueError("Item must be int number")
        if item_number <= 0:
            raise ValueError("Item number must be greater than 0.")
        elif item_number > len(self.data): # если количство виводов(за раз) больше чем количество записей
            item_number = len(self.data) # виводим все
        counter = 0
        result = ""
        for record in self.data.values(): # так как ми наследуемся от UserDict може юзать кк словарь
            result += f"{str(record)[9:]}\n"
            counter += 1
            if not counter % item_number: # условие для вивода в количестве item_number накоплений
                yield result
                result = ""
            elif counter == len(self.data) :
                yield result.rstrip()

class AddressBookEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, AddressBook):
            return obj.to_dict()  # Перетворити AddressBook на словник
        return super().default(obj)

# class AddressBookDecoder(json.JSONDecoder):
#     def decode(self, s, **kwargs):
#         data = super().decode(s, **kwargs)
#         return AddressBook.from_dict(data)         
    
if __name__ == '__main__':

    name_1 = Name('Bill')
    phone_1 = Phone('1234567890')
    phone_2 = Phone('1234567890')
    b_day_1 = Birthday('1994-02-26')
    rec = Record(name_1, phone_1, b_day_1)

    
    # print(phone_1.value == phone_2.value) # True
    # print(phone_1 ==  phone_2) # False
    
    print(rec)
    rec.remove_phone("1234567890")
    print(rec)
    rec.remove_phone("1234567890")
    print(rec)
    # rec.change_phone("1234567890", "0987654321")
    # print(rec)
 


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
   





