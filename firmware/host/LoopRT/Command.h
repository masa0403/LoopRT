#ifndef LOOPRT_COMMAND_H
#define LOOPRT_COMMAND_H

/**
 * @brief Commandの種類
 */
enum class CommandType
{
    None,
    Delay,
    GpioWrite,
};

/**
 * @brief LoopRTの命令
 */
class Command
{
public:

    Command();

    void execute();

private:

    CommandType type;
};

#endif
