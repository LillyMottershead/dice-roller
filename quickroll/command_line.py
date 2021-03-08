from roll_parser import parse_command

if __name__ == "__main__":
    print('Ctrl+C to terminate')
    while True:
        repl_input = input("?: ")
        print(parse_command(repl_input)[0])
        print()
