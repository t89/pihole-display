from abc import ABC, abstractmethod

# Forward declaration
class Observer(ABC): pass

class Subject(ABC):
    """ The Subject interface declares a set of methods for managing subscribers """

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """ Attach an observer to the subject """
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """ Detach an observer from the subject """
        pass

    @abstractmethod
    def notify(self) -> None:
        """ Notify all observers about an event """
        pass

class Observer(ABC):
    """ Observer Interface """

    @abstractmethod
    def update(self, subject: Subject) -> None:
        """ Handle update from subject """
        pass

if __name__ == "__main__":
    main()
