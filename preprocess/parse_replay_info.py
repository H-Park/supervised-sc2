from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import time
import json
import signal
import threading
import queue as Queue
from absl import flags
import multiprocessing
from itertools import chain
from future.builtins import range
from google.protobuf.json_format import MessageToJson

from pysc2 import run_configs
from pysc2.lib import replay
from pysc2.lib.remote_controller import RequestError

FLAGS = flags.FLAGS
flags.DEFINE_string(name='version', default='4.10.0',
                    help='Game version to use, if replays don\'t match, ignore them')
flags.DEFINE_string(name='replays_paths', default='/home/hunter/Documents/small_replays/',
                    help='Paths for replays, split by ;')
flags.DEFINE_string(name='save_path', default='../replays_infos',
                    help='Path for saving results')

flags.DEFINE_integer(name='n_instance', default=1,
                     help='# of processes to run')
flags.DEFINE_integer(name='batch_size', default=10,
                     help='# of replays to process in one iter')
FLAGS(sys.argv)

bad_counter = 0
class ReplayProcessor(multiprocessing.Process):
    """A Process that pulls replays and processes them."""
    def __init__(self, run_config, replay_queue, counter, total_num):
        super(ReplayProcessor, self).__init__()
        self.run_config = run_config
        self.replay_queue = replay_queue
        self.counter = counter
        self.total_num = total_num

    def run(self):
        signal.signal(signal.SIGTERM, lambda a, b: sys.exit())  # Exit quietly.
        while True:
            with self.run_config.start() as controller:
                for _ in range(FLAGS.batch_size):
                    try:
                        replay_path = self.replay_queue.get()
                    except Queue.Empty:
                        return
                    try:
                        replay_data = self.run_config.replay_data(replay_path)
                        ver = replay.get_replay_version(replay_data)
                        FLAGS.set_default("sc2_version", ver.game_version)
                        try:
                            info = controller.replay_info(replay_data)

                            info_json = MessageToJson(info)
                            with open(os.path.join(FLAGS.save_path, os.path.basename(replay_path)), 'w') as f:
                                json.dump({'info': info_json, 'path':replay_path}, f)
                            with self.counter.get_lock():
                                self.counter.value += 1
                                print('Processing {}/{} ...'.format(self.counter.value, self.total_num))
                        except RequestError:
                            bad_counter += 1
                            pass
                    finally:
                        self.replay_queue.task_done()

def replay_queue_filler(replay_queue, replay_list):
    """A thread that fills the replay_queue with replay paths."""
    for replay_path in replay_list:
        replay_queue.put(replay_path)

def main():
    if not os.path.isdir(FLAGS.save_path):
        os.makedirs(FLAGS.save_path)

    run_config = run_configs.get(version=FLAGS.version)
    try:
        replay_list = sorted(chain(*[run_config.replay_paths(path)
                                        for path in FLAGS.replays_paths.split(';')
                                            if len(path.strip()) > 0]))
        replay_queue = multiprocessing.JoinableQueue(FLAGS.n_instance)
        replay_queue_thread = threading.Thread(target=replay_queue_filler,
                                               args=(replay_queue, replay_list))
        replay_queue_thread.daemon = True
        replay_queue_thread.start()

        counter = multiprocessing.Value('i', 0)
        for _ in range(FLAGS.n_instance):
            p = ReplayProcessor(run_config, replay_queue, counter, len(replay_list))
            p.daemon = True
            p.start()
            time.sleep(1)   # Stagger startups, otherwise they seem to conflict somehow

        replay_queue.join() # Wait for the queue to empty.
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, exiting.")
    time.sleep(1)
    print("Corrupt replays: ", str(bad_counter))

if __name__ == '__main__':
    main()
