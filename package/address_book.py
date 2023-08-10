from collections import UserDict
from datetime import date 
from dateparser import parse as dt_parser

class Field:
    """
    Class parent representing a field used in the record of the address book.
    """
    def __init__(self, value: str) -> None:
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
        

class Name(Field):
    """
    Class representing the name field in a record of  the address book.
    """
    def __init__(self, value: str) -> None:
        self.value = value

    # наследуем геттер и сеттер ради тренировки 
    # в данном случае можно било обойтись супер в инит
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
    def __valid_phone(value) -> None:
        phone = ''.join(filter(str.isdigit, value))
        if 9 >= len(phone) <= 15 : #псевдо проверка номера
            raise ValueError("Phone number isn't correct")    

    @Field.value.setter # переопределяем сеттер родительского класса
    def value(self, value: str) -> None:
        super(Phone, Phone).value.__set__(self, value) # родительский сеттер проверка на стр
        self.__valid_phone(value)
        self._value = value
      
class FormatDateError(Exception):
    """
    Exception, If the input date string is not in a valid date format.
    """
    pass

class Birthday(Field):
    """
    Class representing the birthday field in a record of the address book.
    The date is stored in ISO 8601 format.
    """
    def __init__(self, value: str) -> None:
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
            raise FormatDateError('not correct date!!!')
            
    @Field.value.setter
    def value(self, value: str) -> None:
        self._value = self.__valid_date(value)
        
      
class RecordNotBirthdayError(Exception): 
    """
    Custom exception class to indicate that the record does not have a birthday.
    """
    pass

class Record:
    """
    Class representing a record in an address book.

    Attributes:
        name (Name): The name of the contact.
        phones (list): A list of phone numbers associated with the contact.
        birthday (Birthday): The birthday of the contact.
    """
  
    def __init__(self, name: Name, phone: Phone=None, birthday: Birthday=None ) -> None:
        
        name = self.try_valid_type_name(name)
        phone = self.try_valid_type_phone(phone)
        birthday = self.try_valid_type_birthday(birthday)

        self.name = name
        self.phones = [phone] if phone else []
        self.birthday = birthday if birthday is not None else None

    @staticmethod
    def try_valid_type_name(name: str) -> Name: 
        if type(name) != Name:
            try:
                return Name(name) # тут перезаписуємо змінну name в обькт классу
            except Exception: 
                raise ValueError(f"name: '{name}' must be type(Name) or a valid string representation of a Name object")
        return name    

    @staticmethod
    def try_valid_type_phone(phone: str) -> Phone:
        if type(phone) != Phone:
            try:
                return Phone(phone)
            except Exception:
                raise ValueError(f"phone:{phone} must be type(Phone) or a valid string representation of a Phone object")
        return phone    

    @staticmethod
    def try_valid_type_birthday(birthday: str) -> str:    
        if type(birthday) != Birthday and birthday != None:
            try:
                return Birthday(str(birthday))
            except Exception: 
                raise ValueError(f"birthday:{birthday} must be type(Birthday) or a valid string representation of a Birthday object")
        return birthday    
       
        
    def __str__(self) -> str:# для принта рекорда..не знаю как принято..сделал как чувствую
        birthday_str = "birthday: "+str(self.birthday) if self.birthday != None else ""
        phones_str = " ".join([ph.value for ph in self.phones]) 
        return f'<Record> name: {self.name} -->> phone(s): {phones_str} {birthday_str}'

    def add_phone(self, phone: Phone) -> None:
        """
        Add a new phone number to the list of phone numbers for the contact.
        Args:
            phone (Phone) or try valid Str: The phone number to be added to the contact.
        Returns:
            None: This method does not return any value.
        """
        phone = self.try_valid_type_phone(phone)
        self.phones.append(phone)

    def remove_phone(self, phone: Phone) -> None:
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
            raise KeyError(f"The phone '{phone}' is not in the record.")
        self.phones.remove(phone)
        
    def change_phone(self, old_phone: Phone, new_phone : Phone) -> None:
        """
        Change a phone number in the list of phone numbers for the contact.

        Args:
            old_phone (Phone): The existing phone number to be replaced.
            new_phone (Phone): The new phone number to replace the existing one.
            or try valid Str : --//-- .
        Raises:
            ValueError: If the old phone number is not found in the contact's list of phone numbers.
        """
        old_phone = self.try_valid_type_phone(old_phone)
        new_phone = self.try_valid_type_phone(new_phone)
        if old_phone in self.phones: # если номер входит получаем индекс 
            index = self.phones.index(old_phone)
            self.phones[index] = new_phone
        else:
            raise ValueError(f"The phone '{old_phone.value}' is not in this record '{self.name}'.")

    def days_to_birthday(self) -> int :
        """
        Calculate the number of days remaining until the contact's next birthday.

        Returns:
            int: The number of days remaining until the contact's next birthday.
        Raises:
            RecordNotBirthdayError: If the contact does not have a birthday set.
        """
        if self.birthday == None:
            raise RecordNotBirthdayError("No birthday set for the contact.")
        today = date.today()
        bday = date.fromisoformat(self.birthday.value).replace(year=today.year) # дата др в этом году 
        if today > bday : # если др уже прошло берем дату следующего(в следующем году)
           bday= bday.replace(year=today.year+1)
        return (bday - today).days
          
class AddressBook(UserDict):
    """
    A class representing an address book, which is a dictionary 
    with record names as keys and record objects as values.
    TODO Singelton?
    """
    
    def add_record(self, record: Record) -> None:
        """
        Add a record to the address book.

        Args:
            record (Record): The record object to be added.
        Raises:
            TypeError: If the given object is not an instance of the Record class.
        """
        if type(record) != Record:
            raise TypeError("Record must be an instance of the Record class.")
        self.data[record.name.value] = record 
    
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
        if item_number <= 0:
            raise ValueError("Item number must be greater than 0.")
        elif item_number > len(self.data): # если количство виводов(за раз) больше чем количество записей
            item_number = len(self.data) # виводим все
        counter = 0
        result = ""
        for id_, record in self.data.items(): # так как ми наследуемся от UserDict може юзать кк словарь
            result += f"{str(record)}\n"
            counter += 1
            
            if not counter % item_number: # условие для вивода в количестве item_number накоплений
                yield result
                result = ""
            elif counter == len(self.data) - len(self.data) % item_number + 1: # условие для хвоста
                yield result
    
    
if __name__ == '__main__':

    test = Birthday("26*02*1994")
    print(test)
    name_1 = Name('Bill')
    phone_1 = Phone('1234567890')
    b_day_1 = Birthday('1994-02-26')

    name_2 = Name('serg')
    phone_2 = Phone('1234567890')
    b_day_2 = Birthday('1994-02-26')
    
    name_3 = Name('Oleg')
    phone_3 = Phone('1234567890')
    b_day_3 = Birthday('1994-02-26')

    name_4 = Name('яяЯнаа')
    phone_4 = Phone('1234567890')
    b_day_4 = Birthday('1994-02-26')

    rec_1 = Record("Лена", "1234554545", test)
    print(rec_1.days_to_birthday())


    rec_2 = Record("Охрана", phone_2, b_day_2)
    rec_3 = Record("а я не Лена", phone_3, b_day_3)
    rec_4 = Record(name_4, phone_4, b_day_4)
    ab = AddressBook()
    ab.add_record(rec_1)
    ab.add_record(rec_2)
    ab.add_record(rec_3)
    ab.add_record(rec_4)
    # for i in ab.iterator(2):
    #     print(i)
    
    # name = Name('Bill')
    # phone = Phone('1234567890')
    # b_day = Birthday('1994-02-26')
    # rec = Record(name, phone, b_day)
    # print(rec.phones[0].value)
    # print(rec.birthday.value)
    # print(rec.days_to_birthday())
    # name = Name('Bill')
    # phone = Phone('1234567890')
    # b_day = Birthday('1994-02-26')
    # rec = Record(name, phone, "1994-02-26")
    # ab = AddressBook()
    # ab.add_record(rec)
    # assert isinstance(ab['Bill'], Record)
    # assert isinstance(ab['Bill'].name, Name)
    # assert isinstance(ab['Bill'].phones, list)
    # assert isinstance(ab['Bill'].phones[0], Phone)
    # assert isinstance(ab['Bill'].birthday, Birthday)
    # assert ab['Bill'].phones[0].value == '1234567890'
    # print('All Ok)')  
    # # a = Field("name")
    # num = Phone('12345678974')
    # print(a.value)
    # print(num.value)
    # num.value = "987654321123"
    # print(num.value)
    # day = Birthday('1994-02-26')
    # day.value = '1994-26-02'
    # print(day.value)

    





