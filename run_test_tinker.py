#
import asyncio

#


#
from umbria_one.tinker.tinker_utils import update_signals

#
SPREAD = 1.0
INTERVAL = 2.0


async def strategy_engine():
    print(f"Engine started...")
    while True:
        try:

            await update_signals(
                spread=SPREAD,
            )

        except Exception as e:
            print(f"STRATEGY ERROR: {e}")

        await asyncio.sleep(INTERVAL)


async def main():
    try:
        await strategy_engine()
    except asyncio.CancelledError:
        print("Shutting down...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
