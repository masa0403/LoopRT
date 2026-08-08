#ifndef LOOPRT_COMMAND_H
#define LOOPRT_COMMAND_H

/**
 * @brief Commandの種類
 */
enum class CommandType
{
    None,
    PinHigh,
    PinLow,
    Pwm,
    PwmInput,
    Delay,
    End
};

/**
 * @brief LoopRTの命令
 */
class Command
{
public:

    Command();
    Command(CommandType type);
    Command(CommandType type, int value);

    void execute();

    bool isEnd();
    bool isPwmInput();

private:

    CommandType type;
    int value;
};

#endif