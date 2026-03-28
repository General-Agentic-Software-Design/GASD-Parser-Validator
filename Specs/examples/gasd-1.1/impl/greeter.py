"""
CONTEXT: "General Software"
TARGET: "Python"
TRACE: "SRS-000 (Hello World)"
"""

class Greeter:
    """
    COMPONENT Greeter
    """

    def say_hello(self) -> str:
        """
        FLOW say_hello():
            1. RETURN "Hello, World!"
        """
        # Generated implementation of FLOW say_hello()
        return "Hello, World!"

if __name__ == "__main__":
    # Example usage of Greeter component
    greeter = Greeter()
    print(greeter.say_hello())
