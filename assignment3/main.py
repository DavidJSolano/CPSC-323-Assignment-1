from syntax import *
import sys
from io import StringIO


# Helper functions to swap stdout process
output_stream: StringIO = StringIO()
def store_stdout() -> None:
    global output_stream
    sys.stdout = output_stream = StringIO()
def restore_stdout() -> None:
    sys.stdout = sys.__stdout__


while True:
    print("Please enter an integer value for the test case you would like to run (1, 2, or 3) or 'Q' to exit")
    print("1. test1.txt")
    print("2. test2.txt")
    print("3. test3.txt")
    print("Q. Quit")
    number = input()
    match number:
        case '1':
            store_stdout()
            testcase = Syntax(FSM("test3.txt"))
            testcase.Rat24S(testcase.token_list[0])
            sa_output: str = output_stream.getvalue()
            restore_stdout()
            i = 1
            item_list = ""
            for item in testcase.assembly:
                print(f"{i}. {item}")
                item_list += item + '\n'
                i += 1
            f = open("output1.txt", 'w')
            f.write(item_list)
            f.close()
        case '2':
            store_stdout()
            testcase = Syntax(FSM("test2.txt"))
            testcase.Rat24S(testcase.token_list[0])
            sa_output: str = output_stream.getvalue()
            restore_stdout()
            i = 1
            item_list = ""
            for item in testcase.assembly:
                print(f"{i}. {item}")
                item_list += item + '\n'
                i += 1
            f = open("output2.txt", 'w')
            f.write(item_list)
            f.close()
        case '3':
            store_stdout()
            testcase = Syntax(FSM("test3.txt"))
            testcase.Rat24S(testcase.token_list[0])
            sa_output: str = output_stream.getvalue()
            restore_stdout()
            i = 1
            item_list = ""
            for item in testcase.assembly:
                print(f"{i}. {item}")
                item_list += item + '\n'
                i += 1
            f = open("output3.txt", 'w')
            f.write(item_list)
            f.close()

        case 'Q':
            print("Goodbye!")
            break
        case 'q':
            print("Goodbye!")
            break
        case _:
            print("Invalid input. Please enter 1, 2, 3, or 'Q'")