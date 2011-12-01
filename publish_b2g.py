import os
import subprocess
import sys

from mozillapulse.config import PulseConfiguration
from mozillapulse.messages.base import GenericMessage
from mozillapulse.publishers import GenericPublisher

class B2GPulsePublisher(GenericPublisher):
    def __init__(self, **kwargs):
        super(B2GPulsePublisher, self).__init__(PulseConfiguration(**kwargs),
                                                'org.mozilla.exchange.b2g')

def publish_build(commit):
    publisher = B2GPulsePublisher()
    msg = GenericMessage()
    msg.routing_parts = ['b2g', 'qemu', 'build', 'available']
    msg.set_data('buildurl', '10.242.30.20/out/qemu_package.tar.gz')
    msg.set_data('commit', commit)
    publisher.publish(msg)

if __name__ == '__main__':
    args = sys.argv[1:]

    if not args:
        cwd = '.'
    else:
        cwd = args[0]

    proc = subprocess.Popen(['git', 'rev-list', '--max-count=1', 'HEAD'],
                            stderr=subprocess.STDOUT, stdout=subprocess.PIPE,
                            cwd=cwd)
    retcode = proc.wait()
    commit = proc.stdout.read().strip()
    publish_build(commit)

