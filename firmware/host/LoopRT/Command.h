#ifndef LOOPRT_COMMAND_H
#define LOOPRT_COMMAND_H

/**
 * @brief LoopRTの命令実行クラス
 *
 * 現在はダミー命令のみを実行する。
 * 将来的にはWAITやFLASHなどの命令を実装する。
 */
class Command
{
public:

    /**
     * @brief 1つの命令を実行する
     */
    void execute();
};

#endif
