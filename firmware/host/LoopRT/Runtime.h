#ifndef LOOPRT_RUNTIME_H
#define LOOPRT_RUNTIME_H

/**
 * @brief LoopRTの中心となるクラス
 *
 * 現在は起動・終了のみを担当する。
 *
 * 将来的には
 * ・Flash
 * ・Experiment
 * ・Logger
 * などをここから呼び出す。
 */
class Runtime
{
public:

    /**
     * @brief Runtimeを初期化する
     */
    void initialize();

    /**
     * @brief Runtimeを終了する
     */
    void shutdown();
};

#endif
