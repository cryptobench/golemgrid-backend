#!/usr/bin/env python3
from utils import (
    build_parser,
    TEXT_COLOR_CYAN,
    TEXT_COLOR_DEFAULT,
    TEXT_COLOR_RED,
    TEXT_COLOR_MAGENTA,
    format_usage,
    run_golem_example,
    print_env_info,
)
from datetime import datetime, timedelta
import pathlib
import sys

from yapapi import (
    Golem,
    Task,
    WorkContext,
)
from yapapi.payload import vm
from yapapi.rest.activity import BatchTimeoutError
import os
import requests
import aiohttp
import json
import argparse
import asyncio
from yapapi.log import enable_default_logger
import colorama  # type: ignore


TEXT_COLOR_RED = "\033[31;1m"
TEXT_COLOR_GREEN = "\033[32;1m"
TEXT_COLOR_YELLOW = "\033[33;1m"
TEXT_COLOR_BLUE = "\033[34;1m"
TEXT_COLOR_MAGENTA = "\033[35;1m"
TEXT_COLOR_CYAN = "\033[36;1m"
TEXT_COLOR_WHITE = "\033[37;1m"

TEXT_COLOR_DEFAULT = "\033[0m"

colorama.init()
examples_dir = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(examples_dir))


async def main(params,
               subnet_tag, min_cpu_threads, payment_driver=None, payment_network=None, show_usage=False
               ):
    package = await vm.repo(
        image_hash="9a3b5d67b0b27746283cb5f287c13eab1beaa12d92a9f536b747c7ae",
        # only run on provider nodes that have more than 0.5gb of RAM available
        min_mem_gib=0.5,
        # only run on provider nodes that have more than 2gb of storage space available
        min_storage_gib=2.0,
        # only run on provider nodes which a certain number of CPU threads (logical CPU cores) available
        min_cpu_threads=min_cpu_threads,
    )

    async def worker(ctx: WorkContext, tasks):
        scene_path = params['scene_file']
        scene_name = params['scene_name']

        # Set timeout for the first script executed on the provider. Usually, 30 seconds
        # should be more than enough for computing a single frame of the provided scene,
        # however a provider may require more time for the first task if it needs to download
        # the VM image first. Once downloaded, the VM image will be cached and other tasks that use
        # that image will be computed faster.
        script = ctx.new_script(timeout=timedelta(minutes=10))
        script.upload_file(scene_path, f"/golem/resource/{scene_name}")

        async for task in tasks:
            frame = task.data
            crops = [{"outfilebasename": "out", "borders_x": [
                0.0, 1.0], "borders_y": [0.0, 1.0]}]
            script.upload_json(
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
                "/golem/work/params.json",
            )

            script.run("/golem/entrypoints/run-blender.sh")
            output_file = f"/requestor/output/output_{frame}.png"
            script.download_file(
                f"/golem/output/out{frame:04d}.png", output_file)
            try:
                yield script
                # TODO: Check if job results are valid
                # and reject by: task.reject_task(reason = 'invalid file')
                task.accept_result(result=output_file)
                url = 'http://api:8002/v1/blender/subtask/upload'
                with open(output_file, 'rb') as f:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, data={'file': f, 'id': os.getenv("TASKID")}) as response:
                            await response.text()
            except BatchTimeoutError:
                print(
                    f"{TEXT_COLOR_RED}"
                    f"Task {task} timed out on {ctx.provider_name}, time: {task.running_time}"
                    f"{TEXT_COLOR_DEFAULT}"
                )
                raise

            # reinitialize the script which we send to the engine to compute subsequent frames
            script = ctx.new_script(timeout=timedelta(minutes=1))

            if show_usage:
                raw_state = await ctx.get_raw_state()
                usage = format_usage(await ctx.get_usage())
                cost = await ctx.get_cost()
                print(
                    f"{TEXT_COLOR_MAGENTA}"
                    f" --- {ctx.provider_name} STATE: {raw_state}\n"
                    f" --- {ctx.provider_name} USAGE: {usage}\n"
                    f" --- {ctx.provider_name}  COST: {cost}"
                    f"{TEXT_COLOR_DEFAULT}"
                )

    # Iterator over the frame indices that we want to render
    frames: range = range(0, 60, 10)
    # Worst-case overhead, in minutes, for initialization (negotiation, file transfer etc.)
    # TODO: make this dynamic, e.g. depending on the size of files to transfer
    init_overhead = 3
    # Providers will not accept work if the timeout is outside of the [5 min, 30min] range.
    # We increase the lower bound to 6 min to account for the time needed for our demand to
    # reach the providers.
    min_timeout, max_timeout = 6, 30

    timeout = timedelta(minutes=max(
        min(init_overhead + len(frames) * 2, max_timeout), min_timeout))

    async with Golem(
        budget=10.0,
        subnet_tag=subnet_tag,
        payment_driver=payment_driver,
        payment_network=payment_network,
    ) as golem:
        print_env_info(golem)

        num_tasks = 0
        start_time = datetime.now()

        completed_tasks = golem.execute_tasks(
            worker,
            [Task(data=frame) for frame in frames],
            payload=package,
            max_workers=1000,
            timeout=timeout,
        )
        async for task in completed_tasks:
            num_tasks += 1
            print(
                f"{TEXT_COLOR_CYAN}"
                f"Task computed: {task}, result: {task.result}, time: {task.running_time}"
                f"{TEXT_COLOR_DEFAULT}"
            )

        print(
            f"{TEXT_COLOR_CYAN}"
            f"{num_tasks} tasks computed, total time: {datetime.now() - start_time}"
            f"{TEXT_COLOR_DEFAULT}"
        )

        task_id = os.getenv("TASKID")
        url = f"http://container-manager-api:8003/v1/container/ping/shutdown/{task_id}"
        requests.get(url)

if __name__ == "__main__":
    parser = build_parser("Render a Blender scene")
    parser.add_argument("--show-usage", action="store_true",
                        help="show activity usage and cost")
    parser.add_argument(
        "--min-cpu-threads",
        type=int,
        default=1,
        help="require the provider nodes to have at least this number of available CPU threads",
    )
    now = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    parser.set_defaults(log_file=f"blender-yapapi-{now}.log")
    parser.add_argument('-j', '--jpath', type=str, required=True)
    args = parser.parse_args()
    jsonParams = open(args.jpath,)
    params = json.load(jsonParams)

    run_golem_example(
        main(params,
             subnet_tag=args.subnet_tag,
             min_cpu_threads=args.min_cpu_threads,
             payment_driver=args.payment_driver,
             payment_network=args.payment_network,
             show_usage=args.show_usage,
             ),
        log_file=args.log_file,
    )
