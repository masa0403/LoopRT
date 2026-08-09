#ifndef COMMAND_H
#define COMMAND_H

enum class CommandType
{
    None,
    PinHigh,
    PinLow,
    Pwm,
    PwmInput,
    Input,
    Delay,
    End
};

class Command
{
public:

    Command();

    explicit Command(CommandType type);

    Command(
        CommandType type,
        int pin,
        int value
    );

    void execute();

    bool isEnd();

    bool isPwmInput();

    bool isInput();

    int getPin() const;

private:

    CommandType type;

    int pin;

    int value;
};

#endif