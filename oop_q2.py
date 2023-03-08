class Person:
    """A class that represents a Person. It has name and age attributes."""

    def __init__(self, name: str = None, age: int = None) -> None:
        self.name = name
        self.age = age

    def display(self) -> None:
        """A method to display the person's name and age."""

        print("Name:", self.name)
        print("Age:", self.age)


class Student(Person):

    """A class that represents a student. It inherits from the 
    Person class and contains a section attribute."""

    def __init__(self, name: str = None, age: int = None, section: str = None) -> None:
        super().__init__(name, age)
        self.section = section

    def display_student(self) -> None:
        """A method to display the student's name, age and section."""

        self.display()
        print("Section:", self.section)


# testing code
if __name__ == "__main__":

    student = Student("Mustansir", 22, "8A")
    student.display_student()
