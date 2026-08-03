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

    void execute();

    bool isEnd();

private:

    CommandType type;
};

#endif