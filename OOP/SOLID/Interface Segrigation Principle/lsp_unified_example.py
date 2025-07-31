from abc import ABC, abstractmethod
from typing import List, Optional
import json

# Violation:: FAT Interface(ANTI Pattern)

class BadWorkerInterface(ABC):
    """
    Fat interface that forces all implementers to support all operations.
    This violates ISP because diffrent worker types don't need all methods.
    """
    @abstractmethod
    def work(self) -> str:
        pass

    @abstractmethod
    def eat(self) -> str:
        pass

    @abstractmethod
    def sleep(self) -> str:
        pass

    @abstractmethod
    def program(self) -> str:
        pass

    @abstractmethod
    def manage_team(self) -> str:
        pass

    @abstractmethod
    def design_ui(self) -> str:
        pass

    @abstractmethod
    def test_software(self) -> str:
        pass


class BadRobot(BadWorkerInterface):
    """Robot forced to implement human-specific methods"""
    def work(self) -> str:
        return "Robot working efficiently"
    
    def eat(self) -> str:
        # Violation: Robot doesn't eat but forced to implement
        raise NotImplementedError("Robots don't eat!")
    
    def sleep(self) -> str:
        # Violation: Robot doesn't sleep but forced to implement
        raise NotImplementedError("Robot don't sleep!")

    def program(self) -> str:
        return "Robot executing programmed task"   
    
    @abstractmethod
    def manage_team(self) -> str:
        # Violation: This robot doesn't manage teams
        raise NotImplementedError("This robot doesn't manage teams.")

    @abstractmethod
    def design_ui(self) -> str:
        # Violation: This robot doesn't design UIs!
        raise NotImplementedError("This robot doesn't design UIs!")

    @abstractmethod
    def test_software(self) -> str:
        # Violation: This robot doesn't test software
        raise NotImplementedError("This robot doesn't test software!")
    

class BadHumanWorker(BadWorkerInterface):
    """Human worker forced to implement all technical methods"""
    def work(self) -> str:
        return "Human working diligently"
    
    def eat(self) -> str:
        return "Human eating lunch"
    
    def sleep(self) -> str:
        return "Human sleeping 8 hours"
    
    def program(self) -> str:
        # Violation: Not all humans can program
        raise NotImplementedError("This human doesn't know programming!")
    
    def manage_team(self) -> str:
        # Violation: Not all humans manage teams
        raise NotImplementedError("This human doesn't manage teams!")
    
    def design_ui(self) -> str:
        # Violation: Not all humans design UIs
        raise NotImplementedError("This human doesn't design UIs!")
    
    def test_software(self) -> str:
        # Violation: Not all humans test software
        raise NotImplementedError("This human doesn't test software!")
    

# ======================================
# Correct: Segregated Interfaces
# ======================================

# Basic Interfaces
class Workable(ABC):
    @abstractmethod
    def work(self) -> str:
        pass


class Eatable(ABC):
    @abstractmethod
    def eat(self) -> str:
        pass

class Sleepable(ABC):
    def sleep(self) -> str:
        pass


# Technical skill interfaces
class Programmable(ABC):
    @abstractmethod
    def program(self) -> str:
        pass

    @abstractmethod
    def debug_code(self) -> str:
        pass

class Manageable(ABC):
    @abstractmethod
    def manage_team(self) -> str:
        pass

    @abstractmethod
    def conduct_meetings(self) -> str:
        pass


class UIDesignable(ABC):
    @abstractmethod
    def design_ui(self) -> str:
        pass

    @abstractmethod
    def create_wireframes(self) -> str:
        pass


class Testable(ABC):
    @abstractmethod
    def test_software(self) -> str:
        pass

    @abstractmethod
    def write_test_cases(self) -> str:
        pass


# ============================================
# PROPER IMPLEMENTATIONS
# ============================================

class Robot(Workable, Programmable):
    """Robot only implements interfaces it actually needs"""
    def work(self) -> str:
        return "Robot working 24/7 without breaks"
    
    def program(self) -> str:
        return "Robot executing programmed instructions"
    
    def debug_code(self) -> str:
        return "Robot running diagnostic protocols"

class HumanWorker(Workable, Eatable, Sleepable):
    """Basic human worker with essential needs"""
    def work(self) -> str:
        return "Human working during business hours"
    
    def eat(self) -> str:
        return "Human taking a lunch break"
    
    def sleep(self) -> str:
        return "Human resting for 8 hours"

class SoftwareDeveloper(Workable, Eatable, Sleepable, Programmable, Testable):
    """Developer with programming and testing skills"""
    def work(self) -> str:
        return "Developer coding new features"
    
    def eat(self) -> str:
        return "Developer grabbing coffee and snacks"
    
    def sleep(self) -> str:
        return "Developer sleeping (hopefully enough)"
    
    def program(self) -> str:
        return "Developer writing clean, maintainable code"
    
    def debug_code(self) -> str:
        return "Developer fixing bugs and optimizing performance"
    
    def test_software(self) -> str:
        return "Developer writing unit tests"
    
    def write_test_cases(self) -> str:
        return "Developer creating comprehensive test scenarios"

class TeamManager(Workable, Eatable, Sleepable, Manageable):
    """Manager focused on team leadership"""
    def work(self) -> str:
        return "Manager coordinating team activities"
    
    def eat(self) -> str:
        return "Manager having working lunch with team"
    
    def sleep(self) -> str:
        return "Manager resting after long planning sessions"
    
    def manage_team(self) -> str:
        return "Manager guiding team towards project goals"
    
    def conduct_meetings(self) -> str:
        return "Manager running productive team meetings"

class UIDesigner(Workable, Eatable, Sleepable, UIDesignable):
    """Designer focused on user interface"""
    def work(self) -> str:
        return "Designer creating beautiful interfaces"
    
    def eat(self) -> str:
        return "Designer having creative lunch break"
    
    def sleep(self) -> str:
        return "Designer resting creative mind"
    
    def design_ui(self) -> str:
        return "Designer crafting intuitive user experiences"
    
    def create_wireframes(self) -> str:
        return "Designer sketching interface layouts"

class FullStackDeveloper(Workable, Eatable, Sleepable, Programmable, 
                        UIDesignable, Testable):
    """Multi-skilled developer - legitimately needs multiple interfaces"""
    def work(self) -> str:
        return "Full-stack developer handling end-to-end development"
    
    def eat(self) -> str:
        return "Full-stack developer fueling up for long coding sessions"
    
    def sleep(self) -> str:
        return "Full-stack developer recharging after debugging frontend and backend"
    
    def program(self) -> str:
        return "Full-stack developer writing both frontend and backend code"
    
    def debug_code(self) -> str:
        return "Full-stack developer troubleshooting across the entire stack"
    
    def design_ui(self) -> str:
        return "Full-stack developer creating functional user interfaces"
    
    def create_wireframes(self) -> str:
        return "Full-stack developer sketching quick UI mockups"
    
    def test_software(self) -> str:
        return "Full-stack developer testing both frontend and backend"
    
    def write_test_cases(self) -> str:
        return "Full-stack developer writing integration tests"


# ============================================
# REAL-WORLD EXAMPLE: DOCUMENT PROCESSOR
# ============================================

# Violation: Fat interface
class BadDocumentProcessor(ABC):
    @abstractmethod
    def read_pdf(self, file_path: str) -> str:
        pass
    
    @abstractmethod
    def read_word(self, file_path: str) -> str:
        pass
    
    @abstractmethod
    def read_excel(self, file_path: str) -> str:
        pass
    
    @abstractmethod
    def write_pdf(self, content: str, file_path: str) -> bool:
        pass
    
    @abstractmethod
    def write_word(self, content: str, file_path: str) -> bool:
        pass
    
    @abstractmethod
    def write_excel(self, data: List[List[str]], file_path: str) -> bool:
        pass
    
    @abstractmethod
    def compress_document(self, file_path: str) -> bool:
        pass
    
    @abstractmethod
    def encrypt_document(self, file_path: str, password: str) -> bool:
        pass

# Correct: Segregated interfaces
class PDFReadable(ABC):
    @abstractmethod
    def read_pdf(self, file_path: str) -> str:
        pass

class WordReadable(ABC):
    @abstractmethod
    def read_word(self, file_path: str) -> str:
        pass

class ExcelReadable(ABC):
    @abstractmethod
    def read_excel(self, file_path: str) -> str:
        pass

class PDFWritable(ABC):
    @abstractmethod
    def write_pdf(self, content: str, file_path: str) -> bool:
        pass

class WordWritable(ABC):
    @abstractmethod
    def write_word(self, content: str, file_path: str) -> bool:
        pass

class ExcelWritable(ABC):
    @abstractmethod
    def write_excel(self, data: List[List[str]], file_path: str) -> bool:
        pass

class Compressible(ABC):
    @abstractmethod
    def compress_document(self, file_path: str) -> bool:
        pass

class Encryptable(ABC):
    @abstractmethod
    def encrypt_document(self, file_path: str, password: str) -> bool:
        pass

# Specific implementations
class PDFProcessor(PDFReadable, PDFWritable, Compressible, Encryptable):
    """Processes only PDF files with full capabilities"""
    def read_pdf(self, file_path: str) -> str:
        return f"Reading PDF content from {file_path}"
    
    def write_pdf(self, content: str, file_path: str) -> bool:
        print(f"Writing PDF content to {file_path}")
        return True
    
    def compress_document(self, file_path: str) -> bool:
        print(f"Compressing PDF: {file_path}")
        return True
    
    def encrypt_document(self, file_path: str, password: str) -> bool:
        print(f"Encrypting PDF: {file_path} with password")
        return True

class SimpleTextExtractor(PDFReadable, WordReadable):
    """Only extracts text - doesn't need writing, compression, or encryption"""
    def read_pdf(self, file_path: str) -> str:
        return f"Extracting text from PDF: {file_path}"
    
    def read_word(self, file_path: str) -> str:
        return f"Extracting text from Word document: {file_path}"

class ExcelReportGenerator(ExcelReadable, ExcelWritable):
    """Specialized for Excel operations only"""
    def read_excel(self, file_path: str) -> str:
        return f"Reading Excel data from {file_path}"
    
    def write_excel(self, data: List[List[str]], file_path: str) -> bool:
        print(f"Writing Excel report to {file_path}")
        return True

# ============================================
# DEMONSTRATION
# ============================================

def demonstrate_isp():
    print("=== INTERFACE SEGREGATION PRINCIPLE DEMONSTRATION ===\n")
    
    print("1. PROPER IMPLEMENTATIONS (ISP Compliant):")
    print("-" * 50)
    
    workers = [
        ("Robot", Robot()),
        ("Human Worker", HumanWorker()),
        ("Software Developer", SoftwareDeveloper()),
        ("Team Manager", TeamManager()),
        ("UI Designer", UIDesigner()),
        ("Full-Stack Developer", FullStackDeveloper())
    ]
    
    for name, worker in workers:
        print(f"\n{name}:")
        print(f"  Work: {worker.work()}")
        
        # Only call methods that the worker actually implements
        if isinstance(worker, Eatable):
            print(f"  Eat: {worker.eat()}")
        
        if isinstance(worker, Programmable):
            print(f"  Program: {worker.program()}")
        
        if isinstance(worker, Manageable):
            print(f"  Manage: {worker.manage_team()}")
        
        if isinstance(worker, UIDesignable):
            print(f"  Design: {worker.design_ui()}")
    
    print("\n\n2. DOCUMENT PROCESSOR EXAMPLES:")
    print("-" * 40)
    
    processors = [
        ("PDF Processor", PDFProcessor()),
        ("Text Extractor", SimpleTextExtractor()),
        ("Excel Report Generator", ExcelReportGenerator())
    ]
    
    for name, processor in processors:
        print(f"\n{name}:")
        
        if isinstance(processor, PDFReadable):
            print(f"  {processor.read_pdf('document.pdf')}")
        
        if isinstance(processor, WordReadable):
            print(f"  {processor.read_word('document.docx')}")
        
        if isinstance(processor, ExcelReadable):
            print(f"  {processor.read_excel('spreadsheet.xlsx')}")
        
        if isinstance(processor, Compressible):
            processor.compress_document('document.pdf')
        
        if isinstance(processor, Encryptable):
            processor.encrypt_document('document.pdf', 'secret123')

if __name__ == "__main__":
    demonstrate_isp()

# ============================================
# CRITICAL REASONING ANALYSIS
# ============================================

"""
CRITICAL REASONING ABOUT INTERFACE SEGREGATION PRINCIPLE:

1. PROBLEM WITH FAT INTERFACES:
   - Forces implementers to depend on methods they don't use
   - Creates unnecessary coupling between unrelated functionality
   - Leads to empty implementations or NotImplementedError exceptions
   - Makes code harder to maintain and extend
   - Violates the principle of least knowledge

2. BENEFITS OF INTERFACE SEGREGATION:
   - Classes only implement what they actually need
   - Reduces coupling between different concerns
   - Makes code more flexible and extensible
   - Easier to test individual capabilities
   - Promotes composition over inheritance
   - Follows single responsibility principle at interface level

3. HOW TO IDENTIFY ISP VIOLATIONS:
   - Look for interfaces with many unrelated methods
   - Check for empty implementations or NotImplementedError
   - Notice when implementing classes only use subset of interface
   - Find interfaces that serve multiple client types with different needs
   - Observe frequent interface changes affecting unrelated implementers

4. DESIGN STRATEGIES:
   - Role-based interfaces: Create interfaces for specific roles/capabilities
   - Composition: Combine multiple small interfaces when needed
   - Client-driven design: Design interfaces based on client needs
   - Interface evolution: Start small and add interfaces as needed
   - Dependency injection: Use to provide only needed capabilities

5. RELATIONSHIP TO OTHER PRINCIPLES:
   - Supports Single Responsibility: Interfaces have focused purpose
   - Enables Liskov Substitution: Cleaner contracts are easier to substitute
   - Complements Dependency Inversion: Clients depend on minimal abstractions
   - Works with Open/Closed: Easy to extend without modifying existing interfaces

6. REAL-WORLD APPLICATIONS:
   - Plugin architectures: Different plugins implement different capabilities
   - Microservices: Services expose only relevant operations
   - Mobile apps: Different screens need different device capabilities
   - Database access: Different operations need different connection types
   - User interfaces: Different user roles need different interface methods

7. TESTING IMPLICATIONS:
   - Easier to mock specific interfaces for unit tests
   - Test classes can focus on specific capabilities
   - Reduced test complexity due to smaller interface contracts
   - Better test isolation between different concerns
"""