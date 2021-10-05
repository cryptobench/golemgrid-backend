#!/usr/bin/env python3
import asyncio
from datetime import datetime, timedelta
import pathlib
import sys
import json
import argparse
from yapapi import (
    Golem,
    NoPaymentAccountError,
    Task,
    __version__ as yapapi_version,
    WorkContext,
    windows_event_loop_fix,
)
from log import enable_default_logger
from yapapi.payload import vm
from yapapi.rest.activity import BatchTimeoutError

examples_dir = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(examples_dir))


async def main(params, subnet_tag, driver=None, network=None):
    package = await vm.repo(
        image_hash="9a3b5d67b0b27746283cb5f287c13eab1beaa12d92a9f536b747c7ae",
        min_mem_gib=0.5,
        min_storage_gib=2.0,
    )

    async def worker(ctx: WorkContext, tasks):
        scene_path = params['scene_file']
        scene_name = params['scene_name']
        ctx.send_file(scene_path, f"/golem/resource/{scene_name}")
        async for task in tasks:
            frame = task.data
            crops = [{"outfilebasename": "out", "borders_x": [
                0.0, 1.0], "borders_y": [0.0, 1.0]}]
            ctx.send_json(
                "/golem/work/params.json",
                {
                    "scene_file": f"/golem/resource/{scene_name}",
                    "resolution": (params['resolution1'], params['resolution2']),
                    "use_compositing": params['use_compositing'],
                    "crops": crops,
                    "samples": params['samples'],
                    "frames": [frame],
                    "output_format": params['output_format'],
                    "RESOURCES_DIR": params['RESOURCES_DIR'],
                    "WORK_DIR": params['WORK_DIR'],
                    "OUTPUT_DIR": params['OUTPUT_DIR'],
                },
            )
            ctx.run("/golem/entrypoints/run-blender.sh")
            output_file = f"/requestor/output/output_{frame}.png"
            ctx.download_file(f"/golem/output/out{frame:04d}.png", output_file)
            try:
                # Set timeout for executing the script on the provider. Usually, 30 seconds
                # should be more than enough for computing a single frame, however a provider
                # may require more time for the first task if it needs to download a VM image
                # first. Once downloaded, the VM image will be cached and other tasks that use
                # that image will be computed faster.
                yield ctx.commit(timeout=timedelta(minutes=10))
                # TODO: Check if job results are valid
                # and reject by: task.reject_task(reason = 'invalid file')
                task.accept_result(result=output_file)
            except BatchTimeoutError:
                print(
                    f"{TEXT_COLOR_RED}"
                    f"Task {task} timed out on {ctx.provider_name}, time: {task.running_time}"
                    f"{TEXT_COLOR_DEFAULT}"
                )
                raise

    # Iterator over the frame indices that we want to render
    frames: range = range(0, 60, 10)
    # Worst-case overhead, in minutes, for initialization (negotiation, file transfer etc.)
    # TODO: make this dynamic, e.g. depending on the size of files to transfer
    init_overhead = 3
    # Providers will not accept work if the timeout is outside of the [5 min, 30min] range.
    # We increase the lower bound to 6 min to account for the time needed for our demand to
    # reach the providers.
    min_timeout, max_timeout = 6, 29

    timeout = timedelta(minutes=max(
        min(init_overhead + len(frames) * 2, max_timeout), min_timeout))

    async with Golem(
        budget=10.0,
        subnet_tag=subnet_tag,
        driver=driver,
        network=network,
    ) as golem:

        print(
            f"yapapi version: {yapapi_version}\n"
            f"Using subnet: {subnet_tag}, "
            f"payment driver: {golem.driver}, "
            f"and network: {golem.network}\n"
        )

        num_tasks = 0
        start_time = datetime.now()

        completed_tasks = golem.execute_tasks(
            worker,
            [Task(data=frame) for frame in frames],
            payload=package,
            max_workers=3,
            timeout=timeout,
        )
        async for task in completed_tasks:
            num_tasks += 1
            print(
                f"Task computed: {task}, result: {task.result}, time: {task.running_time}"
            )

        print(
            f"{num_tasks} tasks computed, total time: {datetime.now() - start_time}"
        )


if __name__ == "__main__":
    now = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")

    # This is only required when running on Windows with Python prior to 3.8:
    windows_event_loop_fix()
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--jpath', type=str, required=True)
    args = parser.parse_args()
    jsonParams = open(args.jpath,)
    # returns JSON object as
    # a dictionary
    params = json.load(jsonParams)
    enable_default_logger(
        log_file=f"blender-yapapi-{now}.log",
        debug_activity_api=True,
        debug_market_api=True,
        debug_payment_api=True,
    )

    loop = asyncio.get_event_loop()
    task = loop.create_task(
        main(params, subnet_tag="devnet-beta.2",
             driver="zksync", network="rinkeby")
    )

    try:
        loop.run_until_complete(task)
    except NoPaymentAccountError as e:
        handbook_url = (
            "https://handbook.golem.network/requestor-tutorials/"
            "flash-tutorial-of-requestor-development"
        )
        print(
            f"No payment account initialized for driver `{e.required_driver}` "
            f"and network `{e.required_network}`.\n\n"
            f"See {handbook_url} on how to initialize payment accounts for a requestor node."
        )
    except KeyboardInterrupt:
        print(
            "Shutting down gracefully, please wait a short while "
            "or press Ctrl+C to exit immediately..."
        )
        task.cancel()
        try:
            loop.run_until_complete(task)
            print(
                f"Shutdown completed, thank you for waiting!"
            )
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass
